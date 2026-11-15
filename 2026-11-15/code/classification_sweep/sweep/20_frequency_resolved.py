"""Stage 20 (labels, EXPLORATORY): where in frequency x scalp do the groups differ?

For every spectrum family from stage 10 and every contrast, a Freedman-Lane permutation cluster test over
(frequency x channel) with channel adjacency from the 10-20 montage. Each node's statistic is the HC0 t of
the group term after age and sex (optionally + per-subject EMG). Clusters are formed from |t| > t at
two-sided p < 0.01, separately for each sign; cluster mass = sum |t|; FWER over the whole map by the
permutation distribution of the maximum cluster mass.

Also reported for each map, a priori: the 35-45 Hz window (max |t|, ROI mean difference, whether any
significant cluster touches it), and the vigilance-stratified ROI gamma test (E4).
Outputs: results/<ds>/<variant>/freq/{clusters.csv, window_35_45.csv, vigilance_strata.csv, *.png, tmaps.npz}
"""
from __future__ import annotations
import argparse, json
import numpy as np, pandas as pd
from scipy import sparse
from scipy.sparse.csgraph import connected_components
from scipy.stats import t as tdist
from common import variant_dir, participants, OUT, ROI, FMAX_ANALYSIS

FAMILIES = {   # name: (array key, frequency key, fmin)
    "logpsd_csd": ("logpsd_csd", "freqs", 1.0),
    "logpsd_avg": ("logpsd_avg", "freqs", 1.0),
    "logpsd_csd_lowemg50": ("logpsd_csd_lowemg50", "freqs", 1.0),
    "logpsd_csd_lowemg25": ("logpsd_csd_lowemg25", "freqs", 1.0),
    # PRIMARY periodic/aperiodic split: specparam-knee (names kept so the verdict rules read the same)
    "periodic_csd": ("sp_periodic_csd", "sp_freqs", 2.0),
    "fractal_csd": ("sp_aperiodic_csd", "sp_freqs", 2.0),
    "periodic_avg": ("sp_periodic_avg", "sp_freqs", 2.0),
    # SECONDARY: IRASA (shown for comparison; it leaks neighbouring peaks into the fractal part)
    "irasa_periodic_csd": ("irasa_periodic_csd", "irasa_freqs", 2.0),
    "irasa_fractal_csd": ("irasa_fractal_csd", "irasa_freqs", 2.0),
}
CONTRASTS = [("AD", "CN"), ("FTD", "CN"), ("AD", "FTD")]


def ch_adjacency(ch_names):
    import mne
    info = mne.create_info(ch_names, 250.0, "eeg")
    info.set_montage("standard_1020", on_missing="ignore", verbose="ERROR")
    adj, names = mne.channels.find_ch_adjacency(info, "eeg")
    assert list(names) == list(ch_names)
    return adj


def grid_adjacency(n_f, ch_adj):
    """Nodes ordered f-major (node = fi * n_ch + ci): neighbours are adjacent channels at the same frequency
    and the same channel at adjacent frequency bins."""
    n_ch = ch_adj.shape[0]
    a_f = sparse.diags([1, 1], [-1, 1], shape=(n_f, n_f))
    return (sparse.kron(sparse.eye(n_f), ch_adj) + sparse.kron(a_f, sparse.eye(n_ch))).tocsr()


def ols_t(Y, X, j):
    """t of column j of X for every column of Y (HC0 robust SE), vectorized."""
    XtXi = np.linalg.pinv(X.T @ X)
    B = XtXi @ X.T @ Y
    R = Y - X @ B
    h = (XtXi @ X.T)[j]                                   # row of (X'X)^-1 X'
    se = np.sqrt((h[:, None] ** 2 * R ** 2).sum(0))
    return B[j] / np.maximum(se, 1e-300)


def clusters_of(t, thr, adj):
    out = []
    for sign in (1, -1):
        nodes = np.flatnonzero(sign * t > thr)
        if len(nodes) == 0:
            continue
        sub = adj[nodes][:, nodes]
        n, lab = connected_components(sub, directed=False)
        for k in range(n):
            idx = nodes[lab == k]
            out.append((sign, idx, float(np.abs(t[idx]).sum())))
    return out


