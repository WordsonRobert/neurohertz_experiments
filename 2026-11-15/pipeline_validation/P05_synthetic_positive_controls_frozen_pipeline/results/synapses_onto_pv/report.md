# Mechanism report: synthetic / synth-synapses_onto_pv

- Label status: **SYNTHETIC**; fingerprints: **EXPLORATORY**; mechanistic status: **PRIMARY**
- Subjects with a detectable gamma oscillation (presence gate):

| group   |   n_with_gamma |   n |   fraction |
|:--------|---------------:|----:|-----------:|
| AD      |             36 |  36 |          1 |
| CN      |             29 |  29 |          1 |
| FTD     |             23 |  23 |          1 |

## Pre-registered tests (subjects with gamma; Holm across tests)

| id   | name                                    |   n_target |   n_ref |      effect | effect_ci95                                 |          p |     p_holm | equivalent   |
|:-----|:----------------------------------------|-----------:|--------:|------------:|:--------------------------------------------|-----------:|-----------:|:-------------|
| M01  | instability in AD                       |         35 |      28 |  0.180715   | [-0.3066955952799976, 0.6973198916114508]   | 0.477105   | 1          | False        |
| M02  | FTD at frontal electrodes               |         20 |      20 | -0.405709   | [-1.0819700329966748, 0.23103848415532927]  | 0.213357   | 1          | False        |
| M03  | FTD vs AD frontally at matched MMSE     |         20 |      31 | -0.904034   | [-1.437190289838981, -0.2952435090133621]   | 0.00019996 | 0.00319936 | False        |
| M04  | AD effect temporoparietal minus frontal |         31 |      20 | -0.431285   | [-1.023391196923804, 0.17918046362228818]   | 0.133773   | 1          | False        |
| M05  | peak width (damping)                    |         36 |      29 |  0.256859   | [-0.25971019546205043, 0.7648992579835149]  | 0.294341   | 1          | False        |
| M06  | peak frequency                          |         36 |      29 | -0.0307951  | [-0.4917610759123272, 0.4681129993182689]   | 0.903419   | 1          | True         |
| M07  | cycle-scale jitter beyond noise         |         36 |      29 |  0.118624   | [-0.38857178380189444, 0.5909291645982719]  | 0.636273   | 1          | True         |
| M08  | 1-10 s wander beyond noise              |         36 |      29 |  0.145612   | [-0.3721976804615095, 0.6499469944705905]   | 0.568286   | 1          | False        |
| M09  | share of slow wander                    |         36 |      29 |  0.267248   | [-0.23125276294948025, 0.7093468078563825]  | 0.24935    | 1          | False        |
| M10  | phase slips beyond noise                |         36 |      29 |  0.279568   | [-0.22300256438351604, 0.7624488342649363]  | 0.282344   | 1          | False        |
| M11  | slips under load beyond noise           |         36 |      29 | -0.0476605  | [-0.5743361391528571, 0.4370524754016762]   | 0.832034   | 1          | True         |
| M12  | heavy IF tails beyond noise             |         36 |      29 |  0.215105   | [-0.2902705422620702, 0.7083269986267525]   | 0.386923   | 1          | False        |
| M13  | frequency-envelope co-modulation        |         36 |      29 |  0.00919513 | [-0.4993582578897694, 0.48839690920190837]  | 0.970806   | 1          | True         |
| M14  | instability vs MMSE within AD           |         35 |     nan |  0.101688   | [-0.25770440615511947, 0.42417310185557805] | 0.557289   | 1          | False        |
| M15  | instability vs alpha peak within AD     |         35 |     nan | -0.214276   | [-0.5621924782261506, 0.17376762288828035]  | 0.213957   | 1          | False        |
| M16  | AD effect explained by alpha slowing    |         35 |      28 |  0.126405   | [-2.203810476477185, 2.046081545915996]     | 0.417791   | 1          | False        |

## Same tests, ALL subjects (descriptive: includes subjects without a detectable oscillation)

