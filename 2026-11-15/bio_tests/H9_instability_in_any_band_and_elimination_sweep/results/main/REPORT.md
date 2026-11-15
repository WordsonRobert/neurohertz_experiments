# Classification sweep: elimination report (EXPLORATORY)

Dataset ds004504; n = 88 ({'AD': 36, 'CN': 29, 'FTD': 23}). Verdict rules are in the header of sweep/60_report.py and were fixed before any real-data result existed.

| Explanation | Verdict | Evidence |
|---|---|---|
| E0 effect at 35-45 Hz | PRESENT | clusters overlapping 35-45 Hz: logpsd_csd 0, periodic_csd 1 |
| E1 muscle | NOT eliminated | ROI 35-45 Hz t: all epochs -0.23, lowest-EMG 25% -0.32, +EMG covariate 0.02, no BSS-CCA 0.20 |
| E2 ocular/frontal-polar | eliminated | frontal-polar burst excess AD-CN t = 1.24, p = 0.253 |
| E3 aperiodic | no fractal cluster | significant AD-CN clusters: fractal 0 (any frequency); periodic in 35-45 Hz 1; periodic ROI 35-45 t = 1.05 |
| E4 vigilance | NOT eliminated | per-stratum t (low->high alpha/theta): 0.16, -0.42, -0.94, -0.21 |
| E5 alpha harmonics | eliminated | 1:4 locking AD-CN t = 0.06, p = 0.958; rho with periodic 35-45 = -0.12 |
| E6 sharp transients | eliminated | transient rate AD-CN t = 0.03, p = 0.975; gamma change without transients t = 0.41, p = 0.694 |
| E7 notch/filter edge | not suspected | periodic_csd 30.0-35.0 Hz |
| E8 medication (signature only) | untestable | beta-range (15-30 Hz) AD-CN clusters: 16.0-23.0 Hz sign -1 [O1 O2 P3 P4 Pz T3 T5 T6] |

## All significant spectral clusters (p_FWER < 0.05)

