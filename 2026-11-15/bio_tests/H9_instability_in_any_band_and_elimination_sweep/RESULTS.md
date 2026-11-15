
# Results · H9

All results are exploratory (ds004504, n = 88: 36 AD, 29 CN, 23 FTD). Both synthetic positive controls passed first (P10).

## Main results

### 1. Instability in every band (stage 55)
- **Reliability gate:**
    - 68 of 408 measures passed (split-half SB-ICC ≥ 0.6, coverage ≥ 80%): 37 raw instability, 9 beyond-spectrum (`__excess`), 22 rhythm-presence (SNR).
    - Most raw alpha instability measures are 80–92% predicted by their spectrum-matched surrogates (R² 0.80–0.92). For gamma measures it is 3–37%.
- **Family-wise group tests (maxT), covariate ladder:**
    - L0: age + sex
    - L1: + slowing (theta/alpha)
    - L2: + 1/f slope
    - L3: + the band's own rhythm presence

| Family | Contrast | Smallest p_maxT at L0 | L1 | L2 | L3 |
|---|---|---|---|---|---|
| raw instability | AD–CN | 0.004 | 0.15 | 0.23 | 0.23 |
| raw instability | FTD–CN | 0.09 | 0.90 | 0.94 | 0.91 |
| raw instability | AD–FTD | 0.18 | 0.42 | 0.45 | 0.48 |
| beyond spectrum (excess) | AD–CN | 0.27 | 0.26 | 0.24 | 0.29 |
| beyond spectrum (excess) | FTD–CN | 0.57 | 0.71 | 0.82 | 0.95 |
| beyond spectrum (excess) | AD–FTD | 0.68 | 0.75 | 0.77 | 0.79 |
| rhythm presence (SNR) | AD–CN | <0.001 | 0.21 | 0.22 | — |
| rhythm presence (SNR) | FTD–CN | 0.019 | 0.021 | 0.042 | — |

- **Instability measures significant at any level:**
    - Only alpha epoch-to-epoch peak-frequency SD, AD > CN, at L0: global t = 4.15, p = 0.0045; ROI t = 3.56, p = 0.028.
    - With slowing added (L1): t = 1.63, p = 0.97; at L2, p = 0.93; at L3, p = 0.81.
- **Rhythm presence:**
    - At L0, AD has higher theta SNR and lower alpha SNR than CN (p ≤ 0.003).
    - FTD has lower delta SNR than CN at L0, L1 and L2 (p = 0.020, 0.021, 0.042).
- **Time-on-task drift (AD vs CN):** no measure with maxT p < 0.1.
- **Severity (MMSE) within AD:** no measure with q < 0.1.
- **Prediction** (nested CV, measures selected inside the folds, whole-pipeline permutation). The baseline is slowing + 1/f.

| Contrast | Baseline AUC | Instability alone: all / excess / raw | Baseline + instability | Gain (95% CI) |
|---|---|---|---|---|
| AD–CN | 0.818 | 0.711 (p 0.01) / 0.479 / 0.674 | 0.801 | −0.017 (−0.047 to 0.017) |
| FTD–CN | 0.728 | 0.667 (p 0.05) / 0.475 / 0.500 | 0.714 | −0.014 (−0.055 to 0.023) |
| AD–FTD | 0.548 | 0.592 (p 0.18) / 0.616 / 0.665 (p 0.095) | 0.585 | 0.036 (−0.067 to 0.111) |

  In AD–CN, the measures selected most often were theta and alpha rhythm-presence measures (87% of folds).

### 2. Frequency × electrode spectra (stage 20; FWER-significant clusters, age + sex)

| Spectrum | Contrast | Clusters |
|---|---|---|
| periodic (specparam-knee, CSD) | AD–CN | 4–7.5 Hz AD > CN (p < 0.001, all electrodes); 9–11.5 Hz AD < CN (p 0.011); 16–22.5 Hz AD < CN (p 0.004); **30–35 Hz AD > CN (p 0.031, peak C4 33 Hz)** |
| periodic, + EMG covariate | AD–CN | the same four; 30–35 Hz p = 0.036 |
| periodic, average reference | AD–CN | 3.5–7.5 Hz AD > CN; 9–11.5 and 15–21.5 Hz AD < CN; 30–43.5 Hz AD > CN (p 0.002, peak Fp2) |
| periodic | AD–FTD | 4–5.5 Hz AD > FTD (p 0.028) |
| aperiodic (specparam-knee, CSD) | all | no significant cluster at any frequency |
| raw log power, CSD | AD–CN | 16–23 Hz AD < CN (p 0.044); no cluster at 30–48 Hz |
| raw log power, lowest-EMG 25% / 50% epochs | AD–CN | 15.5–24 Hz AD < CN; no cluster at 30–48 Hz |
| without BSS-CCA muscle removal, periodic | AD–CN | 3.5–7.5 Hz AD > CN; 9–12 and 15.5–21 Hz AD < CN; 30.5–40.5 Hz AD > CN (p 0.0025, peak T4 33 Hz) |

