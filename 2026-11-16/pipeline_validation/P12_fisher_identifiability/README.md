# P12 · Fisher identifiability: how many mechanisms can a study of our size resolve?

**Question.** P04 asked whether simulated mechanisms can be *recovered*. P12 asks the underlying mathematical question:
- If each mechanism T1–T6 has a severity k, does the map from (k₁ … k₆) to the expected EEG features separate them?
- If it does, how precisely can each k be estimated from a 36 AD vs 29 CN contrast?

The feature map is "injective" near baseline if its Jacobian has full rank. Whether that is useful depends on the noise, so the analysis uses the Fisher information and the Cramér–Rao bound (the smallest standard error any unbiased estimator can reach).

**Type.** Pipeline validation. Simulated circuits only. No labels. Exploratory: added after the freeze, so it does not change any confirmatory result.
**When / where.** Cloud, 16 Nov 2026. It reuses P04's simulated subjects and runs no new simulation.

**What was run.** For each simulator family (rate, cycle):
1. The 12 fingerprint features were standardised on the baseline circuits. `burst_freq_sd` was dropped because 29% of its simulated values are missing.
2. **Jacobian:** J[f, j] = slope of feature f against severity k of theory j (OLS on baseline + k = 0.25, 0.5, 0.75; 24 simulated subjects per cell).
3. **Noise:** Σ = pooled within-cell covariance of the features (Ledoit–Wolf shrinkage). It includes the simulated between-subject differences in circuit, gamma SNR and 1/f slope.
4. **Fisher information of the group contrast:** F = Jᵀ Σ⁻¹ J / (1/36 + 1/29).
5. **Read-outs:**
    - singular values of the whitened Jacobian;
    - joint Cramér–Rao SE of each k, compared with its SE if it were the only unknown;
    - number of directions with 2 SE < 0.25;
    - n per group needed to resolve k = 0.25;
    - the same for the two-parameter first split (local loop T1, T2, T5 vs input T3, T4, T6);
    - principal angles between the two families' Jacobian column spaces.

A low-SNR check was also run (the third of simulated subjects with the lowest gamma SNR). It is reported in the JSON but is not informative: even that third has an oscillation in 89–100% of subjects, against 9% in ds004504 (H6).

**Command.** `python code/fisher/fisher_identifiability.py ../2026-11-15/pipeline_validation/P04_mechanism_identifiability/results/sim_features.csv pipeline_validation/P12_fisher_identifiability/results` (run from `2026-11-16/`)
**Code.** `../../code/fisher/fisher_identifiability.py`

| Output in `results/` | Content |
|---|---|
| `fisher_identifiability.json` | Every read-out above, per family, plus the cross-family comparison |
| `jacobian_rate.csv`, `jacobian_cycle.csv` | J: rows are features, columns are T1–T6, in baseline SD per unit k |
