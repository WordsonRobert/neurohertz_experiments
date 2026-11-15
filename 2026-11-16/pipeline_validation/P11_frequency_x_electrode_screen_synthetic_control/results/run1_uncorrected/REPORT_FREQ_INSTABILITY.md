# Frequency x electrode instability screen (EXPLORATORY)

Dataset synthetic; n = 88 ({'AD': 36, 'CN': 29, 'FTD': 23}). Windows 4 Hz wide in 2 Hz steps; grid A 2-46 Hz, grid B 54-90 Hz (above ~45 Hz mostly muscle; ds004504 has a 70 Hz amplifier filter). 19 electrodes (CSD). Metrics: if_sd, slip_frac, period_cv, pf_sd_epochs, burst_f_sd (SNR-matched), each raw and beyond the spectrum (__excess); presence: snr_median.

## A. Reliability (cells with SB-ICC >= 0.6 and coverage >= 80%)

| grid   | feature              |   cells |   reliable |   median_icc_sb |
|:-------|:---------------------|--------:|-----------:|----------------:|
| A      | burst_f_sd           |     399 |          9 |           0.356 |
| A      | burst_f_sd__excess   |     399 |          0 |          -0.035 |
| A      | if_sd                |     399 |         23 |           0.572 |
| A      | if_sd__excess        |     399 |          0 |           0.02  |
| A      | period_cv            |     399 |         40 |           0.466 |
| A      | period_cv__excess    |     399 |          0 |          -0.194 |
| A      | pf_sd_epochs         |     399 |          1 |           0.097 |
| A      | pf_sd_epochs__excess |     399 |          0 |          -0.239 |
| A      | slip_frac            |     399 |          1 |           0     |
| A      | slip_frac__excess    |     399 |          0 |           0     |
| A      | snr_median           |     399 |        267 |           0.873 |
| B      | burst_f_sd           |     323 |          1 |           0.02  |
| B      | burst_f_sd__excess   |     323 |          0 |          -0.11  |
| B      | if_sd                |     323 |          0 |           0.17  |
| B      | if_sd__excess        |     323 |          0 |          -0.13  |
| B      | period_cv            |     323 |          0 |          -0.019 |
| B      | period_cv__excess    |     323 |          0 |          -0.191 |
| B      | pf_sd_epochs         |     323 |          0 |           0.097 |
| B      | pf_sd_epochs__excess |     323 |          0 |          -0.232 |
| B      | slip_frac            |     323 |          2 |           0.218 |
| B      | slip_frac__excess    |     323 |          0 |          -0.266 |
| B      | snr_median           |     323 |         93 |           0.488 |

## B. Family-wise significant clusters (Freedman-Lane, p_FWER < 0.05)

Single-cell clusters (n_cells = 1) rest on one window at one electrode; read them with care.

