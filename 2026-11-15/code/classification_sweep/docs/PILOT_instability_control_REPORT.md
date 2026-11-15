> Cloud pilot, 2026-11-15: 28 synthetic subjects (10 CN, 10 AD, 8 FTD), mechanism erratic_drive, k = 1.0, 2 surrogates, 300 permutations. Plumbing and ground-truth check only; not a real-data result.

# Frequency instability across bands: characterization (EXPLORATORY)

Eligible measures (split-half SB-ICC >= 0.6, coverage >= 80%): 58 of 408 ({'excess': 10, 'presence': 17, 'raw': 31}).

## A. Most reliable measures

| feature                           | family   |   coverage |   icc_half |   icc_sb | eligible   |
|:----------------------------------|:---------|-----------:|-----------:|---------:|:-----------|
| beta_high|frac_snr3|global        | presence |          1 |      0.992 |    0.996 | True       |
| beta_high|snr_median|global       | presence |          1 |      0.99  |    0.995 | True       |
| beta_high|frac_snr3|roi           | presence |          1 |      0.981 |    0.99  | True       |
| beta_high|snr_median|roi          | presence |          1 |      0.976 |    0.988 | True       |
| alpha|snr_median|roi              | presence |          1 |      0.97  |    0.985 | True       |
| alpha|snr_median|global           | presence |          1 |      0.959 |    0.979 | True       |
| gamma|frac_snr3|global            | presence |          1 |      0.952 |    0.975 | True       |
| alpha|frac_snr3|global            | presence |          1 |      0.952 |    0.975 | True       |
| gamma|frac_snr3|roi               | presence |          1 |      0.944 |    0.971 | True       |
| alpha|frac_snr3|roi               | presence |          1 |      0.944 |    0.971 | True       |
| gamma|snr_median|global           | presence |          1 |      0.943 |    0.971 | True       |
| gamma|slip_frac_b1|global         | raw      |          1 |      0.937 |    0.967 | True       |
| gamma|snr_median|roi              | presence |          1 |      0.924 |    0.961 | True       |
| gamma|slip_frac|global            | raw      |          1 |      0.923 |    0.96  | True       |
| gamma|pf_sd_epochs_b2|global      | raw      |          1 |      0.916 |    0.956 | True       |
| beta_low|frac_snr3|global         | presence |          1 |      0.892 |    0.943 | True       |
| beta_low|frac_snr3|roi            | presence |          1 |      0.872 |    0.932 | True       |
| beta_low|snr_median|roi           | presence |          1 |      0.86  |    0.925 | True       |
| gamma|pf_sd_epochs|global         | raw      |          1 |      0.858 |    0.924 | True       |
| beta_low|snr_median|global        | presence |          1 |      0.84  |    0.913 | True       |
| gamma|pf_sd_epochs_b2|roi         | raw      |          1 |      0.833 |    0.909 | True       |
| gamma|if_sd_b1|global             | raw      |          1 |      0.832 |    0.909 | True       |
| gamma|burst_f_sd_b1|global        | raw      |          1 |      0.81  |    0.895 | True       |
| gamma|slip_frac_b2__excess|global | excess   |          1 |      0.794 |    0.885 | True       |
| gamma|burst_f_sd|global           | raw      |          1 |      0.784 |    0.879 | True       |

## B. How much of each reliable raw measure is spectrum

| feature                          |   r2_raw_on_surrogate |   rho_with_presence |
|:---------------------------------|----------------------:|--------------------:|
| gamma|pf_sd_epochs_b2|global     |                 0.922 |              -0.562 |
| gamma|pf_sd_epochs|global        |                 0.92  |              -0.543 |
| gamma|pf_sd_epochs_b2|roi        |                 0.906 |              -0.372 |
| gamma|burst_f_sd_b1|global       |                 0.904 |              -0.54  |
| beta_high|pf_sd_epochs_b1|global |                 0.886 |              -0.761 |
| gamma|slip_frac|global           |                 0.88  |               0.416 |
| gamma|burst_f_sd|global          |                 0.875 |              -0.499 |
| gamma|slip_frac_b1|global        |                 0.875 |               0.466 |
| beta_high|period_cv_b1|global    |                 0.832 |               0.854 |
| gamma|slip_frac_b1|roi           |                 0.807 |               0.365 |
| gamma|slip_frac|roi              |                 0.789 |               0.357 |
| gamma|pf_sd_epochs_b1|global     |                 0.785 |              -0.55  |
| gamma|burst_f_sd_b1|roi          |                 0.784 |              -0.387 |
| gamma|pf_sd_epochs|roi           |                 0.757 |              -0.372 |
| gamma|if_sd_b1|global            |                 0.737 |               0.715 |
| gamma|burst_f_sd|roi             |                 0.616 |              -0.293 |
| gamma|if_sd_b1|roi               |                 0.571 |               0.767 |
| gamma|if_sd_naive|global         |                 0.571 |               0.46  |
| gamma|period_cv_b2|global        |                 0.561 |              -0.303 |
| gamma|slip_frac_b2|global        |                 0.529 |               0.209 |
| gamma|period_cv|global           |                 0.496 |               0.018 |
| gamma|period_cv_b1|roi           |                 0.496 |               0.678 |
| gamma|period_cv_b1|global        |                 0.487 |               0.501 |
| gamma|if_sd|global               |                 0.463 |               0.433 |
| alpha|if_sd_naive|roi            |                 0.458 |              -0.687 |
| alpha|period_cv_b1|global        |                 0.431 |              -0.275 |
| gamma|if_sd|roi                  |                 0.352 |               0.616 |
| gamma|period_cv_b2|roi           |                 0.301 |              -0.132 |
| gamma|period_cv|roi              |                 0.299 |               0.307 |
| gamma|if_sd_b2|roi               |                 0.23  |               0.516 |
| alpha|if_sd_naive|global         |                 0.21  |              -0.197 |

