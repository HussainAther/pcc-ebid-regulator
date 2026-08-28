"""Experiment 022: prospective raw-path invariants panel.

Regenerate all five dynamical classes prospectively while retaining every raw
observation trajectory. Frozen canonical EBID is evaluated with the same
leave-one-family-out regulator-demand protocol. The primary synthesis test then
holds out an entire dynamical class and asks whether mechanism-agnostic raw-path
invariants predict EBID's incremental MAE gain in that unseen class.

No Shannon-entropy / EBID quantity appears among the explanatory raw-path
invariants.
"""
from __future__ import annotations
import argparse, csv, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from pcc_ebid_regulator.benchmark import benchmark_step
from pcc_ebid_regulator.dynamics import step as pcc_step
from pcc_ebid_regulator.ebid import canonical_ebid_features,quadratic_rate_features
from pcc_ebid_regulator.metrics import regulation_error
from pcc_ebid_regulator.oscillatory_benchmark import REGIMES as OSC_REGIMES,oscillatory_step,oscillatory_activity
from pcc_ebid_regulator.panel_benchmarks import DAMPED_REGIMES,NEUTRAL_REGIMES,damped_oscillatory_step,damped_activity,neutral_step,neutral_activity
from pcc_ebid_regulator.raw_path import raw_path_features
from pcc_ebid_regulator.regulators import apply_multichannel_action,matched_directional_repertoire
from pcc_ebid_regulator.signals import benchmark_activity,pcc_interaction_activity,simplex_phase
from pcc_ebid_regulator.stochastic import perturb_simplex
from pcc_ebid_regulator.topology import TOPOLOGIES

OUT=ROOT/'results'/'022_raw_path_invariants';OUT.mkdir(parents=True,exist_ok=True)
PERIOD_SOURCE=ROOT/'results'/'015_transition_band'/'reference_periods.csv'
SYSTEMS=['pcc','oscillatory_benchmark','damped_oscillator','directional_benchmark','neutral_diffusion']
REGIMES={
'pcc':list(TOPOLOGIES),
'oscillatory_benchmark':list(OSC_REGIMES),
'damped_oscillator':list(DAMPED_REGIMES),
'directional_benchmark':['pressure_bias','control_bias','chaos_bias','mixed_bias'],
'neutral_diffusion':list(NEUTRAL_REGIMES),
}
RATIOS=[0.60,1.00];STRENGTHS=[1.0,2.0,3.0];TRAIN_NOISE=[0.0,0.002,0.005];TEST_NOISE=[0.01,0.02]
FAMILY_SEEDS=[20270301,20270319,20270407,20270423];REPLICATES=1;HORIZON=40;K=9;MAX_ACTION=0.12;RIDGE_ALPHA=0.10;META_ALPHA=1.0;DAMPING_CYCLES=0.75;SEED=20260922
TARGET=np.ones(3)/3
EBID_KEYS=['ebid_initial_entropy','ebid_mean_entropy','ebid_end_entropy','ebid_entropy_drop','ebid_entropy_slope','ebid_mean_entropy_rate','ebid_min_entropy_rate','ebid_entropy_rate_variance','ebid_deficit_growth','ebid_max_deficit_rate','ebid_deficit_rate_variance']
QUAD_KEYS=['quad_initial','quad_mean','quad_end','quad_growth','quad_slope','quad_mean_rate','quad_min_rate','quad_max_rate','quad_rate_variance']
ACTIVITY_KEYS=['activity_initial','activity_mean','activity_end','activity_max','activity_slope']
RAW_KEYS=['raw_path_length','raw_net_displacement','raw_path_efficiency','raw_recurrence_rate','raw_lag1_autocorrelation','raw_spectral_concentration','raw_turning_persistence','raw_occupancy_fraction']

def read_csv(path):
    with Path(path).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def write_csv(path,rows):
    if not rows:return
    with Path(path).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def period_map():return {float(r['strength']):float(r['median_cycle_period']) for r in read_csv(PERIOD_SOURCE)}
def slope(a):
    a=np.asarray(a,float);return float(np.polyfit(np.arange(len(a)),a,1)[0]) if len(a)>1 else 0.0
def activity_features(v):
    a=np.asarray(v,float);return {'activity_initial':float(a[0]),'activity_mean':float(a.mean()),'activity_end':float(a[-1]),'activity_max':float(a.max()),'activity_slope':slope(a)}