| grid   | feature              | contrast   | ladder   |   sign |   p_fwer |   f_lo |   f_hi | peak_win   | ch_peak   |   t_peak |   n_cells | channels                                             |
|:-------|:---------------------|:-----------|:---------|-------:|---------:|-------:|-------:|:-----------|:----------|---------:|----------:|:-----------------------------------------------------|
| A      | burst_f_sd           | AD-CN      | L0       |      1 |    0.015 |     38 |     42 | 38-42      | O1        |   4.2497 |         2 | O1 O2                                                |
| A      | burst_f_sd           | AD-CN      | L1       |      1 |    0.043 |     38 |     42 | 38-42      | O1        |   4.003  |         2 | O1 O2                                                |
| A      | burst_f_sd           | AD-CN      | L2       |      1 |    0.025 |     38 |     42 | 38-42      | O1        |   3.916  |         2 | O1 O2                                                |
| A      | burst_f_sd           | AD-FTD     | L0       |     -1 |    0.02  |     34 |     38 | 34-38      | Fp1       |  -3.0246 |         3 | F7 Fp1 Fp2                                           |
| A      | burst_f_sd           | AD-FTD     | L2       |     -1 |    0.001 |     32 |     38 | 32-36      | F3        |  -4.1389 |         9 | F3 F4 F7 F8 Fp1 Fp2 Fz                               |
| A      | burst_f_sd__excess   | FTD-CN     | L2       |     -1 |    0.013 |      8 |     12 | 8-12       | Pz        |  -3.3177 |         2 | P4 Pz                                                |
| A      | if_sd                | AD-CN      | L0       |      1 |    0.032 |     38 |     42 | 38-42      | O1        |   4.4544 |         2 | O1 O2                                                |
| A      | if_sd                | AD-CN      | L1       |      1 |    0.028 |     38 |     42 | 38-42      | O1        |   3.8809 |         2 | O1 O2                                                |
| A      | if_sd                | AD-CN      | L2       |      1 |    0.036 |     38 |     42 | 38-42      | O1        |   3.957  |         2 | O1 O2                                                |
| A      | if_sd                | AD-FTD     | L0       |     -1 |    0.048 |     34 |     38 | 34-38      | F3        |  -3.2325 |         2 | F3 Fp1                                               |
| A      | if_sd                | AD-FTD     | L2       |     -1 |    0.001 |     32 |     38 | 34-38      | F4        |  -4.2893 |        10 | F3 F4 F7 F8 Fp1 Fp2 Fz                               |
| A      | if_sd__excess        | AD-CN      | L0       |      1 |    0.001 |     32 |     42 | 32-36      | Pz        |   4.3457 |         5 | O1 Pz                                                |
| A      | if_sd__excess        | AD-CN      | L1       |      1 |    0.004 |     36 |     42 | 38-42      | O1        |   2.908  |         3 | O1 Pz                                                |
| A      | if_sd__excess        | AD-CN      | L2       |      1 |    0.019 |     36 |     42 | 38-42      | O1        |   3.2267 |         2 | O1                                                   |
| A      | if_sd__excess        | AD-CN      | L2       |      1 |    0.05  |     32 |     36 | 32-36      | Pz        |   3.9715 |         1 | Pz                                                   |
| A      | if_sd__excess        | AD-FTD     | L0       |     -1 |    0.025 |     32 |     38 | 34-38      | F8        |  -3.1119 |         2 | F8                                                   |
| A      | if_sd__excess        | FTD-CN     | L0       |      1 |    0.012 |     34 |     40 | 34-38      | Fp1       |   3.7835 |         2 | Fp1                                                  |
| A      | if_sd__excess        | FTD-CN     | L1       |      1 |    0.009 |     34 |     40 | 34-38      | Fp1       |   3.7905 |         2 | Fp1                                                  |
| A      | period_cv            | AD-CN      | L0       |      1 |    0.041 |     34 |     38 | 34-38      | O2        |   3.3298 |         3 | O1 O2 Pz                                             |
| A      | period_cv            | AD-FTD     | L0       |     -1 |    0.005 |     34 |     38 | 34-38      | F8        |  -4.6315 |         5 | F3 F8 Fp1 Fp2 Fz                                     |
| A      | period_cv            | AD-FTD     | L1       |     -1 |    0.016 |     34 |     38 | 34-38      | Fz        |  -4.1881 |         4 | F3 F8 Fp2 Fz                                         |
| A      | period_cv            | AD-FTD     | L2       |      1 |    0.009 |     36 |     40 | 36-40      | Fp2       |   4.1728 |         5 | F3 F4 F7 Fp2 Fz                                      |
| A      | period_cv            | AD-FTD     | L2       |     -1 |    0.01  |     34 |     38 | 34-38      | Fz        |  -4.7962 |         4 | F3 F8 Fp2 Fz                                         |
| A      | period_cv            | FTD-CN     | L0       |      1 |    0.006 |     34 |     38 | 34-38      | Fp1       |   4.8579 |         5 | F8 Fp1 Fp2 Fz T4                                     |
| A      | period_cv            | FTD-CN     | L0       |     -1 |    0.006 |     32 |     36 | 32-36      | P4        |  -4.8203 |         6 | C4 Cz F4 O1 O2 P4                                    |
| A      | period_cv            | FTD-CN     | L1       |      1 |    0.007 |     34 |     38 | 34-38      | Fp1       |   4.8541 |         5 | F8 Fp1 Fp2 Fz T4                                     |
| A      | period_cv            | FTD-CN     | L1       |     -1 |    0.007 |     32 |     36 | 32-36      | P4        |  -5.0312 |         6 | C4 Cz F4 O1 O2 P4                                    |
| A      | period_cv            | FTD-CN     | L2       |      1 |    0.024 |     34 |     38 | 34-38      | F8        |   4.0069 |         4 | F8 Fp1 Fp2 Fz                                        |
| A      | period_cv__excess    | AD-CN      | L0       |      1 |    0.045 |     34 |     38 | 34-38      | O2        |   4.3407 |         1 | O2                                                   |
| A      | period_cv__excess    | AD-CN      | L2       |      1 |    0.025 |     30 |     34 | 30-34      | O2        |   3.0505 |         2 | O1 O2                                                |
| A      | period_cv__excess    | AD-FTD     | L0       |      1 |    0.001 |     34 |     38 | 34-38      | P3        |   3.3998 |         3 | O1 O2 P3                                             |
| A      | period_cv__excess    | AD-FTD     | L0       |     -1 |    0.001 |     34 |     38 | 34-38      | Fz        |  -5.5397 |         4 | F3 F8 Fp2 Fz                                         |
| A      | period_cv__excess    | AD-FTD     | L1       |     -1 |    0.001 |     34 |     38 | 34-38      | Fz        |  -5.82   |         4 | F3 F8 Fp2 Fz                                         |
| A      | period_cv__excess    | AD-FTD     | L2       |     -1 |    0.001 |     34 |     38 | 34-38      | Fz        |  -6.407  |         3 | F3 Fp2 Fz                                            |
| A      | period_cv__excess    | AD-FTD     | L2       |      1 |    0.029 |     34 |     38 | 34-38      | P3        |   3.2508 |         2 | O1 P3                                                |
| A      | period_cv__excess    | FTD-CN     | L0       |      1 |    0.016 |     34 |     38 | 34-38      | Fz        |   3.479  |         2 | Fp1 Fz                                               |
| A      | period_cv__excess    | FTD-CN     | L1       |      1 |    0.012 |     34 |     38 | 34-38      | Fz        |   3.535  |         2 | Fp1 Fz                                               |
| A      | period_cv__excess    | FTD-CN     | L2       |      1 |    0.004 |     34 |     38 | 34-38      | Fz        |   4.1395 |         3 | F3 Fp1 Fz                                            |
| A      | pf_sd_epochs__excess | FTD-CN     | L2       |     -1 |    0.011 |      8 |     12 | 8-12       | C3        |  -3.0246 |         2 | C3 Cz                                                |
| A      | slip_frac            | AD-FTD     | L0       |     -1 |    0.007 |     34 |     38 | 34-38      | Fz        |  -3.0506 |         1 | Fz                                                   |
| A      | slip_frac            | AD-FTD     | L1       |     -1 |    0.019 |     34 |     38 | 34-38      | Fz        |  -2.8342 |         1 | Fz                                                   |
| A      | slip_frac            | AD-FTD     | L2       |     -1 |    0.028 |     34 |     38 | 34-38      | Fz        |  -2.7645 |         1 | Fz                                                   |
| A      | slip_frac            | AD-FTD     | L2       |     -1 |    0.038 |     32 |     36 | 32-36      | F3        |  -2.7143 |         1 | F3                                                   |
| A      | slip_frac            | FTD-CN     | L2       |      1 |    0.017 |     34 |     38 | 34-38      | Fz        |   2.8065 |         1 | Fz                                                   |
| A      | slip_frac__excess    | AD-FTD     | L0       |     -1 |    0.008 |     32 |     36 | 32-36      | F4        |  -3.0145 |         1 | F4                                                   |
| A      | slip_frac__excess    | AD-FTD     | L0       |     -1 |    0.013 |     34 |     38 | 34-38      | Fz        |  -2.8539 |         1 | Fz                                                   |
| A      | slip_frac__excess    | AD-FTD     | L1       |     -1 |    0.013 |     32 |     36 | 32-36      | F4        |  -2.9239 |         1 | F4                                                   |
| A      | slip_frac__excess    | AD-FTD     | L2       |     -1 |    0.019 |     32 |     36 | 32-36      | F4        |  -2.9737 |         1 | F4                                                   |
| A      | slip_frac__excess    | FTD-CN     | L0       |      1 |    0.014 |     32 |     36 | 32-36      | F4        |   3.0496 |         1 | F4                                                   |
| A      | slip_frac__excess    | FTD-CN     | L1       |      1 |    0.021 |     32 |     36 | 32-36      | F4        |   3.0666 |         1 | F4                                                   |
| A      | slip_frac__excess    | FTD-CN     | L2       |      1 |    0.01  |     32 |     36 | 32-36      | F4        |   3.3248 |         1 | F4                                                   |
| A      | snr_median           | AD-FTD     | L2       |      1 |    0.049 |     40 |     46 | 42-46      | Fz        |   4.2486 |        13 | F3 F4 F7 F8 Fp1 Fp2 Fz                               |
| A      | snr_median           | FTD-CN     | L0       |     -1 |    0.005 |     22 |     36 | 24-28      | O2        |  -3.7213 |        51 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T3 T4 |
| A      | snr_median           | FTD-CN     | L0       |      1 |    0.035 |     36 |     46 | 38-42      | O2        |   4.0232 |        13 | O1 O2 P4 Pz                                          |
| A      | snr_median           | FTD-CN     | L1       |     -1 |    0.004 |     22 |     36 | 24-28      | O2        |  -3.7163 |        50 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T3 T4 |
| A      | snr_median           | FTD-CN     | L1       |      1 |    0.027 |     36 |     46 | 38-42      | O2        |   3.9777 |        14 | O1 O2 P4 Pz                                          |
| B      | slip_frac            | FTD-CN     | L0       |     -1 |    0.016 |     84 |     88 | 84-88      | T3        |  -4.0353 |         2 | T3 T5                                                |
| B      | slip_frac            | FTD-CN     | L1       |     -1 |    0.016 |     84 |     88 | 84-88      | T3        |  -4.0391 |         2 | T3 T5                                                |
| B      | slip_frac            | FTD-CN     | L2       |     -1 |    0.033 |     84 |     88 | 84-88      | T3        |  -3.6099 |         2 | T3 T5                                                |
| B      | snr_median           | FTD-CN     | L0       |     -1 |    0.021 |     76 |     88 | 80-84      | O2        |  -3.6285 |         7 | O1 O2                                                |
| B      | snr_median           | FTD-CN     | L1       |     -1 |    0.022 |     76 |     88 | 80-84      | O2        |  -3.6527 |         7 | O1 O2                                                |

