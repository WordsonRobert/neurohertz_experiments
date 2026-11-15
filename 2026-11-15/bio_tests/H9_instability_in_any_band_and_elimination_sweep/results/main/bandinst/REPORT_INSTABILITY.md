# Frequency instability across bands: characterization (EXPLORATORY)

Eligible measures (split-half SB-ICC >= 0.6, coverage >= 80%): 68 of 408 ({'excess': 9, 'presence': 22, 'raw': 37}).

## A. Most reliable measures

| feature                   | family   |   coverage |   icc_half |   icc_sb | eligible   |
|:--------------------------|:---------|-----------:|-----------:|---------:|:-----------|
| alpha|snr_median|roi      | presence |      1     |      0.967 |    0.983 | True       |
| alpha|snr_median|global   | presence |      1     |      0.967 |    0.983 | True       |
| alpha|frac_snr3|global    | presence |      1     |      0.962 |    0.981 | True       |
| alpha|frac_snr3|roi       | presence |      1     |      0.953 |    0.976 | True       |
| theta|snr_median|roi      | presence |      1     |      0.948 |    0.973 | True       |
| theta|snr_median|global   | presence |      1     |      0.945 |    0.972 | True       |
| theta|frac_snr3|global    | presence |      1     |      0.937 |    0.968 | True       |
| theta|frac_snr3|roi       | presence |      1     |      0.934 |    0.966 | True       |
| alpha|period_cv|roi       | raw      |      0.818 |      0.919 |    0.958 | True       |
| beta_high|frac_snr3|roi   | presence |      1     |      0.917 |    0.957 | True       |
| beta_high|snr_median|roi  | presence |      1     |      0.908 |    0.952 | True       |
| alpha|if_sd|roi           | raw      |      0.795 |      0.908 |    0.952 | False      |
| alpha|period_cv_b1|global | raw      |      1     |      0.905 |    0.95  | True       |
| alpha|period_cv|global    | raw      |      0.773 |      0.905 |    0.95  | False      |
| alpha|period_cv_b1|roi    | raw      |      1     |      0.9   |    0.947 | True       |
| alpha|if_sd_b2|roi        | raw      |      0.795 |      0.899 |    0.947 | False      |
| beta_low|frac_snr3|roi    | presence |      1     |      0.895 |    0.944 | True       |
| alpha|if_sd_b2|global     | raw      |      0.739 |      0.894 |    0.944 | False      |
| alpha|if_sd_b1|roi        | raw      |      1     |      0.893 |    0.943 | True       |
| alpha|if_sd|global        | raw      |      0.739 |      0.89  |    0.942 | False      |
| alpha|period_cv_b2|roi    | raw      |      0.818 |      0.885 |    0.939 | True       |
| alpha|period_cv_b2|global | raw      |      0.773 |      0.882 |    0.937 | False      |
| beta_low|snr_median|roi   | presence |      1     |      0.879 |    0.936 | True       |
| theta|period_cv_b1|global | raw      |      0.636 |      0.876 |    0.934 | False      |
| theta|period_cv_b1|roi    | raw      |      0.523 |      0.869 |    0.93  | False      |

## B. How much of each reliable raw measure is spectrum

