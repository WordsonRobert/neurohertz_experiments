
# Results · H10 (instability measures: mean of both SNR sub-bins)

Exploratory; ds004504, n = 88 (36 AD, 29 CN, 23 FTD).

## Main results

### A. Coverage and reliability
- **Instability measures, grid A (2–46 Hz):**
    - No cell was measurable in ≥ 80% of subjects.
    - Median coverage per measure: 5–39% (`period_cv` 39%; `if_sd`, `slip_frac` 9%; `pf_sd_epochs` 11%; `burst_f_sd` 14%).
    - `if_sd` coverage by window: 55–57% in the 6–10 and 8–12 Hz windows; 2–28% in the other windows below 30 Hz; 1–3% at 30–46 Hz.
    - Where measurable, the split-half reliability was moderate to high (median SB-ICC: `pf_sd_epochs` 0.80, `if_sd` 0.77, `burst_f_sd` 0.63).
    - Reliable cells (SB-ICC ≥ 0.6 and coverage ≥ 80%): 0 for every instability measure.
- **Instability measures, grid B (54–90 Hz):** median coverage 0–100% depending on the measure. Median SB-ICC −0.30 to 0.17; 0–5 reliable cells per measure.
- **Rhythm presence (`snr_median`):** 330 of 399 cells reliable in grid A (median SB-ICC 0.89); 3 of 323 in grid B.

### B. Cluster tests (Freedman–Lane; significant = p_family < 0.05)
- **Instability, grid A:** no cell reached 80% coverage, so every cell was held at t = 0. No cluster could form, so this grid was not tested.
- **Instability, grid B:** 8 clusters with p_fwer < 0.05 within their own map:
    - FTD–CN at 78–90 Hz, temporal / occipital (T4, T6, O2), FTD higher;
    - AD–FTD at 78–84 Hz, P3.

  None reached p_family < 0.05 (smallest 0.57).
- **Rhythm presence (`snr_median`), age + sex:**

| Cluster | Direction | Electrodes | p_fwer | p_family |
|---|---|---|---|---|
| 4–8 Hz (theta) | AD > CN | all 19, peak T5 | 0.011 | **0.034** |
| 30–44 Hz, peak 34–38 Hz | AD > CN | P3, P4, Pz, T6, peak P3 | 0.030 | 0.090 |
| 8–14 Hz (alpha) | AD < CN | 15 electrodes, peak T3 | 0.040 | 0.119 |
| 16–24 Hz (beta) | AD < CN | 12 electrodes, peak P3 | 0.051 | 0.154 |
| 4–8 Hz (theta) | FTD > CN | 13 electrodes, peak F3 | 0.052 | 0.156 |

- **Posterior 34–38 Hz presence** (AD–CN t by covariate set: age + sex / + theta/alpha / + 1/f):
    - P3: 4.02 / 2.55 / 2.38
    - P4: 2.94 / 1.46 / 1.00
    - Pz: 1.64 / 0.72 / 0.36
    - O1: 1.66 / 0.35 / −0.54
    - O2: 2.03 / 0.51 / −0.15

  No presence cluster reached p_family < 0.05 with slowing in the model.

### C. Reference cells
- **Equivalent to no group difference** in all three contrasts (90% CI of d within ±0.5): 2 cells, both rhythm presence at 14–18 Hz, at P4 (SB-ICC 0.92) and Fp2 (0.81).
- **Looser tier** (reliable, |t| < 1 in all three contrasts): 53 rhythm-presence cells in grid A; 6 instability cells in grid B.

### D. Prediction (one reliable cell selected inside each training fold; baseline slowing + 1/f)
- **Grid A pools:** empty (no reliable instability cell).

| Contrast | Baseline AUC | Grid B cell alone | p | Baseline + cell | Gain (95% CI) |
|---|---|---|---|---|---|
| AD–CN | 0.818 | 0.537 | 0.33 | 0.806 | −0.012 (−0.039 to 0.016) |
| FTD–CN | 0.728 | 0.521 | 0.36 | 0.682 | −0.046 (−0.122 to 0.015) |
| AD–FTD | 0.548 | 0.425 | 0.71 | 0.485 | −0.063 (−0.129 to −0.002) |

## Consequences
- **At one electrode and a 4-Hz window:** in resting ds004504 EEG, the strict SNR-matched instability measures (≥ 4 s in each of two SNR sub-bins) can be estimated in most people only around theta–alpha, and in almost nobody at 30–46 Hz. The screen therefore did not test instability in grid A. H10 is unanswered for 2–46 Hz by this run.
- **Above 54 Hz:** instability measures are measurable but not reliable within a person, and show no group difference after correction.
- **Rhythm presence:**
    - AD has more theta rhythm above the 1/f background at every electrode.
    - It also has more posterior 30–44 Hz rhythm (age + sex), in the same direction and region as H8 (gamma above the floor) and H9 (periodic 30–35 Hz).
    - The posterior 30–44 Hz difference does not survive the correction over maps, and it shrinks when slowing is added (except partly at P3).
- **Reference cells:** 14–18 Hz rhythm presence at P4 and Fp2 is reliable and shows no group difference. It is a candidate reference measure.
- **Next run:** the low-SNR sub-bin (b1) of the same measures is stored for every cell and is measurable in most subjects (on 10 subjects: median coverage 70–100%, 152–342 of 399 grid-A cells at ≥ 80%). The grid-A question is tested with it in `run_freq_instability_b1.sh`.
