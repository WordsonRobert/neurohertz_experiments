#!/usr/bin/env bash
# Final NeuroHertz run on ds004504 (and ds006036 if downloaded). Output appears live and is also saved in
# logs/. Stops at the first failing step. Re-running is safe: finished subjects are cached and skipped.
#
#   cd <this folder> && conda activate nh && bash run_final.sh
set -eo pipefail
cd "$(dirname "$0")"
J=${JOBS:-8}
mkdir -p logs
step() { local name=$1; shift; echo; echo "================ $name  ($(date +%H:%M)) ================"; "$@" 2>&1 | tee "logs/$name.log"; }
D6036=$(ls -d /media/wordson22/Expansion/projects2/neurohertz2/data/ds006036* /media/wordson22/Expansion/projects2/neurohertz2/data/on006036* ${NH_DRIVE:-/nonexistent}/ds006036* 2>/dev/null | head -1 || true)

step 00_tests        python -m pytest -q

# ---- Stage A: label-blind features (20 surrogates, final pipeline from config/pipeline.yaml)
step 01_ds004504     python scripts/01_extract_features.py --dataset ds004504 --split-half --jobs "$J"
if [ -n "$D6036" ]; then
  step 01_ds006036   python scripts/01_extract_features.py --dataset ds006036 --split-half --jobs "$J"
  step 07_retest     python scripts/07_reliability.py --dataset ds004504 --retest ds006036   # label-free
else
  echo "ds006036 not found under data/ -> skipped (no between-session reliability)"
fi

# ---- simulation metric validation + mechanism fingerprints (label-free)
step 02b_calibrate   python scripts/02b_calibrate_simulation.py --dataset ds004504
step 02_simulation   python scripts/02_simulation_validation.py --jobs "$J"
step 13_fingerprints python scripts/13_mechanism_fingerprints.py --jobs "$J"

# ---- positive controls: synthetic data with a KNOWN mechanism must be recovered
for MECH in synapses_onto_pv erratic_drive; do
  export NH_SYNTH="$PWD/results/synthetic_$MECH"
  step 00_synth_$MECH  python scripts/00_make_synthetic_dataset.py --mechanism "$MECH" --k 0.75 --n 29 36 23 --out "$NH_SYNTH"
  step 01_synth_$MECH  python scripts/01_extract_features.py --dataset synthetic --variant "synth-$MECH" --no-ica --jobs "$J"
  step 14_synth_$MECH  python scripts/14_mechanism_tests.py --dataset synthetic --variant "synth-$MECH"
done
unset NH_SYNTH

# ---- freeze (hashes config, code, plan, metric + method selection, fingerprints)
if [ -f registry/freeze.json ]; then
  echo "Already frozen (registry/freeze.json) -> freeze step skipped"
else
  echo "Setting status: frozen in config/pipeline.yaml"
  sed -i 's/^status: development /status: frozen      /' config/pipeline.yaml
  grep -q "^status: frozen" config/pipeline.yaml || { echo "could not set status: frozen"; exit 1; }
  step 03_freeze python scripts/03_freeze.py --override-reason "Primary = burst_freq_sd (raw) with the 1/f exponent as covariate, not the simulation-selected burst_freq_sd_z: the z version has split-half ICC -0.01 to 0.13 on real data in every pipeline (label-free, registry/method_selection.json); the raw metric's main simulated nuisance (1/f slope) is handled by the covariate."
fi

# ---- Stage B: labels opened (logged in the ledger)
step 04_discovery    python scripts/04_discovery_analysis.py --dataset ds004504
step 07_reliability  python scripts/07_reliability.py --dataset ds004504 || echo "07 failed - continuing"
step 14_mechanism    python scripts/14_mechanism_tests.py --dataset ds004504
step 05_prediction   python scripts/05_prediction.py --dataset ds004504 --jobs "$J"
step 09_ceiling      python scripts/09_ceiling_check.py --dataset ds004504
# 08_normative_and_paired.py needs a normative dataset (--norm); run it separately once one is chosen.
echo; echo "ALL DONE $(date +%H:%M). Logs in logs/, results in results/analysis/."
