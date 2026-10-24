# Research development plan

**Status: proposed work, not executed results.** The present study is closed. This document identifies research questions and evidence that could strengthen a future application or study; it does not reopen stopped experiments or change current conclusions.

## 1. Applicant-led methodological explanation

Using the released records, the applicant can prepare a short method note and oral explanation of three questions:

- Why can additional pedestrian hits leave AnyMiss unchanged? Derive the relation between recovered frames, newly failed frames and the change in the failure count; distinguish observation-count changes from identifiable individual-target recoveries.
- Why do pooled and equal-log recall answer different questions? Explain their weighting and denominators, and construct a small illustrative example with an explicitly hypothetical label.
- Why can ranking, probability loss and a development-fixed alarm policy disagree? Explain ties, comparator choice, alarm-volume drift and the ratio-of-expected-counts convention.

The deliverable is the applicant's own derivation, annotated examples and responses to reviewer questions. These are learning and reasoning artifacts, not a new estimator or new experimental evidence. A contribution statement should identify only tasks actually completed by the applicant and confirmed by them. Code development in the present project used AI assistance; other individual tasks are not inferred from the author byline.

## 2. External critique of the existing analysis

A different researcher could reproduce selected compact results in a clean environment, inspect the detector-to-monitor role assignments and challenge the interpretation of the strongest positive example. Preserve their actual observations and the response to each substantive criticism. This would add independent scrutiny of the released analysis; it would not create an external driving dataset or validate safety effectiveness. No such external review is claimed to have occurred.

## 3. Highest-value empirical next question

**Does a policy frozen before evaluation retain useful failure capture and acceptable alarm burden on genuinely unseen capture logs?**

Fresh legally usable logs are a prerequisite and are not currently available in this project. Another split or more seeds on the already inspected mini logs cannot create fresh external evidence. Before viewing new evaluation outcomes, a future protocol should fix:

1. A detector/checkpoint, the monitor, features and all data roles, with a role audit that includes upstream detector training and selection.
2. A primary comparison against same-volume random expectation and a meaningful confidence baseline, a practical alarm budget, a minimum useful improvement and explicit stop criteria.
3. Separate assessments of ranking at a fixed budget and threshold transfer at its observed alarm volume. Report capture, unflagged failures, alarm burden, log-level heterogeneity and class/event support together.
4. A sampling and uncertainty plan based on the target estimand and dependence between logs and repeated targets. Determine required support from desired precision; do not manufacture sample size by treating correlated frames or seeds as independent.
5. A bounded computation plan and complete failure accounting. Preserve all seeds, comparators, unfavorable logs and unavailable quantities.

This question is a proposed evaluation study, not a promised performance improvement. Model selection itself can overfit finite evaluation data; see [Cawley and Talbot (2010)](https://www.jmlr.org/papers/v11/cawley10a.html).

## 4. Later extensions with distinct evidence requirements

For exact person-level recovery claims, a future endpoint computation should retain immutable annotation/instance identities and matched-prediction identities. The current unsaved identities cannot be reconstructed from frame counts.

For gate-efficacy claims, stronger detection baselines and matched control parameterization are needed, including control of the additional decoder LiDAR path. This is a separate, more expensive research question and is lower priority while fresh data and a credible matched comparison are unavailable.

Calibration and selective prediction require their own designs. Results for image-classification calibration or selective classifiers do not automatically transfer to critical-VRU AnyMiss: [Guo et al. (2017)](https://proceedings.mlr.press/v70/guo17a.html), [Geifman and El-Yaniv (2017)](https://papers.nips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html).

## Decision under the present constraints

Without fresh logs, prioritize methodological understanding, accurate individual attribution and external critique. Additional model or seed search on the same exposed mini data has limited value for establishing generalization. The current negative and mixed findings remain unchanged.
