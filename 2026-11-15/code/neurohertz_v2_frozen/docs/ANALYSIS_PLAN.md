# NeuroHertz v2: Statistical analysis plan and multi-cohort programme

**Status:** draft for pre-registration. The SHA-256 of this file is recorded at freeze (`scripts/03_freeze.py`), so any later edit is detectable.
**Target journal (paper 1):** *Clinical Neurophysiology*. It is not a methods journal and gives low priority to pilot studies, so the paper must be a substantial, replicated finding about human disease physiology.
**Companion document:** `docs/LEAKAGE_CONTRACT.md` (what each stage may see, and how that is enforced).

---

## 1. The claim, and what would falsify it

> **Primary claim.** In Alzheimer's disease, the frequency of resting gamma-band (30–45 Hz) activity is less stable over time than in cognitively normal older adults. This instability (a) is not explained by gamma power, the 1/f background, peak frequency, burstiness or muscle activity; (b) relates to cognitive impairment; and (c) replicates in at least one independent cohort analysed with a pipeline frozen beforehand.

It is a *candidate electrophysiological marker*, not a clinically validated biomarker.

**Falsifiers, stated in advance:**

- H1 fails in discovery.
- The effect disappears once the nuisance covariates in H3 are added.
- The effect does not replicate (E1) in the lockbox cohorts that have usable gamma.

Any of these is reported as found.

## 2. What v1 lacked, and how v2 addresses it

| Gap in v1 | v2 response |
|---|---|
| VAE trained on CN data (labels, and the test subjects themselves) chose each subject's VMD settings | Removed. Extraction is label-blind and fixed in the config (Leakage rules 1–4). |
| P3 chosen from a sweep over the whole dataset | Pre-specified posterior ROI plus a scalp-wide max-T test (rule 5). |
| C chosen on outer-loop accuracy; "permutation test" was one shuffle | Nested CV with full-pipeline permutation (rules 6, 8). |
| README numbers didn't match the saved results (AUC 0.781 vs 0.748) | Every output carries the analysis hash. Only code-generated numbers are reported. |
| No test that the feature measures *instability* rather than power or SNR | Ground-truth simulations plus IAAFT surrogates plus nuisance-adjusted H3. |
| Raw ds004504 above ~25 Hz looks broadband-flat (see §9), consistent with EMG or noise dominance | ICA (ICLabel muscle removal), EMG-burst epoch rejection, EMG covariates, sensitivity on the authors' cleaned derivatives. |
| Unequal recording length (AD 5.1–21.3 min) | The same 240 s of clean data per subject. |
| One dataset, no replication | Discovery, then paired condition, reliability, normative ageing, and lockbox external cohorts (§4). |
| No reliability evidence | Split-half ICC (all cohorts) and test–retest ICC (ds004148). |
| Gamma peak is lower in AD (Güntekin et al. 2023), so "mode nearest 40 Hz" samples different physiology per group | Fixed band as primary, plus an individual-band sensitivity analysis. Peak frequency is reported as a nuisance variable. |
| Group differences in sex (AD 24F/12M vs CN 11F/18M) and no education field | Age and sex are covariates everywhere. Education is used where a cohort has it. |

## 3. Pipeline (stages and gates)

```
Stage A  Label-blind extraction  01_extract_features.py      -> per-subject features + QC (every cohort)
Stage 0  Simulation (no labels)  02b_calibrate_simulation.py -> base signal matched to POOLED label-free descriptives
                                 02_simulation_validation.py -> primary metric chosen on ground truth
Gate 1   Freeze                  03_freeze.py                -> hash(config, code, this plan, metric choice)
Stage B  Discovery inference     04_discovery_analysis.py    -> H1-H4, topography, robustness, exploratory
         Discovery prediction    05_prediction.py            -> P1-P3, then P4 frozen model
Gate 2   Lockbox registration    01_extract_features.py --register (after freeze)
Stage C  External validation     06_external_validation.py   -> E1-E5, one shot per cohort
Stage D  Reliability / norms     07_reliability.py (+ normative analysis, §8)
```

