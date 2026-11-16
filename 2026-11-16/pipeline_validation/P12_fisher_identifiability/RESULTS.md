# Results · P12

## Main results

**1. The map is locally injective in both families, but badly conditioned.**

| Family | Whitened singular values | Condition number | Directions resolvable at k = 0.25 (n = 36 vs 29) |
|---|---|---|---|
| rate | 8.53, 3.44, 2.85, 1.64, 0.94, 0.61 | 14 | 3 of 6 |
| cycle | 3.47, 2.05, 0.88, 0.29, 0.18, 0.09 | 39 | 2 of 6 |

All six singular values are above zero, so the Jacobian has rank 6. In practice, the noise at our sample size leaves only two or three resolvable directions.

**2. Per-mechanism precision (joint Cramér–Rao SE of k; resolving k = 0.25 needs SE ≤ 0.125).**

| | T1 synapses onto PV | T2 PV output | T3 erratic drive | T4 cholinergic | T5 SST loss | T6 tau silencing |
|---|---|---|---|---|---|---|
| rate: SE | 0.39 | 0.13 | 0.12 | 0.11 | 0.22 | 0.18 |
| rate: inflation from confusion | 1.96 | 3.65 | 1.49 | 1.40 | 3.89 | 1.16 |
| rate: n per group needed | 319 | 32 | 30 | 26 | 100 | 64 |
| cycle: SE | 1.64 | 1.48 | 0.71 | 1.92 | 1.20 | 0.16 |
| cycle: inflation from confusion | 4.93 | 3.17 | 5.40 | 7.03 | 1.48 | 2.21 |
| cycle: n per group needed | 5523 | 4488 | 1039 | 7581 | 2979 | 53 |

"Inflation" is the joint SE divided by the SE if only that mechanism were unknown. It is the price of the other mechanisms imitating it.

**3. First split (local loop vs input), two parameters.**
- rate: SE(local − input) = 0.16.
- cycle: SE(local − input) = 0.61.
- 2 SE exceeds 0.25 in both families.

**4. The two families agree on a feature subspace, not on the mechanisms.**
- Principal angles between the column spaces: 1.6°, 10.9°, 25.9°, 47.2°, 65.1°, 82.8°.
- Cosine between the two families' column for the same mechanism: T1 0.77, T3 0.60, T2 0.28, T5 0.15, T4 0.09, T6 −0.05.

## Consequences
- **Injectivity is not the obstacle; conditioning is.** Even in the simulations, where 91–100% of subjects have a gamma rhythm, a 36 vs 29 study resolves 2–3 combinations of the six mechanisms, not the six mechanisms.
- **The resolvable combinations are model-dependent.** Both families span about the same 2–3 feature directions (angles below 26°). They assign different mechanisms to those directions: only T1 and T3 have similar columns in both families. A mechanism label therefore inherits the choice of simulator. This is the quantitative form of P04's cross-family recovery failure.
- **The first split is not resolvable at n = 65,** in either family.
- **These are upper bounds for ds004504.** The simulated gamma SNR never reaches the real-data regime: 9% of real subjects have a detectable oscillation (H6). Real-data identifiability is lower than every figure above.
- **For future data:** the bound says what to change.
    - Under the rate model, T2–T4 become resolvable at about 30 per group *if gamma is measurable in most subjects* (for example 40 Hz driven responses, MEG).
    - Under the cycle model, no realistic n suffices with these features. Separating the mechanisms needs features or modalities that add new directions: independent biomarkers (amyloid / tau PET, CSF, GABA MRS), or a perturbation.