def fl_cluster_test(Y, X, j, adj, n_perm, rng, p_node=0.01):
    df = X.shape[0] - X.shape[1]
    thr = tdist.ppf(1 - p_node / 2, df)
    t_obs = ols_t(Y, X, j)
    cl = clusters_of(t_obs, thr, adj)
    Xr = np.delete(X, j, axis=1)
    Br = np.linalg.pinv(Xr) @ Y
    Fr, Rr = Xr @ Br, Y - Xr @ Br
    null = np.zeros(n_perm)
    for b in range(n_perm):
        tp = ols_t(Fr + Rr[rng.permutation(len(Rr))], X, j)
        cp = clusters_of(tp, thr, adj)
        null[b] = max((c[2] for c in cp), default=0.0)
    res = [(s, idx, m, (np.sum(null >= m) + 1) / (n_perm + 1)) for s, idx, m in cl]
    return t_obs, sorted(res, key=lambda r: r[3]), thr


def load_variant(dataset, variant):
    d = variant_dir(dataset, variant) / "feat"
    zs = {f.stem: np.load(f) for f in sorted(d.glob("sub-*.npz")) if not f.name.endswith(".tmp.npz")}
    return zs


def plot_map(t, f, chs, sig_mask, title, path):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 4.2))
    v = np.nanmax(np.abs(t))
    im = ax.imshow(t.T, aspect="auto", origin="lower", cmap="RdBu_r", vmin=-v, vmax=v,
                   extent=[f[0], f[-1], -0.5, len(chs) - 0.5])
    if sig_mask.any():
        ax.contour(f, np.arange(len(chs)), sig_mask.T.astype(float), levels=[0.5], colors="k", linewidths=1)
    ax.axvspan(35, 45, color="gold", alpha=0.12)
    ax.set_yticks(range(len(chs))); ax.set_yticklabels(chs, fontsize=7)
    ax.set_xlabel("Hz"); ax.set_title(title, fontsize=10)
    fig.colorbar(im, ax=ax, label="t (group, adj.)")
    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="ds004504")
    ap.add_argument("--variant", default="main")
    ap.add_argument("--n-perm", type=int, default=2000)
    ap.add_argument("--families", nargs="*", default=list(FAMILIES))
    a = ap.parse_args()
    rng = np.random.default_rng(20261115)
    zs = load_variant(a.dataset, a.variant)
    P = participants(a.dataset)
    subs = [s for s in zs if s in P.index]
    first = zs[subs[0]]
    chs = [str(c) for c in first["ch_names"]]
    roi = [chs.index(c) for c in ROI if c in chs]
    adj_ch = ch_adjacency(chs)
    out = OUT / a.dataset / a.variant / "freq"; out.mkdir(parents=True, exist_ok=True)
    emg = pd.Series({s: float(np.mean(zs[s]["emg_epoch_csd"])) for s in subs})
    rows_c, rows_w, tmaps = [], [], {}
    for fam in a.families:
        key, fkey, fmin = FAMILIES[fam]
        f_all = first[fkey]; fm = (f_all >= fmin) & (f_all <= FMAX_ANALYSIS)
        f = f_all[fm]
        arr = np.stack([zs[s][key][:, fm] for s in subs])            # n, ch, f
        adj = grid_adjacency(len(f), adj_ch)
        for tgt, ref in CONTRASTS:
            for cov_name, covs in (("age_sex", ["age", "sex_m"]), ("age_sex_emg", ["age", "sex_m", "emg"])):
                if cov_name == "age_sex_emg" and fam not in ("logpsd_csd", "periodic_csd"):
                    continue
                sel = [i for i, s in enumerate(subs) if P.loc[s, "group"] in (tgt, ref)
                       and np.all(np.isfinite(arr[i]))]          # a failed spectral fit drops that subject
                ss = [subs[i] for i in sel]
                C = P.loc[ss, ["age", "sex_m"]].astype(float).copy()
                if "emg" in covs:
                    C["emg"] = emg.loc[ss].values
                C = (C - C.mean()) / C.std(ddof=0).replace(0, 1)
                g = (P.loc[ss, "group"] == tgt).astype(float).values
                X = np.column_stack([np.ones(len(ss)), C.values, g])
                Y = arr[sel].transpose(0, 2, 1).reshape(len(ss), -1)    # f-major nodes
                t, cl, thr = fl_cluster_test(Y, X, X.shape[1] - 1, adj, a.n_perm, rng)
                T = t.reshape(len(f), len(chs))
                sig = np.zeros(T.size, bool)
                for s_, idx, m, p in cl:
                    fi, ci = np.unravel_index(idx, T.shape)
                    if p < 0.05:
                        sig[idx] = True
                    rows_c.append(dict(family=fam, contrast=f"{tgt}-{ref}", covariates=cov_name, sign=int(s_),
                                       mass=m, p_fwer=p, f_lo=float(f[fi.min()]), f_hi=float(f[fi.max()]),
                                       f_peak=float(f[fi[np.argmax(np.abs(t[idx]))]]),
                                       ch_peak=chs[ci[np.argmax(np.abs(t[idx]))]],
                                       n_nodes=len(idx), channels=" ".join(sorted({chs[c] for c in ci}))))
                S = sig.reshape(T.shape)
                w = (f >= 35) & (f <= 45)
                diff = arr[sel][g == 1][:, roi][:, :, w].mean() - arr[sel][g == 0][:, roi][:, :, w].mean()
                rows_w.append(dict(family=fam, contrast=f"{tgt}-{ref}", covariates=cov_name, n=len(ss),
                                   max_abs_t_35_45=float(np.abs(T[w]).max()),
                                   roi_mean_t_35_45=float(T[w][:, roi].mean()),
                                   roi_diff_log10_35_45=float(diff),
                                   sig_cluster_in_35_45=bool(S[w].any()),
                                   frac_35_45_nodes_sig=float(S[w].mean())))
                tmaps[f"{fam}|{tgt}-{ref}|{cov_name}"] = T
                if cov_name == "age_sex":
                    plot_map(T, f, chs, S, f"{a.dataset}/{a.variant}  {fam}  {tgt} vs {ref} (age, sex)",
                             out / f"tmap_{fam}_{tgt}-{ref}.png")
        print(f"[20] {fam} done", flush=True)
    pd.DataFrame(rows_c).to_csv(out / "clusters.csv", index=False)
    pd.DataFrame(rows_w).to_csv(out / "window_35_45.csv", index=False)
    np.savez_compressed(out / "tmaps.npz", **{k.replace("|", "__"): v for k, v in tmaps.items()})

    # ---- E4: ROI 30-45 Hz power inside label-free global vigilance strata
    vig = np.concatenate([zs[s]["vigilance_epoch_csd"] for s in subs])
    edges = np.quantile(vig, [0, .25, .5, .75, 1.0]); edges[0] -= 1e-9; edges[-1] += 1e-9
    rows_v = []
    for s in subs:
        v = zs[s]["vigilance_epoch_csd"]; gm = zs[s]["gamma_epoch_csd"][roi].mean(0)
        k = np.digitize(v, edges[1:-1])
        row = {"subject": s, "group": P.loc[s, "group"], "age": P.loc[s, "age"], "sex_m": P.loc[s, "sex_m"]}
        for q in range(4):
            row[f"n_q{q + 1}"] = int((k == q).sum())
            row[f"gamma_q{q + 1}"] = float(gm[k == q].mean()) if (k == q).sum() >= 8 else np.nan
        rows_v.append(row)
    V = pd.DataFrame(rows_v).set_index("subject")
    tests = []
    for tgt, ref in CONTRASTS:
        for q in range(1, 5):
            x = V[V.group.isin([tgt, ref])].dropna(subset=[f"gamma_q{q}"])
            if min((x.group == tgt).sum(), (x.group == ref).sum()) < 4:
                tests.append(dict(contrast=f"{tgt}-{ref}", stratum=q, n=len(x), t=np.nan, p_perm=np.nan)); continue
            X = np.column_stack([np.ones(len(x)), (x[["age", "sex_m"]] - x[["age", "sex_m"]].mean()).values,
                                 (x.group == tgt).astype(float).values])
            Y = x[[f"gamma_q{q}"]].values
            t0 = ols_t(Y, X, 3)[0]
            Xr = X[:, :3]; Br = np.linalg.pinv(Xr) @ Y; Fr, Rr = Xr @ Br, Y - Xr @ Br
            null = np.array([ols_t(Fr + Rr[rng.permutation(len(Rr))], X, 3)[0] for _ in range(a.n_perm)])
            tests.append(dict(contrast=f"{tgt}-{ref}", stratum=q, n=len(x), t=float(t0),
                              p_perm=float((np.sum(np.abs(null) >= abs(t0)) + 1) / (a.n_perm + 1))))
    V.to_csv(out / "vigilance_strata_subjects.csv")
    occ = V.groupby("group")[[f"n_q{q}" for q in range(1, 5)]].mean()
    pd.DataFrame(tests).to_csv(out / "vigilance_strata.csv", index=False)
    json.dump({"vigilance_edges": edges.tolist(), "epochs_per_stratum_by_group": occ.round(1).to_dict()},
              open(out / "vigilance_meta.json", "w"), indent=1)
    print("[20] done ->", out)


if __name__ == "__main__":
    main()