## 4. Cohorts and what each one is for

| Cohort | Role | Question it answers | n (as described) | Status / to verify |
|---|---|---|---|---|
| **ds004504** (AHEPA, Greece) | discovery | H1–H4, prediction | AD 36, FTD 23, CN 29; 19 ch, 500 Hz, eyes closed | On disk across Drive parts. **Not blind.** |
| ds004504 *derivatives* | discovery-sensitivity | Does the result survive an independent cleaning pipeline (ASR + ICA, 0.5–45 Hz)? | same | Download the `derivatives/` folder. |
| **ds006036** (same 88 people) | paired | Photic session recorded right after ds004504. Checked 2026-11-14 on all 88 event files: eyes closed for most of it; flicker-free eyes-open time median 4 s (max 49 s), so test M17 was dropped. Flicker-free eyes-closed time (median 266 s, 63 people ≥ 120 s) is used as a second session for label-free test-retest reliability. | same people | Done. |
| **ds004148** | reliability | Test–retest ICC in healthy adults | 60 healthy (VERIFY sessions) | Download; VERIFY run naming. |
| **LEMON** (MPI Leipzig) | normative | Does the metric change with healthy ageing? Is the AD effect "accelerated ageing"? | young and older healthy adults (VERIFY) | Download. |
| **ds007427** (Univ. de Antioquia, Colombia) | lockbox | MCI and AD replication; presymptomatic PSEN1-E280A carriers | CN 36, MCI 24, AD 8, + 70 carrier/non-carrier | OpenNeuro, CC0. VERIFY sampling rate. |
| **ds005048** (Tehran) | lockbox / perturbation | Does resting instability predict 40 Hz entrainment? | mild AD 17, MCI 6, CN 10 | 250 Hz, eyes open; rest = silent gaps only. |
| **PEARL-Neuro** (ds004796) | normative / preclinical | Does instability appear with APOE e4 risk alone? | 79 healthy 50-63 y with genotype | 1000 Hz, HW LP 280 Hz. |
| **Dortmund Vital** (ds005385) | normative / reliability | Lifespan norms; 5-year retest | 608 healthy 20-70 y; 208 follow-up | 1000 Hz; VERIFY access. |
| ~~ADFSU~~ | excluded | - | AD 80, HC 12 | 128 Hz, stored 0.5-30 Hz: **cannot test gamma**. Same for ADSZ and APAVA. |
| **BrainLat** (Synapse) | lockbox | Replication plus specificity (AD, bvFTD, PD, MS, HC), 128-ch Biosemi | 780 total; EEG subset VERIFY | Data use agreement; need RAW files (the released processed data stop at 40 Hz). |
| **CAUEEG** | lockbox | MCI continuum (CN < MCI < dementia) | 459 normal / 417 MCI / 311 dementia recordings | 200 Hz, analog 0.5-70 Hz. Request form plus ethics approval; MMSE not listed. |
| **Hospital cohort** (local) | lockbox | Prospective replication in an Indian clinical population | ? | **Not yet identified on disk** (see §11). |

**Power.** ds004504 (36 vs 29) detects g ≥ 0.71 at 80% power (two-sided α = .05), so it is underpowered for moderate effects. For a lockbox replication (one-sided α = .05, 80% power) the needed n per group is 50 at g = 0.5, 35 at g = 0.6 and 26 at g = 0.7. This is why at least one large lockbox (BrainLat or CAUEEG) is part of the plan.

## 5. Measurements

**Preprocessing** (config `preprocessing`):

