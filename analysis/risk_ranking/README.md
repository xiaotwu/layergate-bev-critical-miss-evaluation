# R3 frozen-score ranking/alarm analysis

Run `python analysis/risk_ranking/verify_ranking_alarm.py` from the root. This default entry reads only the released compact rows and outputs; it performs no fitting, writes no receipt, and needs only the Python standard library. Do not use `--receipt` to overwrite the original verification record.

Every seed, baseline, one-class fallback and fixed10/20/30% budget is retained. Primary full404 failure supports are270/272/266; target307 is a GT-defined diagnostic only. All36 development threshold/tie rules and9 seed/36 fold/72 log policies are supplied. The later within-log fixed-policy decomposition is explicitly diagnostic; it does not replace the failed primary criterion.

`AP_risk` is not detector mAP/pedAP. Fractional alarms and captures are exact uniform-tie expectations, not executed fractional frames. Development-policy rates are ratios of expected counts. Pooled scores mix fold models and cannot establish one deployment threshold. No safety/calibration/external-generalization guarantee follows.

The original protocol and analyzer source are retained. The analyzer refuses to overwrite an existing output directory; inspect it or reproduce into a separate scratch copy only. No old extractor, raw source capture or backup controller is included. Original score values and labels are unchanged; public provenance distinguishes archival hashes from deidentified metadata copies.
