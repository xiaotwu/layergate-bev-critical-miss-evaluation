"""New R3 ranking and expected-tie alarms from frozen compact scores only."""
from pathlib import Path
from datetime import datetime,timezone
from collections import defaultdict
import math,json,csv,time,hashlib,traceback
H=Path(__file__).resolve().parent;O=H/'analysis'
KEYS=('logistic','dev_prevalence','max_confidence_risk')
BUDGETS=(.1,.2,.3)
start=time.monotonic()
def write(name,x):
    with (O/name).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False)
def csvout(name,rr):
    keys=list(dict.fromkeys(k for r in rr for k in r))
    with (O/name).open('x',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rr)
def blocks(rr,key,reverse=False):
    out=defaultdict(list)
    for r in rr:out[r[key]].append(r)
    return [(v,out[v]) for v in sorted(out,reverse=reverse)]
def metrics(rr,key):
    n=len(rr);pos=sum(r['failure'] for r in rr);neg=n-pos
    below_neg=0;credit=0.;ap=0.;seen=0;seen_p=0
    for _,group in blocks(rr,key):
        p=sum(r['failure'] for r in group);q=len(group)-p
        credit+=p*below_neg+.5*p*q;below_neg+=q
    for _,group in blocks(rr,key,True):
        p=sum(r['failure'] for r in group);seen+=len(group);seen_p+=p
        if pos:ap+=(p/pos)*(seen_p/seen)
    kept=0;kept_p=0.;risk_sum=0.
    for _,group in blocks(rr,key):
        p=sum(r['failure'] for r in group);size=len(group)
        for j in range(1,size+1):risk_sum+=(kept_p+j*p/size)/(kept+j)
        kept+=size;kept_p+=p
    return {'n':n,'positive':pos,'negative':neg,'logs':len({r['log_token'] for r in rr}),
        'unique_scores':len({r[key] for r in rr}),'AUROC':credit/(pos*neg) if pos and neg else None,
        'threshold_grouped_AP':ap if pos else None,'expected_tie_AURC':risk_sum/n if n else None,
        'constant_score_AP_reference':pos/n if pos else None,'random_retained_failure_rate':pos/n,
        'binary_discrimination_estimable':bool(pos and neg)}
def capture(rr,key,k):
    remaining=k;cap=0.
    for _,group in blocks(rr,key,True):
        count=min(remaining,len(group));cap+=count*sum(r['failure'] for r in group)/len(group);remaining-=count
        if remaining<=0:break
    assert remaining==0
    return cap
def alarm_stats(rr,alarms,captured):
    n=len(rr);p=sum(r['failure'] for r in rr);un=n-alarms;uncap=p-captured
    return {'n':n,'positive':p,'negative':n-p,'expected_alarm_frames':alarms,'actual_expected_alarm_fraction':alarms/n,
        'expected_captured_failures':captured,'failure_capture_fraction':captured/p if p else None,
        'alert_precision':captured/alarms if alarms else None,'expected_alerted_nonfailure_frames':alarms-captured,
        'expected_unflagged_failures':uncap,'expected_unflagged_frames':un,
        'unflagged_failure_rate':uncap/un if un else None,
        'random_expected_captured_failures_same_alarm_volume':alarms*p/n,
        'excess_captured_failures_vs_random':captured-alarms*p/n,
        'capture_fraction_minus_alarm_fraction':captured/p-alarms/n if p else None}
def point(rr,key,budget):
    k=math.floor(budget*len(rr));return {'budget':budget,**alarm_stats(rr,k,capture(rr,key,k))}
def mean(values):
    vv=[v for v in values if v is not None];return math.fsum(vv)/len(vv) if vv else None
def fixed_rule(dev,key):
    # No outer row or outcome is accepted by this threshold-selection function.
    n=len(dev);k=math.floor(.2*n);values=sorted([r[key] for r in dev],reverse=True)
    assert k>0
    cutoff=values[k-1];above=sum(v>cutoff for v in values);ties=sum(v==cutoff for v in values)
    return {'threshold':cutoff,'boundary_alarm_probability':(k-above)/ties,'n_dev':n,'dev_alarm_budget':k,
        'development_scores_above_cutoff':above,'development_scores_equal_cutoff':ties,
        'threshold_selection_uses_outcomes':False,'threshold_selection_uses_outer':False}
def policy(rr,key,rule):
    weights=[1. if r[key]>rule['threshold'] else rule['boundary_alarm_probability'] if r[key]==rule['threshold'] else 0. for r in rr]
    return alarm_stats(rr,math.fsum(weights),math.fsum(w*r['failure'] for w,r in zip(weights,rr)))