- channels mapped to the 19 standard 10–20 sites;
- 1–100 Hz zero-phase FIR filter;
- line-noise notch;
- resample to 250 Hz;
- bad channels in two passes: electrode faults (flat, uncorrelated, |robust z| of log-variance > 10) before ICA; per-subject robust z of variance and 55–90 Hz power after ICA; interpolated;
- extended-infomax ICA, with ICLabel removing muscle, eye, heart, line and channel-noise components at p ≥ 0.80;
- BSS-CCA muscle removal (spectral-slope criterion);
- 2-s epochs: EMG-burst MAD rule plus autoreject (per-subject learned thresholds, label-free);
- **CSD (surface Laplacian) reference**, applied after epoch rejection (average and REST are ablation options);
- the first 240 s of clean data kept; subjects with < 120 s are excluded.

**Gamma metrics** (`nh/gamma.py`). These are computed on the 30–45 Hz band from the analytic signal, per channel. The candidates are:

- spread of median-filtered instantaneous frequency above the subject's median envelope (`if_sd`, `if_mad`, `if_iqr`);
- amplitude-weighted spread (`if_awsd`);
- cycle-period CV;
- within-burst IF spread (`burst_if_sd`);
- **between-burst frequency dispersion** (`burst_freq_sd`);
- SNR-extrapolated IF variance (`xjit_var`);
- the v1-style statistic (`legacy_std`, for reference only).

Each key metric is also expressed relative to 20 IAAFT surrogates (`_z`, `_excess`). Surrogates keep the spectrum and the amplitude distribution, so the surrogate-relative value is the part not explained by the spectrum.

**Comparators and nuisance variables** (`nh/spectral.py`): relative band powers, theta/alpha ratio, alpha peak frequency, aperiodic offset and exponent (specparam, 2–47 Hz), gamma power above the 1/f fit, gamma peak frequency, 55–90 Hz power and 30–90 Hz slope (EMG indices), envelope mean and burst rate.

**Subject-level value.** The mean over the pre-specified posterior ROI (P3, Pz, P4, O1, O2). Regions and single channels are secondary.

**Final pre-freeze decisions (2026-11-14, label-free; full record `registry/method_selection.json`).**

- Methods chosen by the ablation rules below plus one pre-stated second step (no single option reached split-half ICC ≥ 0.6): CSD reference, BSS-CCA, autoreject, specparam, Hilbert, single 20 ms median filter, 30-s surrogate chunks.
- **Primary metric: `burst_freq_sd`** (between-burst gamma frequency dispersion, Hilbert). Most jitter-specific metric in simulation (0.61 vs ≤ 0.2 for all non-burst metrics). Full-length split-half ICC 0.66 (bootstrap 95% CI 0.46–0.79) and EMG coupling 0.09 in the final pipeline.
- **Deviation from the Stage-0 rule, disclosed:** the rule selects `burst_freq_sd_z` (0.68), whose real-data split-half ICC is about 0 in every pipeline. The raw metric is used instead, with the 1/f exponent (ICC 0.98) as a covariate in H1/H2/E1 to remove its largest simulated nuisance. Recorded as `--override-reason` in the freeze record.
- IF standard deviation and cycle CV were rejected as primaries: reliable, but about 20× more sensitive to gamma burstiness than to frequency jitter in simulation.
- Label-free presence check: only about 5–8% of subjects show a 30–45 Hz peak above the 1/f background, so the mechanistic analyses (§9b) are expected to be DESCRIPTIVE_ONLY, and "instability" is interpreted as departure from what the spectrum predicts, not as wobble of a sustained rhythm.

**Primary metric selection (Stage 0, pre-specified rule).** For each candidate, the effect of true jitter (0–4 Hz) is divided by the largest effect of any nuisance factor across its simulated range: gamma amplitude ×6, 1/f exponent 1–2.5, peak 33–39 Hz, burst duration 0.1–1 s, EMG 0–1. Effects are in units of seed-to-seed SD. Only metrics with Spearman ≥ 0.9 against jitter are eligible, and the best score wins. Before freezing, the simulation's base signal is calibrated to *label-free pooled* descriptive statistics of the real data.

## 6. Discovery hypotheses (ds004504)

