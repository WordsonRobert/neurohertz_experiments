"""Stage 50 (labels, EXPLORATORY): which mechanism family carries diagnostic information, and does anything
add to slowing + aperiodic?

Repeated stratified 5-fold CV (20 repeats), L2 logistic with inner 5-fold choice of C, class_weight balanced.
Every data-driven step is fit on the training fold only: scaling, C, and (for the burst family) the burst-type
Gaussian mixture (refit per fold on training subjects' bursts, K fixed from stage 30, which used no labels).
Reported: AUC, balanced accuracy, accuracy (threshold 0 on the decision function), permutation p (whole CV
pipeline on permuted labels), and AUC gain over the slowing + aperiodic baseline (paired over repeats).
"""
from __future__ import annotations
import argparse, json, warnings
import numpy as np, pandas as pd
from joblib import Parallel, delayed
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics import roc_auc_score, balanced_accuracy_score, accuracy_score
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from common import participants, OUT

FAMILIES = {
    "slowing": ["theta_alpha", "iaf"],
    "aperiodic": ["fractal_slope", "fractal_offset"],
    "gamma_periodic": ["periodic_35_45", "periodic_30_48", "logpow_35_45_lowemg"],
    "bursts": ["burst_excess_roi", "__burst_types__"],
    "coupling": ["pac_theta_z", "pac_alpha_z", "alpha_1to4_z"],
    "transients": ["transient_rate", "gamma_no_transient_delta"],
    "muscle": ["emg_mean"],
}
MODELS = {
    "slowing": ["slowing"], "aperiodic": ["aperiodic"], "gamma_periodic": ["gamma_periodic"],
    "bursts": ["bursts"], "coupling": ["coupling"], "transients": ["transients"], "muscle": ["muscle"],
    "BASE slowing+aperiodic": ["slowing", "aperiodic"],
    "BASE+gamma_periodic": ["slowing", "aperiodic", "gamma_periodic"],
    "BASE+bursts": ["slowing", "aperiodic", "bursts"],
    "BASE+coupling": ["slowing", "aperiodic", "coupling"],
    "ALL": list(FAMILIES),
}
SEED = 20261115


def burst_rates(B, subs_train, subs_all, model_meta, seed):
    """Fit the burst-type GMM on training subjects only; return type shares for all subjects."""
    desc, K = model_meta["desc"], model_meta["K"]
    rng = np.random.default_rng(seed)
    Bt = B[B.subject.isin(subs_train)]
    idx = []
    for _, g in Bt.groupby("subject"):
        idx += list(rng.choice(g.index.to_numpy(), min(200, len(g)), replace=False))
    mu, sd = Bt.loc[idx, desc].mean(), Bt.loc[idx, desc].std()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        g = GaussianMixture(K, covariance_type="full", n_init=2, random_state=seed, reg_covar=1e-4).fit(
            ((Bt.loc[idx, desc] - mu) / sd).values)
    Ba = B[B.subject.isin(subs_all)]
    lab = g.predict(((Ba[desc] - mu) / sd).values)
    tab = pd.crosstab(Ba.subject.values, lab, normalize="index").reindex(index=subs_all, columns=range(K)).fillna(0)
    return tab.values[:, :-1]          # K-1 shares (they sum to one)


def cv_once(X, y, subs, B, meta, use_bursts, rep, perm=None):
    yv = y if perm is None else perm
    skf = StratifiedKFold(5, shuffle=True, random_state=SEED + rep)
    s = np.zeros(len(yv))
    for k, (tr, te) in enumerate(skf.split(X, yv)):
        Xtr, Xte = X[tr], X[te]
        if use_bursts:
            R = burst_rates(B, [subs[i] for i in tr], subs, meta, SEED + 100 * rep + k)
            Xtr = np.column_stack([Xtr, R[tr]]) if Xtr.size else R[tr]
            Xte = np.column_stack([Xte, R[te]]) if Xte.size else R[te]
        sc = StandardScaler().fit(Xtr)
        m = LogisticRegressionCV(Cs=np.logspace(-3, 2, 11), cv=5, class_weight="balanced", max_iter=5000,
                                 scoring="roc_auc").fit(sc.transform(Xtr), yv[tr])
        s[te] = m.decision_function(sc.transform(Xte))
    return roc_auc_score(yv, s), balanced_accuracy_score(yv, s > 0), accuracy_score(yv, s > 0)


