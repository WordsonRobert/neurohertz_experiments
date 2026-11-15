"""Stage B: pre-registered mechanistic tests + fingerprint comparison (labels via the gate only).

Reads config `mechanism` (tests, predictions, covariates, thresholds), Stage-A features and the frozen
fingerprints (results/mechanism/fingerprints.json from 13_mechanism_fingerprints.py).

Order of operations (nothing here is chosen after seeing results):
  0. Oscillation-presence gate. A subject "has gamma" if >= roi_fraction of its ROI channels pass the
     presence test (nh/oscfit.py). If < min_present_fraction of subjects pass in ANY group, every
     mechanistic result is labelled DESCRIPTIVE (a limitation, not evidence). Main tests use only
     subjects with gamma (restrict_to_present); the all-subject version is reported alongside.
  1. Every pre-registered test M01..M17, with covariates (age, sex): Freedman-Lane permutation for group
     effects, partial Spearman for correlations, equivalence (TOST via 90% bootstrap CI within the
     smallest effect of interest) for "no difference" predictions. Holm across all tests.
  2. Sensitivity: each group test re-run adding muscle, vigilance and recording-length covariates.
  3. Scorecard: for each theory, each test's outcome = consistent / inconsistent / inconclusive, for the
     VERBAL prediction (config) and the MODEL prediction (where both simulator families agree).
  4. Fingerprint comparison: the adjusted AD-vs-CN effect vector against each family's fingerprints;
     cosine per theory, NNLS shares, LOCAL-LOOP vs INPUT-DRIVEN share with bootstrap CI and a label
     permutation test. A local/input claim is made only if (a) both families agree, (b) the bootstrap
     CI excludes 0.5 and (c) identifiability (13_...) showed >= 0.8 within- and >= 0.7 cross-family accuracy.

Usage
  python scripts/14_mechanism_tests.py --dataset ds004504 [--dev-unblind-reason "..."]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nh.config import FREEZE_PATH, ROOT, analysis_hash, load_config, sha256_file  # noqa: E402
from nh.datasets import get_adapter  # noqa: E402
from nh.fingerprint import compare  # noqa: E402
from nh.labels import open_labels  # noqa: E402
from nh.stats import design, group_effect, hedges_g, hedges_g_bca, holm, partial_spearman  # noqa: E402


# ----------------------------------------------------------------------------- helpers
def _resid(df: pd.DataFrame, y: str, covars: list[str]) -> np.ndarray:
    Z = design(df, covars).values
    yv = df[y].astype(float).values
    return yv - Z @ np.linalg.lstsq(Z, yv, rcond=None)[0]


def adjusted_g(df, y, tgt, ref, covars, n_boot, rng):
    """Hedges g on covariate-residualised values (covariates fitted in the pooled two groups),
    with 90% (for equivalence) and 95% BCa intervals."""
    d = df[df.group.isin([tgt, ref])].dropna(subset=[y] + [c for c in covars if c in df])
    r = _resid(d, y, covars)
    a, b = r[(d.group == tgt).values], r[(d.group == ref).values]
    if len(a) < 3 or len(b) < 3:
        return np.nan, [np.nan] * 2, [np.nan] * 2
    return hedges_g(a, b), hedges_g_bca(a, b, n_boot, rng, 0.90), hedges_g_bca(a, b, n_boot, rng, 0.95)


def _ols_beta(df, y, covars, term="_grp"):
    X = design(df, covars); X[term] = df[term].values
    return float(sm.OLS(df[y].astype(float).values, X.values).fit().params[-1])


def classify(pred: str, est: float, p_adj: float, equivalent: bool | None, alpha: float) -> str:
    if pred not in ("+", "-", "0"):
        return "no_prediction"
    if not np.isfinite(est) or not np.isfinite(p_adj):
        return "not_run"
    sig = p_adj < alpha
    if pred == "0":
        return "consistent" if equivalent else ("inconsistent" if sig else "inconclusive")
    want = 1 if pred == "+" else -1
    if sig and np.sign(est) == want:
        return "consistent"
    if (sig and np.sign(est) == -want) or equivalent:
        return "inconsistent"
    return "inconclusive"


def model_predictions(fp_json: dict | None) -> dict:
    """feature -> {theory_name: '+'|'-'|'0'|'?'} where BOTH families agree (firm_*)."""
    if not fp_json:
        return {}
    out = {}
    for r in fp_json.get("agreement", []):
        v = r.get("verdict", "")
        out.setdefault(r["feature"], {})[r["theory"]] = {"firm_up": "+", "firm_down": "-", "firm_none": "0"}.get(v, "?")
    return out


# ------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="ds004504")
    ap.add_argument("--variant", default="primary")
    ap.add_argument("--dev-unblind-reason", default=None)
    ap.add_argument("--fingerprints", default=str(ROOT / "results" / "mechanism" / "fingerprints.json"))
    a = ap.parse_args()
    cfg = load_config(); mc = cfg["mechanism"]; st = cfg["statistics"]
    primary = st["primary_feature"]; alpha = st["alpha"]
    names = mc["theories"]                                   # T1 -> synapses_onto_pv ...
    covars = mc["covariates"]
    rng = np.random.default_rng(st["seed"])
    fdir = ROOT / "results" / "features" / a.dataset / a.variant
    odir = ROOT / "results" / "analysis" / a.dataset / a.variant / "mechanism"
    odir.mkdir(parents=True, exist_ok=True)

    feats = pd.read_csv(fdir / "features_subject.csv")
    qc = pd.read_csv(fdir / "qc.csv")
    qnum = qc[["subject"] + [c for c in qc.columns if c != "subject" and pd.api.types.is_numeric_dtype(qc[c])]]
    qnum = qnum.rename(columns={c: f"qc__{c}" for c in qnum.columns if c != "subject"})
    labels = open_labels(get_adapter(a.dataset), purpose="mechanism tests", dev_unblind_reason=a.dev_unblind_reason)
    status = labels.attrs.get("evidence_status", "EXPLORATORY")
    D = labels.merge(feats, on="subject").merge(qnum, on="subject", how="left")
    if "sex" in D and not pd.api.types.is_numeric_dtype(D["sex"]):
        D["sex"] = D["sex"].astype(str).str.upper().str[0].map({"M": 1.0, "F": 0.0})

    # fingerprints: must be the frozen ones for a confirmatory reading
    fp_json, fp_status = None, "MISSING"
    fpp = Path(a.fingerprints)
    if fpp.exists():
        fp_json = json.loads(fpp.read_text())
        fp_status = "EXPLORATORY"
        if FREEZE_PATH.exists() and json.loads(FREEZE_PATH.read_text()).get("mechanism_fingerprints_sha256") == sha256_file(fpp):
            fp_status = "FROZEN"
        if fp_json.get("quick"):
            fp_status = "QUICK_RUN_NOT_VALID"

    # ---------------------------------------------------------------- 0. presence gate
    pres_col = "roi__osc_present"
    pc = mc["presence"]
    D["has_gamma"] = D[pres_col] >= pc["roi_fraction"] if pres_col in D else True
    pres = D.groupby("group")["has_gamma"].agg(["sum", "count", "mean"]).rename(
        columns={"sum": "n_with_gamma", "count": "n", "mean": "fraction"})
    pres.to_csv(odir / "presence.csv")
    min_frac = float(pres["fraction"].min())
    mech_status = "PRIMARY" if min_frac >= pc["min_present_fraction"] else "DESCRIPTIVE_ONLY"
    print(pres.to_string()); print("mechanistic status:", mech_status)

    def run_all(df: pd.DataFrame, tag: str) -> pd.DataFrame:
        rows = []
        for t in mc["tests"]:
            f = t["feature"].replace("{primary}", primary)
            row = {"id": t["id"], "name": t["name"], "kind": t["kind"], "feature": f, "subset": tag}
            try:
                if t["kind"] in ("group", "matched_severity", "region_contrast", "paired_delta", "attenuation"):
                    tgt, ref = t["contrast"]
                    dd = df.copy()
                    cv = list(covars)
                    if t["kind"] == "region_contrast":
                        r1, r2 = t["regions"]
                        y = f"{r1}_minus_{r2}__{f}"
                        dd[y] = dd[f"{r1}__{f}"] - dd[f"{r2}__{f}"]
                    elif t["kind"] == "paired_delta":
                        pfile = ROOT / "results" / "features" / t["paired_dataset"] / a.variant / "features_subject.csv"
                        if not pfile.exists():
                            row["note"] = f"paired features not found ({pfile.relative_to(ROOT)})"; rows.append(row); continue
                        pf = pd.read_csv(pfile)[["subject", f"{t['region']}__{f}"]].rename(
                            columns={f"{t['region']}__{f}": "_paired"})
                        dd = dd.merge(pf, on="subject")
                        y = f"delta__{t['region']}__{f}"
                        dd[y] = dd["_paired"] - dd[f"{t['region']}__{f}"]
                    else:
                        y = f"{t['region']}__{f}"
                    if t["kind"] == "matched_severity":
                        cv = cv + ["mmse"]
                    if y not in dd:
                        row["note"] = f"column {y} missing"; rows.append(row); continue
                    ge = group_effect(dd, y, "group", tgt, ref, cv, mc["n_perm"], 500, st["seed"])
                    g, ci90, ci95 = adjusted_g(dd, y, tgt, ref, cv, mc["n_boot"], rng)
                    row.update(n_target=ge["n_target"], n_ref=ge["n_ref"], estimate=ge["beta_adj"], effect=g,
                               effect_ci90=ci90, effect_ci95=ci95, p=ge["p_perm_freedman_lane"],
                               equivalent=bool(np.isfinite(ci90[0]) and -mc["sesoi_d"] < ci90[0] and ci90[1] < mc["sesoi_d"]))
                    if t["kind"] == "attenuation":
                        med = t["mediator"]
                        d2 = dd[dd.group.isin([tgt, ref])].dropna(subset=[y, med] + cv).copy()
                        d2["_grp"] = (d2.group == tgt).astype(float)
                        b0, b1 = _ols_beta(d2, y, cv), _ols_beta(d2, y, cv + [med])
                        boots = []
                        for _ in range(mc["n_boot"]):
                            bs = pd.concat([g_.sample(len(g_), replace=True, random_state=int(rng.integers(2**31)))
                                            for _, g_ in d2.groupby("group")])
                            try:
                                c0, c1 = _ols_beta(bs, y, cv), _ols_beta(bs, y, cv + [med])
                                boots.append(1 - c1 / c0 if c0 != 0 else np.nan)
                            except Exception:
                                pass
                        att = 1 - b1 / b0 if b0 != 0 else np.nan
                        lo, hi = np.nanpercentile(boots, [2.5, 97.5]); lo90, hi90 = np.nanpercentile(boots, [5, 95])
                        row.update(estimate=att, effect=att, effect_ci95=[float(lo), float(hi)],
                                   effect_ci90=[float(lo90), float(hi90)],
                                   p=float((np.sum(np.asarray(boots) <= 0) + 1) / (len(boots) + 1)),
                                   equivalent=bool(hi90 < mc.get("sesoi_attenuation", 0.25)))
                elif t["kind"] == "within_corr":
                    dd = df[df.group == t["group"]]
                    x = f"{t['region']}__{f}"
                    ps = partial_spearman(dd, x, t["with"], covars, mc["n_perm"], mc["n_boot"], st["seed"])
                    row.update(n_target=ps["n"], estimate=ps["rho_partial"], effect=ps["rho_partial"],
                               effect_ci95=ps["ci95"], effect_ci90=ps["ci90"], p=ps["p_perm"],
                               equivalent=bool(-mc["sesoi_r"] < ps["ci90"][0] and ps["ci90"][1] < mc["sesoi_r"]))
                else:
                    row["note"] = f"unknown kind {t['kind']}"
            except Exception as e:                       # recorded, never silently dropped
                row["note"] = f"{type(e).__name__}: {e}"
            rows.append(row)
        out = pd.DataFrame(rows)
        ok = out["p"].notna() if "p" in out else pd.Series(False, index=out.index)
        ph = holm(dict(zip(out.loc[ok, "id"], out.loc[ok, "p"]))) if ok.any() else {}
        out["p_holm"] = out["id"].map(ph)
        return out

    main_df = D[D.has_gamma] if pc["restrict_to_present"] else D
    tests = run_all(main_df, "with_gamma" if pc["restrict_to_present"] else "all")
    tests_all = run_all(D, "all") if pc["restrict_to_present"] else tests
    pd.concat([tests, tests_all] if tests_all is not tests else [tests]).to_csv(odir / "tests.csv", index=False)

    # ---------------------------------------------------------------- 2. sensitivity
    sens = []
    for t in mc["tests"]:
        if t["kind"] != "group":
            continue
        f = t["feature"].replace("{primary}", primary); y = f"{t['region']}__{f}"
        for name, extra in mc["sensitivity_covariates"].items():
            ex = [c for c in extra if c in main_df]
            if len(ex) < len(extra) or y not in main_df:
                sens.append({"id": t["id"], "set": name, "note": "covariate or feature missing"}); continue
            try:
                ge = group_effect(main_df, y, "group", *t["contrast"], covars + ex, 2000, 200, st["seed"])
                sens.append({"id": t["id"], "set": name, "estimate": ge["beta_adj"], "p": ge["p_perm_freedman_lane"]})
            except Exception as e:
                sens.append({"id": t["id"], "set": name, "note": f"{type(e).__name__}: {e}"})
    pd.DataFrame(sens).to_csv(odir / "sensitivity.csv", index=False)

    # ---------------------------------------------------------------- 3. scorecard
    mp = model_predictions(fp_json)
    score = []
    for t in mc["tests"]:
        r = tests[tests.id == t["id"]].iloc[0]
        f = r["feature"]
        for code, pred in t["predict"].items():
            th = names[code]
            model_pred = mp.get(f, {}).get(th, "?") if (t["kind"] == "group" and t["contrast"] == ["AD", "CN"]) else "?"
            est, padj, eq = r.get("estimate", np.nan), r.get("p_holm", np.nan), r.get("equivalent", None)
            score.append({"id": t["id"], "test": t["name"], "theory": code, "name": th,
                          "verbal_prediction": pred, "verbal_outcome": classify(pred, est, padj, eq, alpha),
                          "model_prediction": model_pred, "model_outcome": classify(model_pred, est, padj, eq, alpha)})
    score = pd.DataFrame(score)
    score.to_csv(odir / "scorecard.csv", index=False)
    summary = (score.groupby(["theory", "verbal_outcome"]).size().unstack(fill_value=0)
               .reindex(columns=["consistent", "inconsistent", "inconclusive", "no_prediction", "not_run"], fill_value=0))
    summary_m = (score.groupby(["theory", "model_outcome"]).size().unstack(fill_value=0)
                 .reindex(columns=["consistent", "inconsistent", "inconclusive", "no_prediction"], fill_value=0))

    # ---------------------------------------------------------------- 4. fingerprint comparison
    comp = {"fingerprint_status": fp_status}
    if fp_json:
        fl = fp_json["features"]
        cols = {f: f"roi__{f}" for f in fl if f"roi__{f}" in main_df}
        dd = main_df[main_df.group.isin(["AD", "CN"])].dropna(subset=[c for c in covars if c in main_df]).copy()
        for f, c in cols.items():                       # covariate-adjusted values
            ok = dd[c].notna()
            dd.loc[ok, f"adj__{f}"] = _resid(dd[ok], c, covars)

        def eff(df_):
            out = {}
            for f in cols:
                a_, b_ = df_.loc[df_.group == "AD", f"adj__{f}"].dropna(), df_.loc[df_.group == "CN", f"adj__{f}"].dropna()
                if len(a_) > 2 and len(b_) > 2:
                    out[f] = hedges_g(a_.values, b_.values)
            return pd.Series(out, dtype=float)

        ident = {}
        ip = ROOT / "results" / "mechanism" / "identifiability.json"
        if ip.exists():
            ident = json.loads(ip.read_text())
        E = eff(dd)
        for fam, blob in fp_json["families"].items():
            F = pd.DataFrame(blob["matrix"]).T
            F = F.loc[:, [c for c in F.columns if c in E.index]]
            obs = compare(E, F, fp_json["local"], fp_json["inputs"])
            boots_local, boots_best = [], []
            for _ in range(mc["n_boot"]):
                bs = pd.concat([g_.sample(len(g_), replace=True, random_state=int(rng.integers(2**31)))
                                for _, g_ in dd.groupby("group")])
                rb = compare(eff(bs), F, fp_json["local"], fp_json["inputs"])
                if "local_share" in rb:
                    boots_local.append(rb["local_share"]); boots_best.append(rb["best_single"])
            perm_cos = []
            for _ in range(1000):
                pp = dd.copy(); pp["group"] = rng.permutation(pp["group"].values)
                rp = compare(eff(pp), F, fp_json["local"], fp_json["inputs"])
                if "cosine" in rp:
                    perm_cos.append(max(rp["cosine"].values()))
            max_cos = max(obs["cosine"].values()) if "cosine" in obs else np.nan
            within = ident.get(f"fingerprints_{fam}__data_{fam}", {}).get("local_vs_input_accuracy", np.nan)
            cross = [v.get("local_vs_input_accuracy", np.nan) for k_, v in ident.items()
                     if k_.startswith(f"fingerprints_{fam}__") and not k_.endswith(f"data_{fam}")]
            lo, hi = (np.nanpercentile(boots_local, [2.5, 97.5]) if boots_local else (np.nan, np.nan))
            comp[fam] = {**{k_: v for k_, v in obs.items() if k_ != "features"}, "features": obs.get("features"),
                         "effect_vector": E.to_dict(),
                         "local_share_ci95": [float(lo), float(hi)],
                         "best_single_bootstrap_freq": pd.Series(boots_best).value_counts(normalize=True).to_dict(),
                         "max_cosine_perm_p": float((np.sum(np.asarray(perm_cos) >= max_cos) + 1) / (len(perm_cos) + 1))
                         if perm_cos and np.isfinite(max_cos) else np.nan,
                         "identifiability_within": within,
                         "identifiability_cross": float(np.nanmin(cross)) if cross else np.nan}
        verdicts = []
        for fam in fp_json["families"]:
            c = comp[fam]
            lo, hi = c["local_share_ci95"]
            v = "local_loop" if lo > 0.5 else ("input_driven" if hi < 0.5 else "undetermined")
            ok_id = (c["identifiability_within"] >= 0.8) and (c["identifiability_cross"] >= 0.7)
            verdicts.append((v, ok_id))
        same = len({v for v, _ in verdicts}) == 1
        claim = verdicts[0][0] if (same and all(ok for _, ok in verdicts) and verdicts[0][0] != "undetermined") else "no_claim"
        comp["first_split_claim"] = claim
        comp["first_split_per_family"] = {fam: v for fam, (v, _) in zip(fp_json["families"], verdicts)}
    (odir / "fingerprint_comparison.json").write_text(json.dumps(comp, indent=2, default=float))

    # ---------------------------------------------------------------- report
    lines = [f"# Mechanism report: {a.dataset} / {a.variant}", "",
             f"- Label status: **{status}**; fingerprints: **{fp_status}**; mechanistic status: **{mech_status}**",
             f"- Subjects with a detectable gamma oscillation (presence gate):", "", pres.to_markdown(), "",
             "## Pre-registered tests (subjects with gamma; Holm across tests)", "",
             tests[[c for c in ["id", "name", "n_target", "n_ref", "effect", "effect_ci95", "p", "p_holm", "equivalent", "note"]
                    if c in tests]].to_markdown(index=False), "",
             *(["## Same tests, ALL subjects (descriptive: includes subjects without a detectable oscillation)", "",
                tests_all[[c for c in ["id", "name", "n_target", "n_ref", "effect", "effect_ci95", "p", "p_holm",
                                       "equivalent", "note"] if c in tests_all]].to_markdown(index=False), ""]
               if tests_all is not tests else []),
             "## Scorecard: verbal predictions", "", summary.to_markdown(), "",
             "## Scorecard: model predictions (both simulator families agree)", "", summary_m.to_markdown(), ""]
    if fp_json:
        lines += ["## Fingerprint comparison (AD vs CN, adjusted)", ""]
        for fam in fp_json["families"]:
            c = comp[fam]
            lines.append(f"- **{fam}**: local-loop share {c.get('local_share', np.nan):.2f} "
                         f"(95% CI {c['local_share_ci95'][0]:.2f}-{c['local_share_ci95'][1]:.2f}); best single "
                         f"{c.get('best_single')}; max-cosine permutation p = {c['max_cosine_perm_p']:.3f}; "
                         f"identifiability within {c['identifiability_within']:.2f}, cross {c['identifiability_cross']:.2f}")
        lines += ["", f"**First split claim:** {comp['first_split_claim']}  (requires agreement of both families, "
                  "a CI excluding 0.5 and adequate identifiability)"]
    lines += ["", "Interpretation rule: a test classed 'consistent' supports a theory only together with the "
              "other tests; no single test identifies a mechanism. If mechanistic status is DESCRIPTIVE_ONLY, "
              "report all of this as a limitation."]
    (odir / "report.md").write_text("\n".join(lines))
    (odir / "run_meta.json").write_text(json.dumps({"evidence_status": status, "fingerprints": fp_status,
                                                    "mechanistic_status": mech_status, **analysis_hash()}, indent=2))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
