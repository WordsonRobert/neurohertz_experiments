"""Stage 12 (label-free): frequency INSTABILITY of every rhythm, delta to gamma, measured at MATCHED SNR.

Why matched SNR: the error of any instantaneous-frequency estimate grows as the rhythm's amplitude falls
toward the background. AD has less rhythmic power (Kopcanova et al. 2024), so an unmatched "instability" is
higher in AD for that reason alone (Balaji et al. 2026: 1-s alpha frequency variability is near noise level).
Two safeguards: (1) every sample, cycle, burst and epoch gets its own SNR relative to the subject's APERIODIC
background in that band (IRASA fractal part), and instability is computed inside fixed SNR sub-bins identical
for every subject; (2) the spectrum-matched surrogate excess (below). Validation showed (1) alone is NOT enough:
it equalizes each sample's measurement noise but not the mix of rhythm and background at that SNR (same
jitter at two amplitudes still differed by 17%). (2) is exact under the null: for a Gaussian process with any
spectrum and SNR the excess is ~0 (tests/test_sweep.py), so __excess is the primary measure.

Bands: delta 2-4, theta 4-8, alpha IAF +/- 2, beta_low 13-20, beta_high 20-30, gamma 30-45 Hz (CSD).
Metrics (each MATCHED; *_naive = all samples with SNR >= 3, shown only to expose the SNR confound):
  if_sd         robust SD (1.4826 MAD) of instantaneous frequency
  slip_frac     fraction of samples whose instantaneous frequency leaves the band by > 1 Hz (phase slips)
  period_cv     coefficient of variation of cycle periods (peak to peak)
  pf_sd_epochs  SD across 2-s epochs of the band's spectral peak frequency (dominant-frequency variability)
  burst_f_sd    SD across bursts (>= 3 cycles at SNR >= 3) of each burst's mean frequency
Presence (NOT instability, reported so it can be controlled): frac_snr3 (time at SNR >= 3), snr_median.

BEYOND THE SPECTRUM. For a stationary Gaussian process, every instantaneous-frequency statistic is fixed by the
power spectrum (Rice 1944): "instability" can then be peak width, power or 1/f in disguise. Each metric is
therefore also computed on K phase-randomized surrogates of the same channel (identical spectrum, Gaussian,
no bursts, no frequency dynamics of their own): <metric>__surr = surrogate mean, <metric>__excess = observed
minus surrogate. Raw values that classify while __excess does not = spectral information (already in
slowing / 1/f); __excess that adds beyond the spectral baseline = genuine dynamic instability.
Every metric is computed on all data and on each half (h1, h2) for split-half reliability.
Output: cache/<ds>/<variant>/bandinst/<sub>.csv.gz (long: band, ch, part, metric, value)
"""
from __future__ import annotations
import argparse, importlib.util, json, time, traceback
from pathlib import Path
import numpy as np, pandas as pd
from scipy.signal import find_peaks, periodogram
from joblib import Parallel, delayed
from common import variant_dir, load_clean, csd_transform, ROI, EPOCH_S

_spec = importlib.util.spec_from_file_location("f10", Path(__file__).with_name("10_features_raw.py"))
f10 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(f10)

FIXED = {"delta": (2.0, 4.0), "theta": (4.0, 8.0), "beta_low": (13.0, 20.0), "beta_high": (20.0, 30.0),
         "gamma": (30.0, 45.0)}
BAND_ORDER = ["delta", "theta", "alpha", "beta_low", "beta_high", "gamma"]
SUBBINS = [(3.0, 5.5), (5.5, 10.0)]            # sample/cycle/burst SNR (|z|^2 / E|z|^2 under the background)
EP_SUBBINS = [(4.0, 8.0), (8.0, 16.0)]         # epoch peak-to-background power ratio. A single periodogram bin
                                               # of pure background is Exp(1); the max of ~8 alpha-band bins
                                               # exceeds 4 with p ~ 0.14 and 8 with p ~ 0.003, so these bins
                                               # are rhythm-dominated (gamma, ~30 bins, stays noise-heavy)
MIN_S = 4.0                                    # seconds of samples required per sub-bin
NFFT_EP = 2048
K_SURR = 10
SEED = 20261115


def bands_for(iaf):
    b = dict(FIXED); b["alpha"] = (iaf - 2.0, iaf + 2.0)
    return {k: b[k] for k in BAND_ORDER}


def trans_for(lo):
    return max(0.5, min(2.0, 0.25 * lo))       # narrow bands need sharp filters; delta 2-4 Hz -> 0.5 Hz


def background_power(fract_ch, fi, lo, hi):
    """Variance of a band-passed Gaussian process with the fractal spectrum: integral of the PSD over the band."""
    m = (fi >= lo) & (fi <= hi)
    return float(np.trapezoid(fract_ch[m], fi[m]))


