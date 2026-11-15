# H10 · Instability of any frequency window at any electrode separates AD, beyond slowing and 1/f

**Hypotheses.** Both are answered from the same run.
1. **Separating:** the instability of at least one 4-Hz frequency window, at some electrodes, differs between AD and CN (or FTD), and the difference remains after adjusting for slowing (theta/alpha) and the 1/f slope.
2. **Reference:** some frequency × electrode cells are reliable within a person and show no difference between groups. These can serve as reference or negative-control measures for later analyses.

**Type.** Exploratory (ds004504 labels were opened on 14 Nov 2026). Any separating cell is a candidate to freeze and test in a new cohort.
**Relation to H9.** H9 measured instability in 6 fixed bands and averaged over electrodes. H10 uses 38 windows (2–46 Hz and 54–90 Hz) at each of the 19 electrodes.
**Status at this snapshot.** Not yet run on real data. The synthetic control (P11) must pass first.

**What the run does** (`../../code/classification_sweep/run_freq_instability.sh`, steps `f10`–`f11`).
- **Stage 13** (no labels): the five SNR-matched instability measures and rhythm presence, in every window at every electrode, raw and beyond the spectrum (10 surrogates), on all data and on each half.
- **Stage 57:**
    - **A.** Per-cell reliability.
    - **B.** Freedman–Lane cluster permutation over window × electrode (5000 permutations) for AD–CN, FTD–CN and AD–FTD under three covariate sets: L0 age + sex; L1 + theta/alpha; L2 + 1/f slope. Significant = p_family < 0.05 (30 maps per grid and covariate set).
    - **C.** Reference cells: reliable, with the 90% CI of the group difference d within ±0.5 in all three contrasts; a looser tier requires |t| < 1.
    - **D.** Nested-CV prediction, one reliable cell selected inside each training fold, added to slowing + 1/f; whole-pipeline permutation.

**Expected outputs** (written to `classification/results/ds004504/main/freqinst/`; to be copied into `results/`):
- `REPORT_FREQ_INSTABILITY.md`
- `A_reliability_cells.csv`, `A_reliability_summary.csv`
- `B_clusters.csv`, `B_cells.csv`, `maps/`
- `C_reference_cells.csv`
- `D_prediction.csv`
