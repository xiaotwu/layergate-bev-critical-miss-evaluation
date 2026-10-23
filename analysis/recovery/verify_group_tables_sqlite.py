"""Independent SQL group-by checks of every R2 log/fold output row; read-only inputs."""
from pathlib import Path
from collections import defaultdict
import sqlite3,csv,json,hashlib,sys
P=Path(__file__).resolve().parent
O=P/'analysis_r2'
db=sqlite3.connect(':memory:')
db.execute('CREATE TABLE frames(arm TEXT, seed INT, condition TEXT, log_token TEXT, fold TEXT, n_ped INT,m0_ped INT,m1_ped INT,n_bike INT,m0_bike INT,m1_bike INT,n_moto INT,m0_moto INT,m1_moto INT,n_vru INT,m0_vru INT,m1_vru INT)')
cols=['arm','seed','condition','log_token','fold']+[p+c for c in ['ped','bike','moto','vru'] for p in ['n_','m0_','m1_']]
with (O/'A_PAIRED_FRAME_COUNTS.csv').open(encoding='utf-8-sig',newline='') as f:
    data=list(csv.DictReader(f))
db.executemany('INSERT INTO frames VALUES('+','.join('?' for _ in cols)+')',[tuple(r[k] for k in cols) for r in data])
fields=['frames','observations','hits_control','hits_candidate','target_frames','AnyMiss_control','AnyMiss_candidate',
    'recovered_all_clear_frames','new_failure_frames','persistent_failure_frames','persistent_all_clear_frames',
    'frames_fewer_misses','frames_more_misses','frames_equal_misses','observed_net_count_gains','observed_net_count_losses']
checked=0;groups=0
for dim,name in [('log_token','A_1056_LOG_CLASS_DECOMPOSITIONS.csv'),('fold','A_528_FOLD_CLASS_DECOMPOSITIONS.csv')]:
    with (O/name).open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    expected={(r['arm'],int(r['seed']),r['condition'],r[dim],r['class']):r for r in rows}
    assert len(expected)==len(rows)
    for cl,label in [('ped','pedestrian'),('bike','bicycle'),('moto','motorcycle'),('vru','joint_VRU')]:
        n='n_'+cl;a='m0_'+cl;b='m1_'+cl
        expressions=['COUNT(*)',f'SUM({n})',f'SUM({n}-{a})',f'SUM({n}-{b})',f'SUM({n}>0)',f'SUM({a}>0)',f'SUM({b}>0)',
          f'SUM({a}>0 AND {b}=0)',f'SUM({a}=0 AND {b}>0)',f'SUM({a}>0 AND {b}>0)',f'SUM({a}=0 AND {b}=0)',
          f'SUM({b}<{a})',f'SUM({b}>{a})',f'SUM({a}={b})',
          f'SUM(CASE WHEN {a}>{b} THEN {a}-{b} ELSE 0 END)',f'SUM(CASE WHEN {b}>{a} THEN {b}-{a} ELSE 0 END)']
        sql='SELECT arm,seed,condition,'+dim+','+','.join(expressions)+' FROM frames GROUP BY arm,seed,condition,'+dim
        for record in db.execute(sql):
            e=expected[(*record[:4],label)]
            for k,v in zip(fields,record[4:]):assert int(e[k])==v,(dim,record[:4],label,k);checked+=1
            assert int(e['AnyMiss_delta'])==int(e['new_failure_frames'])-int(e['recovered_all_clear_frames']);checked+=1
            assert int(e['hit_delta'])==int(e['observed_net_count_gains'])-int(e['observed_net_count_losses']);checked+=1
            groups+=1
assert groups==1584
rec={'status':'ALL_1056_LOG_AND_528_FOLD_CLASS_ROWS_RECONCILED_BY_SEPARATE_SQL_GROUPBY','scalar_checks':checked,
     'group_rows':groups,'endpoint_or_prediction_payload_read':0,'new_SDK_training_GT_matching':0,
     'same_author_independent_computation':True,'external_independent_replication':False}
if '--read-only' not in sys.argv:
    with (P/'GROUP_TABLE_SQL_VERIFICATION.json').open('x',encoding='utf-8') as f:json.dump(rec,f,indent=2)
print(json.dumps(rec))
