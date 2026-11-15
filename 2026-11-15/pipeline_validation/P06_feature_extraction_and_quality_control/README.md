# P06 · Feature extraction and quality control

**Question.** How many recordings could be processed, why were any excluded, and how much clean data did each person contribute?
**Type.** Pipeline validation. No labels.
**When / where.** Final run on the laptop, 14 Nov 2026.

**What was run.** The frozen preprocessing (`../../code/neurohertz_v2_frozen/nh/preprocess.py`):
1. Filter 1–100 Hz, 50 Hz notch, resample to 250 Hz.
2. Two-pass bad-channel detection; ICA with ICLabel; BSS-CCA muscle removal.
3. 2-s epochs cleaned with autoreject.
4. CSD re-reference.
5. The first 240 s of clean data are kept per person; under 120 s means exclusion.

For ds006036, only flicker-free, eyes-closed stretches were kept (condition mask in `config/datasets.yaml`). Every feature was then computed, including 20 surrogates per channel.

**Commands.**
```bash
python scripts/01_extract_features.py --dataset ds004504 --split-half --jobs 8
python scripts/01_extract_features.py --dataset ds006036 --split-half --jobs 8
```

| Output in `results/<dataset>/` | Content |
|---|---|
| `qc.csv` | Per subject: status, reason, bad channels, ICA/muscle components removed, epochs rejected, clean seconds |
| `inventory.csv` | Recordings found |
| `run_meta.json` | Status counts and hashes (extraction `e2eebed6…`, code `5ab5a4a7…`) |
| `01_<dataset>.log` | Console log |

The full per-subject feature tables are in `../../data_tables/`.
