"""Named PCC interaction topologies for structural-variety experiments.

The matrices are antisymmetric interaction matrices for a three-state
replicator-like system ordered as [Pressure, Control, Chaos].  They are toy
regimes, not asserted as canonical PCC equations.
"""

from __future__ import annotations

import numpy as np


TOPOLOGIES: dict[str, np.ndarray] = {
    # Baseline used by the original PCC toy model.
    "canonical": np.array(
        [
            [0.0, -1.0, 1.0],
            [1.0, 0.0, -1.0],
            [-1.0, 1.0, 0.0],
        ]
    ),
    # Reverse every interaction direction.
    "reverse": np.array(
        [
            [0.0, 1.0, -1.0],
            [-1.0, 0.0, 1.0],
            [1.0, -1.0, 0.0],
        ]
    ),
    # Remove direct Pressure-Control coupling.
    "no_pressure_control": np.array(
        [
            [0.0, 0.0, 1.0],
            [0.0, 0.0, -1.0],
            [-1.0, 1.0, 0.0],
        ]
    ),
    # Remove direct Control-Chaos coupling.
    "no_control_chaos": np.array(
        [
            [0.0, -1.0, 1.0],
            [1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0],
        ]
    ),
}


def topology_matrix(name: str) -> np.ndarray:
    """Return a copy of a named topology matrix."""
    try:
        return TOPOLOGIES[name].copy()
    except KeyError as exc:
        raise ValueError(f"unknown topology: {name}") from exc


def cyclic_topology_schedule(
    steps: int,
    names: list[str] | tuple[str, ...],
    *,
    dwell: int = 50,
) -> list[str]:
    """Cycle through topology names, holding each for ``dwell`` time steps."""
    if steps < 1:
        raise ValueError("steps must be >= 1")
    if dwell < 1:
        raise ValueError("dwell must be >= 1")
    if not names:
        raise ValueError("names must be non-empty")
    for name in names:
        topology_matrix(name)  # validate
    return [names[(t // dwell) % len(names)] for t in range(steps)]
