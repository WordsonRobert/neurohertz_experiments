# Results · H7

## Main results (AD vs CN, n = 65)

| Model | CV AUC (2.5–97.5%) | CV accuracy | LOSO AUC | LOSO accuracy |
|---|---|---|---|---|
| `legacy_std` alone | 0.48 (0.38–0.58) | 0.54 | 0.34 | 0.51 |
| `legacy_std`, exponent regressed out | 0.39 (0.28–0.48) | 0.54 | — | — |
| `legacy_std`, exponent + theta/alpha out | 0.41 (0.33–0.48) | 0.54 | — | — |
| 1/f exponent alone | 0.77 (0.76–0.78) | 0.68 | 0.75 | 0.68 |
| theta/alpha alone | 0.83 (0.81–0.84) | 0.72 | 0.82 | 0.71 |
| gamma envelope alone | 0.54 | 0.53 | 0.47 | 0.52 |
| `burst_freq_sd` alone | 0.54 | 0.57 | 0.48 | 0.59 |

Spearman ρ of `legacy_std` with: `burst_freq_sd` 0.76, alpha peak frequency −0.30, exponent 0.22, theta/alpha 0.22, EMG 0.21.

## Consequences
- The v1-style metric computed with clean preprocessing does not classify AD vs CN (AUC 0.48).
- The v1 result's accuracy (73.85%) is in the range reached here by slowing (theta/alpha, 72%) and the 1/f exponent (68%). It is not reached by any gamma instability measure.
- The v1 result is attributed to its processing (per-subject VMD settings, the VMD scale issue fixed in v2), not to gamma instability. The exact v1 computation was not re-run.