def deterministic_step(system,x,t,period,strength,regime):
    if system=='pcc':return pcc_step(x,strength=strength,topology=regime)
    if system=='oscillatory_benchmark':return oscillatory_step(x,t=t,period=period,strength=strength,regime=regime)
    if system=='damped_oscillator':return damped_oscillatory_step(x,t=t,period=period,strength=strength,regime=regime,damping_cycles=DAMPING_CYCLES)
    if system=='directional_benchmark':return benchmark_step(x,strength=strength,regime=regime)
    return neutral_step(x,regime=regime)
def activity(system,x,t,period,strength,regime):
    if system=='pcc':return pcc_interaction_activity(x,strength=strength,topology=regime)
    if system=='oscillatory_benchmark':return oscillatory_activity(x,t=t,period=period,strength=strength,regime=regime)
    if system=='damped_oscillator':return damped_activity(x,t=t,period=period,strength=strength,regime=regime,damping_cycles=DAMPING_CYCLES)
    if system=='directional_benchmark':return benchmark_activity(x,strength=strength,regime=regime)
    return neutral_activity(x,regime=regime)
def stoch_step(system,x,t,period,strength,regime,sigma,rng):return perturb_simplex(deterministic_step(system,x,t,period,strength,regime),sigma,rng)
def observe(system,initial,period,strength,regime,sigma,rng,n):
    x=initial.copy();traj=[x.copy()];acts=[]
    for t in range(n+1):
        acts.append(activity(system,x,t,period,strength,regime))
        if t<n:x=stoch_step(system,x,t,period,strength,regime,sigma,rng);traj.append(x.copy())
    return x,np.asarray(traj),activity_features(acts)
def choose_action(system,x,t,period,strength,regime,actions):
    best=actions[0];be=float('inf')
    for u in actions:
        z=apply_multichannel_action(x,u);z=deterministic_step(system,z,t,period,strength,regime);e=regulation_error(z,TARGET)
        if e<be:be=e;best=u
    return best
def future_error(system,state,start_t,period,strength,regime,sigma,seed):
    rng=np.random.default_rng(seed);actions=matched_directional_repertoire((1,),cardinality=K,max_action=MAX_ACTION);x=state.copy();errs=[]
    for j in range(HORIZON):
        t=start_t+j;u=choose_action(system,x,t,period,strength,regime,actions);x=apply_multichannel_action(x,u);x=stoch_step(system,x,t,period,strength,regime,sigma,rng);errs.append(regulation_error(x,TARGET))
    return float(np.mean(errs))
def chunk_seed(system,fi,ratio):return int(FAMILY_SEEDS[fi]+round(10000*ratio)+100000*SYSTEMS.index(system)+220000)
def build_chunk(system,fi,ratio,pmap):
    master=np.random.default_rng(chunk_seed(system,fi,ratio));rows=[];paths={};sample=0
    for si,regime in enumerate(REGIMES[system]):
      for strength in STRENGTHS:
        period=pmap[strength];obs=max(5,int(round(period*ratio)))
        for sigma in TRAIN_NOISE+TEST_NOISE:
          for rep in range(REPLICATES):
            initial=master.dirichlet(np.array([1.4,1.4,1.4]));os=int(master.integers(0,2**31-1));fs=int(master.integers(0,2**31-1))
            end,traj,act=observe(system,initial,period,strength,regime,sigma,np.random.default_rng(os),obs);key=f's{sample:04d}';paths[key]=traj.astype(np.float32)
            rows.append({'system':system,'seed_family':fi,'family_seed':FAMILY_SEEDS[fi],'sample':sample,'raw_path_key':key,'structure_index':si,'structure':regime,'strength':strength,'noise_sigma':sigma,'replicate':rep,'target_cycle_ratio':ratio,'observation_steps':obs,'pcc_reference_cycle_period':period,'P':float(end[0]),'C':float(end[1]),'Ch':float(end[2]),'imbalance':regulation_error(end,TARGET),'phase':simplex_phase(end),**act,**quadratic_rate_features(traj),**canonical_ebid_features(traj),**raw_path_features(traj),'future_error':future_error(system,end,obs,period,strength,regime,sigma,fs)});sample+=1
    return rows,paths
def col(rows,k):return np.asarray([float(r[k]) for r in rows],float)
def raw_design(rows,include_ebid):
    P,C,S=col(rows,'P'),col(rows,'C'),col(rows,'strength');ph=col(rows,'phase');cols=[P,C,S,P*P,C*C,S*S,P*C,P*S,C*S,*[col(rows,k) for k in ACTIVITY_KEYS],np.sin(ph),np.cos(ph),*[col(rows,k) for k in QUAD_KEYS]]
    if include_ebid:cols += [col(rows,k) for k in EBID_KEYS]
    return np.column_stack(cols)
