# neurohertz_experiments

This is the record of every NeuroHertz analysis that has been run: the code, the exact settings, the output files and a plain-English account of each run.

NeuroHertz asks whether the **instability of brain rhythms** in resting EEG separates people with **Alzheimer's disease (AD)** from cognitively normal controls (CN) and from people with frontotemporal dementia (FTD). The study started with the gamma band (30–45 Hz) and has since widened to any frequency band, and to a mechanistic account tested across EEG, a calibrated circuit model, driven responses and human brain tissue (`2026-11-16/MECHANISM_HYPOTHESIS.md`).

## How this repository is organised

```
neurohertz_experiments/
├── README.md                  <- you are here
├── GLOSSARY.md                <- every technical term used below, in plain English
├── DATASETS.md                <- which EEG recordings were used and where they come from
├── 2026-11-15/                <- snapshot: everything run from the last Colab session up to 15 Nov 2026
│   ├── README.md              <- index of all runs, timeline, hypothesis map  (START HERE)
│   ├── pipeline_validation/   <- runs that test the PIPELINE (does the method measure what it claims?)
│   │   └── P01 … P10          one folder per validation run
│   ├── bio_tests/             <- runs that test a BIOLOGICAL HYPOTHESIS about AD
│   │   └── H1 … H9            one folder per hypothesis
│   ├── code/                  <- the exact code that produced every result
│   └── data_tables/           <- per-subject feature tables and participant lists
└── 2026-11-16/                <- frequency x electrode instability screen (same layout; numbering continues)
    ├── README.md
    ├── pipeline_validation/P11
    ├── MECHANISM_HYPOTHESIS.md <- the mechanistic hypothesis and its multimodal evidence chain
    ├── pipeline_validation/P11–P13
    ├── bio_tests/H10–H17
    └── code/                  <- only the files added or changed since 2026-11-15
└── 2026-11-17/                <- tests of the mechanistic hypothesis against its rivals (H18, H19); probe-order audit (P14)
```

Each date folder holds the runs made on that date. Numbering continues across dates (P11 follows P10; H10 follows H9).

Every run folder has the same three parts:

| File | What it contains | Who it is for |
|---|---|---|
| `README.md` | The question, what was run in plain English, the exact command, the code used, the inputs, and a list of output files | Everyone |
| `RESULTS.md` | The main results stated as they came out, then the consequences that follow from them | Everyone |
| `results/` | The raw output files (CSV, JSON, logs, figures) | Anyone re-analysing |

**Biologists:** read `2026-11-15/README.md`, then each folder's `RESULTS.md`; `GLOSSARY.md` explains the terms.
**Computational people:** each `README.md` gives the exact command and code path; the `code/` folder runs end to end (see `code/README.md`).

## Two kinds of evidence

- **Confirmatory.** The frozen, pre-registered analysis of ds004504 (bio tests H1–H6). Its hypotheses, methods and decision rules were fixed and hashed before any diagnosis label was opened (see `pipeline_validation/P09`).
- **Exploratory.** Everything run after the labels were opened (H7 onwards). These analyses generate hypotheses; a result from them needs confirmation in a new cohort.

Each folder states which kind it is.

## Raw EEG is not in this repository

The raw recordings are public on OpenNeuro (see `DATASETS.md`). This repository holds derived features, statistics and logs.
