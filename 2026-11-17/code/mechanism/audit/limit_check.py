import numpy as np, sys
sys.path.insert(0,"."); from order_audit import fisher, ld, AB, BA, P
import pandas as pd
rows=[]
for alpha in (0.05,0.15,0.30):
  for h in (0.05,0.01,0.003,0.001):
    for mode in ("full","commute"):
      G=[];
      for b in P.cals: G.append(ld(fisher(b,AB,alpha,h,mode=mode))-ld(fisher(b,BA,alpha,h,mode=mode)))
      rows.append(dict(alpha=alpha,h=h,mode=mode,G=np.median(G)))
R=pd.DataFrame(rows).pivot_table(index=["alpha","h"],columns="mode",values="G"); R["bracket=full-commute"]=R["full"]-R["commute"]
print(R.round(4)); R.to_csv("G_limit.csv")
print("\nterminal-readout eigenvalues (median over cals), h=.002")
for alpha in (0.0,0.15,0.30):
  for nm,seq in (("rest only",["rest"]),("AB",AB),("BA",BA)):
    for mode in ("full","commute"):
      ev=np.median([np.linalg.eigvalsh(fisher(b,seq,alpha,0.002,mode=mode,readout="terminal")) for b in P.cals],axis=0)
      print(alpha,nm,mode,np.array2string(ev,precision=5))
