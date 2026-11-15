# Results · H5

## Main results (AUC = mean over 50 repeats of 5-fold CV)

| Model | Features | AUC | Permutation p | AUC change vs spectral baseline |
|---|---|---|---|---|
| M1 ROI average | 1 | 0.549 | 0.21 | −0.014 |
| **M2 posterior electrodes (primary)** | 5 | **0.519** | **0.32** | **−0.073** |
| M3 best k electrodes | 19 | 0.559 | 0.40 | −0.061 |
| M4 regions | 5 | 0.450 | 0.80 | −0.058 |
| M5 multi-metric | 6 | 0.788 | 0.005 | −0.014 |
| M2b auto classifier | 5 | 0.516 | 0.31 | −0.073 |
| M6 electrodes + spectral | 9 | 0.781 | 0.005 | −0.073 |

- **Spectral baseline alone:** AUC 0.796. Adding M2's features gives 0.723 (change −0.073, 95% CI −0.160 to +0.016; gain > 0 in 6% of repeats).
- **MMSE within AD** (spectral base): R² = −0.11 (95% CI −0.25 to −0.04).
- **Ceiling:** M2 AUC 0.53 (0.45–0.61); Riemannian classifier on gamma covariance 0.64 (0.56–0.71).

## Consequences
- Gamma burst-frequency variability alone classifies AD vs CN at chance level (AUC 0.52).
- The models that reach AUC 0.78–0.79 (M5, M6) carry spectral features. Their performance matches the spectral baseline (0.80), and the instability features do not add to it.
- Gamma-band covariance holds more AD-related information (0.64) than the instability features.
