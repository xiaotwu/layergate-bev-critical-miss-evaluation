# R3: Ranking and alarm utility of the existing frozen risk scores

Authorized by the user's “按你说的来” in response to the proposed existing-score ranking/alarm analysis. No new detector/risk fitting, detector inference, SDK, GT matching, original prediction/checkpoint reads or automatic follow-up. All old data/labels/thresholds/roles/seeds, failures, nulls and NO_PROMOTION remain unchanged; sources/ and prior artifacts are read-only. The R2 manuscript/PDF will be preserved before the new results are incorporated.

This protocol is frozen before computing these new ranking outcomes. It is an exploratory extension on historically inspected mini, not an independent preregistered confirmation or a fresh test set.

## Inputs and scores (no candidate expansion)

Read only exact source-pinned R1 compact frame inputs (1698 rows), outer saved probabilities (1212 = 404 x 3 seeds), twelve saved model/fallback records, and original result/role metadata. All original F0--F3 cells and seeds 0/1/2 are retained, including three one-class F3 fallbacks. No new model is fit.

Three fixed alarm scores, higher meaning higher predicted failure:
1. R1's saved logistic/fallback probability (sole learned candidate).
2. Original same-fold development-prevalence probability (existing constant baseline).
3. One fixed inference-visible heuristic: 1 minus maximum saved pedestrian confidence at score>=0.1 (third existing feature; zero maximum if no saved pedestrian output). No feature or orientation search.

For deterministic tie handling and consistency between development scalar arithmetic and saved outer probabilities, analysis scores use decimal rounding to 12 places. Original probabilities are retained unmodified; the maximum rounding/reconstruction error is reported. This is not calibration. The frozen monitor is evaluated arithmetically on the 486 existing development feature rows solely to fix the operating thresholds; no detector inference or model update is involved. All outcome metrics use the original AnyMiss failure label. GT target presence is only a diagnostic evaluation stratum, never a score input or an operating-policy condition.

## Ranking endpoints

Primary population: all404 outer frames/eight logs for each seed. Original307 target-containing frames are a separately labelled diagnostic stratum. Compute tie-aware AUROC, threshold-grouped average precision (AP), and expected-tie AURC. AUROC is null when either binary class is absent; no imputed discrimination. AP with no positives is null; an all-positive AP=1 is not evidence of discrimination. AURC averages failure rates among each possible positive retained count, retaining the lowest risk scores. It is a descriptive discrete curve area, not a risk guarantee.

Report pooled out-of-fold scores and equal-log/per-log/per-fold descriptions separately. Pooled outputs come from different fold models and cannot by themselves validate a single deployable threshold or case-level discrimination. Constant within-log scores can discriminate between fold prevalence groups when pooled; this is disclosed rather than interpreted as within-log ranking.

## Fixed alarm budgets and ties

Primary illustrative screening budget: 20%; diagnostic budgets: 10%,30%, fixed now, not selected after outcomes. For N rows, K=floor(budget*N) highest-score alarms. All members of a boundary tie group receive the same fractional alarm weight so total expected alarms equal K. This is exact expectation under label-independent uniform tie allocation, not an executed randomized policy. No new random seeds or arbitrary sample-token tie order.

Report expected captured failures / all failures, captured failures / alarms, unflagged failures / unflagged frames, actual K/N, and excess captured failures versus analytic random alarms K*P/N. Random alarm expectation is used for capture/risk only; population prevalence is not falsely called the exact finite-sample expected random AP. At zero alarms precision is null; at zero retained frames residual risk is null. Equal-log budgets are applied separately inside each log; disclose differing integer budgets. No operational-performance conclusion is drawn from lowering retained coverage alone.

## Development-fixed operating point

Independently of the outer ranking curves, fix one threshold per seed/fold/score using development score values alone, aiming for floor(0.2*n_dev) expected alarms on that development log. The cutoff and boundary-tie probability are frozen before looking at the outer labels; apply them unchanged to all outer frames. Report actual outer alarm rates, failure-capture and residual-failure rates, including one-class F3 and constants. The nominal budget is an illustrative research choice, not a driving requirement. Report apparent improvements together with actual alarm burden; no benefit is inferred merely from more alarms.

## Interpretation and stopping

A consistent internal screening advantage requires the sole learned candidate to capture strictly more failures at primary20% than both existing prevalence and fixed-confidence baselines in all three pooled seed descriptions, exceed analytic random capture in all three, and have no reversed equal-log excess-random direction. Otherwise report mixed/negative or limited seed/stratum observations, never select a winning seed or budget. Positive ranking with unchanged poor Brier/NLL would support only exploratory offline screening utility, not calibrated probabilities, improved detection, deployed alarm efficacy or collision-risk reduction.

The development-fixed point is separately reported with every actual alarm burden and failure denominator; it cannot inherit a guarantee from the descriptive top-K curves. Lack of class support or a constant fallback is retained and may make particular discrimination quantities null. No further feature/regularization/model/GPU search follows this analysis, regardless of outcome. Original risk Brier/NLL are carried unchanged, not used to choose a new monitor. No iid-frame confidence intervals, p-values, significance, causal or external-generalization claims.

## Resource and delivery bounds

New compact scientific source reads <=32 MiB, <=8 MiB/file, <=100 files; output <=32 MiB/1000 files; serial CPU, 10 min per analysis process. Exact source list/bytes/accepted SHA pins will be frozen before the actual pass. Controlled returned-byte ledgers and failures are retained; prior uninstrumented code/schema metadata reads are separate and not claimed zero physical I/O. No original raw audit/source capture/copy/native/SDK operation is replayed. Verify the new metrics with separately written pairwise/rank calculations and small finite enumerations, clearly same-author rather than external replication. Deliver complete source/compact data, Chinese interpretation, updated English paper, compile/all-page visual checks, and a bounded create-only Windows increment with native readback. Automation remains PAUSED.
