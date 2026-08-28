"""Experiment 024: finite-horizon controllability and response memory.

Uses the prospective raw paths and frozen EBID-gain targets from Experiment 022.
For each held-out test trajectory only, standardized state perturbations and
interventions are rolled forward for 5 and 20 steps. The primary test asks
whether these deeper regulator-facing descriptors predict EBID usefulness in a
completely unseen dynamical class.
"""
from __future__ import annotations
import csv, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from pcc_ebid_regulator.benchmark import benchmark_step
from pcc_ebid_regulator.dynamics import step as pcc_step
from pcc_ebid_regulator.oscillatory_benchmark import oscillatory_step
from pcc_ebid_regulator.panel_benchmarks import damped_oscillatory_step, neutral_step
from pcc_ebid_regulator.finite_horizon import finite_horizon_invariants

SRC=ROOT/'results'/'022_raw_path_invariants';OUT=ROOT/'results'/'024_finite_horizon_controllability';OUT.mkdir(parents=True,exist_ok=True)
SYSTEMS=['pcc','oscillatory_benchmark','damped_oscillator','directional_benchmark','neutral_diffusion']
RATIOS=[0.60,1.00];FAMILIES=range(4);META_ALPHA=1.0;DAMPING_CYCLES=0.75
FH_KEYS=[
 'fh_memory_amplification_h5','fh_memory_amplification_h20',
 'fh_memory_anisotropy_h5','fh_memory_anisotropy_h20',
 'fh_action_spread_h5','fh_action_spread_h20',
 'fh_action_spread_sd_h5','fh_action_spread_sd_h20',
 'fh_memory_persistence_ratio','fh_action_persistence_ratio']
META_KEYS=[k+s for k in FH_KEYS for s in ('_mean','_sd')]

def read_csv(path):
    with Path(path).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def write_csv(path,rows):
    if not rows:return
    with Path(path).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def col(rows,k):return np.asarray([float(r[k]) for r in rows],float)

def transition_for(row):
    system=row['system'];strength=float(row['strength']);regime=row['structure'];period=float(row['pcc_reference_cycle_period'])
    if system=='pcc':return lambda x,t:pcc_step(x,strength=strength,topology=regime)
    if system=='oscillatory_benchmark':return lambda x,t:oscillatory_step(x,t=t,period=period,strength=strength,regime=regime)
    if system=='damped_oscillator':return lambda x,t:damped_oscillatory_step(x,t=t,period=period,strength=strength,regime=regime,damping_cycles=DAMPING_CYCLES)
    if system=='directional_benchmark':return lambda x,t:benchmark_step(x,strength=strength,regime=regime)
    return lambda x,t:neutral_step(x,regime=regime)

def fold_targets_and_descriptors():
    gains=read_csv(SRC/'fold_gains_and_raw_descriptors.csv')
    fold_rows=[];trajectory_rows=[]
    for g in gains:
        system=g['system'];fi=int(g['heldout_family']);ratio=float(g['target_cycle_ratio'])
        rows=read_csv(SRC/f'dataset_{system}_f{fi}_r{ratio:.2f}.csv')
        npz=np.load(SRC/f'raw_paths_{system}_f{fi}_r{ratio:.2f}.npz')
        te=[r for r in rows if int(r['structure_index'])==0 and float(r['noise_sigma']) in (0.01,0.02)]
        enriched=[]
        for r in te:
            traj=np.asarray(npz[r['raw_path_key']],float)
            feats=finite_horizon_invariants(traj,transition_for(r))
            enriched.append({**r,**feats})
            trajectory_rows.append({'system':system,'heldout_family':fi,'target_cycle_ratio':ratio,'raw_path_key':r['raw_path_key'],**feats})
        rec={'system':system,'heldout_family':fi,'target_cycle_ratio':ratio,'relative_mae_reduction':float(g['relative_mae_reduction'])}
        for k in FH_KEYS:
            a=np.asarray([float(r[k]) for r in enriched]);rec[k+'_mean']=float(a.mean());rec[k+'_sd']=float(a.std())
        fold_rows.append(rec)
    write_csv(OUT/'trajectory_finite_horizon_features.csv',trajectory_rows)
    write_csv(OUT/'fold_gains_and_finite_horizon_descriptors.csv',fold_rows)
    return fold_rows

def design(rows,include):
    cols=[col(rows,'target_cycle_ratio')]
    if include:cols += [col(rows,k) for k in META_KEYS]
    return np.column_stack(cols)
