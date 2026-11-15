# NeuroHertz v2: gamma-frequency instability in Alzheimer's disease

v2 replaces the v1 Colab sessions (VMD → VAE sweep → LOSO). It is built so that **no step can see anything it shouldn't**, and so that the instability claim is tested against the things that could fake it: gamma power, the 1/f background, burstiness, peak frequency and muscle.

- `docs/ANALYSIS_PLAN.md`: hypotheses, cohorts, endpoints and decision rules (pre-registration draft).
- `docs/LEAKAGE_CONTRACT.md`: 15 explicit rules, each with how the code enforces it.

## Layout

```
config/pipeline.yaml      every analysis parameter (hashed at freeze)
config/datasets.yaml      where each cohort lives + its role (discovery/paired/reliability/normative/lockbox)
nh/
  preprocess.py           label-blind cleaning: filters, bad channels, ICA+ICLabel, EMG-aware epoch rejection, fixed 240 s
  spectral.py             comparators: band powers, specparam aperiodic/peaks, gamma above 1/f, EMG indices
  gamma.py                instantaneous-frequency instability candidates + IAAFT-surrogate normalisation
  surrogates.py           IAAFT surrogates
  simulate.py             ground-truth simulator (jitter vs amplitude, 1/f, peak, burstiness, EMG)
  dynamics.py             mechanism descriptors: fast vs slow jitter, wander timescale, slips, tails, coupling
  oscfit.py               oscillation-presence gate, damped-oscillator fit (f0, width, Q), vigilance series
  mechsim.py              pyramidal-PV-SST rate circuit, one knob per candidate mechanism
  cyclemodel.py           cycle-by-cycle PING map: the same mechanisms "as stated" (second model family)
  fingerprint.py          fingerprints, identifiability, comparison of a real effect pattern with them
  labels.py               THE ONLY module that reads diagnoses/MMSE: blinding + lockbox gates
  ledger.py               append-only access log (registry/access_ledger.jsonl)
  stats.py                Freedman-Lane permutation, Hedges g CIs, partial Spearman, max-T, ICC, DeLong
  predict.py              nested CV, full-pipeline permutation, incremental AUC, frozen model
scripts/
  01_extract_features.py  Stage A (label-blind)       02_simulation_validation.py  Stage 0 (metric choice)
  02b_calibrate_simulation.py  Stage 0 (label-free calibration of the simulator)
  03_freeze.py            Gate 1                      04_discovery_analysis.py     Stage B: H1-H4
  05_prediction.py        Stage B: P1-P4              06_external_validation.py    Stage C: lockbox
  07_reliability.py       split-half / test-retest ICC
  08_normative_and_paired.py   N1 normative ageing deviation (LEMON) + paired condition (ds006036: flicker-free stretches only)
  09_ceiling_check.py     interpretable model vs TabPFN / Riemannian tangent space (benchmarks, never reported as the model)
  10_run_ablations.py     extract every method variant (one-at-a-time, factorial, simulation)  (label-blind)
  11_select_methods.py    choose each method LABEL-FREE: split-half ICC, then least EMG coupling / simulation score
  12_specification_curve.py    H1 across the 36-pipeline multiverse + joint permutation test (reporting only)
  00_make_synthetic_dataset.py  fake EEG with a KNOWN mechanism injected: end-to-end dry run / power check
  13_mechanism_fingerprints.py  Stage 0c (label-free): what each mechanism does to the features, 2 model families
  14_mechanism_tests.py   Stage B: presence gate, pre-registered tests M01-M17, scorecard, fingerprint comparison
tests/                    leakage guards + method checks  (python -m pytest -q)
```

## Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q          # 49 tests: leakage guards must pass before anything else
```

On Google Colab use `colab/NeuroHertz_run_all.ipynb`: unzip this folder anywhere in Drive, open the
notebook, run the cells top to bottom. Dataset folders are found under `${NH_DRIVE}` (default
`/content/drive/MyDrive`), e.g. `MyDrive/data` and `MyDrive/ds004504-download*`; see
`config/datasets.yaml` or pass `--roots`.

## Run order

```bash
# Stage A: label-blind features for ds004504 (all Drive parts are searched; see inventory.csv)
python scripts/01_extract_features.py --dataset ds004504 --jobs 8 --split-half

# Stage 0: calibrate the simulator to POOLED label-free descriptives, then choose the primary metric
python scripts/02b_calibrate_simulation.py --dataset ds004504
python scripts/02_simulation_validation.py --seeds 8 --n-surr 10 --jobs 4
# Stage 0b: method ablations, chosen without labels (docs/METHODS_REVIEW.md)
python scripts/10_run_ablations.py --mode simulation    --jobs 8                     # estimator x median on ground truth
python scripts/10_run_ablations.py --mode one-at-a-time --dataset ds004504 --jobs 8 # each option vs primary
python scripts/11_select_methods.py --dataset ds004504   # -> registry/method_selection.json; copy choices into pipeline.yaml
python scripts/10_run_ablations.py --mode factorial     --dataset ds004504 --jobs 8 # 36 pipelines, for the spec curve later

# Stage 0c: mechanistic fingerprints (label-free; ~1 h on 8 cores), then a synthetic dry run
python scripts/13_mechanism_fingerprints.py --jobs 8
python scripts/00_make_synthetic_dataset.py --mechanism synapses_onto_pv --k 0.75 --n 29 36 23
python scripts/01_extract_features.py --dataset synthetic --no-ica --jobs 8
python scripts/14_mechanism_tests.py --dataset synthetic        # must point to the injected mechanism

# Look ONLY at qc.csv and pooled label-free descriptives.
# Then set `status: frozen` and `statistics.primary_feature: <selected>` in config/pipeline.yaml
python scripts/03_freeze.py

# Stage B: discovery (labels open now, logged)
python scripts/04_discovery_analysis.py --dataset ds004504
python scripts/05_prediction.py         --dataset ds004504        # also saves models/frozen_*.joblib
python scripts/12_specification_curve.py --dataset ds004504       # robustness of H1 across all 36 pipelines
python scripts/09_ceiling_check.py      --dataset ds004504        # is the interpretable model leaving AUC behind?
python scripts/14_mechanism_tests.py    --dataset ds004504        # mechanisms: gate, M01-M17, scorecard, fingerprints

# Stage C: each lockbox, once
python scripts/01_extract_features.py --dataset caueeg --register --jobs 8
python scripts/06_external_validation.py --dataset caueeg --model models/frozen_ds004504_<primary_model>.joblib

# Reliability, normative ageing, paired condition
python scripts/07_reliability.py --dataset ds004504               # split-half
python scripts/08_normative_and_paired.py normative --norm lemon --target ds004504
python scripts/08_normative_and_paired.py paired --a ds004504 --b ds006036   # flicker-free stretches only
```

Before freezing, discovery labels can only be opened with `--dev-unblind-reason "..."`. That opening is logged, and every output it produces is stamped `EXPLORATORY`.

## Runtime

Per subject on one core: about 30 s with ICA plus about 6 s per surrogate × 19 channels. With the default 20 surrogates that is roughly 2–3 min per subject. For 88 subjects use `--jobs` equal to your core count. Per-subject results are cached in `per_subject/*.json`, so runs resume.
