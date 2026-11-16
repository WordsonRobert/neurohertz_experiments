# Results · P13

## Main results
- **63 of 65** AD/CN headers name a **different subject's** `.fdt`. For example, `sub-001`'s header points to `sub-023`'s file.
- **65 of 65:** the subject's own `.fdt` length matches its own header `pnts`.
- MNE follows the header pointer. It either crashes, because the other subject's file has a different length, or it **silently loads the wrong person's EEG under this person's events**.
    - Loaded this way, flicker responses vanish: median SNR is −7 dB at every drive frequency, the level expected with no response.
    - Read from the subject's own `.fdt`, the responses are clear: 6 dB at 10–20 Hz.

## Consequences
- **Read path:** every ds006036 analysis here reads each subject's own `.fdt` directly (`code/mechanism/phaseC/photic.py`, `manual_read`).
- **ds004504 is unaffected.** Its data are embedded in the `.set` files.
- **Other users:** any published or shared analysis of ds006036 that used MNE or EEGLAB on these files may have mixed up subjects. Worth reporting to the dataset authors.
