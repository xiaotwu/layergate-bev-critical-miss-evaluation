# Critical-Miss Evaluation in Small-Sample BEV

**Log-Weight Sensitivity and Risk-Monitor Limits**

**Xiaotong Wu**  
Illinois Risk Lab (IRisk Lab), University of Illinois Urbana-Champaign  
xiaotongwu116@gmail.com | Research Advisor: Dr. Zhiyu Quan

## Research question

When do improved detection metrics translate into fewer critical misses, and do frozen risk scores help identify the remaining failures?

Exploratory nuScenes mini study: 404 frames from 8 capture logs. The original A matrix retains 176/192 groups; complete gate comparisons use seeds 0/1. Seed 2 has a separate 243-frame, 6-log cohort. Risk monitoring uses three model replicas on the same 404 frames.

## Key findings

### 1. Recall and frame failures

In A2/seed1/clean, pedestrian hits rise from 1,000/2,923 to 1,007/2,923, yet all 17 count-improved frames retain a pedestrian miss. Joint-VRU AnyMiss stays 288/307, with exactly the same failed-frame identities. Additional hits can leave a frame failed.

Separate P2 development case: fixed 8k updates, 41 frames, 1 log, 6 pedestrian instances/67 observations and 31 target frames. Other critical VRU classes have no support here.

|Local P2 metric|Control|P2|
|---|---|---|
|mAP (%)|2.1758|2.5328|
|NDS (%)|7.2406|9.2326|
|Pedestrian AP (%)|0|0|
|Pedestrian / joint hits|8/67|15/67|
|AnyMiss / target frames|30/31|30/31|

One frame recovers and one newly fails. Pedestrian outputs change from 2,175 to 2,177; all-range unmatched outputs from 2,165 to 2,160 (score >= 0.1). These are output-burden diagnostics, not official FP/precision. Aggregate AP gain does not improve pedestrian AP.

### 2. Aggregation matters

Observation weighting and equal-log weighting can reverse an effect direction. In one A2/seed0/LiDAR comparison, pooled pedestrian recall changes by -0.2053 percentage points, while equal-log recall changes by +0.0756 points. These describe the same population under different weights.

### 3. Ranking and alarm burden

The event is AnyMiss: at least one critical VRU missed in a frame, not collision risk. At 80/404 expected alarms (19.802%), captured failures are:

|Seed|LR / failures|Dev|Conf|Random|
|---|---|---|---|---|
|0|57.58/270|40.49|47.00|53.47|
|1|43.56/272|39.51|46.00|53.86|
|2|51.47/266|36.54|35.00|52.67|

LR exceeds random expectation only in seed 0; the frozen consistency criterion fails. Dev is same-fold development prevalence; Conf is one minus maximum pedestrian confidence. Fractional capture counts are uniform, label-independent tie expectations, not executed random alarms.

Development-fixed LR thresholds show limited internal enrichment, but alarm fractions drift to 40.97%/23.90%/39.49%; unflagged failure ratios remain 64.85%/63.04%/62.32% (seeds 0/1/2). Unflagged failure ratios divide expected counts. Original detector outputs and mAP/NDS/pedAP remain unchanged.

## Boundaries of the evidence

Eight historically inspected logs, repeated instances, overlapping folds, low absolute AP, imperfect controls and one-log development fitting limit inference. External replication is absent. P1 failure preserves NO_PROMOTION; B2/B3 retain resource/support/implementation stops. Stable gate efficacy, calibrated safety risk and external generalization remain unestablished.

## Next question: proposed, not executed

Can a frozen monitor retain failure enrichment and stable alarm cost on fresh capture logs? Predefine comparators, budget and stopping criteria; report per-log and residual failures. Re-splitting exposed mini data is not fresh validation. This is a proposed next study, not an executed result.

Contribution: a reproducible case analysis of established evaluation principles, with frozen compact inputs and complete result tables; no new estimator. Code development used AI assistance.

[Full technical report](../paper/critical-miss-evaluation.pdf) | [Reproduction guide](reproducibility.md) | [One-page PDF](research-summary.pdf)
