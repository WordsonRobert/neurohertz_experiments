"""Region comparison on the same 43 donors + amyloid vs tau partial rank correlations for L2/3 IT and Sst shares."""
import numpy as np, pandas as pd
from scipy.stats import spearmanr, rankdata
cps = pd.read_csv('/home/claude/data/seaad/CPS.csv', index_col=0)
same = pd.read_csv('seaad_AnG_donor_fractions.csv', index_col=0).index


def pcor(x, y, z):
    rx, ry, rz = [rankdata(v) for v in (x, y, z)]
    ex = rx - np.polyval(np.polyfit(rz, rx, 1), rz); ey = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
    return np.corrcoef(ex, ey)[0, 1]


rows = []
for reg in ['V1C', 'AnG', 'DFC', 'STG', 'MTG', 'ITG']:
    F = pd.read_csv(f'seaad_{reg}_donor_fractions.csv', index_col=0)
    c = cps[cps['Brain Region'] == reg].set_index('Donor ID')[['CPS_Local_ABeta', 'CPS_Local_pTau']]
    F = F.join(c, how='inner'); F = F[F.index.isin(same)].dropna(subset=['CPS', 'CPS_Local_ABeta', 'CPS_Local_pTau'])
    for ct in ['L2/3 IT', 'Sst', 'Pvalb']:
        r, p = spearmanr(F[ct], F.CPS)
        rows.append(dict(region=reg, cell_type=ct, n=len(F), rho_CPS=r, p_CPS=p,
                         partial_rho_Abeta_given_pTau=pcor(F[ct], F.CPS_Local_ABeta, F.CPS_Local_pTau),
                         partial_rho_pTau_given_Abeta=pcor(F[ct], F.CPS_Local_pTau, F.CPS_Local_ABeta),
                         rho_Abeta_pTau=spearmanr(F.CPS_Local_ABeta, F.CPS_Local_pTau)[0]))
R = pd.DataFrame(rows); R.to_csv('logs/H15_regions_tau.csv', index=False)
print(R.round(3).to_string(index=False))
