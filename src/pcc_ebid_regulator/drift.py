"""Time-varying PCC parameter schedules for nonstationary experiments."""

from __future__ import annotations

import numpy as np


def sinusoidal_strength_schedule(
    steps: int,
    *,
    base_strength: float = 1.5,
    amplitude: float = 0.0,
    period: int = 400,
    phase: float = 0.0,
    minimum: float = 0.05,
) -> np.ndarray:
    """Return a bounded sinusoidal coupling-strength schedule."""
    if steps < 1:
        raise ValueError("steps must be >= 1")
    if period < 1:
        raise ValueError("period must be >= 1")
    t = np.arange(steps, dtype=float)
    values = base_strength + amplitude * np.sin(2.0 * np.pi * t / period + phase)
    return np.maximum(values, minimum)


def random_walk_strength_schedule(
    steps: int,
    *,
    base_strength: float = 1.5,
    innovation_std: float = 0.03,
    reversion: float = 0.02,
    minimum: float = 0.05,
    maximum: float = 3.5,
    seed: int = 0,
) -> np.ndarray:
    """Mean-reverting random walk for stochastic parameter drift."""
    if steps < 1:
        raise ValueError("steps must be >= 1")
    rng = np.random.default_rng(seed)
    values = np.empty(steps, dtype=float)
    values[0] = base_strength
    for t in range(1, steps):
        innovation = rng.normal(0.0, innovation_std)
        pull = reversion * (base_strength - values[t - 1])
        values[t] = np.clip(values[t - 1] + pull + innovation, minimum, maximum)
    return values
