# H15 · Which neurons decline with AD pathology under the posterior electrodes? (human tissue, SEA-AD)

**Question.** H13 leaves two explanations, which predict different tissue changes:
- **slow-inhibition loss:** SST interneurons decline;
- **lower excitatory drive:** excitatory pyramidal neurons decline.

Which happens in posterior cortex?
**Type.** Independent modality (post-mortem single-nucleus RNA-seq). Different people from the EEG cohort: triangulation, not a person-level link.
**When / where.** Cloud, 16–17 Nov 2026.

**Data.** Seattle Alzheimer's Disease Brain Cell Atlas (SEA-AD), multiregion release 2026-06-22. Per-nucleus metadata (cell class, subclass, donor, ADNC, Braak) and the per-donor, per-region continuous pseudo-progression score (CPS, with separate Aβ and pTau components).

| Region | Relation to the EEG |
|---|---|
| Angular gyrus (AnG) | under P3/P4 |
| Primary visual cortex (V1C) | under O1/O2 |
| Middle temporal gyrus (MTG) | positive control: published early SST loss |
| Dorsal frontal (DFC), superior temporal (STG), inferior temporal (ITG) | comparison regions |

**What was run.**
- **Per donor:**
    - the share of each GABAergic subclass within GABAergic neurons;
    - the share of each excitatory subclass within excitatory neurons;
    - the GABAergic share of all neurons.
- **Inclusion:** donors with ≥ 500 neurons, neurotypical-reference donors excluded.
- **Tests:**
    - Spearman ρ with the region's local CPS and with ADNC;
    - high-ADNC vs Not-AD/Low ratio;
    - region comparison restricted to the same 43 donors;
    - partial rank correlations with the Aβ and pTau components, each controlling for the other.

**Code.** `../../code/mechanism/tissue/seaad_celltypes.py <regions>`, `seaad_regions_tau.py`

| Output in `results/` | Content |
|---|---|
| `H15_celltypes_by_region.txt` | All subclasses × all regions: ρ with CPS and ADNC, high/low ratio |
| `H15_regions_tau.csv` / `.txt` | Same 43 donors: L2/3 IT, Sst and Pvalb vs CPS, Aβ\|pTau and pTau\|Aβ |
| `seaad_<region>_donor_fractions.csv` | Per-donor shares |
