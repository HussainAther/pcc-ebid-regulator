"""Experiment 021: continuous trajectory-statistics panel.

Replace dynamical-class labels with continuous, pre-specified non-EBID trajectory
summaries from the frozen Experiments 016-020 datasets. The target is the held-out
family-level incremental MAE reduction from adding canonical EBID.

Important: EBID entropy features are NOT used as explanatory descriptors here.
"""
from __future__ import annotations
import csv, math, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'src'))
OUT=ROOT/'results'/'021_trajectory_statistics'; OUT.mkdir(parents=True,exist_ok=True)
RATIOS=[0.60,1.00]; FAMILIES=list(range(8)); ALPHA=1.0; SEED=20260921

DATASETS={
 'pcc': ROOT/'results'/'016_cross_seed_scale_map'/'dataset.csv',
 'oscillatory_benchmark': ROOT/'results'/'019_oscillatory_specificity'/'dataset.csv',
 'directional_benchmark': ROOT/'results'/'018_nonpcc_specificity'/'dataset.csv',
 'damped_oscillator': ROOT/'results'/'020_dynamical_class_panel'/'dataset_damped_oscillator.csv',
 'neutral_diffusion': ROOT/'results'/'020_dynamical_class_panel'/'dataset_neutral_diffusion.csv',
}
GAINS=ROOT/'results'/'020_dynamical_class_panel'/'panel_fold_gains.csv'

# Frozen non-EBID trajectory descriptors. All are computed before the future horizon.
DESC=[
 'endpoint_imbalance_mean','endpoint_imbalance_sd',
 'activity_mean','activity_max','abs_activity_slope',
 'radial_level','radial_drift','radial_excursion','radial_rate_variance',
 'phase_dispersion',
]

def read_csv(path):
    with Path(path).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def write_csv(path,rows):
    if not rows:return
    with Path(path).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def arr(rows,k):return np.asarray([float(r[k]) for r in rows],float)
def mean(rows,k):return float(np.mean(arr(rows,k)))
def sd(rows,k):return float(np.std(arr(rows,k),ddof=0))

def phase_dispersion(rows):
    p=arr(rows,'phase'); z=np.mean(np.exp(1j*p)); return float(1.0-abs(z))

def summarize_test_rows(rows):
    qg=arr(rows,'quad_growth')
    return {
      'endpoint_imbalance_mean':mean(rows,'imbalance'),
      'endpoint_imbalance_sd':sd(rows,'imbalance'),
      'activity_mean':mean(rows,'activity_mean'),
      'activity_max':mean(rows,'activity_max'),
      'abs_activity_slope':float(np.mean(np.abs(arr(rows,'activity_slope')))),
      'radial_level':mean(rows,'quad_mean'),
      'radial_drift':float(np.mean(qg)),
      'radial_excursion':float(np.mean(np.abs(qg))),
      'radial_rate_variance':mean(rows,'quad_rate_variance'),
      'phase_dispersion':phase_dispersion(rows),
    }

def gain_map():
    out={}
    for r in read_csv(GAINS):
        sysn=r['system']; ratio=float(r['target_cycle_ratio']); fam=int(float(r['heldout_family']))
        if ratio in RATIOS:out[(sysn,ratio,fam)]=float(r['relative_mae_reduction'])
    return out

def build_panel():
    gm=gain_map(); panel=[]
    for system,path in DATASETS.items():
      rows=read_csv(path)
      for ratio in RATIOS:
        for fam in FAMILIES:
          # Match the held-out evaluation population: structure 0, unseen noise, held-out family.
          test=[r for r in rows if abs(float(r['target_cycle_ratio'])-ratio)<1e-12 and int(float(r['seed_family']))==fam and int(float(r['structure_index']))==0 and float(r['noise_sigma']) in (0.01,0.02)]
          if len(test)!=16: raise RuntimeError(f'{system} ratio={ratio} family={fam}: expected 16 test rows, got {len(test)}')
          key=(system,ratio,fam)
          if key not in gm: raise KeyError(key)
          panel.append({'system':system,'target_cycle_ratio':ratio,'heldout_family':fam,'ebid_gain':gm[key],**summarize_test_rows(test)})
    return panel

