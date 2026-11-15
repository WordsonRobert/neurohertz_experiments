# Frequency instability across bands: characterization (EXPLORATORY)

Eligible measures (split-half SB-ICC >= 0.6, coverage >= 80%): 61 of 408 ({'excess': 12, 'presence': 16, 'raw': 33}).

## A. Most reliable measures

| feature                           | family   |   coverage |   icc_half |   icc_sb | eligible   |
|:----------------------------------|:---------|-----------:|-----------:|---------:|:-----------|
| beta_high|frac_snr3|global        | presence |      1     |      0.977 |    0.988 | True       |
| beta_high|snr_median|global       | presence |      1     |      0.971 |    0.985 | True       |
| gamma|snr_median|global           | presence |      1     |      0.963 |    0.981 | True       |
| gamma|frac_snr3|global            | presence |      1     |      0.961 |    0.98  | True       |
| beta_high|frac_snr3|roi           | presence |      1     |      0.958 |    0.979 | True       |
| beta_high|snr_median|roi          | presence |      1     |      0.95  |    0.974 | True       |
| gamma|snr_median|roi              | presence |      1     |      0.934 |    0.966 | True       |
| gamma|frac_snr3|roi               | presence |      1     |      0.929 |    0.963 | True       |
| alpha|snr_median|roi              | presence |      1     |      0.928 |    0.963 | True       |
| alpha|snr_median|global           | presence |      1     |      0.915 |    0.956 | True       |
| alpha|frac_snr3|roi               | presence |      1     |      0.909 |    0.952 | True       |
| gamma|slip_frac|global            | raw      |      0.989 |      0.907 |    0.951 | True       |
| alpha|frac_snr3|global            | presence |      1     |      0.898 |    0.946 | True       |
| gamma|slip_frac_b1|global         | raw      |      1     |      0.897 |    0.946 | True       |
| gamma|slip_frac_b2__excess|global | excess   |      0.989 |      0.892 |    0.943 | True       |
| gamma|pf_sd_epochs_b2|global      | raw      |      1     |      0.878 |    0.935 | True       |
| gamma|slip_frac_b2__excess|roi    | excess   |      0.966 |      0.862 |    0.926 | True       |
| gamma|pf_sd_epochs_b2|roi         | raw      |      1     |      0.809 |    0.895 | True       |
| gamma|slip_frac__excess|global    | excess   |      0.989 |      0.807 |    0.893 | True       |
| beta_low|snr_median|roi           | presence |      1     |      0.791 |    0.883 | True       |
| gamma|period_cv_b2|global         | raw      |      1     |      0.79  |    0.883 | True       |
| beta_low|snr_median|global        | presence |      1     |      0.777 |    0.875 | True       |
| gamma|slip_frac|roi               | raw      |      0.977 |      0.766 |    0.868 | True       |
| gamma|burst_f_sd_b1|global        | raw      |      1     |      0.763 |    0.865 | True       |
| gamma|slip_frac_b1__excess|global | excess   |      1     |      0.756 |    0.861 | True       |

## B. How much of each reliable raw measure is spectrum