| family              | contrast   | covariates   |   sign |     mass |   p_fwer |   f_lo |   f_hi |   f_peak | ch_peak   |   n_nodes | channels                                                   |
|:--------------------|:-----------|:-------------|-------:|---------:|---------:|-------:|-------:|---------:|:----------|----------:|:-----------------------------------------------------------|
| logpsd_csd          | AD-CN      | age_sex      |     -1 |  265.077 |    0.044 | 16     | 23     |   18     | T5        |        83 | O1 O2 P3 P4 Pz T3 T5 T6                                    |
| logpsd_csd          | AD-CN      | age_sex_emg  |     -1 |  444.256 |    0.017 | 15     | 29     |   18     | T5        |       133 | C3 O1 O2 P3 P4 Pz T3 T5 T6                                 |
| logpsd_csd          | AD-CN      | age_sex_emg  |      1 |  235.22  |    0.048 |  1.5   |  7.5   |    5     | Fz        |        73 | Cz F3 F4 F7 F8 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T4 T5 T6          |
| logpsd_avg          | AD-CN      | age_sex      |     -1 | 1205.01  |    0.006 |  9     | 32.5   |   18.5   | T5        |       329 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T3 T4 T5 T6 |
| logpsd_avg          | FTD-CN     | age_sex      |     -1 | 1115.01  |    0.009 | 14.5   | 47.5   |   17.5   | T5        |       362 | F3 F4 F8 Fp2 Fz O1 O2 P3 P4 Pz T3 T4 T5 T6                 |
| logpsd_csd_lowemg50 | AD-CN      | age_sex      |     -1 |  288.165 |    0.044 | 16     | 24     |   18     | T5        |        89 | O1 O2 P3 P4 Pz T3 T5 T6                                    |
| logpsd_csd_lowemg50 | FTD-CN     | age_sex      |     -1 |  254.414 |    0.049 | 14.5   | 35     |   20     | Fp2       |        78 | F8 Fp1 Fp2                                                 |
| logpsd_csd_lowemg25 | AD-CN      | age_sex      |     -1 |  252.767 |    0.042 | 15.5   | 23     |   18.5   | T5        |        78 | O1 O2 P3 P4 Pz T3 T5 T6                                    |
| periodic_csd        | AD-CN      | age_sex      |      1 |  554.924 |    0     |  4     |  7.5   |    5.5   | T4        |       121 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T3 T4 T5 T6 |
| periodic_csd        | AD-CN      | age_sex      |     -1 |  306.014 |    0.004 | 16     | 22.5   |   19.5   | P4        |        90 | C3 F4 F7 F8 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T5 T6                |
| periodic_csd        | AD-CN      | age_sex      |     -1 |  217.398 |    0.011 |  9     | 11.5   |   10     | T5        |        58 | C3 C4 Cz F3 F7 F8 O1 O2 P3 P4 Pz T3 T4 T5 T6               |
| periodic_csd        | AD-CN      | age_sex      |      1 |  145.584 |    0.031 | 30     | 35     |   33     | C4        |        45 | C4 F8 O1 O2 P3 P4 Pz T3 T4 T5 T6                           |
| periodic_csd        | AD-CN      | age_sex_emg  |      1 |  566.644 |    0.001 |  3.5   |  7.5   |    5.5   | Fz        |       123 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T3 T4 T5 T6 |
| periodic_csd        | AD-CN      | age_sex_emg  |     -1 |  306.281 |    0.005 | 16     | 22.5   |   19.5   | P4        |        90 | C3 F4 F7 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T5 T6                   |
| periodic_csd        | AD-CN      | age_sex_emg  |     -1 |  229.73  |    0.015 |  9     | 11.5   |   10.5   | T3        |        61 | C3 C4 Cz F3 F7 F8 Fp2 O1 O2 P3 P4 Pz T3 T4 T5 T6           |
| periodic_csd        | AD-CN      | age_sex_emg  |      1 |  155.077 |    0.036 | 30     | 35     |   34.5   | T6        |        48 | C4 F8 Fp2 O1 O2 P3 P4 Pz T3 T4 T5 T6                       |
| periodic_csd        | AD-FTD     | age_sex      |      1 |  164.556 |    0.028 |  4     |  5.5   |    4.5   | F4        |        51 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T3 T4 T5 T6 |
| periodic_csd        | AD-FTD     | age_sex_emg  |      1 |  152.045 |    0.042 |  4     |  5.5   |    4.5   | F4        |        48 | C3 C4 F3 F4 F7 F8 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T3 T4 T5 T6    |
| periodic_avg        | AD-CN      | age_sex      |      1 |  628.941 |    0     |  3.5   |  7.5   |    5.5   | T3        |       132 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T3 T4 T5 T6 |
| periodic_avg        | AD-CN      | age_sex      |     -1 |  572.466 |    0     | 15     | 21.5   |   19     | T5        |       155 | C3 C4 F3 F4 F7 F8 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T3 T4 T5 T6    |
| periodic_avg        | AD-CN      | age_sex      |      1 |  468.152 |    0.002 | 30     | 43.5   |   33.5   | Fp2       |       135 | C3 C4 F3 F4 F7 F8 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T3 T4 T5 T6    |
| periodic_avg        | AD-CN      | age_sex      |     -1 |  301.596 |    0.007 |  9     | 11.5   |   10     | T6        |        79 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T3 T4 T5 T6 |
| periodic_avg        | FTD-CN     | age_sex      |      1 |  166.652 |    0.034 |  4.5   |  6.5   |    5     | F8        |        52 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 O1 P3 P4 Pz T3 T4 T5 T6       |
| periodic_avg        | AD-FTD     | age_sex      |      1 |  222.71  |    0.02  |  3     |  6     |    4.5   | F4        |        65 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T3 T4 T5 T6 |
| irasa_periodic_csd  | AD-CN      | age_sex      |      1 |  883.96  |    0.001 |  4.15  |  7.324 |    5.859 | T5        |       194 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T3 T4 T5 T6 |
| irasa_periodic_csd  | AD-CN      | age_sex      |     -1 |  636.016 |    0.006 |  8.789 | 11.475 |   10.254 | T3        |       159 | C3 C4 Cz F3 F4 F7 F8 Fp1 Fp2 Fz O1 O2 P3 P4 Pz T3 T4 T5 T6 |
| irasa_periodic_csd  | AD-CN      | age_sex      |     -1 |  333.902 |    0.035 | 17.09  | 21.729 |   19.287 | P3        |        93 | C3 O1 O2 P3 P4 Pz T5 T6                                    |
| irasa_periodic_csd  | FTD-CN     | age_sex      |      1 |  397.445 |    0.028 |  4.883 |  7.08  |    5.371 | P3        |       119 | C3 C4 Cz F3 F4 F7 F8 Fz O1 O2 P3 P4 Pz T3 T4 T5 T6         |

