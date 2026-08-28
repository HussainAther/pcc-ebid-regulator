"""Experiment 006: capacity-matched intervention dimensionality.

Experiment 005 allowed multi-channel regulators to have larger raw action sets.
This experiment removes that confound by matching:

1. candidate-action cardinality, and
2. mean L2 intervention norm

between one-channel and two-channel repertoires. All regulators retain oracle
knowledge of the currently active topology so the comparison isolates action
geometry rather than model uncertainty.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pcc_ebid_regulator.experiments import simulate_multichannel_topology_regulation  # noqa: E402
from pcc_ebid_regulator.regulators import (  # noqa: E402
    OracleFixedActionTopologyRegulator,
    matched_directional_repertoire,
    mean_repertoire_norm,
)
from pcc_ebid_regulator.topology import cyclic_topology_schedule  # noqa: E402

OUT = ROOT / "results" / "006_capacity_matched_variety"
OUT.mkdir(parents=True, exist_ok=True)

STEPS = 500
BURN_IN = 180
TRUE_STRENGTH = 1.5
MAX_ACTION = 0.12
CARDINALITIES = [5, 9, 17]
DWELLS = [20, 50]
TOPOLOGY_ORDER = [
    "canonical",
    "reverse",
    "no_pressure_control",
    "no_control_chaos",
]
INITIALS = {
    "default": np.array([0.58, 0.27, 0.15]),
    "pressure_heavy": np.array([0.72, 0.18, 0.10]),
    "chaos_heavy": np.array([0.18, 0.22, 0.60]),
}
ONE_CHANNELS = {
    "P": (0,),
    "C": (1,),
    "Ch": (2,),
}
TWO_CHANNELS = {
    "P+C": (0, 1),
    "P+Ch": (0, 2),
    "C+Ch": (1, 2),
}


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
    for topology_count in [1, 2, 4]:
        names = TOPOLOGY_ORDER[:topology_count]
        for dwell in DWELLS:
            schedule = cyclic_topology_schedule(STEPS, names, dwell=dwell)
            for cardinality in CARDINALITIES:
                # Mean norm target comes from the one-dimensional scalar set.
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
                            result = simulate_multichannel_topology_regulation(
                                OracleFixedActionTopologyRegulator(
                                    actions=actions,
                                    model_strength=TRUE_STRENGTH,
                                ),
                                topology_schedule=schedule,
                                true_strength=TRUE_STRENGTH,
                                initial=initial,
                                burn_in=BURN_IN,
                            )
                            rows.append(
                                {
                                    "topology_count": topology_count,
                                    "topologies": ";".join(names),
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
    for topology_count in [1, 2, 4]:
        for dwell in DWELLS:
            for cardinality in CARDINALITIES:
                cell = [
                    r for r in rows
                    if int(r["topology_count"]) == topology_count
                    and int(r["dwell"]) == dwell
                    and int(r["candidate_actions"]) == cardinality
                ]
                for dimension in (1, 2):
                    subset = [r for r in cell if int(r["dimension"]) == dimension]
                    # Aggregate each channel family over all initial conditions,
                    # then choose the best family within each dimensionality.
                    labels = sorted({str(r["channel_label"]) for r in subset})
                    family_stats = []
                    for label in labels:
                        vals = [float(r["mean_error"]) for r in subset if r["channel_label"] == label]
                        family_stats.append((float(np.mean(vals)), float(np.std(vals)), label))
                    mean_error, std_error, label = min(family_stats, key=lambda x: x[0])
                    output.append(
                        {
                            "topology_count": topology_count,
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
    for topology_count in [1, 2, 4]:
        for dwell in DWELLS:
            for cardinality in CARDINALITIES:
                one = next(
                    r for r in summary
                    if int(r["topology_count"]) == topology_count
                    and int(r["dwell"]) == dwell
                    and int(r["candidate_actions"]) == cardinality
                    and int(r["dimension"]) == 1
                )
                two = next(
                    r for r in summary
                    if int(r["topology_count"]) == topology_count
                    and int(r["dwell"]) == dwell
                    and int(r["candidate_actions"]) == cardinality
                    and int(r["dimension"]) == 2
                )
                e1 = float(one["mean_error_across_initials"])
                e2 = float(two["mean_error_across_initials"])
                output.append(
                    {
                        "topology_count": topology_count,
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


def main() -> None:
    rows = run_sweep()
    summary = summarize(rows)
    advantage = paired_advantage(summary)
    write_csv(OUT / "sweep.csv", rows)
    write_csv(OUT / "best_by_dimension.csv", summary)
    write_csv(OUT / "paired_advantage.csv", advantage)

    print("Experiment 006: capacity-matched intervention dimensionality")
    print("Matched candidate-action cardinality and mean L2 repertoire norm")
    print("Averaged across 3 initial conditions; oracle topology knowledge")
    for cardinality in CARDINALITIES:
        vals = [r for r in advantage if int(r["candidate_actions"]) == cardinality]
        reductions = [float(r["relative_error_reduction"]) for r in vals]
        print(
            f"K={cardinality}: median 2D relative error reduction="
            f"{100*np.median(reductions):.1f}% "
            f"(min={100*np.min(reductions):.1f}%, max={100*np.max(reductions):.1f}%)"
        )

    print("\nFour-topology cells:")
    for row in advantage:
        if int(row["topology_count"]) == 4:
            print(
                f"  dwell={row['dwell']} K={row['candidate_actions']}: "
                f"1D {row['best_1d']}={float(row['mean_error_1d']):.6f}, "
                f"2D {row['best_2d']}={float(row['mean_error_2d']):.6f}, "
                f"reduction={100*float(row['relative_error_reduction']):.1f}%"
            )


if __name__ == "__main__":
    main()
