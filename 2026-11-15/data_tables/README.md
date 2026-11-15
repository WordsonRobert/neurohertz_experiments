# Data tables

| File | Rows | What it contains |
|---|---|---|
| `ds004504_features_per_subject.csv` | 88 subjects | Every feature from the frozen pipeline (final run). Columns are `<region>__<metric>`; regions are `roi` (P3 Pz P4 O1 O2), `frontal`, `central`, `temporal`, `parietal`, `occipital`, `csd_roi`, `ftd_frontal`, `ad_temporoparietal`, plus `emg_sentinel`. `sh1_` / `sh2_` = first / second half of the recording |
| `ds004504_quality_control.csv` | 88 | Per-subject preprocessing record: bad channels, ICA and muscle components removed, epochs rejected, clean seconds (all 240 s), status |
| `ds006036_features_per_subject.csv` | 54 | The same features for the second session (flicker-free, eyes-closed stretches) |
| `ds006036_quality_control.csv` | 88 | 54 ok, 20 excluded (under 120 s clean or too many bad channels), 14 errors (too few epochs for autoreject) |
| `ds004504_participants.tsv` | 88 | participant_id, Gender, Age, Group (A = AD, C = CN, F = FTD), MMSE |
| `ds006036_participants.tsv` | 88 | The same table distributed with ds006036 (identical on all 88 rows) |

Metric names are defined in `code/neurohertz_v2_frozen/nh/gamma.py`, `nh/spectral.py`, `nh/oscfit.py` and `nh/dynamics.py`. The burst/instability metrics are listed at the top of `nh/gamma.py`.
