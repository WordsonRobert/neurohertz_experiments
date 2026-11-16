"""H19: rival R1 at supertype level. SST loss may hide below the subclass.
Discovery: in MTG (83 donors), find Sst supertypes whose share of GABAergic neurons declines with local CPS
(Spearman rho < 0, p < 0.05) = 'MTG-vulnerable Sst set'. Test, out of region and without re-selection, the summed
share of that set in AnG and V1C (43 donors) against local CPS, alongside L2/3 IT. Also per-supertype table.
"""
import numpy as np, pandas as pd
from scipy.stats import spearmanr
D = "/home/claude/data/seaad"; cps = pd.read_csv(f"{D}/CPS.csv", index_col=0)
cols = ["Donor ID", "Class", "Subclass", "Supertype", "Neurotypical reference"]
def shares(reg):
    X = pd.read_csv(f"{D}/{reg}.csv", usecols=cols, low_memory=False)
    X = X[~X["Neurotypical reference"].astype(str).str.lower().eq("true")]
    G = X[X.Class == "Neuronal: GABAergic"]; E = X[X.Class == "Neuronal: Glutamatergic"]
    st = G[G.Subclass == "Sst"].groupby(["Donor ID", "Supertype"]).size().unstack(fill_value=0)
    st = st.div(G.groupby("Donor ID").size(), axis=0)
    l23 = E[E.Subclass == "L2/3 IT"].groupby("Donor ID").size() / E.groupby("Donor ID").size()
    sst = G[G.Subclass == "Sst"].groupby("Donor ID").size() / G.groupby("Donor ID").size()
    n = (G.groupby("Donor ID").size() + E.groupby("Donor ID").size())
    c = cps[cps["Brain Region"] == reg].set_index("Donor ID")["CPS_Local"]
    out = st.join(l23.rename("L23IT")).join(sst.rename("Sst_all")).join(n.rename("n")).join(c.rename("CPS"), how="inner")
    return out[out.n >= 500]
M = shares("MTG")
tab = []
for s in [c for c in M.columns if str(c).startswith("Sst")and c != "Sst_all"]:
    r, p = spearmanr(M[s], M.CPS); tab.append((s, M[s].mean(), r, p))
T = pd.DataFrame(tab, columns=["supertype", "mean_share", "rho_MTG", "p_MTG"]).sort_values("rho_MTG")
vul = T[(T.rho_MTG < 0) & (T.p_MTG < 0.05)].supertype.tolist()
print("MTG-vulnerable Sst supertypes:", vul)
res = []
for reg in ["MTG", "AnG", "V1C"]:
    R = M if reg == "MTG" else shares(reg)
    have = [v for v in vul if v in R.columns]
    R["Sst_vulnerable"] = R[have].sum(1)
    for k in ["Sst_vulnerable", "Sst_all", "L23IT"]:
        r, p = spearmanr(R[k], R.CPS); res.append(dict(region=reg, n=len(R), measure=k, mean=R[k].mean(), rho=r, p=p))
    for s in have:
        T.loc[T.supertype == s, f"rho_{reg}"] = spearmanr(R[s], R.CPS)[0]
Rz = pd.DataFrame(res); pd.set_option("display.width", 200)
print(Rz.round(3).to_string(index=False)); print(); print(T.round(3).to_string(index=False))
Rz.to_csv("/home/claude/work/h19/sst_vulnerable_by_region.csv", index=False); T.to_csv("/home/claude/work/h19/sst_supertypes.csv", index=False)
