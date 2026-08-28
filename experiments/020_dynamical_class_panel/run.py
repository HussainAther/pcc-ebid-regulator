"""Experiment 020: dynamical-class panel.

Compare frozen canonical EBID incremental value across five compositional classes:
PCC, persistent exogenous oscillator, damped oscillator, directional flow, and
neutral stochastic diffusion. New simulations are required only for damped and
neutral controls; PCC, persistent oscillator, and directional results are frozen
from Experiments 017-019.
"""
from __future__ import annotations
import argparse,csv,sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'src'))
from pcc_ebid_regulator.ebid import canonical_ebid_features, quadratic_rate_features
from pcc_ebid_regulator.metrics import regulation_error
from pcc_ebid_regulator.regulators import apply_multichannel_action, matched_directional_repertoire
from pcc_ebid_regulator.signals import simplex_phase
from pcc_ebid_regulator.stochastic import perturb_simplex
from pcc_ebid_regulator.panel_benchmarks import (
    DAMPED_REGIMES,NEUTRAL_REGIMES,damped_oscillatory_step,damped_activity,
    neutral_step,neutral_activity,
)

OUT=ROOT/'results'/'020_dynamical_class_panel';OUT.mkdir(parents=True,exist_ok=True)
PERIOD_SOURCE=ROOT/'results'/'015_transition_band'/'reference_periods.csv'
PCC_FOLDS=ROOT/'results'/'017_leave_one_family_out'/'fold_gains.csv'
OSC_FOLDS=ROOT/'results'/'019_oscillatory_specificity'/'fold_gains.csv'
DIR_FOLDS=ROOT/'results'/'018_nonpcc_specificity'/'fold_gains.csv'
TARGET=np.ones(3)/3;STRENGTHS=[0.5,1.0,2.0,3.0];TRAIN_NOISE=[0.0,0.002,0.005];TEST_NOISE=[0.01,0.02]
RATIOS=[0.60,1.00];HORIZON=40;REPLICATES=2;K=9;MAX_ACTION=0.12;RIDGE_ALPHA=0.10;DAMPING_CYCLES=0.75
SEED=20260920;FAMILY_SEEDS=[20261001,20261019,20261107,20261123,20261211,20261229,20270117,20270203]
EBID_KEYS=["ebid_initial_entropy","ebid_mean_entropy","ebid_end_entropy","ebid_entropy_drop","ebid_entropy_slope","ebid_mean_entropy_rate","ebid_min_entropy_rate","ebid_entropy_rate_variance","ebid_deficit_growth","ebid_max_deficit_rate","ebid_deficit_rate_variance"]
QUAD_KEYS=["quad_initial","quad_mean","quad_end","quad_growth","quad_slope","quad_mean_rate","quad_min_rate","quad_max_rate","quad_rate_variance"]
ACTIVITY_KEYS=["activity_initial","activity_mean","activity_end","activity_max","activity_slope"]


def read_csv(path):
    with Path(path).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def write_csv(path,rows):
    if not rows:return
    with Path(path).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def period_map():return {float(r['strength']):float(r['median_cycle_period']) for r in read_csv(PERIOD_SOURCE)}
def obs_steps(p,r):return max(5,int(round(p*r)))
def slope(a):
    a=np.asarray(a,float);return float(np.polyfit(np.arange(len(a)),a,1)[0]) if len(a)>1 else 0.0
def activity_features(v):
    a=np.asarray(v,float);return {'activity_initial':float(a[0]),'activity_mean':float(a.mean()),'activity_end':float(a[-1]),'activity_max':float(a.max()),'activity_slope':slope(a)}
def regimes(system):return DAMPED_REGIMES if system=='damped_oscillator' else NEUTRAL_REGIMES
def deterministic_step(system,x,t,period,strength,regime):
    if system=='damped_oscillator':return damped_oscillatory_step(x,t=t,period=period,strength=strength,regime=regime,damping_cycles=DAMPING_CYCLES)
    return neutral_step(x,regime=regime)
def activity(system,x,t,period,strength,regime):
    if system=='damped_oscillator':return damped_activity(x,t=t,period=period,strength=strength,regime=regime,damping_cycles=DAMPING_CYCLES)
    return neutral_activity(x,regime=regime)
def stoch_step(system,x,t,period,strength,regime,sigma,rng):return perturb_simplex(deterministic_step(system,x,t,period,strength,regime),sigma,rng)
def observe(system,initial,period,strength,regime,sigma,rng,n):
    x=initial.copy();traj=[x.copy()];acts=[]
    for t in range(n+1):
        acts.append(activity(system,x,t,period,strength,regime))
        if t<n:x=stoch_step(system,x,t,period,strength,regime,sigma,rng);traj.append(x.copy())
    return x,np.asarray(traj),activity_features(acts)
