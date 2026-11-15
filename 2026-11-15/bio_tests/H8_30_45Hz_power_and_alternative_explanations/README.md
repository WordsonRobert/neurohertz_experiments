# H8 · 30–45 Hz power differs in AD beyond muscle, 1/f slope, slowing and alpha harmonics

**Hypothesis.** The level of 30–45 Hz activity (not its instability) differs in AD, and the difference is not explained by muscle (EMG), the 1/f background, EEG slowing or harmonics of alpha.
**Type.** Exploratory: run after the labels were opened (15 Nov 2026). It generates hypotheses for a new cohort.
**What was run** (existing final-run features; no new signal processing):
- **B.** AD vs CN and FTD vs CN for 12 measures of 30–45 Hz power, plus EMG, the 1/f exponent and `legacy_std`. Freedman–Lane permutation p (2000) under six covariate sets: none; age+sex; +exponent; +EMG; +theta/alpha; +all three.
- **C.** Hedges g per scalp region and CSD ROI, for power measures, EMG, exponent, theta/alpha and envelope.
- **D.** Within-group Spearman coupling of 30–45 Hz measures with EMG, the 30–90 Hz slope and the exponent.
- **E.** Whether the fitted 30–45 Hz peak frequency is an integer multiple of the alpha peak frequency; presence by group; correlations with MMSE within AD.

**Command.** `python explore/01_existing_features.py` (sections B–E) in `../../code/classification_sweep/`

| Output in `results/` | Content |
|---|---|
| `B_gamma_eliminations.csv` | Every measure × contrast × covariate set: g, t, p |
| `C_topography_g.csv` | Hedges g per region |
| `D_within_group_coupling.csv` | Within-group correlations with EMG, HF slope, exponent |
| `E_harmonic.json` | Alpha-harmonic test |
| `report.md` | All sections as tables (also includes H7's table) |
