"""Experiment 013: observation-timescale sufficiency for canonical EBID.

Canonical EBID is frozen. We densely sweep observation length and normalize it
by an independently estimated intrinsic PCC cycle period at each coupling
strength. Evaluation uses the hard joint-OOD protocol: held-out canonical PCC
plus unseen noise. A matched non-PCC benchmark is evaluated by raw observation
length only because it has no endogenous cycle period.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pcc_ebid_regulator.benchmark import benchmark_step
from pcc_ebid_regulator.dynamics import step, simulate
from pcc_ebid_regulator.ebid import canonical_ebid_features, quadratic_rate_features
from pcc_ebid_regulator.metrics import regulation_error
from pcc_ebid_regulator.regulators import OracleFixedActionBenchmarkRegulator, OracleFixedActionTopologyRegulator, apply_multichannel_action, matched_directional_repertoire
from pcc_ebid_regulator.signals import benchmark_activity, pcc_interaction_activity, simplex_phase
from pcc_ebid_regulator.stochastic import perturb_simplex
from pcc_ebid_regulator.timescale import phase_cycle_period

OUT = ROOT / "results" / "013_observation_timescale"
OUT.mkdir(parents=True, exist_ok=True)
TARGET = np.ones(3) / 3.0
TOPOLOGIES = ["canonical", "reverse", "no_pressure_control", "no_control_chaos"]
REGIMES = ["pressure_bias", "control_bias", "chaos_bias", "mixed_bias"]
STRENGTHS = [0.5, 1.0, 2.0, 3.0]
TRAIN_NOISE = [0.0, 0.002, 0.005]
TEST_NOISE = [0.01, 0.02]
OBS_WINDOWS = list(range(5, 81, 5))
HORIZONS = [40]
REPLICATES = 1
K = 9
MAX_ACTION = 0.12
SEED = 20260828
EBID_KEYS = ["ebid_initial_entropy","ebid_mean_entropy","ebid_end_entropy","ebid_entropy_drop","ebid_entropy_slope","ebid_mean_entropy_rate","ebid_min_entropy_rate","ebid_entropy_rate_variance","ebid_deficit_growth","ebid_max_deficit_rate","ebid_deficit_rate_variance"]
QUAD_KEYS = ["quad_initial","quad_mean","quad_end","quad_growth","quad_slope","quad_mean_rate","quad_min_rate","quad_max_rate","quad_rate_variance"]
ACTIVITY_KEYS = ["activity_initial","activity_mean","activity_end","activity_max","activity_slope"]


def write_csv(path, rows):
    if not rows: return
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def slope(a):
    a=np.asarray(a,float); return float(np.polyfit(np.arange(len(a)),a,1)[0]) if len(a)>1 else 0.0


def activity_features(a):
    a=np.asarray(a,float); return {"activity_initial":float(a[0]),"activity_mean":float(a.mean()),"activity_end":float(a[-1]),"activity_max":float(a.max()),"activity_slope":slope(a)}


def reference_periods():
    rng=np.random.default_rng(SEED+13)
    out=[]
    for strength in STRENGTHS:
        vals=[]
        for _ in range(10):
            initial=rng.dirichlet(np.array([1.4,1.4,1.4]))
            tr=simulate(initial, 2200, strength=strength, topology="canonical")
            p=phase_cycle_period(tr, min_turns=0.75)
            if np.isfinite(p): vals.append(p)
        med=float(np.median(vals))
        out.append({"strength":strength,"median_cycle_period":med,"n_reference":len(vals)})
    return out


def stochastic_step(system,x,strength,structure,sigma,rng):
    nxt = step(x,strength=strength,topology=structure) if system=="pcc" else benchmark_step(x,strength=strength,regime=structure)
    return perturb_simplex(nxt,sigma,rng)


def observe(system,initial,strength,structure,sigma,rng,n):
    x=initial.copy(); traj=[x.copy()]; acts=[]
    af=pcc_interaction_activity if system=="pcc" else benchmark_activity
    kwargs={"topology":structure} if system=="pcc" else {"regime":structure}
    for t in range(n+1):
        acts.append(af(x,strength=strength,**kwargs))
        if t<n:
            x=stochastic_step(system,x,strength,structure,sigma,rng); traj.append(x.copy())
    return x,np.asarray(traj),activity_features(acts)


def future_errors(system,state,strength,structure,sigma,seed):
    rng=np.random.default_rng(seed)
    actions=matched_directional_repertoire((1,),cardinality=K,max_action=MAX_ACTION)
    if system=="pcc":
        reg=OracleFixedActionTopologyRegulator(actions=actions,model_strength=strength)
        choose=lambda x: reg.choose_topology(x,TARGET,structure)
    else:
        reg=OracleFixedActionBenchmarkRegulator(actions=actions,model_strength=strength)
        choose=lambda x: reg.choose_regime(x,TARGET,structure)
    x=state.copy(); errs=[]; out={}
    for t in range(1,max(HORIZONS)+1):
        x=apply_multichannel_action(x,choose(x)); x=stochastic_step(system,x,strength,structure,sigma,rng)
        errs.append(regulation_error(x,TARGET))
        if t in HORIZONS: out[t]=float(np.mean(errs))
    return out


def build_dataset(period_map):
    master=np.random.default_rng(SEED); rows=[]; sample=0
    for obs in OBS_WINDOWS:
      for si in range(4):
       for strength in STRENGTHS:
        for sigma in TRAIN_NOISE+TEST_NOISE:
         for rep in range(REPLICATES):
          initial=master.dirichlet(np.array([1.4,1.4,1.4])); paired_seed=int(master.integers(0,2**31-1))
          for system,structs in (("pcc",TOPOLOGIES),):
            structure=structs[si]; rng=np.random.default_rng(paired_seed)
            end,traj,act=observe(system,initial,strength,structure,sigma,rng,obs)
            ferr=future_errors(system,end,strength,structure,sigma,int(master.integers(0,2**31-1)))
            base={"sample":sample,"system":system,"structure_index":si,"structure":structure,"strength":strength,"noise_sigma":sigma,"replicate":rep,"observation_steps":obs,"P":float(end[0]),"C":float(end[1]),"Ch":float(end[2]),"imbalance":regulation_error(end,TARGET),"phase":simplex_phase(end),**act,**quadratic_rate_features(traj),**canonical_ebid_features(traj)}
            if system=="pcc":
                base["reference_cycle_period"]=period_map[strength]
                base["obs_cycle_ratio"]=obs/period_map[strength]
            else:
                base["reference_cycle_period"]=""; base["obs_cycle_ratio"]=""
            for h in HORIZONS:
                rows.append({**base,"future_horizon":h,"future_error":ferr[h]})
          sample+=1
    return rows


def col(rows,key): return np.asarray([float(r[key]) for r in rows],float)

def design(rows,ebid):
    P,C,S=col(rows,"P"),col(rows,"C"),col(rows,"strength"); ph=col(rows,"phase")
    O=col(rows,"observation_steps")/80.0
    cols=[P,C,S,O,P*P,C*C,S*S,O*O,P*C,P*S,C*S]+[col(rows,k) for k in ACTIVITY_KEYS]+[np.sin(ph),np.cos(ph)]+[col(rows,k) for k in QUAD_KEYS]
    if ebid: cols += [col(rows,k) for k in EBID_KEYS]
    return np.column_stack([np.ones(len(rows)),*cols])

def fitpred(train,test,ebid):
    beta=np.linalg.lstsq(design(train,ebid),col(train,"future_error"),rcond=None)[0]
    return design(test,ebid)@beta

def rel_mae(y,p0,p1):
    b=float(np.mean(np.abs(y-p0))); e=float(np.mean(np.abs(y-p1))); return (b-e)/b,b,e


def evaluate(rows,system,obs,horizon):
    # Fit once across all observation lengths to avoid a near-saturated
    # regression at each individual window. Observation duration is included
    # in both nested models, so EBID receives no credit for window length alone.
    sub=[r for r in rows if r["system"]==system and int(r["future_horizon"])==horizon]
    train=[r for r in sub if int(r["structure_index"])!=0 and float(r["noise_sigma"]) in TRAIN_NOISE]
    test=[r for r in sub if int(r["structure_index"])==0 and float(r["noise_sigma"]) in TEST_NOISE and int(r["observation_steps"])==obs]
    y=col(test,"future_error"); p0=fitpred(train,test,False); p1=fitpred(train,test,True)
    rr,b,e=rel_mae(y,p0,p1)
    ratios=[float(r["obs_cycle_ratio"]) for r in test]
    return {"system":system,"observation_steps":obs,"future_horizon":horizon,"n_train":len(train),"n_test":len(test),"mean_obs_cycle_ratio":float(np.mean(ratios)),"min_obs_cycle_ratio":float(np.min(ratios)),"max_obs_cycle_ratio":float(np.max(ratios)),"base_mae":b,"ebid_mae":e,"relative_mae_reduction":rr}


def main():
    pr=reference_periods(); write_csv(OUT/"reference_periods.csv",pr); pmap={float(r["strength"]):float(r["median_cycle_period"]) for r in pr}
    rows=build_dataset(pmap); write_csv(OUT/"dataset.csv",rows)
    summary=[]
    for system in ("pcc",):
      for obs in OBS_WINDOWS:
       for h in HORIZONS: summary.append(evaluate(rows,system,obs,h))
    write_csv(OUT/"summary.csv",summary)
    pcc=[r for r in summary if r["system"]=="pcc"]
    # For each horizon, first observation window with positive EBID transfer and first with >=10% gain.
    thresholds=[]
    for h in HORIZONS:
        hh=sorted([r for r in pcc if int(r["future_horizon"])==h],key=lambda r:int(r["observation_steps"]))
        for level in (0.0,0.10):
            hit=next((r for r in hh if float(r["relative_mae_reduction"])>=level),None)
            thresholds.append({"future_horizon":h,"gain_threshold":level,"first_observation_steps":hit["observation_steps"] if hit else "","mean_obs_cycle_ratio":hit["mean_obs_cycle_ratio"] if hit else ""})
    write_csv(OUT/"thresholds.csv",thresholds)
    print("REFERENCE PERIODS"); [print(r) for r in pr]
    print("\nPCC SUMMARY"); [print(r) for r in pcc]
    print("\nTHRESHOLDS"); [print(r) for r in thresholds]

if __name__=="__main__": main()
