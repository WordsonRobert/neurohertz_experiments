# Results · P10

## Main results

**Bugs found and fixed:**
1. The filter edge mask (0.25 s) was shorter than the 30–48 Hz filter's half-length (0.37 s).
2. An IAF above 12.5 Hz crashed the alpha-harmonic test.
3. The muscle-band filter (53–68 Hz) let 44–48 Hz gamma through.
4. The average reference was off by up to 9 µV after autoreject interpolation.
5. Prediction crashed with zero permutations.
6. A constant column (gamma peak height, always 0) produced p < 0.001 in an exploratory table.

**Method finding.** Matching instability measures on instantaneous SNR left a 17% amplitude-driven difference in a ground-truth test. The spectrum-matched surrogate excess was about 0 for Gaussian signals at any SNR. The excess became the primary instability measure.

**Calibration.** In 120 null simulations, the cluster test's family-wise false-positive rate stayed within the binomial bound of 5%. The t statistic matches statsmodels HC0 to 1e-8.

**Control 1, cloud pilot (28 subjects, IRASA):**
- AD–CN cluster 31–44 Hz, peak O2, p = 0.005;
- FTD–CN cluster 30–45 Hz, peak F3, p = 0.001;
- no aperiodic cluster at 30–48 Hz.

**Control 1, laptop run 1 (88 subjects, IRASA):**
- check 1 passed: 29–47 Hz, peak O1, p = 0.001;
- check 2 passed: 26–47 Hz, peak Fz, p = 0.001;
- **check 3 failed:** aperiodic AD–CN cluster 32–41 Hz at O1/O2, p = 0.049.

**Leak diagnosis, cloud, 28 subjects, ROI 32–41 Hz.** "Leak" is the aperiodic effect as a fraction of the periodic effect.

| Split method | Periodic g | Aperiodic g | Leak |
|---|---|---|---|
| IRASA, h 1.1–1.9 | −4.69 | +1.48 | 0.32 |
| IRASA, h 1.1–2.5 | −5.68 | +3.37 | 0.59 |
| IRASA, h 1.5–2.5 | −5.98 | +3.95 | 0.66 |
| IRASA, h 1.1–1.4 | −2.76 | −2.98 | 1.08 |
| IRASA, h 1.05–1.25 | −1.98 | −5.54 | 2.80 |
| specparam, fixed | −6.05 | +0.63 | 0.10 |
| **specparam, knee** | **−5.48** | **+0.17** | **0.03** |

**Control 1 with specparam-knee, cloud pilot:**
- checks 1 and 2 passed;
- check 3 flagged an aperiodic AD–CN cluster at 2.5–32 Hz (p = 0.05), from the injected beta increase;
- at 35–45 Hz the aperiodic ROI t was 0.57, against periodic t −6.4.

**Control 2, cloud pilot (10/10/8 subjects):**
- FTD–CN: a gamma excess measure was family-wise significant (maxT p = 0.003);
- AD–CN: the top measure was gamma (t = 3.1, p = 0.28);
- no non-gamma measure was significant;
- in-fold selection chose gamma measures in 76–96% of folds.

## Consequences
- The sweep's primary periodic/aperiodic split is specparam-knee; IRASA is kept as a secondary estimate. With IRASA, peaks next to a band leak into its aperiodic estimate.
- Controls 1 (checks 1–2) and 2 must pass in the laptop run before H9's real-data results are produced. Their full-size outcome will be in the run-2 logs, `code/classification_sweep` → `logs/`.
