# The mechanistic hypothesis and its evidence chain

This file states the hypothesis that the mechanism work (H12–H17) is testing. It splits the hypothesis into biological steps, and gives each step the evidence modules that bear on it.
- Every module names its level, its modality, what it shows, and where it lives (a run folder here, or a literature item still to be verified).
- Modules are independent: each can be replaced or added to without touching the others.

## The hypothesis (H\*)

> **In posterior association cortex, tau-linked loss of superficial-layer neurons weakens the local circuit's beta-band (~17 Hz) resonance.**
>
> The neurons lost are layer 2/3 IT excitatory pyramids and specific superficial Sst inhibitory supertypes (revised 17 Nov after H19). Lower excitatory drive and weaker slow (dendritic) inhibition together produce three things in resting scalp EEG over P3/P4/Pz:
> 1. loss of posterior oscillatory beta;
> 2. a flatter 24–47 Hz neural spectrum;
> 3. a 32–40 Hz band that keeps its absolute level and so stands out above its surroundings.
>
> The fast (PV-type) gamma loop is not the site of the change.

**Rivals kept in play:**

| Rival | Claim | Status |
|---|---|---|
| R1 | slow (SST-type, dendritic) inhibition is lost, *on its own* | reproduces the EEG alone (H13). Tissue: the vulnerable superficial Sst supertypes do decline in AnG (H19). R1 is **absorbed into H\*** as one of its two components. Sst alone (χ² 8.1) fits worse than combined (4.1) |
| R2 | excitation up, e.g. amyloid-driven hyperexcitability or disinhibition | rejected by the circuit model (S4) |
| R3 | non-neural: muscle, medication, vigilance | constant floor **rejected** (H18). Muscle at the lowest-EMG quartile, vigilance-dependent floor and medication still open |

## Levels

| Level | What it describes |
|---|---|
| L1 molecular | tau, amyloid |
| L2 cellular | which neurons change |
| L3 circuit | gain, inhibition, resonance |
| L4 field | scalp EEG features Φ |
| L5 perturbation | driven responses, probe sequences |

## The chain: step → evidence modules

