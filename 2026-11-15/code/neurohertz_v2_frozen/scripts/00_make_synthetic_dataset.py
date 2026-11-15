"""Generate a small synthetic EEG dataset with a KNOWN mechanism, for an end-to-end dry run.

Every subject gets 19-channel resting EEG (1/f background per channel, posterior alpha, a gamma
circuit from nh/mechsim.py in the posterior and in the frontal region). Controls run the baseline
circuit; "AD" subjects run one chosen mechanism at severity k in the posterior circuit; "FTD" subjects
run it in the frontal circuit only. Running scripts 01 -> 13 -> 14 on this dataset must recover the
injected pattern; if it does not, do not trust the pipeline on real data.

Writes results/synthetic_dataset/ (participants.tsv + sub-XXX/eeg/sub-XXX_eeg.fif). Labels here are
not real data, so the dataset has role "synthetic" (no blinding, nothing logged, stamped SYNTHETIC).

Usage
  python scripts/00_make_synthetic_dataset.py --mechanism synapses_onto_pv --k 0.75
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import mne
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nh.config import ROOT, load_config  # noqa: E402
from nh.mechsim import THEORIES, knob_params, simulate_circuit, subject_base  # noqa: E402
from nh.simulate import _colored  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mechanism", default="synapses_onto_pv", choices=THEORIES)
    ap.add_argument("--k", type=float, default=0.75)
    ap.add_argument("--n", nargs=3, type=int, default=[10, 10, 6], metavar=("CN", "AD", "FTD"))
    ap.add_argument("--dur-s", type=float, default=170.0)
    ap.add_argument("--out", default=str(ROOT / "results" / "synthetic_dataset"))
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    cfg = load_config()
    chans = cfg["common"]["channels"]
    post, front = cfg["common"]["primary_roi"], cfg["common"]["regions"]["ftd_frontal"]
    sf = 250.0
    rng = np.random.default_rng(a.seed)
    groups = ["C"] * a.n[0] + ["A"] * a.n[1] + ["F"] * a.n[2]
    params, drives = [], []
    for i, g in enumerate(groups):
        base = subject_base(np.random.default_rng([a.seed, i]))
        for region in ("post", "front"):
            hit = (g == "A" and region == "post") or (g == "F" and region == "front")
            p, d = knob_params(a.mechanism if hit else None, a.k if hit else 0.0, base)
            params.append(p); drives.append(d)
    print(f"simulating {len(params)} circuits x {a.dur_s:.0f} s ...", flush=True)
    X = simulate_circuit(params, drives, dur_s=a.dur_s, fs_out=sf, seed=a.seed)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    rows = []
    n = X.shape[1]
    t = np.arange(n) / sf
    for i, g in enumerate(groups):
        sub = f"sub-{i + 1:03d}"
        gp, gf = X[2 * i], X[2 * i + 1]
        alpha = np.sin(2 * np.pi * rng.normal(10, 0.5) * t + rng.uniform(0, 6.28))
        data = []
        # volume conduction: every channel mixes 4 shared 1/f sources + its own local activity
        shared = [_colored(n, sf, 1.7, rng) for _ in range(4)]
        for ch in chans:
            w = rng.uniform(0.3, 0.8, size=4)
            x = sum(wi * si for wi, si in zip(w, shared)) + 0.6 * _colored(n, sf, rng.normal(1.6, 0.15), rng) \
                + 0.05 * rng.standard_normal(n)
            if ch in post:
                x += 0.35 * gp + 0.8 * alpha
            if ch in front:
                x += 0.35 * gf
            data.append(x * 10e-6)
        info = mne.create_info(chans, sf, "eeg")
        raw = mne.io.RawArray(np.asarray(data), info, verbose="ERROR")
        raw.set_montage(mne.channels.make_standard_montage("standard_1020"), on_missing="ignore")
        p = out / sub / "eeg"; p.mkdir(parents=True, exist_ok=True)
        raw.save(p / f"{sub}_eeg.fif", overwrite=True, verbose="ERROR")
        mmse = {"C": rng.normal(29.5, 0.5), "A": rng.normal(18, 4), "F": rng.normal(22, 3)}[g]
        rows.append({"participant_id": sub, "Group": g, "Age": int(rng.normal(68, 7)),
                     "Gender": rng.choice(["M", "F"]), "MMSE": int(np.clip(round(mmse), 5, 30))})
    pd.DataFrame(rows).to_csv(out / "participants.tsv", sep="\t", index=False)
    (out / "GROUND_TRUTH.txt").write_text(f"mechanism={a.mechanism} k={a.k} (AD: posterior circuit, FTD: frontal circuit)\n")
    print(f"wrote {len(rows)} subjects to {out}")


if __name__ == "__main__":
    main()
