"""Leakage-safe prediction (secondary evidence only).

Everything that is FITTED across subjects -- scaling, any feature selection, the classifier and
its hyper-parameter C -- lives inside an sklearn Pipeline that is refit on the training part of
every outer fold. The test fold is touched exactly once, by predict_proba.

Per-subject feature extraction happens earlier and is label-blind and subject-independent, so it
cannot leak (each subject's features depend only on that subject's recording and the frozen config).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.feature_selection import SelectKBest, f_classif, f_regression
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import r2_score, roc_auc_score
from sklearn.model_selection import (GridSearchCV, KFold, RepeatedKFold,
                                     RepeatedStratifiedKFold, StratifiedKFold)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .stats import delong_auc


def _candidate_grid(name, C_grid, seed, l1_ratios):
    """Interpretable classifier families only (each gives per-feature weights or per-feature curves)."""
    if name == "lr_l2":
        return {"clf": [LogisticRegression(class_weight="balanced", max_iter=10000)], "clf__C": list(C_grid)}
    if name == "lr_en":
        return {"clf": [LogisticRegression(penalty="elasticnet", solver="saga", class_weight="balanced",
                                           max_iter=20000)], "clf__C": list(C_grid), "clf__l1_ratio": list(l1_ratios)}
    if name == "linear_svm":
        from sklearn.svm import LinearSVC
        return {"clf": [LinearSVC(class_weight="balanced", max_iter=50000)], "clf__C": list(C_grid)}
    if name == "ebm":
        from interpret.glassbox import ExplainableBoostingClassifier
        return {"clf": [ExplainableBoostingClassifier(interactions=0, outer_bags=8, random_state=seed, n_jobs=1)]}   # n_jobs=1: no nested parallelism inside permutation workers
    raise ValueError(name)


def classifier(C_grid, inner_splits: int, seed: int, select_k=None, penalty: str = "l2",
               l1_ratios=(0.2, 0.5, 0.8), candidates=None) -> GridSearchCV:
    """Impute -> scale -> [select k best features] -> classifier; all refit per fold.
    select_k  : None or a list of k values tuned by the inner CV.
    candidates: None (single classifier given by `penalty`) or a list of interpretable families
                (lr_l2, lr_en, linear_svm, ebm) chosen by the inner CV = nested model selection."""
    steps = [("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
    extra = {}
    if select_k:
        steps.append(("select", SelectKBest(f_classif)))
        extra["select__k"] = list(select_k)
    steps.append(("clf", LogisticRegression(class_weight="balanced", max_iter=10000)))
    if candidates:
        grid = [{**_candidate_grid(c, C_grid, seed, l1_ratios), **extra} for c in candidates]
    else:
        grid = {**_candidate_grid("lr_en" if penalty == "elasticnet" else "lr_l2", C_grid, seed, l1_ratios), **extra}
    return GridSearchCV(Pipeline(steps), grid, scoring="roc_auc",
                        cv=StratifiedKFold(inner_splits, shuffle=True, random_state=seed), refit=True)


def score_positive(model, X) -> np.ndarray:
    """Probability of class 1 if available, else the decision function (AUC only needs ranking)."""
    est = model.best_estimator_ if hasattr(model, "best_estimator_") else model
    if hasattr(est, "predict_proba"):
        try:
            return est.predict_proba(X)[:, list(est.classes_).index(1)]
        except AttributeError:
            pass
    return est.decision_function(X)


def regressor(alpha_grid, inner_splits: int, seed: int, select_k=None) -> GridSearchCV:
    steps = [("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
    grid = {"reg__alpha": list(alpha_grid)}
    if select_k:
        steps.append(("select", SelectKBest(f_regression)))
        grid["select__k"] = list(select_k)
    steps.append(("reg", Ridge()))
    return GridSearchCV(Pipeline(steps), grid, scoring="r2",
                        cv=KFold(inner_splits, shuffle=True, random_state=seed), refit=True)


def _model_kw(pcfg, model_kw):
    model_kw = model_kw or {}
    cands = model_kw.get("classifier")
    return dict(select_k=model_kw.get("select_k"), penalty=model_kw.get("penalty", pcfg.get("penalty", "l2")),
                candidates=pcfg.get("classifier_candidates") if cands == "auto" else None)


def nested_cv_auc(X: np.ndarray, y: np.ndarray, pcfg: dict, n_repeats: int | None = None,
                  seed: int | None = None, model_kw: dict | None = None, feature_names=None) -> dict:
    seed = pcfg["seed"] if seed is None else seed
    n_rep = pcfg["outer"]["n_repeats"] if n_repeats is None else n_repeats
    k = pcfg["outer"]["n_splits"]
    outer = RepeatedStratifiedKFold(n_splits=k, n_repeats=n_rep, random_state=seed)
    model = classifier(pcfg["C_grid"], pcfg["inner"]["n_splits"], seed, **_model_kw(pcfg, model_kw))
    oof = np.full((n_rep, len(y)), np.nan)
    picked = np.zeros(X.shape[1]); n_fit = 0; chosen = {}
    for i, (tr, te) in enumerate(outer.split(X, y)):
        r = i // k
        assert not set(tr) & set(te)
        m = clone(model).fit(X[tr], y[tr])
        oof[r, te] = score_positive(m, X[te])
        sel = m.best_estimator_.named_steps.get("select")
        chosen[type(m.best_estimator_.named_steps["clf"]).__name__] = chosen.get(type(m.best_estimator_.named_steps["clf"]).__name__, 0) + 1
        picked += sel.get_support() if sel is not None else 1
        n_fit += 1
    per_rep = np.array([roc_auc_score(y, oof[r]) for r in range(n_rep)])
    mean_score = oof.mean(0)
    names = list(feature_names) if feature_names is not None else [f"x{j}" for j in range(X.shape[1])]
    return {"classifier_chosen_per_fold": chosen, "selection_frequency": dict(sorted(zip(names, (picked / n_fit).round(3).tolist()),
                                               key=lambda kv: -kv[1])),"auc_mean_over_repeats": float(per_rep.mean()),
            "auc_repeat_range_2.5_97.5": [float(np.percentile(per_rep, 2.5)), float(np.percentile(per_rep, 97.5))],
            "auc_of_mean_oof_score_delong": delong_auc(y, mean_score),
            "per_repeat_auc": per_rep.tolist(), "oof_mean_score": mean_score.tolist()}


def permutation_test_pipeline(X, y, pcfg: dict, n_perm: int, n_repeats: int = 5, seed: int | None = None,
                              model_kw: dict | None = None) -> dict:
    """Full-pipeline permutation: labels shuffled, ENTIRE nested CV re-run each time.
    Observed and null use the same (reduced) number of outer repeats so they are comparable."""
    seed = pcfg["seed"] if seed is None else seed
    obs = nested_cv_auc(X, y, pcfg, n_repeats=n_repeats, seed=seed, model_kw=model_kw)["auc_mean_over_repeats"]
    rng = np.random.default_rng(seed)
    perms = [rng.permutation(y) for _ in range(n_perm)]          # drawn in the same order as before: same null
    from joblib import Parallel, delayed
    null = np.array(Parallel(n_jobs=int(pcfg.get("n_jobs", 1)))(
        delayed(lambda yp, b: nested_cv_auc(X, yp, pcfg, n_repeats=n_repeats, seed=seed + 1 + b,
                                            model_kw=model_kw)["auc_mean_over_repeats"])(yp, b)
        for b, yp in enumerate(perms)))
    return {"auc_obs": float(obs), "null_mean": float(null.mean()), "null_sd": float(null.std()),
            "p_perm": float((np.sum(null >= obs) + 1) / (n_perm + 1)), "n_perm": n_perm,
            "n_repeats_each": n_repeats}


def incremental_auc(df: pd.DataFrame, y: np.ndarray, base_cols: list[str], add_cols: list[str],
                    pcfg: dict) -> dict:
    """Same outer splits for base and base+add; reports the distribution of the AUC gain."""
    Xb, Xf = df[base_cols].values.astype(float), df[base_cols + add_cols].values.astype(float)
    rb = nested_cv_auc(Xb, y, pcfg)
    rf = nested_cv_auc(Xf, y, pcfg)
    gain = np.array(rf["per_repeat_auc"]) - np.array(rb["per_repeat_auc"])
    return {"base_cols": base_cols, "add_cols": add_cols,
            "auc_base": rb["auc_mean_over_repeats"], "auc_full": rf["auc_mean_over_repeats"],
            "delta_auc_mean": float(gain.mean()),
            "delta_auc_2.5_97.5": [float(np.percentile(gain, 2.5)), float(np.percentile(gain, 97.5))],
            "frac_repeats_gain_gt_0": float(np.mean(gain > 0))}


def nested_cv_r2(X, y, pcfg: dict, alpha_grid=(0.01, 0.1, 1, 10, 100), select_k=None) -> dict:
    seed, k, n_rep = pcfg["seed"], pcfg["outer"]["n_splits"], pcfg["outer"]["n_repeats"]
    outer = RepeatedKFold(n_splits=k, n_repeats=n_rep, random_state=seed)
    model = regressor(alpha_grid, pcfg["inner"]["n_splits"], seed, select_k=select_k)
    preds = np.full((n_rep, len(y)), np.nan)
    for i, (tr, te) in enumerate(outer.split(X)):
        m = clone(model).fit(X[tr], y[tr])
        preds[i // k, te] = m.predict(X[te])
    r2 = np.array([r2_score(y, preds[r]) for r in range(n_rep)])
    mae = np.array([np.mean(np.abs(y - preds[r])) for r in range(n_rep)])
    return {"r2_mean": float(r2.mean()), "r2_2.5_97.5": [float(np.percentile(r2, 2.5)), float(np.percentile(r2, 97.5))],
            "mae_mean": float(mae.mean()), "per_repeat_r2": r2.tolist()}


def fit_frozen_model(X: np.ndarray, y: np.ndarray, pcfg: dict, model_kw: dict | None = None):
    """Final discovery model (all discovery subjects). Hyper-parameters chosen by inner CV only."""
    return clone(classifier(pcfg["C_grid"], pcfg["inner"]["n_splits"], pcfg["seed"],
                            **_model_kw(pcfg, model_kw))).fit(X, y)


def standardized_coefficients(fitted: GridSearchCV, feature_names) -> dict:
    """Coefficients of the final model on the z-scored scale (comparable across electrodes)."""
    est = fitted.best_estimator_
    names = np.asarray(list(feature_names))
    sel = est.named_steps.get("select")
    if sel is not None:
        names = names[sel.get_support()]
    clf = est.named_steps["clf"]
    params = {k: (v if not isinstance(v, np.generic) else v.item()) for k, v in fitted.best_params_.items()}
    params["clf"] = type(clf).__name__
    if hasattr(clf, "coef_"):
        return {"best_params": params, "coefficients_per_SD": dict(zip(names.tolist(), clf.coef_.ravel().round(4).tolist()))}
    # EBM: per-feature shape functions; report each term's mean absolute contribution
    return {"best_params": params,
            "term_importance": dict(zip(names.tolist(), np.round(clf.term_importances(), 4).tolist()))}
