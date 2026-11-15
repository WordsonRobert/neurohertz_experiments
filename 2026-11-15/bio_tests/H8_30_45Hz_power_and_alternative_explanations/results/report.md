# Exploratory step 1: existing features (ds004504, post-freeze, EXPLORATORY)

## A. What drove the old 73% (old metric = SD of instantaneous frequency in 25-80 Hz)

| model                                                     |   auc |   auc_lo |   auc_hi |   acc |   loso_auc |   loso_acc |
|:----------------------------------------------------------|------:|---------:|---------:|------:|-----------:|-----------:|
| legacy_std (old NeuroHertz metric) alone                  | 0.483 |    0.382 |    0.579 | 0.538 |      0.337 |      0.508 |
| legacy_std with 1/f exponent regressed out (inside folds) | 0.391 |    0.279 |    0.482 | 0.542 |    nan     |    nan     |
| legacy_std with exponent + theta/alpha regressed out      | 0.408 |    0.332 |    0.481 | 0.542 |    nan     |    nan     |
| 1/f exponent alone                                        | 0.768 |    0.759 |    0.776 | 0.682 |      0.75  |      0.677 |
| theta/alpha ratio alone                                   | 0.825 |    0.808 |    0.84  | 0.717 |      0.82  |      0.708 |
| gamma envelope amplitude (env_mean) alone                 | 0.539 |    0.476 |    0.574 | 0.533 |      0.468 |      0.523 |
| burst_freq_sd (new primary) alone                         | 0.544 |    0.459 |    0.589 | 0.568 |      0.478 |      0.585 |


Spearman correlation of legacy_std with:

|                         |     0 |
|:------------------------|------:|
| roi__aperiodic_exponent |  0.22 |
| roi__theta_alpha_ratio  |  0.22 |
| roi__alpha_peak_freq    | -0.3  |
| roi__env_mean           | -0.11 |
| roi__gamma_abs_logpow   | -0.13 |
| roi__emg_logpow         |  0.21 |
| roi__relpow_gamma       |  0.1  |
| roi__burst_freq_sd      |  0.76 |


## B. 30-45 Hz measures, AD vs CN: does the difference survive each alternative explanation?

p = Freedman-Lane permutation p (2000 perms) for the group term after the listed covariates.


| feature                  |      g |   p[none] |   p[age_sex] |   p[+exponent] |   p[+EMG(sentinel 55-90Hz)] |   p[+slowing(theta/alpha)] |   p[+all three] |
|:-------------------------|-------:|----------:|-------------:|---------------:|----------------------------:|---------------------------:|----------------:|
| roi__gamma_abs_logpow    | -0.26  |     0.295 |        0.559 |          0.279 |                       0.712 |                      0.662 |           0.382 |
| roi__relpow_gamma        |  0.206 |     0.397 |        0.212 |          0.012 |                       0.158 |                      0.321 |           0.029 |
| roi__gamma_osc_logpow    |  1.098 |     0     |        0     |          0.037 |                       0     |                      0.053 |           0.113 |
| roi__gamma_above_floor   |  0.76  |     0.002 |        0.017 |          0.042 |                       0.017 |                      0.174 |           0.124 |
| roi__env_mean            | -0.271 |     0.272 |        0.518 |          0.245 |                       0.646 |                      0.667 |           0.361 |
| roi__burst_rate          |  0.275 |     0.255 |        0.297 |          0.327 |                       0.305 |                      0.128 |           0.173 |
| roi__hf_slope_30_90      |  0.337 |     0.175 |        0.102 |          0.559 |                       0.101 |                      0.453 |           0.633 |
| roi__emg_logpow          | -0.04  |     0.872 |        0.683 |          0.148 |                       0.098 |                      0.961 |           0.124 |
| emg_sentinel__emg_logpow | -0.287 |     0.231 |        0.604 |          0.701 |                       0.593 |                      0.479 |           0.893 |
| roi__floor_log10         |  0.578 |     0.018 |        0.072 |          0.166 |                       0.059 |                      0.998 |           0.708 |
| roi__aperiodic_exponent  |  1.113 |     0     |        0     |          0     |                       0     |                      0.106 |           0.111 |
| roi__legacy_std          |  0.12  |     0.667 |        0.495 |          0.72  |                       0.445 |                      0.608 |           0.754 |


Same for FTD vs CN (is it AD-specific or any dementia?):


