# H11 · The posterior 32–40 Hz excess in AD is not an artefact of fitting one 1/f background over 2–48 Hz

**Hypothesis.** The AD > CN excess at about 32–40 Hz over P3/P4/Pz (H8, H9, H10) remains when the background is estimated locally around 25–47 Hz, so it is not produced by fitting a single aperiodic curve to spectra whose low end is reshaped by slowing.
**Rival.** The excess is a fitting artefact. A steeper AD spectrum, bent by excess theta, leaves a positive residual at 30–40 Hz when one curve is fitted from 2 to 48 Hz.
**Type.** Exploratory (ds004504 labels open). The decision rule was written in the script header, and the script's SHA-256 was recorded **before** the 88 spectra were loaded (`results/prereg_hash_before_data.txt`; the hash in `verdict.json` matches).
**When / where.** Cloud, 16 Nov 2026, from the per-subject spectra of stage 10 (copied from the laptop).

**What was run.**
- **Spectra:** per-subject 0.5-Hz CSD spectra, from all clean epochs and from the lowest-EMG 25% of epochs.
- **Sites:**
    - PRIMARY: the average of P3, P4 and Pz;
    - also P3, P4 and Pz separately, and the pre-registered ROI (P3 Pz P4 O1 O2).
- **Four measures of the 32–40 Hz level** (mean over 32–40 Hz of log power minus a background estimate):

| Measure | Background removed |
|---|---|
| M0 raw | none |
| M1 flank line | straight line in log–log fitted only to 24–30 and 42–47 Hz |
| M2 local fit | specparam, fixed aperiodic, fitted over 25–47 Hz only |
| M3 global fit | specparam, knee aperiodic, 2–48 Hz (the method under suspicion) |

- **Test:** AD vs CN (and FTD vs CN), Freedman–Lane permutation (5000), covariates L0 age + sex and L1 + theta/alpha; Hedges g.
- **Decision rule (fixed beforehand; all epochs, PRIMARY, L0):**
    - SURVIVES if M1 and M2 both show AD > CN with p < 0.05;
    - DIES if both p ≥ 0.2, or both g ≤ 0.2, or either shows AD < CN;
    - otherwise OPEN.
- The lowest-EMG spectra and L1 are reported but do not change the verdict.

**Command.** `python explore/02_local_aperiodic_check.py --feat-dir <cache/ds004504/main/feat> --participants <ds004504 participants.tsv> --subject-table <results/ds004504/main/subject_table.csv> --out <dir>` (with `NH_CODE` pointing to the frozen code, for specparam)
**Code.** `../../code/classification_sweep/explore/02_local_aperiodic_check.py`

| Output in `results/` | Content |
|---|---|
| `verdict.json` | Verdict, the two deciding tests, script hash |
| `group_tests.csv` | Every contrast × spectrum × site × measure × covariate set: t, permutation p, Hedges g |
| `subject_measures.csv` | The four measures per subject, spectrum and site |
| `prereg_hash_before_data.txt` | Script hash recorded before the data were loaded |