def ridge_predict(train,test,include_ebid):
    X=raw_design(train,include_ebid);Z=raw_design(test,include_ebid);y=col(train,'future_error');mu=X.mean(0);sd=X.std(0);sd[sd<1e-10]=1;X=(X-mu)/sd;Z=(Z-mu)/sd;Xa=np.column_stack([np.ones(len(X)),X]);Za=np.column_stack([np.ones(len(Z)),Z]);pen=np.eye(Xa.shape[1]);pen[0,0]=0;beta=np.linalg.solve(Xa.T@Xa+RIDGE_ALPHA*pen,Xa.T@y);return Za@beta
def split(rows,ratio,held):
    rr=[r for r in rows if abs(float(r['target_cycle_ratio'])-ratio)<1e-12];tr=[r for r in rr if int(r['seed_family'])!=held and int(r['structure_index'])!=0 and float(r['noise_sigma']) in TRAIN_NOISE];te=[r for r in rr if int(r['seed_family'])==held and int(r['structure_index'])==0 and float(r['noise_sigma']) in TEST_NOISE];return tr,te
def evaluate_system(system,rows):
    out=[]
    for ratio in RATIOS:
      for fi in range(len(FAMILY_SEEDS)):
        tr,te=split(rows,ratio,fi);y=col(te,'future_error');p0=ridge_predict(tr,te,False);p1=ridge_predict(tr,te,True);b=float(np.mean(np.abs(y-p0)));e=float(np.mean(np.abs(y-p1)));g=(b-e)/b
        rec={'system':system,'target_cycle_ratio':ratio,'heldout_family':fi,'n_train':len(tr),'n_test':len(te),'base_mae':b,'ebid_mae':e,'relative_mae_reduction':g}
        for k in RAW_KEYS:
            a=col(te,k);rec[k+'_mean']=float(a.mean());rec[k+'_sd']=float(a.std())
        out.append(rec)
    return out
META_KEYS=[k+s for k in RAW_KEYS for s in ('_mean','_sd')]
def meta_design(rows,include_raw):
    cols=[col(rows,'target_cycle_ratio')]
    if include_raw:cols += [col(rows,k) for k in META_KEYS]
    return np.column_stack(cols)
def meta_predict(train,test,include_raw):
    X=meta_design(train,include_raw);Z=meta_design(test,include_raw);y=col(train,'relative_mae_reduction');mu=X.mean(0);sd=X.std(0);sd[sd<1e-10]=1;X=(X-mu)/sd;Z=(Z-mu)/sd;Xa=np.column_stack([np.ones(len(X)),X]);Za=np.column_stack([np.ones(len(Z)),Z]);pen=np.eye(Xa.shape[1]);pen[0,0]=0;beta=np.linalg.solve(Xa.T@Xa+META_ALPHA*pen,Xa.T@y);return Za@beta
def mae(y,p):return float(np.mean(np.abs(np.asarray(y)-np.asarray(p))))
def r2(y,p):
    y=np.asarray(y,float);p=np.asarray(p,float);d=np.sum((y-y.mean())**2);return float(1-np.sum((y-p)**2)/d) if d>1e-12 else float('nan')
def class_cv(folds):
    preds=[];summary=[]
    for held in SYSTEMS:
        tr=[r for r in folds if r['system']!=held];te=[r for r in folds if r['system']==held];y=col(te,'relative_mae_reduction');p0=meta_predict(tr,te,False);p1=meta_predict(tr,te,True);b=mae(y,p0);e=mae(y,p1)
        summary.append({'heldout_system':held,'n_test':len(te),'scale_only_mae':b,'raw_descriptor_mae':e,'relative_mae_reduction':(b-e)/b,'raw_descriptor_r2':r2(y,p1)})
        for r,a,z in zip(te,p0,p1):preds.append({'heldout_system':held,'target_cycle_ratio':r['target_cycle_ratio'],'heldout_family':r['heldout_family'],'ebid_gain':r['relative_mae_reduction'],'scale_only_prediction':float(a),'raw_descriptor_prediction':float(z)})
    y=col(preds,'ebid_gain');p0=col(preds,'scale_only_prediction');p1=col(preds,'raw_descriptor_prediction');b=mae(y,p0);e=mae(y,p1);summary.append({'heldout_system':'ALL','n_test':len(preds),'scale_only_mae':b,'raw_descriptor_mae':e,'relative_mae_reduction':(b-e)/b,'raw_descriptor_r2':r2(y,p1)})
    return preds,summary

