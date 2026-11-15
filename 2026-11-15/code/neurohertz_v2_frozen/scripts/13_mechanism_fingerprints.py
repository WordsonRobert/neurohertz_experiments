"""Stage 0c (LABEL-FREE): mechanistic fingerprints + identifiability, frozen before any labels.

For each model family (nh/mechsim.py rate circuit, nh/cyclemodel.py cycle map) and each candidate
mechanism (config `mechanism.theories`), simulated subjects are run at several severities and
measured with the real NeuroHertz feature code. Outputs (results/mechanism/):

  sim_features.csv       every simulated subject x severity x feature
  fingerprints.csv       per family x theory x feature: slope, t, sign, standardised effect d at k = 0.5
  agreement.csv          do the two families agree on each direction? (firm / weak / conflict)
  separability.csv       cosine similarity between theory fingerprints (> 0.9 = not separable)
  identifiability.json   recovery at OUR sample size (36 vs 29), within and ACROSS families
  fingerprints.json      what 14_mechanism_tests.py reads (hashed into the freeze by 03_freeze.py)

Nothing here reads a dataset or a label (tests/test_leakage.py checks the imports).

Usage
  python scripts/13_mechanism_fingerprints.py --jobs 8                 # full (config settings)
  python scripts/13_mechanism_fingerprints.py --quick --jobs 4         # smoke test: 6 subjects, 60 s
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nh.config import ROOT, analysis_hash, load_config  # noqa: E402
from nh.fingerprint import (agreement, compare, fingerprint_matrix, fingerprints, measure,  # noqa: E402
                            recovery, simulate_family)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--quick", action="store_true", help="tiny run to check the machinery")
    ap.add_argument("--out", default=str(ROOT / "results" / "mechanism"))
    a = ap.parse_args()
    cfg = load_config(); mc = cfg["mechanism"]; fc = dict(mc["fingerprint"])
    if a.quick:
        fc.update(seeds=6, dur_s=60.0, n_surr=2, recovery_resamples=20, levels=[0.0, 0.5, 1.0])
    theories = list(mc["theories"].values())
    code = {v: k for k, v in mc["theories"].items()}
    local = [mc["theories"][t] for t in mc["local_loop"]]
    inputs = [mc["theories"][t] for t in mc["input_driven"]]
    primary = cfg["statistics"]["primary_feature"]
    features = list(dict.fromkeys(fc["features"] + [primary]))
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    seed = cfg["statistics"]["seed"]

    rows = []
    for fam in fc["families"]:
        t0 = time.time()
        sims = simulate_family(fam, theories, fc["levels"], fc["seeds"], fc["dur_s"], master_seed=seed)
        print(f"[{fam}] simulated {len(sims)} signals in {time.time() - t0:.0f} s; measuring ...", flush=True)
        recs = Parallel(n_jobs=a.jobs, verbose=2)(
            delayed(measure)(s, cfg["features"], fc["gamma_snr"], fc["n_surr"], seed, primary) for s in sims)
        rows += recs
        print(f"[{fam}] done in {time.time() - t0:.0f} s", flush=True)
    df = pd.DataFrame(rows)
    if primary in df:
        df[primary] = df[primary]
    df.to_csv(out / "sim_features.csv", index=False)

    k_ref = min(fc["levels"][1:], key=lambda k: abs(k - 0.5))
    fp = fingerprints(df, features, fc["slope_t_threshold"], k_ref=k_ref)
    fp["code"] = fp.theory.map(code)
    fp.to_csv(out / "fingerprints.csv", index=False)
    agr = agreement(fp); agr["code"] = agr.theory.map(code)
    agr.to_csv(out / "agreement.csv", index=False)

    # separability: cosine between theory fingerprints within each family
    sep_rows, mats = [], {}
    for fam in fc["families"]:
        M = fingerprint_matrix(fp, fam, features).dropna(axis=1)
        mats[fam] = M
        U = M.values / (np.linalg.norm(M.values, axis=1, keepdims=True) + 1e-12)
        C = U @ U.T
        for i, ti in enumerate(M.index):
            for j, tj in enumerate(M.index):
                if j > i:
                    sep_rows.append({"family": fam, "a": code[ti], "b": code[tj], "cosine": float(C[i, j]),
                                     "separable": bool(C[i, j] < 0.9)})
    pd.DataFrame(sep_rows).to_csv(out / "separability.csv", index=False)

    # identifiability: fingerprints from one half of the simulated subjects, studies drawn from the
    # other half; within family and across families (model misspecification)
    rng = np.random.default_rng(seed)
    nseeds = fc["seeds"]
    half_a = set(range(0, nseeds, 2)); half_b = set(range(1, nseeds, 2))
    ident = {}
    for fam_fp in fc["families"]:
        fpA = fingerprints(df[df.seed.isin(half_a)], features, fc["slope_t_threshold"], k_ref=k_ref)
        F = fingerprint_matrix(fpA, fam_fp, features).dropna(axis=1)
        for fam_data in fc["families"]:
            test = df[(df.family == fam_data) & df.seed.isin(half_b)]
            r = recovery(test, F, list(F.columns), local, inputs, mc["fingerprint"]["recovery_n"]["patients"],
                         mc["fingerprint"]["recovery_n"]["controls"], fc["recovery_resamples"], k_ref, rng)
            ident[f"fingerprints_{fam_fp}__data_{fam_data}"] = r
            print(f"recovery fp={fam_fp} data={fam_data}: local-vs-input {r['local_vs_input_accuracy']:.2f}; "
                  + ", ".join(f"{code[t]} {v:.2f}" for t, v in r["accuracy_per_theory"].items()), flush=True)
    (out / "identifiability.json").write_text(json.dumps(ident, indent=2, default=float))

    payload = {"features": features, "k_ref": k_ref, "theories": mc["theories"], "local": local, "inputs": inputs,
               "families": {fam: {"matrix": mats[fam].to_dict(orient="index")} for fam in fc["families"]},
               "signs": fp[["family", "theory", "feature", "sign", "t", "d_at_k"]].to_dict("records"),
               "agreement": agr.to_dict("records"), "settings": fc, "quick": a.quick,
               "labels_used": False, **analysis_hash()}
    (out / "fingerprints.json").write_text(json.dumps(payload, indent=2, default=float))
    show = agr.pivot_table(index="feature", columns="code", values="verdict", aggfunc="first")
    print("\nAgreement between model families (firm_up / firm_down / firm_none / weak_* / conflict):")
    print(show.to_string())


if __name__ == "__main__":
    main()