def strat(values_by_bin, min_n, fn):
    """fn inside each SNR sub-bin (NaN when a bin has < min_n values) and their equal-weight mean (NaN unless
    every bin has data). Returns (bin1, bin2, mean). Bin 1 has the widest coverage (weak rhythms reach it),
    bin 2 the cleanest estimate; the mean is the strictest match."""
    vals = []
    for v in values_by_bin:
        v = np.asarray(v, float); v = v[np.isfinite(v)]
        vals.append(float(fn(v)) if len(v) >= min_n else np.nan)
    return vals[0], vals[1], (float(np.mean(vals)) if np.all(np.isfinite(vals)) else np.nan)


def put(r, name, triple):
    r[f"{name}_b1"], r[f"{name}_b2"], r[name] = triple


def rmad(v):
    return 1.4826 * np.median(np.abs(v - np.median(v)))


def channel_metrics(x, segs, sf, lo, hi, bg_var, ep_logbg, fi_ep):
    """All metrics for one channel and one band. x = 1-D CSD signal; segs = contiguous segments."""
    tr = trans_for(lo)
    z = f10.analytic(x, segs, sf, lo, hi, tr, edge=int(0.25 * sf))
    snr = np.abs(z) ** 2 / (2.0 * bg_var)                     # E|z|^2 = 2 * variance of the real band signal
    inst = np.angle(z[1:] * np.conj(z[:-1])) * sf / (2 * np.pi)
    s1 = snr[1:]
    r = {"frac_snr3": float(np.nanmean(s1 >= 3)), "snr_median": float(np.nanmedian(s1))}
    in_bins = [(s1 >= a) & (s1 < b) for a, b in SUBBINS]
    min_n = int(MIN_S * sf)
    put(r, "if_sd", strat([inst[m] for m in in_bins], min_n, rmad))
    put(r, "slip_frac", strat([((inst[m] < lo - 1) | (inst[m] > hi + 1)).astype(float) for m in in_bins], min_n, np.mean))
    naive = s1 >= 3
    r["if_sd_naive"] = rmad(inst[naive & np.isfinite(inst)]) if naive.sum() >= min_n else np.nan
    # cycles: peaks of the band-passed signal, period between successive peaks inside one segment
    per, per_snr = [], []
    xr = np.real(z)
    for a, b in segs:
        seg = xr[a:b]
        ok = np.isfinite(seg)
        if ok.sum() < sf:
            continue
        pk, _ = find_peaks(np.where(ok, seg, -np.inf), distance=max(1, int(0.6 * sf / hi)))
        pk = pk[ok[pk]]
        if len(pk) < 3:
            continue
        d = np.diff(pk)
        good = d <= 1.5 * sf / lo                                # a gap longer than 1.5 slow periods is not one cycle
        sn = np.array([np.nanmean(snr[a + p0: a + p1]) for p0, p1 in zip(pk[:-1], pk[1:])])
        per += list(d[good] / sf); per_snr += list(sn[good])
    per, per_snr = np.asarray(per), np.asarray(per_snr)
    put(r, "period_cv", strat([per[(per_snr >= a2) & (per_snr < b2)] for a2, b2 in SUBBINS], 30,
                              lambda v: np.std(v) / np.mean(v)))
    # bursts: runs at SNR >= 3 lasting >= 3 cycles; burst frequency and burst SNR
    above = np.nan_to_num(snr, nan=0.0) >= 3
    dd = np.diff(np.r_[0, above.astype(int), 0]); on, off = np.flatnonzero(dd == 1), np.flatnonzero(dd == -1)
    bf, bs = [], []
    for a, b in zip(on, off):
        f_b = inst[a:b - 1]
        if b - a < 4 or not np.all(np.isfinite(f_b)):
            continue
        fm = np.median(f_b)
        if fm > 0 and (b - a) / sf * fm >= 3:
            bf.append(fm); bs.append(np.mean(snr[a:b]))
    bf, bs = np.asarray(bf), np.asarray(bs)
    put(r, "burst_f_sd", strat([bf[(bs >= a2) & (bs < b2)] for a2, b2 in SUBBINS], 8, np.std))
    # epoch-wise spectral peak (dominant-frequency variability), matched on epoch peak-to-background ratio
    ep = f10.epochs_of(x[None], sf)[0]
    fe, pe = periodogram(ep, sf, window="hann", nfft=NFFT_EP, axis=-1, detrend="constant")
    m = (fe >= lo) & (fe <= hi)
    bg = np.interp(fe[m], fi_ep, ep_logbg)
    ratio = np.log10(pe[:, m] + 1e-30) - bg
    k = np.argmax(ratio, 1)
    pf = fe[m][k]; pr = 10 ** ratio[np.arange(len(k)), k]
    put(r, "pf_sd_epochs", strat([pf[(pr >= a2) & (pr < b2)] for a2, b2 in EP_SUBBINS], 8, np.std))
    return r


