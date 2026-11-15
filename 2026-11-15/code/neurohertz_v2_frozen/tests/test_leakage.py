"""Leakage guards. Run: python -m pytest -q tests/"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
STAGE_A = ["nh/preprocess.py", "nh/spectral.py", "nh/gamma.py", "nh/surrogates.py",
           "nh/simulate.py", "scripts/01_extract_features.py", "scripts/02_simulation_validation.py",
           "scripts/02b_calibrate_simulation.py", "nh/dynamics.py", "nh/oscfit.py", "nh/mechsim.py",
           "nh/cyclemodel.py", "nh/fingerprint.py", "scripts/13_mechanism_fingerprints.py",
           "scripts/10_run_ablations.py", "scripts/11_select_methods.py"]


def _imports_and_names(path: Path):
    tree = ast.parse(path.read_text())
    mods, names, attrs, strings = set(), set(), set(), set()
    docs = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and ast.get_docstring(n, clean=False):
            docs.add(ast.get_docstring(n, clean=False).lower())
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            mods |= {a.name for a in n.names}
        elif isinstance(n, ast.ImportFrom):
            mods.add(n.module or "")
            names |= {a.name for a in n.names}
        elif isinstance(n, ast.Attribute):
            attrs.add(n.attr)
        elif isinstance(n, ast.Name):
            names.add(n.id)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value.lower() not in docs:
            strings.add(n.value.lower())
    return mods, names, attrs, strings


@pytest.mark.parametrize("rel", STAGE_A)
def test_stage_a_never_touches_labels(rel):
    mods, names, attrs, strings = _imports_and_names(ROOT / rel)
    assert not any(m.endswith("labels") for m in mods), f"{rel} imports the label module"
    assert "read_participants" not in attrs | names, f"{rel} reads participants"
    assert "open_labels" not in names, f"{rel} opens labels"
    assert not any("participants" in s for s in strings), f"{rel} references a participants file"


def test_subject_features_independent_of_batch_and_order():
    from nh.config import load_config
    from nh.gamma import gii_subject, subject_rng
    from nh.simulate import simulate
    cf = load_config()["features"]
    x1, sf = simulate(seed=1, dur_s=40); x2, _ = simulate(seed=2, dur_s=40)
    seg = [(0, len(x1))]
    a = gii_subject(x1[None], seg, sf, ["c"], cf["gamma_band"], cf, subject_rng(5, "sub-A"), n_surr=3)
    _ = gii_subject(x2[None], seg, sf, ["c"], cf["gamma_band"], cf, subject_rng(5, "sub-B"), n_surr=3)
    b = gii_subject(x1[None], seg, sf, ["c"], cf["gamma_band"], cf, subject_rng(5, "sub-A"), n_surr=3)
    for k in a["c"]:
        va, vb = a["c"][k], b["c"][k]
        assert (np.isnan(va) and np.isnan(vb)) or va == vb, k


def test_nested_cv_is_not_fooled_by_noise_but_leaky_selection_is():
    from sklearn.feature_selection import SelectKBest, f_classif
    from nh.predict import nested_cv_auc
    rng = np.random.default_rng(0)
    n, p = 60, 2000
    X = rng.standard_normal((n, p)); y = np.r_[np.zeros(30), np.ones(30)].astype(int)
    pc = {"seed": 0, "outer": {"n_splits": 5, "n_repeats": 3}, "inner": {"n_splits": 3},
          "C_grid": [0.01, 1.0]}
    # LEAKY: choose features on ALL subjects, then cross-validate -> optimistic
    Xl = SelectKBest(f_classif, k=5).fit_transform(X, y)
    leaky = nested_cv_auc(Xl, y, pc)["auc_mean_over_repeats"]
    # CORRECT: a single fixed (pre-specified) column, no selection -> chance
    honest = nested_cv_auc(X[:, :1], y, pc)["auc_mean_over_repeats"]
    assert leaky > 0.75, leaky
    assert 0.25 < honest < 0.75, honest


def test_lockbox_refuses_when_not_frozen(tmp_path, monkeypatch):
    import nh.config as C
    import nh.ledger as L
    from nh.labels import LabelAccessError, open_labels
    monkeypatch.setattr(C, "FREEZE_PATH", tmp_path / "freeze.json")
    monkeypatch.setattr(L, "LEDGER_PATH", tmp_path / "ledger.jsonl")

    class FakeAdapter:
        name, role = "fake_lockbox", "lockbox"
        def read_participants(self):  # pragma: no cover - must never be reached
            raise AssertionError("labels were read")
    f = tmp_path / "features_subject.csv"; f.write_text("subject,x\ns1,1\n")
    with pytest.raises(LabelAccessError):
        open_labels(FakeAdapter(), features_path=f, purpose="test")


def test_discovery_blinded_during_development(tmp_path, monkeypatch):
    import nh.config as C
    import nh.ledger as L
    from nh.labels import LabelAccessError, open_labels
    monkeypatch.setattr(C, "FREEZE_PATH", tmp_path / "freeze.json")
    monkeypatch.setattr(L, "LEDGER_PATH", tmp_path / "ledger.jsonl")
    import pandas as pd

    class FakeAdapter:
        name, role = "fake_disc", "discovery"
        def read_participants(self):
            return pd.DataFrame({"subject": ["s1"], "group": ["AD"]})
    with pytest.raises(LabelAccessError):
        open_labels(FakeAdapter(), purpose="test")
    df = open_labels(FakeAdapter(), purpose="test", dev_unblind_reason="unit test")
    assert df.attrs["evidence_status"] == "EXPLORATORY"
    events = [json.loads(l)["event"] for l in (tmp_path / "ledger.jsonl").read_text().splitlines()]
    assert "DISCOVERY_DEV_UNBLINDED" in events


def test_in_fold_electrode_selection_does_not_inflate_auc():
    """Picking the 'best' 3-4 electrodes is honest only inside each training fold."""
    from sklearn.feature_selection import SelectKBest, f_classif
    from nh.predict import nested_cv_auc
    rng = np.random.default_rng(1)
    n, p = 60, 19 * 10                                   # 19 electrodes x 10 noise features
    X = rng.standard_normal((n, p)); y = np.r_[np.zeros(30), np.ones(30)].astype(int)
    pc = {"seed": 1, "outer": {"n_splits": 5, "n_repeats": 3}, "inner": {"n_splits": 3}, "C_grid": [0.1, 1.0]}
    honest = nested_cv_auc(X, y, pc, model_kw={"select_k": [3, 4]})["auc_mean_over_repeats"]
    leaky = nested_cv_auc(SelectKBest(f_classif, k=4).fit_transform(X, y), y, pc)["auc_mean_over_repeats"]
    assert 0.25 < honest < 0.75, honest
    assert leaky > honest + 0.15, (leaky, honest)


def test_featureset_builder_channel_columns():
    import pandas as pd
    from nh.config import load_config
    from nh.featuresets import build
    cfg = load_config()
    long = pd.DataFrame([(s, c, "burst_freq_sd", float(i)) for s in ["a", "b"] for i, c in enumerate(cfg["common"]["channels"])],
                        columns=["subject", "channel", "feature", "value"])
    subj = pd.DataFrame({"subject": ["a", "b"], "roi__burst_freq_sd": [1.0, 2.0]})
    df, cols = build(subj, long, ["allch:burst_freq_sd", "roi:burst_freq_sd"], cfg)
    assert len(cols) == 20 and cols[-1] == "roi__burst_freq_sd"
    assert df.loc[0, "ch__P3__burst_freq_sd"] == cfg["common"]["channels"].index("P3")
