# Experiment 023 — predictive / response invariants

## Question

Can trajectory-level predictability and standardized response probes explain when frozen canonical EBID will improve future regulator-demand prediction in a **dynamical class that was never represented during calibration**?

This experiment follows the negative raw-path-morphology result in Experiment 022. It reuses the same prospective five-class panel and the same held-out-family EBID gains, but augments each retained observation path with non-EBID response descriptors:

- chronological one-step linear forecast error,
- innovation variance,
- autocorrelation / predictability decay,
- finite-difference local Jacobian norm,
- perturbation amplification,
- local response anisotropy.

The finite-difference probes use the same two tangent-plane directions and perturbation size for every system. No future regulation target and no Shannon-entropy / EBID quantity is used to construct these descriptors.

## Primary leave-one-dynamical-class-out result

| Held-out class | Response-invariant MAE change vs scale-only |
|---|---:|
| PCC | -97.6% |
| Persistent oscillator | -88.4% |
| Damped oscillator | +9.6% |
| Directional benchmark | -79.5% |
| Neutral diffusion | -42.9% |
| **All held-out predictions** | **-45.7%** |

Negative values mean that adding the response invariants made extrapolation worse. The pooled response model has negative held-out-class R² (`-1.326`). Only the damped oscillator shows a small improvement.

## Secondary known-class / new-family control

When the dynamical classes are represented during training and only the seed family is held out, response invariants still do not improve the class+scale baseline:

- class+scale MAE: `0.5380`
- class+scale+response MAE: `0.5867`
- relative MAE change: **-9.0%**

Thus the negative primary result cannot be explained solely by the difficulty of class-level extrapolation.

## Descriptive associations

The largest absolute fold-level correlations with EBID gain are modest:

- variability of local response anisotropy: `r ≈ -0.316`
- variability of local Jacobian norm: `r ≈ -0.277`
- variability of Jacobian-norm variation: `r ≈ -0.258`
- mean innovation variance: `r ≈ +0.225`

These are descriptive only; they do not support a transferable predictive law.

## Interpretation

Experiment 023 rejects the simple idea that generic local forecastability or small-perturbation response statistics are sufficient to determine when EBID will add regulator-demand information.

Together, Experiments 021–023 now rule out three progressively richer candidate explanations as universal cross-class laws:

1. coarse dynamical class alone,
2. raw trajectory morphology,
3. simple local predictive / response invariants.

The remaining possibility is that EBID value depends on **how observed history constrains longer-horizon controlled futures**, rather than on a small set of local path or Jacobian summaries. A next experiment should therefore measure intervention-conditioned future separation directly—for example finite-horizon controllability / reachability, response-memory duration, or action-conditioned forecast uncertainty.

## Claim boundary

This is a negative result about the current finite set of simple response descriptors. It does **not** show that response structure is irrelevant to regulation, and it does not invalidate canonical EBID. It shows that these local response summaries do not provide the missing universal cross-class map from observed dynamics to EBID usefulness.
