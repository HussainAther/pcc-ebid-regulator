# Experiment 009 — Canonical EBID incremental value

## Question

Does the **frozen canonical EBID entropy-rate feature family** add held-out
predictive information about future regulator difficulty after controlling for:

1. nonlinear endpoint simplex geometry and coupling strength,
2. generic vector-field activity over the observation window,
3. endpoint phase and known structural regime,
4. the matched quadratic-distance trajectory baseline used in the parent EBID
   manuscript?

## Canonical EBID freeze

The feature family is ported from the parent PCC/EBID manuscript without
outcome-driven tuning. For an observed trajectory,

\[
H(t)=-\sum_i x_i(t)\log x_i(t),\qquad D(t)=\log 3-H(t).
\]

The frozen features are initial/mean/end entropy, entropy drop and slope, mean
and minimum entropy rate, entropy-rate variance, deficit growth, maximum deficit
rate, and deficit-rate variance.

The quadratic control uses \(Q(t)=\|x(t)-x^*\|^2\) and matched trajectory/rate
summaries. This is important because the parent manuscript explicitly notes that
entropy deficit is locally quadratic near the symmetric equilibrium.

## Protocol

- 320 matched initial states per system.
- PCC: 4 topologies x 5 coupling strengths.
- Non-PCC control: 4 exogenous directional regimes x the same strengths.
- Observe 25 uncontrolled steps.
- Predict mean regulation error over the next 50 controlled steps.
- Same 9-action one-channel oracle family as Experiment 008.
- Eight deterministic sample-ID folds.

The primary statistic is the change in cross-validated \(R^2\) when canonical
EBID is added **after** the quadratic trajectory baseline.
