# Mechanism report: synthetic / synth-erratic_drive

- Label status: **SYNTHETIC**; fingerprints: **EXPLORATORY**; mechanistic status: **PRIMARY**
- Subjects with a detectable gamma oscillation (presence gate):

| group   |   n_with_gamma |   n |   fraction |
|:--------|---------------:|----:|-----------:|
| AD      |             36 |  36 |          1 |
| CN      |             29 |  29 |          1 |
| FTD     |             23 |  23 |          1 |

## Pre-registered tests (subjects with gamma; Holm across tests)

| id   | name                                    |   n_target |   n_ref |     effect | effect_ci95                                 |          p |     p_holm | equivalent   |
|:-----|:----------------------------------------|-----------:|--------:|-----------:|:--------------------------------------------|-----------:|-----------:|:-------------|
| M01  | instability in AD                       |         36 |      29 |  0.268698  | [-0.25212369979502636, 0.7538603859007741]  | 0.25015    | 1          | False        |
| M02  | FTD at frontal electrodes               |         21 |      22 |  0.22682   | [-0.39154163960012, 0.8388866511169638]     | 0.460508   | 1          | False        |
| M03  | FTD vs AD frontally at matched MMSE     |         21 |      29 | -0.162698  | [-0.6992073963669293, 0.3947561686440576]   | 0.516897   | 1          | False        |
| M04  | AD effect temporoparietal minus frontal |         29 |      22 | -0.159562  | [-0.6963673248847017, 0.4230404396868299]   | 0.59988    | 1          | False        |
| M05  | peak width (damping)                    |         36 |      29 |  0.241052  | [-0.2702873917221956, 0.7574733032038918]   | 0.326335   | 1          | False        |
| M06  | peak frequency                          |         36 |      29 |  0.429771  | [-0.0815101445879611, 0.9024480101732191]   | 0.0637872  | 0.70166    | False        |
| M07  | cycle-scale jitter beyond noise         |         36 |      29 |  0.977894  | [0.4342960688075077, 1.4299251362750922]    | 0.00039992 | 0.0059988  | False        |
| M08  | 1-10 s wander beyond noise              |         36 |      29 |  1.15407   | [0.7184181228947384, 1.5339547418455293]    | 0.00019996 | 0.00319936 | False        |
| M09  | share of slow wander                    |         36 |      29 |  0.449319  | [0.038340766016710645, 0.834019346082098]   | 0.0157968  | 0.194961   | False        |
| M10  | phase slips beyond noise                |         36 |      29 |  0.651889  | [0.14974820337240555, 1.1923413257548896]   | 0.00659868 | 0.0923815  | False        |
| M11  | slips under load beyond noise           |         36 |      29 |  0.189272  | [-0.31446822853763884, 0.67803090498377]    | 0.426315   | 1          | False        |
| M12  | heavy IF tails beyond noise             |         36 |      29 |  0.559219  | [0.08200594249777711, 1.002436433162541]    | 0.014997   | 0.194961   | False        |
| M13  | frequency-envelope co-modulation        |         36 |      29 |  0.150024  | [-0.3471913110124734, 0.5897440765723699]   | 0.489502   | 1          | False        |
| M14  | instability vs MMSE within AD           |         36 |     nan |  0.0625201 | [-0.30640223085614776, 0.40928310125658823] | 0.716857   | 1          | False        |
| M15  | instability vs alpha peak within AD     |         36 |     nan | -0.124064  | [-0.4666311126732099, 0.23582048994907945]  | 0.466907   | 1          | False        |
| M16  | AD effect explained by alpha slowing    |         36 |      29 |  0.0895871 | [-1.001978023133097, 1.4108841285480287]    | 0.341329   | 1          | False        |

## Same tests, ALL subjects (descriptive: includes subjects without a detectable oscillation)