| feature                  |      g |   p[age_sex] |   p[+all three] |
|:-------------------------|-------:|-------------:|----------------:|
| roi__gamma_abs_logpow    | -0.337 |        0.13  |           0.588 |
| roi__relpow_gamma        |  0.221 |        0.658 |           0.063 |
| roi__gamma_osc_logpow    |  0.839 |        0.016 |           0.273 |
| roi__gamma_above_floor   |  0.521 |        0.215 |           0.347 |
| roi__env_mean            | -0.254 |        0.105 |           0.606 |
| roi__burst_rate          |  0.166 |        0.924 |           0.903 |
| roi__hf_slope_30_90      |  0.309 |        0.165 |           0.585 |
| roi__emg_logpow          | -0.196 |        0.38  |           0.212 |
| emg_sentinel__emg_logpow | -0.455 |        0.073 |           0.445 |
| roi__floor_log10         |  0.28  |        0.584 |           0.99  |
| roi__aperiodic_exponent  |  0.74  |        0.015 |           0.344 |
| roi__legacy_std          | -0.047 |        0.874 |           0.908 |


## C. Where on the scalp (Hedges g AD-CN per region; muscle is largest at temporal/frontal edges)

| metric             |   frontal |   central |   temporal |   parietal |   occipital |   csd_roi |
|:-------------------|----------:|----------:|-----------:|-----------:|------------:|----------:|
| gamma_abs_logpow   |     -0.24 |     -0.33 |      -0.41 |      -0.24 |       -0.26 |     -0.31 |
| relpow_gamma       |     -0.32 |     -0.12 |      -0.12 |       0.22 |        0.17 |      0    |
| gamma_above_floor  |      0.47 |      0.34 |       0.63 |       0.75 |        0.71 |      0.56 |
| emg_logpow         |     -0.2  |     -0.22 |      -0.31 |       0.02 |       -0.11 |     -0.14 |
| aperiodic_exponent |      1.08 |      1.07 |       1.12 |       1.16 |        0.97 |      1.15 |
| theta_alpha_ratio  |      1.19 |      1.17 |       1.32 |       1.07 |        1.28 |      1.14 |
| env_mean           |     -0.11 |     -0.25 |      -0.32 |      -0.27 |       -0.25 |     -0.27 |


## D. Within-group coupling of 30-45 Hz measures with muscle (55-90 Hz) and 1/f

| group   | feature                |   rho_emg |   rho_hfslope |   rho_exponent |
|:--------|:-----------------------|----------:|--------------:|---------------:|
| CN      | roi__gamma_abs_logpow  |      0.68 |         -0.28 |          -0.44 |
| CN      | roi__gamma_above_floor |      0.36 |          0.06 |          -0.19 |
| CN      | roi__relpow_gamma      |      0.12 |          0.09 |          -0.4  |
| CN      | roi__legacy_std        |      0.36 |          0.63 |          -0.09 |
| CN      | roi__burst_freq_sd     |      0.26 |          0.6  |           0.12 |
| AD      | roi__gamma_abs_logpow  |      0.74 |         -0.02 |          -0.28 |
| AD      | roi__gamma_above_floor |     -0.03 |         -0.36 |           0.15 |
| AD      | roi__relpow_gamma      |      0.12 |          0.14 |          -0.51 |
| AD      | roi__legacy_std        |      0.18 |          0.65 |           0.36 |
| AD      | roi__burst_freq_sd     |      0.26 |          0.6  |           0.29 |
| FTD     | roi__gamma_abs_logpow  |      0.79 |         -0.37 |          -0.45 |
| FTD     | roi__gamma_above_floor |      0.03 |         -0.28 |          -0.16 |
| FTD     | roi__relpow_gamma      |      0.38 |         -0.01 |          -0.75 |
| FTD     | roi__legacy_std        |      0.17 |          0.4  |           0.43 |
| FTD     | roi__burst_freq_sd     |      0.39 |          0.35 |           0.22 |


## E. Is a 30-45 Hz peak a harmonic of alpha?  Presence by group.  Severity (MMSE within AD)

Subjects with a fitted 30-45 Hz peak: 49; rho(peak f, alpha f) = -0.14; median f_gamma/f_alpha = 3.00; fraction within 0.15 of an integer ratio = 0.33 (about 0.30 expected by chance).


| group   |   sum |   count |      frac |
|:--------|------:|--------:|----------:|
| AD      |   5   |      36 | 0.138889  |
| CN      |   1.2 |      29 | 0.0413793 |
| FTD     |   2.2 |      23 | 0.0956522 |


Spearman rho with MMSE within AD (n=36):


|                         |     0 |
|:------------------------|------:|
| roi__gamma_above_floor  | -0.15 |
| roi__gamma_abs_logpow   | -0.1  |
| roi__relpow_gamma       | -0.21 |
| roi__legacy_std         | -0.03 |
| roi__theta_alpha_ratio  | -0.07 |
| roi__aperiodic_exponent |  0.02 |