def rankdata(x):
    x=np.asarray(x,float); order=np.argsort(x,kind='mergesort'); ranks=np.empty(len(x),float); i=0
    while i<len(x):
      j=i+1
      while j<len(x) and x[order[j]]==x[order[i]]:j+=1
      ranks[order[i:j]]=(i+j-1)/2+1; i=j
    return ranks

def corr(x,y):
    x=np.asarray(x,float);y=np.asarray(y,float)
    if np.std(x)<1e-12 or np.std(y)<1e-12:return 0.0
    return float(np.corrcoef(x,y)[0,1])
def correlations(panel):
    y=arr(panel,'ebid_gain'); out=[]
    for d in DESC:
      x=arr(panel,d); out.append({'descriptor':d,'pearson_r':corr(x,y),'spearman_rho':corr(rankdata(x),rankdata(y))})
    return sorted(out,key=lambda r:abs(float(r['spearman_rho'])),reverse=True)

SYSTEMS=list(DATASETS)
def design(rows,include_desc=True,include_class=False):
    ratio=arr(rows,'target_cycle_ratio'); cols=[ratio]
    if include_class:
      # Drop the final class as the reference category.
      cols += [np.asarray([1.0 if r['system']==sysn else 0.0 for r in rows]) for sysn in SYSTEMS[:-1]]
    if include_desc:cols += [arr(rows,d) for d in DESC]
    return np.column_stack(cols)
def fit_predict(train,test,include_desc=True,include_class=False):
    X=design(train,include_desc,include_class);Z=design(test,include_desc,include_class);y=arr(train,'ebid_gain');mu=X.mean(0);sd=X.std(0);sd[sd<1e-10]=1;X=(X-mu)/sd;Z=(Z-mu)/sd
    Xa=np.column_stack([np.ones(len(X)),X]);Za=np.column_stack([np.ones(len(Z)),Z]);pen=np.eye(Xa.shape[1]);pen[0,0]=0
    beta=np.linalg.solve(Xa.T@Xa+ALPHA*pen,Xa.T@y);return Za@beta

def mae(y,p):return float(np.mean(np.abs(np.asarray(y)-np.asarray(p))))
def r2(y,p):
    y=np.asarray(y,float);p=np.asarray(p,float);den=np.sum((y-y.mean())**2);return float(1-np.sum((y-p)**2)/den) if den>1e-12 else float('nan')

def family_cv(panel):
    preds=[]
    for fam in FAMILIES:
      tr=[r for r in panel if int(r['heldout_family'])!=fam];te=[r for r in panel if int(r['heldout_family'])==fam]
      p0=fit_predict(tr,te,False,False);p1=fit_predict(tr,te,True,False);pc=fit_predict(tr,te,False,True);pcd=fit_predict(tr,te,True,True)
      for r,a,b,c,d in zip(te,p0,p1,pc,pcd):preds.append({'heldout_family':fam,'system':r['system'],'target_cycle_ratio':r['target_cycle_ratio'],'ebid_gain':r['ebid_gain'],'ratio_only_prediction':float(a),'descriptor_prediction':float(b),'class_ratio_prediction':float(c),'class_descriptor_prediction':float(d)})
    y=arr(preds,'ebid_gain');p0=arr(preds,'ratio_only_prediction');p1=arr(preds,'descriptor_prediction');pc=arr(preds,'class_ratio_prediction');pcd=arr(preds,'class_descriptor_prediction')
    b0=mae(y,p0);bd=mae(y,p1);bc=mae(y,pc);bcd=mae(y,pcd)
    return preds,[{'protocol':'leave_one_family_out','n':len(preds),'ratio_only_mae':b0,'descriptor_mae':bd,'descriptor_vs_ratio_reduction':(b0-bd)/b0,'class_ratio_mae':bc,'class_descriptor_mae':bcd,'descriptor_beyond_class_reduction':(bc-bcd)/bc,'ratio_only_r2':r2(y,p0),'descriptor_r2':r2(y,p1),'class_ratio_r2':r2(y,pc),'class_descriptor_r2':r2(y,pcd)}]