| feature                          |   r2_raw_on_surrogate |   rho_with_presence |
|:---------------------------------|----------------------:|--------------------:|
| alpha|period_cv_b1|global        |                 0.922 |               0.519 |
| beta_low|pf_sd_epochs_b1|global  |                 0.919 |               0.141 |
| beta_high|pf_sd_epochs_b1|global |                 0.907 |              -0.418 |
| alpha|if_sd_b1|roi               |                 0.899 |               0.863 |
| alpha|period_cv|roi              |                 0.895 |               0.618 |
| alpha|period_cv_b1|roi           |                 0.89  |               0.552 |
| theta|pf_sd_epochs_b1|global     |                 0.874 |              -0.627 |
| beta_high|pf_sd_epochs_b1|roi    |                 0.869 |              -0.459 |
| alpha|if_sd_b1|global            |                 0.862 |               0.797 |
| beta_low|pf_sd_epochs_b1|roi     |                 0.848 |               0.104 |
| alpha|slip_frac_b1|roi           |                 0.834 |               0.485 |
| alpha|period_cv_b2|roi           |                 0.823 |               0.555 |
| gamma|pf_sd_epochs_b1|global     |                 0.821 |              -0.402 |
| alpha|slip_frac_b1|global        |                 0.821 |               0.486 |
| alpha|pf_sd_epochs_b1|global     |                 0.814 |              -0.738 |
| theta|pf_sd_epochs_b1|roi        |                 0.782 |              -0.565 |
| alpha|if_sd_naive|roi            |                 0.743 |               0.617 |
| alpha|if_sd_naive|global         |                 0.691 |               0.556 |
| alpha|pf_sd_epochs_b1|roi        |                 0.627 |              -0.644 |
| beta_high|period_cv_b1|roi       |                 0.582 |               0.655 |
| beta_low|period_cv_b1|roi        |                 0.545 |               0.592 |
| beta_low|period_cv_b1|global     |                 0.54  |               0.613 |
| beta_high|if_sd_b1|global        |                 0.515 |               0.613 |
| beta_low|if_sd_b1|roi            |                 0.503 |               0.672 |
| beta_high|if_sd_b1|roi           |                 0.477 |               0.615 |
| beta_low|if_sd_b1|global         |                 0.468 |               0.628 |
| beta_high|if_sd_naive|global     |                 0.462 |               0.519 |
| beta_low|if_sd_naive|roi         |                 0.442 |               0.611 |
| beta_high|if_sd_naive|roi        |                 0.41  |               0.579 |
| beta_low|if_sd_naive|global      |                 0.391 |               0.575 |
| beta_high|period_cv_b1|global    |                 0.387 |               0.577 |
| gamma|if_sd_naive|global         |                 0.375 |               0.482 |
| gamma|if_sd_b1|global            |                 0.358 |               0.575 |
| theta|if_sd_b1|global            |                 0.247 |               0.491 |
| gamma|period_cv_b1|global        |                 0.241 |               0.587 |
| theta|if_sd_naive|global         |                 0.224 |               0.352 |
| gamma|slip_frac_b1|global        |                 0.031 |               0.306 |

## C. Structure
```
{
 "raw": {
  "n": 37,
  "var_explained_pc1_3": [
   0.254,
   0.181,
   0.103
  ],
  "pc1_top_loadings": {
   "alpha|period_cv_b1|roi": 0.26,
   "alpha|period_cv_b1|global": 0.23,
   "beta_low|period_cv_b1|global": -0.22,
   "beta_low|period_cv_b1|roi": -0.22,
   "alpha|period_cv|roi": 0.22,
   "beta_low|if_sd_b1|global": -0.21,
   "alpha|if_sd_b1|global": 0.21,
   "beta_low|if_sd_naive|global": -0.21
  }
 },
 "excess": {
  "n": 9,
  "var_explained_pc1_3": [
   0.424,
   0.311,
   0.165
  ],
  "pc1_top_loadings": {
   "beta_high|if_sd_naive__excess|global": -0.46,
   "beta_high|if_sd_b1__excess|global": -0.45,
   "beta_high|period_cv_b1__excess|global": -0.41,
   "beta_high|if_sd_naive__excess|roi": -0.4,
   "alpha|if_sd_b1__excess|global": -0.31,
   "alpha|if_sd_b1__excess|roi": -0.24,
   "alpha|if_sd_naive__excess|global": -0.24,
   "alpha|if_sd_naive__excess|roi": -0.19
  }
 }
}
```

## D. Family-wise significant group differences (maxT p < 0.05)

| family   | contrast   | ladder   | feature                      |       t |   p_maxT |
|:---------|:-----------|:---------|:-----------------------------|--------:|---------:|
| raw      | AD-CN      | L0       | alpha|pf_sd_epochs_b1|roi    |  3.56   |   0.028  |
| raw      | AD-CN      | L0       | alpha|pf_sd_epochs_b1|global |  4.1536 |   0.0045 |
| presence | AD-CN      | L0       | alpha|frac_snr3|roi          | -4.45   |   0.001  |
| presence | AD-CN      | L0       | theta|frac_snr3|roi          |  4.8664 |   0.0005 |
| presence | AD-CN      | L0       | theta|snr_median|roi         |  5.0383 |   0.0005 |
| presence | AD-CN      | L0       | alpha|frac_snr3|global       | -4.1024 |   0.003  |
| presence | AD-CN      | L0       | delta|snr_median|global      | -3.4599 |   0.019  |
| presence | AD-CN      | L0       | theta|frac_snr3|global       |  5.2566 |   0.0005 |
| presence | AD-CN      | L0       | theta|snr_median|global      |  5.0754 |   0.0005 |
| presence | FTD-CN     | L0       | delta|snr_median|global      | -3.4868 |   0.0195 |
| presence | FTD-CN     | L0       | theta|snr_median|global      |  3.2005 |   0.038  |
| presence | FTD-CN     | L1       | delta|snr_median|global      | -3.5873 |   0.021  |
| presence | FTD-CN     | L2       | delta|snr_median|global      | -3.3499 |   0.042  |

