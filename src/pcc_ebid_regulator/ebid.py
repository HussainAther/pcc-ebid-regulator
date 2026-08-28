"""Frozen entropy-rate feature construction from the parent EBID work.

The parent manuscript defines Shannon entropy H(t) and entropy deficit
D(t)=log(3)-H(t), then extracts finite-time entropy/deficit rate features from
an early observation window.  This module ports that feature family without
outcome-driven changes for Experiment 009.
"""

from __future__ import annotations

import numpy as np


LOG3 = float(np.log(3.0))
EQUILIBRIUM = np.full(3, 1.0 / 3.0)


def shannon_entropy_trajectory(trajectory: np.ndarray) -> np.ndarray:
    """Raw Shannon entropy H(t) for a 3-component simplex trajectory."""
    x = np.asarray(trajectory, dtype=float)
    if x.ndim != 2 or x.shape[1] != 3:
        raise ValueError("trajectory must have shape (time, 3)")
    safe = np.clip(x, 1e-15, 1.0)
    return -np.sum(safe * np.log(safe), axis=1)


def _slope(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    if values.size < 2:
        return 0.0
    t = np.arange(values.size, dtype=float)
    return float(np.polyfit(t, values, 1)[0])


def canonical_ebid_features(trajectory: np.ndarray) -> dict[str, float]:
    """Return the frozen canonical entropy-rate feature family.

    Feature names follow the parent manuscript's stated early-window set:
    initial entropy, mean entropy, end-window entropy, entropy drop, entropy
    slope, mean entropy rate, minimum entropy rate, entropy-rate variance,
    deficit growth, maximum deficit rate, and deficit-rate variance.
    Finite differences use one simulation step as the time unit.
    """
    h = shannon_entropy_trajectory(trajectory)
    d = LOG3 - h
    dh = np.diff(h)
    dd = np.diff(d)
    return {
        "ebid_initial_entropy": float(h[0]),
        "ebid_mean_entropy": float(np.mean(h)),
        "ebid_end_entropy": float(h[-1]),
        "ebid_entropy_drop": float(h[0] - h[-1]),
        "ebid_entropy_slope": _slope(h),
        "ebid_mean_entropy_rate": float(np.mean(dh)) if dh.size else 0.0,
        "ebid_min_entropy_rate": float(np.min(dh)) if dh.size else 0.0,
        "ebid_entropy_rate_variance": float(np.var(dh)) if dh.size else 0.0,
        "ebid_deficit_growth": float(d[-1] - d[0]),
        "ebid_max_deficit_rate": float(np.max(dd)) if dd.size else 0.0,
        "ebid_deficit_rate_variance": float(np.var(dd)) if dd.size else 0.0,
    }


def quadratic_rate_features(trajectory: np.ndarray) -> dict[str, float]:
    """Matched quadratic-distance trajectory baseline from the EBID manuscript."""
    x = np.asarray(trajectory, dtype=float)
    if x.ndim != 2 or x.shape[1] != 3:
        raise ValueError("trajectory must have shape (time, 3)")
    q = np.sum((x - EQUILIBRIUM) ** 2, axis=1)
    dq = np.diff(q)
    return {
        "quad_initial": float(q[0]),
        "quad_mean": float(np.mean(q)),
        "quad_end": float(q[-1]),
        "quad_growth": float(q[-1] - q[0]),
        "quad_slope": _slope(q),
        "quad_mean_rate": float(np.mean(dq)) if dq.size else 0.0,
        "quad_min_rate": float(np.min(dq)) if dq.size else 0.0,
        "quad_max_rate": float(np.max(dq)) if dq.size else 0.0,
        "quad_rate_variance": float(np.var(dq)) if dq.size else 0.0,
    }
