"""Stage 13 (label-free): frequency INSTABILITY at fine frequency resolution, every electrode, 2-90 Hz.

Stage 12 measured instability in six fixed bands (delta ... gamma). This stage slides a 4-Hz window in 2-Hz steps
from 2 to 90 Hz and computes, at all 19 electrodes (CSD), the same SNR-matched metrics and the same
spectrum-matched surrogate excess (definitions, safeguards and validation: 12_band_instability.py).

Windows never touch the 50 Hz notch (LINE_EXCL 47.5-52.5 Hz), so there are two separate grids:
  grid A  2-46 Hz  (21 windows; brain rhythms)
  grid B  54-90 Hz (17 windows; above ~45 Hz scalp EEG is dominated by muscle, and ds004504 has a 70 Hz
                    amplifier filter, so windows above 70 Hz carry attenuated signal: reported as a muscle /
                    hardware reference, not as brain rhythm)
Output: cache/<ds>/<variant>/freqinst/<sub>.csv.gz (long: win_lo, win_hi, ch, part, metric, value)
"""
from __future__ import annotations
import argparse, importlib.util, json, time, traceback
from pathlib import Path
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from common import variant_dir, load_clean, csd_transform, EPOCH_S, LINE_EXCL

_spec = importlib.util.spec_from_file_location("s12", Path(__file__).with_name("12_band_instability.py"))
s12 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(s12)
f10 = s12.f10

WIDTH, STEP, FMIN, FMAX = 4.0, 2.0, 2.0, 90.0
K_SURR = 10
SEED = 20261116


def windows(fmin=FMIN, fmax=FMAX, width=WIDTH, step=STEP):
    """(lo, hi, grid) for every window that lies entirely outside the line-noise exclusion."""
    out = []
    lo = fmin
    while lo + width <= fmax + 1e-9:
        hi = lo + width
        if hi <= LINE_EXCL[0]:
            out.append((lo, hi, "A"))
        elif lo >= LINE_EXCL[1]:
            out.append((lo, hi, "B"))
        lo += step
    return out


def process(sub, cfile, out, k_surr=K_SURR, wins=None):
    fo = out / "freqinst" / f"{sub}.csv.gz"
    if fo.exists():
        return {"subject": sub, "status": "cached"}
    t0 = time.time()
    try:
        c = load_clean(cfile)
        x_avg, sf, chs, segs = c["data"].astype(float), float(c["sfreq"]), c["ch_names"], c["segments"]
        x_avg = x_avg - x_avg.mean(0, keepdims=True)
        x = csd_transform(x_avg, chs, sf) * 1e6
        ep = f10.epochs_of(x, sf)
        fi, _, fract = f10.irasa(ep, sf)
        wins = [w for w in (wins or windows()) if w[1] < sf / 2 - 2]
        parts = s12.split_segments(segs, x.shape[1], int(round(EPOCH_S * sf)))
        rng = np.random.default_rng([SEED, int("".join(c_ for c_ in sub if c_.isdigit()) or 0)])
        rows = []
        for i, ch in enumerate(chs):
            surrs = [f10.phase_surrogate(x[i], rng) for _ in range(k_surr)]
            ep_logbg = np.log10(fract[i] + 1e-30)
            for lo, hi, grid in wins:
                bgv = s12.background_power(fract[i], fi, lo, hi)
                if not np.isfinite(bgv) or bgv <= 0:
                    continue
                for part, sg in parts.items():
                    if not sg:
                        continue
                    if part == "all":
                        run = lambda xx: s12.channel_metrics(xx, np.asarray(sg), sf, lo, hi, bgv, ep_logbg, fi)
                    else:
                        run = lambda xx: s12._half_metrics(xx, sg, sf, lo, hi, bgv, ep_logbg, fi, x.shape[1])
                    met = run(x[i])
                    sv = [run(s_) for s_ in surrs]
                    for k_, v in met.items():
                        rows.append((lo, hi, grid, ch, part, k_, v))
                        if k_ in ("frac_snr3", "snr_median"):
                            continue
                        sm_ = np.array([d[k_] for d in sv], float)
                        mu = float(np.nanmean(sm_)) if np.isfinite(sm_).sum() >= max(1, k_surr // 2) else np.nan
                        rows.append((lo, hi, grid, ch, part, f"{k_}__surr", mu))
                        rows.append((lo, hi, grid, ch, part, f"{k_}__excess", v - mu if np.isfinite(mu) else np.nan))
        df = pd.DataFrame(rows, columns=["win_lo", "win_hi", "grid", "ch", "part", "metric", "value"])
        df.insert(0, "subject", sub)
        fo.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(fo, index=False, float_format="%.6g")
        (out / "freqinst" / f"{sub}.meta.json").write_text(json.dumps({"windows": wins, "k_surr": k_surr,
                                                                       "seconds": round(time.time() - t0, 1)}))
        return {"subject": sub, "status": "ok", "seconds": round(time.time() - t0, 1)}
    except Exception as e:  # noqa: BLE001
        return {"subject": sub, "status": "error", "reason": f"{type(e).__name__}: {e}",
                "trace": traceback.format_exc()[-1500:]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="ds004504")
    ap.add_argument("--variant", default="main")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--subjects", nargs="*", default=None)
    ap.add_argument("--k-surr", type=int, default=K_SURR)
    ap.add_argument("--fmax", type=float, default=FMAX)
    a = ap.parse_args()
    out = variant_dir(a.dataset, a.variant)
    files = [f for f in sorted((out / "clean").glob("sub-*.npz")) if not f.name.endswith(".tmp.npz")]
    if a.subjects:
        files = [f for f in files if f.stem in set(a.subjects)]
    wins = windows(fmax=a.fmax)
    print(f"[13] {a.dataset}/{a.variant}: {len(files)} clean subjects, {len(wins)} windows "
          f"({sum(w[2] == 'A' for w in wins)} in grid A, {sum(w[2] == 'B' for w in wins)} in grid B), "
          f"{a.k_surr} surrogates", flush=True)
    res = Parallel(n_jobs=a.jobs, verbose=5)(delayed(process)(f.stem, f, out, a.k_surr, wins) for f in files)
    for r in res:
        if r["status"] == "error":
            print("ERROR", r["subject"], r["reason"], "\n", r.get("trace", ""))
    print("[13] done:", {s: sum(r["status"] == s for r in res) for s in {r["status"] for r in res}})
