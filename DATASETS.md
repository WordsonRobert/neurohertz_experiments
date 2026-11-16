# Datasets

| Dataset | What it is | People | Recording | Used for | Labels opened? |
|---|---|---|---|---|---|
| **ds004504** (OpenNeuro, v1.0.8) | Resting EEG, eyes closed; Miltiadous et al. 2023, AHEPA Hospital, Thessaloniki | 36 AD, 23 FTD, 29 CN (88) | 19 channels (10–20), Nihon Kohden, 500 Hz, about 13 min each, 70 Hz hardware low-pass | Discovery: all confirmatory tests (H1–H6) and the exploratory work (H7–H9) | Yes, on 2026-11-14 after the freeze (ledger in `P09`) |
| **ds006036** (OpenNeuro / NEMAR on006036) | Same 88 people, recorded right after ds004504: photic stimulation at 5/10/15/20 Hz with eyes closed and opened | Same 88 people | Same system; about 6.7 min each | Second-session reliability (P08); driven responses H14. **63/65 AD/CN `.set` headers point to another subject's `.fdt`; read each subject's own `.fdt` (P13)** | Participant table opened 2026-11-14 to check IDs (88/88 identical on age, sex, group, MMSE) |
| **SEA-AD** (Allen Institute, multiregion release 2026-06-22; `s3://sea-ad-single-cell-profiling`) | Post-mortem single-nucleus RNA-seq; per-nucleus cell type; per-donor ADNC, Braak, continuous pseudo-progression (CPS, Aβ and pTau parts) | 84 donors (43 in AnG, V1C, STG, ITG) | AnG, V1C, MTG, DFC, STG, ITG metadata tables | Independent tissue modality for the mechanism (H15, H16) | Not applicable (different people) |
| **synthetic** | Simulated 19-channel EEG with a known injected mechanism (`scripts/00_make_synthetic_dataset.py`) | 29 CN, 36 "AD", 23 "FTD" (or smaller pilots) | 250 Hz, 170 s | Positive controls: the pipeline must find what was injected (P05, P10) | Ground truth by construction |
| **ds007427** (OpenNeuro, Antioquia) | CN, MCI, AD and PSEN1 carriers | about 140 | Not yet verified | Reserved as an untouched lockbox for confirmation | No |
| **Hospital cohort** (unpublished) | Collected by a collaborating lab | Not yet received | — | Planned confirmation cohort | No |

Groups in ds004504: AD = Alzheimer's disease; FTD = frontotemporal dementia; CN = cognitively normal controls. MMSE (Mini-Mental State Examination, 0–30; lower means more impaired) means: AD 17.75, FTD 22.17, CN 30.

The participant tables for ds004504 and ds006036 are in `2026-11-15/data_tables/`.
