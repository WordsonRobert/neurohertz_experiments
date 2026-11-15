# Mechanisms: which biology could make gamma unstable in AD?

Planning doc with the literature: "NeuroHertz: testing the four mechanisms behind gamma instability"
(Claude Doc, https://claude.ai/artifact/5AxPcDXarYhPze3umV3cnn). This file says how the code tests it.

## The candidates

| Code | Name in code | Mechanism | Class |
|---|---|---|---|
| T1 | synapses_onto_pv | Weaker pyramidal-to-PV synapses (NPTX2 / GluA4) | local loop |
| T2 | nav11_pv_output | PV cells fail to fire under load (Nav1.1) | local loop |
| T3 | erratic_drive | Excitatory input surges and dips over seconds (amyloid) | input |
| T4 | acetylcholine | Less tonic cholinergic depolarisation, less stable state | input |
| T5 | sst_loss | Fewer somatostatin interneurons (human postmortem: SST lost, PV preserved) | local loop |
| T6 | tau_silencing | Tau silences neurons: general loss of excitatory drive | input |

The theories are not exclusive. The realistic target is the **first split**: is the AD pattern more
consistent with a failing local PV-pyramidal loop (T1, T2, T5) or with changed input (T3, T4, T6)?

## Three layers, all fixed before labels are opened

**0. Is there an oscillation?** (`nh/oscfit.py`, config `features.oscillation`, `mechanism.presence`)
Per channel, the 30-45 Hz band must stand at least 0.5 dB above its flanks (22-27 and 53-62 Hz),
consistently across 4-s chunks (one-sided t, p < 0.01), against a background fitted only below 65 Hz
(ds004504's amplifier low-pass is 70 Hz). A subject "has gamma" if at least half of the posterior ROI
channels pass. If fewer than 50% of subjects in ANY group pass, every mechanistic result is labelled
DESCRIPTIVE_ONLY and belongs in the limitations, because instantaneous frequency of a non-oscillation
measures filter noise.

**1. Pre-registered tests M01-M16** (M17 dropped before freezing) (`config/pipeline.yaml: mechanism.tests`). Each test lists what
every theory predicts: `+`, `-`, `0` (no difference, tested as EQUIVALENCE: 90% CI inside +-0.5 SD or
+-0.3 r) or `?`. Covariates age and sex; Freedman-Lane permutation for group effects; partial Spearman
for correlations; Holm across all tests; sensitivity re-runs adding muscle, vigilance and recording
length. Outcome per theory per test: consistent / inconsistent / inconclusive.

| Test | What it asks | Mainly separates |
|---|---|---|
| M01 | Instability higher in AD (posterior ROI) | all predict it |
| M02 | FTD effect at Fz, F3, F4 (where FTD does damage) | T1 vs T2-T4 |
| M03 | FTD vs AD frontally at matched MMSE | T1 vs AD-specific theories |
| M04 | AD effect temporoparietal minus frontal | atrophy-following vs diffuse (T4) |
| M05, M06 | Peak width (damping), peak frequency | local loop; T2 keeps frequency |
| M07, M08, M09 | Cycle-scale jitter, 1-10 s wander, wander share (all beyond IAAFT noise) | local loop vs input |
| M10-M12 | Phase slips, slips under load, heavy tails (beyond noise) | T2 |
| M13 | Frequency-envelope co-modulation over seconds | T3 |
| M14 | Instability vs MMSE within AD (T3 predicts more in MILDER patients) | T3 vs the rest |
| M15, M16 | Alpha slowing goes with / explains the instability | T4 |
| ~~M17~~ | Eyes-open change: DROPPED, ds006036 has almost no flicker-free eyes-open time (median 4 s) | - |

"Beyond noise" = `<feature>_z`: the real value against 20 IAAFT surrogates with the same spectrum and
amplitude distribution. Phase slips happen in noise whenever the envelope dips; only the excess counts.

**2. Fingerprints** (`scripts/13_mechanism_fingerprints.py`, `nh/fingerprint.py`). Two deliberately
different simulators, each with one knob per theory: a pyramidal-PV-SST rate circuit (`nh/mechsim.py`,
tuned to a damped 38 Hz focus, Q ~ 4.8) and a cycle-by-cycle PING map that encodes each theory as stated
(`nh/cyclemodel.py`). Simulated subjects differ in baseline circuit, gamma SNR and 1/f slope, and are
measured with the real feature code. Outputs: per-theory fingerprints, whether the two families agree
(`agreement.csv`: firm / weak / conflict), separability, and identifiability: simulated studies of our
size where one theory is true, analysed within and ACROSS families.

Already visible during development: the rate model says weaker pyramidal-to-PV synapses make gamma
LESS damped, the opposite of the verbal prediction. Where the families disagree, the model prediction is
`?`, and the verbal prediction is scored separately.

**Comparison** (`14_mechanism_tests.py`): the covariate-adjusted AD-vs-CN effect vector is compared with
each family's fingerprints (cosine per theory, non-negative mix, local-loop share). A first-split claim is
made only if both families agree, the bootstrap 95% CI of the local share excludes 0.5, and
identifiability reached >= 0.8 within and >= 0.7 across families. Otherwise: "no claim".

## Run order (after Stage A and before freezing)

```bash
python scripts/13_mechanism_fingerprints.py --jobs 8           # ~1 h on 8 cores; never use --quick results
python scripts/00_make_synthetic_dataset.py --mechanism synapses_onto_pv --k 0.75 --n 29 36 23
python scripts/01_extract_features.py --dataset synthetic --no-ica --jobs 8
python scripts/14_mechanism_tests.py --dataset synthetic       # positive control: must recover the injection
# repeat the synthetic run with another --mechanism (e.g. erratic_drive) to see the other side of the split
python scripts/03_freeze.py                                    # hashes fingerprints.json with everything else
python scripts/14_mechanism_tests.py --dataset ds004504        # CONFIRMATORY only if frozen + unchanged
```

Outputs: `results/analysis/<dataset>/primary/mechanism/` - `presence.csv`, `tests.csv` (with-gamma and
all-subject versions), `sensitivity.csv`, `scorecard.csv`, `fingerprint_comparison.json`, `report.md`.

## Things to verify before freezing

- ds006036 is eyes-open with photic stimulation. Check the event names against
  `exclude_annotation_regex` in `config/datasets.yaml` and how much flicker-free time survives.
- The team's earlier finding (within AD, instability vs MMSE r = -0.43) came from the v1 pipeline.
  M14 re-tests it with covariates; do not cite the old number as support for or against T3.
- Two literature items flagged by the team as unverified: NPTX2 in genetic FTD (van der Ende et al.
  2020, JNNP; checked in the planning doc) and SST contribution to gamma (Veit et al. 2017, Nat
  Neurosci; not yet checked).
- Benzodiazepines lower gamma frequency and cholinesterase inhibitors may change gamma: without a
  medication list, the AD-vs-FTD comparison has an uncorrectable confound (say so in the paper).
