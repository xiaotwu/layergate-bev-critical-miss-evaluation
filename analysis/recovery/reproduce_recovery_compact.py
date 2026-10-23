"""Separate scalar verifier of the saved paired counts. No source-payload reader."""
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone
from itertools import combinations
import json,csv,hashlib,math
P=Path(__file__).resolve().parent
O=P/'analysis_r2'
reads=[]
def read(p,fmt='json'):
    b=p.read_bytes();reads.append({'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
    return json.loads(b) if fmt=='json' else list(csv.DictReader(b.decode('utf-8-sig').splitlines()))

frames=read(O/'A_PAIRED_FRAME_COUNTS.csv','csv')
pframes=read(O/'P2_PAIRED_FRAME_COUNTS.csv','csv')
scopes=read(O/'A_36_SCOPE_CLASS_DECOMPOSITIONS.json')
p2=read(O/'P2_DEVELOPMENT_DECOMPOSITION.json')
for f in frames+pframes:
    for cl in ('ped','bike','moto','vru'):
        for prefix in ('n_','m0_','m1_'):f[prefix+cl]=int(f[prefix+cl])
    if 'seed' in f:f['seed']=int(f['seed'])
groups=defaultdict(list)
for f in frames:groups[f['arm'],f['seed'],f['condition']].append(f)
assert len(groups)==36 and len(frames)==12612 and len(pframes)==41
checks=0
for s in scopes+p2:
    fs=groups[s['arm'],s['seed'],s['condition']] if 'arm' in s else pframes
    cl={'pedestrian':'ped','bicycle':'bike','motorcycle':'moto','joint_VRU':'vru'}[s['class']]
    n=[f['n_'+cl] for f in fs];a=[f['m0_'+cl] for f in fs];b=[f['m1_'+cl] for f in fs]
    d={'frames':len(fs),'logs':len(set(f['log_token'] for f in fs)),'observations':sum(n),
       'hits_control':sum(n)-sum(a),'hits_candidate':sum(n)-sum(b),'target_frames':sum(x!=0 for x in n),
       'hit_delta':sum(a)-sum(b),'AnyMiss_control':len([x for x in a if x]),'AnyMiss_candidate':len([x for x in b if x]),
       'AnyMiss_delta':sum(bool(y)-bool(x) for x,y in zip(a,b)),
       'recovered_all_clear_frames':sum(bool(x) and not y for x,y in zip(a,b)),
       'new_failure_frames':sum(not x and bool(y) for x,y in zip(a,b)),
       'persistent_failure_frames':sum(bool(x) and bool(y) for x,y in zip(a,b)),
       'persistent_all_clear_frames':sum(not x and not y for x,y in zip(a,b)),
       'frames_fewer_misses':sum(y<x for x,y in zip(a,b)),'frames_more_misses':sum(y>x for x,y in zip(a,b)),
       'frames_equal_misses':sum(x==y for x,y in zip(a,b)),
       'observed_net_count_gains':sum(x-y for x,y in zip(a,b) if x>y),
       'observed_net_count_losses':sum(y-x for x,y in zip(a,b) if y>x),
       'persistent_failure_fewer_misses':sum(0<y<x for x,y in zip(a,b)),
       'persistent_failure_more_misses':sum(0<x<y for x,y in zip(a,b)),
       'persistent_failure_equal_misses':sum(x==y and x!=0 for x,y in zip(a,b))}
    # Different algebra: recoveries = candidate hits minus persistent-hit intersection.
    h0=[x-y for x,y in zip(n,a)];h1=[x-y for x,y in zip(n,b)]
    intersection_max=[min(x,y) for x,y in zip(h0,h1)]
    intersection_min=[max(0,x+y-z) for x,y,z in zip(h0,h1,n)]
    d.update({'recovered_observations_lower':sum(h1)-sum(intersection_max),
              'recovered_observations_upper':sum(h1)-sum(intersection_min),
              'lost_observations_lower':sum(h0)-sum(intersection_max),
              'lost_observations_upper':sum(h0)-sum(intersection_min)})
    for key,value in d.items():assert value==s[key],(key,value,s[key]);checks+=1
    assert s['recovered_observations_lower']-s['lost_observations_lower']==s['hit_delta']
    assert s['recovered_observations_upper']-s['lost_observations_upper']==s['hit_delta']
    if cl=='ped':
        improved=[f for f in fs if f['m1_ped']<f['m0_ped']]
        vals={'ped_count_improved_but_joint_still_failure_frames':sum(f['m1_vru']!=0 for f in improved),
              'ped_count_improved_and_joint_recovered_frames':sum(f['m0_vru']!=0 and f['m1_vru']==0 for f in improved),
              'ped_count_improved_remaining_ped_miss_frames':sum(f['m1_ped']!=0 for f in improved),
              'ped_count_improved_ped_clear_other_VRU_missed_frames':sum(f['m1_ped']==0 and f['m1_bike']+f['m1_moto']!=0 for f in improved)}
        for k,v in vals.items():assert v==s[k];checks+=1

# Exhaustively enumerate identities in small populations rather than testing the same formula twice.
bound_cases=0
for n in range(7):
    subsets={k:[set(s) for s in combinations(range(n),k)] for k in range(n+1)}
    for h0 in range(n+1):
        for h1 in range(n+1):
            feasible={len(b-a) for a in subsets[h0] for b in subsets[h1]}
            assert min(feasible)==max(0,h1-h0) and max(feasible)==min(h1,n-h0)
            bound_cases+=1

ped=[s for s in scopes if s['class']=='pedestrian' and s['seed']<2]
joint=[s for s in scopes if s['class']=='joint_VRU' and s['seed']<2]
same=[s for s in joint if s['AnyMiss_delta']==0]
summary={'full404_scopes':24,'ped_positive_scopes':sum(s['hit_delta']>0 for s in ped),
    'ped_negative_scopes':sum(s['hit_delta']<0 for s in ped),
    'joint_AnyMiss_unchanged':len(same),
    'unchanged_with_no_frame_transitions':sum(s['new_failure_frames']==s['recovered_all_clear_frames']==0 for s in same),
    'unchanged_with_canceling_transitions':sum(s['new_failure_frames']==s['recovered_all_clear_frames']>0 for s in same),
    'scope_count_not_independent_replicates':True,
    'complete_ped_improved_frame_comparison_occurrences':sum(s['frames_fewer_misses'] for s in ped),
    'complete_ped_improved_and_joint_recovered_occurrences':sum(s['ped_count_improved_and_joint_recovered_frames'] for s in ped),
    'complete_ped_improved_still_ped_missed_occurrences':sum(s['ped_count_improved_remaining_ped_miss_frames'] for s in ped),
    'complete_ped_improved_ped_clear_other_VRU_missed_occurrences':sum(s['ped_count_improved_ped_clear_other_VRU_missed_frames'] for s in ped)}
receipt={'status':'ALL_36_SCOPES_FOUR_CLASSES_AND_LOCAL_P2_SCALAR_DECOMPOSITIONS_VERIFIED',
    'at_utc':datetime.now(timezone.utc).isoformat(),'scalar_checks':checks,'enumerated_sharp_bound_cases':bound_cases,
    'summary':summary,'sources':reads,'compact_return_bytes':sum(r['bytes'] for r in reads),
    'same_author_separate_implementation':True,'external_independent_replication':False,
    'raw_source_replayed':False,'SDK_training_GT_matching':0}
# Portable read-only reproduction: never overwrite the original receipt.
print(json.dumps({'checks':checks,'bound_cases':bound_cases,'summary':summary}))
