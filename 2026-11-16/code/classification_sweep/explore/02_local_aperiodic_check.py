"""Step 1 of the 2026-11-16 plan: is the posterior 30-44 Hz "excess" in AD a real oscillatory excess, or an artefact
of fitting ONE 1/f background over 2-48 Hz to spectra whose low end is reshaped by slowing? (EXPLORATORY;
ds004504 labels are open.) Written and hashed BEFORE the per-subject spectra were loaded into this analysis.

Data: per-subject 0.5-Hz CSD log10 spectra from stage 10 (all clean epochs; and lowest-EMG 25% of epochs).
Electrodes: PRIMARY = mean of P3, P4, Pz (the electrodes of the H10 presence cluster); P3, P4, Pz, and the
pre-registered ROI (P3 Pz P4 O1 O2) reported separately.
Measures of the 32-40 Hz excess (mean over 32-40 Hz of log10 power minus a background estimate):
  M0 raw            log10 power, no background removed
  M1 flank line     straight line in log-f / log-P fitted to 24-30 and 42-47 Hz only (local, no peak fitting)
  M2 local fit      specparam, fixed aperiodic, 25-47 Hz, up to 2 peaks
  M3 global fit     specparam, knee aperiodic, 2-48 Hz, up to 8 peaks (the sweep's method; the one under suspicion)
Test: AD vs CN, Freedman-Lane permutation (5000), covariates L0 age + sex, L1 + theta/alpha; Hedges g (unadjusted).
FTD vs CN reported alongside.

DECISION RULE (fixed here, before any result of this script):
  SURVIVES  M1 and M2 (all epochs, PRIMARY) both AD > CN with permutation p < 0.05 at L0.
  DIES      M1 and M2 both p >= 0.2 at L0, or both Hedges g <= 0.2, or either has AD < CN.
  OPEN      anything else.
The lowest-EMG spectra and L1 are reported; they do not change the verdict.
Run: python explore/02_local_aperiodic_check.py --feat-dir <cache/ds004504/main/feat> --participants <tsv>
         --subject-table <results/ds004504/main/subject_table.csv> --out <dir>
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd

SEED = 20261116
BANDS = {"excess": (32.0, 40.0)}
PRIMARY = ["P3", "P4", "Pz"]
ROI = ["P3", "Pz", "P4", "O1", "O2"]
N_PERM = 5000


def spectral_model(kw):
    sys.path.insert(0, os.environ.get("NH_CODE", ""))
    from nh.spectral import _spectral_model
    return _spectral_model(kw)


def m1_flank(f, lp):
    fl = ((f >= 24) & (f <= 30)) | ((f >= 42) & (f <= 47))
    b, a = np.polyfit(np.log10(f[fl]), lp[fl], 1)
    m = (f >= 32) & (f <= 40)
    return float(np.mean(lp[m] - (a + b * np.log10(f[m]))))


def m_fit(f, lp, fmin, fmax, mode, npk):
    k = (f >= fmin) & (f <= fmax)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fm = spectral_model(dict(peak_width_limits=[1.0, 8.0], max_n_peaks=npk, min_peak_height=0.05,
                                 aperiodic_mode=mode))
        fm.fit(f[k], 10 ** lp[k], [fmin, fmax])
        ap = np.atleast_1d(fm.get_params("aperiodic"))
    if mode == "knee":
        if not (np.all(np.isfinite(ap)) and ap[1] > 0):
            return m_fit(f, lp, fmin, fmax, "fixed", npk)
        bg = ap[0] - np.log10(ap[1] + f ** ap[2])
    else:
        bg = ap[0] - ap[1] * np.log10(f)
    m = (f >= 32) & (f <= 40)
    return float(np.mean(lp[m] - bg[m]))


def subject_measures(z):
    f = z["freqs"]; ch = [str(c) for c in z["ch_names"]]; out = {}
    for spec in ("logpsd_csd", "logpsd_csd_lowemg25"):
        L = z[spec]
        for site, chans in [("primary", PRIMARY), ("roi", ROI)] + [(c, [c]) for c in PRIMARY]:
            idx = [ch.index(c) for c in chans if c in ch]
            lp = np.log10(np.mean(10 ** L[idx], 0))                       # average power, then log
            m = (f >= 32) & (f <= 40)
            out[(spec, site, "M0_raw")] = float(np.mean(lp[m]))
            out[(spec, site, "M1_flank_line")] = m1_flank(f, lp)
            for name, args in (("M2_local_fit", (25.0, 47.0, "fixed", 2)), ("M3_global_fit", (2.0, 48.0, "knee", 8))):
                try:
                    out[(spec, site, name)] = m_fit(f, lp, *args)
                except Exception:  # noqa: BLE001
                    out[(spec, site, name)] = np.nan
    return out


def fl_test(y, g, C, rng, n_perm=N_PERM):
    ok = np.isfinite(y) & np.isfinite(C).all(1)
    y, g, C = y[ok], g[ok], C[ok]
    C = C - C.mean(0)
    X = np.column_stack([np.ones(len(y)), C, g]); Xr = X[:, :-1]
    def tstat(yy):
        b, *_ = np.linalg.lstsq(X, yy, rcond=None); r = yy - X @ b
        XtXi = np.linalg.pinv(X.T @ X); h = (XtXi @ X.T)[-1]
        return b[-1] / np.sqrt(np.sum(h ** 2 * r ** 2))
    br, *_ = np.linalg.lstsq(Xr, y, rcond=None); F, R = Xr @ br, y - Xr @ br
    t = tstat(y)
    null = np.array([tstat(F + R[rng.permutation(len(R))]) for _ in range(n_perm)])
    p = (np.sum(np.abs(null) >= abs(t)) + 1) / (n_perm + 1)
    a, b = y[g == 1], y[g == 0]
    s = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
    d = (a.mean() - b.mean()) / s; gh = d * (1 - 3 / (4 * (len(a) + len(b)) - 9))
    return float(t), float(p), float(gh), int(len(a)), int(len(b))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feat-dir", required=True); ap.add_argument("--participants", required=True)
    ap.add_argument("--subject-table", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    rows = {}
    for fn in sorted(Path(a.feat_dir).glob("sub-*.npz")):
        rows[fn.stem] = subject_measures(np.load(fn))
    M = pd.DataFrame(rows).T; M.index.name = "subject"
    M.columns = ["|".join(c) for c in M.columns]
    M.to_csv(out / "subject_measures.csv")
    P = pd.read_csv(a.participants, sep="\t").rename(columns={"participant_id": "subject"}).set_index("subject")
    P["group"] = P["Group"].map({"A": "AD", "C": "CN", "F": "FTD"})
    P["sex_m"] = (P["Gender"].astype(str).str.upper() == "M").astype(float)
    st = pd.read_csv(a.subject_table, index_col=0)
    D = P[["group", "Age", "sex_m"]].join(st[["theta_alpha"]]).join(M, how="inner")
    rng = np.random.default_rng(SEED); res = []
    for tgt, ref in (("AD", "CN"), ("FTD", "CN")):
        x = D[D.group.isin([tgt, ref])]; g = (x.group == tgt).astype(float).values
        for col in M.columns:
            spec, site, meas = col.split("|")
            for lad, covs in (("L0", ["Age", "sex_m"]), ("L1", ["Age", "sex_m", "theta_alpha"])):
                t, p, gh, n1, n0 = fl_test(x[col].values.astype(float), g, x[covs].values.astype(float), rng)
                res.append(dict(contrast=f"{tgt}-{ref}", spectrum=spec, site=site, measure=meas, ladder=lad,
                                t=t, p_perm=p, hedges_g=gh, n_target=n1, n_ref=n0))
    R = pd.DataFrame(res); R.to_csv(out / "group_tests.csv", index=False)
    k = R[(R.contrast == "AD-CN") & (R.spectrum == "logpsd_csd") & (R.site == "primary") & (R.ladder == "L0")].set_index("measure")
    m1, m2 = k.loc["M1_flank_line"], k.loc["M2_local_fit"]
    if (m1.t > 0 and m2.t > 0 and m1.p_perm < 0.05 and m2.p_perm < 0.05):
        verdict = "SURVIVES"
    elif (m1.p_perm >= 0.2 and m2.p_perm >= 0.2) or (m1.hedges_g <= 0.2 and m2.hedges_g <= 0.2) or m1.t < 0 or m2.t < 0:
        verdict = "DIES"
    else:
        verdict = "OPEN"
    src = Path(__file__).read_bytes()
    meta = {"verdict": verdict, "script_sha256": hashlib.sha256(src).hexdigest(), "n_perm": N_PERM,
            "M1": m1[["t", "p_perm", "hedges_g"]].to_dict(), "M2": m2[["t", "p_perm", "hedges_g"]].to_dict()}
    json.dump(meta, open(out / "verdict.json", "w"), indent=1)
    show = R[(R.contrast == "AD-CN")].pivot_table(index=["spectrum", "site", "measure"], columns="ladder",
                                                    values=["hedges_g", "t", "p_perm"]).round(3)
    print(show.to_string()); print("\nVERDICT (AD-CN, all epochs, P3/P4/Pz, L0):", verdict)


if __name__ == "__main__":
    main()