def split_segments(segs, n_total, n_ep):
    half = (n_total // n_ep // 2) * n_ep          # split on an epoch boundary so both halves hold whole epochs
    h1 = [(a, min(b, half)) for a, b in segs if a < half]
    h2 = [(max(a, half), b) for a, b in segs if b > half]
    return {"all": [tuple(s) for s in segs], "h1": h1, "h2": h2}


def process(sub, cfile, out, k_surr=K_SURR):
    fo = out / "bandinst" / f"{sub}.csv.gz"
    if fo.exists():
        return {"subject": sub, "status": "cached"}
    t0 = time.time()
    try:
        c = load_clean(cfile)
        x_avg, sf, chs, segs = c["data"].astype(float), float(c["sfreq"]), c["ch_names"], c["segments"]
        x_avg = x_avg - x_avg.mean(0, keepdims=True)
        x = csd_transform(x_avg, chs, sf) * 1e6
        ep = f10.epochs_of(x, sf)
        fi, _, fract = f10.irasa(ep, sf)                         # background per channel (all data)
        f, p = f10.epoch_psd(ep, sf)
        roi = [chs.index(c_) for c_ in ROI if c_ in chs]
        iaf = f10.iaf_from_psd(f[f <= 70], np.log10(p[roi].mean((0, 1))[f <= 70] + 1e-30))
        bands = bands_for(iaf)
        parts = split_segments(segs, x.shape[1], int(round(EPOCH_S * sf)))
        rng = np.random.default_rng([SEED, int("".join(c_ for c_ in sub if c_.isdigit()) or 0)])
        rows = []
        for i, ch in enumerate(chs):
            surrs = [f10.phase_surrogate(x[i], rng) for _ in range(k_surr)]
            ep_logbg = np.log10(fract[i] + 1e-30)     # background per Hz, same scale as one periodogram
            for bname, (lo, hi) in bands.items():
                bgv = background_power(fract[i], fi, lo, hi)
                if not np.isfinite(bgv) or bgv <= 0:
                    continue
                for part, sg in parts.items():
                    if not sg:
                        continue
                    run = (lambda xx: channel_metrics(xx, np.asarray(sg), sf, lo, hi, bgv, ep_logbg, fi)) \
                        if part == "all" else (lambda xx: _half_metrics(xx, sg, sf, lo, hi, bgv, ep_logbg, fi, x.shape[1]))
                    met = run(x[i])
                    sv = [run(s_) for s_ in surrs]
                    for k_, v in met.items():
                        rows.append((bname, ch, part, k_, v))
                        if k_ in ("frac_snr3", "snr_median"):
                            continue
                        sm_ = np.array([d[k_] for d in sv], float)
                        mu = float(np.nanmean(sm_)) if np.isfinite(sm_).sum() >= max(1, k_surr // 2) else np.nan
                        rows.append((bname, ch, part, f"{k_}__surr", mu))
                        rows.append((bname, ch, part, f"{k_}__excess", v - mu if np.isfinite(mu) else np.nan))
        df = pd.DataFrame(rows, columns=["band", "ch", "part", "metric", "value"])
        df.insert(0, "subject", sub)
        fo.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(fo, index=False)
        (out / "bandinst" / f"{sub}.meta.json").write_text(json.dumps({"iaf": iaf, "bands": bands,
                                                                       "seconds": round(time.time() - t0, 1)}))
        return {"subject": sub, "status": "ok", "seconds": round(time.time() - t0, 1)}
    except Exception as e:  # noqa: BLE001
        return {"subject": sub, "status": "error", "reason": f"{type(e).__name__}: {e}",
                "trace": traceback.format_exc()[-1500:]}


def _half_metrics(xx, sg, sf, lo, hi, bgv, ep_logbg, fi, n_total):
    """Metrics on one half. Epoch-based measures need whole epochs, so the half is re-cut on epoch boundaries."""
    n = int(round(EPOCH_S * sf))
    a0 = min(a for a, _ in sg); b0 = max(b for _, b in sg)
    a0, b0 = (a0 // n) * n, (b0 // n) * n
    sub_x = xx[a0:b0]
    sub_segs = np.asarray([(max(a, a0) - a0, min(b, b0) - a0) for a, b in sg if min(b, b0) > max(a, a0)])
    return channel_metrics(sub_x, sub_segs, sf, lo, hi, bgv, ep_logbg, fi)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="ds004504")
    ap.add_argument("--variant", default="main")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--subjects", nargs="*", default=None)
    ap.add_argument("--k-surr", type=int, default=K_SURR, help="phase-randomized surrogates per channel (pilots only lower it)")
    a = ap.parse_args()
    out = variant_dir(a.dataset, a.variant)
    files = [f for f in sorted((out / "clean").glob("sub-*.npz")) if not f.name.endswith(".tmp.npz")]
    if a.subjects:
        files = [f for f in files if f.stem in set(a.subjects)]
    print(f"[12] {a.dataset}/{a.variant}: {len(files)} clean subjects", flush=True)
    res = Parallel(n_jobs=a.jobs, verbose=5)(delayed(process)(f.stem, f, out, a.k_surr) for f in files)
    for r in res:
        if r["status"] == "error":
            print("ERROR", r["subject"], r["reason"], "\n", r.get("trace", ""))
    print("[12] done:", {s: sum(r["status"] == s for r in res) for s in {r["status"] for r in res}})
