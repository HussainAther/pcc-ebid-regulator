"""Mechanism-agnostic descriptors of raw trajectories on the 3-simplex.

These descriptors deliberately avoid Shannon entropy / EBID quantities. They are
used prospectively in Experiment 022 to ask whether geometric and temporal path
structure predicts when frozen EBID features improve regulator-demand prediction.
"""
from __future__ import annotations

import numpy as np


def _validate(trajectory: np.ndarray) -> np.ndarray:
    x = np.asarray(trajectory, dtype=float)
    if x.ndim != 2 or x.shape[1] != 3 or len(x) < 2:
        raise ValueError("trajectory must have shape (time>=2, 3)")
    return x


def _tangent_xy(x: np.ndarray) -> np.ndarray:
    c = x - np.full(3, 1.0 / 3.0)
    e1 = np.array([1.0, -1.0, 0.0]) / np.sqrt(2.0)
    e2 = np.array([1.0, 1.0, -2.0]) / np.sqrt(6.0)
    return np.column_stack([c @ e1, c @ e2])


def path_length(trajectory: np.ndarray) -> float:
    x = _validate(trajectory)
    return float(np.linalg.norm(np.diff(x, axis=0), axis=1).sum())


def recurrence_rate(trajectory: np.ndarray, radius: float = 0.04, max_points: int = 80) -> float:
    """Fraction of non-neighbor sampled state pairs closer than ``radius``."""
    x = _validate(trajectory)
    if radius <= 0:
        raise ValueError("radius must be positive")
    idx = np.unique(np.linspace(0, len(x)-1, min(max_points, len(x)), dtype=int))
    z = x[idx]
    if len(z) < 4:
        return 0.0
    d = np.linalg.norm(z[:, None, :] - z[None, :, :], axis=2)
    # A recurrence should be a return after meaningful elapsed time, not merely
    # the local continuity of a slowly moving path. Exclude the nearest quarter
    # of the sampled trajectory in time.
    min_lag = max(3, len(z) // 4)
    ii, jj = np.triu_indices(len(z), k=min_lag)
    return float(np.mean(d[ii, jj] < radius)) if len(ii) else 0.0


def lag1_autocorrelation(trajectory: np.ndarray) -> float:
    """Mean lag-1 autocorrelation across tangent-plane coordinates."""
    z = _tangent_xy(_validate(trajectory))
    vals = []
    for j in range(2):
        a = z[:-1, j]; b = z[1:, j]
        if np.std(a) > 1e-12 and np.std(b) > 1e-12:
            vals.append(float(np.corrcoef(a, b)[0, 1]))
    return float(np.mean(vals)) if vals else 0.0


def spectral_concentration(trajectory: np.ndarray) -> float:
    """Largest non-DC Fourier power fraction of the 2D tangent trajectory."""
    z = _tangent_xy(_validate(trajectory))
    z = z - z.mean(axis=0, keepdims=True)
    if len(z) < 4:
        return 0.0
    spec = np.fft.rfft(z, axis=0)
    power = np.sum(np.abs(spec) ** 2, axis=1)
    if len(power) <= 1:
        return 0.0
    p = power[1:]
    total = float(p.sum())
    return float(p.max() / total) if total > 1e-15 else 0.0


def turning_persistence(trajectory: np.ndarray) -> float:
    """Mean cosine between consecutive nonzero displacement vectors."""
    x = _validate(trajectory)
    v = np.diff(_tangent_xy(x), axis=0)
    n = np.linalg.norm(v, axis=1)
    good = n > 1e-12
    v = v[good]; n = n[good]
    if len(v) < 2:
        return 0.0
    cos = np.sum(v[:-1] * v[1:], axis=1) / (n[:-1] * n[1:])
    return float(np.mean(np.clip(cos, -1.0, 1.0)))


def occupancy_fraction(trajectory: np.ndarray, bins: int = 8) -> float:
    """Fraction of a fixed tangent-plane grid visited by the path."""
    if bins < 2:
        raise ValueError("bins must be >= 2")
    z = _tangent_xy(_validate(trajectory))
    # All simplex states lie inside roughly [-0.71,0.71] in these coordinates.
    lo, hi = -0.75, 0.75
    q = np.floor((np.clip(z, lo, hi - 1e-12) - lo) / (hi - lo) * bins).astype(int)
    cells = set(map(tuple, q))
    return float(len(cells) / (bins * bins))


def raw_path_features(trajectory: np.ndarray) -> dict[str, float]:
    x = _validate(trajectory)
    plen = path_length(x)
    net = float(np.linalg.norm(x[-1] - x[0]))
    return {
        "raw_path_length": plen,
        "raw_net_displacement": net,
        "raw_path_efficiency": float(net / plen) if plen > 1e-15 else 0.0,
        "raw_recurrence_rate": recurrence_rate(x),
        "raw_lag1_autocorrelation": lag1_autocorrelation(x),
        "raw_spectral_concentration": spectral_concentration(x),
        "raw_turning_persistence": turning_persistence(x),
        "raw_occupancy_fraction": occupancy_fraction(x),
    }
