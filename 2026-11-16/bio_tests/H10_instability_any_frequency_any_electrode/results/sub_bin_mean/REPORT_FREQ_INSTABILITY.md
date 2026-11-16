# Frequency x electrode instability screen (EXPLORATORY)

Dataset ds004504; n = 88 ({'AD': 36, 'CN': 29, 'FTD': 23}). Windows 4 Hz wide in 2 Hz steps; grid A 2-46 Hz, grid B 54-90 Hz (above ~45 Hz mostly muscle; ds004504 has a 70 Hz amplifier filter). 19 electrodes (CSD). Metrics: if_sd, slip_frac, period_cv, pf_sd_epochs, burst_f_sd (SNR-matched), each raw and beyond the spectrum (__excess); presence: snr_median.

## A. Reliability (cells with SB-ICC >= 0.6 and coverage >= 80%)

| grid   | feature              |   cells |   reliable |   median_icc_sb |
|:-------|:---------------------|--------:|-----------:|----------------:|
| A      | burst_f_sd           |     399 |          0 |           0.633 |
| A      | burst_f_sd__excess   |     399 |          0 |           0.287 |
| A      | if_sd                |     399 |          0 |           0.77  |
| A      | if_sd__excess        |     399 |          0 |           0.56  |
| A      | period_cv            |     399 |          0 |           0.45  |
| A      | period_cv__excess    |     399 |          0 |           0.225 |
| A      | pf_sd_epochs         |     399 |          0 |           0.795 |
| A      | pf_sd_epochs__excess |     399 |          0 |           0.091 |
| A      | slip_frac            |     399 |          0 |           0     |
| A      | slip_frac__excess    |     399 |          0 |           0.005 |
| A      | snr_median           |     399 |        330 |           0.887 |
| B      | burst_f_sd           |     323 |          5 |           0.061 |
| B      | burst_f_sd__excess   |     323 |          1 |          -0.045 |
| B      | if_sd                |     323 |          0 |           0.155 |
| B      | if_sd__excess        |     323 |          0 |           0.07  |
| B      | period_cv            |     323 |          1 |           0.004 |
| B      | period_cv__excess    |     323 |          0 |          -0.128 |
| B      | pf_sd_epochs         |     323 |          1 |           0.167 |
| B      | pf_sd_epochs__excess |     323 |          0 |          -0.217 |
| B      | slip_frac            |     323 |          2 |          -0.148 |
| B      | slip_frac__excess    |     323 |          5 |          -0.304 |
| B      | snr_median           |     323 |          3 |          -0.317 |

## B. Significant clusters (Freedman-Lane; p_family = 30 x p_FWER < 0.05)

Single-cell clusters (n_cells = 1) rest on one window at one electrode; read them with care.

| grid   | feature    | contrast   | ladder   |   sign |   p_fwer |   f_lo |   f_hi | peak_win   | ch_peak   |   t_peak |   n_cells | channels                                                   | family   |   n_maps |   p_family |
|:-------|:-----------|:-----------|:---------|-------:|---------:|-------:|-------:|:-----------|:----------|---------:|----------:|:-----------------------------------------------------------|:---------|---------:|-----------:|
| A      | snr_median | AD-CN      | L0       |      1 |   0.0114 |      4 |      8 | 4-8        | T5        |   6.0594 |        19 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T3 T4 T5 T6 | presence |        3 |     0.0342 |

Clusters with p_FWER < 0.05 within their own map that do not survive the correction over maps:

| grid   | feature           | contrast   | ladder   |   sign |   p_fwer |   f_lo |   f_hi | peak_win   | ch_peak   |   t_peak |   n_cells | channels                               | family      |   n_maps |   p_family |
|:-------|:------------------|:-----------|:---------|-------:|---------:|-------:|-------:|:-----------|:----------|---------:|----------:|:---------------------------------------|:------------|---------:|-----------:|
| A      | snr_median        | AD-CN      | L0       |      1 |   0.03   |     30 |     44 | 34-38      | P3        |   4.0152 |        16 | P3 P4 Pz T6                            | presence    |        3 |     0.09   |
| A      | snr_median        | AD-CN      | L0       |     -1 |   0.0396 |      8 |     14 | 8-12       | T3        |  -4.5689 |        15 | Cz F3 F7 F8 O1 O2 P3 P4 Pz T3 T4 T5 T6 | presence    |        3 |     0.1188 |
| B      | burst_f_sd        | AD-FTD     | L0       |     -1 |   0.049  |     78 |     84 | 78-82      | P3        |  -3.1924 |         2 | P3                                     | instability |       30 |     1      |
| B      | if_sd__excess     | FTD-CN     | L0       |      1 |   0.031  |     78 |     86 | 78-82      | T4        |   3.74   |         5 | C4 T4 T6                               | instability |       30 |     0.9298 |
| B      | period_cv__excess | FTD-CN     | L0       |      1 |   0.0294 |     80 |     86 | 82-86      | T4        |   3.6813 |         2 | T4                                     | instability |       30 |     0.8818 |
| B      | period_cv__excess | FTD-CN     | L2       |      1 |   0.0476 |     80 |     86 | 82-86      | T4        |   3.6774 |         2 | T4                                     | instability |       30 |     1      |
| B      | slip_frac__excess | FTD-CN     | L0       |      1 |   0.0372 |     86 |     90 | 86-90      | T6        |   3.3624 |         3 | O2 T4 T6                               | instability |       30 |     1      |
| B      | slip_frac__excess | FTD-CN     | L0       |      1 |   0.0428 |     80 |     86 | 82-86      | T6        |   3.2185 |         3 | T4 T6                                  | instability |       30 |     1      |
| B      | slip_frac__excess | FTD-CN     | L1       |      1 |   0.019  |     84 |     90 | 86-90      | O2        |   3.6347 |         4 | O2 T4 T6                               | instability |       30 |     0.5699 |
| B      | slip_frac__excess | FTD-CN     | L2       |      1 |   0.0238 |     84 |     90 | 86-90      | O2        |   3.9857 |         4 | O2 T4 T6                               | instability |       30 |     0.7139 |