## C. Structure
```
{
 "raw": {
  "n": 31,
  "var_explained_pc1_3": [
   0.455,
   0.228,
   0.104
  ],
  "pc1_top_loadings": {
   "gamma|burst_f_sd|global": 0.26,
   "gamma|burst_f_sd_b1|global": 0.26,
   "gamma|pf_sd_epochs_b2|roi": 0.26,
   "gamma|pf_sd_epochs_b2|global": 0.25,
   "gamma|pf_sd_epochs|global": 0.25,
   "gamma|burst_f_sd_b1|roi": 0.25,
   "gamma|pf_sd_epochs|roi": 0.24,
   "gamma|pf_sd_epochs_b1|global": 0.24
  }
 },
 "excess": {
  "n": 10,
  "var_explained_pc1_3": [
   0.519,
   0.156,
   0.112
  ],
  "pc1_top_loadings": {
   "gamma|if_sd__excess|global": -0.41,
   "gamma|slip_frac__excess|global": -0.41,
   "gamma|slip_frac_b1__excess|global": -0.4,
   "gamma|period_cv_b1__excess|global": -0.39,
   "gamma|if_sd_b2__excess|global": -0.37,
   "gamma|if_sd_b1__excess|global": -0.36,
   "gamma|slip_frac_b2__excess|global": -0.28,
   "gamma|burst_f_sd_b2__excess|roi": -0.05
  }
 }
}
```

## D. Family-wise significant group differences (maxT p < 0.05)

| family   | contrast   | ladder   | feature                           |       t |   p_maxT |
|:---------|:-----------|:---------|:----------------------------------|--------:|---------:|
| raw      | FTD-CN     | L0       | gamma|period_cv_b1|global         |  4.7479 |   0.0465 |
| raw      | FTD-CN     | L3       | gamma|period_cv_b1|global         |  6.5154 |   0.0233 |
| raw      | AD-FTD     | L2       | gamma|if_sd_b1|global             | -5.2508 |   0.0332 |
| raw      | AD-FTD     | L2       | gamma|period_cv_b1|global         | -5.562  |   0.0266 |
| excess   | FTD-CN     | L0       | gamma|if_sd__excess|global        |  4.073  |   0.0299 |
| excess   | FTD-CN     | L0       | gamma|period_cv_b1__excess|global |  6.3049 |   0.0033 |
| excess   | FTD-CN     | L0       | gamma|slip_frac__excess|global    |  5.0635 |   0.0033 |
| excess   | FTD-CN     | L0       | gamma|slip_frac_b1__excess|global |  5.033  |   0.0033 |
| excess   | FTD-CN     | L1       | gamma|period_cv_b1__excess|global |  7.1306 |   0.0066 |
| excess   | FTD-CN     | L1       | gamma|slip_frac__excess|global    |  5.1854 |   0.01   |
| excess   | FTD-CN     | L1       | gamma|slip_frac_b1__excess|global |  5.1384 |   0.01   |
| excess   | FTD-CN     | L2       | gamma|period_cv_b1__excess|global |  7.3344 |   0.01   |
| excess   | FTD-CN     | L2       | gamma|slip_frac__excess|global    |  5.3053 |   0.0233 |
| excess   | FTD-CN     | L2       | gamma|slip_frac_b1__excess|global |  5.2465 |   0.0233 |
| excess   | FTD-CN     | L3       | gamma|period_cv_b1__excess|global |  7.0928 |   0.0066 |
| excess   | FTD-CN     | L3       | gamma|slip_frac__excess|global    |  5.1062 |   0.0465 |
| excess   | FTD-CN     | L3       | gamma|slip_frac_b1__excess|global |  5.0964 |   0.0465 |
| excess   | AD-FTD     | L0       | gamma|slip_frac__excess|global    | -4.529  |   0.0199 |
| excess   | AD-FTD     | L0       | gamma|slip_frac_b1__excess|global | -4.5758 |   0.0199 |
| excess   | AD-FTD     | L1       | gamma|slip_frac__excess|global    | -4.5846 |   0.0233 |
| excess   | AD-FTD     | L1       | gamma|slip_frac_b1__excess|global | -4.8796 |   0.0233 |
| excess   | AD-FTD     | L2       | gamma|slip_frac__excess|global    | -4.5023 |   0.0432 |
| excess   | AD-FTD     | L2       | gamma|slip_frac_b1__excess|global | -4.548  |   0.0432 |
| excess   | AD-FTD     | L3       | gamma|slip_frac__excess|global    | -5.1049 |   0.0399 |
| excess   | AD-FTD     | L3       | gamma|slip_frac_b1__excess|global | -5.4007 |   0.0332 |

