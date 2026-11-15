# Biological hypothesis tests

Each folder is one hypothesis about Alzheimer's disease. All use ds004504 (36 AD, 23 FTD, 29 CN).

- **H1–H6 are confirmatory.** They were pre-specified in `code/neurohertz_v2_frozen/docs/ANALYSIS_PLAN.md` and run once, after the freeze (`pipeline_validation/P09`). H2–H4 and H6 were *gated*: they count as confirmatory only if an earlier gate passed. Otherwise they are reported as descriptive.
- **H7–H9 are exploratory.** They were run after the labels had been opened, and they generate hypotheses for a new cohort.

| Folder | Hypothesis | Kind |
|---|---|---|
| `H1_gamma_instability_differs_AD_vs_CN` | Gamma burst-frequency variability differs between AD and CN (primary) | Confirmatory |
| `H2_gamma_instability_tracks_MMSE_within_AD` | It correlates with MMSE within AD | Confirmatory, gated |
| `H3_gamma_instability_beyond_spectral_nuisance` | The AD–CN difference survives spectral and nuisance covariates | Confirmatory, gated |
| `H4_gamma_instability_AD_vs_FTD` | It separates AD from FTD | Confirmatory, gated |
| `H5_gamma_instability_classifies_AD` | It classifies AD vs CN in cross-validation | Confirmatory |
| `H6_mechanism_behind_a_gamma_change` | One of six circuit mechanisms explains the gamma pattern | Confirmatory, gated (descriptive) |
| `H7_old_73pct_accuracy_reproduces` | The v1 pipeline's 73.8% accuracy reproduces with clean preprocessing | Exploratory |
| `H8_30_45Hz_power_and_alternative_explanations` | 30–45 Hz power differs in AD beyond muscle, 1/f, slowing and harmonics | Exploratory |
| `H9_instability_in_any_band_and_elimination_sweep` | Instability in any band separates AD beyond slowing and 1/f | Exploratory |
