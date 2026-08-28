# Research Status

## Current status: baseline computational scaffold

The repository now cleanly separates two questions that were previously easy to
confound:

1. **Regulatory capacity / requisite variety** — Experiment 001 varies only the
   discrete action repertoire of a fixed reactive regulator.
2. **Internal model content / Good Regulator connection** — Experiment 002 holds
   action repertoire fixed while changing the regulator's predictive model.

Four unit tests currently pass.

## Preliminary baseline results

### Experiment 001 — deterministic requisite-variety sweep

Using the current three-state deterministic PCC toy dynamics and an error
criterion of 0.08, a three-action repertoire was sufficient at every tested
coupling strength from 0.5 through 3.0. A one-action (no-control) repertoire
failed throughout.

This baseline therefore **does not support** the stronger hypothesis that
increasing PCC coupling by itself raises the empirical minimum regulator
variety. It also shows that more finely discretized action repertoires do not
monotonically improve the present reactive controller.

Interpretation: the current deterministic system can be driven near the
symmetric equilibrium and then requires little sustained intervention. It is
therefore too forgiving to establish a trajectory-dependent requisite-variety
result.

### Experiment 002 — model-content ablation

The correctly specified one-step PCC model did **not** consistently outperform
state-only, short-history, or parameter-misspecified alternatives at the tested
coupling strengths.

This baseline therefore **does not support** a Good-Regulator-style claim that
explicit PCC model content is necessary in this toy regime.

Interpretation: the task is currently simple enough that richer model content
provides little advantage; moreover, a one-step greedy predictor is not a fair
proxy for the deeper informational claims of the Good Regulator Theorem.

## What can be claimed now

- The repo has executable, falsifiable versions of the first two questions.
- Capacity and model-content variables are now experimentally separated.
- The simplest deterministic implementation produces informative null results.

## What cannot be claimed now

- That EBID predicts requisite regulatory variety.
- That PCC coupling causes requisite variety to increase.
- That a PCC-aware controller is required by the Good Regulator Theorem.
- That cycle phase is necessary regulator information.
- That PCC/EBID extends, generalizes, or supersedes any established theorem.

## Next decisive tests

The next experiments should create regimes where regulation remains genuinely
nontrivial over time:

- stochastic perturbations,
- drifting coupling parameters,
- nonstationary targets,
- topology changes or edge failures,
- multiple initial conditions,
- threshold-sensitivity analysis,
- capacity-matched topology and phase ablations.

Null results should remain in the repository as part of the evidence trail.


## Experiment 003 — parameter drift

Dynamic coupling drift produces modest degradation at fixed regulator variety,
and stricter error thresholds sometimes require larger repertoires. The effect
is threshold-sensitive and non-monotonic across the small stochastic sample, so
H1 remains **unconfirmed**. The present result is best described as mixed /
weakly suggestive evidence motivating stronger nonstationary perturbations.
