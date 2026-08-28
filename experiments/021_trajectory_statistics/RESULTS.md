# Experiment 021 — Continuous trajectory-statistics panel

## Question
Can continuous, pre-horizon trajectory properties explain when frozen canonical EBID improves prediction of future regulator difficulty better than coarse dynamical-class labels?

The analysis reuses the frozen datasets and family-level EBID gains from Experiments 016–020. No EBID/entropy feature is allowed on the explanatory side. Each of the 80 class × family × scale folds is summarized using endpoint imbalance, interaction activity, quadratic/radial trajectory behavior, and endpoint phase dispersion.

## Main findings

### 1. Several trajectory summaries correlate with EBID benefit
The strongest rank associations across the 80 folds are:

- endpoint-imbalance variability: Spearman rho ≈ **+0.50**;
- mean dynamical activity: rho ≈ **+0.33**;
- mean radial level away from the simplex center: rho ≈ **−0.27**;
- radial-rate variance: rho ≈ **−0.25**;
- endpoint phase dispersion: rho ≈ **+0.19**.

Cluster bootstraps over the eight shared simulation families keep these five correlations away from zero in this panel. These are associations, not causal effects.

### 2. Continuous descriptors help within represented dynamical classes
Under leave-one-seed-family-out validation across all five classes, a fixed ridge model using scale + trajectory descriptors reduces MAE by **32.0%** relative to observation scale alone and reaches cross-family R² ≈ **0.67**.

A stricter baseline already knows the dynamical class and observation scale. Adding the continuous trajectory descriptors still reduces MAE by **22.5%**, improving cross-family R² from about **0.56** to **0.74**.

Thus the descriptors contain information beyond merely labeling a trajectory as PCC, oscillator, directional flow, damped oscillator, or neutral diffusion.

### 3. The descriptor rule does not extrapolate to a new dynamical class
Leave-one-class-out validation fails. Across all 80 held-out-class predictions, the descriptor model increases MAE by about **67%** relative to a scale-only baseline and has strongly negative out-of-class R². Every individual held-out class is worse or essentially neutral.

This means the current continuous statistics are useful for interpolation across new trajectory families *within dynamical classes already represented during calibration*, but do not define a universal law that transfers to a qualitatively unseen class.

## Interpretation
Experiment 021 narrows the emerging principle. EBID usefulness is not random: within the present panel it is associated with measurable trajectory properties, especially variability in endpoint imbalance and overall dynamical activity. However, those relationships are class-dependent. The same low-dimensional descriptor-to-EBID-gain mapping cannot yet be exported to a wholly unseen dynamical mechanism.

The defensible statement is therefore:

> Continuous pre-horizon trajectory statistics predict variation in EBID's incremental regulator value beyond class identity for represented dynamical classes, but the current descriptor set does not support a universal cross-class rule.

The next experiment should test richer *mechanism-invariant* descriptors from the raw paths themselves—especially path length, recurrence/return, spectral concentration, and directional persistence—under an explicitly held-out-class protocol. Those quantities were not stored in the frozen 016–020 summary datasets and should be generated prospectively rather than reconstructed post hoc.
