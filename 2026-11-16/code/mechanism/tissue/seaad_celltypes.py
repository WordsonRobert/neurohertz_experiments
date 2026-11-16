"""Biological test of the Phase B result in human tissue (SEA-AD, posterior cortex).
Phase B: resting phenotype = weaker slow (dendritic, SST-like) inhibitory loop OR lower excitatory drive; PV-type
perisomatic loop not required. Prediction if the slow-inhibition account holds: Sst neurons decline with AD
progression in posterior cortex (AnG under P3/P4; V1C under O1/O2), while Pvalb neurons are relatively preserved.
Prediction if lower-excitatory-drive (excitatory loss) holds: excitatory neurons decline relative to inhibitory.
Per donor: fractions of each GABAergic subclass within GABAergic neurons; GABA / (GABA + Glut) neuron ratio;
fraction of each excitatory subclass within excitatory neurons. Relation to pseudo-progression (CPS) and ADNC.
"""
import sys, numpy as np, pandas as pd
from scipy.stats import spearmanr, mannwhitneyu
pd.set_option("display.width", 220)
D = "/home/claude/data/seaad"
cps = pd.read_csv(f"{D}/CPS.csv", index_col=0)
print("CPS regions:", cps["Brain Region"].unique())
cols = ["Donor ID", "Class", "Subclass", "Overall AD neuropathological Change", "Braak", "Severely Affected Donor",
        "Neurotypical reference", "Cognitive Status", "Age at Death"]
for reg in sys.argv[1:] or ["AnG", "V1C"]:
    X = pd.read_csv(f"{D}/{reg}.csv", usecols=cols, low_memory=False)
    X = X[~X["Neurotypical reference"].astype(str).str.lower().eq("true")]
    don = X.groupby("Donor ID").agg(adnc=("Overall AD neuropathological Change", "first"), braak=("Braak", "first"),
                                    severe=("Severely Affected Donor", "first"), age=("Age at Death", "first"))
    neur = X[X.Class.isin(["Neuronal: GABAergic", "Neuronal: Glutamatergic"])]
    cnt = neur.groupby(["Donor ID", "Class", "Subclass"]).size().rename("n").reset_index()
    tot = cnt.groupby(["Donor ID", "Class"]).n.transform("sum")
    cnt["frac_in_class"] = cnt.n / tot
    F = cnt.pivot_table(index="Donor ID", columns="Subclass", values="frac_in_class", fill_value=0)
    cls = neur.groupby(["Donor ID", "Class"]).size().unstack(fill_value=0)
    F["GABA_over_neurons"] = cls["Neuronal: GABAergic"] / cls.sum(1)
    F["n_neurons"] = cls.sum(1)
    c = cps[cps["Brain Region"].astype(str).str.contains(reg, case=False)].set_index("Donor ID")
    if len(c) == 0:
        c = cps.groupby("Donor ID")[["CPS_Global"]].mean(); col = "CPS_Global"
    else:
        col = "CPS_Local" if "CPS_Local" in c else "CPS_Global"
    F = F.join(don).join(c[[col]].rename(columns={col: "CPS"}), how="left")
    F = F[F.n_neurons >= 500]
    order = {"Not AD": 0, "Low": 1, "Intermediate": 2, "High": 3}
    F["adnc_n"] = F.adnc.map(order)
    print(f"\n=== {reg}: {len(F)} donors (>=500 neurons), CPS source = {col}, ADNC counts {F.adnc.value_counts().to_dict()}")
    gaba = ["Sst", "Pvalb", "Vip", "Lamp5", "Sncg", "Chandelier", "Sst Chodl", "Lamp5 Lhx6", "Pax6"]
    exc = [s for s in F.columns if any(t in str(s) for t in ["IT", "ET", "CT", "NP", "L6b"]) and s in cnt.Subclass.unique()]
    rows = []
    for s in [g for g in gaba if g in F] + exc + ["GABA_over_neurons"]:
        r1, p1 = spearmanr(F[s], F.CPS, nan_policy="omit")
        r2, p2 = spearmanr(F[s], F.adnc_n, nan_policy="omit")
        lo = F[F.adnc_n <= 1][s]; hi = F[F.adnc_n >= 3][s]
        rows.append(dict(subclass=s, mean_frac=F[s].mean(), rho_CPS=r1, p_CPS=p1, rho_ADNC=r2, p_ADNC=p2,
                         high_vs_notlow_ratio=hi.mean() / lo.mean() if lo.mean() > 0 else np.nan,
                         p_high_vs_notlow=mannwhitneyu(hi, lo).pvalue if len(hi) > 2 and len(lo) > 2 else np.nan))
    R = pd.DataFrame(rows)
    print(R.round(3).to_string(index=False))
    F.to_csv(f"/home/claude/work/seaad_{reg}_donor_fractions.csv")
