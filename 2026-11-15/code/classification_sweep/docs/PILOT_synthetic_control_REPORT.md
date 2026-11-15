> Cloud pilot, 2026-11-15: 28 synthetic subjects (10 CN, 10 AD, 8 FTD), mechanism nav11_pv_output, k = 1.0, 300 permutations. It checks the plumbing and ground-truth recovery only; it is not a real-data result.

# Classification sweep: elimination report (EXPLORATORY)

Dataset synthetic; n = 28 ({'CN': 10, 'AD': 10, 'FTD': 8}). Verdict rules are in the header of sweep/60_report.py and were fixed before any real-data result existed.

| Explanation | Verdict | Evidence |
|---|---|---|
| E0 effect at 35-45 Hz | PRESENT | clusters overlapping 35-45 Hz: logpsd_csd 1, periodic_csd 1 |
| E1 muscle | eliminated | ROI 35-45 Hz t: all epochs -4.59, lowest-EMG 25% -3.99, +EMG covariate -6.61, no BSS-CCA nan |
| E2 ocular/frontal-polar | eliminated | frontal-polar burst excess AD-CN t = -0.68, p = 0.550 |
| E3 aperiodic | no fractal cluster | significant AD-CN clusters: fractal 0 (any frequency); periodic in 35-45 Hz 1; periodic ROI 35-45 t = -5.89 |
| E4 vigilance | eliminated | per-stratum t (low->high alpha/theta): -12.35, -13.69, -12.97, -18.98 |
| E5 alpha harmonics | eliminated | 1:4 locking AD-CN t = -0.72, p = 0.533; rho with periodic 35-45 = -0.03 |
| E6 sharp transients | eliminated | transient rate AD-CN t = -1.92, p = 0.086; gamma change without transients t = 1.93, p = 0.081 |
| E7 notch/filter edge | not suspected | logpsd_csd 30.5-44.0 Hz; periodic_csd 30.8-43.9 Hz |
| E8 medication (signature only) | untestable | beta-range (15-30 Hz) AD-CN clusters: 13.0-25.0 Hz sign +1 [Cz O1 O2 P3 P4 Pz] |

## All significant spectral clusters (p_FWER < 0.05)

