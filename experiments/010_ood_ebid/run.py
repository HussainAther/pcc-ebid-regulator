"""Experiment 010: frozen canonical EBID under stochastic/OOD shift.

No EBID features are changed from Experiment 009. We test whether their
incremental predictive value survives (1) unseen noise levels, (2) held-out
PCC topologies / benchmark regimes, and (3) both shifts jointly.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pcc_ebid_regulator.benchmark import benchmark_step
from pcc_ebid_regulator.dynamics import step
from pcc_ebid_regulator.ebid import canonical_ebid_features, quadratic_rate_features
from pcc_ebid_regulator.metrics import regulation_error
from pcc_ebid_regulator.regulators import (
    OracleFixedActionBenchmarkRegulator,
    OracleFixedActionTopologyRegulator,
    apply_multichannel_action,
    matched_directional_repertoire,
)
from pcc_ebid_regulator.signals import benchmark_activity, pcc_interaction_activity, simplex_phase
from pcc_ebid_regulator.stochastic import perturb_simplex

OUT = ROOT / "results" / "010_ood_ebid"
OUT.mkdir(parents=True, exist_ok=True)
TARGET = np.ones(3) / 3.0
TOPOLOGIES = ["canonical", "reverse", "no_pressure_control", "no_control_chaos"]
REGIMES = ["pressure_bias", "control_bias", "chaos_bias", "mixed_bias"]
STRENGTHS = [0.5, 1.0, 1.5, 2.0, 3.0]
TRAIN_NOISE = [0.0, 0.002, 0.005]
TEST_NOISE = [0.01, 0.02]
ALL_NOISE = TRAIN_NOISE + TEST_NOISE
REPLICATES = 6
OBSERVATION_STEPS = 25
FUTURE_HORIZON = 40
K = 9
MAX_ACTION = 0.12
SEED = 20260828

EBID_KEYS = [
    "ebid_initial_entropy", "ebid_mean_entropy", "ebid_end_entropy",
    "ebid_entropy_drop", "ebid_entropy_slope", "ebid_mean_entropy_rate",
    "ebid_min_entropy_rate", "ebid_entropy_rate_variance",
    "ebid_deficit_growth", "ebid_max_deficit_rate", "ebid_deficit_rate_variance",
]
QUAD_KEYS = [
    "quad_initial", "quad_mean", "quad_end", "quad_growth", "quad_slope",
    "quad_mean_rate", "quad_min_rate", "quad_max_rate", "quad_rate_variance",
]
ACTIVITY_KEYS = ["activity_initial", "activity_mean", "activity_end", "activity_max", "activity_slope"]
BASE_SPEC = "geometry+activity+phase+quadratic"
EBID_SPEC = BASE_SPEC + "+ebid"


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def slope(a: np.ndarray) -> float:
    a = np.asarray(a, dtype=float)
    return float(np.polyfit(np.arange(a.size, dtype=float), a, 1)[0]) if a.size > 1 else 0.0


def activity_features(values: list[float]) -> dict[str, float]:
    a = np.asarray(values, dtype=float)
    return {"activity_initial": float(a[0]), "activity_mean": float(a.mean()),
            "activity_end": float(a[-1]), "activity_max": float(a.max()), "activity_slope": slope(a)}


def stochastic_pcc_step(x, strength, structure, sigma, rng):
    return perturb_simplex(step(x, strength=strength, topology=structure), sigma, rng)


def stochastic_benchmark_step(x, strength, structure, sigma, rng):
    return perturb_simplex(benchmark_step(x, strength=strength, regime=structure), sigma, rng)


def observe(system, initial, strength, structure, sigma, rng):
    x = initial.copy(); traj = [x.copy()]; acts = []
    activity_fn = pcc_interaction_activity if system == "pcc" else benchmark_activity
    step_fn = stochastic_pcc_step if system == "pcc" else stochastic_benchmark_step
    for _ in range(OBSERVATION_STEPS + 1):
        acts.append(activity_fn(x, strength=strength, **({"topology": structure} if system == "pcc" else {"regime": structure})))
        if len(traj) <= OBSERVATION_STEPS:
            x = step_fn(x, strength, structure, sigma, rng); traj.append(x.copy())
    return x, np.asarray(traj), activity_features(acts)


def future_error(system, state, strength, structure, sigma, rng):
    actions = matched_directional_repertoire((1,), cardinality=K, max_action=MAX_ACTION)
    if system == "pcc":
        reg = OracleFixedActionTopologyRegulator(actions=actions, model_strength=strength)
        choose = lambda x: reg.choose_topology(x, TARGET, structure)
        step_fn = stochastic_pcc_step
    else:
        reg = OracleFixedActionBenchmarkRegulator(actions=actions, model_strength=strength)
        choose = lambda x: reg.choose_regime(x, TARGET, structure)
        step_fn = stochastic_benchmark_step
    x = state.copy(); errors = []
    for _ in range(FUTURE_HORIZON):
        x = apply_multichannel_action(x, choose(x))
        x = step_fn(x, strength, structure, sigma, rng)
        errors.append(regulation_error(x, TARGET))
    return float(np.mean(errors))


def build_dataset():
    master = np.random.default_rng(SEED); rows = []; sample = 0
    for structure_index in range(4):
        for strength in STRENGTHS:
            for sigma in ALL_NOISE:
                for rep in range(REPLICATES):
                    initial = master.dirichlet(np.array([1.4, 1.4, 1.4]))
                    paired_seed = int(master.integers(0, 2**31 - 1))
                    for system, structures in (("pcc", TOPOLOGIES), ("benchmark", REGIMES)):
                        structure = structures[structure_index]
                        rng = np.random.default_rng(paired_seed)
                        end, traj, act = observe(system, initial, strength, structure, sigma, rng)
                        ferr = future_error(system, end, strength, structure, sigma, rng)
                        row = {"sample": sample, "replicate": rep, "system": system,
                               "structure_index": structure_index, "structure": structure,
                               "strength": strength, "noise_sigma": sigma,
                               "P": float(end[0]), "C": float(end[1]), "Ch": float(end[2]),
                               "imbalance": regulation_error(end, TARGET), "phase": simplex_phase(end),
                               **act, **quadratic_rate_features(traj), **canonical_ebid_features(traj),
                               "future_error": ferr}
                        rows.append(row)
                    sample += 1
    return rows


def col(rows, key): return np.asarray([float(r[key]) for r in rows], dtype=float)


def design(rows, spec):
    P, C, S = col(rows,"P"), col(rows,"C"), col(rows,"strength")
    cols = [P,C,S,P*P,C*C,S*S,P*C,P*S,C*S]
    if "+activity" in spec: cols += [col(rows,k) for k in ACTIVITY_KEYS]
    if "+phase" in spec:
        ph = col(rows,"phase"); cols += [np.sin(ph), np.cos(ph)]
    if "+quadratic" in spec: cols += [col(rows,k) for k in QUAD_KEYS]
    if "+ebid" in spec: cols += [col(rows,k) for k in EBID_KEYS]
    return np.column_stack([np.ones(len(rows)), *cols])


def fit_predict(train, test, spec):
    Xtr, Xte = design(train,spec), design(test,spec); ytr = col(train,"future_error")
    beta = np.linalg.lstsq(Xtr, ytr, rcond=None)[0]
    return Xte @ beta


def metrics(test, pred):
    y=col(test,"future_error"); denom=float(np.sum((y-y.mean())**2))
    r2 = 1.0-float(np.sum((y-pred)**2))/denom if denom>0 else float("nan")
    return r2, float(np.mean(np.abs(y-pred)))


def evaluate(train, test, system, protocol, held_out="", repeat=0):
    out=[]
    preds={}
    for spec in (BASE_SPEC, EBID_SPEC):
        pred=fit_predict(train,test,spec); preds[spec]=pred
        r2,mae=metrics(test,pred)
        out.append({"system":system,"protocol":protocol,"held_out":held_out,"repeat":repeat,
                    "spec":spec,"n_train":len(train),"n_test":len(test),"r2":r2,"mae":mae,
                    "relative_mae_reduction":"","bootstrap_low":"","bootstrap_high":""})
    base, ebid = out
    y=col(test,"future_error")
    base_abs=np.abs(y-preds[BASE_SPEC]); ebid_abs=np.abs(y-preds[EBID_SPEC])
    mae_gain=float(base_abs.mean()-ebid_abs.mean())
    rel=mae_gain/float(base_abs.mean()) if float(base_abs.mean())>0 else float("nan")
    rng=np.random.default_rng(SEED + 1009 + int(held_out or 0) + (0 if system=="pcc" else 100))
    boot=[]
    n=len(test)
    for _ in range(1000):
        idx=rng.integers(0,n,size=n)
        b=float(base_abs[idx].mean()); e=float(ebid_abs[idx].mean())
        boot.append((b-e)/b if b>0 else 0.0)
    low,high=np.quantile(boot,[0.025,0.975])
    out.append({"system":system,"protocol":protocol,"held_out":held_out,"repeat":repeat,
                "spec":"EBID_INCREMENT","n_train":len(train),"n_test":len(test),
                "r2":ebid["r2"]-base["r2"],"mae":mae_gain,
                "relative_mae_reduction":rel,"bootstrap_low":float(low),"bootstrap_high":float(high)})
    return out


def main():
    rows=build_dataset(); write_csv(OUT/"dataset.csv",rows)
    summary=[]
    for system in ("pcc","benchmark"):
        sub=[r for r in rows if r["system"]==system]
        # Noise OOD: all structures, low/no noise -> unseen higher noise.
        train=[r for r in sub if float(r["noise_sigma"]) in TRAIN_NOISE]
        test=[r for r in sub if float(r["noise_sigma"]) in TEST_NOISE]
        summary += evaluate(train,test,system,"noise_ood")
        # Leave-one-structure-out, using all noise levels to isolate structural OOD.
        for idx in range(4):
            tr=[r for r in sub if int(r["structure_index"])!=idx]
            te=[r for r in sub if int(r["structure_index"])==idx]
            summary += evaluate(tr,te,system,"structure_ood",held_out=str(idx))
            # Joint OOD: remaining structures at train noise -> held-out structure at unseen noise.
            trj=[r for r in sub if int(r["structure_index"])!=idx and float(r["noise_sigma"]) in TRAIN_NOISE]
            tej=[r for r in sub if int(r["structure_index"])==idx and float(r["noise_sigma"]) in TEST_NOISE]
            summary += evaluate(trj,tej,system,"joint_ood",held_out=str(idx))
    write_csv(OUT/"summary.csv",summary)

    increments=[r for r in summary if r["spec"]=="EBID_INCREMENT"]
    comparative=[]
    for protocol in ("noise_ood","structure_ood","joint_ood"):
        keys=sorted({r["held_out"] for r in increments if r["protocol"]==protocol})
        for key in keys:
            p=next(r for r in increments if r["protocol"]==protocol and r["held_out"]==key and r["system"]=="pcc")
            b=next(r for r in increments if r["protocol"]==protocol and r["held_out"]==key and r["system"]=="benchmark")
            comparative.append({"protocol":protocol,"held_out":key,
                                "pcc_ebid_delta_r2":p["r2"],"benchmark_ebid_delta_r2":b["r2"],
                                "specificity_margin":p["r2"]-b["r2"],
                                "pcc_relative_mae_reduction":p["relative_mae_reduction"],
                                "pcc_bootstrap_low":p["bootstrap_low"],"pcc_bootstrap_high":p["bootstrap_high"],
                                "benchmark_relative_mae_reduction":b["relative_mae_reduction"],
                                "benchmark_bootstrap_low":b["bootstrap_low"],"benchmark_bootstrap_high":b["bootstrap_high"],
                                "relative_mae_specificity_margin":p["relative_mae_reduction"]-b["relative_mae_reduction"]})
    write_csv(OUT/"comparative.csv",comparative)
    for r in comparative: print(r)

if __name__ == "__main__": main()
