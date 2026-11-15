# H4 · Gamma instability separates AD from FTD

**Hypothesis.** `burst_freq_sd` differs between AD and FTD, which would make it specific to AD rather than to dementia in general. FTD vs CN is tested alongside.
**Type.** Confirmatory: pre-registered and run once after the freeze (`pipeline_validation/P09`). Dataset ds004504 (36 AD, 23 FTD, 29 CN). Pipeline: `combo-csd` (`pipeline_validation/P02`). **Gated on H1** (descriptive).
**What was run.** The H1 regression (age, sex, exponent) for AD vs FTD and for FTD vs CN; permutation p's; Holm correction over the two contrasts.
**Command / code.** Part of `04_discovery_analysis.py`.

| Output in `results/` | Content |
|---|---|
| `H4_result.json` | Both contrasts: means, adjusted β, CI, permutation p, Holm p, Hedges g |
