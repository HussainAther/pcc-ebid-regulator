"""Experiment 025: direct EBID prediction of achievable control benefit.

Regenerate no dynamics: reuse Experiment 022's prospective observation paths.
From each endpoint, construct a standardized deterministic 40-step future under
(1) no action and (2) the same optimistic 9-action/two-channel greedy oracle.
Primary test: does frozen canonical EBID improve prediction of relative control
benefit beyond endpoint geometry when an entire dynamical class is unseen?
"""
from __future__ import annotations
import csv,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from pcc_ebid_regulator.control_benefit import greedy_control_benefit
from pcc_ebid_regulator.dynamics import step as pcc_step
from pcc_ebid_regulator.benchmark import benchmark_step
from pcc_ebid_regulator.oscillatory_benchmark import oscillatory_step
from pcc_ebid_regulator.panel_benchmarks import damped_oscillatory_step, neutral_step

SRC=ROOT/'results'/'022_raw_path_invariants';OUT=ROOT/'results'/'025_direct_control_benefit';OUT.mkdir(parents=True,exist_ok=True)
SYSTEMS=['pcc','oscillatory_benchmark','damped_oscillator','directional_benchmark','neutral_diffusion']
RATIOS=[0.60,1.00];FAMILIES=range(4);HORIZON=40;ALPHA=10.0;DAMPING_CYCLES=0.75
EBID_KEYS=['ebid_initial_entropy','ebid_mean_entropy','ebid_end_entropy','ebid_entropy_drop','ebid_entropy_slope','ebid_mean_entropy_rate','ebid_min_entropy_rate','ebid_entropy_rate_variance','ebid_deficit_growth','ebid_max_deficit_rate','ebid_deficit_rate_variance']
BASE_KEYS=['target_cycle_ratio','P','C','strength','quad_initial','quad_mean','quad_end','quad_growth','quad_slope','quad_mean_rate','quad_min_rate','quad_max_rate','quad_rate_variance','activity_initial','activity_mean','activity_end','activity_max','activity_slope']
TARGET='control_relative_benefit'

STATIC_ENTROPY_KEYS=['ebid_initial_entropy','ebid_mean_entropy','ebid_end_entropy']
RATE_EBID_KEYS=[k for k in EBID_KEYS if k not in STATIC_ENTROPY_KEYS]

def custom_ridge(train,test,keys):
    X=np.column_stack([col(train,k) for k in keys]); Z=np.column_stack([col(test,k) for k in keys]); y=col(train,TARGET)
    mu=X.mean(0);sd=X.std(0);sd[sd<1e-10]=1;X=(X-mu)/sd;Z=(Z-mu)/sd
    Xa=np.column_stack([np.ones(len(X)),X]);Za=np.column_stack([np.ones(len(Z)),Z]);pen=np.eye(Xa.shape[1]);pen[0,0]=0
    b=np.linalg.solve(Xa.T@Xa+ALPHA*pen,Xa.T@y);return Za@b

def ablation(rows):
    out=[]
    for held in SYSTEMS+['ALL']:
        holds=SYSTEMS if held=='ALL' else [held]; ys=[];pbase=[];pstatic=[];pfull=[]
        for h in holds:
            tr=[r for r in rows if r['system']!=h];te=[r for r in rows if r['system']==h];ys.extend(col(te,TARGET))
            pbase.extend(custom_ridge(tr,te,BASE_KEYS));pstatic.extend(custom_ridge(tr,te,BASE_KEYS+STATIC_ENTROPY_KEYS));pfull.extend(custom_ridge(tr,te,BASE_KEYS+STATIC_ENTROPY_KEYS+RATE_EBID_KEYS))
        y=np.asarray(ys);m0=mae(y,pbase);m1=mae(y,pstatic);m2=mae(y,pfull)
        out.append({'heldout_system':held,'baseline_mae':m0,'plus_entropy_levels_mae':m1,'plus_full_ebid_mae':m2,'entropy_level_gain':(m0-m1)/m0,'rate_increment_beyond_levels':(m1-m2)/m1,'full_ebid_gain':(m0-m2)/m0})
    return out


def read_csv(p):
    with Path(p).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def write_csv(p,rows):
    if not rows:return
    with Path(p).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def col(rows,k):return np.asarray([float(r[k]) for r in rows],float)

def transition_for(row):
    system=row['system'];strength=float(row['strength']);regime=row['structure'];period=float(row['pcc_reference_cycle_period']);offset=int(row['observation_steps'])
    if system=='pcc': return lambda x,h:pcc_step(x,strength=strength,topology=regime)
    if system=='oscillatory_benchmark': return lambda x,h:oscillatory_step(x,t=offset+h,period=period,strength=strength,regime=regime)
    if system=='damped_oscillator': return lambda x,h:damped_oscillatory_step(x,t=offset+h,period=period,strength=strength,regime=regime,damping_cycles=DAMPING_CYCLES)
    if system=='directional_benchmark': return lambda x,h:benchmark_step(x,strength=strength,regime=regime)
    return lambda x,h:neutral_step(x,regime=regime)

def build_dataset():
    out=[]
    for system in SYSTEMS:
      for fi in FAMILIES:
       for ratio in RATIOS:
        rows=read_csv(SRC/f'dataset_{system}_f{fi}_r{ratio:.2f}.csv')
        for r in rows:
            initial=np.array([float(r['P']),float(r['C']),float(r['Ch'])])
            cb=greedy_control_benefit(initial,transition_for(r),horizon=HORIZON,cardinality=9,max_action=0.06,channels=(0,1))
            out.append({**r,**cb})
    write_csv(OUT/'dataset.csv',out);return out