All tests are two-sided at α = .05. Group effects are OLS with HC3 standard errors and Freedman–Lane permutation p (10,000 permutations); Hedges' g has a bootstrap 95% CI. Fixed-sequence gatekeeping applies: a hypothesis can only be confirmed if every one before it was.

- **H1.** `primary ~ group(AD vs CN) + age + sex + aperiodic exponent (ROI)`. The 1/f exponent is in the primary model because it is the raw primary metric's largest nuisance in simulation (§5, final decisions).
- **H2.** Within AD: partial Spearman(primary, MMSE | age, sex, aperiodic exponent). MMSE is coarse (33 of 36 values even) and CN are at ceiling, so this is a correlation, not a severity model.
- **H3.** H1 plus gamma power above 1/f, aperiodic exponent, envelope mean, burst rate, alpha peak frequency and the EMG index. Also a nested-logit likelihood-ratio test: does the primary metric add to the nuisance-only model?
- **H4.** AD vs FTD and FTD vs CN, Holm-adjusted within H4.

*Over-adjustment caveat for H3:* true frequency jitter itself broadens the gamma spectral peak, so it can partly show up in spectral covariates. A drop in the H3 effect is therefore not, on its own, proof that "it was only spectrum". The surrogate-normalised metrics (`_z`) are the primary guard against this, because they remove exactly what the spectrum predicts. Report H3 alongside the surrogate result.

**Always reported, not gated:**

- scalp topography (19 channels, max-|t| FWER);
- regions;
- robustness: plus EMG, plus clean duration, individual band, average reference (specification curve), ICA off, derivatives;
- an **EXPLORATORY** table of every candidate metric with BH-FDR.

## 7. Prediction (secondary; ds004504)

Several **multi-feature models** are fixed in `config/pipeline.yaml` (`prediction.models`) before unblinding. Each one is impute → scale → [in-fold selection] → logistic regression (L2, or elastic net where marked):

| Model | Inputs | Purpose |
|---|---|---|
| M1 | ROI mean of the primary metric (1 feature) | reference: one number per person |
| **M2 (primary)** | primary metric at P3, Pz, P4, O1, O2 as 5 separate features | lets the model weight electrodes instead of averaging them |
| M3 | primary metric at all 19 electrodes; the best k = 3 or 4 are picked **inside each training fold** (k tuned by inner CV) | data-driven electrode choice without leakage; reports how often each electrode is picked |
| M4 | 5 region means | coarse topography |
| M5 | ROI primary metric + gamma power above 1/f, aperiodic exponent, alpha peak frequency, theta/alpha ratio, EMG index | instability alongside the measures it must beat |
| M6 | M2 electrodes + the M5 spectral measures, elastic net | combined model |

For each model:

- **P1.** 5-fold × 50 repeated nested CV AUC. Full-pipeline permutation p (1,000 for M2, 200 for the others), with selection and tuning re-run inside every permutation. Also: how often each feature was selected, and the final model's standardised coefficients.
- **P2.** Incremental value over base [age, sex, theta/alpha ratio, alpha peak frequency, aperiodic exponent, gamma power above 1/f, relative gamma], on identical splits.
- **P3.** MMSE within AD: nested ridge regression R², base vs base + model. Descriptive only (n = 36).
- **P4.** After freezing, M2 is refitted on all AD + CN subjects and sent unchanged to the lockbox cohorts.

Only M2 is confirmatory; M1 and M3–M6 are secondary and reported as such. With 65 subjects, about 5–10 correlated predictors is the practical ceiling even with regularisation. More electrodes or features than that means more variance, not more signal.

## 8. External, reliability and normative analyses

