"""Externally forced oscillatory simplex dynamics for PCC specificity controls.

These dynamics are intentionally non-PCC: the composition responds to a time-varying
exogenous bias vector. There are no endogenous pairwise dominance terms and no
rock-paper-scissors interaction matrix. The forcing period can be matched to the
intrinsic PCC period to isolate generic oscillation from PCC structure.
"""
from __future__ import annotations

import numpy as np

REGIMES = ("circular", "reverse", "elliptic", "harmonic")
_E1 = np.array([1.0, -0.5, -0.5], dtype=float)
_E2 = np.array([0.0, np.sqrt(3.0)/2.0, -np.sqrt(3.0)/2.0], dtype=float)


def oscillatory_bias(t: int, *, period: float, regime: str = "circular") -> np.ndarray:
    """Return a zero-sum exogenous oscillatory bias vector."""
    if period <= 0:
        raise ValueError("period must be positive")
    if regime not in REGIMES:
        raise ValueError(f"unknown oscillatory benchmark regime: {regime}")
    theta = 2.0 * np.pi * float(t) / float(period)
    if regime == "circular":
        a, b = np.cos(theta), np.sin(theta)
    elif regime == "reverse":
        a, b = np.cos(theta), -np.sin(theta)
    elif regime == "elliptic":
        a, b = np.cos(theta), 0.55 * np.sin(theta)
    else:  # harmonic
        a = 0.75 * np.cos(theta) + 0.25 * np.cos(2.0 * theta)
        b = 0.75 * np.sin(theta) - 0.25 * np.sin(2.0 * theta)
    return a * _E1 + b * _E2


def oscillatory_step(
    state: np.ndarray,
    *,
    t: int,
    period: float,
    regime: str = "circular",
    dt: float = 0.02,
    strength: float = 1.5,
) -> np.ndarray:
    """Advance one replicator-like step under exogenous periodic forcing."""
    x = np.asarray(state, dtype=float)
    if x.shape != (3,):
        raise ValueError("state must have shape (3,)")
    bias = oscillatory_bias(t, period=period, regime=regime)
    mean_bias = float(x @ bias)
    dx = strength * x * (bias - mean_bias)
    nxt = x + dt * dx
    nxt = np.clip(nxt, 1e-12, None)
    return nxt / nxt.sum()


def oscillatory_activity(
    state: np.ndarray,
    *,
    t: int,
    period: float,
    regime: str,
    strength: float,
) -> float:
    """Generic instantaneous forcing activity, not an EBID feature."""
    x = np.asarray(state, dtype=float)
    b = oscillatory_bias(t, period=period, regime=regime)
    mean_bias = float(x @ b)
    dx = strength * x * (b - mean_bias)
    return float(np.linalg.norm(dx))
