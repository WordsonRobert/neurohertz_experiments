# P07 · Split-half reliability of every measure

**Question.** If each person's 240 s of clean data is split into two halves, do the halves give the same value? This is measured by ICC(2,1), corrected to full length with Spearman–Brown.
**Type.** Pipeline validation. No labels.
**When / where.** Final run on the laptop, 14 Nov 2026.

**Command.** `python scripts/07_reliability.py --dataset ds004504`
**Code.** `../../code/neurohertz_v2_frozen/scripts/07_reliability.py`, `../../code/neurohertz_v2_frozen/nh/stats.py` (`icc_2_1`)

| Output in `results/` | Content |
|---|---|
| `split_half_icc.csv` | metric, n, half-length ICC, Spearman–Brown full-length ICC (ROI) |
| `07_reliability.log` | Console log |