- **E1. Replication.** Same model as H1 in each lockbox cohort, one-sided (AD > CN), α = .05. *Replication = correct direction and p < .05.* With several lockboxes, also report a random-effects meta-analysis of g across all cohorts.
- **E2. Frozen-model discrimination.** AUC with DeLong 95% CI. Success = lower CI bound > 0.5.
- **E3. Calibration.** Intercept and slope (descriptive).
- **E4. Continuum** (cohorts with MCI). Ordered trend CN < MCI < AD.
- **E5. Cognition.** Partial Spearman with MMSE or MoCA within patients.
- **R1. Test–retest.** ICC(2,1) between sessions (ds004148). Pre-stated benchmark: ICC ≥ 0.60 counts as acceptable for a group-level marker.
- **R2. Split-half.** ICC(2,1) between the first and second 120 s, with Spearman–Brown correction, in every cohort.
- **N1. Normative ageing** (LEMON, plus CN from all cohorts). Age slope of the metric in healthy adults. Each AD patient is expressed as a z-deviation from the age-expected value. Test whether AD deviation exceeds what age explains.

## 9. Label-blind observation that shapes the plan

On four ds004504 recordings (engineering check, labels not opened), the raw spectrum from about 25 Hz up to about 130 Hz is nearly flat, and temporal and frontopolar channels sit higher than posterior ones. That is the signature of broadband EMG and/or the amplifier noise floor, not neural 1/f activity. On one subject after cleaning, posterior gamma showed no power above the 1/f fit, and its IF spread matched spectrum-matched surrogates (if_sd_z ≈ 0).

Running the full v2 Stage A on four recordings (sub-015, sub-047, sub-050, sub-075; labels not opened) gave:

- posterior gamma power above the 1/f fit ≈ 0 in all four (−0.025 to −0.001 log units);
- no gamma spectral peak (the "peaks" found sit at 25–28 Hz, the beta edge);
- surrogate-normalised IF metrics within ±1 SD of spectrum-matched noise;
- the provisional primary metric (`burst_freq_sd`) higher in the two recordings with the strongest EMG signature (flatter 30–90 Hz slope, −0.66 / −0.80, vs −1.6 / −1.5 in the other two).

Runtime was about 2 min per subject on one core (20 surrogates + split-half).

**Implication:** muscle control (rules in §5, H3, the derivatives analysis) is not optional. A null result after these controls is a legitimate, publishable outcome and is reported as such.

**Simulation finding (Stage 0, preliminary).** The v1-style statistic (`legacy_std`) barely changes as true jitter goes from 0 to 4 Hz (≈ 5.40 → 5.52). It falls by ≈ 1.2 Hz when bursts lengthen from 0.1 to 1 s, and it also moves with gamma amplitude and the 1/f exponent. v1 reported a 1.6 Hz AD–CN difference, which is far larger than any jitter effect in the simulations. That difference therefore most likely reflects burstiness, SNR or spectral shape, not frequency instability. v2 must test this directly (H3), and the paper should say so.

With the uncalibrated base signal, the pre-specified rule currently selects **`burst_freq_sd`**: the dispersion of mean frequency across gamma bursts. Its jitter effect is 8.9 SD; its largest nuisance effect is EMG at 7.5 SD. The runner-up, `burst_freq_sd_z` (surrogate-normalised), is about 3.6× less EMG-sensitive (2.1 vs 7.5) but more sensitive to the 1/f slope. The selection is re-run after label-free calibration (`02b`). Whichever metric wins, the EMG covariate and the derivatives analysis stay mandatory. `results/simulation/sim_sweeps.png` is a candidate Figure 1.

## 9b. Method ablations (decided before labels)

Every implementation step with more than one defensible tool is an ablation dimension
(`ablations.stage_a` in the config; rationale and sources in docs/METHODS_REVIEW.md):

| Dimension | Options (primary first) | Decided by |
|---|---|---|
| Reference | average, CSD (surface Laplacian) — chosen, REST | split-half ICC ≥ 0.6, then least EMG coupling |
| Muscle removal | none, BSS-CCA + spectral slope | same |
| Epoch rejection | MAD rules, autoreject | same |
| Aperiodic fit | specparam 3–30 Hz, IRASA | same, judged on the aperiodic exponent |
| IF estimator | Hilbert, synchrosqueezed CWT, VMD (fixed K, α) | simulation jitter-specificity score, then ICC |
| IF median filter | multi-window (Cohen 2014), single 20 ms | same |

