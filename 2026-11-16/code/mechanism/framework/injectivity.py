"""Multimodal injectivity map B -> P(Phi).
Each candidate mechanism b gets a signature: for every characterization phi_j in a modality, the sign of the
predicted change (+1 up, -1 down, 0 = |change| < 2 SE of the observed contrast) at the k that best fits the resting
EEG. A map is injective on a feature set S if every mechanism has a distinct signature restricted to S.
Modalities
  REST   (6)  model-predicted resting EEG features (Phase B circuit, ensemble of good calibrations)
  PHOTIC (2)  model-predicted driven response at 15 and 20 Hz (|H|^2 change), SE from ds006036
  TISSUE (3)  cell-composition signature in posterior cortex. NOT model output: a stated mapping assumption
              (loss-of-cells mechanisms change the share of that cell class; functional mechanisms change none)
Observed signature: ds004504 (rest), ds006036 (photic), SEA-AD AnG (tissue).
Outputs: signature table, distinct-signature counts per modality combination, mechanisms consistent with observed.
"""
import itertools, json, sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/claude/work/phaseB"); sys.path.insert(0, "/home/claude/work")
import model as M
from bridge import features, FEATS

OUT = "/home/claude/work/framework/out"; import os; os.makedirs(OUT, exist_ok=True)
Jz = np.load("/home/claude/work/phaseB/out/jacobian.npz", allow_pickle=True); delta, se = Jz["delta"], Jz["se"]
cals = json.load(open("/home/claude/work/phaseB/out/good_calibrations.json"))
ph = pd.read_csv("/home/claude/work/phaseC/out/photic_group_delta.csv")
ph_obs = {15: ph[(ph.fd == 15) & (ph.n == 1)].iloc[0], 20: ph[(ph.fd == 20) & (ph.n == 1)].iloc[0]}
fq = np.arange(2, 50.01, 0.5)

# candidate set B: signed knobs (so 'less gain' is its own mechanism, distinct from 'more gain')
B = {"gain_up (M1+)": ("M1_drive_gain_up", +1), "gain_down / excitatory loss (M1-)": ("M1_drive_gain_up", -1),
     "PV->E inhibition down (M2)": ("M2_PV_to_E_down", +1), "recurrent E up (M3)": ("M3_recurrent_E_up", +1),
     "slow/SST loop down (M4)": ("M4_slow_inhib_down", +1), "input E/I up (M5+)": ("M5_input_EI_up", +1),
     "input E/I down (M5-)": ("M5_input_EI_up", -1), "L2/3 loss, all outputs (tissue-scaled)": ("L23", +1)}
# tissue mapping assumption: (L2/3 IT share, SST share, PV share) change
TISSUE_MAP = {"gain_up (M1+)": (0, 0, 0), "gain_down / excitatory loss (M1-)": (-1, 0, 0), "PV->E inhibition down (M2)": (0, 0, 0),
              "recurrent E up (M3)": (0, 0, 0), "slow/SST loop down (M4)": (0, -1, 0), "input E/I up (M5+)": (0, 0, 0),
              "input E/I down (M5-)": (0, 0, 0), "L2/3 loss, all outputs (tissue-scaled)": (-1, 0, 0)}
TISSUE_OBS = (-1, 0, 0)       # SEA-AD AnG: L2/3 IT rho -0.46 p .002; SST -0.11 n.s.; PV +0.08 n.s.
OFF = np.array([1, 1, 1, 1, 0, 0], float)


def H2(p, f):
    A, Bm, C = M.system(p)
    return np.array([np.abs(C @ np.linalg.solve(2j * np.pi * fi * np.eye(6) - A, Bm[:, 0])) ** 2 for fi in f])


def state(base, key, sgn, k):
    if key == "L23":
        q = dict(base)
        for w in ("wEE", "wFE", "wSE"): q[w] = base[w] * (1 - 0.12 * k)
        return q
    return M.apply(base, key, sgn * k)


def best_k(base, key, sgn):
    best = (np.inf, None)
    for k in np.linspace(0.05, 1.5, 30):
        q = state(base, key, sgn, k)
        if not M.stable(q): continue
        d = features(fq, np.log10(M.psd(q, fq))) - features(fq, np.log10(M.psd(base, fq)))
        w = 1 / se ** 2; off = np.sum(w * OFF * (delta - d)) / np.sum(w * OFF); r = delta - d - off * OFF
        c = np.sum((r / se) ** 2)
        if c < best[0]: best = (c, k, d)
    return best


def tern(x, s):
    return 0 if abs(x) < 2 * s else int(np.sign(x))


