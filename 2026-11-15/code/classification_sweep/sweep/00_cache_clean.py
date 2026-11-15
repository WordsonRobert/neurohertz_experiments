"""Stage 0 (label-free): run the FROZEN preprocessing once per subject and cache the clean data.

Variants
  main      : the frozen pipeline exactly (ICA + BSS-CCA muscle removal + autoreject), cached at average
              reference; CSD is applied downstream with the same MNE call the frozen pipeline used.
  nomuscle  : identical except BSS-CCA muscle removal is switched off (ICLabel muscle rejection stays).
              Comparing the two tells us whether any 30-48 Hz group effect depends on muscle handling (E1).

Output: cache/<dataset>/<variant>/clean/<sub>.npz  (data in uV float32, segments, sfreq, ch_names, qc)
"""
from __future__ import annotations
import argparse, json, time, traceback
from pathlib import Path
import numpy as np
from joblib import Parallel, delayed

from common import CODE, variant_dir, save_npz, jsonable  # noqa: E402
from nh.config import load_config, apply_overrides  # noqa: E402
from nh.datasets import get_adapter  # noqa: E402
from nh.preprocess import ExcludedRecording, preprocess  # noqa: E402

VARIANTS = {"main": [], "nomuscle": ["preprocessing.muscle.method=none"]}


def one(dataset, sub, path, variant, roots, out: Path, no_ica: bool = False):
    fn = out / "clean" / f"{sub}.npz"
    if fn.exists():
        return {"subject": sub, "status": "cached"}
    t0 = time.time()
    try:
        cfg = apply_overrides(load_config(), VARIANTS[variant])
        ad = get_adapter(dataset, **({"roots": roots} if roots else {}))
        raw = ad.load_raw(path)
        lf = ad.line_freq if isinstance(ad.line_freq, (int, float)) else cfg["common"]["line_freq"]
        clean = preprocess(raw, cfg, lf, skip_ica=True if no_ica else ad.skip_ica,
                           reference="average")
        qc = {**clean.qc, "raw_seconds": float(raw.times[-1]), "variant": variant}
        save_npz(fn, data=(clean.data * 1e6).astype(np.float32), segments=np.asarray(clean.segments, int),
                 sfreq=np.float64(clean.sfreq), ch_names=np.asarray(clean.ch_names),
                 qc=np.asarray(json.dumps(qc, default=jsonable)))
        return {"subject": sub, "status": "ok", "seconds": round(time.time() - t0, 1)}
    except ExcludedRecording as e:
        rec = {"subject": sub, "status": "excluded", "reason": str(e)}
    except Exception as e:  # noqa: BLE001  recorded, never silently dropped
        rec = {"subject": sub, "status": "error", "reason": f"{type(e).__name__}: {e}",
               "trace": traceback.format_exc()[-1500:]}
    (out / "clean").mkdir(parents=True, exist_ok=True)
    (out / "clean" / f"{sub}.status.json").write_text(json.dumps(rec))
    return rec


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="ds004504")
    ap.add_argument("--variant", default="main", choices=list(VARIANTS))
    ap.add_argument("--roots", nargs="*", default=None)
    ap.add_argument("--subjects", nargs="*", default=None)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--no-ica", action="store_true", help="synthetic data only (as in the frozen dry runs)")
    a = ap.parse_args()
    ad = get_adapter(a.dataset, **({"roots": a.roots} if a.roots else {}))
    recs = ad.recordings()
    if a.subjects:
        recs = {s: p for s, p in recs.items() if s in set(a.subjects)}
    out = variant_dir(a.dataset, a.variant)
    print(f"[00] {a.dataset}/{a.variant}: {len(recs)} recordings -> {out}  (frozen code: {CODE})", flush=True)
    res = Parallel(n_jobs=a.jobs, verbose=5)(delayed(one)(a.dataset, s, p, a.variant, a.roots, out, a.no_ica)
                                              for s, p in sorted(recs.items()))
    st = {}
    for r in res:
        st[r["status"]] = st.get(r["status"], 0) + 1
    (out / "cache_meta.json").write_text(json.dumps({"dataset": a.dataset, "variant": a.variant,
                                                     "overrides": VARIANTS[a.variant], "status": st}, indent=1))
    print("[00] status:", st)
