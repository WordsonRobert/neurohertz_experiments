# H3 · Any AD–CN difference in gamma instability survives spectral and nuisance covariates

**Hypothesis.** An AD–CN difference in `burst_freq_sd` remains after adjusting for the quantities that change instability estimates without being instability: gamma power above background, the background floor, gamma envelope amplitude, burst rate, alpha peak frequency and muscle (EMG).
**Type.** Confirmatory: pre-registered and run once after the freeze (`pipeline_validation/P09`). Dataset ds004504 (36 AD, 23 FTD, 29 CN). Pipeline: `combo-csd` (`pipeline_validation/P02`). **Gated on H1** (descriptive).
**What was run.** The H1 regression with nine covariates: age, sex, aperiodic exponent, `gamma_above_floor`, `floor_log10`, `env_mean`, `burst_rate`, `alpha_peak_freq`, EMG log-power. Plus a logistic likelihood-ratio test of whether `burst_freq_sd` adds to a model of the six nuisance terms.
**Command / code.** Part of `04_discovery_analysis.py`.

| Output in `results/` | Content |
|---|---|
| `H3_result.json` | Adjusted β, CI, t, permutation p, covariates, logistic LR test |
