# Layer-Gate BEV: Matched Conditioning Study

**Xiaotong Wu**<br>
Illinois Risk Lab (IRisk Lab), University of Illinois Urbana-Champaign<br>
xiaotongwu116@gmail.com | Research Advisor: Dr. Zhiyu Quan

**Question:** Does frame conditioning recover critical pedestrians beyond an equally sized input-independent gate?

The frozen useful-effect criterion was not met; candidate expansion stops.

Exploratory nuScenes mini follow-up: 162 outer frames from four capture logs; 1,347 pedestrian and 1,590 joint-VRU observations. Original seeds 0/1/2 reuse the same logs. Twelve new trajectories use paired U8000 parents, identical data draws and fixed 200+400 updates; both gates have 29,380 parameters. The shared decoder LiDAR route is frozen in both arms.

| Seed | Ped hits: C to D | Delta recall pooled / equal-log (pp) | AnyMiss: C to D /137 target frames | Ped recovered / newly lost |
| --- | --- | --- | --- | --- |
| 0 | 410 to 408 / 1347 | -0.148 / -0.157 | 131 to 131 | 5 / 7 |
| 1 | 486 to 488 / 1347 | +0.148 / -0.227 | 124 to 125 | 5 / 3 |
| 2 | 424 to 433 / 1347 | +0.668 / +0.796 | 130 to 130 | 9 / 0 |

C = constant-descriptor control; D = dynamic bounded gate.

Exact matched annotation observations recovered/newly lost are 5/7, 5/3, 9/0 (seeds 0/1/2). Joint all-clear recoveries/new failures are 0/0, 0/1, 0/0. AnyMiss means at least one missed critical VRU, not all targets missed; repeated observations are not distinct people.

Pooled-box SDK delta mAP/NDS/pedAP (percentage points, seeds 0/1/2): -0.004/-0.070/+0.028; -0.003/+0.017/-0.013; -0.000/-0.004/+0.058. Saved pedestrian outputs at score >=0.1: 4898 to 4920; 6537 to 6529; 5527 to 5553. Saved and all-range unmatched counts measure output burden, not official false positives or precision.

**Mechanism:** The original gate already had neutral initialization and a same-sized A3 constant control. The new bounded residual changes each inherited mixture by at most 0.1; the matched constant arm also pools real features before replacing descriptors. All original A arms already shared the decoder bypass, so its presence alone is not a differential confound. New identities distinguish recovery, new loss and within-frame exchanges. Decoder-input masking is an inference diagnostic, not a retrained path-free control.

**Limits:** The panel remains historically inspected mini data, with repeated instances, overlapping folds and low absolute detector AP. Seeds are model replicas, not new datasets. There is no matched unbounded dynamic arm, fresh-data validation, calibrated safety monitor, collision-risk or causal claim. Old failures, missingness and NO_PROMOTION remain unchanged. Same-process AI review and numerical checks are not external replication.

Actual new work: 7,200 scientific plus 3 engineering updates; 1.438 conservative GPU-reserved hours including CPU/I/O and inference. No old training or failed experiment was restarted. Code development used AI assistance.

[New paper](../paper/matched-conditioning-study.pdf) | [Compact reproduction](../studies/gate-mechanism-20261028/README.md) | [Historical one-page summary](archive/research-summary-v1.0.3.pdf)
