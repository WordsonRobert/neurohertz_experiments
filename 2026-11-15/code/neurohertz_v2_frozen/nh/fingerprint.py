"""Mechanistic fingerprints: what each candidate mechanism does to the NeuroHertz features.

Label-free. Simulated "subjects" (each with their own baseline circuit, gamma SNR and 1/f slope) are
run at several severities of each mechanism, in two model families, and measured with the SAME
feature code as real EEG (nh/oscfit.py + nh/gamma.py incl. nh/dynamics.py, IAAFT-normalised).

  fingerprint d   standardised effect at k = 0.5: (mean_k0.5 - mean_k0) / pooled SD   (same scale as a
                  real patient-vs-control Hedges-type effect)
  slope, t        paired per-subject slope of the feature on k, its mean and t across subjects
  sign            "+" / "-" if |t| >= slope_t_threshold, else "0"

Comparison of a real effect vector D (one adjusted standardised effect per feature) with fingerprints:
  cosine(D, F_t) per theory, and a non-negative least-squares mix D ~ sum_t w_t F_t / |F_t|, giving
  each theory's share and the LOCAL-LOOP share (T1, T2, T5) vs INPUT-DRIVEN share (T3, T4, T6).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import nnls

from . import cyclemodel, mechsim
from .gamma import gii_subject
from .oscfit import channel_oscillation


# ------------------------------------------------------------------------------- simulation
def simulate_family(family: str, theories: list[str], levels: list[float], seeds: int, dur_s: float,
                    master_seed: int = 0, fs: float = 250.0) -> list[dict]:
    """Returns [{family, theory, k, seed, signal}] with a SHARED baseline (k = 0) per seed."""
    specs = [(None, 0.0)] + [(t, k) for t in theories for k in levels if k > 0]
    out = []
    if family == "rate":
        params, drives, meta = [], [], []
        for j in range(seeds):
            base = mechsim.subject_base(np.random.default_rng([master_seed, 11, j]))
            for t, k in specs:
                p, d = mechsim.knob_params(t, k, base)
                params.append(p); drives.append(d); meta.append((t, k, j))
        X = mechsim.simulate_circuit(params, drives, dur_s=dur_s, fs_out=fs, seed=master_seed)
        for (t, k, j), x in zip(meta, X):
            out.append({"family": family, "theory": t or "baseline", "k": k, "seed": j, "signal": x})
    elif family == "cycle":
        for j in range(seeds):
            base = cyclemodel.subject_base(np.random.default_rng([master_seed, 12, j]))
            for t, k in specs:
                x = cyclemodel.simulate_cycles(t, k, dur_s=dur_s, fs=fs, seed=hash((master_seed, j, t, k)) % 2**31,
                                               base=base)
                out.append({"family": family, "theory": t or "baseline", "k": k, "seed": j, "signal": x})
    else:
        raise KeyError(family)
    return out


def measure(sim: dict, cfg_feat: dict, gamma_snr: float, n_surr: int, master_seed: int = 0,
            primary: str | None = None, fs: float = 250.0) -> dict:
    """Mix one simulated circuit into the subject's background and extract the real-data features."""
    j = sim["seed"]
    srng = np.random.default_rng([master_seed, 13, j])              # the SAME background per subject
    snr = gamma_snr * float(np.exp(srng.normal(0, 0.3)))
    chi = float(np.clip(srng.normal(1.5, 0.2), 0.8, 2.5))
    x = mechsim.add_background(sim["signal"], fs, srng, gamma_snr=snr, chi=chi)
    seg = [(0, len(x))]
    feats = channel_oscillation(x, seg, fs, cfg_feat)
    g = gii_subject(x[None], seg, fs, ["sim"], cfg_feat["gamma_band"], cfg_feat,
                    np.random.default_rng([master_seed, 14, j, int(sim["k"] * 100)]), n_surr=n_surr)["sim"]
    feats.update(g)
    rec = {k: v for k, v in sim.items() if k != "signal"}
    rec.update(gamma_snr=snr, chi=chi, **feats)
    if primary:
        rec["primary"] = feats.get(primary, np.nan)
    return rec


# ------------------------------------------------------------------------------ fingerprints
def fingerprints(df: pd.DataFrame, features: list[str], t_thr: float = 3.0, k_ref: float = 0.5) -> pd.DataFrame:
    rows = []
    for (fam, th), d in df[df.theory != "baseline"].groupby(["family", "theory"]):
        base = df[(df.family == fam) & (df.theory == "baseline")]
        dd = pd.concat([base, d], ignore_index=True)          # shared k = 0 row for every subject
        for f in features:
            if f not in dd:
                continue
            piv = dd.pivot_table(index="seed", columns="k", values=f, aggfunc="first")
            if piv.empty or 0.0 not in piv.columns or piv.shape[1] < 2:
                continue
            ks = np.array(piv.columns, float)
            slopes = []
            for _, r in piv.iterrows():
                ok = np.isfinite(r.values)
                if ok.sum() >= 3:
                    slopes.append(np.polyfit(ks[ok], r.values[ok], 1)[0])
            slopes = np.asarray(slopes)
            b0 = piv[0.0].dropna() if 0.0 in piv else pd.Series(dtype=float)
            kr = min(piv.columns, key=lambda c: abs(c - k_ref))
            b1 = piv[kr].dropna()
            sd = np.sqrt(0.5 * (b0.var(ddof=1) + b1.var(ddof=1))) if len(b0) > 2 and len(b1) > 2 else np.nan
            m = slopes.mean() if len(slopes) else np.nan
            t = m / (slopes.std(ddof=1) / np.sqrt(len(slopes))) if len(slopes) > 2 and slopes.std() > 0 else np.nan
            sign = "+" if (np.isfinite(t) and t >= t_thr) else ("-" if (np.isfinite(t) and t <= -t_thr) else "0")
            rows.append({"family": fam, "theory": th, "feature": f, "slope": m, "t": t, "sign": sign,
                         "d_at_k": (b1.mean() - b0.mean()) / sd if sd and np.isfinite(sd) and sd > 0 else np.nan,
                         "k_ref": kr, "n_subjects": len(slopes)})
    return pd.DataFrame(rows)


