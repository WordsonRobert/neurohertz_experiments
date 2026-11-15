#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
B="python scripts/01_extract_features.py --dataset ds004504 --jobs 8 --split-half"
run () { echo; echo "===== $(date '+%F %T')  START $*"; $B "$@"; echo "===== $(date '+%F %T')  END (exit $?)"; }
run --n-surr 4  --variant estimator-sst  --set features.if_estimator=sst
run --n-surr 4  --variant estimator-vmd  --set features.if_estimator=vmd
run --n-surr 4  --variant median-single  --set features.if_median.mode=single
run --n-surr 10 --variant surr_chunk-s30
run --n-surr 10 --variant surr_chunk-s15 --set features.surrogates.chunk_s=15
run --n-surr 10 --variant surr_chunk-s60 --set features.surrogates.chunk_s=60
echo; echo "===== ALL DONE $(date '+%F %T')"
