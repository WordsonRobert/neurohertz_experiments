#!/usr/bin/env bash
# Frequency x electrode instability screen, 2-90 Hz (EXPLORATORY, post-freeze). Run from this folder:
#   cd /media/wordson22/Expansion/projects2/neurohertz2/classification && conda activate nh && bash run_freq_instability.sh
# Needs the caches of run_classification.sh (clean data, subject tables). Re-running is safe: finished subjects
# are cached. Stops at the first failing step; output is shown live and saved in logs/.
# Time on 8 cores (laptop, 2026-11-16): synthetic control 2.4 h (cached after the first run), real data ~5-6 h.
set -eo pipefail
cd "$(dirname "$0")"
J=${JOBS:-8}
export NH_CODE=${NH_CODE:-$PWD/../final_run/neurohertz_v2}
mkdir -p logs
step() { local name=$1; shift; echo; echo "================ $name  ($(date +%H:%M)) ================"; "$@" 2>&1 | tee "logs/$name.log"; }
[ -d "$NH_CODE/nh" ] || { echo "frozen code not found at $NH_CODE"; exit 1; }

step f00_tests            python -m pytest -q tests -p no:cacheprovider

# ---- positive control: the erratic-gamma-drive synthetic data left by run_classification.sh (control 2)
export NH_SYNTH="$PWD/cache/synth_dataset"
grep -q "erratic_drive" "$NH_SYNTH/GROUND_TRUTH.txt" || { echo "synthetic cache is not the erratic_drive control; re-run run_classification.sh steps c10-c13"; exit 1; }
step f01_synth_freqinst   python sweep/13_freq_instability.py --dataset synthetic --jobs "$J" --k-surr 4
step f02_synth_analysis   python sweep/57_freq_instability_analysis.py --dataset synthetic --n-perm 2000 --n-perm-cv 50 --n-rep 10
step f03_synth_check      python sweep/check_freqinst_control.py

# ---- ds004504 (already unblinded; EXPLORATORY)
step f10_freqinst_main    python sweep/13_freq_instability.py --dataset ds004504 --variant main --jobs "$J" --k-surr 10
step f11_analysis_main    python sweep/57_freq_instability_analysis.py --dataset ds004504 --variant main --n-perm 5000
echo; echo "ALL DONE $(date +%H:%M). Report: results/ds004504/main/freqinst/REPORT_FREQ_INSTABILITY.md"