| id   | name                                    |   n_target |   n_ref |     effect | effect_ci95                                 |          p |     p_holm | equivalent   |
|:-----|:----------------------------------------|-----------:|--------:|-----------:|:--------------------------------------------|-----------:|-----------:|:-------------|
| M01  | instability in AD                       |         36 |      29 |  0.268698  | [-0.252825263488888, 0.8136444809682126]    | 0.25015    | 1          | False        |
| M02  | FTD at frontal electrodes               |         21 |      22 |  0.22682   | [-0.36111939642052143, 0.8007740260630092]  | 0.460508   | 1          | False        |
| M03  | FTD vs AD frontally at matched MMSE     |         21 |      29 | -0.162698  | [-0.7288985483483726, 0.37758268627512825]  | 0.516897   | 1          | False        |
| M04  | AD effect temporoparietal minus frontal |         29 |      22 | -0.159562  | [-0.7691070812571882, 0.3912844239620603]   | 0.59988    | 1          | False        |
| M05  | peak width (damping)                    |         36 |      29 |  0.241052  | [-0.2797588839043214, 0.7474006861244161]   | 0.326335   | 1          | False        |
| M06  | peak frequency                          |         36 |      29 |  0.429771  | [-0.0675444318167294, 0.9422129474222856]   | 0.0637872  | 0.70166    | False        |
| M07  | cycle-scale jitter beyond noise         |         36 |      29 |  0.977894  | [0.48648218462974635, 1.4940325136814825]   | 0.00039992 | 0.0059988  | False        |
| M08  | 1-10 s wander beyond noise              |         36 |      29 |  1.15407   | [0.7626795409792665, 1.5509019341497097]    | 0.00019996 | 0.00319936 | False        |
| M09  | share of slow wander                    |         36 |      29 |  0.449319  | [-0.009325682662363291, 0.7986976297104853] | 0.0157968  | 0.194961   | False        |
| M10  | phase slips beyond noise                |         36 |      29 |  0.651889  | [0.11533156765620188, 1.1735141981818682]   | 0.00659868 | 0.0923815  | False        |
| M11  | slips under load beyond noise           |         36 |      29 |  0.189272  | [-0.3210541567825253, 0.6433990030348606]   | 0.426315   | 1          | False        |
| M12  | heavy IF tails beyond noise             |         36 |      29 |  0.559219  | [0.10210809156594781, 0.9892925761071238]   | 0.014997   | 0.194961   | False        |
| M13  | frequency-envelope co-modulation        |         36 |      29 |  0.150024  | [-0.33186568312012404, 0.6279639671201481]  | 0.489502   | 1          | False        |
| M14  | instability vs MMSE within AD           |         36 |     nan |  0.0625201 | [-0.30640223085614776, 0.40928310125658823] | 0.716857   | 1          | False        |
| M15  | instability vs alpha peak within AD     |         36 |     nan | -0.124064  | [-0.4666311126732099, 0.23582048994907945]  | 0.466907   | 1          | False        |
| M16  | AD effect explained by alpha slowing    |         36 |      29 |  0.0895871 | [-0.8245974851971415, 1.5054662128033265]   | 0.332834   | 1          | False        |

## Scorecard: verbal predictions

| theory   |   consistent |   inconsistent |   inconclusive |   no_prediction |   not_run |
|:---------|-------------:|---------------:|---------------:|----------------:|----------:|
| T1       |            1 |              1 |             14 |               0 |         0 |
| T2       |            1 |              1 |             12 |               2 |         0 |
| T3       |            1 |              1 |              9 |               5 |         0 |
| T4       |            1 |              1 |             12 |               2 |         0 |
| T5       |            1 |              1 |              9 |               5 |         0 |
| T6       |            0 |              1 |              8 |               7 |         0 |

## Scorecard: model predictions (both simulator families agree)

| theory   |   consistent |   inconsistent |   inconclusive |   no_prediction |
|:---------|-------------:|---------------:|---------------:|----------------:|
| T1       |            0 |              2 |              7 |               7 |
| T2       |            0 |              1 |              4 |              11 |
| T3       |            1 |              0 |              3 |              12 |
| T4       |            0 |              2 |              5 |               9 |
| T5       |            0 |              2 |              4 |              10 |
| T6       |            0 |              2 |              4 |              10 |

## Fingerprint comparison (AD vs CN, adjusted)

- **rate**: local-loop share 0.24 (95% CI 0.00-0.39); best single erratic_drive; max-cosine permutation p = 0.429; identifiability within 0.94, cross 0.30
- **cycle**: local-loop share 0.63 (95% CI 0.00-1.00); best single sst_loss; max-cosine permutation p = 0.220; identifiability within 0.65, cross 0.47

**First split claim:** no_claim  (requires agreement of both families, a CI excluding 0.5 and adequate identifiability)

Interpretation rule: a test classed 'consistent' supports a theory only together with the other tests; no single test identifies a mechanism. If mechanistic status is DESCRIPTIVE_ONLY, report all of this as a limitation.