## Subject-level measures, group tests (Freedman-Lane, age + sex, 5000 perms)

| measure                  |   AD-CN |   AD-FTD |   FTD-CN |
|:-------------------------|--------:|---------:|---------:|
| alpha_1to4_z             |  0.958  |   0.9366 |   0.8914 |
| aperiodic_knee           |  0.0262 |   0.9734 |   0.018  |
| burst_excess_fp          |  0.2533 |   0.0668 |   0.5677 |
| burst_excess_roi         |  0.0686 |   0.0406 |   0.2549 |
| emg_mean                 |  0.7618 |   0.3929 |   0.1618 |
| fractal_offset           |  0.0004 |   0.4185 |   0.0148 |
| fractal_slope            |  0.0004 |   0.3083 |   0.0176 |
| gamma_no_transient_delta |  0.6943 |   0.2955 |   0.6311 |
| iaf                      |  0.0356 |   0.0596 |   0.8546 |
| irasa_fractal_slope      |  0.0064 |   0.3997 |   0.0792 |
| irasa_periodic_35_45     |  0.0014 |   0.4147 |   0.1524 |
| logpow_35_45             |  0.7946 |   0.3819 |   0.1594 |
| logpow_35_45_lowemg      |  0.7379 |   0.4359 |   0.2106 |
| pac_alpha_z              |  0.5601 |   0.8572 |   0.3471 |
| pac_theta_z              |  0.9112 |   0.4603 |   0.5163 |
| periodic_30_48           |  0.0322 |   0.2346 |   0.9004 |
| periodic_35_45           |  0.117  |   0.3597 |   0.9638 |
| theta_alpha              |  0.0002 |   0.0684 |   0.0016 |
| transient_rate           |  0.9752 |   0.5671 |   0.4873 |
| vigilance_mean           |  0.0002 |   0.0736 |   0.0012 |

## Burst types (bursts_p95): K = 7, stability ARI 0.38

|   type |   share | auto_name                                        |   frac_roi |   mean_f_mean |   mean_nb_index |   mean_emg_coact |
|-------:|--------:|:-------------------------------------------------|-----------:|--------------:|----------------:|-----------------:|
|      0 |   0.098 | high abs_chirp, low log_dur_cycles, high f_mean  |      0.147 |        39.457 |          -0.425 |            0.192 |
|      1 |   0.109 | low log_f_mad, low log_dur_cycles, high spread   |      0.181 |        38.581 |          -0.532 |            0.258 |
|      2 |   0.183 | high log_dur_cycles, high log_f_mad, high spread |      0.135 |        38.524 |          -0.416 |            0.269 |
|      3 |   0.105 | low f_mean, low sharp, low log_amp               |      0.233 |        35.628 |          -0.421 |            0.126 |
|      4 |   0.308 | low spread, low log_amp, low sharp               |      0.262 |        38.098 |          -0.458 |            0.136 |
|      5 |   0.097 | low log_f_mad, low abs_chirp, high f_mean        |      0.154 |        39.627 |          -0.407 |            0.185 |
|      6 |   0.1   | high spread, high log_amp, high sharp            |      0.2   |        38.52  |          -0.684 |            0.444 |