## C. Reference cells: reliable, and equivalent to no group difference in all three contrasts (90% CI of d within +/- 0.5)

| grid   | feature    |   cells |
|:-------|:-----------|--------:|
| A      | snr_median |       2 |

Top 30 by tightest bound:

| grid   | feature    |   win_lo | ch   |   icc_sb |   coverage |   n_contrasts |   max_abs_t |   max_ci90_bound | equivalent   | no_detectable_difference   |   win_hi |
|:-------|:-----------|---------:|:-----|---------:|-----------:|--------------:|------------:|-----------------:|:-------------|:---------------------------|---------:|
| A      | snr_median |       14 | P4   |    0.921 |          1 |             3 |       0.155 |            0.48  | True         | True                       |       18 |
| A      | snr_median |       14 | Fp2  |    0.807 |          1 |             3 |       0.291 |            0.488 | True         | True                       |       18 |

Looser tier (reliable, |t| < 1 in all three contrasts), counts:

| grid   | feature            |   cells |
|:-------|:-------------------|--------:|
| A      | snr_median         |      53 |
| B      | burst_f_sd         |       1 |
| B      | burst_f_sd__excess |       1 |
| B      | period_cv          |       1 |
| B      | slip_frac          |       1 |
| B      | slip_frac__excess  |       2 |

## D. Prediction with in-fold selection of one reliable cell (baseline: slowing + 1/f)

| contrast   | pool                    |   n_cells |   n |   auc_baseline |   auc_cell_alone |   p_alone |   auc_baseline_plus |   p_plus |    gain |   gain_lo |   gain_hi | top_picks_alone                                                                                                                                                     |
|:-----------|:------------------------|----------:|----:|---------------:|-----------------:|----------:|--------------------:|---------:|--------:|----------:|----------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| AD-CN      | grid A, beyond spectrum |         0 | nan |        nan     |          nan     |   nan     |             nan     |  nan     | nan     |   nan     |   nan     | nan                                                                                                                                                                 |
| AD-CN      | grid A, raw             |         0 | nan |        nan     |          nan     |   nan     |             nan     |  nan     | nan     |   nan     |   nan     | nan                                                                                                                                                                 |
| AD-CN      | grid B, all instability |        15 |  65 |          0.818 |            0.537 |     0.328 |               0.806 |    0.005 |  -0.012 |    -0.039 |     0.016 | B|burst_f_sd|86-90|Cz (72%); B|slip_frac__excess|78-82|F4 (8%); B|slip_frac__excess|76-80|Pz (6%); B|pf_sd_epochs|70-74|C3 (5%); B|burst_f_sd__excess|82-86|F8 (4%) |
| FTD-CN     | grid A, beyond spectrum |         0 | nan |        nan     |          nan     |   nan     |             nan     |  nan     | nan     |   nan     |   nan     | nan                                                                                                                                                                 |
| FTD-CN     | grid A, raw             |         0 | nan |        nan     |          nan     |   nan     |             nan     |  nan     | nan     |   nan     |   nan     | nan                                                                                                                                                                 |
| FTD-CN     | grid B, all instability |        15 |  52 |          0.728 |            0.521 |     0.358 |               0.682 |    0.04  |  -0.046 |    -0.122 |     0.015 | B|burst_f_sd|86-90|C4 (66%); B|burst_f_sd|70-74|T3 (12%); B|pf_sd_epochs|70-74|C3 (9%); B|slip_frac__excess|76-80|Pz (7%); B|burst_f_sd|86-90|Cz (3%)               |
| AD-FTD     | grid A, beyond spectrum |         0 | nan |        nan     |          nan     |   nan     |             nan     |  nan     | nan     |   nan     |   nan     | nan                                                                                                                                                                 |
| AD-FTD     | grid A, raw             |         0 | nan |        nan     |          nan     |   nan     |             nan     |  nan     | nan     |   nan     |   nan     | nan                                                                                                                                                                 |
| AD-FTD     | grid B, all instability |        15 |  59 |          0.548 |            0.425 |     0.706 |               0.485 |    0.473 |  -0.063 |    -0.129 |    -0.002 | B|burst_f_sd|86-90|C4 (43%); B|burst_f_sd__excess|82-86|F8 (31%); B|slip_frac__excess|78-82|F4 (14%); B|burst_f_sd|86-90|Cz (3%); B|burst_f_sd|70-74|T4 (3%)        |