def agreement(fp: pd.DataFrame) -> pd.DataFrame:
    """Per theory x feature: do the two families agree on the direction?"""
    piv = fp.pivot_table(index=["theory", "feature"], columns="family", values="sign", aggfunc="first")
    def verdict(r):
        s = [v for v in r.values if isinstance(v, str)]
        if len(s) < 2:
            return "single_family"
        if s[0] == s[1]:
            return "firm_" + {"+": "up", "-": "down", "0": "none"}[s[0]]
        if "0" in s:
            return "weak_" + ("up" if "+" in s else "down")
        return "conflict"
    piv["verdict"] = piv.apply(verdict, axis=1)
    return piv.reset_index()


def fingerprint_matrix(fp: pd.DataFrame, family: str, features: list[str]) -> pd.DataFrame:
    """theory x feature matrix of standardised effects (d at k_ref) for one family."""
    m = fp[fp.family == family].pivot_table(index="theory", columns="feature", values="d_at_k", aggfunc="first")
    return m.reindex(columns=[f for f in features if f in m.columns])


# --------------------------------------------------------------------------------- comparison
def compare(effect: pd.Series, F: pd.DataFrame, local: list[str], inputs: list[str]) -> dict:
    """effect: feature -> standardised effect (real data). F: theory x feature fingerprint matrix."""
    feats = [f for f in F.columns if f in effect.index and np.isfinite(effect[f]) and F[f].notna().all()]
    if len(feats) < 3:
        return {"n_features": len(feats)}
    D = effect[feats].values.astype(float)
    M = F[feats].values.astype(float)
    norms = np.linalg.norm(M, axis=1); norms[norms == 0] = np.nan
    U = (M.T / norms).T
    cos = {th: float(np.dot(D, U[i]) / (np.linalg.norm(D) + 1e-12)) for i, th in enumerate(F.index)}
    ok = np.isfinite(norms)
    w = np.zeros(len(F.index))
    if ok.any():
        w[ok], resid = nnls(U[ok].T, D)
    tot = w.sum()
    share = {th: float(w[i] / tot) if tot > 0 else np.nan for i, th in enumerate(F.index)}
    loc = sum(share.get(t, 0) for t in local if t in share) if tot > 0 else np.nan
    inp = sum(share.get(t, 0) for t in inputs if t in share) if tot > 0 else np.nan
    fit = U[ok].T @ w[ok] if ok.any() else np.zeros_like(D)
    return {"n_features": len(feats), "features": feats, "cosine": cos, "weight": dict(zip(F.index, w.tolist())),
            "share": share, "local_share": loc, "input_share": inp,
            "best_single": max(cos, key=cos.get),
            "r2_mix": float(1 - np.sum((D - fit) ** 2) / (np.sum(D ** 2) + 1e-12))}


def effect_vector(pat: pd.DataFrame, ctl: pd.DataFrame, features: list[str]) -> pd.Series:
    """Standardised mean difference per feature (pooled SD), NaN-safe."""
    out = {}
    for f in features:
        a, b = pat[f].dropna(), ctl[f].dropna()
        if len(a) > 2 and len(b) > 2:
            sd = np.sqrt(((len(a) - 1) * a.var() + (len(b) - 1) * b.var()) / (len(a) + len(b) - 2))
            out[f] = (a.mean() - b.mean()) / sd if sd > 0 else np.nan
    return pd.Series(out, dtype=float)


def recovery(df_test: pd.DataFrame, F: pd.DataFrame, features: list[str], local: list[str], inputs: list[str],
             n_pat: int, n_ctl: int, R: int, k_ref: float, rng: np.random.Generator) -> dict:
    """Simulate studies of our size where ONE mechanism is true; does the comparison find it?"""
    theories = list(F.index)
    ctl_pool = df_test[df_test.theory == "baseline"]
    conf = pd.DataFrame(0, index=theories, columns=theories)
    split_ok, n = 0, 0
    for th in theories:
        pool = df_test[(df_test.theory == th) & (np.isclose(df_test.k, k_ref))]
        if len(pool) < 3 or len(ctl_pool) < 3:
            continue
        for _ in range(R):
            P = pool.sample(n_pat, replace=True, random_state=int(rng.integers(2**31)))
            C = ctl_pool.sample(n_ctl, replace=True, random_state=int(rng.integers(2**31)))
            res = compare(effect_vector(P, C, features), F, local, inputs)
            if "best_single" not in res:
                continue
            conf.loc[th, res["best_single"]] += 1
            truth_local = th in local
            if np.isfinite(res["local_share"]):
                split_ok += int((res["local_share"] > 0.5) == truth_local); n += 1
    acc = {th: float(conf.loc[th, th] / conf.loc[th].sum()) if conf.loc[th].sum() else np.nan for th in theories}
    return {"confusion": conf.to_dict(), "accuracy_per_theory": acc,
            "local_vs_input_accuracy": float(split_ok / n) if n else np.nan}