def choose_action(system,x,t,period,strength,regime,actions):
    best=None;besterr=float('inf')
    for u in actions:
        z=apply_multichannel_action(x,u);z=deterministic_step(system,z,t,period,strength,regime);e=regulation_error(z,TARGET)
        if e<besterr:besterr=e;best=u
    return best
def future_error(system,state,start_t,period,strength,regime,sigma,seed):
    rng=np.random.default_rng(seed);actions=matched_directional_repertoire((1,),cardinality=K,max_action=MAX_ACTION);x=state.copy();errs=[]
    for j in range(HORIZON):
        t=start_t+j;u=choose_action(system,x,t,period,strength,regime,actions);x=apply_multichannel_action(x,u);x=stoch_step(system,x,t,period,strength,regime,sigma,rng);errs.append(regulation_error(x,TARGET))
    return float(np.mean(errs))
def family_ratio_seed(system,fi,ratio):return int(FAMILY_SEEDS[fi]+round(ratio*10000)+(200000 if system=='damped_oscillator' else 210000))
def build_family_ratio(system,fi,ratio,pmap):
    master=np.random.default_rng(family_ratio_seed(system,fi,ratio));rows=[]
    for si,regime in enumerate(regimes(system)):
      for strength in STRENGTHS:
        period=pmap[strength];obs=obs_steps(period,ratio)
        for sigma in TRAIN_NOISE+TEST_NOISE:
          for rep in range(REPLICATES):
            initial=master.dirichlet(np.array([1.4,1.4,1.4]));os=int(master.integers(0,2**31-1));fs=int(master.integers(0,2**31-1))
            end,traj,act=observe(system,initial,period,strength,regime,sigma,np.random.default_rng(os),obs)
            rows.append({'system':system,'seed_family':fi,'family_seed':FAMILY_SEEDS[fi],'structure_index':si,'structure':regime,'strength':strength,'noise_sigma':sigma,'replicate':rep,'target_cycle_ratio':ratio,'observation_steps':obs,'pcc_reference_cycle_period':period,'P':float(end[0]),'C':float(end[1]),'Ch':float(end[2]),'imbalance':regulation_error(end,TARGET),'phase':simplex_phase(end),**act,**quadratic_rate_features(traj),**canonical_ebid_features(traj),'future_error':future_error(system,end,obs,period,strength,regime,sigma,fs)})
    return rows
def col(rows,k):return np.asarray([float(r[k]) for r in rows],float)
def raw_design(rows,include_ebid):
    P,C,S=col(rows,'P'),col(rows,'C'),col(rows,'strength');ph=col(rows,'phase');cols=[P,C,S,P*P,C*C,S*S,P*C,P*S,C*S,*[col(rows,k) for k in ACTIVITY_KEYS],np.sin(ph),np.cos(ph),*[col(rows,k) for k in QUAD_KEYS]]
    if include_ebid:cols += [col(rows,k) for k in EBID_KEYS]
    return np.column_stack(cols)
def ridge_predict(train,test,include_ebid):
    X=raw_design(train,include_ebid);Z=raw_design(test,include_ebid);mu=X.mean(0);sd=X.std(0);sd[sd<1e-10]=1;X=(X-mu)/sd;Z=(Z-mu)/sd;Xa=np.column_stack([np.ones(len(X)),X]);Za=np.column_stack([np.ones(len(Z)),Z]);pen=np.eye(Xa.shape[1]);pen[0,0]=0;beta=np.linalg.solve(Xa.T@Xa+RIDGE_ALPHA*pen,Xa.T@col(train,'future_error'));return Za@beta
def rel_gain(y,p0,p1):
    b=float(np.mean(np.abs(y-p0)));e=float(np.mean(np.abs(y-p1)));return (b-e)/b,b,e
def bootstrap(y,p0,p1,seed,n=3000):
    rng=np.random.default_rng(seed);vals=[]
    for _ in range(n):
      idx=rng.integers(0,len(y),len(y));b=float(np.mean(np.abs(y[idx]-p0[idx])));e=float(np.mean(np.abs(y[idx]-p1[idx])));vals.append((b-e)/b if b>1e-12 else 0)
    return tuple(map(float,np.quantile(vals,[.025,.975])))
def split(rows,ratio,held):
    rr=[r for r in rows if abs(float(r['target_cycle_ratio'])-ratio)<1e-12];tr=[r for r in rr if int(r['seed_family'])!=held and int(r['structure_index'])!=0 and float(r['noise_sigma']) in TRAIN_NOISE];te=[r for r in rr if int(r['seed_family'])==held and int(r['structure_index'])==0 and float(r['noise_sigma']) in TEST_NOISE];return tr,te