| family              | contrast   | covariates   |   sign |     mass |   p_fwer |   f_lo |   f_hi |   f_peak | ch_peak   |   n_nodes | channels                                                   |
|:--------------------|:-----------|:-------------|-------:|---------:|---------:|-------:|-------:|---------:|:----------|----------:|:-----------------------------------------------------------|
| logpsd_csd          | AD-CN      | age_sex      |     -1 |  655.381 |    0.01  | 30.5   | 44     |   36     | O2        |       127 | C3 C4 Cz O1 O2 P3 P4 Pz                                    |
| logpsd_csd          | AD-CN      | age_sex      |      1 |  363.145 |    0.03  | 13     | 25     |   19     | O2        |        76 | Cz O1 O2 P3 P4 Pz                                          |
| logpsd_csd          | AD-CN      | age_sex_emg  |     -1 | 1719.81  |    0.003 | 31     | 47.5   |   37     | O2        |       315 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T4 T5 T6    |
| logpsd_csd          | AD-CN      | age_sex_emg  |      1 |  433.16  |    0.037 | 12     | 26     |   19     | O2        |        86 | Cz O1 O2 P3 P4 Pz                                          |
| logpsd_csd          | FTD-CN     | age_sex      |     -1 | 1551.79  |    0.003 | 28.5   | 45     |   33.5   | F3        |       272 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz T3 T4 T5 T6                |
| logpsd_csd          | FTD-CN     | age_sex      |      1 |  422.622 |    0.033 | 14     | 24.5   |   22     | F4        |        80 | Cz F3 F4 F7 F8 Fp1 Fp2 Fz                                  |
| logpsd_csd          | FTD-CN     | age_sex_emg  |     -1 | 2637.61  |    0.003 | 28.5   | 47.5   |   33.5   | F3        |       395 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz O1 P3 T3 T4 T5 T6          |
| logpsd_csd          | FTD-CN     | age_sex_emg  |      1 |  500.332 |    0.04  | 13     | 25.5   |   22     | F4        |        90 | Cz F3 F4 F7 F8 Fp1 Fp2 Fz                                  |
| logpsd_csd          | AD-FTD     | age_sex      |      1 | 1135.44  |    0.003 | 29     | 42.5   |   35     | F3        |       210 | C3 Cz F3 F4 F7 F8 Fp1 Fp2 Fz T3 T4 T5 T6                   |
| logpsd_csd          | AD-FTD     | age_sex      |     -1 |  957.245 |    0.003 | 30.5   | 43.5   |   39.5   | O1        |       127 | O1 O2 P3 P4 Pz                                             |
| logpsd_csd          | AD-FTD     | age_sex      |      1 |  458.947 |    0.01  | 15     | 27     |   20.5   | O1        |        83 | Cz O1 O2 P3 P4 Pz                                          |
| logpsd_csd          | AD-FTD     | age_sex      |     -1 |  456.399 |    0.01  | 11     | 26     |   21     | Fz        |        82 | F3 F4 F7 F8 Fp2 Fz                                         |
| logpsd_csd          | AD-FTD     | age_sex_emg  |      1 | 1525.92  |    0.003 | 27.5   | 44.5   |   36.5   | Fz        |       257 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz T3 T4 T5 T6                |
| logpsd_csd          | AD-FTD     | age_sex_emg  |     -1 | 1127.87  |    0.003 | 30.5   | 46.5   |   39     | P3        |       143 | O1 O2 P3 P4 Pz                                             |
| logpsd_csd          | AD-FTD     | age_sex_emg  |      1 |  489.336 |    0.023 | 15     | 27     |   20.5   | O1        |        86 | Cz O1 O2 P3 P4 Pz                                          |
| logpsd_csd          | AD-FTD     | age_sex_emg  |     -1 |  478.149 |    0.023 | 10.5   | 26     |   20     | Fz        |        78 | F3 F4 F8 Fp1 Fp2 Fz                                        |
| logpsd_avg          | AD-CN      | age_sex      |     -1 |  855.775 |    0.003 | 30     | 46.5   |   35.5   | O2        |       156 | C3 F7 O1 O2 P3 P4 Pz T3                                    |
| logpsd_avg          | AD-CN      | age_sex      |      1 |  337.265 |    0.01  | 13.5   | 25     |   19.5   | P3        |        82 | Cz O1 O2 P3 P4 Pz T5 T6                                    |
| logpsd_avg          | FTD-CN     | age_sex      |     -1 |  577.497 |    0.003 | 28.5   | 44.5   |   33     | F3        |       101 | C3 F3 F4 F7 Fp2 Fz                                         |
| logpsd_avg          | FTD-CN     | age_sex      |      1 |  313.564 |    0.017 | 14     | 24.5   |   22     | F4        |        60 | F3 F4 Fp1 Fz                                               |
| logpsd_avg          | AD-FTD     | age_sex      |     -1 | 1195.57  |    0.003 | 30     | 46     |   37     | O1        |       148 | O1 O2 P3 P4 Pz                                             |
| logpsd_avg          | AD-FTD     | age_sex      |      1 |  591.013 |    0.01  | 13.5   | 27     |   23.5   | O2        |       127 | C3 C4 Cz O1 O2 P3 P4 Pz T3                                 |
| logpsd_avg          | AD-FTD     | age_sex      |      1 |  360.921 |    0.027 | 29.5   | 40.5   |   35     | F3        |        65 | F3 F4 Fz                                                   |
| logpsd_avg          | AD-FTD     | age_sex      |     -1 |  344.625 |    0.03  | 11.5   | 25     |   17.5   | Fz        |        58 | F3 F4 Fz                                                   |
| logpsd_csd_lowemg50 | AD-CN      | age_sex      |     -1 |  568.547 |    0.01  | 30.5   | 43.5   |   37.5   | O2        |       115 | C3 Cz O1 O2 P3 P4 Pz                                       |
| logpsd_csd_lowemg50 | FTD-CN     | age_sex      |     -1 | 1310.15  |    0.003 | 28.5   | 45     |   33.5   | F4        |       244 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz T3 T4 T5 T6                |
| logpsd_csd_lowemg50 | FTD-CN     | age_sex      |      1 |  338.44  |    0.043 | 14     | 24.5   |   20.5   | F4        |        74 | Cz F3 F4 F7 F8 Fp1 Fp2 Fz                                  |
| logpsd_csd_lowemg50 | AD-FTD     | age_sex      |      1 | 1039.7   |    0.003 | 29     | 43.5   |   35     | F3        |       194 | C3 C4 F3 F4 F7 F8 Fp1 Fp2 Fz T3 T4 T5 T6                   |
| logpsd_csd_lowemg50 | AD-FTD     | age_sex      |     -1 |  810.934 |    0.01  | 30.5   | 44     |   38     | O1        |       124 | O1 O2 P3 P4 Pz                                             |
| logpsd_csd_lowemg50 | AD-FTD     | age_sex      |      1 |  451.543 |    0.017 | 12.5   | 27     |   21     | O2        |        91 | C3 C4 Cz O1 O2 P3 P4 Pz T3                                 |
| logpsd_csd_lowemg50 | AD-FTD     | age_sex      |     -1 |  293.321 |    0.023 | 15     | 25.5   |   21     | Fz        |        58 | F3 F4 F8 Fp1 Fp2 Fz                                        |
| logpsd_csd_lowemg25 | AD-CN      | age_sex      |     -1 |  506.184 |    0.003 | 31.5   | 43     |   36.5   | O1        |       102 | C3 Cz O1 O2 P3 P4 Pz                                       |
| logpsd_csd_lowemg25 | FTD-CN     | age_sex      |     -1 | 1101.7   |    0.003 | 29     | 43.5   |   33     | F3        |       208 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz T3 T4 T5 T6                |
| logpsd_csd_lowemg25 | FTD-CN     | age_sex      |      1 |  222.622 |    0.017 | 14.5   | 24     |   22     | F4        |        49 | F3 F4 F7 F8 Fp1 Fp2 Fz                                     |
| logpsd_csd_lowemg25 | AD-FTD     | age_sex      |      1 |  880.155 |    0.003 | 29.5   | 41     |   35     | F3        |       171 | C4 F3 F4 F7 F8 Fp1 Fp2 Fz T3 T4 T5 T6                      |
| logpsd_csd_lowemg25 | AD-FTD     | age_sex      |     -1 |  658.094 |    0.01  | 30.5   | 44     |   38     | O1        |       116 | O1 O2 P3 P4 Pz                                             |
| logpsd_csd_lowemg25 | AD-FTD     | age_sex      |      1 |  185.018 |    0.037 | 17     | 26     |   20.5   | O2        |        43 | Cz O1 O2 P3 P4 Pz T6                                       |
| logpsd_csd_lowemg25 | AD-FTD     | age_sex      |     -1 |  180.195 |    0.04  | 15.5   | 24     |   19     | Fz        |        38 | F3 F4 Fp2 Fz                                               |
| periodic_csd        | AD-CN      | age_sex      |     -1 | 1973.04  |    0.003 | 30.762 | 43.945 |   37.109 | O2        |       354 | C3 C4 Cz F7 O1 O2 P3 P4 Pz T3 T4                           |
| periodic_csd        | AD-CN      | age_sex      |      1 |  993.462 |    0.02  | 17.822 | 25.879 |   21.973 | O1        |       184 | C3 C4 Cz F7 O1 O2 P3 P4 Pz T3 T5                           |
| periodic_csd        | AD-CN      | age_sex_emg  |     -1 | 4234.53  |    0.003 | 30.762 | 47.363 |   43.701 | O1        |       712 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T3 T4 T5 T6 |
| periodic_csd        | AD-CN      | age_sex_emg  |      1 | 1947.32  |    0.007 | 17.578 | 33.203 |   21.729 | O1        |       396 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T3 T4 T5 T6 |
| periodic_csd        | FTD-CN     | age_sex      |     -1 | 3307.33  |    0.003 | 29.785 | 45.166 |   34.424 | F3        |       561 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz T3 T4 T5 T6                |
| periodic_csd        | FTD-CN     | age_sex      |      1 | 1778.75  |    0.013 | 17.578 | 26.123 |   21.973 | F4        |       275 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz T3 T4 T5 T6                |
| periodic_csd        | FTD-CN     | age_sex_emg  |     -1 | 5060.85  |    0.003 | 29.053 | 47.363 |   38.574 | Fp1       |       753 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz T3 T4 T5 T6                |
| periodic_csd        | FTD-CN     | age_sex_emg  |      1 | 2229.64  |    0.01  | 17.578 | 26.855 |   21.973 | F4        |       328 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz T3 T4 T5 T6                |
| periodic_csd        | AD-FTD     | age_sex      |      1 | 1223.77  |    0.003 | 17.09  | 27.344 |   20.752 | O1        |       188 | Cz O1 O2 P3 P4 Pz                                          |
| periodic_csd        | AD-FTD     | age_sex      |      1 | 2428.98  |    0.003 | 30.029 | 44.434 |   36.865 | F4        |       377 | F3 F4 F7 F8 Fp1 Fp2 Fz T3 T4 T5 T6                         |
| periodic_csd        | AD-FTD     | age_sex      |     -1 | 1577.12  |    0.003 | 15.625 | 26.367 |   22.461 | F4        |       239 | C4 F3 F4 F7 F8 Fp1 Fp2 Fz T3 T4 T5 T6                      |
| periodic_csd        | AD-FTD     | age_sex      |     -1 | 2711.54  |    0.003 | 30.273 | 47.119 |   39.795 | O1        |       328 | C3 C4 Cz O1 O2 P3 P4 Pz                                    |
| periodic_csd        | AD-FTD     | age_sex_emg  |      1 | 3283.78  |    0.003 | 27.832 | 44.434 |   36.377 | Fz        |       486 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz T3 T4 T5 T6                |
| periodic_csd        | AD-FTD     | age_sex_emg  |     -1 | 2929.99  |    0.003 | 30.273 | 47.363 |   40.527 | O2        |       349 | C3 C4 Cz O1 O2 P3 P4 Pz                                    |
| periodic_csd        | AD-FTD     | age_sex_emg  |     -1 | 1766.83  |    0.007 | 15.381 | 26.367 |   22.461 | F4        |       254 | C4 F3 F4 F7 F8 Fp1 Fp2 Fz T3 T4 T5 T6                      |
| periodic_csd        | AD-FTD     | age_sex_emg  |      1 | 1329.27  |    0.013 | 17.09  | 27.344 |   23.438 | O1        |       188 | C3 Cz O1 O2 P3 P4 Pz                                       |
| fractal_csd         | FTD-CN     | age_sex      |     -1 |  605.073 |    0.05  | 18.555 | 27.588 |   21.24  | F3        |       140 | C3 F3 F4 F7 F8 Fp1 Fp2 Fz                                  |
| fractal_csd         | AD-FTD     | age_sex      |      1 |  809.506 |    0.02  | 30.518 | 46.875 |   41.748 | O2        |       147 | O1 O2 P4                                                   |
| fractal_csd         | AD-FTD     | age_sex      |      1 |  552.515 |    0.04  | 18.311 | 28.076 |   21.24  | F7        |       133 | F3 F7 Fp1 Fp2 Fz T3                                        |
| periodic_avg        | AD-CN      | age_sex      |     -1 | 3329.72  |    0.003 | 31.006 | 46.387 |   33.447 | O1        |       644 | C3 C4 Cz F7 F8 Fp1 Fp2 O1 O2 P3 P4 Pz T3 T4 T5 T6          |
| periodic_avg        | AD-CN      | age_sex      |      1 | 1271.07  |    0.023 | 18.066 | 25.879 |   22.949 | O1        |       217 | C3 C4 Cz F7 Fp1 Fz O1 O2 P3 P4 Pz T3 T4 T5 T6              |
| periodic_avg        | FTD-CN     | age_sex      |     -1 | 1100.67  |    0.007 | 29.785 | 44.922 |   34.424 | F3        |       182 | F3 F4 Fp1 Fz                                               |
| periodic_avg        | FTD-CN     | age_sex      |      1 |  738.463 |    0.013 | 16.602 | 25.146 |   22.217 | F4        |       102 | C3 C4 Cz F3 F4 Fp1 Fz                                      |
| periodic_avg        | AD-FTD     | age_sex      |     -1 | 4440.99  |    0.003 | 30.029 | 47.119 |   39.307 | O1        |       658 | C3 C4 Cz F7 F8 Fp1 Fp2 O1 O2 P3 P4 Pz T3 T4 T5 T6          |
| periodic_avg        | AD-FTD     | age_sex      |      1 | 1501.19  |    0.01  | 16.846 | 27.344 |   23.682 | O2        |       227 | C3 C4 Cz F8 O1 O2 P3 P4 Pz T3 T5 T6                        |
| periodic_avg        | AD-FTD     | age_sex      |      1 |  933.065 |    0.017 | 30.762 | 42.969 |   36.865 | F4        |       141 | F3 F4 Fz                                                   |
| periodic_avg        | AD-FTD     | age_sex      |     -1 |  658.979 |    0.027 | 16.846 | 25.635 |   20.264 | F4        |        95 | F3 F4 Fz                                                   |

