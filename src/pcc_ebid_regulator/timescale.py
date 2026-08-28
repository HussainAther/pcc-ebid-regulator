"""Cycle-timescale diagnostics for PCC trajectories."""
from __future__ import annotations

import numpy as np
from .signals import simplex_phase


def phase_cycle_period(trajectory: np.ndarray, *, min_turns: float = 0.75) -> float:
    """Estimate period in simulation steps from unwrapped simplex phase.

    Returns NaN when the trajectory does not traverse enough angular distance
    to support a cycle estimate. This is a diagnostic, not an EBID feature.
    """
    x = np.asarray(trajectory, dtype=float)
    if x.ndim != 2 or x.shape[1] != 3 or len(x) < 3:
        raise ValueError("trajectory must have shape (time, 3) with >=3 rows")
    phase = np.unwrap(np.asarray([simplex_phase(s) for s in x], dtype=float))
    turns = abs(float(phase[-1] - phase[0])) / (2.0 * np.pi)
    if turns < min_turns:
        return float("nan")
    t = np.arange(len(phase), dtype=float)
    slope = float(np.polyfit(t, phase, 1)[0])
    if abs(slope) < 1e-12:
        return float("nan")
    return float(2.0 * np.pi / abs(slope))