def run_model(name, fams, D, y, subs, B, meta, n_rep, n_perm, jobs):
    cols = [c for f in fams for c in FAMILIES[f] if c != "__burst_types__"]
    use_b = any("__burst_types__" in FAMILIES[f] for f in fams) and B is not None
    X = D[cols].to_numpy(float) if cols else np.empty((len(D), 0))
    reps = Parallel(n_jobs=jobs)(delayed(cv_once)(X, y, subs, B, meta, use_b, r) for r in range(n_rep))
    reps = np.asarray(reps)
    rng = np.random.default_rng(SEED)
    perms = [rng.permutation(y) for _ in range(n_perm)]
    null = Parallel(n_jobs=jobs)(delayed(cv_once)(X, y, subs, B, meta, use_b, i % n_rep, p) for i, p in enumerate(perms))
    null = np.asarray(null)[:, 0] if n_perm else np.array([])
    return dict(model=name, n_features=len(cols) + (meta["K"] - 1 if use_b else 0),
                auc=reps[:, 0].mean(), auc_lo=np.percentile(reps[:, 0], 2.5), auc_hi=np.percentile(reps[:, 0], 97.5),
                bal_acc=reps[:, 1].mean(), acc=reps[:, 2].mean(),
                p_perm=(np.sum(null >= reps[:, 0].mean()) + 1) / (n_perm + 1) if n_perm else np.nan), reps[:, 0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="ds004504")
    ap.add_argument("--variant", default="main")
    ap.add_argument("--burst-threshold", default="p95")
    ap.add_argument("--n-rep", type=int, default=20)
    ap.add_argument("--n-perm", type=int, default=200)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--contrasts", nargs="*", default=["AD-CN", "FTD-CN", "AD-FTD"])
    a = ap.parse_args()
    base = OUT / a.dataset / a.variant
    out = base / "predict"; out.mkdir(parents=True, exist_ok=True)
    st = pd.read_csv(base / "subject_table.csv", index_col=0)
    P = participants(a.dataset)
    B, meta = None, None
    mp = base / f"bursts_{a.burst_threshold}" / "typing_model.joblib"
    if mp.exists():
        import joblib, importlib.util, sys
        from pathlib import Path
        spec = importlib.util.spec_from_file_location("b30", Path(__file__).with_name("30_burst_types.py"))
        b30 = importlib.util.module_from_spec(spec); spec.loader.exec_module(b30)
        meta = joblib.load(mp)
        B = b30.load_bursts(a.dataset, a.variant)
        if a.burst_threshold == "p99":
            B = B[B.above99].reset_index(drop=True)
    rows = []
    for con in a.contrasts:
        tgt, ref = con.split("-")
        D = P[P.group.isin([tgt, ref])].join(st, how="inner").dropna(subset=[c for f in FAMILIES.values() for c in f if c in st])
        subs = list(D.index); y = (D.group == tgt).astype(int).to_numpy()
        aucs = {}
        for name, fams in MODELS.items():
            r, au = run_model(name, fams, D, y, subs, B if "bursts" in fams else None, meta, a.n_rep, a.n_perm, a.jobs)
            r["contrast"] = con; r["n"] = len(D); rows.append(r); aucs[name] = au
            print(f"[50] {con} {name}: AUC {r['auc']:.3f} bal.acc {r['bal_acc']:.3f} p {r['p_perm']:.3f}", flush=True)
        for name in [m for m in MODELS if m.startswith("BASE+") or m == "ALL"]:
            d = aucs[name] - aucs["BASE slowing+aperiodic"]
            for r in rows:
                if r["contrast"] == con and r["model"] == name:
                    r.update(gain_vs_base=d.mean(), gain_lo=np.percentile(d, 2.5), gain_hi=np.percentile(d, 97.5),
                             frac_repeats_gain_gt0=float((d > 0).mean()))
    pd.DataFrame(rows).to_csv(out / "prediction.csv", index=False)
    print("[50] done ->", out)


if __name__ == "__main__":
    main()
