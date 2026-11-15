# P02 · Method ablations: choosing preprocessing and estimator settings without labels

**Question.** Which preprocessing and frequency-estimation settings give a primary instability measure (`burst_freq_sd`, the spread of gamma burst frequencies) that is reliable within a recording and not driven by muscle?
**Type.** Pipeline validation. No labels; diagnoses were never opened.
**When / where.**
- Colab, 13 Nov 2026: primary, reference-csd/rest, muscle-bss_cca, epochs-autoreject, aperiodic-irasa.
- Laptop, 13–14 Nov 2026: estimator-sst/vmd, median-single, surr_chunk-s15/s30/s60. The estimator variants were re-run after an estimator scale fix.
- Laptop, 14 Nov 2026: combo-csd and combo-rest.

**What was run.** The full feature extraction on ds004504 was repeated with one setting changed at a time:
- **reference:** average / CSD / REST
- **muscle removal:** none / BSS-CCA
- **epoch rejection:** MAD rule / autoreject
- **aperiodic method:** specparam / IRASA
- **IF estimator:** Hilbert / SST / VMD
- **median filter:** multi / single
- **surrogate chunk:** 15 / 30 / 60 s

For each variant two label-free numbers were computed:
- the split-half reliability (ICC) of the primary measure;
- its correlation with a muscle (EMG) index.

Because no single change met the pre-stated reliability floor (ICC ≥ 0.6), two **combined** pipelines were then run (CSD + BSS-CCA + autoreject + single median, and the same with REST). The rule for choosing between them was written before they were run.

**Commands.**
```bash
python scripts/10_run_ablations.py --mode one-at-a-time --dataset ds004504 --jobs 8     # Colab
bash run_laptop_ablations.sh                                                            # laptop, code/colab/
python scripts/01_extract_features.py --dataset ds004504 --split-half --variant combo-csd --set preprocessing.reference=csd preprocessing.muscle.method=bss_cca preprocessing.epochs.method=autoreject features.if_median.mode=single
python scripts/11_select_methods.py --dataset ds004504
```
**Code.** `../../code/neurohertz_v2_frozen/scripts/10_run_ablations.py`, `11_select_methods.py`, `01_extract_features.py`, `../../code/neurohertz_v2_frozen/config/pipeline.yaml` (section `ablations`).

| Output in `results/` | Content |
|---|---|
| `method_selection.json` | Every candidate's ICC and EMG coupling, the choice per dimension, and the `final_decision` block (combined runs, rule, final pipeline, caveats) |
| `variants/<variant>/run_meta.json` | Settings, hashes and status counts of each variant run |
| `variants/<variant>/qc.csv` | Per-subject preprocessing record of each variant |
| `ablations_laptop.log` | Console log of the laptop ablations |

Note: the ablations used single-pass bad-channel detection (83 usable subjects); the final run uses two-pass detection (88).
