# Matched Layer-Gate BEV mechanism study: compact companion

This package reproduces arithmetic from saved critical-target matching statuses
for a fixed, historically exposed nuScenes mini panel. It is not an end-to-end
detector training release. The original study's failures, missing groups,
conditional stops, nulls, and original NO_PROMOTION decision are unchanged.

## Reproduce

Use Python 3.11+ and run from this directory:

```bash
python public_reproduce_compact.py
python public_reproduce_compact.py --self-test
```

The default command is read-only and uses only the Python standard library. It
checks public byte hashes, every scope/class/log numerator and denominator,
AnyMiss, equal-log descriptions, instance observation coverage, all released
target/frame comparison aggregates, gate differences, saved burden sums, and
the fixed descriptive criterion. Numerical float comparisons allow 1e-12.
It needs no GPU, torch, SDK, model/data download, fitting, or detector inference.

SDK mAP/NDS/pedestrian AP, SDK-filtered class support, and decoder input RMS are
copied local outputs and are not recomputed from this compact data. SDK metrics
come from pooled unique-token predictions, not averaged fold AP. Missing class
support is disclosed. Saved/unmatched output counts are supplied diagnostics,
not official false positives or precision. The compact verifier does not rerun
greedy matching or recheck spatial/point filtering: those require the full local
records and were covered by the separately retained new-result verification.

## Contents and compact schema

There are 30 pooled input scopes, each combining F1/F2, derived from 60 original
evaluation groups: dynamic/constant arms in four fixed views and a neutral U8000
reference in two views, across the original three seeds. Neutral retains the
already-trained same-fold/seed U8000 detector with a newly inserted gate whose
residual is zero, and receives no new adaptation.

`compact_index.json` maps scope keys to files. Each file stores schema_version,
scope_key and frames. A frame has exactly these abbreviated keys:

| Key | Meaning |
|---|---|
| s | sample token |
| l | capture-log token |
| f | detector fold |
| r | development or outer role |
| g | four encoder camera-mixture coefficients, in layer order |
| b | [saved_all, saved_pedestrian, unmatched_pedestrian_allrange] at score >= 0.1 |
| h | SHA256 of the original same-fold/view prediction JSON |
| t | critical-target tuples, described below |

Each target tuple is [annotation_token, instance_token, class_code,
matched_prediction_slot, match_distance_m, matched_prediction_score]. Codes p/b/m
mean pedestrian/bicycle/motorcycle. Unmatched targets have three null match
fields. Only already eligible critical GT observations are included; GT XY,
full annotation tables, raw sensor files and prediction boxes are omitted.

The combination of scope/fold/sample, prediction-file hash, and slot identifies
one original run-local output. Slots are not tracking identities and are not
compared as identities across runs. Immutable annotation tokens identify target
observations; instance tokens group repeated observations. Recovery/loss counts
are endpoint match-status changes, not independently verified person recovery.
AnyMiss means at least one critical VRU missed; empty-target frames do not fail.

`summary_results.json` retains full-precision scope summaries and every comparison
aggregate. Large per-frame/per-target lists and instance observation lists are
removed because compact inputs reconstruct their counts. The copied SDK and
decoder diagnostics remain labeled. `protocol.json` is a derived portable copy:
local root paths are descriptive placeholders; scientific settings are unchanged.
Its publication_role_audit includes explicit scene/log roles, ordered training
sample/scene tokens and pinned source hashes. Raw expected role frame counts and
actual sampling-metadata lengths remain separate. Role overlap across folds is
retained; this is not a fresh split.

`gates.py` is the byte-identical new gate implementation, supplied for inspection.
Its optional synthetic contract requires PyTorch; the compact reproduction script
does not import it. The rest of the detector, inherited checkpoints, full original
predictions, complete identity records and execution logs remain in the local
archive/backup, subject to upstream code and nuScenes data conditions. This package
does not redistribute those full artifacts or grant a new unrestricted dataset
license. Derived opaque IDs/counts remain subject to applicable nuScenes terms.

## Provenance and limits

`source_verification.json` preserves a portable copy of the actual PASS receipt
and its stated verification scope, including whether checkpoint bytes were hashed.
`provenance.json` records source hashes and publication transformations. Transformed
files have their own hashes and are not claimed byte-identical to source records.
`manifest.json` hashes the published bytes. `compact_verification.json` records the
export-time numerical check; the default command checks again without writing.

This is same-process AI code review and numerical reproduction, not external
researcher replication. Historical data exposure, repeated targets, few capture
logs, overlapping training populations, and shared inherited detector paths remain.
Seeds are model replicas on the same logs, not independent datasets. No iid-frame
confidence interval, p-value, causal/SOTA claim, calibrated safety risk, collision-
risk reduction, or external generalization follows. Neutral-reference changes are
unequal-update descriptions; decoder masking is a same-checkpoint inference
intervention, not a retrained control. No old risk score is transferred to changed
detector outputs. Code development used AI assistance.
