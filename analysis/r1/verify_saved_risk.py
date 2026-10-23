"""Public read-only saved-model inference/scoring check.

Publication adaptation of the archived R1 portable checker: the optional refit
flag and branch are removed. The default inference/scoring arithmetic is unchanged.
No new fits, original predictions, checkpoints or SDK are available to this entry.
"""
from pathlib import Path
import argparse,json,math

def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def logistic(z):
    if z>=0:return 1/(1+math.exp(-z))
    e=math.exp(z);return e/(1+e)
def score(rows,key):
    probs=[max(1e-12,min(1-1e-12,row[key])) for row in rows]
    yy=[row['failure'] for row in rows];n=len(rows)
    return {'n':n,'positive':sum(yy),'negative':n-sum(yy),
      'Brier':math.fsum((p-y)**2 for p,y in zip(probs,yy))/n,
      'NLL':-math.fsum(y*math.log(p)+(1-y)*math.log1p(-p) for p,y in zip(probs,yy))/n}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--base-dir',type=Path,default=Path(__file__).resolve().parent)
    args=ap.parse_args();base=args.base_dir.resolve();pilot=base/'risk_pilot_actual_once'
    inputs=load(pilot/'FROZEN_FRAME_INPUTS.json')['rows'];rows=load(pilot/'OUTER_RISK_PROBABILITIES.json')['rows']
    expected=load(pilot/'RESULTS.json');assert len(inputs)==1698 and len(rows)==1212
    models={(s,f):load(pilot/f'MODEL_seed{s}_{f}.json') for s in range(3) for f in ['F0','F1','F2','F3']}
    max_error=0.;scopes=[]
    for row in rows:
        model=models[(row['seed'],row['fold'])]
        assert row['role']=='outer' and row['log_token'] in model['test_logs']
        assert not (set(model['fit_logs'])&set(model['test_logs']))
        if model['beta'] is None:pred=model['p']
        else:
            z=model['beta'][0]+math.fsum(b*(x-m)/s for b,x,m,s in zip(model['beta'][1:],row['features'],model['mean'],model['scale']))
            pred=logistic(z)
        max_error=max(max_error,abs(pred-row['logistic_p']))
        assert abs(row['dev_prevalence_p']-model['p'])<1e-15
    assert max_error<1e-12
    for seed in range(3):
        full=[r for r in rows if r['seed']==seed]
        assert len(full)==404 and len({r['sample_token'] for r in full})==404 and len({r['log_token'] for r in full})==8
        for scope,subset in [('all404',full),('original_target_frames_only',[r for r in full if r['critical_objects']>0])]:
            ref=next(x for x in expected['results'] if x['seed']==seed and x['scope']==scope)
            metrics={key:score(subset,key) for key in ['logistic_p','dev_prevalence_p','uninformative_p']}
            for key in metrics:
                for metric in ['n','positive','negative','Brier','NLL']:
                    assert abs(metrics[key][metric]-ref['metrics'][key][metric])<1e-12
            scopes.append({'seed':seed,'scope':scope,'metrics':metrics})
        for key in ['logistic_p','dev_prevalence_p']:
            by_log=[score([r for r in full if r['log_token']==log],key) for log in sorted({r['log_token'] for r in full})]
            ref=next(x for x in expected['equal_log_descriptions'] if x['seed']==seed)['metrics'][key]
            for metric in ['Brier','NLL']:
                assert abs(math.fsum(x[metric] for x in by_log)/8-ref[metric])<1e-12
    refit_count=0
    print(json.dumps({'status':'PASS','saved_probabilities':len(rows),'max_probability_error':max_error,
      'scopes_reproduced':len(scopes),'optional_logistic_refits':refit_count,'SDK':0,'GPU':0,
      'original_payload_read':0,'RSS_actual':None,'results':scopes},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