## Subject-level measures, group tests (Freedman-Lane, age + sex, 5000 perms)

| measure                  |   AD-CN |   AD-FTD |   FTD-CN |
|:-------------------------|--------:|---------:|---------:|
| alpha_1to4_z             |  0.5331 |   0.5123 |   0.2086 |
| burst_excess_fp          |  0.5505 |   0.0152 |   0.0238 |
| burst_excess_roi         |  0.0132 |   0.0982 |   0.1316 |
| emg_mean                 |  0.3507 |   0.4663 |   0.5237 |
| fractal_offset           |  0.0692 |   0.1364 |   0.3819 |
| fractal_slope            |  0.6949 |   0.3277 |   0.4533 |
| gamma_no_transient_delta |  0.0808 |   0.5105 |   0.1846 |
| iaf                      |  0.0568 |   0.3917 |   0.8    |
| logpow_35_45             |  0.0004 |   0.0002 |   0.8526 |
| logpow_35_45_lowemg      |  0.0006 |   0.0002 |   0.9258 |
| pac_alpha_z              |  0.2991 |   0.1834 |   0.7986 |
| pac_theta_z              |  0.1048 |   0.2771 |   0.0506 |
| periodic_30_48           |  0.0002 |   0.0002 |   0.7013 |
| periodic_35_45           |  0.0002 |   0.0002 |   0.6715 |
| theta_alpha              |  0.4623 |   0.8346 |   0.5517 |
| transient_rate           |  0.0864 |   0.5287 |   0.2667 |
| vigilance_mean           |  0.5139 |   0.7528 |   0.7193 |

