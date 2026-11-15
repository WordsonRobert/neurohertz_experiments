# H2 · Gamma instability tracks cognitive severity (MMSE) within AD

**Hypothesis.** Within the AD group, `burst_freq_sd` correlates with MMSE.
**Type.** Confirmatory: pre-registered and run once after the freeze (`pipeline_validation/P09`). Dataset ds004504 (36 AD, 23 FTD, 29 CN). Pipeline: `combo-csd` (`pipeline_validation/P02`). **Gated on H1.** H1 was not significant, so this result is descriptive (`tested_confirmatory: false`).
**What was run.** A partial Spearman correlation between `burst_freq_sd` and MMSE in the 36 AD patients, adjusted for age, sex and the 1/f exponent. Permutation p (10 000); bootstrap CIs.
**Command / code.** Part of `python scripts/04_discovery_analysis.py --dataset ds004504`; `../../code/neurohertz_v2_frozen/nh/stats.py` (`partial_spearman`).

| Output in `results/` | Content |
|---|---|
| `H2_result.json` | n, partial rho, 95% and 90% CI, permutation p, covariates |