| feature                          |   r2_raw_on_surrogate |   rho_with_presence |
|:---------------------------------|----------------------:|--------------------:|
| gamma|pf_sd_epochs|global        |                 0.928 |              -0.759 |
| gamma|slip_frac|global           |                 0.911 |               0.652 |
| gamma|pf_sd_epochs_b2|global     |                 0.902 |              -0.724 |
| beta_high|pf_sd_epochs_b1|global |                 0.901 |              -0.727 |
| gamma|slip_frac_b1|global        |                 0.901 |               0.707 |
| gamma|burst_f_sd_b1|global       |                 0.878 |              -0.736 |
| gamma|burst_f_sd|global          |                 0.871 |              -0.668 |
| gamma|pf_sd_epochs_b1|global     |                 0.857 |              -0.79  |
| gamma|pf_sd_epochs_b2|roi        |                 0.848 |              -0.555 |
| gamma|pf_sd_epochs|roi           |                 0.807 |              -0.603 |
| beta_high|pf_sd_epochs_b1|roi    |                 0.779 |              -0.509 |
| gamma|slip_frac_b1|roi           |                 0.773 |               0.556 |
| gamma|burst_f_sd_b1|roi          |                 0.766 |              -0.493 |
| gamma|slip_frac|roi              |                 0.758 |               0.501 |
| gamma|period_cv_b2|global        |                 0.736 |              -0.563 |
| gamma|burst_f_sd|roi             |                 0.715 |              -0.364 |
| gamma|if_sd_b1|global            |                 0.694 |               0.718 |
| gamma|if_sd_b1|roi               |                 0.675 |               0.662 |
| beta_high|period_cv_b1|global    |                 0.664 |               0.756 |
| alpha|if_sd_naive|roi            |                 0.573 |              -0.706 |
| gamma|period_cv_b1|global        |                 0.533 |               0.693 |
| gamma|period_cv_b2|roi           |                 0.517 |              -0.246 |
| gamma|period_cv_b1|roi           |                 0.51  |               0.633 |
| gamma|slip_frac_b2|global        |                 0.474 |               0.299 |
| gamma|period_cv|global           |                 0.454 |              -0.128 |
| gamma|if_sd_naive|roi            |                 0.396 |               0.386 |
| gamma|if_sd|roi                  |                 0.37  |               0.462 |
| gamma|period_cv|roi              |                 0.362 |               0.16  |
| gamma|if_sd|global               |                 0.352 |               0.35  |
| gamma|if_sd_naive|global         |                 0.33  |               0.363 |
| alpha|burst_f_sd_b2|roi          |                 0.291 |              -0.317 |
| gamma|if_sd_b2|roi               |                 0.173 |               0.284 |
| gamma|if_sd_b2|global            |                 0.129 |               0.103 |

## C. Structure
```
{
 "raw": {
  "n": 33,
  "var_explained_pc1_3": [
   0.455,
   0.237,
   0.07
  ],
  "pc1_top_loadings": {
   "gamma|burst_f_sd|global": 0.24,
   "gamma|burst_f_sd_b1|global": 0.24,
   "gamma|pf_sd_epochs_b2|global": 0.24,
   "gamma|pf_sd_epochs|global": 0.24,
   "gamma|burst_f_sd_b1|roi": 0.23,
   "gamma|burst_f_sd|roi": 0.23,
   "gamma|period_cv_b2|global": 0.23,
   "gamma|pf_sd_epochs_b2|roi": 0.23
  }
 },
 "excess": {
  "n": 12,
  "var_explained_pc1_3": [
   0.666,
   0.168,
   0.086
  ],
  "pc1_top_loadings": {
   "gamma|slip_frac_b1__excess|roi": 0.32,
   "gamma|slip_frac__excess|roi": 0.32,
   "gamma|slip_frac__excess|global": 0.31,
   "gamma|slip_frac_b1__excess|global": 0.31,
   "gamma|slip_frac_b2__excess|global": 0.3,
   "gamma|if_sd_b2__excess|global": 0.28,
   "gamma|if_sd__excess|global": 0.28,
   "gamma|if_sd__excess|roi": 0.27
  }
 }
}
```

## D. Family-wise significant group differences (maxT p < 0.05)

