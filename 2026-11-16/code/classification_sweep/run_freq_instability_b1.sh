#!/usr/bin/env bash
# Frequency x electrode screen re-analysed with the low-SNR sub-bin (b1) of every instability metric. No new
# feature extraction: stage 13 already stored b1 for every cell. Synthetic control first, then ds004504. ~15 min.
#   cd /media/wordson22/Expansion/projects2/neurohertz2/classification && conda activate nh && bash run_freq_instability_b1.sh
set -eo pipefail
cd "$(dirname "$0")"
export NH_CODE=${NH_CODE:-$PWD/../final_run/neurohertz_v2}
mkdir -p logs
step() { local name=$1; shift; echo; echo "================ $name  ($(date +%H:%M)) ================"; "$@" 2>&1 | tee "logs/$name.log"; }
export NH_SYNTH="$PWD/cache/synth_dataset"
step f20_synth_analysis_b1  python sweep/57_freq_instability_analysis.py --dataset synthetic --subbin b1 --n-perm 2000 --n-perm-cv 50 --n-rep 10
step f21_synth_check_b1     python sweep/check_freqinst_control.py freqinst_b1
step f22_analysis_main_b1   python sweep/57_freq_instability_analysis.py --dataset ds004504 --variant main --subbin b1 --n-perm 5000
echo; echo "ALL DONE $(date +%H:%M). Report: results/ds004504/main/freqinst_b1/REPORT_FREQ_INSTABILITY.md"
