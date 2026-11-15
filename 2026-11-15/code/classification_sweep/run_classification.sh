#!/usr/bin/env bash
# Classification sweep (EXPLORATORY, post-freeze). Run from this folder:
#   cd /media/wordson22/Expansion/projects2/neurohertz2/classification && conda activate nh && bash run_classification.sh
# Uses the FROZEN code in ../final_run/neurohertz_v2 read-only. Re-running is safe: finished subjects are cached.
# Stops at the first failing step; every step's output is shown live and saved in logs/.
set -eo pipefail
cd "$(dirname "$0")"
J=${JOBS:-8}
export NH_CODE=${NH_CODE:-$PWD/../final_run/neurohertz_v2}
mkdir -p logs
step() { local name=$1; shift; echo; echo "================ $name  ($(date +%H:%M)) ================"; "$@" 2>&1 | tee "logs/$name.log"; }
[ -d "$NH_CODE/nh" ] || { echo "frozen code not found at $NH_CODE"; exit 1; }

step t00_tests            python -m pytest -q tests -p no:cacheprovider

# ---- positive control FIRST: synthetic data with a known gamma mechanism (PV output loss, posterior in "AD",
#      frontal in "FTD"). The sweep must find a posterior gamma effect for AD-CN; if it does not, stop and
#      do not interpret the real-data results.
export NH_SYNTH="$PWD/cache/synth_dataset"
step c00_synth_make       python "$NH_CODE/scripts/00_make_synthetic_dataset.py" --mechanism nav11_pv_output --k 1.0 --n 29 36 23 --out "$NH_SYNTH"
step c01_synth_cache      python sweep/00_cache_clean.py --dataset synthetic --no-ica --jobs "$J"
step c02_synth_features   python sweep/10_features_raw.py --dataset synthetic --jobs "$J"
step c03_synth_table      python sweep/15_subject_table.py --dataset synthetic
step c04_synth_freq       python sweep/20_frequency_resolved.py --dataset synthetic --families logpsd_csd periodic_csd fractal_csd --n-perm 1000
step c05_synth_check      python sweep/check_positive_control.py

# ---- positive control 2: an ERRATIC gamma drive (injected frequency instability) must be recovered by the
#      band-instability stages before their real-data results are interpreted
export NH_SYNTH="$PWD/cache/synth_dataset"
step c10_synth2_make      python "$NH_CODE/scripts/00_make_synthetic_dataset.py" --mechanism erratic_drive --k 1.0 --n 29 36 23 --out "$NH_SYNTH"
rm -rf cache/synthetic results/synthetic            # the second control replaces the first one's caches
step c11_synth2_cache     python sweep/00_cache_clean.py --dataset synthetic --no-ica --jobs "$J"
step c12_synth2_features  python sweep/10_features_raw.py --dataset synthetic --jobs "$J"
step c13_synth2_table     python sweep/15_subject_table.py --dataset synthetic
step c14_synth2_bandinst  python sweep/12_band_instability.py --dataset synthetic --jobs "$J"
step c15_synth2_analysis  python sweep/55_band_instability_analysis.py --dataset synthetic --n-perm 1000 --n-perm-cv 50 --n-rep 10
step c16_synth2_check     python sweep/check_instability_control.py

# ---- ds004504: clean-data caches (frozen preprocessing; with and without BSS-CCA muscle removal)
step s00_cache_main       python sweep/00_cache_clean.py --dataset ds004504 --variant main --jobs "$J"
step s00_cache_nomuscle   python sweep/00_cache_clean.py --dataset ds004504 --variant nomuscle --jobs "$J"
# ---- label-free raw measures
step s10_feat_main        python sweep/10_features_raw.py --dataset ds004504 --variant main --jobs "$J"
step s10_feat_nomuscle    python sweep/10_features_raw.py --dataset ds004504 --variant nomuscle --jobs "$J"
step s15_table_main       python sweep/15_subject_table.py --dataset ds004504 --variant main
step s15_table_nomuscle   python sweep/15_subject_table.py --dataset ds004504 --variant nomuscle
step s12_bandinst_main    python sweep/12_band_instability.py --dataset ds004504 --variant main --jobs "$J"
# ---- labels from here on (ds004504 is already unblinded; everything is EXPLORATORY)
step s20_freq_main        python sweep/20_frequency_resolved.py --dataset ds004504 --variant main --n-perm 5000
step s20_freq_nomuscle    python sweep/20_frequency_resolved.py --dataset ds004504 --variant nomuscle --families logpsd_csd periodic_csd --n-perm 2000
step s30_bursts_p95       python sweep/30_burst_types.py --dataset ds004504 --variant main --threshold p95
step s30_bursts_p99       python sweep/30_burst_types.py --dataset ds004504 --variant main --threshold p99
step s40_stratify         python sweep/40_stratify.py --dataset ds004504 --variant main
step s50_predict          python sweep/50_predict.py --dataset ds004504 --variant main --jobs "$J"
step s55_bandinst        python sweep/55_band_instability_analysis.py --dataset ds004504 --variant main
step s60_report           python sweep/60_report.py --dataset ds004504
echo; echo "ALL DONE $(date +%H:%M). Reports: results/ds004504/main/REPORT.md and results/ds004504/main/bandinst/REPORT_INSTABILITY.md"
