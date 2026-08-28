"""Mechanism-agnostic predictive and response descriptors for simplex dynamics.

Experiment 023 uses two information sources that are distinct from EBID:
1. Predictability statistics estimated from the observed raw trajectory.
2. Small standardized counterfactual perturbations passed through a supplied
   deterministic transition function.

No Shannon-entropy or EBID quantity is computed here.
"""
from __future__ import annotations

import numpy as np


def _validate(traj: np.ndarray) -> np.ndarray:
    x = np.asarray(traj, dtype=float)
    if x.ndim != 2 or x.shape[1] != 3 or len(x) < 4:
        raise ValueError("trajectory must have shape (time>=4, 3)")
    return x


def _tangent_xy(x: np.ndarray) -> np.ndarray:
    c = x - np.full(3, 1.0 / 3.0)
    e1 = np.array([1.0, -1.0, 0.0]) / np.sqrt(2.0)
    e2 = np.array([1.0, 1.0, -2.0]) / np.sqrt(6.0)
    return np.column_stack([c @ e1, c @ e2])


def linear_forecast_error(trajectory: np.ndarray) -> float:
    """Normalized one-step error of a locally fitted linear state predictor.

    The fit is chronological: first 70% of transitions train, the remaining
    transitions evaluate. Normalization by held-out state variance makes the
    statistic comparable across dynamical classes.
    """
    z = _tangent_xy(_validate(trajectory))
    n = len(z) - 1
    if n < 5:
        return 1.0
    split = max(3, min(n - 1, int(np.floor(0.7 * n))))
    X = np.column_stack([np.ones(split), z[:split]])
    Y = z[1 : split + 1]
    beta = np.linalg.lstsq(X, Y, rcond=None)[0]
    Xt = np.column_stack([np.ones(n - split), z[split:n]])
    yt = z[split + 1 : n + 1]
    pred = Xt @ beta
    mse = float(np.mean((yt - pred) ** 2))
    scale = float(np.mean((yt - yt.mean(axis=0, keepdims=True)) ** 2))
    return float(mse / max(scale, 1e-12))


def innovation_variance(trajectory: np.ndarray) -> float:
    """Residual variance from an in-sample affine one-step predictor."""
    z = _tangent_xy(_validate(trajectory))
    X = np.column_stack([np.ones(len(z) - 1), z[:-1]])
    Y = z[1:]
    beta = np.linalg.lstsq(X, Y, rcond=None)[0]
    resid = Y - X @ beta
    return float(np.mean(resid**2))


def predictability_decay(trajectory: np.ndarray, max_lag: int = 12) -> float:
    """Rate at which tangent-coordinate autocorrelation decays with lag.

    Positive values indicate faster loss of linear predictability. The fit uses
    the log of absolute autocorrelation over available lags.
    """
    z = _tangent_xy(_validate(trajectory))
    L = min(max_lag, max(2, (len(z) - 1) // 3))
    vals = []
    lags = []
    for lag in range(1, L + 1):
        cc = []
        for j in range(2):
            a = z[:-lag, j]
            b = z[lag:, j]
            if len(a) > 2 and np.std(a) > 1e-12 and np.std(b) > 1e-12:
                cc.append(abs(float(np.corrcoef(a, b)[0, 1])))
        if cc:
            vals.append(max(np.mean(cc), 1e-8))
            lags.append(lag)
    if len(vals) < 2:
        return 0.0
    slope = np.polyfit(np.asarray(lags, float), np.log(np.asarray(vals)), 1)[0]
    return float(max(0.0, -slope))


def _project_simplex(v: np.ndarray) -> np.ndarray:
    v = np.maximum(np.asarray(v, float), 1e-12)
    return v / v.sum()


def local_response_features(
    trajectory: np.ndarray,
    transition,
    probe_eps: float = 1e-3,
    sample_points: int = 12,
) -> dict[str, float]:
    """Finite-difference response descriptors of a deterministic transition.

    ``transition(state, t)`` must return the next simplex state. Probe
    directions lie in the simplex tangent plane and are identical across
    dynamical classes.
    """
    x = _validate(trajectory)
    if probe_eps <= 0:
        raise ValueError("probe_eps must be positive")
    e1 = np.array([1.0, -1.0, 0.0]) / np.sqrt(2.0)
    e2 = np.array([1.0, 1.0, -2.0]) / np.sqrt(6.0)
    dirs = (e1, e2)
    idx = np.unique(np.linspace(0, len(x) - 2, min(sample_points, len(x) - 1), dtype=int))
    jac_norms = []
    amps = []
    anis = []
    for t in idx:
        state = x[t]
        base = np.asarray(transition(state, int(t)), float)
        cols = []
        local_amp = []
        for d in dirs:
            zp = _project_simplex(state + probe_eps * d)
            zm = _project_simplex(state - probe_eps * d)
            fp = np.asarray(transition(zp, int(t)), float)
            fm = np.asarray(transition(zm, int(t)), float)
            deriv = (fp - fm) / (2.0 * probe_eps)
            cols.append(deriv)
            din = np.linalg.norm(zp - state)
            dout = np.linalg.norm(fp - base)
            local_amp.append(float(dout / max(din, 1e-12)))
        J = np.column_stack(cols)
        svals = np.linalg.svd(J, compute_uv=False)
        jac_norms.append(float(np.linalg.norm(J, ord="fro")))
        amps.append(float(np.mean(local_amp)))
        anis.append(float(svals[0] / max(svals[-1], 1e-8)))
    return {
        "resp_jacobian_fro_mean": float(np.mean(jac_norms)),
        "resp_jacobian_fro_sd": float(np.std(jac_norms)),
        "resp_perturbation_amplification_mean": float(np.mean(amps)),
        "resp_perturbation_amplification_sd": float(np.std(amps)),
        "resp_local_anisotropy_mean": float(np.mean(anis)),
    }


def response_invariants(trajectory: np.ndarray, transition) -> dict[str, float]:
    """Combined path-predictability and standardized response features."""
    out = {
        "resp_linear_forecast_error": linear_forecast_error(trajectory),
        "resp_innovation_variance": innovation_variance(trajectory),
        "resp_predictability_decay": predictability_decay(trajectory),
    }
    out.update(local_response_features(trajectory, transition))
    return out