## C. Reference cells: reliable, and equivalent to no group difference in all three contrasts (90% CI of d within +/- 0.5)

| grid   | feature    |   cells |
|:-------|:-----------|--------:|
| A      | period_cv  |       1 |
| A      | snr_median |       2 |
| B      | snr_median |       1 |

Top 30 by tightest bound:

| grid   | feature    |   win_lo | ch   |   icc_sb |   coverage |   n_contrasts |   max_abs_t |   max_ci90_bound | equivalent   | no_detectable_difference   |   win_hi |
|:-------|:-----------|---------:|:-----|---------:|-----------:|--------------:|------------:|-----------------:|:-------------|:---------------------------|---------:|
| A      | period_cv  |       30 | O2   |    0.728 |      0.955 |             3 |       0.272 |            0.478 | True         | True                       |       34 |
| A      | snr_median |       36 | F7   |    0.934 |      1     |             3 |       0.118 |            0.483 | True         | True                       |       40 |
| A      | snr_median |       18 | P4   |    0.775 |      1     |             3 |       0.215 |            0.486 | True         | True                       |       22 |
| B      | snr_median |       56 | Fp2  |    0.646 |      1     |             3 |       0.125 |            0.494 | True         | True                       |       60 |

Looser tier (reliable, |t| < 1 in all three contrasts), counts:

