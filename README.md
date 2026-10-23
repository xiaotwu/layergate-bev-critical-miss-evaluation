# Layer-Gate BEV: critical-miss evaluation

[中文说明](README.zh-CN.md) · [Paper PDF](paper/critical-miss-evaluation.pdf) · [LaTeX](paper/latex/) · [Reproduction guide](docs/reproducibility.md) · [Versioned release](https://github.com/xiaotwu/layergate-bev-critical-miss-evaluation/releases/tag/v1.0.0)

**Critical-Miss Evaluation in Small-Sample BEV: Log-Weight Sensitivity and Risk-Monitor Limits**

This repository accompanies a completed exploratory research report on **404 nuScenes mini frames from eight capture logs**. It documents negative and mixed findings, rather than a validated safety improvement. The three monitor seeds use the same logs and are not three independent datasets. The report is a learning/research manuscript; **no peer-reviewed acceptance, DOI, SOTA result, or deployed safety guarantee is claimed**.

## What is worth learning from this study?

1. **Aggregation can reverse an apparent effect.** In one A2/seed0/LiDAR comparison, pooled pedestrian recall changes by −0.2053 percentage points, while equal-log weighting gives +0.0756 points. Both describe the same observations under different weights; neither establishes external benefit.
2. **More pedestrian hits need not remove a failed frame.** For A2/seed1/clean, hits increase from 1,000/2,923 to 1,007/2,923, but all 17 count-improved frames still miss a pedestrian. Joint-VRU AnyMiss stays 288/307, with exactly the same failed-frame identities. A local P2 development example instead recovers one frame and creates one new failure. These are different explanations for an unchanged total.
3. **Probability scores, ranking, and alarms require separate evaluation.** The fixed three-feature monitor has inconsistent Brier/NLL improvements. Its frozen-score ranking extension finds limited internal enrichment at some operating points, but fails the predefined consistent-screening criterion.

These are a reproducible case analysis of established evaluation principles, not a new statistical estimator. Unsaved individual match identities prevent exact claims about which people were recovered or lost; frame-count changes and explicit turnover bounds are retained.

## Risk-monitor result: partial signal, important limits

The event is **AnyMiss: at least one critical VRU missed in a frame**, not collision risk. LR is the saved logistic/one-class-fallback score; Dev is development prevalence; Conf is one minus maximum pedestrian confidence.

At the primary fixed budget of **80/404 alarms (19.802%)**, all seeds and comparators are:

| Seed | LR expected capture / failures | Dev capture | Conf capture | Same-volume random expectation |
|---|---:|---:|---:|---:|
| 0 | 57.58/270 | 40.49 | 47.00 | 53.47 |
| 1 | 43.56/272 | 39.51 | 46.00 | 53.86 |
| 2 | 51.47/266 | 36.54 | 35.00 | 52.67 |

LR exceeds the weak Dev comparator in all three seeds, but exceeds random expectation in **only seed0**. Equal-log descriptions also lack a consistent advantage. The frozen consistency criterion therefore **fails**; no winning seed or budget is selected afterward.

When thresholds are chosen using development scores alone and then held fixed, LR shows excess captures of **+4.73/+13.18/+8.60** failures above random at each actual alarm volume. This is limited internal enrichment. Outer alarm fractions drift to **40.97%/23.90%/39.49%**, with gains concentrated in a few logs. Unflagged failure ratios remain **64.85%/63.04%/62.32%**. More captured failures at a larger alarm volume are not evidence of improvement at a fixed 20% budget.

Fractional alarm/capture counts are analytic expectations under uniform, label-independent boundary-tie allocation. Fixed-policy rates are ratios of expected counts, not expectations of ratios from an executed random policy. No randomized alarm system was deployed. Failure-event `AP_risk` is distinct from detector mAP/pedestrian AP; original detector outputs and metrics do not change in R1–R3.

![All three frozen-score risk–coverage descriptions](docs/figures/risk-coverage.png)

## Scope and limits

- Mini is the formal exploratory dataset, using a custom capture-log partition rather than the official challenge evaluation. Frames/instances repeat and fold training populations overlap; historical/adaptive exposure remains.
- The A matrix retains **176/192** primary groups; the missing sixteen F0/seed2 groups are not filled. Full404 gate effects use seeds0/1; seed2 has only its separate 243-frame/six-log valid-fold cohort.
- Nine monitor models and three predetermined one-class F3 fallbacks are retained. One-log development fitting and detector checkpoint selection on that log limit monitor evaluation.
- Detection baselines have low absolute AP; controls differ in parameterization. The A implementation has an additional decoder LiDAR path. B1 is LiDAR-only, so camera/clean equality is an expected negative control, not implemented fusion evidence.
- Mandatory P1 execution failure preserves the original **NO_PROMOTION** decision. B2/B3 remain conditionally stopped for the recorded resource/support/implementation limits.
- **Not established:** stable gate efficacy, consistent fixed-budget screening, calibrated safety risk, deployed alarm benefit, collision-risk reduction, causal effects, significance, or external generalization. No iid-frame confidence intervals or p-values are supplied.

See [study status](docs/study-status.md), [Chinese conclusions](reports/risk-ranking-conclusions.zh-CN.md), and all full-precision outputs rather than isolated positive examples.

## Reproduce the compact analysis

Python **3.11+**, standard library only; no GPU, SDK, model download, dataset download, or new training is needed for the following checks:

```bash
python scripts/verify_release.py
python analysis/r1/verify_saved_risk.py
python analysis/recovery/reproduce_recovery_compact.py
python analysis/recovery/verify_group_tables_sqlite.py --read-only
python analysis/risk_ranking/verify_ranking_alarm.py
```

The checks use frozen compact records. They are same-author numerical reproduction and publication portability checks, **not external independent replication**. The archived R3 verifier reports 27,741 checks; R2 includes saved-count decompositions and finite identification-bound enumerations. No old evaluator, fit, source-capture, or raw-backup operation is replayed. Candidate expansion is stopped.

This is a **compact analysis companion**, not an end-to-end detector training release. Raw sensor data, full nuScenes annotation tables, detector checkpoints, large saved prediction payloads, private machine paths, and execution/automation controls are not redistributed. The complete historical local archive is retained separately. See [data and rights](LICENSES_AND_DATA.md).

## Paper, provenance, and citation

The released 11-page PDF and `main.tex` match the accepted final R3 files. Full-precision results, exact copied inputs, and public-path deidentification are mapped in [the provenance record](provenance/SOURCE_COPY_RECORD.json); [the release manifest](provenance/PUBLIC_RELEASE_MANIFEST.json) binds the public files. Any path-redacted copy has its own hash and is not represented as byte-identical to its archive source.

The LaTeX source uses IEEEtran from a normal TeX distribution; third-party class/style files are not vendored. See [build instructions](paper/latex/README.md). References and upstream attribution are in [references.bib](paper/latex/references.bib).

Use [CITATION.cff](CITATION.cff) for the versioned repository citation. It identifies the GitHub maintainer account and does not invent a personal author identity, ORCID, publication venue, or DOI. Academic Writing Toolkit provides offline manuscript/README language-logic and BibTeX-structure checks recorded in `provenance/academic-writing-toolkit/`; these are not scientific peer review or online verification of the results. No repository-wide relicensing of the paper, code or upstream data is implied.
