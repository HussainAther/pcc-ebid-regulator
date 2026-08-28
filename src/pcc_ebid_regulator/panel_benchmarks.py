"""Additional non-PCC dynamical classes for Experiment 020.

The classes here are intentionally simple controls on the same three-component
simplex. They are not PCC models and contain no endogenous pairwise dominance.
"""
from __future__ import annotations

import numpy as np

from .oscillatory_benchmark import oscillatory_bias

DAMPED_REGIMES = ("circular", "reverse", "elliptic", "harmonic")
NEUTRAL_REGIMES = ("neutral_a", "neutral_b", "neutral_c", "neutral_d")


def damped_oscillatory_step(
    state: np.ndarray,
    *,
    t: int,
    period: float,
    regime: str = "circular",
    dt: float = 0.02,
    strength: float = 1.5,
    damping_cycles: float = 0.75,
) -> np.ndarray:
    """Externally forced oscillation whose forcing amplitude decays exponentially."""
    if damping_cycles <= 0:
        raise ValueError("damping_cycles must be positive")
    x = np.asarray(state, dtype=float)
    if x.shape != (3,):
        raise ValueError("state must have shape (3,)")
    if regime not in DAMPED_REGIMES:
        raise ValueError(f"unknown damped regime: {regime}")
    envelope = float(np.exp(-float(t) / (damping_cycles * float(period))))
    bias = envelope * oscillatory_bias(t, period=period, regime=regime)
    mean_bias = float(x @ bias)
    dx = strength * x * (bias - mean_bias)
    nxt = np.clip(x + dt * dx, 1e-12, None)
    return nxt / nxt.sum()


def damped_activity(
    state: np.ndarray,
    *,
    t: int,
    period: float,
    regime: str,
    strength: float,
    damping_cycles: float = 0.75,
) -> float:
    """Instantaneous deterministic activity of the damped forcing."""
    x = np.asarray(state, dtype=float)
    envelope = float(np.exp(-float(t) / (damping_cycles * float(period))))
    bias = envelope * oscillatory_bias(t, period=period, regime=regime)
    mean_bias = float(x @ bias)
    dx = strength * x * (bias - mean_bias)
    return float(np.linalg.norm(dx))


def neutral_step(state: np.ndarray, *, regime: str = "neutral_a") -> np.ndarray:
    """Identity deterministic dynamics; stochasticity is supplied separately."""
    if regime not in NEUTRAL_REGIMES:
        raise ValueError(f"unknown neutral regime: {regime}")
    x = np.asarray(state, dtype=float)
    if x.shape != (3,):
        raise ValueError("state must have shape (3,)")
    y = np.clip(x, 1e-12, None)
    return y / y.sum()


def neutral_activity(state: np.ndarray, *, regime: str = "neutral_a") -> float:
    """No deterministic activity by construction."""
    neutral_step(state, regime=regime)
    return 0.0
