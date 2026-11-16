# H10 · Instability of any frequency window at any electrode separates AD, beyond slowing and 1/f

**Hypotheses.** Both are answered from the same run.
1. **Separating:** the instability of at least one 4-Hz frequency window, at some electrodes, differs between AD and CN (or FTD), and the difference remains after adjusting for slowing (theta/alpha) and the 1/f slope.
2. **Reference:** some frequency × electrode cells are reliable within a person and show no difference between groups. These can serve as reference or negative-control measures for later analyses.

**Type.** Exploratory (ds004504 labels were opened on 14 Nov 2026). Any separating cell is a candidate to freeze and test in a new cohort.
**Relation to H9.** H9 measured instability in 6 fixed bands and averaged over electrodes. H10 uses 38 windows (2–46 Hz and 54–90 Hz) at each of the 19 electrodes.
**When / where.** Laptop, 16 Nov 2026: stage 13, 04:08–11:41 (453 min, 8 cores); stage 57, 11:41–11:56. The synthetic control (P11, run 2) passed first.

**What the run does** (`../../code/classification_sweep/run_freq_instability.sh`, steps `f10`–`f11`).
- **Stage 13** (no labels): the five SNR-matched instability measures and rhythm presence, in every window at every electrode, raw and beyond the spectrum (10 surrogates), on all data and on each half.
- **Stage 57:**
    - **A.** Per-cell reliability.
    - **B.** Freedman–Lane cluster permutation over window × electrode (5000 permutations) for AD–CN, FTD–CN and AD–FTD under three covariate sets: L0 age + sex; L1 + theta/alpha; L2 + 1/f slope. Significant = p_family < 0.05 (30 maps per grid and covariate set).
    - **C.** Reference cells: reliable, with the 90% CI of the group difference d within ±0.5 in all three contrasts; a looser tier requires |t| < 1.
    - **D.** Nested-CV prediction, one reliable cell selected inside each training fold, added to slowing + 1/f; whole-pipeline permutation.

| Output in `results/` | Content |
|---|---|
| `sub_bin_mean/REPORT_FREQ_INSTABILITY.md` | Report (sections A–D) |
| `sub_bin_mean/A_reliability_cells.csv`, `A_reliability_summary.csv` | Coverage and split-half reliability of every cell |
| `sub_bin_mean/B_clusters.csv` | Every cluster: p within its map (`p_fwer`) and over maps (`p_family`) |
| `sub_bin_mean/B_cells.csv` | t and standardized difference d (90% CI) for every cell, contrast and covariate set |
| `sub_bin_mean/C_reference_cells.csv` | Reliable cells with their largest group difference |
| `sub_bin_mean/D_prediction.csv` | Nested-CV prediction |
| `logs/` | Logs of stages 13 and 57 |

`sub_bin_mean` = instability measures averaged over both SNR sub-bins (the default of stage 57). The t-map figures (`maps/`) stay on the laptop under `classification/results/ds004504/main/freqinst/maps/`.

**Follow-up defined after this run.** `run_freq_instability_b1.sh` repeats stages 57 and the synthetic check using only the low-SNR sub-bin (b1). Stage 13 already computed b1 for every cell, so no new feature extraction is needed. Its results go in `results/sub_bin_b1/`.
