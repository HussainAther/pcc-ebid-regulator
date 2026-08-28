"""Experiment 023: predictive and response invariants.

Uses the prospectively retained raw paths from Experiment 022 and augments each
trajectory with mechanism-agnostic predictability statistics plus standardized
finite-difference response probes. The primary test remains leave-one-dynamical-
class-out prediction of EBID's incremental regulator-demand benefit.

No EBID/entropy feature is used as a meta-level explanatory invariant.
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
from pcc_ebid_regulator.response_invariants import response_invariants

SRC=ROOT/'results'/'022_raw_path_invariants';OUT=ROOT/'results'/'023_response_invariants';OUT.mkdir(parents=True,exist_ok=True)
SYSTEMS=['pcc','oscillatory_benchmark','damped_oscillator','directional_benchmark','neutral_diffusion']
RATIOS=[0.60,1.00];FAMILIES=range(4);META_ALPHA=1.0;DAMPING_CYCLES=0.75
RESP_KEYS=['resp_linear_forecast_error','resp_innovation_variance','resp_predictability_decay','resp_jacobian_fro_mean','resp_jacobian_fro_sd','resp_perturbation_amplification_mean','resp_perturbation_amplification_sd','resp_local_anisotropy_mean']


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

def augment_chunk(system,fi,ratio):
    rows=read_csv(SRC/f'dataset_{system}_f{fi}_r{ratio:.2f}.csv')
    npz=np.load(SRC/f'raw_paths_{system}_f{fi}_r{ratio:.2f}.npz')
    out=[]
    for r in rows:
        traj=np.asarray(npz[r['raw_path_key']],float)
        out.append({**r,**response_invariants(traj,transition_for(r))})
    return out

def fold_targets_and_descriptors():
    gains=read_csv(SRC/'fold_gains_and_raw_descriptors.csv')
    all_rows=[]
    for system in SYSTEMS:
      for fi in FAMILIES:
        for ratio in RATIOS:all_rows += augment_chunk(system,fi,ratio)
    write_csv(OUT/'trajectory_response_features.csv',all_rows)
    idx={(r['system'],int(r['seed_family']),round(float(r['target_cycle_ratio']),2)):[] for r in all_rows}
    for r in all_rows:idx[(r['system'],int(r['seed_family']),round(float(r['target_cycle_ratio']),2))].append(r)
    folds=[]
    for g in gains:
        key=(g['system'],int(g['heldout_family']),round(float(g['target_cycle_ratio']),2));rr=idx[key]
        # Match the actual held-out test subset from 022: structure index 0, high noise.
        te=[r for r in rr if int(r['structure_index'])==0 and float(r['noise_sigma']) in (0.01,0.02)]
        rec={'system':g['system'],'heldout_family':int(g['heldout_family']),'target_cycle_ratio':float(g['target_cycle_ratio']),'relative_mae_reduction':float(g['relative_mae_reduction'])}
        for k in RESP_KEYS:
            a=col(te,k);rec[k+'_mean']=float(a.mean());rec[k+'_sd']=float(a.std())
        folds.append(rec)
    write_csv(OUT/'fold_gains_and_response_descriptors.csv',folds)
    return folds

META_KEYS=[k+s for k in RESP_KEYS for s in ('_mean','_sd')]
def design(rows,include_resp):
    cols=[col(rows,'target_cycle_ratio')]
    if include_resp:cols += [col(rows,k) for k in META_KEYS]
    return np.column_stack(cols)
def predict(train,test,include_resp):
    X=design(train,include_resp);Z=design(test,include_resp);y=col(train,'relative_mae_reduction');mu=X.mean(0);sd=X.std(0);sd[sd<1e-10]=1;X=(X-mu)/sd;Z=(Z-mu)/sd
    Xa=np.column_stack([np.ones(len(X)),X]);Za=np.column_stack([np.ones(len(Z)),Z]);pen=np.eye(Xa.shape[1]);pen[0,0]=0
    b=np.linalg.solve(Xa.T@Xa+META_ALPHA*pen,Xa.T@y);return Za@b
def mae(y,p):return float(np.mean(np.abs(np.asarray(y)-np.asarray(p))))
def r2(y,p):
    y=np.asarray(y,float);p=np.asarray(p,float);d=np.sum((y-y.mean())**2);return float(1-np.sum((y-p)**2)/d) if d>1e-12 else float('nan')

def class_cv(folds):
    preds=[];summary=[]
    for held in SYSTEMS:
        tr=[r for r in folds if r['system']!=held];te=[r for r in folds if r['system']==held];y=col(te,'relative_mae_reduction');p0=predict(tr,te,False);p1=predict(tr,te,True);b=mae(y,p0);e=mae(y,p1)
        summary.append({'heldout_system':held,'n_test':len(te),'scale_only_mae':b,'response_descriptor_mae':e,'relative_mae_reduction':(b-e)/b,'response_descriptor_r2':r2(y,p1)})
        for r,a,z in zip(te,p0,p1):preds.append({'heldout_system':held,'target_cycle_ratio':r['target_cycle_ratio'],'heldout_family':r['heldout_family'],'ebid_gain':r['relative_mae_reduction'],'scale_only_prediction':float(a),'response_prediction':float(z)})
    y=col(preds,'ebid_gain');p0=col(preds,'scale_only_prediction');p1=col(preds,'response_prediction');b=mae(y,p0);e=mae(y,p1)
    summary.append({'heldout_system':'ALL','n_test':len(preds),'scale_only_mae':b,'response_descriptor_mae':e,'relative_mae_reduction':(b-e)/b,'response_descriptor_r2':r2(y,p1)})
    return preds,summary

def family_design(rows,include_resp):
    cols=[col(rows,'target_cycle_ratio')]
    cols += [np.asarray([1.0 if r['system']==sysn else 0.0 for r in rows],float) for sysn in SYSTEMS[:-1]]
    if include_resp:cols += [col(rows,k) for k in META_KEYS]
    return np.column_stack(cols)
def family_predict(train,test,include_resp):
    X=family_design(train,include_resp);Z=family_design(test,include_resp);y=col(train,'relative_mae_reduction');mu=X.mean(0);sd=X.std(0);sd[sd<1e-10]=1;X=(X-mu)/sd;Z=(Z-mu)/sd
    Xa=np.column_stack([np.ones(len(X)),X]);Za=np.column_stack([np.ones(len(Z)),Z]);pen=np.eye(Xa.shape[1]);pen[0,0]=0
    b=np.linalg.solve(Xa.T@Xa+META_ALPHA*pen,Xa.T@y);return Za@b
def family_cv(folds):
    preds=[]
    for held in FAMILIES:
        tr=[r for r in folds if int(r['heldout_family'])!=held];te=[r for r in folds if int(r['heldout_family'])==held];y=col(te,'relative_mae_reduction');p0=family_predict(tr,te,False);p1=family_predict(tr,te,True)
        for r,a,z in zip(te,p0,p1):preds.append({'heldout_family':held,'system':r['system'],'target_cycle_ratio':r['target_cycle_ratio'],'ebid_gain':r['relative_mae_reduction'],'class_scale_prediction':float(a),'response_prediction':float(z)})
    y=col(preds,'ebid_gain');p0=col(preds,'class_scale_prediction');p1=col(preds,'response_prediction');b=mae(y,p0);e=mae(y,p1)
    return preds,[{'protocol':'leave_one_family_out_known_classes','n_test':len(preds),'class_scale_mae':b,'response_descriptor_mae':e,'relative_mae_reduction':(b-e)/b,'class_scale_r2':r2(y,p0),'response_descriptor_r2':r2(y,p1)}]

def correlations(folds):
    y=col(folds,'relative_mae_reduction');out=[]
    for k in META_KEYS:
        x=col(folds,k);r=float(np.corrcoef(x,y)[0,1]) if np.std(x)>1e-12 else 0.0;out.append({'descriptor':k,'pearson_r':r})
    return sorted(out,key=lambda z:abs(z['pearson_r']),reverse=True)

def main():
    folds=fold_targets_and_descriptors();write_csv(OUT/'response_descriptor_correlations.csv',correlations(folds));preds,summ=class_cv(folds);write_csv(OUT/'class_cv_predictions.csv',preds);write_csv(OUT/'class_cv_summary.csv',summ);fp,fs=family_cv(folds);write_csv(OUT/'family_cv_predictions.csv',fp);write_csv(OUT/'family_cv_summary.csv',fs)
    print('LEAVE-ONE-DYNAMICAL-CLASS-OUT RESPONSE-INVARIANT TEST')
    for r in summ:print(f"{r['heldout_system']:<24} response-vs-scale MAE change={100*float(r['relative_mae_reduction']):+6.1f}% R2={float(r['response_descriptor_r2']):+.3f}")
if __name__=='__main__':main()
