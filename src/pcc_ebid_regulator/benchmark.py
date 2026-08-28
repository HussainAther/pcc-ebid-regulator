"""Non-PCC compositional benchmark dynamics for specificity controls.

The benchmark lives on the same 3-component simplex as PCC but removes
endogenous pairwise/cyclic interaction. Each named regime supplies a fixed
exogenous fitness/bias vector, yielding ordinary directional selection.
"""

from __future__ import annotations

import numpy as np

_BIASES: dict[str, np.ndarray] = {
    "pressure_bias": np.array([1.0, -0.5, -0.5], dtype=float),
    "control_bias": np.array([-0.5, 1.0, -0.5], dtype=float),
    "chaos_bias": np.array([-0.5, -0.5, 1.0], dtype=float),
    "mixed_bias": np.array([0.75, 0.25, -1.0], dtype=float),
}


def benchmark_bias(name: str) -> np.ndarray:
    """Return a copy of a named exogenous compositional bias vector."""
    try:
        return _BIASES[name].copy()
    except KeyError as exc:
        raise ValueError(f"unknown benchmark regime: {name}") from exc


def benchmark_step(
    state: np.ndarray,
    *,
    regime: str = "pressure_bias",
    dt: float = 0.02,
    strength: float = 1.5,
) -> np.ndarray:
    """Advance non-interacting directional-selection dynamics one Euler step."""
    x = np.asarray(state, dtype=float)
    if x.shape != (3,):
        raise ValueError("state must have shape (3,)")
    bias = benchmark_bias(regime)
    mean_bias = float(x @ bias)
    dx = strength * x * (bias - mean_bias)
    nxt = x + dt * dx
    nxt = np.clip(nxt, 1e-12, None)
    return nxt / nxt.sum()


def cyclic_benchmark_schedule(
    steps: int,
    names: list[str] | tuple[str, ...],
    *,
    dwell: int = 50,
) -> list[str]:
    """Cycle through exogenous benchmark regimes."""
    if steps < 1:
        raise ValueError("steps must be >= 1")
    if dwell < 1:
        raise ValueError("dwell must be >= 1")
    if not names:
        raise ValueError("names must be non-empty")
    for name in names:
        benchmark_bias(name)
    return [names[(t // dwell) % len(names)] for t in range(steps)]