| id   | name                                    |   n_target |   n_ref |      effect | effect_ci95                                 |          p |     p_holm | equivalent   |
|:-----|:----------------------------------------|-----------:|--------:|------------:|:--------------------------------------------|-----------:|-----------:|:-------------|
| M01  | instability in AD                       |         35 |      28 |  0.180715   | [-0.34045933791530514, 0.6705609885402734]  | 0.477105   | 1          | False        |
| M02  | FTD at frontal electrodes               |         20 |      20 | -0.405709   | [-1.0471787484663528, 0.20040518401358512]  | 0.213357   | 1          | False        |
| M03  | FTD vs AD frontally at matched MMSE     |         20 |      31 | -0.904034   | [-1.4490446179751326, -0.3081077374807675]  | 0.00019996 | 0.00319936 | False        |
| M04  | AD effect temporoparietal minus frontal |         31 |      20 | -0.431285   | [-1.0111066046490875, 0.19767619471203673]  | 0.133773   | 1          | False        |
| M05  | peak width (damping)                    |         36 |      29 |  0.256859   | [-0.2840907181552442, 0.748407876493885]    | 0.294341   | 1          | False        |
| M06  | peak frequency                          |         36 |      29 | -0.0307951  | [-0.5060233058664155, 0.4476344243593595]   | 0.903419   | 1          | True         |
| M07  | cycle-scale jitter beyond noise         |         36 |      29 |  0.118624   | [-0.4119239855840363, 0.5899508401705059]   | 0.636273   | 1          | False        |
| M08  | 1-10 s wander beyond noise              |         36 |      29 |  0.145612   | [-0.36629480645029583, 0.6347022724766404]  | 0.568286   | 1          | False        |
| M09  | share of slow wander                    |         36 |      29 |  0.267248   | [-0.2647106193551522, 0.7160420834676094]   | 0.24935    | 1          | False        |
| M10  | phase slips beyond noise                |         36 |      29 |  0.279568   | [-0.24493884789279136, 0.777908568096101]   | 0.282344   | 1          | False        |
| M11  | slips under load beyond noise           |         36 |      29 | -0.0476605  | [-0.5670719309407354, 0.4171113778447194]   | 0.832034   | 1          | True         |
| M12  | heavy IF tails beyond noise             |         36 |      29 |  0.215105   | [-0.2839331201910576, 0.7162913409012516]   | 0.386923   | 1          | False        |
| M13  | frequency-envelope co-modulation        |         36 |      29 |  0.00919513 | [-0.4675688013174722, 0.5299620989852457]   | 0.970806   | 1          | True         |
| M14  | instability vs MMSE within AD           |         35 |     nan |  0.101688   | [-0.25770440615511947, 0.42417310185557805] | 0.557289   | 1          | False        |
| M15  | instability vs alpha peak within AD     |         35 |     nan | -0.214276   | [-0.5621924782261506, 0.17376762288828035]  | 0.213957   | 1          | False        |
| M16  | AD effect explained by alpha slowing    |         35 |      28 |  0.126405   | [-2.048502619220005, 2.0722785707231]       | 0.385807   | 1          | False        |

## Scorecard: verbal predictions

| theory   |   consistent |   inconsistent |   inconclusive |   no_prediction |   not_run |
|:---------|-------------:|---------------:|---------------:|----------------:|----------:|
| T1       |            2 |              3 |             11 |               0 |         0 |
| T2       |            3 |              2 |              9 |               2 |         0 |
| T3       |            2 |              1 |              8 |               5 |         0 |
| T4       |            3 |              1 |             10 |               2 |         0 |
| T5       |            2 |              1 |              8 |               5 |         0 |
| T6       |            3 |              1 |              5 |               7 |         0 |

## Scorecard: model predictions (both simulator families agree)

| theory   |   consistent |   inconsistent |   inconclusive |   no_prediction |
|:---------|-------------:|---------------:|---------------:|----------------:|
| T1       |            2 |              1 |              6 |               7 |
| T2       |            2 |              1 |              2 |              11 |
| T3       |            1 |              0 |              3 |              12 |
| T4       |            2 |              0 |              5 |               9 |
| T5       |            2 |              0 |              4 |              10 |
| T6       |            2 |              0 |              4 |              10 |

## Fingerprint comparison (AD vs CN, adjusted)

- **rate**: local-loop share 0.63 (95% CI 0.00-1.00); best single nav11_pv_output; max-cosine permutation p = 0.644; identifiability within 0.94, cross 0.30
- **cycle**: local-loop share 1.00 (95% CI 0.00-1.00); best single sst_loss; max-cosine permutation p = 0.506; identifiability within 0.65, cross 0.47

**First split claim:** no_claim  (requires agreement of both families, a CI excluding 0.5 and adequate identifiability)

Interpretation rule: a test classed 'consistent' supports a theory only together with the other tests; no single test identifies a mechanism. If mechanistic status is DESCRIPTIVE_ONLY, report all of this as a limitation.