| contrast   | covariates   | measure     |   n |       t |   p_perm |   p_holm |
|:-----------|:-------------|:------------|----:|--------:|---------:|---------:|
| AD-CN      | age_sex      | rate_type1  |  65 |  2.1115 |   0.044  |   0.9235 |
| AD-CN      | age_sex      | share_type1 |  65 |  2.9303 |   0.0065 |   0.1494 |
| AD-CN      | age_sex      | fmad_type4  |  65 | -2.6203 |   0.0145 |   0.3188 |
| AD-CN      | age_sex      | share_type4 |  65 | -1.8908 |   0.0725 |   1      |
| AD-CN      | age_sex      | fmad_type6  |  63 |  2.0313 |   0.057  |   1      |
| FTD-CN     | age_sex      | share_type1 |  52 |  2.142  |   0.044  |   0.9675 |
| FTD-CN     | age_sex      | rate_type4  |  52 | -2.6276 |   0.015  |   0.3448 |
| AD-FTD     | age_sex      | rate_type0  |  59 |  1.8469 |   0.082  |   1      |

## Burst types (bursts_p99): K = 7, stability ARI 0.26

|   type |   share | auto_name                                         |   frac_roi |   mean_f_mean |   mean_nb_index |   mean_emg_coact |
|-------:|--------:|:--------------------------------------------------|-----------:|--------------:|----------------:|-----------------:|
|      0 |   0.116 | high laterality, high spread, high log_dur_cycles |      0     |        38.645 |          -0.536 |            0.341 |
|      1 |   0.047 | low laterality, low spread, low emg_coact         |      0.292 |        36.907 |          -0.472 |            0.069 |
|      2 |   0.046 | low laterality, high spread, high log_dur_cycles  |      0.191 |        37.41  |          -0.51  |            0.251 |
|      3 |   0.218 | high laterality, low log_dur_cycles, low spread   |      0     |        38.598 |          -0.433 |            0.187 |
|      4 |   0.043 | low laterality, low sharp, low log_dur_cycles     |      0.28  |        37.77  |          -0.41  |            0.155 |
|      5 |   0.33  | low spread, low log_dur_cycles, low log_amp       |      0.31  |        38.25  |          -0.427 |            0.174 |
|      6 |   0.198 | high spread, high log_dur_cycles, high sharp      |      0.284 |        38.376 |          -0.55  |            0.334 |


| contrast   | covariates   | measure     |   n |       t |   p_perm |   p_holm |
|:-----------|:-------------|:------------|----:|--------:|---------:|---------:|
| AD-CN      | age_sex      | share_type3 |  65 | -2.075  |   0.0575 |   1      |
| AD-CN      | age_sex      | fmad_type5  |  65 | -2.05   |   0.0555 |   1      |
| FTD-CN     | age_sex      | fmad_type2  |  52 |  2.5184 |   0.012  |   0.2759 |
| FTD-CN     | age_sex      | fmad_type3  |  52 | -2.7067 |   0.0135 |   0.2969 |
| FTD-CN     | age_sex      | share_type4 |  52 |  1.9636 |   0.076  |   1      |
| FTD-CN     | age_sex      | fmad_type5  |  52 | -1.8726 |   0.0915 |   1      |
| FTD-CN     | age_sex      | fmad_all    |  52 | -1.7509 |   0.095  |   1      |
| AD-FTD     | age_sex      | fmad_type2  |  59 | -2.5442 |   0.017  |   0.3908 |
| AD-FTD     | age_sex      | rate_type5  |  59 |  1.8568 |   0.081  |   1      |

## Stratification

```
{
 "K": 2,
 "silhouette": {
  "2": 0.14178265093033834,
  "3": 0.11419447849342092,
  "4": 0.11370500178191659,
  "5": 0.12484377317282912
 },
 "stability_ari_mean": 0.42997271781057605,
 "stability_ari_sd": 0.3077738652451133,
 "chi2_cluster_vs_diagnosis_p": 0.031018268372164474,
 "mmse_by_cluster_median": {
  "0": 20.0,
  "1": 20.0
 },
 "kruskal_mmse_p": 0.444070290983026,
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
  "bursts_share_type0",
  "bursts_share_type1",
  "bursts_share_type2",
  "bursts_share_type3",
  "bursts_share_type4",
  "bursts_share_type5",
  "bursts_share_type6"
 ]
}
```