def class_cv(panel):
    preds=[]
    for system in DATASETS:
      tr=[r for r in panel if r['system']!=system];te=[r for r in panel if r['system']==system]
      p0=fit_predict(tr,te,False);p1=fit_predict(tr,te,True)
      for r,a,b in zip(te,p0,p1):preds.append({'heldout_system':system,'heldout_family':r['heldout_family'],'target_cycle_ratio':r['target_cycle_ratio'],'ebid_gain':r['ebid_gain'],'ratio_only_prediction':float(a),'descriptor_prediction':float(b)})
    out=[]
    for system in DATASETS:
      ss=[r for r in preds if r['heldout_system']==system];y=arr(ss,'ebid_gain');p0=arr(ss,'ratio_only_prediction');p1=arr(ss,'descriptor_prediction');b=mae(y,p0);e=mae(y,p1)
      out.append({'heldout_system':system,'n':len(ss),'ratio_only_mae':b,'descriptor_mae':e,'relative_mae_reduction':(b-e)/b,'descriptor_r2':r2(y,p1)})
    y=arr(preds,'ebid_gain');p0=arr(preds,'ratio_only_prediction');p1=arr(preds,'descriptor_prediction');b=mae(y,p0);e=mae(y,p1)
    out.append({'heldout_system':'ALL','n':len(preds),'ratio_only_mae':b,'descriptor_mae':e,'relative_mae_reduction':(b-e)/b,'descriptor_r2':r2(y,p1)})
    return preds,out

def coefficients(panel):
    X=design(panel,True);y=arr(panel,'ebid_gain');mu=X.mean(0);sd=X.std(0);sd[sd<1e-10]=1;Xs=(X-mu)/sd;Xa=np.column_stack([np.ones(len(Xs)),Xs]);pen=np.eye(Xa.shape[1]);pen[0,0]=0;beta=np.linalg.solve(Xa.T@Xa+ALPHA*pen,Xa.T@y)
    names=['target_cycle_ratio']+DESC
    return sorted([{'feature':n,'standardized_coefficient':float(b)} for n,b in zip(names,beta[1:])],key=lambda r:abs(float(r['standardized_coefficient'])),reverse=True)

def bootstrap_corr(panel,d,n=5000):
    rng=np.random.default_rng(SEED+sum(map(ord,d))); vals=[]
    # cluster bootstrap by family to respect shared seed-family structure across classes
    for _ in range(n):
      fs=rng.integers(0,8,8);sample=[]
      for f in fs: sample += [r for r in panel if int(r['heldout_family'])==int(f)]
      vals.append(corr(rankdata(arr(sample,d)),rankdata(arr(sample,'ebid_gain'))))
    return tuple(map(float,np.quantile(vals,[.025,.975])))

def main():
    panel=build_panel();write_csv(OUT/'fold_trajectory_statistics.csv',panel)
    cor=correlations(panel)
    for r in cor:r['spearman_ci_low'],r['spearman_ci_high']=bootstrap_corr(panel,r['descriptor'])
    write_csv(OUT/'correlations.csv',cor)
    fp,fs=family_cv(panel);write_csv(OUT/'family_cv_predictions.csv',fp);write_csv(OUT/'family_cv_summary.csv',fs)
    cp,cs=class_cv(panel);write_csv(OUT/'class_cv_predictions.csv',cp);write_csv(OUT/'class_cv_summary.csv',cs)
    coef=coefficients(panel);write_csv(OUT/'ridge_coefficients.csv',coef)
    print('Top rank correlations with EBID gain:')
    for r in cor[:5]:print(f"  {r['descriptor']:<26} rho={float(r['spearman_rho']):+.3f} CI=[{float(r['spearman_ci_low']):+.3f},{float(r['spearman_ci_high']):+.3f}]")
    s=fs[0];print(f"Family-held-out: descriptors change MAE by {100*float(s['descriptor_vs_ratio_reduction']):+.1f}% vs ratio-only; R2={float(s['descriptor_r2']):+.3f}")
    print(f"Beyond class+scale: descriptors change MAE by {100*float(s['descriptor_beyond_class_reduction']):+.1f}%; class+desc R2={float(s['class_descriptor_r2']):+.3f}")
    a=[r for r in cs if r['heldout_system']=='ALL'][0];print(f"Class-held-out: descriptors change MAE by {100*float(a['relative_mae_reduction']):+.1f}% vs ratio-only; R2={float(a['descriptor_r2']):+.3f}")
if __name__=='__main__':main()
