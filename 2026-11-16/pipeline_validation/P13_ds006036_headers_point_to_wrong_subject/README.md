# P13 · ds006036: 63 of 65 EEGLAB headers point to another subject's data file

**Question.** When the photic-stimulation recordings (ds006036, same 88 people as ds004504) are loaded with MNE, does each subject get their own EEG?
**Type.** Pipeline validation (data integrity). No labels involved.
**When / where.** Cloud, 16 Nov 2026.

**What was run.**
- **Header check:** for each AD/CN `.set` file, read the header field that names the data file (`EEG.data`) and the header sample count (`pnts`).
- **Data check:** compare both with the subject's own `.fdt` file.

**Command.** One-off script, inline in the session; its output is `results/header_check.csv`.

| Output in `results/` | Content |
|---|---|
| `P13_header_check.csv` | Subject, file the header points to, header samples, samples in the subject's own `.fdt`, match |