def evaluate(system,rows):
    folds=[]
    for ratio in RATIOS:
      for fi in range(8):
        tr,te=split(rows,ratio,fi);y=col(te,'future_error');p0=ridge_predict(tr,te,False);p1=ridge_predict(tr,te,True);g,b,e=rel_gain(y,p0,p1);lo,hi=bootstrap(y,p0,p1,SEED+fi*100+int(ratio*1000)+(0 if system=='damped_oscillator' else 50000));folds.append({'system':system,'target_cycle_ratio':ratio,'heldout_family':fi,'n_train':len(tr),'n_test':len(te),'base_mae':b,'ebid_mae':e,'relative_mae_reduction':g,'bootstrap_ci_low':lo,'bootstrap_ci_high':hi,'ebid_better':int(g>0)})
    return folds
def boot_family(vals,seed,n=10000):
    a=np.asarray(vals,float);rng=np.random.default_rng(seed);means=[float(np.mean(a[rng.integers(0,len(a),len(a))])) for _ in range(n)];return tuple(map(float,np.quantile(means,[.025,.975])))
def summarize_folds(folds):
    out=[]
    for system in sorted(set(r['system'] for r in folds)):
      for ratio in RATIOS:
        ss=[r for r in folds if r['system']==system and abs(float(r['target_cycle_ratio'])-ratio)<1e-12];v=np.asarray([float(r['relative_mae_reduction']) for r in ss]);lo,hi=boot_family(v,SEED+hash(system)%10000+int(ratio*1000));out.append({'system':system,'target_cycle_ratio':ratio,'mean_gain':float(v.mean()),'median_gain':float(np.median(v)),'positive_families':int(np.sum(v>0)),'n_families':len(v),'bootstrap_mean_ci_low':lo,'bootstrap_mean_ci_high':hi})
    return out
def normalize_existing(path,system):
    out=[]
    for r in read_csv(path):
      ratio=float(r['target_cycle_ratio'])
      if ratio not in RATIOS:continue
      out.append({'system':system,'target_cycle_ratio':ratio,'heldout_family':int(r['heldout_family']),'relative_mae_reduction':float(r['relative_mae_reduction'])})
    return out
def class_properties():
    return [
      {'system':'pcc','endogenous_interaction':1,'persistent_oscillation':1,'transient_oscillation':0,'directional_drift':0,'neutral_diffusion':0},
      {'system':'oscillatory_benchmark','endogenous_interaction':0,'persistent_oscillation':1,'transient_oscillation':0,'directional_drift':0,'neutral_diffusion':0},
      {'system':'damped_oscillator','endogenous_interaction':0,'persistent_oscillation':0,'transient_oscillation':1,'directional_drift':0,'neutral_diffusion':0},
      {'system':'directional_benchmark','endogenous_interaction':0,'persistent_oscillation':0,'transient_oscillation':0,'directional_drift':1,'neutral_diffusion':0},
      {'system':'neutral_diffusion','endogenous_interaction':0,'persistent_oscillation':0,'transient_oscillation':0,'directional_drift':0,'neutral_diffusion':1},
    ]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--system',choices=['damped_oscillator','neutral_diffusion']);ap.add_argument('--family',type=int);ap.add_argument('--ratio',type=float);ap.add_argument('--aggregate-only',action='store_true');args=ap.parse_args();pmap=period_map()
    if args.family is not None:
      rows=build_family_ratio(args.system,args.family,float(args.ratio),pmap);write_csv(OUT/f"dataset_{args.system}_f{args.family}_r{float(args.ratio):.2f}.csv",rows);print(len(rows));return
    new_folds=[]
    for system in ['damped_oscillator','neutral_diffusion']:
      rows=[]
      for fi in range(8):
        for ratio in RATIOS:
          path=OUT/f'dataset_{system}_f{fi}_r{ratio:.2f}.csv'
          rows += read_csv(path) if args.aggregate_only else build_family_ratio(system,fi,ratio,pmap)
      write_csv(OUT/f'dataset_{system}.csv',rows);new_folds += evaluate(system,rows)
    write_csv(OUT/'new_class_fold_gains.csv',new_folds)
    all_folds=[]
    all_folds += normalize_existing(PCC_FOLDS,'pcc')
    all_folds += normalize_existing(OSC_FOLDS,'oscillatory_benchmark')
    all_folds += normalize_existing(DIR_FOLDS,'directional_benchmark')
    all_folds += [{'system':r['system'],'target_cycle_ratio':float(r['target_cycle_ratio']),'heldout_family':int(r['heldout_family']),'relative_mae_reduction':float(r['relative_mae_reduction'])} for r in new_folds]
    summary=summarize_folds(all_folds);write_csv(OUT/'panel_summary.csv',summary);write_csv(OUT/'panel_fold_gains.csv',all_folds);write_csv(OUT/'class_properties.csv',class_properties())
    for ratio in RATIOS:
      print(f'ratio={ratio:.2f}')
      for r in summary:
        if abs(float(r['target_cycle_ratio'])-ratio)<1e-12: print(f"  {r['system']:<24} {100*float(r['mean_gain']):+6.1f}%  positive {r['positive_families']}/8")
if __name__=='__main__':main()
