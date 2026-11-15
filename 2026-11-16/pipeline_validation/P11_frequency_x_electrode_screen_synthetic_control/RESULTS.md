# Results · P11

## Main results

**Unit tests.** 12 passed.

**Run 1** (88 subjects, 4 surrogates, 1000 permutations per map; each cluster's p controlled within its own map):

| Check | Result |
|---|---|
| 1. Injected gamma instability found | PASS. Example clusters: `if_sd__excess`, AD–CN, 32–42 Hz, peak Pz, p = 0.001; `if_sd__excess`, FTD–CN, 34–40 Hz, peak Fp1, p = 0.012; `period_cv`, FTD–CN, 34–38 Hz, peak Fp1, p = 0.006 |
| 2. Nothing below 24 Hz | PASS. Smallest p for a cluster below 24 Hz: 0.17 |
| 3. Nothing in grid B | **FAIL.** One cluster: `slip_frac`, FTD–CN, 84–88 Hz, peak T3, FTD lower, 2 cells, p = 0.016 |

- **Uncorrected significant clusters (p < 0.05 within their own map), age + sex:** 19 in grid A (all at 30–42 Hz) and 1 in grid B.
- **Number of tests behind those counts:** each grid and covariate set holds 30 maps (10 measures × 3 contrasts), each controlled at 5% only within itself.
    - Under the null, about 1.5 significant clusters are expected per 30 maps.
    - At least one is expected with probability about 0.79.
    - In grid B, where nothing was injected, 1 of 30 maps gave a cluster with p < 0.05.

**Correction applied.** A cluster is called significant if p_family = min(1, 30 × p_fwer) < 0.05 (Bonferroni over the maps of a grid and covariate set).
- It was added to stage 57 and the check on 16 Nov 2026, after run 1 and before any real-data run.
- The three criteria are unchanged.
- Run-1 clusters under the correction (age + sex):

| Cluster | p_fwer | p_family |
|---|---|---|
| `if_sd__excess`, AD–CN, 32–42 Hz, peak Pz, AD higher | 0.001 | 0.030 |
| `period_cv__excess`, AD–FTD, 34–38 Hz, peak P3, AD higher | 0.001 | 0.030 |
| `period_cv__excess`, AD–FTD, 34–38 Hz, peak Fz, FTD higher | 0.001 | 0.030 |

Every other cluster has p_family ≥ 0.18, including the grid B cluster (p_family 0.48) and the FTD–CN frontal clusters (smallest p_family 0.18). Applied to run 1, the corrected check gives PASS on all three criteria.

**Reliability (synthetic, 4 surrogates).**
- Raw measures in grid A: 1–40 reliable cells per measure (SB-ICC ≥ 0.6, coverage ≥ 80%).
- Beyond-spectrum (`__excess`) measures: 0 reliable cells in either grid.
- `snr_median` (rhythm presence): 267 of 399 cells reliable in grid A; 93 of 323 in grid B.

**Prediction** (synthetic; one reliable cell selected inside each training fold):
- FTD–CN: cell alone AUC 0.79 (p 0.02); gain over baseline 0.10 (0.07 to 0.14).
- AD–FTD: cell alone AUC 0.71 (p 0.04).
- AD–CN: cell alone AUC 0.59 (p 0.22).
- The beyond-spectrum pool was empty (no reliable cell).

**Reference cells (synthetic):** 4 cells equivalent to no group difference (90% CI of d within ±0.5); 66 cells reliable with |t| < 1 in every contrast.

## Consequences
- **Criterion 3 as first written:** under the uncorrected rule it fails with probability of about 0.79 even when nothing was injected. The run-1 failure is consistent with that rate.
- **With the correction over maps:**
    - the screen finds the injected instability at the injected frequency (32–42 Hz) and posterior location (Pz, P3);
    - it separates the posterior ("AD") from the frontal ("FTD") injection;
    - it gives no significant cluster below 24 Hz or in grid B.
- **Price of the correction:** the frontal FTD–CN injection, found at p = 0.006–0.012 within its own maps, is not significant after correction. At n = 88, the corrected screen detects the strongest injected effects only.
- **Beyond-spectrum measures in the synthetic data:** they were not reliable within subjects at 4 surrogates. The real-data run uses 10 surrogates.
- **Run 2:** the synthetic features are cached, so run 2 repeats only the analysis and the check (2000 permutations) before the real-data stages.
