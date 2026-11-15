# Results · P07

## Main results (ROI, n = 88; full-length Spearman–Brown ICC)

| Measure | Full-length ICC |
|---|---|
| gamma envelope mean | 0.99 |
| aperiodic exponent | 0.99 |
| gamma IF median | 0.96 |
| `legacy_std` (old v1 metric) | 0.90 |
| `slip_rate` | 0.86 |
| `burst_rate` | 0.86 |
| `if_sd` | 0.80 |
| `slow_sd` | 0.75 |
| **`burst_freq_sd` (primary)** | **0.69** (half-length 0.53) |
| `burst_freq_sd_z` | 0.07 |
| `burst_freq_sd_excess` | 0.00 |

Surrogate-normalised (`_z`, `_excess`) measures range from −0.12 (`tail_frac_excess`) to 0.72 (`slow_sd_z`). The gamma burst-frequency versions are at 0.07 (`burst_freq_sd_z`) and 0.00 (`burst_freq_sd_excess`). The full table is in `results/split_half_icc.csv`.

## Consequences
- The primary measure's within-recording reliability (0.69) clears the pre-specified floor of 0.6.
- The surrogate-normalised burst-frequency measures, which isolate instability beyond what the spectrum predicts, are not reliable in this dataset, so group tests built on them have little power. The surrogate-normalised slow-wander measures (`slow_sd_z` 0.72, `slow_sd_excess` 0.71) are moderately reliable.
