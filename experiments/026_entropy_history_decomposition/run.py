"""Experiment 026: entropy-history decomposition for direct control benefit.

Reuse the frozen Experiment-025 dataset. Primary protocol is leave-one-dynamical-
class-out. Decompose predictive information into:
  M0: strong nonlinear current-state/geometry representation
  M1: M0 + endpoint entropy H_end
  M2: M1 + historical entropy H_initial, H_mean
  M3: M2 + remaining canonical EBID rate/deficit-rate features

A second sanity track places the exact endpoint entropy transform inside the
state baseline before any history is added. This distinguishes a convenient
nonlinear transform of current state from genuine trajectory-history value.
"""
from __future__ import annotations
import csv, itertools, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
SRC=ROOT/'results'/'025_direct_control_benefit'/'dataset.csv'
OUT=ROOT/'results'/'026_entropy_history_decomposition'; OUT.mkdir(parents=True,exist_ok=True)
SYSTEMS=['pcc','oscillatory_benchmark','damped_oscillator','directional_benchmark','neutral_diffusion']
TARGET='control_relative_benefit'; ALPHA=10.0
H_END='ebid_end_entropy'; H_HISTORY=['ebid_initial_entropy','ebid_mean_entropy']
RATE_KEYS=['ebid_entropy_drop','ebid_entropy_slope','ebid_mean_entropy_rate','ebid_min_entropy_rate','ebid_entropy_rate_variance','ebid_deficit_growth','ebid_max_deficit_rate','ebid_deficit_rate_variance']


def read_csv(p):
    with Path(p).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def write_csv(p,rows):
    if not rows:return
    with Path(p).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def col(rows,k): return np.asarray([float(r[k]) for r in rows],float)
def mae(y,p): return float(np.mean(np.abs(np.asarray(y)-np.asarray(p))))
def r2(y,p):
    y=np.asarray(y,float);p=np.asarray(p,float);d=np.sum((y-y.mean())**2)
    return float(1-np.sum((y-p)**2)/d) if d>1e-12 else float('nan')

def state_matrix(rows, include_exact_entropy=False):
    # Strong class-blind current-state representation. No trajectory summaries.
    P=col(rows,'P'); C=col(rows,'C'); Ch=col(rows,'Ch'); s=col(rows,'strength'); ratio=col(rows,'target_cycle_ratio')
    base=[ratio,s,P,C,Ch]
    # all monomials in P,C,Ch through degree 3, plus state-strength interactions
    xs=[P,C,Ch]
    for degree in (2,3):
        for inds in itertools.combinations_with_replacement(range(3),degree):
            v=np.ones(len(rows))
            for i in inds:v*=xs[i]
            base.append(v)
    base += [s*P,s*C,s*Ch,s*s,ratio*P,ratio*C,ratio*Ch,ratio*s]
    # smooth nonlinear current-state transforms independent of trajectory history
    eps=1e-12
    for x in xs:
        base += [np.log(np.clip(x,eps,None)), np.sqrt(np.clip(x,0,None))]
    center=np.sqrt((P-1/3)**2+(C-1/3)**2+(Ch-1/3)**2)
    base += [center,center**2]
    if include_exact_entropy:
        H=-(P*np.log(np.clip(P,eps,None))+C*np.log(np.clip(C,eps,None))+Ch*np.log(np.clip(Ch,eps,None)))
        base.append(H)
    return np.column_stack(base)

def extra_matrix(rows, keys):
    return np.column_stack([col(rows,k) for k in keys]) if keys else np.empty((len(rows),0))

def design(rows, stage, exact_entropy_baseline=False):
    X=state_matrix(rows,include_exact_entropy=exact_entropy_baseline)
    keys=[]
    if stage>=1 and not exact_entropy_baseline: keys += [H_END]
    if stage>=2: keys += H_HISTORY
    if stage>=3: keys += RATE_KEYS
    if keys:X=np.column_stack([X,extra_matrix(rows,keys)])
    return X

def ridge(train,test,stage,exact_entropy_baseline=False):
    X=design(train,stage,exact_entropy_baseline); Z=design(test,stage,exact_entropy_baseline); y=col(train,TARGET)
    mu=X.mean(0); sd=X.std(0); sd[sd<1e-10]=1; X=(X-mu)/sd; Z=(Z-mu)/sd
    Xa=np.column_stack([np.ones(len(X)),X]); Za=np.column_stack([np.ones(len(Z)),Z]); pen=np.eye(Xa.shape[1]);pen[0,0]=0
    b=np.linalg.solve(Xa.T@Xa+ALPHA*pen,Xa.T@y); return Za@b