def meta_design_family(rows,include_raw):
    ratio=col(rows,'target_cycle_ratio');cols=[ratio]
    # Class identity is available in this secondary within-represented-class test.
    cols += [np.asarray([1.0 if r['system']==sysn else 0.0 for r in rows],float) for sysn in SYSTEMS[:-1]]
    if include_raw:cols += [col(rows,k) for k in META_KEYS]
    return np.column_stack(cols)
def meta_predict_family(train,test,include_raw):
    X=meta_design_family(train,include_raw);Z=meta_design_family(test,include_raw);y=col(train,'relative_mae_reduction');mu=X.mean(0);sd=X.std(0);sd[sd<1e-10]=1;X=(X-mu)/sd;Z=(Z-mu)/sd;Xa=np.column_stack([np.ones(len(X)),X]);Za=np.column_stack([np.ones(len(Z)),Z]);pen=np.eye(Xa.shape[1]);pen[0,0]=0;beta=np.linalg.solve(Xa.T@Xa+META_ALPHA*pen,Xa.T@y);return Za@beta
def family_cv_secondary(folds):
    preds=[]
    for fam in range(len(FAMILY_SEEDS)):
        tr=[r for r in folds if int(r['heldout_family'])!=fam];te=[r for r in folds if int(r['heldout_family'])==fam];y=col(te,'relative_mae_reduction');p0=meta_predict_family(tr,te,False);p1=meta_predict_family(tr,te,True)
        for r,a,z in zip(te,p0,p1):preds.append({'heldout_family':fam,'system':r['system'],'target_cycle_ratio':r['target_cycle_ratio'],'ebid_gain':r['relative_mae_reduction'],'class_scale_prediction':float(a),'class_scale_raw_prediction':float(z)})
    y=col(preds,'ebid_gain');p0=col(preds,'class_scale_prediction');p1=col(preds,'class_scale_raw_prediction');b=mae(y,p0);e=mae(y,p1)
    return preds,[{'protocol':'leave_one_family_out_known_classes','n':len(preds),'class_scale_mae':b,'class_scale_raw_mae':e,'relative_mae_reduction':(b-e)/b,'class_scale_r2':r2(y,p0),'class_scale_raw_r2':r2(y,p1)}]

def correlations(folds):
    y=col(folds,'relative_mae_reduction');out=[]
    for k in META_KEYS:
        x=col(folds,k)
        r=float(np.corrcoef(x,y)[0,1]) if np.std(x)>1e-12 else 0.0
        out.append({'descriptor':k,'pearson_r':r})
    return sorted(out,key=lambda z:abs(z['pearson_r']),reverse=True)
def aggregate_only():
    all_rows=[];folds=[]
    for system in SYSTEMS:
      rows=[]
      for fi in range(len(FAMILY_SEEDS)):
        for ratio in RATIOS:rows+=read_csv(OUT/f'dataset_{system}_f{fi}_r{ratio:.2f}.csv')
      write_csv(OUT/f'dataset_{system}.csv',rows);all_rows+=rows;folds+=evaluate_system(system,rows)
    write_csv(OUT/'prospective_dataset.csv',all_rows);write_csv(OUT/'fold_gains_and_raw_descriptors.csv',folds);write_csv(OUT/'raw_descriptor_correlations.csv',correlations(folds));preds,summ=class_cv(folds);write_csv(OUT/'class_cv_predictions.csv',preds);write_csv(OUT/'class_cv_summary.csv',summ);fp,fs=family_cv_secondary(folds);write_csv(OUT/'family_cv_predictions.csv',fp);write_csv(OUT/'family_cv_summary.csv',fs)
    print('LEAVE-ONE-DYNAMICAL-CLASS-OUT RAW-PATH TEST')
    for r in summ:print(f"{r['heldout_system']:<24} raw-vs-scale MAE change={100*float(r['relative_mae_reduction']):+6.1f}% R2={float(r['raw_descriptor_r2']):+.3f}")
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--system',choices=SYSTEMS);ap.add_argument('--family',type=int);ap.add_argument('--ratio',type=float);ap.add_argument('--aggregate-only',action='store_true');a=ap.parse_args()
    if a.aggregate_only:return aggregate_only()
    if a.system is None or a.family is None or a.ratio is None:raise SystemExit('provide --system --family --ratio, or --aggregate-only')
    rows,paths=build_chunk(a.system,a.family,float(a.ratio),period_map());write_csv(OUT/f'dataset_{a.system}_f{a.family}_r{float(a.ratio):.2f}.csv',rows);np.savez_compressed(OUT/f'raw_paths_{a.system}_f{a.family}_r{float(a.ratio):.2f}.npz',**paths);print(a.system,a.family,a.ratio,len(rows))
if __name__=='__main__':main()
