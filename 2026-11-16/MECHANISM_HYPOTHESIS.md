# The mechanistic hypothesis and its evidence chain

This file states the hypothesis that the mechanism work (H12–H17) is testing. It splits the hypothesis into biological steps, and gives each step the evidence modules that bear on it.
- Every module names its level, its modality, what it shows, and where it lives (a run folder here, or a literature item still to be verified).
- Modules are independent: each can be replaced or added to without touching the others.

## The hypothesis (H\*)

> **In posterior association cortex, tau-linked loss of superficial (layer 2/3) excitatory pyramidal neurons reduces the excitatory drive of the local circuit.**
>
> Lower drive weakens the circuit's beta-band (~17 Hz) resonance. This produces three things in resting scalp EEG over P3/P4/Pz:
> 1. loss of posterior beta;
> 2. a flatter 24–47 Hz spectrum;
> 3. a 32–40 Hz band that keeps its absolute level and so stands out above its surroundings.
>
> The fast (PV-type) gamma loop is not the site of the change.

**Rivals kept in play:**

| Rival | Claim | Status |
|---|---|---|
| R1 | slow (SST-type, dendritic) inhibition is lost | reproduces the EEG; rejected posteriorly by tissue (S2) |
| R2 | excitation up, e.g. amyloid-driven hyperexcitability or disinhibition | rejected by the circuit model (S4) |
| R3 | non-neural: muscle, medication, vigilance | partly addressed (S5) |

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
| | | E1.3 | L4 | literature MEG/EEG | flatter 15–50 Hz posterior slope in AD; flatter 30–48 Hz exponent in AD | Ranasinghe 2025 *Nat Commun*; van Nifterick 2023 *Sci Rep* | **to verify** wording; direction matches |
| **S2** | The posterior neurons that decline with AD are L2/3 excitatory, not SST/PV inhibitory | E2.1 | L2 | snRNA-seq, SEA-AD | AnG L2/3 IT ρ = −0.46 (p = 0.002), share 0.73 at high pathology; SST, PV flat | `bio_tests/H15` | **supported** (shares, n = 43) |
| | | E2.2 | L2 | snRNA-seq | positive control: SST loss found in MTG (published) | `bio_tests/H15` | **supported** |
| | | E2.3 | L2 | literature | L2/3 IT and SST vulnerability in MTG | Gabitto et al. 2024 *Nat Neurosci* (SEA-AD) | **to verify** |
| **S3** | The L2/3 loss is tau-linked | E3.1 | L1→L2 | snRNA-seq + quantitative neuropathology | partial ρ with pTau −0.37 (AnG), −0.46 (MTG), −0.35 (DFC); with Aβ ≈ 0 | `bio_tests/H15` | supported (Aβ–pTau collinearity 0.6–0.7) |
| | | E3.2 | L1→L3 | literature | tau associated with neuronal silencing / hypoactivity | Busche et al. 2019 *Nat Neurosci* | **to verify** |
| | | E3.3 | L1→L4 | literature MEG + PET | tau tracks the excitability measure (aperiodic slope) | Ranasinghe 2025 | **to verify** |
| **S4** | Lower excitatory drive in a calibrated circuit produces the S1 phenotype; excitation-up does not | E4.1 | L3→L4 | circuit model (12 calibrations) | gain ↓ and slow-loop ↓ fit (χ² 0.6–8.2); M2/M3/M5+ fail (χ² 15–24) | `bio_tests/H13` | **supported** (model-dependent) |
| | | E4.2 | L3 | literature | cortical beta driven by superficial-layer input | Sherman et al. 2016 *PNAS* | **to verify** |
| **S5** | The tissue-measured loss predicts the EEG, with nothing fitted | E5.1 | L2→L4 | tissue → circuit → EEG | right signs in 99% of draws; about half the magnitude; χ² 24.5 → 12.3 | `bio_tests/H16` | **supported** (magnitude partial) |
| **S6** | Rest alone cannot identify the mechanism; multimodal + non-commuting probes can | E6.1 | L4 | Fisher / injectivity | REST: 5 signatures for 8 mechanisms, about 2–3 effective dimensions | `bio_tests/H17`, `P12` | **supported** (theory) |
| | | E6.2 | L2+L4 | injectivity | REST+PHOTIC+TISSUE: 7 signatures for 8 mechanisms; the remaining collision is between two rejected mechanisms | `bio_tests/H17` | supported |
| | | E6.3 | L5 | probe-order Fisher | rest → 40 Hz → rest + tissue: all three survivors estimable; order changes information (Δ log det up to 0.6) | `bio_tests/H17` | design-level (α assumed) |
| **S7** | A shared transfer function governs rest and drive | E7.1 | L5 | photic, same people | driven power lower in AD at 10/20 Hz with SNR unchanged; rest–drive ρ ≈ 0.2 | `bio_tests/H14` | weakly supported |
| **S8** | Non-neural explanations are excluded | E8.1 | L4 | EEG controls | EMG sentinel, harmonics, transients, ocular sources | H8, H9, H11 | partly: muscle not excluded at the lowest-EMG quartile |
| | | E8.2 | — | data integrity | ds006036 header bug found and corrected | `pipeline_validation/P13` | done |
| | | E8.3 | — | medication | not recorded in ds004504 | — | **open** |

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

## Open items (in order)
1. **Verify the literature modules** E1.3, E2.3, E3.2, E3.3 and E4.2.
2. **F5:** a second circuit family.
3. **F2:** absolute densities from SEA-AD spatial data.
4. **External EEG replication** of S1 in a second AD cohort.
5. **F1:** access to paired EEG + PET.