| family   | contrast   | ladder   | feature                           |       t |   p_maxT |
|:---------|:-----------|:---------|:----------------------------------|--------:|---------:|
| raw      | AD-CN      | L0       | gamma|if_sd|roi                   |  5.6287 |    0.001 |
| raw      | AD-CN      | L0       | gamma|if_sd_b1|roi                |  3.6288 |    0.014 |
| raw      | AD-CN      | L0       | gamma|if_sd_b2|roi                |  6.9369 |    0.001 |
| raw      | AD-CN      | L0       | gamma|if_sd_naive|roi             |  4.9849 |    0.001 |
| raw      | AD-CN      | L0       | gamma|period_cv|roi               |  6.905  |    0.001 |
| raw      | AD-CN      | L0       | gamma|period_cv_b1|roi            |  4.3904 |    0.003 |
| raw      | AD-CN      | L0       | gamma|period_cv_b2|roi            |  5.7205 |    0.001 |
| raw      | AD-CN      | L0       | gamma|if_sd|global                |  3.4673 |    0.019 |
| raw      | AD-CN      | L0       | gamma|if_sd_b2|global             |  5.0071 |    0.001 |
| raw      | AD-CN      | L0       | gamma|period_cv|global            |  4.2986 |    0.004 |
| raw      | AD-CN      | L0       | gamma|period_cv_b2|global         |  3.3175 |    0.033 |
| raw      | AD-CN      | L1       | gamma|if_sd|roi                   |  5.2919 |    0.001 |
| raw      | AD-CN      | L1       | gamma|if_sd_b2|roi                |  6.5072 |    0.001 |
| raw      | AD-CN      | L1       | gamma|if_sd_naive|roi             |  4.6994 |    0.001 |
| raw      | AD-CN      | L1       | gamma|period_cv|roi               |  6.2501 |    0.001 |
| raw      | AD-CN      | L1       | gamma|period_cv_b1|roi            |  3.8808 |    0.014 |
| raw      | AD-CN      | L1       | gamma|period_cv_b2|roi            |  5.1833 |    0.001 |
| raw      | AD-CN      | L1       | gamma|if_sd_b2|global             |  4.7581 |    0.001 |
| raw      | AD-CN      | L1       | gamma|period_cv|global            |  3.7741 |    0.019 |
| raw      | AD-CN      | L2       | gamma|if_sd|roi                   |  5.4805 |    0.001 |
| raw      | AD-CN      | L2       | gamma|if_sd_b1|roi                |  3.7899 |    0.017 |
| raw      | AD-CN      | L2       | gamma|if_sd_b2|roi                |  6.43   |    0.001 |
| raw      | AD-CN      | L2       | gamma|if_sd_naive|roi             |  4.8693 |    0.002 |
| raw      | AD-CN      | L2       | gamma|period_cv|roi               |  6.2435 |    0.001 |
| raw      | AD-CN      | L2       | gamma|period_cv_b1|roi            |  4.6654 |    0.003 |
| raw      | AD-CN      | L2       | gamma|period_cv_b2|roi            |  6.0153 |    0.001 |
| raw      | AD-CN      | L2       | gamma|if_sd|global                |  3.3566 |    0.044 |
| raw      | AD-CN      | L2       | gamma|if_sd_b2|global             |  4.6828 |    0.003 |
| raw      | AD-CN      | L2       | gamma|period_cv|global            |  3.8649 |    0.013 |
| raw      | AD-CN      | L2       | gamma|period_cv_b2|global         |  3.3278 |    0.049 |
| raw      | AD-CN      | L3       | gamma|if_sd|roi                   |  7.5781 |    0.001 |
| raw      | AD-CN      | L3       | gamma|if_sd_b1|roi                |  6.3253 |    0.001 |
| raw      | AD-CN      | L3       | gamma|if_sd_b2|roi                |  7.7233 |    0.001 |
| raw      | AD-CN      | L3       | gamma|if_sd_naive|roi             |  5.9497 |    0.001 |
| raw      | AD-CN      | L3       | gamma|period_cv|roi               |  7.6836 |    0.001 |
| raw      | AD-CN      | L3       | gamma|period_cv_b1|roi            |  6.6849 |    0.001 |
| raw      | AD-CN      | L3       | gamma|period_cv_b2|roi            |  6.4465 |    0.001 |
| raw      | AD-CN      | L3       | gamma|if_sd|global                |  5.1619 |    0.001 |
| raw      | AD-CN      | L3       | gamma|if_sd_b1|global             |  3.9173 |    0.01  |
| raw      | AD-CN      | L3       | gamma|if_sd_b2|global             |  5.8317 |    0.001 |
| raw      | AD-CN      | L3       | gamma|if_sd_naive|global          |  4.0236 |    0.006 |
| raw      | AD-CN      | L3       | gamma|period_cv|global            |  4.3321 |    0.002 |
| raw      | AD-CN      | L3       | gamma|period_cv_b1|global         |  5.3361 |    0.001 |
| raw      | FTD-CN     | L0       | gamma|if_sd|global                |  7.9804 |    0.001 |
| raw      | FTD-CN     | L0       | gamma|if_sd_b2|global             |  9.5049 |    0.001 |
| raw      | FTD-CN     | L0       | gamma|if_sd_naive|global          |  4.4824 |    0.004 |
| raw      | FTD-CN     | L0       | gamma|period_cv|global            |  6.1884 |    0.001 |
| raw      | FTD-CN     | L0       | gamma|period_cv_b2|global         |  4.4813 |    0.005 |
| raw      | FTD-CN     | L0       | gamma|pf_sd_epochs|global         |  3.3733 |    0.038 |
| raw      | FTD-CN     | L0       | gamma|pf_sd_epochs_b1|global      |  3.997  |    0.012 |
| raw      | FTD-CN     | L1       | gamma|if_sd|global                |  8.0664 |    0.001 |
| raw      | FTD-CN     | L1       | gamma|if_sd_b2|global             |  9.6977 |    0.001 |
| raw      | FTD-CN     | L1       | gamma|if_sd_naive|global          |  4.6081 |    0.004 |
| raw      | FTD-CN     | L1       | gamma|period_cv|global            |  6.1545 |    0.001 |
| raw      | FTD-CN     | L1       | gamma|period_cv_b2|global         |  4.4105 |    0.005 |
| raw      | FTD-CN     | L1       | gamma|pf_sd_epochs_b1|global      |  3.9662 |    0.014 |
| raw      | FTD-CN     | L2       | gamma|if_sd|global                |  6.7152 |    0.001 |
| raw      | FTD-CN     | L2       | gamma|if_sd_b2|global             |  7.6824 |    0.001 |
| raw      | FTD-CN     | L2       | gamma|if_sd_naive|global          |  4.062  |    0.011 |
| raw      | FTD-CN     | L2       | gamma|period_cv|global            |  5.2563 |    0.002 |
| raw      | FTD-CN     | L2       | gamma|period_cv_b1|global         |  4.0222 |    0.011 |
| raw      | FTD-CN     | L3       | gamma|if_sd|global                |  6.6618 |    0.001 |
| raw      | FTD-CN     | L3       | gamma|if_sd_b1|global             |  4.869  |    0.003 |
| raw      | FTD-CN     | L3       | gamma|if_sd_b2|global             |  7.4515 |    0.001 |
| raw      | FTD-CN     | L3       | gamma|if_sd_naive|global          |  4.6812 |    0.004 |
| raw      | FTD-CN     | L3       | gamma|period_cv|global            |  5.076  |    0.002 |
| raw      | FTD-CN     | L3       | gamma|period_cv_b1|global         |  6.5459 |    0.001 |
| raw      | FTD-CN     | L3       | gamma|pf_sd_epochs_b1|global      |  4.2572 |    0.008 |
| raw      | AD-FTD     | L0       | gamma|if_sd|roi                   |  4.3326 |    0.005 |
| raw      | AD-FTD     | L0       | gamma|if_sd_b2|roi                |  5.3434 |    0.001 |
| raw      | AD-FTD     | L0       | gamma|if_sd_naive|roi             |  4.7591 |    0.003 |
| raw      | AD-FTD     | L0       | gamma|period_cv|roi               |  5.9562 |    0.001 |
| raw      | AD-FTD     | L0       | gamma|period_cv_b1|roi            |  4.2387 |    0.006 |
| raw      | AD-FTD     | L0       | gamma|period_cv_b2|roi            |  4.2123 |    0.006 |
| raw      | AD-FTD     | L0       | gamma|if_sd|global                | -3.9776 |    0.009 |
| raw      | AD-FTD     | L0       | gamma|if_sd_b2|global             | -4.1723 |    0.007 |
| raw      | AD-FTD     | L1       | gamma|if_sd|roi                   |  3.5361 |    0.027 |
| raw      | AD-FTD     | L1       | gamma|if_sd_b2|roi                |  4.3885 |    0.006 |
| raw      | AD-FTD     | L1       | gamma|if_sd_naive|roi             |  4.2309 |    0.007 |
| raw      | AD-FTD     | L1       | gamma|period_cv|roi               |  4.6781 |    0.002 |
| raw      | AD-FTD     | L1       | gamma|period_cv_b1|roi            |  3.7287 |    0.018 |
| raw      | AD-FTD     | L1       | gamma|if_sd|global                | -4.4038 |    0.006 |
| raw      | AD-FTD     | L1       | gamma|if_sd_b2|global             | -4.413  |    0.006 |
| raw      | AD-FTD     | L2       | gamma|if_sd_b2|roi                |  4.1573 |    0.008 |
| raw      | AD-FTD     | L2       | gamma|period_cv|roi               |  4.8677 |    0.003 |
| raw      | AD-FTD     | L2       | gamma|period_cv_b2|roi            |  4.7636 |    0.004 |
| raw      | AD-FTD     | L2       | gamma|if_sd|global                | -4.5214 |    0.004 |
| raw      | AD-FTD     | L2       | gamma|if_sd_b2|global             | -4.0305 |    0.013 |
| raw      | AD-FTD     | L3       | gamma|if_sd|roi                   |  6.6185 |    0.001 |
| raw      | AD-FTD     | L3       | gamma|if_sd_b1|roi                |  5.0184 |    0.001 |
| raw      | AD-FTD     | L3       | gamma|if_sd_b2|roi                |  6.9225 |    0.001 |
| raw      | AD-FTD     | L3       | gamma|if_sd_naive|roi             |  5.15   |    0.001 |
| raw      | AD-FTD     | L3       | gamma|period_cv|roi               |  6.1223 |    0.001 |
| raw      | AD-FTD     | L3       | gamma|period_cv_b1|roi            |  6.9266 |    0.001 |
| raw      | AD-FTD     | L3       | gamma|period_cv_b2|roi            |  4.6819 |    0.001 |
| excess   | AD-CN      | L0       | gamma|if_sd__excess|roi           |  6.9389 |    0.001 |
| excess   | AD-CN      | L0       | gamma|if_sd_b2__excess|roi        |  7.28   |    0.001 |
| excess   | AD-CN      | L0       | gamma|period_cv__excess|roi       |  7.6466 |    0.001 |
| excess   | AD-CN      | L0       | gamma|period_cv_b1__excess|roi    |  6.9188 |    0.001 |
| excess   | AD-CN      | L0       | gamma|slip_frac__excess|roi       |  3.2931 |    0.011 |
| excess   | AD-CN      | L0       | gamma|slip_frac_b1__excess|roi    |  3.5331 |    0.007 |
| excess   | AD-CN      | L0       | gamma|if_sd__excess|global        |  5.7007 |    0.001 |
| excess   | AD-CN      | L0       | gamma|if_sd_b2__excess|global     |  5.8882 |    0.001 |
| excess   | AD-CN      | L1       | gamma|if_sd__excess|roi           |  6.5978 |    0.001 |
| excess   | AD-CN      | L1       | gamma|if_sd_b2__excess|roi        |  6.8184 |    0.001 |
| excess   | AD-CN      | L1       | gamma|period_cv__excess|roi       |  7.4451 |    0.001 |
| excess   | AD-CN      | L1       | gamma|period_cv_b1__excess|roi    |  6.7613 |    0.001 |
| excess   | AD-CN      | L1       | gamma|slip_frac__excess|roi       |  3.0458 |    0.024 |
| excess   | AD-CN      | L1       | gamma|slip_frac_b1__excess|roi    |  3.326  |    0.009 |
| excess   | AD-CN      | L1       | gamma|if_sd__excess|global        |  5.3231 |    0.001 |
| excess   | AD-CN      | L1       | gamma|if_sd_b2__excess|global     |  5.5373 |    0.001 |
| excess   | AD-CN      | L2       | gamma|if_sd__excess|roi           |  6.6295 |    0.001 |
| excess   | AD-CN      | L2       | gamma|if_sd_b2__excess|roi        |  6.7439 |    0.001 |
| excess   | AD-CN      | L2       | gamma|period_cv__excess|roi       |  7.6242 |    0.001 |
| excess   | AD-CN      | L2       | gamma|period_cv_b1__excess|roi    |  6.745  |    0.001 |
| excess   | AD-CN      | L2       | gamma|slip_frac__excess|roi       |  3.0524 |    0.018 |
| excess   | AD-CN      | L2       | gamma|slip_frac_b1__excess|roi    |  3.3746 |    0.011 |
| excess   | AD-CN      | L2       | gamma|if_sd__excess|global        |  5.267  |    0.001 |
| excess   | AD-CN      | L2       | gamma|if_sd_b2__excess|global     |  5.4754 |    0.001 |
| excess   | AD-CN      | L3       | gamma|if_sd__excess|roi           |  7.0474 |    0.001 |
| excess   | AD-CN      | L3       | gamma|if_sd_b2__excess|roi        |  6.9042 |    0.001 |
| excess   | AD-CN      | L3       | gamma|period_cv__excess|roi       |  8.1127 |    0.001 |
| excess   | AD-CN      | L3       | gamma|period_cv_b1__excess|roi    |  6.8793 |    0.001 |
| excess   | AD-CN      | L3       | gamma|slip_frac__excess|roi       |  2.9705 |    0.036 |
| excess   | AD-CN      | L3       | gamma|slip_frac_b1__excess|roi    |  3.3312 |    0.018 |
| excess   | AD-CN      | L3       | gamma|if_sd__excess|global        |  5.7343 |    0.001 |
| excess   | AD-CN      | L3       | gamma|if_sd_b2__excess|global     |  5.7241 |    0.001 |
| excess   | FTD-CN     | L0       | gamma|if_sd__excess|global        |  9.3944 |    0.001 |
| excess   | FTD-CN     | L0       | gamma|if_sd_b2__excess|global     |  8.8934 |    0.001 |
| excess   | FTD-CN     | L0       | gamma|slip_frac__excess|global    |  3.94   |    0.002 |
| excess   | FTD-CN     | L0       | gamma|slip_frac_b1__excess|global |  4.1319 |    0.001 |
| excess   | FTD-CN     | L1       | gamma|if_sd__excess|global        |  9.7106 |    0.001 |
| excess   | FTD-CN     | L1       | gamma|if_sd_b2__excess|global     |  9.11   |    0.001 |
| excess   | FTD-CN     | L1       | gamma|slip_frac__excess|global    |  3.9304 |    0.003 |
| excess   | FTD-CN     | L1       | gamma|slip_frac_b1__excess|global |  4.133  |    0.003 |
| excess   | FTD-CN     | L2       | gamma|if_sd__excess|global        |  7.7918 |    0.001 |
| excess   | FTD-CN     | L2       | gamma|if_sd_b2__excess|global     |  7.1641 |    0.001 |
| excess   | FTD-CN     | L2       | gamma|slip_frac__excess|global    |  3.4487 |    0.014 |
| excess   | FTD-CN     | L2       | gamma|slip_frac_b1__excess|global |  3.7233 |    0.005 |
| excess   | FTD-CN     | L3       | gamma|if_sd__excess|global        |  7.9163 |    0.001 |
| excess   | FTD-CN     | L3       | gamma|if_sd_b2__excess|global     |  7.7798 |    0.001 |
| excess   | FTD-CN     | L3       | gamma|slip_frac__excess|global    |  3.424  |    0.017 |
| excess   | FTD-CN     | L3       | gamma|slip_frac_b1__excess|global |  3.7011 |    0.009 |
| excess   | AD-FTD     | L0       | gamma|if_sd__excess|roi           |  6.7981 |    0.001 |
| excess   | AD-FTD     | L0       | gamma|if_sd_b2__excess|roi        |  6.1505 |    0.001 |
| excess   | AD-FTD     | L0       | gamma|period_cv__excess|roi       |  8.4131 |    0.001 |
| excess   | AD-FTD     | L0       | gamma|period_cv_b1__excess|roi    |  8.1028 |    0.001 |
| excess   | AD-FTD     | L0       | gamma|if_sd__excess|global        | -4.9893 |    0.001 |
| excess   | AD-FTD     | L0       | gamma|if_sd_b2__excess|global     | -3.98   |    0.003 |
| excess   | AD-FTD     | L0       | gamma|slip_frac__excess|global    | -3.2863 |    0.02  |
| excess   | AD-FTD     | L0       | gamma|slip_frac_b1__excess|global | -3.2864 |    0.02  |
| excess   | AD-FTD     | L1       | gamma|if_sd__excess|roi           |  5.9777 |    0.001 |
| excess   | AD-FTD     | L1       | gamma|if_sd_b2__excess|roi        |  5.2636 |    0.001 |
| excess   | AD-FTD     | L1       | gamma|period_cv__excess|roi       |  7.569  |    0.001 |
| excess   | AD-FTD     | L1       | gamma|period_cv_b1__excess|roi    |  7.1867 |    0.001 |
| excess   | AD-FTD     | L1       | gamma|if_sd__excess|global        | -4.758  |    0.001 |
| excess   | AD-FTD     | L1       | gamma|if_sd_b2__excess|global     | -3.861  |    0.005 |
| excess   | AD-FTD     | L1       | gamma|slip_frac__excess|global    | -3.2189 |    0.029 |
| excess   | AD-FTD     | L1       | gamma|slip_frac_b1__excess|global | -3.2154 |    0.029 |
| excess   | AD-FTD     | L2       | gamma|if_sd__excess|roi           |  6.2781 |    0.001 |
| excess   | AD-FTD     | L2       | gamma|if_sd_b2__excess|roi        |  6.1787 |    0.001 |
| excess   | AD-FTD     | L2       | gamma|period_cv__excess|roi       |  7.8243 |    0.001 |
| excess   | AD-FTD     | L2       | gamma|period_cv_b1__excess|roi    |  7.1214 |    0.001 |
| excess   | AD-FTD     | L2       | gamma|if_sd__excess|global        | -4.2698 |    0.002 |
| excess   | AD-FTD     | L2       | gamma|if_sd_b2__excess|global     | -3.1288 |    0.029 |
| excess   | AD-FTD     | L3       | gamma|if_sd__excess|roi           |  6.5386 |    0.001 |
| excess   | AD-FTD     | L3       | gamma|if_sd_b2__excess|roi        |  6.3406 |    0.001 |
| excess   | AD-FTD     | L3       | gamma|period_cv__excess|roi       |  8.2718 |    0.001 |
| excess   | AD-FTD     | L3       | gamma|period_cv_b1__excess|roi    |  7.3338 |    0.001 |
| excess   | AD-FTD     | L3       | gamma|if_sd__excess|global        | -4.5645 |    0.002 |
| excess   | AD-FTD     | L3       | gamma|if_sd_b2__excess|global     | -4.1438 |    0.004 |
| presence | FTD-CN     | L0       | beta_high|frac_snr3|roi           | -2.9198 |    0.045 |
| presence | FTD-CN     | L0       | beta_high|snr_median|roi          | -3.1898 |    0.026 |
| presence | FTD-CN     | L0       | beta_low|frac_snr3|roi            |  3.765  |    0.006 |
| presence | FTD-CN     | L0       | beta_low|snr_median|roi           |  3.1356 |    0.029 |
| presence | FTD-CN     | L1       | beta_high|snr_median|roi          | -3.1634 |    0.034 |
| presence | FTD-CN     | L1       | beta_low|frac_snr3|roi            |  4.0375 |    0.004 |
| presence | FTD-CN     | L1       | beta_low|snr_median|roi           |  3.1846 |    0.029 |
| presence | AD-FTD     | L2       | gamma|snr_median|roi              | -3.2632 |    0.017 |