def main():
    assert not O.exists();O.mkdir()
    source=H/'actual_compact_extraction/FROZEN_ANALYSIS_SCORE_ROWS.json';b=source.read_bytes();data=json.loads(b)
    rows=data['rows'];outer=[r for r in rows if r['role']=='outer'];models={(r['seed'],r['fold']):r for r in data['models']}
    scope_results=[];log_results=[];fold_results=[];budget_results=[];equal=[];curves=[]
    for seed in (0,1,2):
        full=[r for r in outer if r['seed']==seed];assert len(full)==404
        for scope,rr in [('all404',full),('target307_diagnostic',[r for r in full if r['critical_objects']>0])]:
            assert len(rr)==(404 if scope=='all404' else 307)
            for key in KEYS:
                identity={'seed':seed,'scope':scope,'score':key}
                scope_results.append({**identity,**metrics(rr,key)})
                for budget in BUDGETS:budget_results.append({**identity,**point(rr,key,budget)})
                lg=[]
                for token in sorted({r['log_token'] for r in rr}):
                    sub=[r for r in rr if r['log_token']==token]
                    m={**identity,'log_token':token,**metrics(sub,key)};log_results.append(m);lg.append(m)
                for fold in ('F0','F1','F2','F3'):
                    sub=[r for r in rr if r['fold']==fold]
                    fold_results.append({**identity,'fold':fold,**metrics(sub,key)})
                for budget in BUDGETS:
                    pp=[point([r for r in rr if r['log_token']==token],key,budget) for token in sorted({r['log_token'] for r in rr})]
                    equal.append({**identity,'budget':budget,'logs':len(pp),
                        'AUROC_logs_with_both_classes':sum(x['AUROC'] is not None for x in lg),
                        'capture_logs_with_positive':sum(x['failure_capture_fraction'] is not None for x in pp),
                        'mean_log_AUROC':mean([x['AUROC'] for x in lg]),
                        'mean_log_AP':mean([x['threshold_grouped_AP'] for x in lg]),
                        'mean_log_AURC':mean([x['expected_tie_AURC'] for x in lg]),
                        'mean_log_capture_fraction':mean([x['failure_capture_fraction'] for x in pp]),
                        'mean_log_actual_alarm_fraction':mean([x['actual_expected_alarm_fraction'] for x in pp]),
                        'mean_log_capture_minus_alarm_fraction':mean([x['capture_fraction_minus_alarm_fraction'] for x in pp]),
                        'mean_log_unflagged_failure_rate':mean([x['unflagged_failure_rate'] for x in pp])})
                if scope=='all404':
                    for k in range(404):
                        cap=capture(rr,key,k)
                        curves.append({'seed':seed,'score':key,'alarms':k,'retained_fraction':(404-k)/404,
                            'retained_failure_rate':(sum(r['failure'] for r in rr)-cap)/(404-k),
                            'expected_captured_failures':cap,'tie_handling':'uniform-label-independent-expectation'})
    thresholds=[];policy_folds=[];policy_logs=[]
    for seed in (0,1,2):
        for fold in ('F0','F1','F2','F3'):
            dev=[r for r in rows if r['seed']==seed and r['fold']==fold and r['role']=='development']
            test=[r for r in outer if r['seed']==seed and r['fold']==fold]
            assert set(r['log_token'] for r in dev)==set(models[seed,fold]['fit_logs'])
            assert set(r['log_token'] for r in test)==set(models[seed,fold]['test_logs'])
            for key in KEYS:
                rule=fixed_rule(dev,key)
                thresholds.append({'seed':seed,'fold':fold,'score':key,**rule,'dev_events':sum(r['failure'] for r in dev),
                    'model_kind':models[seed,fold]['kind'],'fit_logs':models[seed,fold]['fit_logs'],'test_logs':models[seed,fold]['test_logs']})
                policy_folds.append({'seed':seed,'fold':fold,'score':key,**policy(test,key,rule)})
                for token in sorted({r['log_token'] for r in test}):
                    sub=[r for r in test if r['log_token']==token]
                    policy_logs.append({'seed':seed,'fold':fold,'log_token':token,'score':key,**policy(sub,key,rule)})
    policy_seed=[]
    for seed in (0,1,2):
        rr=[r for r in outer if r['seed']==seed]
        for key in KEYS:
            ff=[r for r in policy_folds if r['seed']==seed and r['score']==key]
            alarms=math.fsum(x['expected_alarm_frames'] for x in ff);cap=math.fsum(x['expected_captured_failures'] for x in ff)
            policy_seed.append({'seed':seed,'score':key,'nominal_development_budget':.2,**alarm_stats(rr,alarms,cap),
                'actual_alarm_fraction_exceeds_30_percent':alarms/404>.3})
    primary=[]
    for seed in (0,1,2):
        pp={r['score']:r for r in budget_results if r['seed']==seed and r['scope']=='all404' and r['budget']==.2}
        eq=next(r for r in equal if r['seed']==seed and r['scope']=='all404' and r['score']=='logistic' and r['budget']==.2)
        cap=pp['logistic']['expected_captured_failures']
        primary.append({'seed':seed,'logistic_captured_failures':cap,'development_prevalence_captured':pp['dev_prevalence']['expected_captured_failures'],
            'max_confidence_captured':pp['max_confidence_risk']['expected_captured_failures'],
            'random_expected_captured':pp['logistic']['random_expected_captured_failures_same_alarm_volume'],
            'beats_prevalence':cap>pp['dev_prevalence']['expected_captured_failures']+1e-10,
            'beats_fixed_confidence':cap>pp['max_confidence_risk']['expected_captured_failures']+1e-10,
            'beats_random_expectation':pp['logistic']['excess_captured_failures_vs_random']>1e-10,
            'equal_log_excess_random_not_reversed':eq['mean_log_capture_minus_alarm_fraction']>=-1e-12})
    consistent=all(all(r[k] for k in ['beats_prevalence','beats_fixed_confidence','beats_random_expectation','equal_log_excess_random_not_reversed']) for r in primary)
    write('SCOPE_SCORE_METRICS.json',scope_results);csvout('SCOPE_SCORE_METRICS.csv',scope_results)
    write('SCREENING_BUDGETS.json',budget_results);csvout('SCREENING_BUDGETS.csv',budget_results)
    write('EQUAL_LOG_DESCRIPTIONS.json',equal);csvout('EQUAL_LOG_DESCRIPTIONS.csv',equal)
    csvout('PER_LOG_RANKING.csv',log_results);csvout('PER_FOLD_RANKING.csv',fold_results)
    csvout('EXPECTED_TIE_RISK_COVERAGE_CURVES.csv',curves)
    write('DEVELOPMENT_FIXED_THRESHOLDS.json',thresholds)
    csvout('FIXED_POLICY_PER_FOLD.csv',policy_folds);csvout('FIXED_POLICY_PER_LOG.csv',policy_logs)
    write('FIXED_POLICY_SEED_SUMMARY.json',policy_seed);csvout('FIXED_POLICY_SEED_SUMMARY.csv',policy_seed)
    write('RESULTS_AND_STOP.json',{'status':'COMPLETE_EXPLORATORY_FROZEN_SCORE_RANKING_AND_ALARM_ANALYSIS','at_utc':datetime.now(timezone.utc).isoformat(),
        'primary_budget':.2,'primary':primary,'consistent_internal_screening_advantage':consistent,
        'decision':'Report complete results and stop candidate expansion; no additional features/refits/training regardless of ranking outcome.',
        'rank_scope_rows':len(scope_results),'per_log_rows':len(log_results),'per_fold_rows':len(fold_results),
        'threshold_rules':len(thresholds),'fixed_policy_fold_rows':len(policy_folds),'fixed_policy_log_rows':len(policy_logs),
        'fixed_policy_seed_rows':len(policy_seed),'curve_rows':len(curves),'score_input_sha256':hashlib.sha256(b).hexdigest(),
        'source_entry_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'compact_read_bytes_this_pass':len(b),
        'wall_seconds_this_analysis':time.monotonic()-start,'new_SDK_training_detector_inference_GT_matching_refits':0,
        'original_Brier_NLL_and_detection_metrics_changed':False,'NO_PROMOTION_changed':False,'automation':'PAUSED',
        'interpretation':'Uniform tie expectations; descriptive mixed-fold outputs on historically exposed mini; no deployed or calibrated safety claim.'})
    print(json.dumps({'primary':primary,'consistent_internal_screening_advantage':consistent,'policy_seed':policy_seed},ensure_ascii=True))
try:main()
except Exception as e:
    if O.exists():write('FAILED_NO_AUTORETRY.json',{'error':repr(e),'traceback':traceback.format_exc(),'original_source_replay':False})
    raise
