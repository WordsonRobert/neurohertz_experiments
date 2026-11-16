import numpy as np, pandas as pd, glob, os
from scipy.stats import mannwhitneyu, spearmanr
F='/mnt/user-data/uploads/neurohertz2/classification/cache/ds004504/main/feat'
P=pd.read_csv('/home/claude/data/ds004504/participants.tsv',sep='\t').set_index('participant_id')
der=pd.read_csv('/home/claude/work/flanks.csv').set_index('sub')
def line_bump(f,lp,fl):
    m=np.zeros_like(f,bool)
    for a,b in fl: m|=(f>=a)&(f<=b)
    c=np.polyfit(np.log10(f[m]),lp[m],1); k=(f>=32)&(f<=40)
    return np.mean(lp[k]-np.polyval(c,np.log10(f[k]))), c[0]
rows=[]
for fn in sorted(glob.glob(F+'/sub-*.npz')):
    s=os.path.basename(fn)[:-4]
    if P.loc[s,'Group'] not in 'AC': continue
    z=np.load(fn); f=z['freqs']; ch=list(z['ch_names']); idx=[ch.index(c) for c in ['P3','P4','Pz']]
    r=dict(sub=s,group=P.loc[s,'Group'])
    for ref in ['csd','avg']:
        lp=np.log10(np.mean(10**z['logpsd_'+ref][idx],0))
        r[f'{ref}_bump_h11'],r[f'{ref}_slope_h11']=line_bump(f,lp,[(24,30),(42,47)])
        r[f'{ref}_bump_my'],r[f'{ref}_slope_my']=line_bump(f,lp,[(24,30),(41,44)])
        for nm,(a,b) in {'beta':(16,23),'lo':(24,30),'mid':(32,40),'hi':(42,47)}.items():
            r[f'{ref}_{nm}']=lp[(f>=a)&(f<=b)].mean()
    rows.append(r)
D=pd.DataFrame(rows).set_index('sub').join(der[['local_bump','local_slope']].rename(columns=lambda c:'der_'+c))
def g(a,b):
    s=np.sqrt(((len(a)-1)*a.var(ddof=1)+(len(b)-1)*b.var(ddof=1))/(len(a)+len(b)-2)); return (a.mean()-b.mean())/s
print('freq range', f.min(), f.max())
for c in D.columns[1:]:
    a=D[D.group=='A'][c].dropna(); b=D[D.group=='C'][c].dropna()
    print(f'{c:18s} g={g(a,b):+.2f}  p={mannwhitneyu(a,b).pvalue:.3f}')
print('\nper-subject agreement (spearman):')
for x,y in [('csd_bump_h11','avg_bump_h11'),('csd_bump_h11','der_local_bump'),('avg_bump_my','der_local_bump'),('csd_slope_h11','der_local_slope')]:
    print(x,y, round(spearmanr(D[x],D[y],nan_policy='omit')[0],2))
print('\n--- periodic vs aperiodic split (CSD, P3/P4/Pz) ---')
rows=[]
for fn in sorted(glob.glob(F+'/sub-*.npz')):
    s=os.path.basename(fn)[:-4]
    if P.loc[s,'Group'] not in 'AC': continue
    z=np.load(fn); sf=z['sp_freqs']; ch=list(z['ch_names']); idx=[ch.index(c) for c in ['P3','P4','Pz']]
    per=z['sp_periodic_csd'][idx].mean(0); ap=z['sp_aperiodic_csd'][idx].mean(0)
    r=dict(group=P.loc[s,'Group'])
    for nm,(a,b) in {'beta16_23':(16,23),'b24_30':(24,30),'g32_40':(32,40)}.items():
        m=(sf>=a)&(sf<=b); r['per_'+nm]=per[m].mean(); r['ap_'+nm]=ap[m].mean()
    r['ap_slope_24_45']=np.polyfit(np.log10(sf[(sf>=24)&(sf<=45)]),ap[(sf>=24)&(sf<=45)],1)[0]
    rows.append(r)
E=pd.DataFrame(rows)
for c in E.columns[1:]:
    a=E[E.group=='A'][c].dropna(); b=E[E.group=='C'][c].dropna()
    print(f'{c:16s} g={g(a,b):+.2f}  p={mannwhitneyu(a,b).pvalue:.3f}')
print('sp_freqs range', sf.min(), sf.max())