## E. Time-on-task drift, AD vs CN (maxT p < 0.1)

| feature   | t   | p_maxT   |
|-----------|-----|----------|

## F. Severity within AD (q < 0.1)

| feature   | n   | rho_partial   | p_perm   | q_bh   |
|-----------|-----|---------------|----------|--------|

## G. Prediction with in-fold selection

| contrast   | pool         |   n |   auc_baseline |   auc_instability_alone |   p_alone |   auc_baseline_plus |   p_plus |   bal_acc_plus |   gain |   gain_lo |   gain_hi | top_picks                                                                                                                               |
|:-----------|:-------------|----:|---------------:|------------------------:|----------:|--------------------:|---------:|---------------:|-------:|----------:|----------:|:----------------------------------------------------------------------------------------------------------------------------------------|
| AD-CN      | all eligible |  65 |          0.598 |                   0.901 |      0.02 |               0.878 |    0.02  |          0.805 |  0.28  |     0.234 |     0.326 | gamma|period_cv__excess|roi (88%); gamma|if_sd_b2__excess|roi (10%); gamma|period_cv_b1__excess|roi (2%)                                |
| AD-CN      | excess only  |  65 |          0.598 |                   0.901 |      0.02 |               0.878 |    0.02  |          0.805 |  0.28  |     0.234 |     0.326 | gamma|period_cv__excess|roi (88%); gamma|if_sd_b2__excess|roi (10%); gamma|period_cv_b1__excess|roi (2%)                                |
| AD-CN      | raw only     |  65 |          0.598 |                   0.835 |      0.02 |               0.802 |    0.02  |          0.728 |  0.204 |     0.17  |     0.234 | gamma|period_cv|roi (62%); gamma|if_sd_b2|roi (36%); gamma|period_cv_b2|roi (2%)                                                        |
| FTD-CN     | all eligible |  52 |          0.664 |                   0.95  |      0.02 |               0.925 |    0.02  |          0.873 |  0.262 |     0.228 |     0.31  | gamma|if_sd__excess|global (100%)                                                                                                       |
| FTD-CN     | excess only  |  52 |          0.664 |                   0.95  |      0.02 |               0.925 |    0.02  |          0.873 |  0.262 |     0.228 |     0.31  | gamma|if_sd__excess|global (100%)                                                                                                       |
| FTD-CN     | raw only     |  52 |          0.664 |                   0.925 |      0.02 |               0.896 |    0.02  |          0.813 |  0.232 |     0.203 |     0.272 | gamma|if_sd_b2|global (100%)                                                                                                            |
| AD-FTD     | all eligible |  59 |          0.693 |                   0.931 |      0.02 |               0.941 |    0.02  |          0.854 |  0.249 |     0.211 |     0.273 | gamma|period_cv__excess|roi (96%); gamma|period_cv_b1__excess|roi (4%)                                                                  |
| AD-FTD     | excess only  |  59 |          0.693 |                   0.931 |      0.02 |               0.941 |    0.02  |          0.854 |  0.249 |     0.211 |     0.273 | gamma|period_cv__excess|roi (96%); gamma|period_cv_b1__excess|roi (4%)                                                                  |
| AD-FTD     | raw only     |  59 |          0.693 |                   0.767 |      0.02 |               0.78  |    0.039 |          0.717 |  0.087 |     0.021 |     0.144 | gamma|period_cv|roi (86%); gamma|slip_frac_b1|roi (6%); gamma|if_sd_b2|global (4%); gamma|if_sd_b2|roi (2%); gamma|if_sd_naive|roi (2%) |