def evaluate(rows, exact=False):
    preds=[]
    for held in SYSTEMS:
        tr=[r for r in rows if r['system']!=held]; te=[r for r in rows if r['system']==held]; y=col(te,TARGET)
        ps=[ridge(tr,te,k,exact) for k in range(4)]
        for i,(r,*vals) in enumerate(zip(te,*ps)):
            preds.append({'track':'exact_entropy_state' if exact else 'nonlinear_state','heldout_system':held,'seed_family':r['seed_family'],'target_cycle_ratio':r['target_cycle_ratio'],'actual':float(y[i]),'m0':float(vals[0]),'m1':float(vals[1]),'m2':float(vals[2]),'m3':float(vals[3])})
    out=[]
    for held in SYSTEMS+['ALL']:
        rr=preds if held=='ALL' else [r for r in preds if r['heldout_system']==held]
        y=col(rr,'actual'); ms=[mae(y,col(rr,f'm{k}')) for k in range(4)]; rs=[r2(y,col(rr,f'm{k}')) for k in range(4)]
        out.append({'track':'exact_entropy_state' if exact else 'nonlinear_state','heldout_system':held,'n_test':len(rr),'m0_mae':ms[0],'m1_mae':ms[1],'m2_mae':ms[2],'m3_mae':ms[3],
                    'm0_r2':rs[0],'m1_r2':rs[1],'m2_r2':rs[2],'m3_r2':rs[3],
                    'end_entropy_increment':0.0 if exact else (ms[0]-ms[1])/ms[0],
                    'history_increment':(ms[1]-ms[2])/ms[1],
                    'rate_increment':(ms[2]-ms[3])/ms[2],
                    'full_history_gain_vs_m0':(ms[0]-ms[3])/ms[0]})
    return preds,out

def family_cv(rows, exact=True):
    fams=sorted({int(r['seed_family']) for r in rows}); preds=[]
    for held in fams:
        tr=[r for r in rows if int(r['seed_family'])!=held];te=[r for r in rows if int(r['seed_family'])==held];y=col(te,TARGET)
        ps=[ridge(tr,te,k,exact) for k in range(4)]
        for i,(r,*vals) in enumerate(zip(te,*ps)):
            preds.append({'heldout_family':held,'system':r['system'],'actual':float(y[i]),'m0':float(vals[0]),'m2':float(vals[2]),'m3':float(vals[3])})
    y=col(preds,'actual');m0=mae(y,col(preds,'m0'));m2=mae(y,col(preds,'m2'));m3=mae(y,col(preds,'m3'))
    return preds,[{'protocol':'leave_one_family_out_exact_entropy_state','n_test':len(preds),'m0_mae':m0,'m2_mae':m2,'m3_mae':m3,'history_gain':(m0-m2)/m0,'rate_increment':(m2-m3)/m2,'full_gain':(m0-m3)/m0,'m0_r2':r2(y,col(preds,'m0')),'m3_r2':r2(y,col(preds,'m3'))}]

def bootstrap_increment(preds, a='m0', b='m2', B=2000,seed=26026):
    rng=np.random.default_rng(seed); y=col(preds,'actual');pa=col(preds,a);pb=col(preds,b); n=len(y); vals=[]
    for _ in range(B):
        ix=rng.integers(0,n,n);ma=mae(y[ix],pa[ix]);mb=mae(y[ix],pb[ix]);vals.append((ma-mb)/ma if ma>1e-12 else 0)
    return {'comparison':f'{a}_to_{b}','mean':float(np.mean(vals)),'lo95':float(np.quantile(vals,.025)),'hi95':float(np.quantile(vals,.975))}

def main():
    rows=read_csv(SRC)
    p1,s1=evaluate(rows,False);p2,s2=evaluate(rows,True); write_csv(OUT/'class_cv_predictions.csv',p1+p2);write_csv(OUT/'class_cv_summary.csv',s1+s2)
    fp,fs=family_cv(rows,True);write_csv(OUT/'family_cv_predictions.csv',fp);write_csv(OUT/'family_cv_summary.csv',fs)
    exact_all=[r for r in p2]; boot=[bootstrap_increment(exact_all,'m0','m2'),bootstrap_increment(exact_all,'m2','m3')];write_csv(OUT/'bootstrap.csv',boot)
    print('EXPERIMENT 026: ENTROPY-HISTORY DECOMPOSITION')
    for r in s2:
        print(f"{r['heldout_system']:<24} history={100*float(r['history_increment']):+6.1f}% rate={100*float(r['rate_increment']):+6.1f}% full={100*float(r['full_history_gain_vs_m0']):+6.1f}% R2={float(r['m3_r2']):+.3f}")
    print('Family CV',fs[0]);print('Bootstrap',boot)
if __name__=='__main__':main()