No option is chosen by group separation. Labels are never read by 10_run_ablations.py or
11_select_methods.py (enforced by tests). The chosen options are written into the config before
03_freeze.py, so the frozen hash covers them.

After unblinding, H1 is re-estimated on all 3 × 2 × 3 × 2 = 36 combinations of reference, muscle,
estimator and median filter (12_specification_curve.py). The curve and a joint permutation test
(same label permutation across all specifications) are reported as robustness evidence; they never
change the primary pipeline.

The interpretable classifier family is chosen in the inner CV loop among LR-L2, elastic-net LR,
linear SVM and an explainable boosting machine. TabPFN and a Riemannian tangent-space model on the
gamma-band covariance are run as ceilings only (09_ceiling_check.py). If they beat the interpretable
model by less than the spread of repeated-CV AUCs, the interpretable model is reported as costing
nothing; if they beat it clearly, that gap is reported as a limitation.

## 9c. Mechanisms (docs/MECHANISMS.md)

Six candidate mechanisms (weaker synapses onto PV cells, Nav1.1 PV output failure, erratic amyloid
drive, cholinergic loss, SST interneuron loss, tau-driven silencing) are tested in three layers, all
fixed before unblinding: (1) an oscillation-presence gate; (2) 16 pre-registered tests (M01-M16; M17 dropped, see §3) with
verbal predictions per theory, equivalence tests for "no difference" predictions, Holm across tests;
(3) a comparison of the AD effect pattern with mechanistic fingerprints from two simulator families,
with identifiability checked at our sample size and across families. Mechanistic conclusions are
limited to "local PV-pyramidal loop vs external input" unless the identifiability checks allow more.

## 10. Reporting

- STARD 2015 for diagnostic-accuracy parts.
- TRIPOD+AI for prediction.
- The ds004504 "AHEPA benchmark" reporting checklist (Cognitive Neurodynamics 2026) for anything on this dataset.
- Publish `registry/freeze.json`, `registry/access_ledger.jsonl`, the simulation outputs and all code.
- Report every exclusion and every deviation from this plan, with dates.

## 11. Open items

1. **Hospital cohort.** The folder `mask_unmask_preprocessed_data` holds 59-channel × 308-sample epoched task data (masked/unmasked × familiar/famous/unfamiliar conditions, from 2021), with no diagnosis labels, sampling rate or channel names. It does not look like resting-state AD data. Confirm what it is; the hospital cohort needs raw resting EEG with labels and metadata.
2. ds004504 is split across Drive parts. Run `01_extract_features.py` and check `inventory.csv` for all 88 subjects.
3. Download ds006036, ds004148, LEMON, ds007427, ds005048, PEARL-Neuro and ds005385. Request CAUEEG (ethics approval needed) and raw BrainLat. ADFSU is excluded (filtered at 30 Hz). Full survey: NeuroHertz_dataset_survey.pdf.
4. Calibrate the simulation base signal on pooled, label-free descriptives. Re-run Stage 0, run the method ablations (§9b), then freeze.

## 12. Paper 1 outline (Clinical Neurophysiology)

1. Simulations: what IF-variability metrics really measure (legacy vs selected metric).
2. Discovery: H1–H4 and topography, with the muscle and spectral controls.
3. Reliability (split-half and test–retest) and normative ageing.
4. Lockbox replication (E1–E5) and meta-analysis across cohorts.
5. Prediction as secondary evidence (P1–P2).

**Paper 2 (higher scope, if paper 1 holds):** severity and continuum (CAUEEG, hospital), longitudinal change, specificity across disorders (BrainLat), and a biophysical (PING / neural-mass) model fitted per subject, to give an interneuron-integrity readout.
