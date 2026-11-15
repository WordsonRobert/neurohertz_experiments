"""Stage 15 (label-free): one row per subject of mechanistic summary measures from stage 10.

Columns (ROI = pre-registered P3 Pz P4 O1 O2, CSD unless noted):
  periodic_35_45, periodic_30_48     specparam-knee periodic log-power above the aperiodic fit (PRIMARY)
  fractal_slope, fractal_offset      specparam-knee aperiodic exponent / offset, 2-48 Hz; aperiodic_knee
  irasa_periodic_35_45, irasa_fractal_slope   the same from IRASA (SECONDARY; leaks neighbouring peaks)
  logpow_35_45, logpow_35_45_lowemg  raw log power, all epochs / lowest-EMG 25% epochs (E1)
  theta_alpha, iaf                   slowing
  emg_mean                           mean log 53-68 Hz power (muscle)
  vigilance_mean                     mean per-epoch log alpha/theta
  transient_rate                     sharp-transient candidates per minute (all channels, avg ref; E6)
  gamma_no_transient_delta           ROI 30-45 Hz log power without minus with transient epochs
  pac_theta_z, pac_alpha_z, alpha_1to4_z   coupling vs time-shift surrogates (E5)
  burst_excess_roi, burst_excess_fp  log(bursts / bursts expected from the spectrum)
"""
from __future__ import annotations
import argparse
import numpy as np, pandas as pd
from common import variant_dir, ROI, REGION, OUT


def summarize(z) -> dict:
    ch = [str(c) for c in z["ch_names"]]
    roi = [ch.index(c) for c in ROI if c in ch]
    fp = [i for i, c in enumerate(ch) if REGION.get(c) == "fp"]
    f, fi = z["freqs"], z["irasa_freqs"]
    r = {}
    # PRIMARY periodic/aperiodic split = specparam-knee (10_features_raw.sp_split); IRASA kept as irasa_*
    fs_ = z["sp_freqs"]
    per = z["sp_periodic_csd"][roi].mean(0)
    r["periodic_35_45"] = np.nanmean(per[(fs_ >= 35) & (fs_ <= 45)])
    r["periodic_30_48"] = np.nanmean(per[(fs_ >= 30) & (fs_ <= 47.5)])
    apar = z["sp_params_csd"][roi]
    # names kept for downstream stages: fractal_slope = aperiodic exponent, fractal_offset = offset
    r["fractal_slope"], r["fractal_offset"] = np.nanmean(apar[:, 2]), np.nanmean(apar[:, 0])
    r["aperiodic_knee"] = np.nanmean(apar[:, 1])
    iper = z["irasa_periodic_csd"][roi].mean(0)
    r["irasa_periodic_35_45"] = iper[(fi >= 35) & (fi <= 45)].mean()
    fr = z["irasa_fractal_csd"][roi].mean(0); m = (fi >= 2) & (fi <= 40)
    sl, off = np.polyfit(np.log10(fi[m]), fr[m], 1)
    r["irasa_fractal_slope"] = -sl
    g = (f >= 35) & (f <= 45)
    r["logpow_35_45"] = z["logpsd_csd"][roi][:, g].mean()
    r["logpow_35_45_lowemg"] = z["logpsd_csd_lowemg25"][roi][:, g].mean()
    lp = 10 ** z["logpsd_csd"][roi].mean(0)
    th = lp[(f >= 4) & (f < 8)].sum(); al = lp[(f >= 8) & (f < 13)].sum()
    r["theta_alpha"] = np.log10(th / al)
    r["iaf"] = float(z["iaf"])
    r["emg_mean"] = float(np.mean(z["emg_epoch_csd"]))
    r["vigilance_mean"] = float(np.mean(z["vigilance_epoch_csd"]))
    r["transient_rate"] = float(np.mean(z["transient_rate_per_min"]))
    r["gamma_no_transient_delta"] = float(z["gamma_roi_no_transients"] - z["gamma_roi_all"])
    cc = pd.DataFrame(z["coupling_roi"], columns=[str(c) for c in z["coupling_cols"]]).mean()
    r["pac_theta_z"], r["pac_alpha_z"], r["alpha_1to4_z"] = cc["pac_theta_z"], cc["pac_alpha_z"], cc["alpha_1to4_z"]
    be = z["burst_excess"]
    r["burst_excess_roi"] = float(be[roi].mean()); r["burst_excess_fp"] = float(be[fp].mean()) if fp else np.nan
    return r


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="ds004504")
    ap.add_argument("--variant", default="main")
    a = ap.parse_args()
    d = variant_dir(a.dataset, a.variant)
    rows = {}
    for fn in sorted((d / "feat").glob("sub-*.npz")):
        if fn.name.endswith(".tmp.npz"):
            continue
        rows[fn.stem] = summarize(np.load(fn))
    df = pd.DataFrame.from_dict(rows, orient="index"); df.index.name = "subject"
    o = OUT / a.dataset / a.variant; o.mkdir(parents=True, exist_ok=True)
    df.to_csv(o / "subject_table.csv")
    print(f"[15] {len(df)} subjects -> {o / 'subject_table.csv'}")
    print(df.describe().T.round(3).to_string())
