"""Experiment 005: multi-channel requisite variety under topology switching.

This experiment changes the definition of regulator variety. Instead of finer
resolution on a single Control scalar, the regulator receives access to one,
two, or three component-specific intervention channels: Pressure, Control,
and Chaos. The controller is granted oracle knowledge of the active topology,
so the sweep isolates intervention access rather than model uncertainty.

Because PCC state is compositional (P + C + Ch = 1), the intervention space
has at most two independent relative directions. Three-channel access is kept
as an explicit saturation/redundancy check rather than assumed to add a third
independent degree of freedom.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pcc_ebid_regulator.experiments import simulate_multichannel_topology_regulation  # noqa: E402
from pcc_ebid_regulator.regulators import OracleMultiChannelTopologyRegulator  # noqa: E402
from pcc_ebid_regulator.topology import cyclic_topology_schedule  # noqa: E402

OUT = ROOT / "results" / "005_multichannel_variety"
OUT.mkdir(parents=True, exist_ok=True)

STEPS = 800
BURN_IN = 300
TRUE_STRENGTH = 1.5
MAX_ACTION = 0.12
DWELLS = [20, 50, 100]
ERROR_CRITERIA = [0.200, 0.100, 0.050, 0.030, 0.020, 0.015, 0.010]
TOPOLOGY_ORDER = [
    "canonical",
    "reverse",
    "no_pressure_control",
    "no_control_chaos",
]
CHANNEL_SETS = {
    "P": (0,),
    "C": (1,),
    "Ch": (2,),
    "P+C": (0, 1),
    "P+Ch": (0, 2),
    "C+Ch": (1, 2),
    "P+C+Ch": (0, 1, 2),
}


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run_sweep() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for topology_count in range(1, len(TOPOLOGY_ORDER) + 1):
        names = TOPOLOGY_ORDER[:topology_count]
        for dwell in DWELLS:
            schedule = cyclic_topology_schedule(STEPS, names, dwell=dwell)
            for channel_label, channels in CHANNEL_SETS.items():
                regulator = OracleMultiChannelTopologyRegulator(
                    channels=channels,
                    model_strength=TRUE_STRENGTH,
                    max_action=MAX_ACTION,
                )
                result = simulate_multichannel_topology_regulation(
                    regulator,
                    topology_schedule=schedule,
                    true_strength=TRUE_STRENGTH,
                    burn_in=BURN_IN,
                )
                rows.append(
                    {
                        "topology_count": topology_count,
                        "topologies": ";".join(names),
                        "dwell": dwell,
                        "channel_label": channel_label,
                        "channel_count": len(channels),
                        "candidate_actions": 3 ** len(channels),
                        "max_action": MAX_ACTION,
                        **result,
                    }
                )
    return rows


def summarize_best(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for topology_count in range(1, 5):
        for dwell in DWELLS:
            cell = [
                r for r in rows
                if int(r["topology_count"]) == topology_count and int(r["dwell"]) == dwell
            ]
            for channel_count in (1, 2, 3):
                subset = [r for r in cell if int(r["channel_count"]) == channel_count]
                best = min(subset, key=lambda r: float(r["mean_error"]))
                output.append(
                    {
                        "topology_count": topology_count,
                        "dwell": dwell,
                        "channel_count": channel_count,
                        "best_channel_label": best["channel_label"],
                        "best_mean_error": float(best["mean_error"]),
                        "best_p95_error": float(best["p95_error"]),
                        "best_max_error": float(best["max_error"]),
                    }
                )
    return output


def summarize_thresholds(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for topology_count in range(1, 5):
        for dwell in DWELLS:
            cell = [
                r for r in rows
                if int(r["topology_count"]) == topology_count and int(r["dwell"]) == dwell
            ]
            for criterion in ERROR_CRITERIA:
                passing = [r for r in cell if float(r["mean_error"]) <= criterion]
                min_channels = min((int(r["channel_count"]) for r in passing), default=-1)
                best_label = ""
                if passing:
                    eligible = [r for r in passing if int(r["channel_count"]) == min_channels]
                    best_label = str(min(eligible, key=lambda r: float(r["mean_error"]))["channel_label"])
                output.append(
                    {
                        "topology_count": topology_count,
                        "dwell": dwell,
                        "error_criterion": criterion,
                        "minimum_channel_count": min_channels,
                        "best_minimum_channel_set": best_label,
                    }
                )
    return output



def run_amplitude_sensitivity() -> list[dict[str, object]]:
    """Check whether the channel-dimensionality result survives action scale changes."""
    rows: list[dict[str, object]] = []
    names = TOPOLOGY_ORDER
    for max_action in [0.03, 0.06, 0.09, 0.12]:
        for dwell in [50]:
            schedule = cyclic_topology_schedule(STEPS, names, dwell=dwell)
            sensitivity_sets = {
                "C": CHANNEL_SETS["C"],
                "P+Ch": CHANNEL_SETS["P+Ch"],
                "P+C+Ch": CHANNEL_SETS["P+C+Ch"],
            }
            for channel_label, channels in sensitivity_sets.items():
                result = simulate_multichannel_topology_regulation(
                    OracleMultiChannelTopologyRegulator(
                        channels=channels,
                        model_strength=TRUE_STRENGTH,
                        max_action=max_action,
                    ),
                    topology_schedule=schedule,
                    true_strength=TRUE_STRENGTH,
                    burn_in=BURN_IN,
                )
                rows.append(
                    {
                        "max_action": max_action,
                        "dwell": dwell,
                        "channel_label": channel_label,
                        "channel_count": len(channels),
                        **result,
                    }
                )
    return rows

def main() -> None:
    rows = run_sweep()
    best = summarize_best(rows)
    thresholds = summarize_thresholds(rows)
    sensitivity = run_amplitude_sensitivity()
    write_csv(OUT / "sweep.csv", rows)
    write_csv(OUT / "best_by_dimension.csv", best)
    write_csv(OUT / "thresholds.csv", thresholds)
    write_csv(OUT / "amplitude_sensitivity.csv", sensitivity)

    print("Experiment 005: multi-channel regulator variety")
    print(f"max_action={MAX_ACTION:.3f}; oracle active-topology knowledge")
    print("\nBest mean error by topology count, dwell, and channel dimension:")
    for dwell in DWELLS:
        print(f"dwell={dwell}")
        for count in range(1, 5):
            vals = [
                r for r in best
                if int(r["topology_count"]) == count and int(r["dwell"]) == dwell
            ]
            text = ", ".join(
                f"{int(r['channel_count'])}ch {r['best_channel_label']}={float(r['best_mean_error']):.6f}"
                for r in vals
            )
            print(f"  topologies={count}: {text}")

    print("\nMinimum channel count at criterion=0.100:")
    for dwell in DWELLS:
        vals = []
        for count in range(1, 5):
            row = next(
                r for r in thresholds
                if int(r["topology_count"]) == count
                and int(r["dwell"]) == dwell
                and float(r["error_criterion"]) == 0.100
            )
            vals.append((int(row["minimum_channel_count"]), row["best_minimum_channel_set"]))
        print(f"  dwell={dwell}: {vals}")


if __name__ == "__main__":
    main()
