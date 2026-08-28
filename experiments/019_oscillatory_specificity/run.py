"""Experiment 019: oscillatory non-PCC specificity control.

Tests the two stabilized PCC observation scales (0.60 and 1.00 reference cycles)
against an externally forced oscillatory simplex benchmark. The benchmark has matched
absolute observation periods and cyclic trajectories but no endogenous PCC/RPS coupling.
"""
from __future__ import annotations
import argparse, csv, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from pcc_ebid_regulator.ebid import canonical_ebid_features, quadratic_rate_features
from pcc_ebid_regulator.metrics import regulation_error
from pcc_ebid_regulator.regulators import apply_multichannel_action, matched_directional_repertoire
from pcc_ebid_regulator.signals import simplex_phase
from pcc_ebid_regulator.stochastic import perturb_simplex
from pcc_ebid_regulator.oscillatory_benchmark import REGIMES, oscillatory_step, oscillatory_activity

OUT=ROOT/'results'/'019_oscillatory_specificity'; OUT.mkdir(parents=True,exist_ok=True)
PCC_SCALE=ROOT/'results'/'017_leave_one_family_out'/'scale_map.csv'
PCC_FOLDS=ROOT/'results'/'017_leave_one_family_out'/'fold_gains.csv'
PERIOD_SOURCE=ROOT/'results'/'015_transition_band'/'reference_periods.csv'
TARGET=np.ones(3)/3
STRENGTHS=[0.5,1.0,2.0,3.0]; TRAIN_NOISE=[0.0,0.002,0.005]; TEST_NOISE=[0.01,0.02]
RATIOS=[0.60,1.00]; HORIZON=40; REPLICATES=2; K=9; MAX_ACTION=0.12; RIDGE_ALPHA=0.10
SEED=20260919; FAMILY_SEEDS=[20261001,20261019,20261107,20261123,20261211,20261229,20270117,20270203]
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
def stoch_step(x,t,period,strength,regime,sigma,rng):return perturb_simplex(oscillatory_step(x,t=t,period=period,strength=strength,regime=regime),sigma,rng)
def observe(initial,period,strength,regime,sigma,rng,n):
    x=initial.copy();traj=[x.copy()];acts=[]
    for t in range(n+1):
        acts.append(oscillatory_activity(x,t=t,period=period,regime=regime,strength=strength))
        if t<n:x=stoch_step(x,t,period,strength,regime,sigma,rng);traj.append(x.copy())
    return x,np.asarray(traj),activity_features(acts)
def choose_action(x,t,period,strength,regime,actions):
    best=None;besterr=float('inf')
    for u in actions:
        z=apply_multichannel_action(x,u)
        z=oscillatory_step(z,t=t,period=period,strength=strength,regime=regime)
        e=regulation_error(z,TARGET)
        if e<besterr:besterr=e;best=u
    return best
def future_error(state,start_t,period,strength,regime,sigma,seed):
    rng=np.random.default_rng(seed);actions=matched_directional_repertoire((1,),cardinality=K,max_action=MAX_ACTION);x=state.copy();errs=[]
    for j in range(HORIZON):
        t=start_t+j;u=choose_action(x,t,period,strength,regime,actions);x=apply_multichannel_action(x,u);x=stoch_step(x,t,period,strength,regime,sigma,rng);errs.append(regulation_error(x,TARGET))
    return float(np.mean(errs))
def family_ratio_seed(fi,ratio):return int(FAMILY_SEEDS[fi]+round(ratio*10000)+190000)
def build_family_ratio(fi,ratio,pmap):
    master=np.random.default_rng(family_ratio_seed(fi,ratio));rows=[]
    for si,regime in enumerate(REGIMES):
      for strength in STRENGTHS:
        period=pmap[strength];obs=obs_steps(period,ratio)
        for sigma in TRAIN_NOISE+TEST_NOISE:
          for rep in range(REPLICATES):
            initial=master.dirichlet(np.array([1.4,1.4,1.4]));os=int(master.integers(0,2**31-1));fs=int(master.integers(0,2**31-1))
            end,traj,act=observe(initial,period,strength,regime,sigma,np.random.default_rng(os),obs)
            rows.append({'seed_family':fi,'family_seed':FAMILY_SEEDS[fi],'structure_index':si,'structure':regime,'strength':strength,'noise_sigma':sigma,'replicate':rep,'target_cycle_ratio':ratio,'observation_steps':obs,'pcc_reference_cycle_period':period,'P':float(end[0]),'C':float(end[1]),'Ch':float(end[2]),'imbalance':regulation_error(end,TARGET),'phase':simplex_phase(end),**act,**quadratic_rate_features(traj),**canonical_ebid_features(traj),'future_error':future_error(end,obs,period,strength,regime,sigma,fs)})
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
def evaluate(rows):
    folds=[];preds=[]
    for ratio in RATIOS:
      for fi in range(8):
        tr,te=split(rows,ratio,fi);y=col(te,'future_error');p0=ridge_predict(tr,te,False);p1=ridge_predict(tr,te,True);g,b,e=rel_gain(y,p0,p1);lo,hi=bootstrap(y,p0,p1,SEED+fi*100+int(ratio*1000));folds.append({'system':'oscillatory_benchmark','target_cycle_ratio':ratio,'heldout_family':fi,'n_train':len(tr),'n_test':len(te),'base_mae':b,'ebid_mae':e,'relative_mae_reduction':g,'bootstrap_ci_low':lo,'bootstrap_ci_high':hi,'ebid_better':int(g>0)})
        for r,yy,a,z in zip(te,y,p0,p1):preds.append({'target_cycle_ratio':ratio,'heldout_family':fi,'strength':r['strength'],'noise_sigma':r['noise_sigma'],'future_error':yy,'baseline_prediction':a,'ebid_prediction':z})
    return folds,preds