def dm(rows,include_ebid,known_classes=False):
    cols=[col(rows,k) for k in BASE_KEYS]
    if known_classes: cols += [np.asarray([1.0 if r['system']==s else 0.0 for r in rows]) for s in SYSTEMS[:-1]]
    if include_ebid: cols += [col(rows,k) for k in EBID_KEYS]
    return np.column_stack(cols)
def ridge(train,test,include_ebid,known_classes=False):
    X=dm(train,include_ebid,known_classes);Z=dm(test,include_ebid,known_classes);y=col(train,TARGET)
    mu=X.mean(0);sd=X.std(0);sd[sd<1e-10]=1;X=(X-mu)/sd;Z=(Z-mu)/sd
    Xa=np.column_stack([np.ones(len(X)),X]);Za=np.column_stack([np.ones(len(Z)),Z]);pen=np.eye(Xa.shape[1]);pen[0,0]=0
    b=np.linalg.solve(Xa.T@Xa+ALPHA*pen,Xa.T@y);return Za@b
def mae(y,p):return float(np.mean(np.abs(np.asarray(y)-np.asarray(p))))
def r2(y,p):
    y=np.asarray(y,float);p=np.asarray(p,float);d=np.sum((y-y.mean())**2);return float(1-np.sum((y-p)**2)/d) if d>1e-12 else float('nan')

def class_cv(rows):
    preds=[];summ=[]
    for held in SYSTEMS:
        tr=[r for r in rows if r['system']!=held];te=[r for r in rows if r['system']==held];y=col(te,TARGET);p0=ridge(tr,te,False);p1=ridge(tr,te,True);b=mae(y,p0);e=mae(y,p1)
        summ.append({'heldout_system':held,'n_test':len(te),'geometry_mae':b,'geometry_ebid_mae':e,'ebid_relative_mae_reduction':(b-e)/b,'geometry_r2':r2(y,p0),'geometry_ebid_r2':r2(y,p1),'mean_control_benefit':float(np.mean(y))})
        for r,a,z in zip(te,p0,p1):preds.append({'heldout_system':held,'seed_family':r['seed_family'],'target_cycle_ratio':r['target_cycle_ratio'],'actual_control_benefit':r[TARGET],'geometry_prediction':float(a),'geometry_ebid_prediction':float(z)})
    y=col(preds,'actual_control_benefit');p0=col(preds,'geometry_prediction');p1=col(preds,'geometry_ebid_prediction');b=mae(y,p0);e=mae(y,p1)
    summ.append({'heldout_system':'ALL','n_test':len(preds),'geometry_mae':b,'geometry_ebid_mae':e,'ebid_relative_mae_reduction':(b-e)/b,'geometry_r2':r2(y,p0),'geometry_ebid_r2':r2(y,p1),'mean_control_benefit':float(np.mean(y))})
    return preds,summ

def family_cv(rows):
    preds=[]
    for held in FAMILIES:
        tr=[r for r in rows if int(r['seed_family'])!=held];te=[r for r in rows if int(r['seed_family'])==held];y=col(te,TARGET);p0=ridge(tr,te,False,True);p1=ridge(tr,te,True,True)
        for r,a,z in zip(te,p0,p1):preds.append({'heldout_family':held,'system':r['system'],'target_cycle_ratio':r['target_cycle_ratio'],'actual_control_benefit':r[TARGET],'class_geometry_prediction':float(a),'class_geometry_ebid_prediction':float(z)})
    y=col(preds,'actual_control_benefit');p0=col(preds,'class_geometry_prediction');p1=col(preds,'class_geometry_ebid_prediction');b=mae(y,p0);e=mae(y,p1)
    return preds,[{'protocol':'leave_one_family_out_known_classes','n_test':len(preds),'class_geometry_mae':b,'class_geometry_ebid_mae':e,'ebid_relative_mae_reduction':(b-e)/b,'class_geometry_r2':r2(y,p0),'class_geometry_ebid_r2':r2(y,p1)}]

def direct_correlations(rows):
    y=col(rows,TARGET);out=[]
    for k in EBID_KEYS:
        x=col(rows,k);rr=float(np.corrcoef(x,y)[0,1]) if np.std(x)>1e-12 else 0.0;out.append({'ebid_feature':k,'pearson_r_with_control_benefit':rr})
    return sorted(out,key=lambda z:abs(z['pearson_r_with_control_benefit']),reverse=True)

def main():
    rows=build_dataset();write_csv(OUT/'ebid_control_benefit_correlations.csv',direct_correlations(rows));write_csv(OUT/'ablation.csv',ablation(rows));cp,cs=class_cv(rows);write_csv(OUT/'class_cv_predictions.csv',cp);write_csv(OUT/'class_cv_summary.csv',cs);fp,fs=family_cv(rows);write_csv(OUT/'family_cv_predictions.csv',fp);write_csv(OUT/'family_cv_summary.csv',fs)
    print('EXPERIMENT 025: DIRECT EBID -> CONTROL BENEFIT')
    for r in cs:print(f"{r['heldout_system']:<24} EBID MAE change={100*float(r['ebid_relative_mae_reduction']):+7.1f}% R2={float(r['geometry_ebid_r2']):+.3f} meanBenefit={float(r['mean_control_benefit']):.3f}")
    print('Known-class family CV:',fs[0])
if __name__=='__main__':main()