Vigilance strata (low → high alpha/theta), 35–45 Hz AD–CN: t = 0.16, −0.42, −0.94, −0.21; all p ≥ 0.39.

### 3. Elimination table (verdict rules fixed before any real-data result)

| Explanation | Verdict | Evidence |
|---|---|---|
| E0 effect at 35–45 Hz | PRESENT | one periodic cluster touching 35 Hz (30–35 Hz); no raw-power cluster |
| E1 muscle | not eliminated | ROI 35–45 Hz t: all epochs −0.23; lowest-EMG 25% −0.32; +EMG covariate 0.02; no BSS-CCA 0.20 |
| E2 ocular / frontal-polar | eliminated | frontal-polar burst excess t = 1.24, p = 0.25 |
| E3 aperiodic | no aperiodic cluster | periodic ROI 35–45 Hz t = 1.05 |
| E4 vigilance | not eliminated | per-stratum t: 0.16, −0.42, −0.94, −0.21 |
| E5 alpha harmonics | eliminated | 1:4 locking t = 0.06, p = 0.96 |
| E6 sharp transients | eliminated | transient rate t = 0.03, p = 0.98; gamma without transient epochs t = 0.41, p = 0.69 |
| E7 notch / filter edge | not suspected | cluster at 30–35 Hz |
| E8 medication | untestable | beta cluster 16–23 Hz, AD < CN, posterior |

### 4. Subject-level measures (Freedman–Lane, age + sex, 5000 permutations; p values)

| Measure | AD–CN | FTD–CN | AD–FTD |
|---|---|---|---|
| theta/alpha | 0.0002 | 0.0016 | 0.068 |
| aperiodic exponent (specparam-knee) | 0.0004 | 0.018 | 0.31 |
| aperiodic knee | 0.026 | 0.018 | 0.97 |
| individual alpha frequency | 0.036 | 0.85 | 0.060 |
| periodic 35–45 Hz (specparam-knee) | 0.12 | 0.96 | 0.36 |
| periodic 30–48 Hz (specparam-knee) | 0.032 | 0.90 | 0.23 |
| periodic 35–45 Hz (IRASA) | 0.0014 | 0.15 | 0.41 |
| raw 35–45 Hz power | 0.79 | 0.16 | 0.38 |
| muscle (53–68 Hz) | 0.76 | 0.16 | 0.39 |
| theta–gamma / alpha–gamma PAC | 0.91 / 0.56 | 0.52 / 0.35 | 0.46 / 0.86 |

### 5. Burst types (stage 30)
- **Typing:** 7 types at both thresholds; stability ARI 0.38 (p95) and 0.26 (p99).
- **Group tests:** no burst-type measure reached Holm p < 0.05 (smallest Holm p 0.15, share of type 1, AD > CN).

### 6. Stratification with diagnosis hidden (stage 40)
- **Clusters:** K = 2, silhouette 0.14, stability ARI 0.43 ± 0.31.
- **Composition:** cluster 0 has 15 AD and 17 FTD; cluster 1 has 21 AD and 6 FTD (χ² p = 0.031).
- **MMSE:** median 20 in both clusters (p = 0.44).

### 7. Prediction by mechanism family (stage 50, nested CV; AD–CN AUC)

| Model | AUC | Gain over slowing + 1/f |
|---|---|---|
| slowing | 0.821 | — |
| aperiodic | 0.774 | — |
| gamma periodic | 0.655 (p 0.035) | — |
| bursts | 0.632 (p 0.065) | — |
| muscle | 0.547 | — |
| slowing + aperiodic (base) | 0.824 | — |
| base + gamma periodic | 0.800 | −0.024 (−0.065 to 0.011) |
| base + bursts | 0.799 | −0.026 (−0.106 to 0.035) |
| all 20 features | 0.757 | −0.067 (−0.168 to 0.003) |

FTD–CN base AUC 0.653; AD–FTD base AUC 0.572. No family added AUC over the base in either contrast.

## Consequences
- In ds004504, no frequency-instability measure in any band separates AD from CN, or from FTD, once slowing (theta/alpha) is accounted for. The single family-wise difference, alpha peak-frequency SD across epochs, does not remain after adjusting for theta/alpha.
- Instability beyond what the spectrum predicts (surrogate excess) shows no group difference in any band, contrast or covariate set.
- Instability measures do not add classification performance to slowing + 1/f, for AD–CN or FTD–CN.
- The AD–CN differences in these data are spectral:
    - more periodic theta;
    - less periodic alpha and beta;
    - a steeper aperiodic slope at subject level;
    - a periodic AD > CN increase at about 30–35 Hz.

  Muscle and vigilance were not eliminated as explanations of that 30–35 Hz increase by the pre-fixed rules. Raw 30–48 Hz power shows no group difference.
- Under the sweep's own criterion, a candidate for a frozen hypothesis in a new cohort comes from these spectral measures, not from instability.