## Burst types (bursts_p95): K = 5, stability ARI 0.74

|   type |   share | auto_name                                       |   frac_roi |   mean_f_mean |   mean_nb_index |   mean_emg_coact |
|-------:|--------:|:------------------------------------------------|-----------:|--------------:|----------------:|-----------------:|
|      0 |   0.24  | low spread, low laterality, high nb_index       |      0.294 |        36.551 |          -0.302 |           -0.001 |
|      1 |   0.118 | high spread, high log_dur_cycles, low abs_chirp |      0.247 |        36.13  |          -0.265 |            0.033 |
|      2 |   0.067 | high spread, low log_f_mad, low log_dur_cycles  |      0.248 |        36.237 |          -0.327 |           -0.005 |
|      3 |   0.49  | low spread, low nb_index, low log_dur_cycles    |      0.348 |        36.747 |          -0.32  |            0.002 |
|      4 |   0.085 | high spread, high abs_chirp, high log_amp       |      0.155 |        37.069 |          -0.284 |           -0.063 |


| contrast   | covariates   | measure     |   n |       t |   p_perm |   p_holm |
|:-----------|:-------------|:------------|----:|--------:|---------:|---------:|
| AD-CN      | age_sex      | rate_type0  |  20 | -2.3169 |   0.0864 |   1      |
| AD-CN      | age_sex      | rate_type1  |  20 | -2.3953 |   0.0432 |   0.7342 |
| AD-CN      | age_sex      | rate_all    |  20 | -2.5858 |   0.0565 |   0.9037 |
| FTD-CN     | age_sex      | fmad_type0  |  18 |  3.0009 |   0.0233 |   0.3953 |
| FTD-CN     | age_sex      | share_type1 |  18 | -2.2594 |   0.0963 |   1      |
| AD-FTD     | age_sex      | fmad_type2  |  18 |  1.9857 |   0.0831 |   1      |

