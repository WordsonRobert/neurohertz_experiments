"""Extract features for every method ablation (label-blind; calls 01_extract_features.py).

  --mode one-at-a-time : each option of each Stage-A dimension, all other choices at the primary
                         setting -> results/features/<dataset>/<dim>-<option>/   (for 11_select_methods.py)
  --mode factorial     : every combination of the `ablations.multiverse` dimensions
                         -> results/features/<dataset>/mv__<dim>-<opt>__...       (for 12_specification_curve.py)
  --mode simulation    : the estimator / median options on ground-truth simulations
                         -> results/simulation/<dim>-<option>/                     (02_simulation_validation.py)

The primary option of each dimension is the one with an empty override list; it is not re-extracted
in one-at-a-time mode (the 'primary' variant is used), except for dimensions listed in
`ablations.surrogate_dims`, which get their own baseline run with the same surrogate count as their
other options. Surrogate counts: `ablations.n_surr_selection` (default 4) and `n_surr_surrogate_dims`
(default 10). The ablation 'primary' therefore has fewer surrogates than the final run; the per-subject
cache key includes the surrogate count, so the final run recomputes rather than reusing it.

Usage
  python scripts/10_run_ablations.py --dataset ds004504 --mode one-at-a-time --jobs 8
  python scripts/10_run_ablations.py --mode simulation --jobs 8
  python scripts/10_run_ablations.py --dataset ds004504 --mode factorial --jobs 8
"""
from __future__ import annotations

import argparse
import itertools
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nh.config import ROOT, load_config  # noqa: E402

PY = sys.executable


def run(cmd):
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="ds004504")
    ap.add_argument("--mode", required=True, choices=["one-at-a-time", "factorial", "simulation"])
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--n-surr", type=int, default=None)
    ap.add_argument("--roots", nargs="*", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    cfg = load_config()
    dims = cfg["ablations"]["stage_a"]
    base = [PY, str(ROOT / "scripts" / "01_extract_features.py"), "--dataset", a.dataset, "--jobs", str(a.jobs),
            "--split-half"] + (["--n-surr", str(a.n_surr)] if a.n_surr else []) + (["--roots", *a.roots] if a.roots else [])
    todo = []
    if a.mode == "one-at-a-time":
        ab = cfg["ablations"]
        sdims = set(ab.get("surrogate_dims", []))
        def ns(dim):                      # --n-surr given on the command line wins
            if a.n_surr:
                return []
            k = ab.get("n_surr_surrogate_dims", 10) if dim in sdims else ab.get("n_surr_selection")
            return ["--n-surr", str(k)] if k else []
        todo.append(base + ns(None) + ["--variant", "primary"])
        for dim, opts in dims.items():
            for opt, ov in opts.items():
                if dim in sdims:          # own baseline, same surrogate count for every option of this dimension
                    todo.append(base + ns(dim) + ["--variant", f"{dim}-{opt}"] + (["--set", *ov] if ov else []))
                elif ov:
                    todo.append(base + ns(dim) + ["--variant", f"{dim}-{opt}", "--set", *ov])
    elif a.mode == "factorial":
        mv = cfg["ablations"]["multiverse"]
        for combo in itertools.product(*[list(dims[d].items()) for d in mv]):
            name = "mv__" + "__".join(f"{d}-{o}" for d, (o, _) in zip(mv, combo))
            ov = [x for _, (_, o) in zip(mv, combo) for x in o]
            todo.append(base + ["--variant", name] + (["--set", *ov] if ov else []))
    else:
        sim = [PY, str(ROOT / "scripts" / "02_simulation_validation.py"), "--jobs", str(a.jobs)]
        for dim in cfg["ablations"]["selection_rule"]["simulation_first"]:
            for opt, ov in dims[dim].items():
                todo.append(sim + ["--tag", f"{dim}-{opt}"] + (["--set", *ov] if ov else []))
    for cmd in todo:
        if a.dry_run:
            print(" ".join(cmd))
        else:
            run(cmd)


if __name__ == "__main__":
    main()
