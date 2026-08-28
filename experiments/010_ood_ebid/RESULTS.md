# Experiment 010 — Stochastic / OOD canonical EBID replication

## Question

Does the frozen Experiment 009 canonical EBID feature family retain incremental
predictive value for future regulator difficulty under distribution shift?

No EBID formula or feature was changed after observing Experiment 009.

## Protocols

The same tangent-plane Gaussian perturbation is applied to PCC and the matched
non-PCC benchmark.

- Training noise: `sigma = 0, 0.002, 0.005`
- Unseen test noise: `sigma = 0.01, 0.02`
- Four PCC topologies and four matched non-PCC regimes
- Five interaction strengths
- Six replicates per structure/strength/noise cell

Three tests are reported:

1. **Noise OOD:** train on the low/no-noise range, test on unseen higher noise.
2. **Structure OOD:** leave one topology/regime out entirely.
3. **Joint OOD:** train on other structures at low/no noise; test the held-out
   structure at unseen higher noise.

Because OOD R-squared can become strongly negative when a model extrapolates
badly, relative MAE reduction is the primary interpretable effect metric. R-squared
is retained in the raw tables for completeness.

## Main results

### Unseen noise

Adding canonical EBID to the geometry + activity + phase + quadratic trajectory
baseline reduces PCC MAE by **43.9%** (paired bootstrap 95% interval about
**35.1% to 51.3%**). The same features *increase* benchmark MAE by **13.0%**.

### Held-out structure

PCC relative MAE reductions by held-out topology index are approximately:

- canonical: **7.6%**
- reverse: **7.2%**
- no-pressure-control: **20.2%**
- no-control-chaos: **17.7%**

The reverse-topology bootstrap interval narrowly crosses zero, so that cell is
not individually decisive. The matched benchmark gains are smaller and mixed.

### Joint unseen-noise + held-out-structure

PCC relative MAE reductions are approximately:

- canonical: **-2.5%** (no replication)
- reverse: **58.4%**
- no-pressure-control: **65.4%**
- no-control-chaos: **36.3%**

Thus the strongest OOD setting replicates on three of four PCC topologies but
fails on canonical PCC. The benchmark does not show a comparable pattern.

## Interpretation

Experiment 010 strengthens the case that the frozen EBID trajectory family can
carry regulator-demand information that is enriched in PCC relative to the
matched non-PCC benchmark under stochastic shift. The unseen-noise result is
particularly strong.

However, the joint-OOD canonical failure prevents a universal claim. The result
should be described as **partial OOD replication with topology dependence**, not
as proof that EBID is a general regulator theorem or a universally sufficient
PCC statistic.

A next experiment should diagnose *why* canonical PCC is the exception: test
interaction strength, horizon, observation-window length, and phase-conditioned
failure without altering the frozen EBID definition.