## Stratification

```
{
 "K": 2,
 "silhouette": {
  "2": 0.2300252194255581,
  "3": 0.18914942145290342,
  "4": 0.18654049033624626,
  "5": 0.17022424098854366
 },
 "stability_ari_mean": 0.6696963439133826,
 "stability_ari_sd": 0.27112720348928265,
 "chi2_cluster_vs_diagnosis_p": 0.01106486313067275,
 "mmse_by_cluster_median": {
  "0": 21.0,
  "1": 17.0
 },
 "kruskal_mmse_p": 0.008221165004429591,
 "axes_used": [
  "slowing_theta_alpha",
  "slowing_iaf",
  "aperiodic_slope",
  "aperiodic_offset",
  "gamma_periodic_35_45",
  "gamma_lowemg_35_45",
  "gamma_burst_excess",
  "muscle",
  "transients",
  "pac_theta_gamma",
  "alpha_harmonic",
  "bursts_share_type0",
  "bursts_share_type1",
  "bursts_share_type2",
  "bursts_share_type3",
  "bursts_share_type4"
 ]
}
```

## Prediction (nested CV, 20 repeats)

| model                  |   n_features |   auc |   auc_lo |   auc_hi |   bal_acc |   acc |   p_perm | contrast   |   n |   gain_vs_base |   gain_lo |   gain_hi |   frac_repeats_gain_gt0 |
|:-----------------------|-------------:|------:|---------:|---------:|----------:|------:|---------:|:-----------|----:|---------------:|----------:|----------:|------------------------:|
| slowing                |            2 | 0.537 |    0.444 |    0.635 |     0.55  | 0.55  |    0.667 | AD-CN      |  20 |        nan     |   nan     |   nan     |                 nan     |
| aperiodic              |            2 | 0.52  |    0.463 |    0.577 |     0.517 | 0.517 |    0.333 | AD-CN      |  20 |        nan     |   nan     |   nan     |                 nan     |
| gamma_periodic         |            3 | 1     |    1     |    1     |     0.9   | 0.9   |    0.167 | AD-CN      |  20 |        nan     |   nan     |   nan     |                 nan     |
| bursts                 |            5 | 0.873 |    0.822 |    0.936 |     0.783 | 0.783 |    0.167 | AD-CN      |  20 |        nan     |   nan     |   nan     |                 nan     |
| coupling               |            3 | 0.503 |    0.472 |    0.538 |     0.483 | 0.483 |    0.333 | AD-CN      |  20 |        nan     |   nan     |   nan     |                 nan     |
| transients             |            2 | 0.563 |    0.55  |    0.588 |     0.65  | 0.65  |    0.167 | AD-CN      |  20 |        nan     |   nan     |   nan     |                 nan     |
| muscle                 |            1 | 0.587 |    0.56  |    0.627 |     0.617 | 0.617 |    0.333 | AD-CN      |  20 |        nan     |   nan     |   nan     |                 nan     |
| BASE slowing+aperiodic |            4 | 0.477 |    0.412 |    0.555 |     0.45  | 0.45  |    0.5   | AD-CN      |  20 |        nan     |   nan     |   nan     |                 nan     |
| BASE+gamma_periodic    |            7 | 0.96  |    0.95  |    0.978 |     0.9   | 0.9   |    0.167 | AD-CN      |  20 |          0.483 |     0.395 |     0.566 |                   1     |
| BASE+bursts            |            9 | 0.91  |    0.881 |    0.948 |     0.833 | 0.833 |    0.167 | AD-CN      |  20 |          0.433 |     0.392 |     0.486 |                   1     |
| BASE+coupling          |            7 | 0.443 |    0.384 |    0.48  |     0.433 | 0.433 |    0.5   | AD-CN      |  20 |         -0.033 |    -0.17  |     0.058 |                   0.667 |
| ALL                    |           18 | 1     |    1     |    1     |     0.983 | 0.983 |    0.167 | AD-CN      |  20 |          0.523 |     0.445 |     0.588 |                   1     |