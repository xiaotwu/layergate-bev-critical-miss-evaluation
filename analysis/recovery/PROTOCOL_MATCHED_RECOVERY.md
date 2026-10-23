# R2: Recovery and new-failure decomposition from existing saved matches

User authorization: analyze existing matched records completely, explain critical pedestrian recall versus AnyMiss, update the paper; no new training. This is a new bounded descriptive analysis, not replay of a prior scientific executor or reopening of its budget. All original sources, failures, thresholds, labels, roles and versions remain read-only. The automation stays PAUSED.

## Frozen question and comparisons (before outcome extraction)

Primary: every available selected A1/A2/A3 versus same-seed, same-fold, same-condition selected A0. Original disk method names B0--B3 map to paper A0--A3. Seeds 0/1 use their complete four-fold, 404-frame population. Seed 2 is separately restricted to the original valid F1--F3, 243-frame population, never imputed to full404. All four existing conditions are retained. All 36 available seed/arm/condition scopes and 132 fold comparisons will be reported if the records support them. U-reference trajectories are not new treatment comparisons. B1 remains a separate architecture, not an A control.

The original P2 versus frozen B1 control clean development comparison is a separate local case only. It is analyzed if exact source-pinned records can be located. It cannot overturn P1 failure or NO_PROMOTION.

No new SDK, GT matching, detector/risk fitting, checkpoint loading, inference, label derivation from geometry, or change of thresholds. Read only existing saved per-frame/per-class counts and existing matched target identities if they were actually retained. Do not infer individual identity from equal counts. When identities are absent, observation turnover is only bounded by the saved counts; exact frame transitions and count changes may still be identified. Explicitly mark any unidentifiable target recovery/new-miss partition rather than manufacture it.

## Quantities and invariants

For identical eligible target-observation sets, if saved detection identities exist: recovered targets = previously missed/currently hit; lost targets = previously hit/currently missed; persistent misses and persistent hits complete the 2x2 table. Their difference must reproduce the original hit change. Report pedestrian, bicycle, motorcycle and joint VRU separately.

For each identical sample token and class/joint population, let m0 and m1 be the original saved miss counts. Frame transitions are: recovered all-clear frame (m0>0,m1=0), newly failed frame (m0=0,m1>0), persistently failed (both>0), persistently all-clear (both=0). AnyMiss delta = newly failed minus recovered frames. Split persistent failures by fewer/equal/more misses. Split pedestrian recovery under joint AnyMiss by remaining pedestrian and other-VRU misses. All-clear refers only to the specified original critical population.

When identities are absent, use sharp count-only per-frame bounds: target recovery R lies in [max(0,h1-h0), min(h1,n-h0)]; target loss L=R-(h1-h0). These are bounds on existing saved match outcomes, not estimates of actual turnover. Count-increase/decrease is not exact recovery/loss when the frame has multiple targets. No intervals over unknown target turnover are confidence intervals.

Aggregate per original log and fold; also provide repeated-instance descriptions only when original instance IDs are saved. Keep exact denominators, class support, target frames/all frames, sample/log counts, seed cohort and calibration state. Reconcile against accepted full404/log/fold tables. Carry mAP/NDS/pedAP and saved/unmatched output burden as unchanged accepted fields, with unavailable SDK values remaining null. No new statistical estimator, p-value, iid-frame CI, causal or safety claim.

## Bounded resource and provenance plan

Preparation metadata: <=64 MiB total newly returned bytes, <=8 MiB/file. A prior console-encoding failure after one metadata read is preserved; that manifest's actual size is charged once, plus subsequent successful reads. No scientific payload had been read before this protocol.

New saved-endpoint analysis: <=512 MiB source-return bytes, <=16 MiB/file, <=1,000 selected source files, serial CPU, 10 min per extraction process. The exact source list, sizes and original backup SHA pins will be frozen before full extraction. Metadata preparation carry is recorded, not erased. No prediction JSON, tensor, checkpoint or full dataset/source-tree scan is required. Output <=128 MiB/1,000 files; exceeding a bound or source/role inconsistency stops the affected operation with failures retained; no automatic retry or cap increase.

Freeze source identities with actual backup manifests; verify selected files by streaming SHA and before/after stat during the actual extraction. Store compact paired frame rows, source ledger and all scopes so the derived statistics can be reproduced without rereading original payload. Independently implement scalar verification from the compact rows; this is same-author implementation verification, not external independent replication. Preserve the prior manuscript and report sources. Save a version before editing the current LaTeX project, compile and visually inspect every page of the final exported PDF; create a new source/data package and a bounded create-only Windows increment.
