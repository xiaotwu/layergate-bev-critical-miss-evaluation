# New follow-up reproduction scope

Run `python studies/gate-mechanism-20261028/public_reproduce_compact.py` from the repository root. This standard-library check reconstructs all new compact scope/class/log/instance counts, target/frame transitions and the frozen criterion. It performs no model fitting, GPU work, GT rematching, SDK replay or old-job execution. Copied SDK metrics/support are explicitly outside compact recomputation; pooled AP is never averaged from folds. The new module `gates.py`, derived protocol, exact role/sampler audit, source hashes and numerical receipts accompany the records. Full local detector/checkpoint/prediction artifacts remain outside this public compact release. Same-process verification is not external replication.

The new [LaTeX project](../paper/mechanism-latex/README.md) and [paper](../paper/matched-conditioning-study.pdf) coexist with the original eleven-page report. The original read-only reproduction scope below remains historical and unchanged.

# Reproduction scope and commands

The repository reproduces compact-record analysis, not original detector training/inference. Install Python 3.11+ and clone the repository; the default scientific checks need only the standard library. They read released compact copies and print results. They do not need a GPU, torch, nuScenes SDK, NumPy, model fitting or network access.

Run from the repository root:

```bash
python scripts/verify_release.py
python analysis/r1/verify_saved_risk.py
python analysis/recovery/reproduce_recovery_compact.py
python analysis/recovery/verify_group_tables_sqlite.py --read-only
python analysis/risk_ranking/verify_ranking_alarm.py
```

- R1 reconstructs saved probabilities and verifies Brier/NLL on all404, target307 and equal-log descriptions. Its public wrapper removes the archived optional refit branch; the original default inference/scoring arithmetic is unchanged. All original nine models and three F3 constants are retained. The public entry cannot fit a model.
- R2 checks 36 arm/seed/condition scopes and four classes using saved paired counts, including the separate seed2 valid-fold cohort and local P2 development case. It verifies exact frame transitions and count-only individual-turnover bounds. These bounds are identification limits, not confidence intervals. Individual matched target identities were not retained and are not reconstructed.
- The R2 SQLite entry checks all 1,056 log-class and 528 fold-class rows. Always use `--read-only`; the archived source retains an optional create-only receipt branch when that flag is absent.
- R3 verifies all frozen score rows, tie-aware ranking, 10/20/30% budgets, equal-log and per-log/fold descriptions, all 36 development rules and all operating policies, 3,636 curve points, and finite tie permutations. Its default command writes nothing. Do not pass `--receipt` over an existing archived receipt.

The R3 `analyze_ranking_alarm.py` source is retained for inspection. Optional regeneration requires a separate scratch directory with that script and its compact input, without an existing `analysis/` directory; it deliberately refuses to overwrite accepted outputs. Do not run it over the release or claim a regeneration is new independent evidence.

All fractional alarm/capture counts are uniform label-independent tie expectations. Development-fixed policy rates divide expected counts; they are not expectations of ratios under a randomized execution. AUROC is null without both classes. Failure AP is distinct from detector mAP/pedAP. Original source/protocol/receipt SHA references are archival; public byte hashes are in the release manifest. Metadata-only local path redactions are recorded separately.

The released data include no original sensor files or full nuScenes annotation tables. Opaque sample/log tokens and derived labels/counts preserve grouping and pairing; use remains subject to applicable nuScenes conditions. This is not an unrestricted newly owned dataset. See LICENSES_AND_DATA.md.

Same-author numerical reproduction, publication portability and Academic Writing Toolkit document checks are not external independent scientific replication. No new detector evaluation or model training is authorized or triggered by these commands. Training costs, nulls, failures, missing A groups and NO_PROMOTION retain their archived meanings.

To build the manuscript, see `paper/latex/README.md`. A local TeX build can differ in PDF metadata or layout with engine/version differences; the supplied final PDF is the accepted exported version with all eleven pages visually checked. No theorem, calibration guarantee or driving requirement is certified by compilation.
