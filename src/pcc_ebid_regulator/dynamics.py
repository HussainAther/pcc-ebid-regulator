"""Minimal PCC dynamics used by the regulator experiments."""

from __future__ import annotations

import numpy as np

from .topology import topology_matrix


def step(
    state: np.ndarray,
    dt: float = 0.02,
    strength: float = 1.0,
    topology: str = "canonical",
) -> np.ndarray:
    """Advance a normalized three-state interaction system by one Euler step.

    State order is [Pressure, Control, Chaos]. ``canonical`` exactly reproduces
    the original toy PCC equations. Other named topologies are used only for
    structural-variety experiments and are not asserted as canonical PCC.
    """
    x = np.asarray(state, dtype=float)
    matrix = topology_matrix(topology)
    fitness = matrix @ x
    mean_fitness = float(x @ fitness)
    dx = strength * x * (fitness - mean_fitness)
    nxt = x + dt * dx
    nxt = np.clip(nxt, 1e-12, None)
    return nxt / nxt.sum()


def simulate(
    initial: np.ndarray,
    steps: int,
    dt: float = 0.02,
    strength: float = 1.0,
    topology: str = "canonical",
) -> np.ndarray:
    trajectory = np.empty((steps + 1, 3), dtype=float)
    trajectory[0] = np.asarray(initial, dtype=float) / np.sum(initial)
    for t in range(steps):
        trajectory[t + 1] = step(
            trajectory[t], dt=dt, strength=strength, topology=topology
        )
    return trajectory