| Step | Claim | Module | Level | Modality | What it shows | Where | Status |
|---|---|---|---|---|---|---|---|
| **S1** | The posterior EEG phenotype is beta loss + flattening + relatively preserved 32–40 Hz | E1.1 | L4 | resting EEG, 3 pipelines | beta g ≈ −0.95; slope flatter g = 0.7–1.0 in every pipeline; absolute 32–40 Hz unchanged | `bio_tests/H12` | **supported** (single cohort) |
| | | E1.2 | L4 | resting EEG | the bump survives local-background removal | `bio_tests/H11` | supported, pipeline-dependent |
| | | E1.3 | L4 | literature MEG | flatter 15–50 Hz slope, posterior temporoparietal, tracks tau PET independent of amyloid (82 AD, 40 CN); flatter 30–48 Hz parieto-occipital exponent and lower 14–32 Hz power in AD dementia (51 AD) | Ranasinghe 2025 *Nat Commun* 16:7957; van Nifterick 2023 *Sci Rep* 13:7419 | **verified**. Both read flattening as *more excitation*; H\* explains it as loss of the beta shoulder plus lower neural amplitude (H13, H18) |
| | | E1.4 | L4 | literature EEG | AD spectral changes are periodic (alpha/beta loss), aperiodic unchanged over 3–40 Hz (two cohorts) | Kopčanová 2024 *Neurobiol Dis* | verified; supports beta loss as oscillatory |
| | | E1.5 | L4 | literature, same dataset | ds004504 gives a **steeper** 2–40 Hz exponent in AD | Wang 2024 | verified: sign depends on fit range. Broadband fits include slowing; 24–47 Hz does not |
| | | E1.6 | L4 | resting EEG, floor model | neural exponent flatter after a per-subject floor is modelled; floor identical | `2026-11-17/bio_tests/H18` | **supported**. FTD shows the same flattening, so it is not AD-specific |
| **S2** | The posterior neurons that decline with AD are L2/3 excitatory, not SST/PV inhibitory | E2.1 | L2 | snRNA-seq, SEA-AD | AnG L2/3 IT ρ = −0.46 (p = 0.002), share 0.73 at high pathology; SST, PV flat | `bio_tests/H15` | **supported** (shares, n = 43) |
| | | E2.2 | L2 | snRNA-seq | positive control: SST loss found in MTG (published) | `bio_tests/H15` | **supported** |
| | | E2.3 | L2 | literature | MTG (84 donors): early loss of superficial Sst supertypes; later L2/3 IT and Pvalb; L2/3 IT carry the highest tau burden | Gabitto 2024 *Nat Neurosci* 27:2366 | **verified** (MTG/DLPFC only); multiregion preprint 2026 reports L2/3 IT as the most consistently affected excitatory type and the same Sst types lost across regions |
| | | E2.4 | L2 | snRNA-seq, supertype level | MTG-vulnerable Sst set declines in AnG (ρ −0.29, p 0.06; Sst_23 −0.45) | `2026-11-17/bio_tests/H19` | supported, marginal |
| | | E2.5 | L2 | literature, histology | layer III/V long-projection pyramids lost in association cortex, loss tracks tangles | Hof & Morrison 1990 | verified (older); not purely supragranular |
| **S3** | The L2/3 loss is tau-linked | E3.1 | L1→L2 | snRNA-seq + quantitative neuropathology | partial ρ with pTau −0.37 (AnG), −0.46 (MTG), −0.35 (DFC); with Aβ ≈ 0 | `bio_tests/H15` | supported (Aβ–pTau collinearity 0.6–0.7) |
| | | E3.2 | L1→L3 | literature, mouse | tau makes 53–63% of cortical neurons silent and overrides amyloid-driven hyperactivity | Busche 2019 *Nat Neurosci* 22:57 | **verified**; this is functional silencing, not cell loss |
| | | E3.4 | L1→L4 | literature EEG + PET | tau and amyloid **both** associated with lower beta (AD-MCI, 36); amyloid predicts beta decline in unimpaired adults | Cheng 2026 *Alz Res Ther*; *Brain Commun* 2025 | mixed: the beta link is not tau-specific |
| | | E3.3 | L1→L4 | literature MEG + PET | regional tau predicts slope flattening (F = 49, survives amyloid adjustment) | Ranasinghe 2025 | **verified** |
| **S4** | Lower excitatory drive in a calibrated circuit produces the S1 phenotype; excitation-up does not | E4.1 | L3→L4 | circuit model (12 calibrations) | gain ↓ and slow-loop ↓ fit (χ² 0.6–8.2); M2/M3/M5+ fail (χ² 15–24) | `bio_tests/H13` | **supported** (model-dependent) |
| | | E4.2 | L3 | literature, model + MEG | beta events need a strong ~50 ms distal (supragranular) drive coinciding with proximal drive; stronger drive gives more beta | Sherman 2016 *PNAS* 113:E4885 | **verified**. The drive is extrinsic (likely higher-order thalamus) onto L2/3–L5 dendrites; L2/3 loss shrinks the generator, not the drive |
| | | E4.3 | L3 | literature, mouse V1 | SOM (SST) spiking tracks beta, PV tracks gamma; silencing SOM reduces <30 Hz power | Chen 2017 *Neuron* | verified; supports the Sst component of H\* and the separable PV gamma loop |
| | | E4.4 | L3 | literature | Gao 2017: reduced excitation **steepens** the 30–50 Hz LFP slope | Gao 2017 *NeuroImage* | **conflicts** with reading the flattening as an aperiodic E/I change. H\*'s flattening comes from losing the beta shoulder and neural amplitude, not from E/I rotation (H13, H18) |
| **S5** | The tissue-measured loss predicts the EEG, with nothing fitted | E5.1 | L2→L4 | tissue → circuit → EEG | L2/3 only: right signs 99%, about half the size, χ² 24.5 → 12.3 | `bio_tests/H16` | supported (partial) |
| | | E5.2 | L2→L4 | tissue → circuit → EEG | L2/3 IT + vulnerable Sst: χ² 4.1, signs 100%, beta 78% and slope 90% of the observed effect | `2026-11-17/bio_tests/H19` | **supported** |
| **S6** | Rest alone cannot identify the mechanism; multimodal + non-commuting probes can | E6.1 | L4 | Fisher / injectivity | REST: 5 signatures for 8 mechanisms, about 2–3 effective dimensions | `bio_tests/H17`, `P12` | **supported** (theory) |
| | | E6.2 | L2+L4 | injectivity | REST+PHOTIC+TISSUE: 7 signatures for 8 mechanisms; the remaining collision is between two rejected mechanisms | `bio_tests/H17` | supported |
| | | E6.3 | L5 | probe-order Fisher | rest → 40 Hz → rest + tissue: all three survivors estimable; order changes information (Δ log det up to 0.6) | `bio_tests/H17` | design-level (α assumed) |
| **S7** | A shared transfer function governs rest and drive | E7.1 | L5 | photic, same people | driven power lower in AD at 10/20 Hz with SNR unchanged; rest–drive ρ ≈ 0.2 | `bio_tests/H14` | weakly supported |
| **S8** | Non-neural explanations are excluded | E8.1 | L4 | EEG controls | EMG sentinel, harmonics, transients, ocular sources | H8, H9, H11 | partly: muscle not excluded at the lowest-EMG quartile |
| | | E8.2 | — | data integrity | ds006036 header bug found and corrected | `pipeline_validation/P13` | done |
| | | E8.3 | — | medication | not recorded in ds004504 | — | **open** |
| | | E8.4 | L4 | noise floor | constant floor identical between groups | `2026-11-17/bio_tests/H18` | rejected as an explanation |
| | | E8.5 | L5 | literature, pharmacology | levetiracetam raises beta coherence in AD | Musaeus 2017 | weakly favours R2. H\* predicts no beta restoration: a test for existing LEV trial EEG |

