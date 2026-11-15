# What could make 30–48 Hz resting EEG differ in Alzheimer's? An elimination tree

**Status: EXPLORATORY.** ds004504 was unblinded on 2026-11-14 for the frozen confirmatory test, whose
pre-registered H1 (gamma frequency instability) was null. Everything in `classification/` therefore
generates hypotheses. A lead becomes a claim only after we freeze it and confirm it on a cohort that
was never looked at: the hospital data or the ds007427 lockbox.

## What the existing features already say (explore/01, 2026-11-15)

| Observation | Value | Meaning |
|---|---|---|
| Old metric (`legacy_std`, SD of IF in 25–80 Hz) re-computed with clean preprocessing | AUC 0.48 (CV) | The old 73.8% does not reproduce once preprocessing is clean. It came from the v1 processing (per-subject VMD K/alpha sweep, scale bug), not from the metric |
| Absolute 30–45 Hz power, AD vs CN | g = −0.26, n.s. | AD does **not** have more raw gamma power |
| 30–45 Hz power *above the 1/f fit* | g = +0.76 to +1.10 | Larger in AD, but … |
| … after adjusting for slowing (theta/alpha) | p = 0.05–0.17 | … it mostly follows the steeper 1/f spectrum and slowing |
| Muscle (55–90 Hz) AD vs CN | g = −0.04 to −0.29 | AD are not more tense. But muscle drives *individual differences* in absolute gamma (ρ = 0.68–0.79 within every group) |
| Topography of the above-1/f effect | parietal/occipital ≥ temporal ≥ frontal | Not the muscle pattern (muscle is largest at temporal/frontal edges) |
| 30–45 Hz peak frequency vs alpha frequency | ρ = −0.14; integer ratios 33% (≈ chance) | No sign of alpha harmonics |
| Anything vs MMSE within AD | \|ρ\| ≤ 0.21 | No severity link |
| Strongest separators | theta/alpha AUC 0.83; 1/f exponent AUC 0.77 | Slowing and the aperiodic slope carry the AD signal |

So there is no evidence for a 40 Hz-specific effect yet. The resolution was coarse, though: one 30–45 Hz
band, ROI averages, and no muscle-matched epochs. The raw-level sweep tests each explanation below at
1/2-Hz × channel resolution.

## The explanations and how each is tested

| # | Explanation | Biological meaning if true | Test in the sweep (script) | Eliminated if … |
|---|---|---|---|---|
| E1 | **Muscle (EMG)** contaminates 30–48 Hz (Whitham et al. 2007; Muthukumaraswamy 2013) | none (artifact) | (a) cache with and without BSS-CCA muscle removal; (b) spectra from the lowest-EMG half/quarter of each person's epochs; (c) EMG covariate; (d) burst EMG co-activation (10, 20, 30) | the group effect is unchanged in low-EMG epochs and without the muscle step, and bursts are not EMG-coupled |
| E2 | **Ocular / saccadic spike potentials** (broadband 20–100+ Hz transients at frontal-polar sites; Yuval-Greenberg et al. 2008) | none (artifact) | burst spatial location (Fp/F7/F8 vs posterior) and broadband index, by burst type (30) | effect-carrying bursts are posterior and narrowband |
| E3 | **Aperiodic (1/f) change**: steeper spectrum shifts every "above 1/f" measure; the exponent is proposed as an E/I proxy (Gao et al. 2017; Martínez-Cañada et al. 2023) | E/I balance shift (network-wide, not 40 Hz-specific) | IRASA split into fractal and periodic parts; specparam with a knee 2–48 Hz; cluster tests on each part (10, 20) | the periodic (oscillatory) part shows a 35–45 Hz difference that the fractal part does not explain |
| E4 | **Slowing / vigilance**: drowsier, slower EEG changes high frequencies | thalamocortical / cholinergic slowing, arousal | epoch-level vigilance (alpha/theta) matching: compare 30–48 Hz power within matched vigilance strata (10, 20) | the effect persists within vigilance-matched epochs |
| E5 | **Harmonics of a non-sinusoidal alpha** produce peaks at 3–4 × IAF (Cole & Voytek 2017) | waveform shape, not gamma | 1:4 n:m phase locking alpha→4·IAF with time-shift surrogates; IAF-scaled spectra (10) | no excess n:m locking; effect not at integer multiples of IAF |
| E6 | **Interictal-like sharp transients** (subclinical epileptiform activity in ~42% of AD on long-term EEG/MEG; Vossel et al. 2016) | hyperexcitability (PV / Nav1.1 failure in AD models; Verret et al. 2012) | sharp-transient detector (1–70 Hz); 30–48 Hz power with transient windows removed; burst sharpness (10, 30) | transients are not more frequent in AD and removing them changes nothing |
| E7 | **Line noise / filters / amplifier** (50 Hz notch, 70 Hz hardware low-pass in ds004504) | none (artifact) | cluster test runs to 48 Hz; checks whether the effect hugs the 45–50 Hz notch edge (20) | effect is not concentrated at the notch edge |
| E8 | **Medication** (cholinesterase inhibitors; benzodiazepines → beta/low-gamma "buzz" 15–30 Hz, frontocentral) | drug effect | cannot be tested (no medication list); signature check only: is the effect continuous with a frontocentral beta excess? (20) | never fully; reported as a limitation |
| E9 | **Neural gamma change** (PV-interneuron/E–I dysfunction; enhanced resting gamma reported in small samples, e.g. Wang et al. 2017; reduced gamma in others) | the hypothesis itself | a periodic, narrowband, posterior 35–45 Hz difference that survives E1–E8, carried by a specific burst type, ideally related to MMSE (20, 30, 40) | — this is what survives |

