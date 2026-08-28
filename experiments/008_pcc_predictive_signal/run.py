"""Experiment 008: PCC-specific predictive signal after geometry controls."""

from __future__ import annotations

import csv
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pcc_ebid_regulator.benchmark import benchmark_step
from pcc_ebid_regulator.dynamics import step
from pcc_ebid_regulator.metrics import regulation_error, entropy_deficit
from pcc_ebid_regulator.regulators import (
    OracleFixedActionBenchmarkRegulator,
    OracleFixedActionTopologyRegulator,
    apply_multichannel_action,
    matched_directional_repertoire,
)
from pcc_ebid_regulator.signals import benchmark_activity, pcc_interaction_activity, simplex_phase

OUT = ROOT / "results" / "008_pcc_predictive_signal"
OUT.mkdir(parents=True, exist_ok=True)
TARGET = np.ones(3) / 3.0
TOPOLOGIES = ["canonical", "reverse", "no_pressure_control", "no_control_chaos"]
REGIMES = ["pressure_bias", "control_bias", "chaos_bias", "mixed_bias"]
STRENGTHS = [0.5, 1.0, 1.5, 2.0, 3.0]
HORIZON = 50
K = 9
MAX_ACTION = 0.12
SEED = 20260828


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def future_pcc_error(state, strength, topology):
    actions = matched_directional_repertoire((1,), cardinality=K, max_action=MAX_ACTION)
    reg = OracleFixedActionTopologyRegulator(actions=actions, model_strength=strength)
    x = state.copy(); errs=[]
    for _ in range(HORIZON):
        u = reg.choose_topology(x, TARGET, topology)
        x = step(apply_multichannel_action(x, u), strength=strength, topology=topology)
        errs.append(regulation_error(x, TARGET))
    return float(np.mean(errs))


def future_benchmark_error(state, strength, regime):
    actions = matched_directional_repertoire((1,), cardinality=K, max_action=MAX_ACTION)
    reg = OracleFixedActionBenchmarkRegulator(actions=actions, model_strength=strength)
    x = state.copy(); errs=[]
    for _ in range(HORIZON):
        u = reg.choose_regime(x, TARGET, regime)
        x = benchmark_step(apply_multichannel_action(x, u), strength=strength, regime=regime)
        errs.append(regulation_error(x, TARGET))
    return float(np.mean(errs))


def build_dataset(n=320):
    rng=np.random.default_rng(SEED); rows=[]
    states=rng.dirichlet(np.array([1.4,1.4,1.4]), size=n)
    for i,x in enumerate(states):
        strength=float(STRENGTHS[i % len(STRENGTHS)])
        topology=TOPOLOGIES[(i // len(STRENGTHS)) % len(TOPOLOGIES)]
        regime=REGIMES[(i // len(STRENGTHS)) % len(REGIMES)]
        base={"sample":i,"P":x[0],"C":x[1],"Ch":x[2],"strength":strength,
              "imbalance":regulation_error(x,TARGET),"entropy_deficit":entropy_deficit(x),
              "phase":simplex_phase(x)}
        rows.append({**base,"system":"pcc","structure":topology,
                     "activity":pcc_interaction_activity(x,strength=strength,topology=topology),
                     "future_error":future_pcc_error(x,strength,topology)})
        rows.append({**base,"system":"benchmark","structure":regime,
                     "activity":benchmark_activity(x,strength=strength,regime=regime),
                     "future_error":future_benchmark_error(x,strength,regime)})
    return rows


def design(rows, spec):
    cols=[]
    if "geometry2" in spec:
        P=np.array([float(r["P"]) for r in rows]); C=np.array([float(r["C"]) for r in rows]); S=np.array([float(r["strength"]) for r in rows])
        cols += [P,C,S,P*P,C*C,S*S,P*C,P*S,C*S]
    elif "geometry" in spec:
        cols += [np.array([float(r["P"]) for r in rows]), np.array([float(r["C"]) for r in rows]), np.array([float(r["strength"]) for r in rows])]
    if "coarse" in spec:
        cols += [np.array([float(r["imbalance"]) for r in rows]), np.array([float(r["strength"]) for r in rows])]
    if "activity" in spec: cols += [np.array([float(r["activity"]) for r in rows])]
    if "phase" in spec:
        ph=np.array([float(r["phase"]) for r in rows]); cols += [np.sin(ph),np.cos(ph)]
    X=np.column_stack([np.ones(len(rows)),*cols])
    return X


def cv_r2(rows, spec, folds=8):
    y=np.array([float(r["future_error"]) for r in rows]); preds=np.empty_like(y)
    idx=np.arange(len(rows))
    for fold in range(folds):
        test=(idx % folds)==fold; train=~test
        Xtr=design([rows[j] for j in idx[train]],spec); Xte=design([rows[j] for j in idx[test]],spec)
        beta=np.linalg.lstsq(Xtr,y[train],rcond=None)[0]; preds[test]=Xte@beta
    denom=np.sum((y-y.mean())**2)
    return 1-float(np.sum((y-preds)**2)/denom)


def main():
    rows=build_dataset(); write_csv(OUT/"dataset.csv",rows)
    summaries=[]
    specs=["coarse","coarse+activity","coarse+phase","coarse+activity+phase","geometry","geometry+activity","geometry2","geometry2+activity"]
    for system in ("pcc","benchmark"):
        sub=[r for r in rows if r["system"]==system]
        scores={s:cv_r2(sub,s) for s in specs}
        for s,v in scores.items(): summaries.append({"system":system,"model":s,"cv_r2":v})
        print(system.upper())
        for s in specs: print(f"  {s:24s} R2={scores[s]:.4f}")
        print(f"  activity gain over coarse: {scores['coarse+activity']-scores['coarse']:+.4f}")
        print(f"  activity gain over geometry: {scores['geometry+activity']-scores['geometry']:+.4f}")
        print(f"  activity gain over nonlinear geometry: {scores['geometry2+activity']-scores['geometry2']:+.4f}")
    write_csv(OUT/"predictive_models.csv",summaries)
    p=[r for r in summaries if r['system']=='pcc']; b=[r for r in summaries if r['system']=='benchmark']
    def score(lst,name): return float(next(r['cv_r2'] for r in lst if r['model']==name))
    comparison=[{
      "pcc_activity_gain_over_coarse":score(p,"coarse+activity")-score(p,"coarse"),
      "benchmark_activity_gain_over_coarse":score(b,"coarse+activity")-score(b,"coarse"),
      "pcc_activity_gain_over_geometry":score(p,"geometry+activity")-score(p,"geometry"),
      "benchmark_activity_gain_over_geometry":score(b,"geometry+activity")-score(b,"geometry"),
      "pcc_minus_benchmark_geometry_gain":(score(p,"geometry+activity")-score(p,"geometry"))-(score(b,"geometry+activity")-score(b,"geometry")),
      "pcc_activity_gain_over_geometry2":score(p,"geometry2+activity")-score(p,"geometry2"),
      "benchmark_activity_gain_over_geometry2":score(b,"geometry2+activity")-score(b,"geometry2"),
      "pcc_minus_benchmark_geometry2_gain":(score(p,"geometry2+activity")-score(p,"geometry2"))-(score(b,"geometry2+activity")-score(b,"geometry2")),
    }]
    write_csv(OUT/"specificity_summary.csv",comparison)

if __name__=="__main__": main()
