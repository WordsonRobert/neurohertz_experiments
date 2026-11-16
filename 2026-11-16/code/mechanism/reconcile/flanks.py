import sys, numpy as np, pandas as pd, mne
from scipy.signal import welch
mne.set_log_level('ERROR')
d = sys.argv[1]
p = pd.read_csv(f'{d}/participants.tsv', sep='\t'); p = p[p.Group.isin(['A','C'])]
bands = {'beta_16_23':(16,23),'flank_24_30':(24,30),'bump_32_40':(32,40),'flank_41_44':(41,44)}
rows=[]
for _,r in p.iterrows():
    raw = mne.io.read_raw_eeglab(f'{d}/{r.participant_id}_task-eyesclosed_eeg.set', preload=True)
    x = raw.get_data(picks=['P3','P4','Pz'])
    f, P = welch(x, fs=raw.info['sfreq'], nperseg=1000, axis=-1)
    P = P.mean(0)
    rec = dict(sub=r.participant_id, group=r.Group, age=r.Age)
    for k,(a,b) in bands.items(): rec[k] = np.log10(P[(f>=a)&(f<=b)].mean())
    # local line in log-log through flanks 24-30 and 41-44, residual at 32-40
    m = ((f>=24)&(f<=30))|((f>=41)&(f<=44)); c = np.polyfit(np.log10(f[m]), np.log10(P[m]), 1)
    b = (f>=32)&(f<=40); rec['local_bump'] = np.mean(np.log10(P[b]) - np.polyval(c, np.log10(f[b]))); rec['local_slope']=c[0]
    rows.append(rec)
df = pd.DataFrame(rows); df.to_csv('/home/claude/work/flanks.csv', index=False)
def g(a,b):
    s=np.sqrt(((len(a)-1)*a.var(ddof=1)+(len(b)-1)*b.var(ddof=1))/(len(a)+len(b)-2)); return (a.mean()-b.mean())/s*(1-3/(4*(len(a)+len(b))-9))
from scipy.stats import mannwhitneyu
for k in list(bands)+['local_bump','local_slope']:
    a=df[df.group=='A'][k]; c=df[df.group=='C'][k]
    print(f'{k:14s} AD {a.mean():8.3f}  CN {c.mean():8.3f}  g={g(a,c):+.2f}  p_MW={mannwhitneyu(a,c).pvalue:.3f}')