## E. Time-on-task drift, AD vs CN (maxT p < 0.1)

| feature   | t   | p_maxT   |
|-----------|-----|----------|

## F. Severity within AD (q < 0.1)

| feature   | n   | rho_partial   | p_perm   | q_bh   |
|-----------|-----|---------------|----------|--------|

## G. Prediction with in-fold selection

| contrast   | pool         |   n |   auc_baseline |   auc_instability_alone |   p_alone |   auc_baseline_plus |   p_plus |   bal_acc_plus |   gain |   gain_lo |   gain_hi | top_picks                                                                                                                                                                                           |
|:-----------|:-------------|----:|---------------:|------------------------:|----------:|--------------------:|---------:|---------------:|-------:|----------:|----------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| AD-CN      | all eligible |  65 |          0.818 |                   0.711 |     0.01  |               0.801 |    0.005 |          0.706 | -0.017 |    -0.047 |     0.017 | theta|frac_snr3|global (52%); alpha|frac_snr3|roi (25%); theta|frac_snr3|roi (10%); alpha|pf_sd_epochs_b1|global (6%); theta|snr_median|roi (3%)                                                    |
| AD-CN      | excess only  |  65 |          0.818 |                   0.479 |     0.552 |               0.81  |    0.005 |          0.723 | -0.009 |    -0.039 |     0.011 | alpha|period_cv_b1__excess|roi (45%); beta_high|period_cv_b1__excess|global (25%); beta_high|if_sd_b1__excess|global (17%); alpha|if_sd_naive__excess|roi (7%); alpha|if_sd_b1__excess|roi (6%)     |
| AD-CN      | raw only     |  65 |          0.818 |                   0.674 |     0.035 |               0.809 |    0.005 |          0.712 | -0.009 |    -0.042 |     0.01  | alpha|pf_sd_epochs_b1|global (49%); alpha|pf_sd_epochs_b1|roi (31%); theta|if_sd_b1|global (10%); alpha|if_sd_b1|roi (5%); theta|if_sd_naive|global (2%)                                            |
| FTD-CN     | all eligible |  52 |          0.728 |                   0.667 |     0.05  |               0.714 |    0.03  |          0.669 | -0.014 |    -0.055 |     0.023 | theta|snr_median|global (32%); delta|snr_median|global (30%); theta|snr_median|roi (29%); theta|frac_snr3|global (6%); beta_high|if_sd_naive|global (1%)                                            |
| FTD-CN     | excess only  |  52 |          0.728 |                   0.475 |     0.567 |               0.686 |    0.03  |          0.646 | -0.042 |    -0.116 |     0.005 | alpha|if_sd_naive__excess|roi (64%); beta_high|period_cv_b1__excess|global (21%); alpha|if_sd_b1__excess|global (9%); beta_high|if_sd_naive__excess|roi (4%); alpha|if_sd_naive__excess|global (2%) |
| FTD-CN     | raw only     |  52 |          0.728 |                   0.5   |     0.423 |               0.671 |    0.075 |          0.618 | -0.057 |    -0.121 |    -0.014 | beta_low|pf_sd_epochs_b1|roi (41%); beta_high|if_sd_naive|global (12%); alpha|pf_sd_epochs_b1|global (10%); beta_high|if_sd_b1|global (9%); alpha|pf_sd_epochs_b1|roi (9%)                          |
| AD-FTD     | all eligible |  59 |          0.548 |                   0.592 |     0.184 |               0.585 |    0.199 |          0.578 |  0.036 |    -0.067 |     0.111 | theta|if_sd_b1|global (42%); theta|if_sd_naive|global (25%); alpha|snr_median|roi (12%); alpha|period_cv_b1__excess|roi (11%); alpha|pf_sd_epochs_b1|roi (3%)                                       |
| AD-FTD     | excess only  |  59 |          0.548 |                   0.616 |     0.114 |               0.583 |    0.219 |          0.609 |  0.035 |    -0.016 |     0.073 | alpha|period_cv_b1__excess|roi (82%); beta_high|period_cv_b1__excess|global (13%); beta_high|if_sd_b1__excess|global (4%); beta_high|if_sd_naive__excess|global (1%)                                |
| AD-FTD     | raw only     |  59 |          0.548 |                   0.665 |     0.095 |               0.616 |    0.129 |          0.614 |  0.068 |    -0.013 |     0.132 | theta|if_sd_b1|global (54%); theta|if_sd_naive|global (38%); alpha|pf_sd_epochs_b1|roi (5%); alpha|pf_sd_epochs_b1|global (2%); gamma|period_cv_b1|global (1%)                                      |