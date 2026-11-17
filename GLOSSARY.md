# Glossary (plain English)

**EEG terms**
- **Frequency band**: a range of rhythm speeds. Delta 1–4 Hz, theta 4–8 Hz, alpha 8–13 Hz, beta 13–30 Hz, gamma 30–45 Hz here (Hz = cycles per second).
- **Gamma oscillation**: a fast rhythm thought to depend on PV (parvalbumin) inhibitory interneurons. Its loss or instability in AD is the starting hypothesis of NeuroHertz.
- **Instability / frequency instability**: how much a rhythm's speed wobbles over time instead of staying at one frequency. Measured as the spread of the instantaneous frequency, the variability between bursts, phase slips, and so on.
- **Instantaneous frequency (IF)**: the rhythm's speed at each moment, from the Hilbert transform (or SST/VMD, which are alternative estimators).
- **Burst**: a short stretch where a rhythm stands out above the background.
- **Power spectrum**: how much signal power sits at each frequency.
- **1/f background (aperiodic part, exponent)**: the smooth decline of power with frequency that is not a rhythm. Its slope (the exponent) is proposed as a marker of excitation/inhibition balance.
- **Periodic part**: the rhythmic peaks that stand above the 1/f background.
- **specparam / IRASA**: two methods that split a spectrum into its periodic and aperiodic parts.
- **Slowing**: the classic EEG change in AD, where power shifts from alpha to theta/delta. Measured as the theta/alpha ratio or the individual alpha frequency (IAF).
- **CSD (current source density) / REST / average reference**: ways of re-referencing EEG. CSD sharpens the spatial picture and reduces volume conduction.
- **EMG**: muscle activity, which contaminates high frequencies (above about 20 Hz) on scalp EEG.
- **BSS-CCA / ICA / autoreject**: methods that remove muscle, eye and other artifacts.
- **ROI**: region of interest. Here the pre-registered posterior electrodes P3, Pz, P4, O1, O2.
- **PAC (phase–amplitude coupling)**: whether a fast rhythm's strength follows the phase of a slower one.
- **Surrogate**: a scrambled copy of a signal that keeps its power spectrum but destroys everything else. Used as a "what chance alone gives" reference.

**Statistics terms**
- **Hedges g**: the size of a group difference in standard deviations; 0.2 small, 0.5 medium, 0.8 large (conventional labels).
- **p-value / permutation p**: how often a difference this large would appear if group labels were random. Permutation p's are computed by shuffling the labels thousands of times.
- **Freedman–Lane**: a permutation method that respects covariates (age, sex, …).
- **FWER / maxT / Holm / FDR**: corrections for running many tests, so that the overall chance of any false positive (FWER) or the expected share of false positives (FDR) stays controlled.
- **Cluster permutation test**: tests a whole frequency × electrode map at once and reports connected regions that differ.
- **ICC (intraclass correlation)**: reliability of a measure, 0–1. Split-half ICC compares the first and second half of each recording; Spearman–Brown corrects it to the full recording length.
- **AUC**: how well a score separates two groups. 0.5 = chance, 1.0 = perfect.
- **Balanced accuracy**: the average of sensitivity and specificity.
- **Nested cross-validation**: model choices are made only on training data inside each fold, so the test data never influences the model (no leakage).
- **Positive control**: data where the true answer is known in advance. The method must find it.
- **Pre-registration / freeze**: fixing the hypotheses, code and decision rules (and recording their hashes) before looking at diagnoses.
- **Confirmatory / exploratory**: confirmatory = a pre-specified test on unseen labels; exploratory = analyses chosen after seeing data.
- **CSD (current source density)**: a spatial filter that sharpens each electrode toward local sources.
- **Flank-line bump**: 32–40 Hz log power minus a straight line in log–log fitted through 24–30 and 42–47 Hz (H11, H12).
- **Transfer function H(f)**: how strongly a circuit responds at each frequency. Spontaneous and driven activity share it in a linear model.
- **L2/3 IT neurons**: excitatory pyramidal neurons in superficial cortical layers that project within the cortex. SST, PV (Pvalb): two classes of inhibitory interneuron.
- **SEA-AD / CPS**: Seattle Alzheimer's Disease Brain Cell Atlas; CPS is its continuous score of how far each donor's pathology has progressed, per region.
- **Injective map**: different inputs give different outputs. Here: different mechanisms give different signatures across the characterizations.
- **Non-commuting probes**: measurements that change the state being measured, so their order changes what is learned.
- **Readout-schedule term**: the part of an order effect that appears even when probes commute, because each probe is read at a different accumulated state. It must be subtracted before an order effect is called non-commutativity (P14).
- **Bracket term**: the part of an order effect caused by non-commutativity. To leading order it is the θ-derivative of the Lie bracket of the two probes' state updates.