def ridge_predict(train,test,include,known_classes=False):
    def dm(rows):
        cols=[col(rows,'target_cycle_ratio')]
        if known_classes:
            cols += [np.asarray([1.0 if r['system']==s else 0.0 for r in rows]) for s in SYSTEMS[:-1]]
        if include:cols += [col(rows,k) for k in META_KEYS]
        return np.column_stack(cols)
    X=dm(train);Z=dm(test);y=col(train,'relative_mae_reduction');mu=X.mean(0);sd=X.std(0);sd[sd<1e-10]=1;X=(X-mu)/sd;Z=(Z-mu)/sd
    Xa=np.column_stack([np.ones(len(X)),X]);Za=np.column_stack([np.ones(len(Z)),Z]);pen=np.eye(Xa.shape[1]);pen[0,0]=0
    b=np.linalg.solve(Xa.T@Xa+META_ALPHA*pen,Xa.T@y);return Za@b
def mae(y,p):return float(np.mean(np.abs(np.asarray(y)-np.asarray(p))))
def r2(y,p):
    y=np.asarray(y,float);p=np.asarray(p,float);d=np.sum((y-y.mean())**2);return float(1-np.sum((y-p)**2)/d) if d>1e-12 else float('nan')

def class_cv(folds):
    preds=[];summary=[]
    for held in SYSTEMS:
        tr=[r for r in folds if r['system']!=held];te=[r for r in folds if r['system']==held];y=col(te,'relative_mae_reduction');p0=ridge_predict(tr,te,False);p1=ridge_predict(tr,te,True);b=mae(y,p0);e=mae(y,p1)
        summary.append({'heldout_system':held,'n_test':len(te),'scale_only_mae':b,'finite_horizon_mae':e,'relative_mae_reduction':(b-e)/b,'finite_horizon_r2':r2(y,p1)})
        for r,a,z in zip(te,p0,p1):preds.append({'heldout_system':held,'target_cycle_ratio':r['target_cycle_ratio'],'heldout_family':r['heldout_family'],'ebid_gain':r['relative_mae_reduction'],'scale_only_prediction':float(a),'finite_horizon_prediction':float(z)})
    y=col(preds,'ebid_gain');p0=col(preds,'scale_only_prediction');p1=col(preds,'finite_horizon_prediction');b=mae(y,p0);e=mae(y,p1)
    summary.append({'heldout_system':'ALL','n_test':len(preds),'scale_only_mae':b,'finite_horizon_mae':e,'relative_mae_reduction':(b-e)/b,'finite_horizon_r2':r2(y,p1)})
    return preds,summary

def family_cv(folds):
    preds=[]
    for held in FAMILIES:
        tr=[r for r in folds if int(r['heldout_family'])!=held];te=[r for r in folds if int(r['heldout_family'])==held];y=col(te,'relative_mae_reduction');p0=ridge_predict(tr,te,False,True);p1=ridge_predict(tr,te,True,True)
        for r,a,z in zip(te,p0,p1):preds.append({'heldout_family':held,'system':r['system'],'target_cycle_ratio':r['target_cycle_ratio'],'ebid_gain':r['relative_mae_reduction'],'class_scale_prediction':float(a),'finite_horizon_prediction':float(z)})
    y=col(preds,'ebid_gain');p0=col(preds,'class_scale_prediction');p1=col(preds,'finite_horizon_prediction');b=mae(y,p0);e=mae(y,p1)
    return preds,[{'protocol':'leave_one_family_out_known_classes','n_test':len(preds),'class_scale_mae':b,'finite_horizon_mae':e,'relative_mae_reduction':(b-e)/b,'class_scale_r2':r2(y,p0),'finite_horizon_r2':r2(y,p1)}]

def correlations(folds):
    y=col(folds,'relative_mae_reduction');out=[]
    for k in META_KEYS:
        x=col(folds,k);rr=float(np.corrcoef(x,y)[0,1]) if np.std(x)>1e-12 else 0.0;out.append({'descriptor':k,'pearson_r':rr})
    return sorted(out,key=lambda z:abs(z['pearson_r']),reverse=True)

def main():
    folds=fold_targets_and_descriptors();write_csv(OUT/'finite_horizon_correlations.csv',correlations(folds));cp,cs=class_cv(folds);write_csv(OUT/'class_cv_predictions.csv',cp);write_csv(OUT/'class_cv_summary.csv',cs);fp,fs=family_cv(folds);write_csv(OUT/'family_cv_predictions.csv',fp);write_csv(OUT/'family_cv_summary.csv',fs)
    print('EXPERIMENT 024: FINITE-HORIZON CONTROLLABILITY / RESPONSE MEMORY')
    for r in cs:print(f"{r['heldout_system']:<24} FH-vs-scale MAE change={100*float(r['relative_mae_reduction']):+6.1f}% R2={float(r['finite_horizon_r2']):+.3f}")
    print('Known-class family CV:',fs[0])
if __name__=='__main__':main()
