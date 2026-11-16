"""Local (Fisher-information) identifiability of the six P04 mechanisms.

Reuses P04's simulated subjects (sim_features.csv); runs no new simulation.

For each simulator family:
  J[f, j]  = d E[z_f] / d k_j   (slope of standardised feature f on severity k of theory j)
  Sigma    = pooled within-cell covariance of the standardised features (Ledoit-Wolf)
  F(n)     = J' Sigma^-1 J / (1/n_AD + 1/n_CN)  (Fisher information of a two-group mean contrast)

Reports: singular values / condition number of the whitened Jacobian, the joint
Cramer-Rao bound on each k_j at n = 36 vs 29, variance inflation from confusability,
the number of resolvable directions, the n per group needed to resolve k = 0.25,
the same quantities for the 2-parameter first split (local loop vs input), the
cross-family principal angles, and a low-SNR proxy (the sims with the lowest gamma SNR).
"""
import json
import sys
import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf

SIM = sys.argv[1]
OUT = sys.argv[2]
FEATS = ['osc_f0', 'osc_width_hz', 'osc_contrast_db', 'fast_sd_z', 'slow_sd_z', 'slow_frac',
         'slow_tau_s', 'if_env_coupling', 'slip_rate_z', 'slip_rate_highamp_z', 'tail_frac_z',
         'jitter_amp_slope']          # burst_freq_sd dropped: 29% missing in the sims
THEORIES = {'synapses_onto_pv': 'T1', 'nav11_pv_output': 'T2', 'erratic_drive': 'T3',
            'acetylcholine': 'T4', 'sst_loss': 'T5', 'tau_silencing': 'T6'}
LOCAL, INPUT = ['T1', 'T2', 'T5'], ['T3', 'T4', 'T6']
N_AD, N_CN = 36, 29
K_RES = 0.25                         # severity step we want to resolve
SE_TARGET = K_RES / 2                # 2 SE < 0.25


def jac_sigma(d):
    base = d[d.theory == 'baseline']
    mu, sd = base[FEATS].mean(), base[FEATS].std()
    z = d.copy()
    z[FEATS] = (d[FEATS] - mu) / sd
    z = z.dropna(subset=FEATS)
    J = np.zeros((len(FEATS), len(THEORIES)))
    for j, th in enumerate(THEORIES):
        s = z[z.theory.isin(['baseline', th])]
        X = np.c_[np.ones(len(s)), s.k.values]
        J[:, j] = np.linalg.lstsq(X, s[FEATS].values, rcond=None)[0][1]
    resid = z[FEATS] - z.groupby(['theory', 'k'])[FEATS].transform('mean')
    S = LedoitWolf().fit(resid.values).covariance_
    return J, S


def analyse(J, S, n_ad=N_AD, n_cn=N_CN):
    Si = np.linalg.inv(S)
    F1 = J.T @ Si @ J                        # information per unit of (1/n_AD + 1/n_CN)^-1
    F = F1 / (1 / n_ad + 1 / n_cn)
    L = np.linalg.cholesky(Si)
    sv = np.linalg.svd(L.T @ J, compute_uv=False)
    ev = np.linalg.eigvalsh(F)[::-1]
    Finv = np.linalg.pinv(F)
    joint = np.sqrt(np.diag(Finv))
    marg = 1 / np.sqrt(np.diag(F))
    n_req = 2 * np.diag(np.linalg.pinv(F1)) / SE_TARGET ** 2   # balanced groups: 1/n+1/n = 2/n
    # first split: 2 parameters, each moving its three theories together
    codes = list(THEORIES.values())
    A = np.zeros((len(codes), 2))
    A[[codes.index(c) for c in LOCAL], 0] = 1 / 3
    A[[codes.index(c) for c in INPUT], 1] = 1 / 3
    F2 = A.T @ F @ A
    F2inv = np.linalg.inv(F2)
    c = np.array([1, -1])                    # local minus input
    return {
        'singular_values_whitened_J': sv.round(3).tolist(),
        'condition_number': float(sv[0] / sv[-1]),
        'fisher_eigenvalues_n36_29': ev.round(2).tolist(),
        'n_directions_resolvable_at_k0.25': int((ev > 1 / SE_TARGET ** 2).sum()),
        'crlb_se_joint': dict(zip(codes, joint.round(3).tolist())),
        'crlb_se_if_only_this_theory': dict(zip(codes, marg.round(3).tolist())),
        'variance_inflation_from_confusion': dict(zip(codes, (joint / marg).round(2).tolist())),
        'n_per_group_to_resolve_k0.25': dict(zip(codes, np.ceil(n_req).astype(int).tolist())),
        'first_split': {
            'crlb_se_local': float(np.sqrt(F2inv[0, 0])),
            'crlb_se_input': float(np.sqrt(F2inv[1, 1])),
            'crlb_se_local_minus_input': float(np.sqrt(c @ F2inv @ c)),
            'corr_local_input_estimates': float(F2inv[0, 1] / np.sqrt(F2inv[0, 0] * F2inv[1, 1])),
        },
    }


def principal_angles(A, B):
    qa, _ = np.linalg.qr(A)
    qb, _ = np.linalg.qr(B)
    s = np.clip(np.linalg.svd(qa.T @ qb, compute_uv=False), -1, 1)
    return np.degrees(np.arccos(s))


d = pd.read_csv(SIM)
res, Js = {}, {}
for fam in ['rate', 'cycle']:
    df = d[d.family == fam]
    J, S = jac_sigma(df)
    Js[fam] = J
    r = analyse(J, S)
    # low-SNR proxy: the third of simulated subjects with the lowest gamma SNR
    lo = df[df.gamma_snr <= df.gamma_snr.quantile(1 / 3)]
    Jl, Sl = jac_sigma(lo)
    r['low_snr_third'] = {k: v for k, v in analyse(Jl, Sl).items()
                          if k in ('condition_number', 'n_directions_resolvable_at_k0.25',
                                   'crlb_se_joint', 'first_split')}
    r['low_snr_third']['gamma_snr_max'] = float(lo.gamma_snr.max())
    r['low_snr_third']['osc_present_frac'] = float(lo.osc_present.mean())
    res[fam] = r
    pd.DataFrame(J, index=FEATS, columns=list(THEORIES.values())).round(3).to_csv(f'{OUT}/jacobian_{fam}.csv')

codes = list(THEORIES.values())
cos = [float(Js['rate'][:, j] @ Js['cycle'][:, j] /
             (np.linalg.norm(Js['rate'][:, j]) * np.linalg.norm(Js['cycle'][:, j]))) for j in range(6)]
res['cross_family'] = {
    'column_cosine_rate_vs_cycle': dict(zip(codes, np.round(cos, 2).tolist())),
    'principal_angles_deg': principal_angles(Js['rate'], Js['cycle']).round(1).tolist(),
}
with open(f'{OUT}/fisher_identifiability.json', 'w') as fh:
    json.dump(res, fh, indent=2)
print(json.dumps(res, indent=2))