## Classifying the instabilities (30)

Every 30–48 Hz burst (amplitude above a phase-randomized surrogate threshold, ≥ 3 cycles) is described by
duration, mean frequency, within-burst frequency SD (instability at its most local), chirp, amplitude,
narrowband index, EMG co-activation, spatial spread, location, sharpness, and alpha/theta phase at
onset. Burst types are found **without labels** (Gaussian mixture, K by BIC, bootstrap stability).
Types are then named from their centroid profiles, e.g. "narrowband posterior oscillation",
"broadband frontal transient (ocular/muscle)" or "sharp spike-locked".

Only after that are labels used: rate of each burst type by group, and within-burst frequency SD by group
(mixed model, subject random intercept).

## Stratifying the patients (40)

Each patient's deviation from the controls (leave-one-out normative z-scores) is computed on the
mechanistic axes: periodic slowing, aperiodic slope/knee, periodic 35–45 Hz power, burst-type rates,
transients, PAC and EMG. Patients are clustered label-blind (AD vs FTD hidden). We then ask whether
the clusters match diagnosis or MMSE, and which axes drive each cluster.

## Prediction (50)

Nested CV by feature family: slowing, aperiodic, gamma-periodic, bursts, transients, PAC, EMG. Reported:
AUC, balanced accuracy, accuracy, permutation p, and incremental value over slowing + aperiodic. Every
data-driven step (burst-type model, normative z, scaling) is fit inside the training folds.

## References (verified where linked)

- Wang J. et al. (2017) Enhanced gamma activity and cross-frequency interaction of resting-state EEG in AD. *Front Aging Neurosci* 9:243. n = 8 AD vs 12 CN; no EMG or 1/f control. https://www.frontiersin.org/articles/10.3389/fnagi.2017.00243/full
- Vossel K.A. et al. (2016) Incidence and impact of subclinical epileptiform activity in AD. *Ann Neurol* 80:858–870. 42.4% AD vs 10.5% CN (long-term EEG/MEG). https://escholarship.org/uc/item/3zw468xg
- Martínez-Cañada P. et al. (2023) Combining aperiodic 1/f slopes and brain simulation: an EEG/MEG proxy marker of E/I imbalance in AD. *Alzheimer's Dement DADM* 15(3). https://doaj.org/article/09342bf9b57c4629ad8e8494a572f3b2
- Manippa V. et al. (2022) An update on gamma (multi)sensory stimulation for AD. *Front Aging Neurosci* 14:1095081. https://www.frontiersin.org/journals/aging-neuroscience/articles/10.3389/fnagi.2022.1095081/pdf
- Cole S.R., Voytek B. (2017) Brain oscillations and the importance of waveform shape. *Trends Cogn Sci*; and Cole et al. (2017) nonsinusoidal oscillations and spurious PAC, *eNeuro* 3(6). https://www.eneuro.org/content/3/6/ENEURO.0334-16.2016
- Goodman M.S. et al. (2018) Theta-gamma coupling and working memory in AD and MCI. *Front Aging Neurosci* 10:101. https://www.frontiersin.org/articles/10.3389/fnagi.2018.00101/full
- Muthukumaraswamy S.D. (2013) High-frequency brain activity and muscle artifacts in MEG/EEG. *Front Hum Neurosci* 7:138. https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00138/pdf
- Yuval-Greenberg S. et al. (2008) Transient induced gamma-band response in EEG as a manifestation of miniature saccades. *Neuron* 58:429–441 (cited from knowledge; not re-fetched).
- Whitham E.M. et al. (2007) Scalp electrical recording during paralysis. *Clin Neurophysiol* 118:1877–1888 (cited from knowledge; not re-fetched).
- Gao R., Peterson E.J., Voytek B. (2017) Inferring synaptic E/I balance from field potentials. *NeuroImage* 158:70–78 (cited from knowledge; not re-fetched).
- Verret L. et al. (2012) Inhibitory interneuron deficit links altered network activity and cognitive dysfunction in AD models. *Cell* 149:708–721 (cited from knowledge; not re-fetched).
