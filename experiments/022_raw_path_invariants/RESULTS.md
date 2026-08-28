# Experiment 022 — prospective raw-path invariants

## Question

Can mechanism-agnostic properties of the **raw observed trajectory** predict when frozen canonical EBID will improve future regulator-demand prediction in a dynamical class that was never represented during calibration?

This is the prospective version of Experiment 021. All five classes were regenerated under one matched protocol and every observation trajectory was retained in compressed `.npz` files. The explanatory descriptors intentionally exclude Shannon entropy and all EBID quantities.

## Locked panel

Five classes:

1. PCC,
2. persistent exogenous oscillator,
3. damped exogenous oscillator,
4. directional compositional flow,
5. neutral stochastic diffusion.

For every class the panel uses four independent seed families, PCC-reference observation ratios `0.60` and `1.00`, strengths `1, 2, 3`, four class-specific regimes, the same train-noise (`0, 0.002, 0.005`) / test-noise (`0.01, 0.02`) split, the same 40-step future-control horizon, and the same frozen baseline-versus-EBID ridge readout.

Raw-path descriptors:

- total path length,
- net displacement,
- path efficiency (net displacement / path length),
- long-lag recurrence rate,
- lag-1 tangent-plane autocorrelation,
- spectral concentration,
- turning persistence,
- state-space occupancy.

Each fold uses the mean and standard deviation of these quantities over its held-out test trajectories.

## Prospective EBID gains

The prospectively regenerated panel itself remains heterogeneous. Mean held-out-family EBID gains are:

| class | 0.60 | 1.00 |
|---|---:|---:|
| PCC | +6.2% | +19.8% |
| persistent oscillator | +27.0% | -7.9% |
| damped oscillator | -1.3% | +57.4% |
| directional flow | -5.9% | -31.7% |
| neutral diffusion | -40.3% | -79.7% |

These values should not be treated as replacements for the higher-replication results in Experiments 017–020; Experiment 022 uses a new, smaller prospective seed panel so that raw trajectories can be retained for all classes.

## Primary test: leave one dynamical class out

At each fold the raw-descriptor meta-model is trained using four dynamical classes and predicts EBID gain for the fifth, completely unseen class. The comparison baseline uses observation scale only.

**Result: not supported.** Across all 40 class × family × scale targets:

- scale-only MAE: `0.5634`
- raw-descriptor MAE: `0.8287`
- relative MAE change from adding raw descriptors: **-47.1%**
- raw-descriptor cross-class R²: **-1.38**

Adding the raw-path invariants worsens MAE for every held-out class. The largest failure is directional flow, where raw descriptors increase error by more than threefold relative to scale alone.

## Secondary test: unseen family, represented classes

A secondary leave-one-family-out test allows class identity to be known and asks whether raw descriptors improve a `class + scale` baseline.

They do not:

- class + scale MAE: `0.5380`
- class + scale + raw descriptors MAE: `0.7207`
- relative MAE change: **-33.9%**

Thus the negative primary result cannot be explained only by the difficulty of extrapolating to an unseen class.

## Descriptive associations

Some raw features correlate with EBID benefit in this finite panel, most notably:

- variability of turning persistence: `r ≈ +0.38`
- mean occupancy fraction: `r ≈ +0.35`
- mean turning persistence: `r ≈ +0.34`
- mean spectral concentration: `r ≈ +0.30`

These are descriptive associations only. They do not survive as a useful predictive rule under the preregistered held-out tests.

## Interpretation

Experiment 022 falsifies the simplest prospective version of the proposed general principle. Basic geometric and temporal invariants of the observed simplex path are **not sufficient** to predict, across mechanisms, whether canonical EBID will add regulator-demand information.

This narrows the program in two ways:

1. Experiment 021's within-class descriptor success does not generalize to a prospectively regenerated panel with stricter raw-path controls.
2. The missing information is likely higher-order or relational: e.g. how observed path structure couples to the regulator, disturbance process, or future transition law—not merely the shape of the past trajectory in isolation.

No post-hoc descriptor selection or alternate regularization was performed after observing this failure.

## Claim boundary

Supported:

> EBID benefit varies systematically across dynamical realizations and can correlate with raw trajectory morphology.

Not supported:

> A small set of generic raw-path invariants provides a universal cross-class predictor of EBID regulator value.

A logical next test is to move from **path-only** invariants to **predictive/dynamical invariants** measured from the path, such as local transition predictability, finite-time response/Jacobian sensitivity, forecastability, and state-action coupling.
