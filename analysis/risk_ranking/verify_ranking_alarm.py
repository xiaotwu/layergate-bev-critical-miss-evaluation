"""Read-only R3 compact-data numerical reproduction; --receipt writes once.

Separate same-author implementation: pairwise AUROC, direct threshold AP,
fractional prefix expectations, and finite tie permutations. No old executor,
model fitting, prediction payload, SDK, detector, or matching is invoked.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction
from itertools import permutations, product
from datetime import datetime, timezone
import argparse, ast, csv, hashlib, json, math, time

H = Path(__file__).resolve().parent
A = H / 'analysis'
checks = 0
reads = []
started = time.monotonic()

def read(path, csv_file=False):
    b = path.read_bytes()
    reads.append({'path': str(path.relative_to(H)), 'bytes': len(b),
                  'sha256': hashlib.sha256(b).hexdigest()})
    if csv_file:
        from io import StringIO
        def value(s):
            if s == '': return None
            if s in ('True', 'False'): return s == 'True'
            try: return float(s)
            except ValueError: return s
        return [{k: value(v) for k, v in r.items()}
                for r in csv.DictReader(StringIO(b.decode('utf-8-sig')))]
    return json.loads(b)

def equal(actual, expected, where):
    global checks
    checks += 1
    if expected is None or isinstance(expected, (bool, str)):
        assert actual == expected, (where, actual, expected)
    else:
        assert actual is not None and math.isclose(float(actual), float(expected),
            rel_tol=2e-11, abs_tol=2e-11), (where, actual, expected)

def compare(actual, expected, where):
    for k, v in expected.items(): equal(actual[k], v, f'{where}/{k}')

def prefix(rows, key, number, high=True):
    """Exact expected positives at the boundary, no ordering by labels/IDs."""
    if number == 0: return Fraction(0)
    boundary = sorted((r[key] for r in rows), reverse=high)[number - 1]
    strict = [r for r in rows if (r[key] > boundary if high else r[key] < boundary)]
    tied = [r for r in rows if r[key] == boundary]
    return Fraction(sum(r['failure'] for r in strict)) + Fraction(
        (number - len(strict)) * sum(r['failure'] for r in tied), len(tied))

def metric(rows, key):
    n = len(rows); positive = sum(r['failure'] for r in rows); negative = n-positive
    pos = [r[key] for r in rows if r['failure']]
    neg = [r[key] for r in rows if not r['failure']]
    credit_twice = sum(2*(p>q)+(p==q) for p in pos for q in neg)
    ap = Fraction(0)
    if positive:
        for threshold in set(r[key] for r in rows):
            at = sum(r['failure'] for r in rows if r[key] == threshold)
            above = [r for r in rows if r[key] >= threshold]
            ap += Fraction(at, positive) * Fraction(sum(r['failure'] for r in above), len(above))
    aurc = sum((prefix(rows, key, m, False)/m for m in range(1, n+1)), Fraction(0))/n
    return {'n': n, 'positive': positive, 'negative': negative,
        'logs': len({r['log_token'] for r in rows}), 'unique_scores': len(set(r[key] for r in rows)),
        'AUROC': credit_twice/(2*positive*negative) if positive and negative else None,
        'threshold_grouped_AP': float(ap) if positive else None,
        'expected_tie_AURC': float(aurc),
        'constant_score_AP_reference': positive/n if positive else None,
        'random_retained_failure_rate': positive/n,
        'binary_discrimination_estimable': bool(positive and negative)}

def alarm(rows, k, captured):
    n=len(rows); p=sum(r['failure'] for r in rows); k=float(k); captured=float(captured)
    remaining=n-k; misses=p-captured
    return {'n':n,'positive':p,'negative':n-p,'expected_alarm_frames':k,
        'actual_expected_alarm_fraction':k/n,'expected_captured_failures':captured,
        'failure_capture_fraction':captured/p if p else None,
        'alert_precision':captured/k if k else None,
        'expected_alerted_nonfailure_frames':k-captured,
        'expected_unflagged_failures':misses,'expected_unflagged_frames':remaining,
        'unflagged_failure_rate':misses/remaining if remaining else None,
        'random_expected_captured_failures_same_alarm_volume':k*p/n,
        'excess_captured_failures_vs_random':captured-k*p/n,
        'capture_fraction_minus_alarm_fraction':captured/p-k/n if p else None}

def select(outer, record, log=False, fold=False):
    r=[x for x in outer if x['seed']==record['seed']]
    if record.get('scope') == 'target307_diagnostic': r=[x for x in r if x['critical_objects']>0]
    if log: r=[x for x in r if x['log_token']==record['log_token']]
    if fold: r=[x for x in r if x['fold']==record['fold']]
    return r

def average(values):
    xs=[v for v in values if v is not None]
    return math.fsum(xs)/len(xs) if xs else None

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',action='store_true');args=parser.parse_args()
    data=read(H/'actual_compact_extraction/FROZEN_ANALYSIS_SCORE_ROWS.json')
    rows=data['rows'];outer=[r for r in rows if r['role']=='outer']
    models={(m['seed'],m['fold']):m for m in data['models']}
    equal(len(rows),1698,'all rows');equal(len(outer),1212,'outer rows');equal(len(models),12,'models')
    for r in rows:
        equal(r['failure'],int(r['missed_critical_objects']>0),'label')
        equal(r['logistic'],round(r['logistic_saved_or_dev_arithmetic_p'],12),'saved probability precision')
        equal(r['dev_prevalence'],round(models[r['seed'],r['fold']]['p'],12),'development baseline')
        equal(r['max_confidence_risk'],round(1-r['features'][2],12),'fixed heuristic')
        assert 0 <= r['logistic'] <= 1
    for seed in range(3):
        rr=[r for r in outer if r['seed']==seed]
        equal(len({r['sample_token'] for r in rr}),404,'unique outer samples')
        equal(sum(r['failure'] for r in rr),(270,272,266)[seed],'failures')
        equal(len({r['log_token'] for r in rr}),8,'logs')
        for fold in ('F0','F1','F2','F3'):
            dev=[r for r in rows if r['seed']==seed and r['fold']==fold and r['role']=='development']
            test=[r for r in rr if r['fold']==fold]
            assert {r['log_token'] for r in dev} == set(models[seed,fold]['fit_logs'])
            assert {r['log_token'] for r in test} == set(models[seed,fold]['test_logs'])
            assert not {r['log_token'] for r in dev} & {r['log_token'] for r in test}
    scope=read(A/'SCOPE_SCORE_METRICS.json');lg=read(A/'PER_LOG_RANKING.csv',True);ff=read(A/'PER_FOLD_RANKING.csv',True)
    for coll,logs,folds in [(scope,False,False),(lg,True,False),(ff,False,True)]:
        for i, rec in enumerate(coll): compare(rec,metric(select(outer,rec,logs,folds),rec['score']),f'metrics/{logs}/{folds}/{i}')
    budgets=read(A/'SCREENING_BUDGETS.json')
    for i,rec in enumerate(budgets):
        rr=select(outer,rec);k=math.floor(rec['budget']*len(rr))
        compare(rec,alarm(rr,k,prefix(rr,rec['score'],k)),f'budget/{i}')
    eq=read(A/'EQUAL_LOG_DESCRIPTIONS.json')
    for i,rec in enumerate(eq):
        rr=select(outer,rec);logs=sorted({r['log_token'] for r in rr});ms=[];pts=[]
        for token in logs:
            sub=[r for r in rr if r['log_token']==token]
            ms.append(metric(sub,rec['score']));k=math.floor(rec['budget']*len(sub))
            pts.append(alarm(sub,k,prefix(sub,rec['score'],k)))
        compare(rec,{'logs':len(logs),'AUROC_logs_with_both_classes':sum(m['AUROC'] is not None for m in ms),
            'capture_logs_with_positive':sum(p['failure_capture_fraction'] is not None for p in pts),
            'mean_log_AUROC':average([m['AUROC'] for m in ms]),
            'mean_log_AP':average([m['threshold_grouped_AP'] for m in ms]),
            'mean_log_AURC':average([m['expected_tie_AURC'] for m in ms]),
            'mean_log_capture_fraction':average([p['failure_capture_fraction'] for p in pts]),
            'mean_log_actual_alarm_fraction':average([p['actual_expected_alarm_fraction'] for p in pts]),
            'mean_log_capture_minus_alarm_fraction':average([p['capture_fraction_minus_alarm_fraction'] for p in pts]),
            'mean_log_unflagged_failure_rate':average([p['unflagged_failure_rate'] for p in pts])},f'equal log/{i}')
    rules=read(A/'DEVELOPMENT_FIXED_THRESHOLDS.json');rulemap={}
    for i,r in enumerate(rules):
        dev=[x for x in rows if x['role']=='development' and x['seed']==r['seed'] and x['fold']==r['fold']]
        key=r['score'];n=len(dev);k=n//5;hist=Counter(x[key] for x in dev)
        # Histogram descending cumulative crossing: no labels, test data or IDs.
        accumulated=0
        for threshold in sorted(hist,reverse=True):
            if accumulated+hist[threshold]>=k: break
            accumulated+=hist[threshold]
        probability=Fraction(k-accumulated,hist[threshold])
        compare(r,{'threshold':threshold,'boundary_alarm_probability':float(probability),
            'n_dev':n,'dev_alarm_budget':k,'development_scores_above_cutoff':accumulated,
            'development_scores_equal_cutoff':hist[threshold],
            'threshold_selection_uses_outcomes':False,'threshold_selection_uses_outer':False,
            'dev_events':sum(x['failure'] for x in dev)},f'rule/{i}')
        rulemap[r['seed'],r['fold'],key]=(threshold,probability)
    def applied(rr,key):
        k=Fraction(0);cap=Fraction(0)
        for x in rr:
            t,q=rulemap[x['seed'],x['fold'],key]
            w=Fraction(1) if x[key]>t else q if x[key]==t else Fraction(0)
            k+=w;cap+=w*x['failure']
        return alarm(rr,k,cap)
    pff=read(A/'FIXED_POLICY_PER_FOLD.csv',True);plg=read(A/'FIXED_POLICY_PER_LOG.csv',True);ps=read(A/'FIXED_POLICY_SEED_SUMMARY.json')
    for coll,logs,folds in [(pff,False,True),(plg,True,True),(ps,False,False)]:
        for i,rec in enumerate(coll): compare(rec,applied(select(outer,rec,logs,folds),rec['score']),f'policy/{logs}/{folds}/{i}')
    curves=read(A/'EXPECTED_TIE_RISK_COVERAGE_CURVES.csv',True)
    for i,rec in enumerate(curves):
        rr=select(outer,rec);kept=len(rr)-int(rec['alarms']);low=prefix(rr,rec['score'],kept,False)
        compare(rec,{'retained_fraction':kept/len(rr),'retained_failure_rate':float(low/kept),
            'expected_captured_failures':sum(x['failure'] for x in rr)-float(low),
            'tie_handling':'uniform-label-independent-expectation'},f'curve/{i}')
    diagnostic=read(A/'FIXED_POLICY_LOG_CONDITIONAL_DIAGNOSTIC.json')
    for i,rec in enumerate(diagnostic['rows']):
        rr=[r for r in plg if r['seed']==rec['seed'] and r['score']==rec['score']]
        compare(rec,{'logs':len(rr),'sum_log_conditional_excess_captured_failures':math.fsum(r['excess_captured_failures_vs_random'] for r in rr),
            'mean_log_capture_minus_alarm_fraction':average([r['capture_fraction_minus_alarm_fraction'] for r in rr]),
            'logs_positive_within_log_enrichment':sum(r['excess_captured_failures_vs_random']>1e-10 for r in rr),
            'logs_negative_within_log_enrichment':sum(r['excess_captured_failures_vs_random'] < -1e-10 for r in rr)},f'conditional log/{i}')
    stop=read(A/'RESULTS_AND_STOP.json')
    equal(stop['consistent_internal_screening_advantage'],False,'primary stop')
    for rec in stop['primary']:
        seed=rec['seed'];b={r['score']:r for r in budgets if r['seed']==seed and r['scope']=='all404' and r['budget']==.2}
        e=next(r for r in eq if r['seed']==seed and r['scope']=='all404' and r['score']=='logistic' and r['budget']==.2)
        v=b['logistic']['expected_captured_failures']
        compare(rec,{'logistic_captured_failures':v,'development_prevalence_captured':b['dev_prevalence']['expected_captured_failures'],
            'max_confidence_captured':b['max_confidence_risk']['expected_captured_failures'],
            'random_expected_captured':b['logistic']['random_expected_captured_failures_same_alarm_volume'],
            'beats_prevalence':v>b['dev_prevalence']['expected_captured_failures']+1e-10,
            'beats_fixed_confidence':v>b['max_confidence_risk']['expected_captured_failures']+1e-10,
            'beats_random_expectation':b['logistic']['excess_captured_failures_vs_random']>1e-10,
            'equal_log_excess_random_not_reversed':e['mean_log_capture_minus_alarm_fraction']>=-1e-12},f'stop/{seed}')
    # Exhaustive label patterns and score-preserving tie permutations (n=4).
    configurations=0;permutation_orders=0
    for scores in [(0,0,0,0),(0,0,1,1),(0,1,1,2),(0,1,2,3)]:
        admissible=[p for p in permutations(range(4)) if [scores[i] for i in p]==sorted(scores)]
        for labels in product((0,1),repeat=4):
            tiny=[{'x':scores[i],'failure':labels[i]} for i in range(4)]
            explicit_aurcs=[]
            for order in admissible:
                explicit_aurcs.append(sum(Fraction(sum(labels[order[j]] for j in range(m)),m) for m in range(1,5))/4)
                permutation_orders+=1
            for m in range(1,5):
                empirical=sum(Fraction(sum(labels[p[j]] for j in range(m))) for p in admissible)/len(admissible)
                equal(prefix(tiny,'x',m,False),empirical,'finite tie prefix')
            calculated=sum(prefix(tiny,'x',m,False)/m for m in range(1,5))/4
            equal(calculated,sum(explicit_aurcs)/len(explicit_aurcs),'finite tie AURC')
            configurations+=1
    # Static scope check of the actual threshold selector, no execution of it.
    src=(H/'analyze_ranking_alarm.py').read_bytes();tree=ast.parse(src)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='fixed_rule')
    assert [a.arg for a in fn.args.args]==['dev','key']
    accessed=[n.slice.value for n in ast.walk(fn) if isinstance(n,ast.Subscript) and isinstance(n.slice,ast.Constant)]
    assert not set(accessed)&{'failure','critical_objects','missed_critical_objects','sample_token','log_token','outer'}
    output={'status':'PASS_SEPARATE_SAME_AUTHOR_NUMERICAL_IMPLEMENTATION_NOT_EXTERNAL_REPLICATION',
        'at_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'tie_label_configurations':configurations,
        'tie_permutation_orders':permutation_orders,'source_reads':reads,'controlled_returned_read_bytes':sum(r['bytes'] for r in reads),
        'schema_and_code_read_bytes':len(src),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'wall_seconds':time.monotonic()-started,'new_model_fits_SDK_detector_inference_GT_rematching':0,
        'primary_consistency_passed':False,'original_Brier_NLL_and_detector_endpoints_changed':False,
        'threshold_selector_outcome_or_outer_access_detected':False,
        'scope':'Compact R3 rows and outputs only. Pairwise AUROC, direct threshold AP, exact rational tie-prefix checks; no population inference.'}
    if args.receipt:
        path=H/'verification/R3_SEPARATE_NUMERICAL_VERIFICATION.json';path.parent.mkdir(exist_ok=True)
        with path.open('x',encoding='utf-8') as f:json.dump(output,f,ensure_ascii=False,indent=2,allow_nan=False)
    print(json.dumps({k:v for k,v in output.items() if k!='source_reads'},ensure_ascii=False))

if __name__=='__main__': main()
