# P08 · Second session (ds006036): test–retest reliability and subject-ID check

**Question.**
1. Do the measures repeat in the same people's second recording? This was planned as between-session ICC on flicker-free, eyes-closed data.
2. After a low ICC, do the subject numbers in ds006036 refer to the same people as in ds004504?

**Type.** Pipeline validation.
- Part 1 is label-free.
- Part 2 compared the two participant tables. It was done on 15 Nov, after the freeze, and logged in the ledger (P09).

**When / where.** Part 1 on the laptop, 14 Nov 2026. Part 2 in the cloud, 15 Nov 2026.

**What was run.**
1. `07_reliability.py --retest ds006036`: ICC(2,1) between ds004504 and ds006036 for the 54 subjects valid in both.
2. A comparison of age, sex, group and MMSE between the two participant tables, row by row.
3. A label-free check:
    - per-feature cross-session rank correlations;
    - within-session split-half correlations;
    - a fingerprint match: can a person's ds004504 spectral profile find their own ds006036 profile?

**Command.** `python scripts/07_reliability.py --dataset ds004504 --retest ds006036`

| Output in `results/` | Content |
|---|---|
| `retest_icc_vs_ds006036.csv` | Between-session ICC for every feature (n = 54) |
| `07_retest.log` | Console log |