## Prediction (nested CV, 20 repeats)

| model                  |   n_features |   auc |   auc_lo |   auc_hi |   bal_acc |   acc |   p_perm | contrast   |   n |   gain_vs_base |   gain_lo |   gain_hi |   frac_repeats_gain_gt0 |
|:-----------------------|-------------:|------:|---------:|---------:|----------:|------:|---------:|:-----------|----:|---------------:|----------:|----------:|------------------------:|
| slowing                |            2 | 0.821 |    0.781 |    0.865 |     0.786 | 0.779 |    0.005 | AD-CN      |  58 |        nan     |   nan     |   nan     |                  nan    |
| aperiodic              |            2 | 0.774 |    0.731 |    0.814 |     0.742 | 0.742 |    0.005 | AD-CN      |  58 |        nan     |   nan     |   nan     |                  nan    |
| gamma_periodic         |            3 | 0.655 |    0.561 |    0.706 |     0.597 | 0.595 |    0.035 | AD-CN      |  58 |        nan     |   nan     |   nan     |                  nan    |
| bursts                 |            7 | 0.632 |    0.536 |    0.736 |     0.612 | 0.612 |    0.065 | AD-CN      |  58 |        nan     |   nan     |   nan     |                  nan    |
| coupling               |            3 | 0.411 |    0.333 |    0.496 |     0.416 | 0.417 |    0.791 | AD-CN      |  58 |        nan     |   nan     |   nan     |                  nan    |
| transients             |            2 | 0.355 |    0.291 |    0.44  |     0.392 | 0.398 |    0.9   | AD-CN      |  58 |        nan     |   nan     |   nan     |                  nan    |
| muscle                 |            1 | 0.547 |    0.472 |    0.586 |     0.568 | 0.573 |    0.269 | AD-CN      |  58 |        nan     |   nan     |   nan     |                  nan    |
| BASE slowing+aperiodic |            4 | 0.824 |    0.795 |    0.85  |     0.768 | 0.765 |    0.005 | AD-CN      |  58 |        nan     |   nan     |   nan     |                  nan    |
| BASE+gamma_periodic    |            7 | 0.8   |    0.757 |    0.834 |     0.748 | 0.745 |    0.005 | AD-CN      |  58 |         -0.024 |    -0.065 |     0.011 |                    0.2  |
| BASE+bursts            |           11 | 0.799 |    0.698 |    0.855 |     0.747 | 0.747 |    0.005 | AD-CN      |  58 |         -0.026 |    -0.106 |     0.035 |                    0.45 |
| BASE+coupling          |            7 | 0.801 |    0.749 |    0.855 |     0.733 | 0.729 |    0.005 | AD-CN      |  58 |         -0.023 |    -0.069 |     0.032 |                    0.3  |
| ALL                    |           20 | 0.757 |    0.677 |    0.805 |     0.732 | 0.731 |    0.005 | AD-CN      |  58 |         -0.067 |    -0.168 |     0.003 |                    0.05 |
| slowing                |            2 | 0.672 |    0.585 |    0.743 |     0.612 | 0.624 |    0.04  | FTD-CN     |  45 |        nan     |   nan     |   nan     |                  nan    |
| aperiodic              |            2 | 0.637 |    0.58  |    0.685 |     0.607 | 0.607 |    0.065 | FTD-CN     |  45 |        nan     |   nan     |   nan     |                  nan    |
| gamma_periodic         |            3 | 0.497 |    0.413 |    0.603 |     0.502 | 0.52  |    0.478 | FTD-CN     |  45 |        nan     |   nan     |   nan     |                  nan    |
| bursts                 |            7 | 0.523 |    0.383 |    0.661 |     0.524 | 0.54  |    0.453 | FTD-CN     |  45 |        nan     |   nan     |   nan     |                  nan    |
| coupling               |            3 | 0.338 |    0.235 |    0.454 |     0.374 | 0.363 |    0.925 | FTD-CN     |  45 |        nan     |   nan     |   nan     |                  nan    |
| transients             |            2 | 0.493 |    0.376 |    0.563 |     0.486 | 0.483 |    0.463 | FTD-CN     |  45 |        nan     |   nan     |   nan     |                  nan    |
| muscle                 |            1 | 0.586 |    0.495 |    0.623 |     0.596 | 0.6   |    0.164 | FTD-CN     |  45 |        nan     |   nan     |   nan     |                  nan    |
| BASE slowing+aperiodic |            4 | 0.653 |    0.573 |    0.717 |     0.636 | 0.64  |    0.055 | FTD-CN     |  45 |        nan     |   nan     |   nan     |                  nan    |
| BASE+gamma_periodic    |            7 | 0.603 |    0.517 |    0.691 |     0.596 | 0.604 |    0.129 | FTD-CN     |  45 |         -0.05  |    -0.112 |     0.055 |                    0.1  |
| BASE+bursts            |           11 | 0.589 |    0.48  |    0.674 |     0.6   | 0.612 |    0.164 | FTD-CN     |  45 |         -0.064 |    -0.208 |     0.068 |                    0.2  |
| BASE+coupling          |            7 | 0.597 |    0.526 |    0.674 |     0.59  | 0.59  |    0.209 | FTD-CN     |  45 |         -0.056 |    -0.145 |     0.035 |                    0.1  |
| ALL                    |           20 | 0.518 |    0.412 |    0.622 |     0.515 | 0.529 |    0.473 | FTD-CN     |  45 |         -0.135 |    -0.256 |     0.014 |                    0.05 |
| slowing                |            2 | 0.648 |    0.583 |    0.703 |     0.653 | 0.623 |    0.065 | AD-FTD     |  49 |        nan     |   nan     |   nan     |                  nan    |
| aperiodic              |            2 | 0.558 |    0.468 |    0.629 |     0.585 | 0.599 |    0.244 | AD-FTD     |  49 |        nan     |   nan     |   nan     |                  nan    |
| gamma_periodic         |            3 | 0.393 |    0.266 |    0.509 |     0.397 | 0.407 |    0.811 | AD-FTD     |  49 |        nan     |   nan     |   nan     |                  nan    |
| bursts                 |            7 | 0.567 |    0.488 |    0.676 |     0.56  | 0.579 |    0.249 | AD-FTD     |  49 |        nan     |   nan     |   nan     |                  nan    |
| coupling               |            3 | 0.381 |    0.247 |    0.506 |     0.403 | 0.389 |    0.841 | AD-FTD     |  49 |        nan     |   nan     |   nan     |                  nan    |
| transients             |            2 | 0.412 |    0.283 |    0.504 |     0.437 | 0.474 |    0.766 | AD-FTD     |  49 |        nan     |   nan     |   nan     |                  nan    |
| muscle                 |            1 | 0.45  |    0.352 |    0.531 |     0.466 | 0.459 |    0.557 | AD-FTD     |  49 |        nan     |   nan     |   nan     |                  nan    |
| BASE slowing+aperiodic |            4 | 0.572 |    0.495 |    0.636 |     0.557 | 0.556 |    0.244 | AD-FTD     |  49 |        nan     |   nan     |   nan     |                  nan    |
| BASE+gamma_periodic    |            7 | 0.544 |    0.425 |    0.622 |     0.552 | 0.552 |    0.413 | AD-FTD     |  49 |         -0.028 |    -0.139 |     0.043 |                    0.25 |
| BASE+bursts            |           11 | 0.589 |    0.533 |    0.669 |     0.59  | 0.599 |    0.194 | AD-FTD     |  49 |          0.017 |    -0.074 |     0.11  |                    0.65 |
| BASE+coupling          |            7 | 0.566 |    0.457 |    0.633 |     0.533 | 0.532 |    0.289 | AD-FTD     |  49 |         -0.006 |    -0.085 |     0.089 |                    0.35 |
| ALL                    |           20 | 0.5   |    0.388 |    0.616 |     0.519 | 0.538 |    0.537 | AD-FTD     |  49 |         -0.072 |    -0.204 |     0.057 |                    0.15 |