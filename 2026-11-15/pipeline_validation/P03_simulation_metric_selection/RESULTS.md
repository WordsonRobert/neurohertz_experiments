# Results · P03

## Main results (final run)

| Rank | Metric | Specificity score | Jitter correlation | Eligible |
|---|---|---|---|---|
| 1 | `burst_freq_sd_z` | 0.674 | 0.90 | yes |
| 2 | `burst_freq_sd_excess` | 0.660 | 0.90 | yes |
| 3 | `burst_freq_sd` | 0.613 | 1.00 | yes |
| 4 | `slow_frac_excess` | 0.212 | 1.00 | yes |
| 5 | `burst_if_sd` | 0.210 | 0.70 | no |

- The simulation-selected metric was `burst_freq_sd_z`.
- The frozen primary is `burst_freq_sd`, by a recorded override (P09). The reason given: `burst_freq_sd_z` had split-half ICC −0.01 to 0.13 on real data (P02), and the raw metric's main simulated nuisance (the 1/f slope) is handled by the exponent covariate.
- Top metric under each setting variant:

| Variant | Top metric | Score |
|---|---|---|
| estimator-hilbert | `slow_frac_excess` | 0.68 |
| estimator-sst | `if_awsd` | 0.71 |
| estimator-vmd | `legacy_std` | 0.40 |
| median-single | `burst_freq_sd` | 0.67 |
| surr_chunk-s15 | `burst_freq_sd_excess` | 0.72 |
| surr_chunk-s60 | `if_env_coupling_z` | 0.66 |

## Consequences
- In simulation, `burst_freq_sd` tracks jitter perfectly in rank (1.00), but it also responds to the 1/f slope. Every confirmatory test therefore adjusts for the 1/f exponent.
- Which metric ranks first depends on the estimator and surrogate settings. The metric choice is therefore conditional on the pipeline chosen in P02.
