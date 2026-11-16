# H19 · Superficial Sst supertypes in angular gyrus, and the combined tissue → EEG bridge

**Question 1.** H15 found the Sst subclass share stable in angular gyrus (AnG). The SEA-AD papers report that only specific superficial Sst supertypes are lost. Do the Sst supertypes that are vulnerable in middle temporal gyrus (MTG) also decline in AnG and V1C?
**Question 2.** If both L2/3 IT and vulnerable-Sst losses are put into the H13 circuit, each sized from AnG tissue, does the prediction match the EEG better than L2/3 alone (H16)?
**Rival tested.** R1 (slow/SST inhibition loss), raised by the 17 Nov literature check.
**Type.** Independent modality (SEA-AD) plus cross-modal prediction. Exploratory.
**When / where.** Cloud, 17 Nov 2026.

**What was run.**
- **Discovery (MTG, 83 donors):** each Sst supertype's share of GABAergic neurons vs local CPS (Spearman). The vulnerable set is every supertype with ρ < 0 and p < 0.05.
- **Out-of-region test (AnG and V1C, 43 donors each):** the summed share of that fixed set vs local CPS, with no re-selection, alongside L2/3 IT and the whole Sst subclass.
- **Bridge (AnG):** high ADNC vs Not AD/Low, bootstrapped over donors.
    - Excitatory-drive loss, as in H16: all pyramidal outputs × (1 − loss).
    - Fraction of all Sst neurons lost from the vulnerable set: slow-loop output wES × (1 − loss).
    - Run three ways: L2/3 only, Sst only, and combined. Nothing is fitted to EEG apart from one global offset.

**Code.** `../../code/mechanism/sst_supertypes.py`, `bridge2.py`

| Output in `results/` | Content |
|---|---|
| `sst_log.txt`, `sst_supertypes.csv` | Per-supertype ρ in MTG, AnG and V1C |
| `sst_vulnerable_by_region.csv` | Vulnerable-set sum, whole Sst subclass and L2/3 IT vs CPS, by region |
| `bridge2_log.txt` | Tissue losses with CIs; predicted vs observed EEG features for the three variants |
