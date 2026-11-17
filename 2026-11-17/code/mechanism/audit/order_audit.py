"""P14: audit of the probe-order gain G (H17). Decomposes G into
 (i) readout-schedule term (commuting probes, readouts taken at different accumulated states),
 (ii) non-commuting term (state update depends on current state, so final state depends on order),
 plus controls: alpha=0, tissue permutation (static data, must give G=0 exactly), finite-difference step.
Also the labelled mixed-order design criterion: mixing helps over pure AB iff Tr(I_AB^-1 I_BA) > d.
"""
import json, sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/claude/work/framework"); sys.path.insert(0, "/home/claude/work/phaseB"); sys.path.insert(0, "/home/claude/work")
import probe_order as P   # reuses circuit, H2, rel, noise, features, cals
import model as M
from bridge import features

def run(base, th, seq, alpha, mode="full", readout="all"):
    """mode: full = increment depends on current adapted state (non-commuting)
             commute = increment computed on the unadapted circuit (increments commute; a_final order-free)
       readout: all = record every probe; terminal = record drives only as state updates, record final rest only."""
    p = P.circuit(base, th); a = 0.0; obs = []; noise = []
    for i, probe in enumerate(seq):
        q = dict(p); q["gE"] = p["gE"] * (1 - a)
        last = i == len(seq) - 1
        if probe == "rest":
            if readout == "all" or last:
                obs += list(P.rel(features(P.fq, np.log10(M.psd(q, P.fq))))); noise += list(P.se_rest)
        elif probe.startswith("drive"):
            fd = float(probe[5:])
            r = P.H2(q if mode == "full" else p, [fd])[0]
            if readout == "all":
                obs.append(10 * np.log10(P.H2(q, [fd])[0])); noise.append(P.SE_PH)
            a = a + alpha * r / P.H2(base, [fd])[0]
        elif probe == "tissue":
            obs.append(-0.27 * th[2]); noise.append(P.SE_TIS)
    return np.array(obs), np.array(noise)

def fisher(base, seq, alpha, h=0.05, **kw):
    th0 = np.zeros(3); y0, S = run(base, th0, seq, alpha, **kw)
    J = np.column_stack([(run(base, th0 + h * e, seq, alpha, **kw)[0] - y0) / h for e in np.eye(3)])
    return J.T @ np.diag(1 / S ** 2) @ J

def ld(F): return np.sum(np.log(np.maximum(np.linalg.eigvalsh(F), 1e-12)))

AB = ["rest", "drive20", "drive40", "rest"]; BA = ["rest", "drive40", "drive20", "rest"]
if __name__ == "__main__":
    rows = []
    for alpha in (0.0, 0.05, 0.15, 0.30):
        for mode in ("full", "commute"):
            for readout in ("all", "terminal"):
                for h in (0.05, 0.01):
                    Gs, tr = [], []
                    for b in P.cals:
                        Fa, Fb = fisher(b, AB, alpha, h, mode=mode, readout=readout), fisher(b, BA, alpha, h, mode=mode, readout=readout)
                        Gs.append(ld(Fa) - ld(Fb))
                        try: tr.append(np.trace(np.linalg.solve(Fa, Fb)))
                        except np.linalg.LinAlgError: tr.append(np.nan)
                    rows.append(dict(alpha=alpha, mode=mode, readout=readout, h=h, G_median=np.median(Gs),
                                     G_q25=np.percentile(Gs, 25), G_q75=np.percentile(Gs, 75),
                                     tr_IAB_inv_IBA=np.nanmedian(tr)))
    R = pd.DataFrame(rows); pd.set_option("display.width", 200)
    print(R.round(4).to_string(index=False))
    R.to_csv("/home/claude/work/audit/G_decomposition.csv", index=False)
    
    # tissue permutation control: static data -> G must be exactly 0
    t = []
    for b in P.cals:
        F1 = fisher(b, ["rest", "drive40", "rest", "tissue"], 0.15); F2 = fisher(b, ["tissue", "rest", "drive40", "rest"], 0.15)
        t.append(ld(F1) - ld(F2))
    print("\ntissue position permuted (alpha .15): max |G| over calibrations =", np.max(np.abs(t)))
    
    # final adapted state difference: direct readout of non-commutativity
    b = P.cals[0]
    def a_final(seq, alpha, th, mode):
        p = P.circuit(b, th); a = 0.0
        for probe in seq:
            if probe.startswith("drive"):
                fd = float(probe[5:]); q = dict(p); q["gE"] = p["gE"] * (1 - a)
                a += alpha * P.H2(q if mode == "full" else p, [fd])[0] / P.H2(b, [fd])[0]
        return a
    for mode in ("full", "commute"):
        d = [a_final(AB, .15, th, mode) - a_final(BA, .15, th, mode) for th in (np.zeros(3), np.array([.4, 0, 0]), np.array([0, .4, 0]), np.array([0, 0, .4]))]
        print(f"a_AB - a_BA ({mode}) at theta = 0, M4 .4, M1 .4, L23 .4:", np.round(d, 6))
    
    # mixed design: best labelled mixture p* of AB vs BA (D-optimal)
    ps = np.linspace(0, 1, 101); best = []
    for b in P.cals:
        Fa, Fb = fisher(b, AB, .15), fisher(b, BA, .15)
        v = [ld(p * Fa + (1 - p) * Fb) for p in ps]; best.append((ps[int(np.argmax(v))], max(v) - ld(Fa)))
    print("\nmixture alpha .15: p* (weight on AB) median", np.median([x[0] for x in best]), "| gain over pure AB median", np.round(np.median([x[1] for x in best]), 4))
    json.dump({"tissue_perm_maxG": float(np.max(np.abs(t))), "mix_p_star": [x[0] for x in best], "mix_gain": [x[1] for x in best]},
              open("/home/claude/work/audit/controls.json", "w"))
