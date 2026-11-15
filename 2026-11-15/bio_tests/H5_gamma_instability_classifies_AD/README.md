# H5 · Gamma instability classifies AD vs CN

**Hypothesis.** A classifier using gamma burst-frequency variability separates AD from CN in held-out subjects. The primary model is M2: `burst_freq_sd` at the five posterior electrodes.
**Type.** Confirmatory prediction (pre-specified models), ds004504 AD vs CN (36 vs 29).
**When / where.** 14 Nov 2026, laptop (ledger 15:14:50 UTC); ceiling check 16:36:07 UTC.

**What was run.**
- **Models.** Seven pre-specified models, all with nested cross-validation (outer 5-fold × 50 repeats; inner fold chooses classifier and regularisation; scaling inside folds):
    - M1: ROI average;
    - **M2: posterior electrodes (primary)**;
    - M3: best k electrodes (k chosen inside folds);
    - M4: regions;
    - M5: multi-metric (instability + gamma above floor + exponent + alpha peak + theta/alpha + EMG);
    - M2b: M2 with automatic classifier choice;
    - M6: electrodes plus spectral features.
- **Significance.** A permutation test of the whole pipeline (1000 permutations for M2, 200 for others).
- **Incremental value.** Gain over a spectral baseline: age, sex, theta/alpha, alpha peak, exponent, gamma above floor, gamma relative power.
- **MMSE within AD.** Regression of MMSE on the features, within AD.
- **Ceiling check.** The M2 features against a Riemannian classifier on gamma-band covariance (TabPFN was not installed).
- The frozen M2 model was saved.

**Commands.** `python scripts/05_prediction.py --dataset ds004504 --jobs 8`; `python scripts/09_ceiling_check.py --dataset ds004504`
**Code.** `../../code/neurohertz_v2_frozen/scripts/05_prediction.py`, `09_ceiling_check.py`, `../../code/neurohertz_v2_frozen/nh/predict.py`

| Output in `results/` | Content |
|---|---|
| `prediction_summary.csv` | Per model: features, AUC, permutation p, AUC change vs baseline |
| `prediction_results.json` | Full output: per-repeat AUCs, DeLong CIs, selection frequencies, coefficients, incremental and MMSE analyses |
| `ceiling_check.json`, `09_ceiling.log` | Interpretable model vs Riemannian ceiling |
| `frozen_model_M2_posterior_electrodes.joblib` | The final fitted M2 model (scikit-learn) |