## What would falsify H\*

| ID | Test | H\* fails if |
|---|---|---|
| F1 | Paired EEG + tau PET (GARD-type) | posterior beta loss / flattening is **not** associated with parietal tau, or is associated with amyloid instead |
| F2 | Absolute neuron densities (SEA-AD spatial / MERFISH) | there is no absolute L2/3 loss in AnG, or there is SST loss there |
| F3 | Probe sequence rest → 40 Hz → rest, with longer blocks | the order effect predicted for gain loss vs slow-loop loss (H17) is absent, or goes the opposite way |
| F4 | Lowest-EMG data / paralysis-controlled recording | the flattening disappears |
| F5 | Second circuit family (e.g. neural mass with alpha) | it reverses the H13 ranking |

## The injectivity statement

Let B be the candidate mechanisms and Φ the characterizations, from any modality. Each b ∈ B maps to a signature s(b) ∈ {−1, 0, +1}^|Φ|: the predicted change at matched effect size, coded against a 2-SE threshold.

| Characterization set | Distinct signatures (8 mechanisms) | Injective? | Source |
|---|---|---|---|
| Φ_rest | 5 | no | H17 |
| Φ_rest ∪ Φ_photic ∪ Φ_tissue | 7 | almost; the remaining collision is between two excitation-up mechanisms that the data reject anyway | H17 |
| plus a non-commuting probe sequence | the three data-compatible mechanisms become separately estimable | — | H17 |

Over the mechanisms that the data allow, the multimodal map is injective; the resting-EEG map is not.

## Literature check (17 Nov)
A research pass verified the five literature modules marked "to verify" and added E1.4–E1.5, E2.4–E2.5, E3.4, E4.3–E4.4 and E8.5. Three corrections followed:
1. **Slope framing.** The cited MEG studies read the same flattening as *more* excitation, and Gao 2017 predicts reduced excitation steepens the slope. H\* does not claim an aperiodic E/I rotation. It claims loss of beta generators and neural amplitude over a stable floor (H13, H18).
2. **R1.** Sst loss at supertype level is present in AnG (H19). It is now part of H\*.
3. **Tau specificity.** Beta loss also tracks amyloid in other cohorts (E3.4). The tau claim rests on SEA-AD (E3.1) and Ranasinghe's slope–tau link (E3.3).

## Open items (in order)
1. **Tau link at supertype level:** check whether vulnerable-Sst loss in AnG tracks pTau or Aβ.
2. **F5:** a second circuit family, including whether it also gets the flattening from beta-shoulder loss.
3. **Paired data:** request UCSF (MEG + flortaucipir, Ranasinghe) or Amsterdam Dementia Cohort (MEG + tau PET).
4. **Levetiracetam test:** H\* predicts LEV does not restore beta; R2 predicts it does.
5. **F2:** absolute densities from SEA-AD spatial data.
6. **External EEG replication** of S1 in a second AD cohort.
