# Research Status

## Current status: baseline computational scaffold

The repository now cleanly separates two questions that were previously easy to
confound:

1. **Regulatory capacity / requisite variety** — Experiment 001 varies only the
   discrete action repertoire of a fixed reactive regulator.
2. **Internal model content / Good Regulator connection** — Experiment 002 holds
   action repertoire fixed while changing the regulator's predictive model.

The executable scaffold now includes six regulator experiments and capacity-matched vector interventions.

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

## Experiment 004 — topology switching

Experiment 004 separates structural environmental variety from scalar coupling
drift.

### 004A — structural requisite variety

Switching among reversed-cycle and edge-removal topologies produces a much
larger increase in regulation error than Experiment 003's scalar drift. At the
mean-error criterion of `0.030`, three- and four-topology environments cannot
be regulated below threshold by any tested repertoire up to variety `17`.

This is **not** evidence for a monotonic requisite-variety law. Among repertoires
that do regulate well, larger cardinality is often neutral or worse. The result
instead suggests that a one-dimensional family of scalar Control actions is a
poor operationalization of regulator variety for structural disturbances.

### 004B — topology-model adequacy

With repertoire fixed at nine actions, one-step predictive model controllers
roughly halve mean regulation error relative to state-only and short-history
controllers under four-topology switching. Exact active-topology knowledge does
not confer a consistent advantage over fixed misspecified predictive models;
the fixed reverse model is marginally best in the tested grid.

Thus H3 receives **partial support only in its weak form** (predictive dynamical
structure helps relative to simple model-free baselines). The stronger claim
that correct PCC topology representation is required remains unsupported.

Eleven unit tests pass after adding topology dynamics and switching support.

## Experiment 005 — multi-channel regulator variety

Experiment 005 replaces the scalar action-level definition of regulator variety
with component-specific intervention access on Pressure, Control, and Chaos.
The controller retains oracle knowledge of the active topology so that model
adequacy is held optimistic and the main variable is intervention access.

The result is the clearest Ashby-shaped pattern in the repository so far. At a
mean-error criterion of `0.100`, a one-topology environment can be regulated by
a one-channel controller, while environments switching among two, three, or
four topologies require at least two intervention channels for dwell values 20,
50, and 100. At stricter criteria, two channels are already required even in the
one-topology case, so the threshold shift is explicitly performance-dependent.

Within the common multi-channel intervention semantics, the performance jump is
large: in four-topology switching the best one-channel mean error is roughly
`0.34–0.36`, whereas the best two-channel controllers achieve approximately
`0.009–0.012`. Three-channel access offers little systematic gain over two
channels. This saturation is consistent with the geometry of a normalized
three-component simplex, whose relative-state tangent space is two-dimensional.

A reduced action-magnitude sensitivity sweep (`0.03`, `0.06`, `0.09`, `0.12`)
preserves the qualitative one-channel versus two-channel separation.

This is **threshold-dependent computational support**, not a theorem. The next
critical controls are action-capacity matching, multiple initial conditions,
stochastic disturbances, non-PCC compositional baselines, and an operational
canonical EBID predictor.

Sixteen unit tests pass after adding vector-valued interventions and the
multi-channel simulation harness.

## Experiment 006 — capacity-matched intervention dimensionality

Experiment 006 directly tests the main confound in Experiment 005. One- and
two-dimensional regulator families are given the same number of candidate
actions (`K = 5, 9, 17`) and exactly matched mean L2 action-set norm. The sweep
also repeats each comparison across three initial compositions.

The two-dimensional advantage survives decisively. Across all tested cells, the
best 2D family reduces mean regulation error by approximately `95–98%` relative
to the best 1D family. In four-topology switching at dwell 50 and K=9, for
example, the aggregate error is `0.239551` for the best 1D family versus
`0.005250` for the best 2D family, a 97.8% reduction.

This rules out the simplest explanation that Experiment 005 was driven merely
by giving multi-channel regulators more candidate actions or greater average
intervention magnitude.

The important counterpoint is that the 2D advantage is already comparably large
in the one-topology condition (median relative reduction about 97.2%). Therefore
Experiment 006 strongly supports an **intervention geometry / controllability**
effect but does not show that increasing topology count monotonically causes a
higher required intervention dimension. That distinction is now part of the
claim boundary.

Nineteen unit tests pass after adding matched-repertoire construction and the
capacity-matched regulator path.