def rel(d):          # remove the free global offset: bands relative to their mean, slope and bump as is
    x = np.array(d, float).copy(); x[:4] = x[:4] - x[:4].mean(); return x


SEr = se.copy()
obs_rel = rel(delta); obs_norm = np.linalg.norm(obs_rel / SEr)
rows = []; dirs = {}
for name, (key, sgn) in B.items():
    sigs, vecs = [], []
    for base in cals:
        h = 0.1
        q = state(base, key, sgn, h)
        if not M.stable(q): continue
        d = rel(features(fq, np.log10(M.psd(q, fq))) - features(fq, np.log10(M.psd(base, fq))))
        if np.linalg.norm(d / SEr) < 1e-9: continue
        scale = obs_norm / np.linalg.norm(d / SEr)           # same whitened effect size as the observed contrast
        d = d * scale
        dph = 10 * np.log10(H2(q, [15, 20]) / H2(base, [15, 20])) * scale
        rest_sig = tuple(tern(d[j], SEr[j]) for j in range(6))
        ph_sig = (tern(dph[1] - dph[0], np.hypot(ph_obs[15].se, ph_obs[20].se)),)
        sigs.append((rest_sig, ph_sig)); vecs.append(d / SEr)
    rest_mode = max(set(s_[0] for s_ in sigs), key=[s_[0] for s_ in sigs].count)
    ph_mode = max(set(s_[1] for s_ in sigs), key=[s_[1] for s_ in sigs].count)
    dirs[name] = np.mean(vecs, 0)
    cosobs = float(np.mean([v @ (obs_rel / SEr) / (np.linalg.norm(v) * obs_norm) for v in vecs]))
    rows.append(dict(mechanism=name, rest_signature=rest_mode, rest_agree=round(np.mean([s_[0] == rest_mode for s_ in sigs]), 2),
                     photic_signature=ph_mode, tissue_signature=TISSUE_MAP[name], cos_to_observed=round(cosobs, 2)))
S = pd.DataFrame(rows)
obs_rest = tuple(tern(obs_rel[j], SEr[j]) for j in range(6))
obs_ph = (tern(ph_obs[20].delta_db - ph_obs[15].delta_db, np.hypot(ph_obs[15].se, ph_obs[20].se)),)
print("Characterizations: REST = [b16_23, b24_30, b32_40, b42_47 (each relative to the mean band change), slope, bump]; "
      "PHOTIC = [20 Hz minus 15 Hz driven change]; TISSUE = [L2/3 IT share, SST share, PV share]\n")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
print(S.to_string(index=False))
print(f"\nOBSERVED: rest {obs_rest}  photic {obs_ph}  tissue {TISSUE_OBS}")
combos = {"REST": ["rest_signature"], "PHOTIC": ["photic_signature"], "TISSUE": ["tissue_signature"],
          "REST+PHOTIC": ["rest_signature", "photic_signature"], "REST+TISSUE": ["rest_signature", "tissue_signature"],
          "REST+PHOTIC+TISSUE": ["rest_signature", "photic_signature", "tissue_signature"]}
obs = {"rest_signature": obs_rest, "photic_signature": obs_ph, "tissue_signature": TISSUE_OBS}
res = []
for nm, cs in combos.items():
    keys = [tuple(r[c] for c in cs) for _, r in S.iterrows()]
    consistent = [S.mechanism[i] for i, kk in enumerate(keys) if kk == tuple(obs[c] for c in cs)]
    res.append(dict(features=nm, n_mechanisms=len(S), distinct_signatures=len(set(keys)), injective=len(set(keys)) == len(S),
                    consistent_with_observed=consistent))
R = pd.DataFrame(res); print("\n" + R.to_string(index=False))
S.to_csv(f"{OUT}/signatures.csv", index=False); R.to_csv(f"{OUT}/injectivity.csv", index=False)
json.dump(dict(observed=dict(rest=obs_rest, photic=obs_ph, tissue=TISSUE_OBS)), open(f"{OUT}/observed_signature.json", "w"))

names = list(dirs); Dm = np.array([dirs[n] / np.linalg.norm(dirs[n]) for n in names])
print("\nCosine between mechanism directions in whitened REST space (1 = indistinguishable, -1 = opposite):")
print(pd.DataFrame(Dm @ Dm.T, index=[n[:22] for n in names], columns=[n[:10] for n in names]).round(2).to_string())
sv = np.linalg.svd(Dm, compute_uv=False); print("singular values of stacked REST directions:", np.round(sv, 3))