def boot_family(vals,seed,n=10000):
    a=np.asarray(vals,float);rng=np.random.default_rng(seed);means=[float(np.mean(a[rng.integers(0,len(a),len(a))])) for _ in range(n)];return tuple(map(float,np.quantile(means,[.025,.975])))
def aggregate(folds):
    out=[]
    for ratio in RATIOS:
      ss=[r for r in folds if abs(float(r['target_cycle_ratio'])-ratio)<1e-12];v=np.asarray([float(r['relative_mae_reduction']) for r in ss]);lo,hi=boot_family(v,SEED+5000+int(ratio*1000));out.append({'system':'oscillatory_benchmark','target_cycle_ratio':ratio,'mean_gain':float(v.mean()),'median_gain':float(np.median(v)),'positive_families':int(np.sum(v>0)),'n_families':len(v),'bootstrap_mean_ci_low':lo,'bootstrap_mean_ci_high':hi})
    return out
def compare(summ):
    pcc={float(r['target_cycle_ratio']):r for r in read_csv(PCC_SCALE)};out=[]
    for b in summ:
      ratio=float(b['target_cycle_ratio']);p=pcc[ratio];pg=float(p['mean_gain']);bg=float(b['mean_gain']);out.append({'target_cycle_ratio':ratio,'pcc_mean_gain':pg,'pcc_positive_families':int(float(p['positive_families'])),'osc_mean_gain':bg,'osc_positive_families':int(b['positive_families']),'specificity_margin_pcc_minus_osc':pg-bg})
    return out
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--family',type=int);ap.add_argument('--ratio',type=float);ap.add_argument('--aggregate-only',action='store_true');args=ap.parse_args();pmap=period_map()
    if args.family is not None:
      rows=build_family_ratio(args.family,float(args.ratio),pmap);write_csv(OUT/f"dataset_f{args.family}_r{float(args.ratio):.2f}.csv",rows);print(len(rows));return
    if args.aggregate_only:
      rows=[]
      for fi in range(8):
        for ratio in RATIOS:rows += read_csv(OUT/f'dataset_f{fi}_r{ratio:.2f}.csv')
    else:
      rows=[]
      for fi in range(8):
        for ratio in RATIOS:rows += build_family_ratio(fi,ratio,pmap)
    write_csv(OUT/'dataset.csv',rows);folds,preds=evaluate(rows);summ=aggregate(folds);comp=compare(summ);pcc_folds=read_csv(PCC_FOLDS);paired=[]
    for ratio in RATIOS:
      pv={int(r['heldout_family']):float(r['relative_mae_reduction']) for r in pcc_folds if abs(float(r['target_cycle_ratio'])-ratio)<1e-12};ov={int(r['heldout_family']):float(r['relative_mae_reduction']) for r in folds if abs(float(r['target_cycle_ratio'])-ratio)<1e-12};m=np.asarray([pv[i]-ov[i] for i in sorted(pv)],float);lo,hi=boot_family(m,SEED+9000+int(ratio*1000))
      for i in sorted(pv):paired.append({'target_cycle_ratio':ratio,'heldout_family':i,'pcc_gain':pv[i],'osc_gain':ov[i],'specificity_margin':pv[i]-ov[i]})
      for r in comp:
        if abs(float(r['target_cycle_ratio'])-ratio)<1e-12:r['paired_margin_ci_low']=lo;r['paired_margin_ci_high']=hi;r['positive_specificity_families']=int(np.sum(m>0))
    write_csv(OUT/'fold_gains.csv',folds);write_csv(OUT/'test_predictions.csv',preds);write_csv(OUT/'scale_map.csv',summ);write_csv(OUT/'family_specificity.csv',paired);write_csv(OUT/'pcc_vs_oscillatory.csv',comp)
    for r in comp:print(f"ratio={r['target_cycle_ratio']:.2f} PCC={100*r['pcc_mean_gain']:+.1f}% osc={100*r['osc_mean_gain']:+.1f}% margin={100*r['specificity_margin_pcc_minus_osc']:+.1f} pp CI=[{100*r['paired_margin_ci_low']:+.1f},{100*r['paired_margin_ci_high']:+.1f}] pp")
if __name__=='__main__':main()
