"""Minimal PCC dynamics used by the first regulator experiments."""

from __future__ import annotations

import numpy as np


def step(state: np.ndarray, dt: float = 0.02, strength: float = 1.0) -> np.ndarray:
    """Advance a normalized three-state cyclic system by one Euler step.

    State order is [Pressure, Control, Chaos]. The interaction signs encode:
    Control suppresses Pressure, Pressure suppresses Chaos, Chaos disrupts Control.
    The model is intentionally minimal and is not asserted to be a canonical PCC equation.
    """
    p, c, ch = np.asarray(state, dtype=float)
    dp = strength * p * (ch - c)
    dc = strength * c * (p - ch)
    dch = strength * ch * (c - p)
    x = np.array([p + dt * dp, c + dt * dc, ch + dt * dch])
    x = np.clip(x, 1e-12, None)
    return x / x.sum()


def simulate(initial: np.ndarray, steps: int, dt: float = 0.02, strength: float = 1.0) -> np.ndarray:
    trajectory = np.empty((steps + 1, 3), dtype=float)
    trajectory[0] = np.asarray(initial, dtype=float) / np.sum(initial)
    for t in range(steps):
        trajectory[t + 1] = step(trajectory[t], dt=dt, strength=strength)
    return trajectory