| grid   | feature      |   cells |
|:-------|:-------------|--------:|
| A      | burst_f_sd   |       3 |
| A      | if_sd        |       4 |
| A      | period_cv    |       7 |
| A      | pf_sd_epochs |       1 |
| A      | snr_median   |      26 |
| B      | snr_median   |      25 |

## D. Prediction with in-fold selection of one reliable cell (baseline: slowing + 1/f)

| contrast   | pool                    |   n_cells |   n |   auc_baseline |   auc_cell_alone |   p_alone |   auc_baseline_plus |   p_plus |    gain |   gain_lo |   gain_hi | top_picks_alone                                                                                                                           |
|:-----------|:------------------------|----------:|----:|---------------:|-----------------:|----------:|--------------------:|---------:|--------:|----------:|----------:|:------------------------------------------------------------------------------------------------------------------------------------------|
| AD-CN      | grid A, beyond spectrum |         0 | nan |        nan     |          nan     |   nan     |             nan     |  nan     | nan     |   nan     |   nan     | nan                                                                                                                                       |
| AD-CN      | grid A, raw             |        74 |  65 |          0.598 |            0.593 |     0.216 |               0.599 |    0.137 |   0.001 |    -0.089 |     0.049 | A|period_cv|34-38|O1 (36%); A|period_cv|34-38|O2 (28%); A|burst_f_sd|32-36|F3 (24%); A|period_cv|32-36|P4 (4%); A|burst_f_sd|8-12|Pz (2%) |
| AD-CN      | grid B, all instability |         3 |  65 |          0.598 |            0.478 |     0.627 |               0.548 |    0.294 |  -0.051 |    -0.074 |    -0.022 | B|slip_frac|84-88|Fz (48%); B|burst_f_sd|84-88|P3 (48%); B|slip_frac|80-84|Fz (4%)                                                        |
| FTD-CN     | grid A, beyond spectrum |         0 | nan |        nan     |          nan     |   nan     |             nan     |  nan     | nan     |   nan     |   nan     | nan                                                                                                                                       |
| FTD-CN     | grid A, raw             |        74 |  52 |          0.664 |            0.788 |     0.02  |               0.767 |    0.02  |   0.104 |     0.07  |     0.14  | A|period_cv|34-38|Fp1 (86%); A|period_cv|32-36|P4 (14%)                                                                                   |
| FTD-CN     | grid B, all instability |         3 |  52 |          0.664 |            0.549 |     0.353 |               0.615 |    0.235 |  -0.049 |    -0.124 |    -0.009 | B|slip_frac|84-88|Fz (88%); B|slip_frac|80-84|Fz (6%); B|burst_f_sd|84-88|P3 (6%)                                                         |
| AD-FTD     | grid A, beyond spectrum |         0 | nan |        nan     |          nan     |   nan     |             nan     |  nan     | nan     |   nan     |   nan     | nan                                                                                                                                       |
| AD-FTD     | grid A, raw             |        74 |  59 |          0.693 |            0.706 |     0.039 |               0.766 |    0.02  |   0.073 |    -0.02  |     0.148 | A|period_cv|34-38|Fz (64%); A|period_cv|34-38|F3 (30%); A|period_cv|30-34|Fz (4%); A|if_sd|32-36|Pz (2%)                                  |
| AD-FTD     | grid B, all instability |         3 |  59 |          0.693 |            0.525 |     0.314 |               0.669 |    0.039 |  -0.024 |    -0.067 |    -0.002 | B|burst_f_sd|84-88|P3 (88%); B|slip_frac|80-84|Fz (6%); B|slip_frac|84-88|Fz (6%)                                                         |