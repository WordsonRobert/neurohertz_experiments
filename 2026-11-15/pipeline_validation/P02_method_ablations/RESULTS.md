# Results · P02

## Main results (split-half ICC of `burst_freq_sd`; |correlation with EMG|; n = 83)

| Dimension | Option | ICC (half) | EMG coupling |
|---|---|---|---|
| reference | average | 0.14 | 0.23 |
| reference | CSD | 0.57 | 0.34 |
| reference | REST | 0.34 | 0.22 |
| muscle | BSS-CCA | 0.34 | 0.01 |
| epochs | autoreject | 0.34 | 0.13 |
| aperiodic (judged on exponent) | specparam / IRASA | 0.98 / 0.98 | 0.14 / 0.20 |
| estimator | Hilbert / SST / VMD | 0.14 / 0.49 / 0.50 | 0.23 / 0.20 / 0.17 |
| median filter | single | 0.16 | 0.23 |
| surrogate chunk (judged on `burst_freq_sd_z`) | 15 / 30 / 60 s | −0.18 / −0.15 / −0.01 | 0.02 / 0.09 / 0.09 |

- No single change reached the reliability floor of 0.6.
- **Combined pipelines.**
    - `combo-csd`: split-half ICC 0.49; full-length ICC 0.66 (bootstrap 95% CI 0.46–0.79); EMG coupling 0.09. It passed the pre-stated rule.
    - `combo-rest`: full-length ICC 0.53; EMG coupling 0.14. It did not pass.
- **Final pipeline:** CSD reference, BSS-CCA muscle removal, autoreject, specparam, Hilbert estimator, single median filter, 30 s surrogate chunks.
- **Primary metric:** `burst_freq_sd` with age, sex and the 1/f exponent as covariates. The surrogate-normalised version (`burst_freq_sd_z`) had split-half ICC between −0.01 and 0.13 in every pipeline.

## Consequences
- The frozen analysis used `combo-csd`, and every confirmatory result (H1–H6) was computed with it.
- Even in the chosen pipeline the primary measure's reliability CI includes values below 0.6, which limits how well any group difference in it can be detected.
- The surrogate-normalised gamma measures are not reliable in ds004504, so they were not used as the primary.
