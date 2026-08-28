"""Experiment 007: non-PCC compositional specificity benchmark.

Tests whether the capacity-matched 2D intervention advantage from Experiment
006 is specific to PCC/non-transitive interaction or is reproduced by a simpler
3-component compositional system with exogenous directional selection.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pcc_ebid_regulator.benchmark import cyclic_benchmark_schedule  # noqa: E402
from pcc_ebid_regulator.experiments import simulate_multichannel_benchmark_regulation  # noqa: E402
from pcc_ebid_regulator.regulators import (  # noqa: E402
    OracleFixedActionBenchmarkRegulator,
    matched_directional_repertoire,
    mean_repertoire_norm,
)

OUT = ROOT / "results" / "007_nonpcc_benchmark"
OUT.mkdir(parents=True, exist_ok=True)

STEPS = 500
BURN_IN = 180
TRUE_STRENGTH = 1.5
MAX_ACTION = 0.12
CARDINALITIES = [5, 9, 17]
DWELLS = [20, 50]
REGIME_ORDER = [
    "pressure_bias",
    "control_bias",
    "chaos_bias",
    "mixed_bias",
]
INITIALS = {
    "default": np.array([0.58, 0.27, 0.15]),
    "pressure_heavy": np.array([0.72, 0.18, 0.10]),
    "chaos_heavy": np.array([0.18, 0.22, 0.60]),
}
ONE_CHANNELS = {"P": (0,), "C": (1,), "Ch": (2,)}
TWO_CHANNELS = {"P+C": (0, 1), "P+Ch": (0, 2), "C+Ch": (1, 2)}


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_actions(channels: tuple[int, ...], cardinality: int, target_mean_norm: float | None = None):
    return matched_directional_repertoire(
        channels,
        cardinality=cardinality,
        max_action=MAX_ACTION,
        target_mean_norm=target_mean_norm,
    )


def run_sweep() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for regime_count in [1, 2, 4]:
        names = REGIME_ORDER[:regime_count]
        for dwell in DWELLS:
            schedule = cyclic_benchmark_schedule(STEPS, names, dwell=dwell)
            for cardinality in CARDINALITIES:
                reference = build_actions((1,), cardinality)
                norm_target = mean_repertoire_norm(reference)
                for initial_label, initial in INITIALS.items():
                    for dimension, families in ((1, ONE_CHANNELS), (2, TWO_CHANNELS)):
                        for channel_label, channels in families.items():
                            actions = build_actions(
                                channels,
                                cardinality,
                                target_mean_norm=norm_target if dimension == 2 else None,
                            )
                            result = simulate_multichannel_benchmark_regulation(
                                OracleFixedActionBenchmarkRegulator(
                                    actions=actions,
                                    model_strength=TRUE_STRENGTH,
                                ),
                                regime_schedule=schedule,
                                true_strength=TRUE_STRENGTH,
                                initial=initial,
                                burn_in=BURN_IN,
                            )
                            rows.append(
                                {
                                    "regime_count": regime_count,
                                    "regimes": ";".join(names),
                                    "dwell": dwell,
                                    "initial": initial_label,
                                    "dimension": dimension,
                                    "channel_label": channel_label,
                                    "candidate_actions": len(actions),
                                    "repertoire_mean_norm": mean_repertoire_norm(actions),
                                    "reference_mean_norm": norm_target,
                                    "max_action": MAX_ACTION,
                                    **result,
                                }
                            )
    return rows


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for regime_count in [1, 2, 4]:
        for dwell in DWELLS:
            for cardinality in CARDINALITIES:
                cell = [
                    r for r in rows
                    if int(r["regime_count"]) == regime_count
                    and int(r["dwell"]) == dwell
                    and int(r["candidate_actions"]) == cardinality
                ]
                for dimension in (1, 2):
                    subset = [r for r in cell if int(r["dimension"]) == dimension]
                    labels = sorted({str(r["channel_label"]) for r in subset})
                    family_stats = []
                    for label in labels:
                        vals = [float(r["mean_error"]) for r in subset if r["channel_label"] == label]
                        family_stats.append((float(np.mean(vals)), float(np.std(vals)), label))
                    mean_error, std_error, label = min(family_stats, key=lambda x: x[0])
                    output.append(
                        {
                            "regime_count": regime_count,
                            "dwell": dwell,
                            "candidate_actions": cardinality,
                            "dimension": dimension,
                            "best_channel_label": label,
                            "mean_error_across_initials": mean_error,
                            "std_error_across_initials": std_error,
                        }
                    )
    return output


def paired_advantage(summary: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for regime_count in [1, 2, 4]:
        for dwell in DWELLS:
            for cardinality in CARDINALITIES:
                one = next(r for r in summary if int(r["regime_count"]) == regime_count and int(r["dwell"]) == dwell and int(r["candidate_actions"]) == cardinality and int(r["dimension"]) == 1)
                two = next(r for r in summary if int(r["regime_count"]) == regime_count and int(r["dwell"]) == dwell and int(r["candidate_actions"]) == cardinality and int(r["dimension"]) == 2)
                e1 = float(one["mean_error_across_initials"])
                e2 = float(two["mean_error_across_initials"])
                output.append(
                    {
                        "regime_count": regime_count,
                        "dwell": dwell,
                        "candidate_actions": cardinality,
                        "best_1d": one["best_channel_label"],
                        "best_2d": two["best_channel_label"],
                        "mean_error_1d": e1,
                        "mean_error_2d": e2,
                        "absolute_improvement": e1 - e2,
                        "relative_error_reduction": (e1 - e2) / e1 if e1 > 0 else 0.0,
                    }
                )
    return output


def load_pcc_advantage() -> list[dict[str, str]]:
    path = ROOT / "results" / "006_capacity_matched_variety" / "paired_advantage.csv"
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def compare_to_pcc(benchmark: list[dict[str, object]]) -> list[dict[str, object]]:
    pcc = load_pcc_advantage()
    output: list[dict[str, object]] = []
    for b in benchmark:
        count = int(b["regime_count"])
        dwell = int(b["dwell"])
        k = int(b["candidate_actions"])
        p = next(r for r in pcc if int(r["topology_count"]) == count and int(r["dwell"]) == dwell and int(r["candidate_actions"]) == k)
        pcc_reduction = float(p["relative_error_reduction"])
        baseline_reduction = float(b["relative_error_reduction"])
        output.append(
            {
                "structural_count": count,
                "dwell": dwell,
                "candidate_actions": k,
                "pcc_1d_error": float(p["mean_error_1d"]),
                "pcc_2d_error": float(p["mean_error_2d"]),
                "pcc_relative_reduction": pcc_reduction,
                "benchmark_1d_error": float(b["mean_error_1d"]),
                "benchmark_2d_error": float(b["mean_error_2d"]),
                "benchmark_relative_reduction": baseline_reduction,
                "reduction_difference_pcc_minus_benchmark": pcc_reduction - baseline_reduction,
            }
        )
    return output


def main() -> None:
    rows = run_sweep()
    summary = summarize(rows)
    advantage = paired_advantage(summary)
    comparison = compare_to_pcc(advantage)
    write_csv(OUT / "sweep.csv", rows)
    write_csv(OUT / "best_by_dimension.csv", summary)
    write_csv(OUT / "paired_advantage.csv", advantage)
    write_csv(OUT / "pcc_vs_benchmark.csv", comparison)

    reductions = np.array([float(r["relative_error_reduction"]) for r in advantage])
    diffs = np.array([float(r["reduction_difference_pcc_minus_benchmark"]) for r in comparison])
    print("Experiment 007: non-PCC compositional specificity benchmark")
    print(f"Benchmark 2D median relative error reduction: {100*np.median(reductions):.1f}%")
    print(f"Benchmark range: {100*np.min(reductions):.1f}% to {100*np.max(reductions):.1f}%")
    print(f"Median PCC-minus-benchmark reduction difference: {100*np.median(diffs):+.1f} pp")
    print("\nMatched four-regime cells:")
    for row in comparison:
        if int(row["structural_count"]) == 4:
            print(
                f"  dwell={row['dwell']} K={row['candidate_actions']}: "
                f"PCC={100*float(row['pcc_relative_reduction']):.1f}%, "
                f"benchmark={100*float(row['benchmark_relative_reduction']):.1f}%"
            )


if __name__ == "__main__":
    main()
