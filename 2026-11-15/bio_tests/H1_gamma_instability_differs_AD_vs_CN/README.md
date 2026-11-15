# H1 · Gamma frequency instability differs between AD and CN (primary hypothesis)

**Hypothesis.** In resting, eyes-closed EEG, the variability of gamma-burst frequencies (`burst_freq_sd`, 30–45 Hz, posterior ROI P3 Pz P4 O1 O2) differs between people with Alzheimer's disease and controls. The biological motivation is PV-interneuron dysfunction in AD, which in animal models destabilises gamma rhythms.
**Type.** Confirmatory: pre-registered and run once after the freeze (`pipeline_validation/P09`). Dataset ds004504 (36 AD, 23 FTD, 29 CN). Pipeline: `combo-csd` (`pipeline_validation/P02`).
**When / where.** 14 Nov 2026, laptop (ledger entry 15:12:22 UTC).

**What was run.**
1. **Group comparison.** For each person: detect 30–45 Hz bursts on each ROI channel (Hilbert transform), take each burst's mean frequency, and compute the SD of those frequencies. Average over the ROI. Compare AD with CN by linear regression, adjusting for age, sex and the 1/f exponent, with robust (HC3) errors. p-value from 10 000 Freedman–Lane permutations; effect size Hedges g with a BCa bootstrap CI.
2. **Pre-specified robustness checks:** add the EMG index; add clean seconds; each scalp region separately.
3. **Electrode map:** an AD–CN t value per electrode, with maxT family-wise correction.
4. **Exploratory table:** every other feature AD vs CN, adjusted for the exponent, with FDR q-values. Labelled exploratory.

**Command.** `python scripts/04_discovery_analysis.py --dataset ds004504`
**Code.** `../../code/neurohertz_v2_frozen/scripts/04_discovery_analysis.py`, `../../code/neurohertz_v2_frozen/nh/stats.py` (`group_effect`, `maxT_channels`), `../../code/neurohertz_v2_frozen/nh/gamma.py` (`burst_freq_sd`)

| Output in `results/` | Content |
|---|---|
| `H1_result.json` | H1 effect, CI, t, parametric and permutation p, Hedges g, covariates |
| `robustness_checks.json` | The same test with extra covariates and per region |
| `topography_AD_vs_CN.csv` | Per-electrode t and maxT-corrected p |
| `exploratory_all_features_AD_vs_CN.csv` | Every feature, AD vs CN (exploratory, FDR) |
| `discovery_results_FULL.json` | The complete output of the discovery script (H1–H4, robustness, topography, exploratory) |