## E. Time-on-task drift, AD vs CN (maxT p < 0.1)

| feature   | t   | p_maxT   |
|-----------|-----|----------|

## F. Severity within AD (q < 0.1)

none

## G. Prediction with in-fold selection

| contrast   | pool         |   n |   auc_baseline |   auc_instability_alone |   p_alone |   auc_baseline_plus |   p_plus |   bal_acc_plus |   gain |   gain_lo |   gain_hi | top_picks                                                                                                                                 |
|:-----------|:-------------|----:|---------------:|------------------------:|----------:|--------------------:|---------:|---------------:|-------:|----------:|----------:|:------------------------------------------------------------------------------------------------------------------------------------------|
| AD-CN      | all eligible |  20 |          0.568 |                   0.666 |     0.097 |               0.782 |    0.032 |          0.7   |  0.214 |     0.166 |     0.23  | gamma|period_cv_b1__excess|global (56%); gamma|if_sd__excess|global (24%); gamma|period_cv|roi (16%); gamma|if_sd|roi (4%)                |
| AD-CN      | excess only  |  20 |          0.568 |                   0.738 |     0.097 |               0.784 |    0.032 |          0.74  |  0.216 |     0.171 |     0.266 | gamma|period_cv_b1__excess|global (76%); gamma|if_sd__excess|global (24%)                                                                 |
| AD-CN      | raw only     |  20 |          0.568 |                   0.612 |     0.194 |               0.694 |    0.065 |          0.56  |  0.126 |    -0.023 |     0.249 | gamma|period_cv|roi (56%); gamma|if_sd|roi (20%); gamma|if_sd_b2|roi (8%); alpha|if_sd_naive|roi (4%); gamma|slip_frac|roi (4%)           |
| FTD-CN     | all eligible |  18 |          0.488 |                   0.955 |     0.032 |               0.922 |    0.032 |          0.835 |  0.435 |     0.331 |     0.565 | gamma|period_cv_b1__excess|global (88%); gamma|if_sd_naive|global (8%); gamma|if_sd__excess|global (4%)                                   |
| FTD-CN     | excess only  |  18 |          0.488 |                   0.978 |     0.032 |               0.933 |    0.032 |          0.855 |  0.445 |     0.354 |     0.565 | gamma|period_cv_b1__excess|global (96%); gamma|if_sd__excess|global (4%)                                                                  |
| FTD-CN     | raw only     |  18 |          0.488 |                   0.838 |     0.032 |               0.772 |    0.032 |          0.673 |  0.285 |     0.052 |     0.449 | gamma|period_cv_b1|global (60%); gamma|if_sd_naive|global (20%); gamma|if_sd|global (16%); gamma|slip_frac_b2|global (4%)                 |
| AD-FTD     | all eligible |  18 |          0.415 |                   0.8   |     0.161 |               0.76  |    0.097 |          0.69  |  0.345 |     0.283 |     0.375 | gamma|slip_frac__excess|global (52%); gamma|period_cv_b1|global (40%); gamma|period_cv_b1__excess|global (4%); alpha|if_sd_naive|roi (4%) |
| AD-FTD     | excess only  |  18 |          0.415 |                   0.862 |     0.161 |               0.753 |    0.065 |          0.645 |  0.338 |     0.279 |     0.428 | gamma|slip_frac__excess|global (84%); gamma|period_cv_b1__excess|global (16%)                                                             |
| AD-FTD     | raw only     |  18 |          0.415 |                   0.818 |     0.065 |               0.823 |    0.065 |          0.732 |  0.408 |     0.314 |     0.486 | gamma|period_cv_b1|global (88%); alpha|if_sd_naive|roi (8%); gamma|slip_frac|roi (4%)                                                     |