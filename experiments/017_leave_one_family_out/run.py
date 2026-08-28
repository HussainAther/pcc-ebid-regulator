"""Experiment 017: leave-one-seed-family-out calibration.

Uses the frozen Experiment-016 simulated dataset. At each locked cycle ratio, the
baseline and canonical-EBID readouts are trained on seven complete seed families
(noncanonical structures at training-noise levels) and evaluated on the eighth
family's held-out canonical topology at unseen noise levels. This separates
small-sample local calibration instability from genuine out-of-family trajectory
heterogeneity without changing EBID, the ratios, horizon, or ridge readout.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

OUT = ROOT / "results" / "017_leave_one_family_out"
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / "results" / "016_cross_seed_scale_map" / "dataset.csv"

TRAIN_NOISE = {0.0, 0.002, 0.005}
TEST_NOISE = {0.01, 0.02}
CYCLE_RATIOS = [0.50, 0.60, 0.75, 1.00, 1.10, 1.20]
RIDGE_ALPHA = 0.10
SEED = 20260917

EBID_KEYS = [
    "ebid_initial_entropy", "ebid_mean_entropy", "ebid_end_entropy",
    "ebid_entropy_drop", "ebid_entropy_slope", "ebid_mean_entropy_rate",
    "ebid_min_entropy_rate", "ebid_entropy_rate_variance",
    "ebid_deficit_growth", "ebid_max_deficit_rate",
    "ebid_deficit_rate_variance",
]
QUAD_KEYS = [
    "quad_initial", "quad_mean", "quad_end", "quad_growth", "quad_slope",
    "quad_mean_rate", "quad_min_rate", "quad_max_rate", "quad_rate_variance",
]
ACTIVITY_KEYS = [
    "activity_initial", "activity_mean", "activity_end", "activity_max",
    "activity_slope",
]


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)


def col(rows, key):
    return np.asarray([float(r[key]) for r in rows], dtype=float)


def raw_design(rows, include_ebid):
    P, C, S = col(rows, "P"), col(rows, "C"), col(rows, "strength")
    phase = col(rows, "phase")
    cols = [
        P, C, S, P*P, C*C, S*S, P*C, P*S, C*S,
        *[col(rows, k) for k in ACTIVITY_KEYS],
        np.sin(phase), np.cos(phase),
        *[col(rows, k) for k in QUAD_KEYS],
    ]
    if include_ebid:
        cols += [col(rows, k) for k in EBID_KEYS]
    return np.column_stack(cols)


def ridge_fit_predict(train, test, include_ebid, alpha=RIDGE_ALPHA):
    X = raw_design(train, include_ebid); Z = raw_design(test, include_ebid)
    mu = X.mean(axis=0); sd = X.std(axis=0)
    sd[sd < 1e-10] = 1.0
    Xs = (X - mu) / sd; Zs = (Z - mu) / sd
    Xa = np.column_stack([np.ones(len(Xs)), Xs])
    Za = np.column_stack([np.ones(len(Zs)), Zs])
    penalty = np.eye(Xa.shape[1]); penalty[0, 0] = 0.0
    beta = np.linalg.solve(Xa.T @ Xa + alpha * penalty, Xa.T @ col(train, "future_error"))
    return Za @ beta


def relative_mae(y, p0, p1):
    b = float(np.mean(np.abs(y - p0))); e = float(np.mean(np.abs(y - p1)))
    return (b - e) / b, b, e


def bootstrap_relative_gain(y, p0, p1, seed, n_boot=5000):
    rng = np.random.default_rng(seed); n = len(y); gains = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        b = float(np.mean(np.abs(y[idx] - p0[idx]))); e = float(np.mean(np.abs(y[idx] - p1[idx])))
        if b > 1e-12:
            gains.append((b - e) / b)
    return float(np.quantile(gains, .025)), float(np.quantile(gains, .975))


def split_for_fold(rows, ratio: float, heldout_family: int):
    ratio_rows = [r for r in rows if abs(float(r["target_cycle_ratio"]) - ratio) < 1e-12]
    train = [
        r for r in ratio_rows
        if int(r["seed_family"]) != heldout_family
        and int(r["structure_index"]) != 0
        and float(r["noise_sigma"]) in TRAIN_NOISE
    ]
    test = [
        r for r in ratio_rows
        if int(r["seed_family"]) == heldout_family
        and int(r["structure_index"]) == 0
        and float(r["noise_sigma"]) in TEST_NOISE
    ]
    return train, test


def evaluate_folds(rows):
    families = sorted({int(r["seed_family"]) for r in rows})
    out = []; preds = []
    for ratio in CYCLE_RATIOS:
        for fi in families:
            train, test = split_for_fold(rows, ratio, fi)
            y = col(test, "future_error")
            p0 = ridge_fit_predict(train, test, False)
            p1 = ridge_fit_predict(train, test, True)
            gain, base, ebid = relative_mae(y, p0, p1)
            lo, hi = bootstrap_relative_gain(y, p0, p1, SEED + fi * 100 + int(ratio * 1000))
            out.append({
                "target_cycle_ratio": ratio,
                "heldout_family": fi,
                "family_seed": int(float(test[0]["family_seed"])),
                "n_train": len(train), "n_test": len(test),
                "base_mae": base, "ebid_mae": ebid,
                "relative_mae_reduction": gain,
                "bootstrap_ci_low": lo, "bootstrap_ci_high": hi,
                "ebid_better": int(gain > 0),
                "ci_strictly_positive": int(lo > 0),
                "ci_strictly_negative": int(hi < 0),
            })
            for r, yy, q0, q1 in zip(test, y, p0, p1):
                preds.append({
                    "target_cycle_ratio": ratio, "heldout_family": fi,
                    "sample": int(float(r["sample"])), "strength": float(r["strength"]),
                    "noise_sigma": float(r["noise_sigma"]), "replicate": int(float(r["replicate"])),
                    "future_error": float(yy), "baseline_prediction": float(q0), "ebid_prediction": float(q1),
                    "baseline_abs_error": float(abs(yy-q0)), "ebid_abs_error": float(abs(yy-q1)),
                })
    return out, preds


def bootstrap_family_mean(values, seed, n_boot=10000):
    a = np.asarray(values, dtype=float); rng = np.random.default_rng(seed); means = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(a), size=len(a))
        means.append(float(np.mean(a[idx])))
    return float(np.quantile(means, .025)), float(np.quantile(means, .975))


def aggregate(folds):
    rows = []
    for ratio in CYCLE_RATIOS:
        subset = [r for r in folds if abs(float(r["target_cycle_ratio"]) - ratio) < 1e-12]
        vals = np.asarray([float(r["relative_mae_reduction"]) for r in subset])
        lo, hi = bootstrap_family_mean(vals, SEED + 5000 + int(ratio*1000))
        rows.append({
            "target_cycle_ratio": ratio, "n_heldout_families": len(vals),
            "mean_gain": float(np.mean(vals)), "median_gain": float(np.median(vals)),
            "min_gain": float(np.min(vals)), "max_gain": float(np.max(vals)),
            "positive_families": int(np.sum(vals > 0)), "positive_fraction": float(np.mean(vals > 0)),
            "bootstrap_mean_ci_low": lo, "bootstrap_mean_ci_high": hi,
            "mean_ci_strictly_positive": int(lo > 0), "mean_ci_strictly_negative": int(hi < 0),
            "folds_ci_positive": int(sum(int(r["ci_strictly_positive"]) for r in subset)),
            "folds_ci_negative": int(sum(int(r["ci_strictly_negative"]) for r in subset)),
        })
    return rows


def compare_to_exp016(summary):
    prior_path = ROOT / "results" / "016_cross_seed_scale_map" / "scale_map.csv"
    prior = read_csv(prior_path)
    prior_map = {float(r["target_cycle_ratio"]): r for r in prior}
    out = []
    for r in summary:
        ratio = float(r["target_cycle_ratio"]); p = prior_map[ratio]
        old = float(p["mean_gain"]); new = float(r["mean_gain"])
        out.append({
            "target_cycle_ratio": ratio,
            "exp016_local_mean_gain": old,
            "exp017_leave_family_out_mean_gain": new,
            "gain_change": new - old,
            "exp016_positive_families": int(float(p["positive_families"])),
            "exp017_positive_families": int(float(r["positive_families"])),
        })
    return out


def main():
    rows = read_csv(SOURCE)
    folds, preds = evaluate_folds(rows)
    summary = aggregate(folds)
    comparison = compare_to_exp016(summary)
    write_csv(OUT / "fold_gains.csv", folds)
    write_csv(OUT / "test_predictions.csv", preds)
    write_csv(OUT / "scale_map.csv", summary)
    write_csv(OUT / "comparison_to_016.csv", comparison)
    print("LEAVE-ONE-FAMILY-OUT SCALE MAP")
    for r in summary:
        print(f"ratio={float(r['target_cycle_ratio']):.2f} mean={100*float(r['mean_gain']):+7.2f}% "
              f"positive={int(r['positive_families'])}/8 CI=[{100*float(r['bootstrap_mean_ci_low']):+.2f}%, {100*float(r['bootstrap_mean_ci_high']):+.2f}%]")


if __name__ == "__main__":
    main()
