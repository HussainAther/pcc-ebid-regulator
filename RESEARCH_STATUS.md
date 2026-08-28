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

## Experiment 007 — non-PCC compositional specificity benchmark

Experiment 007 tests whether Experiment 006's large 2D intervention advantage
is specific to PCC/non-transitive dynamics. The control system uses the same
three-component simplex, target, vector intervention semantics, matched action
cardinality (`K = 5, 9, 17`), matched mean L2 repertoire norm, initial
conditions, and dwell times. The PCC interaction matrix is replaced by fixed
exogenous directional-selection regimes, so there is no endogenous cyclic or
pairwise interaction.

The benchmark reproduces the 2D advantage almost exactly. Its median relative
error reduction is `97.2%` (range `93.4–98.5%`). Across the directly matched
cells, the median difference between PCC and benchmark relative reductions is
about `-0.4` percentage points. In four-regime switching, benchmark reductions
of about `97.0–98.5%` closely track PCC's `96.6–98.3%`.

This is a **specificity failure** for the strong interpretation of H5. The large
1D-to-2D advantage should currently be attributed primarily to generic
compositional controllability / simplex geometry, not to PCC structure itself.
The intervention-dimensionality phenomenon remains computationally robust, but
it is not evidence by itself for a PCC-specific extension of requisite variety.

Twenty-three unit tests pass after adding the non-PCC benchmark dynamics,
regime-aware benchmark regulator, and benchmark simulation path.


## Experiment 008 — PCC-specific predictive signal

Experiment 008 asks whether candidate PCC dynamic descriptors predict future
regulation difficulty after controlling for the generic simplex geometry
identified in Experiment 007. It uses 320 matched initial states, five coupling
strengths, four PCC topologies, four non-PCC benchmark regimes, and a fixed
9-action one-channel regulator. The outcome is mean error over a 50-step future
horizon.

The tested PCC interaction-activity statistic is explicitly **EBID-adjacent**,
not claimed as the canonical EBID measure. With second-order state/strength
geometry controls, adding activity increases PCC cross-validated R² from about
`0.652` to `0.704` (`+0.052`). The analogous non-PCC activity signal increases
R² from about `0.383` to `0.501` (`+0.118`). Thus dynamic activity is useful,
but the present signal fails the PCC-specificity test and does not support H2
as currently operationalized.

Cycle phase adds a modest amount beyond a coarse PCC imbalance baseline, but a
smaller gain also appears in the benchmark. H4 therefore remains unconfirmed.
The next decisive step is to implement the actual/canonical EBID statistic (if
its definition is fixed in the parent PCC work) and test **incremental
out-of-sample value over generic activity, phase, state geometry, and benchmark
controls**.

## Experiment 009 — canonical EBID incremental value

Experiment 009 imports and freezes the canonical finite-time EBID feature family
from the parent PCC/EBID manuscript: Shannon entropy `H(t)`, entropy deficit
`D(t)=log(3)-H(t)`, and the stated early-window entropy/deficit rate features.
It deliberately includes the parent's matched quadratic-distance trajectory
baseline `Q(t)=||x(t)-x*||^2` because entropy deficit is locally quadratic near
the symmetric equilibrium.

The experiment observes 25 uncontrolled steps for 320 matched initial states,
then predicts mean regulation error over a subsequent 50-step controlled
horizon. Nested held-out models add nonlinear endpoint geometry, generic
activity, phase/known structure, quadratic trajectory features, and finally
canonical EBID.

For PCC, adding the quadratic trajectory baseline to the geometry/activity/
phase/structure model leaves CV R² near `0.717`; adding canonical EBID raises it
to about `0.792` (`+0.075`). For the non-PCC benchmark the corresponding gain is
about `+0.047`. The fixed-fold PCC specificity margin is therefore `+0.028`.
Across 30 repeated 8-fold sample-level partitions, the median PCC-minus-
benchmark margin is about `+0.021`, positive in `96.7%` of repeats, with a range
of roughly `-0.002` to `+0.044`.

This is the first experiment in this repo to show a reproducible *relative*
advantage for the frozen EBID feature family after a conservative quadratic
control. It remains provisional: EBID also improves the non-PCC benchmark, the
specificity margin is modest, and one repeated partition is slightly negative.
The next priority is an out-of-distribution / stochastic replication rather
than further in-sample feature invention.

Twenty-nine unit tests pass after adding the frozen EBID implementation and
quadratic-baseline tests.

## Experiment 010 — stochastic / out-of-distribution canonical EBID replication

Experiment 010 keeps the Experiment 009 canonical EBID feature definition frozen
and applies matched tangent-plane Gaussian process perturbations to PCC and the
non-PCC benchmark. Models are evaluated under unseen noise strengths,
leave-one-structure-out transfer, and their joint combination.

OOD R-squared is retained but not used as the headline metric because hard
extrapolation can make its baseline strongly negative. Relative MAE reduction
provides the more interpretable paired comparison.

Under unseen higher noise, EBID reduces PCC MAE by `43.9%` (paired bootstrap 95%
interval about `35.1%–51.3%`) while worsening the non-PCC benchmark by `13.0%`.
Under held-out structures it improves PCC in all four cases (`7.2–20.2%`), with
one interval narrowly crossing zero. Under the hardest joint shift, it improves
three non-canonical PCC topologies strongly (`36.3–65.4%`) but slightly worsens
canonical PCC (`-2.5%`).

The current status is therefore **partial OOD replication with topology
dependence**. This strengthens H6/H7 relative to Experiment 009, especially for
unseen stochasticity, but rules out a topology-uniform claim.

Thirty-two unit tests pass after adding the matched stochastic perturbation
module and Experiment 010 controls.

## Experiment 011 — topology-dependent transfer diagnosis

Experiment 011 keeps canonical EBID frozen and diagnoses the joint-OOD failure
from Experiment 010. The dominant factor is observation-window length. With a
50-step observation window, EBID improves held-out canonical-PCC MAE at all
three tested future horizons (`+40.5%`, `+9.8%`, and `+32.2%`). Ten- and 25-step
windows are frequently harmful, especially at the 40-step horizon. Phase
stratification is also suggestive: Q1/Q4 show positive median gains whereas
Q2/Q3 show negative median gains. Strength effects are non-monotonic.

The current claim is therefore narrower: canonical EBID has **timescale- and
phase-dependent OOD transfer** in this toy system. It is not uniformly robust,
and the short-window failures remain part of the evidence record.

## Experiment 012 — pre-specified phase-aware EBID calibration

Experiment 012 directly tests the most tempting mechanistic interpretation of
Experiment 011. Canonical EBID remains frozen. The only added terms are
first-harmonic interactions between each of the 11 EBID features and
`sin(phase)` / `cos(phase)`. The exact Experiment 011 trajectories and the same
joint held-out-topology + unseen-noise protocol are reused, preventing dataset
regeneration from becoming an additional degree of freedom.

The result is a clear negative. For held-out canonical PCC, phase-aware EBID
improves prediction in only `1/9` observation-window × horizon cells; the median
relative MAE change is strongly negative. The one positive cell (10-step
observation, 40-step horizon; about `+46.6%`) has a paired-bootstrap interval
that crosses zero. Across the control PCC topologies the interaction model is
also usually worse than plain EBID.

Therefore the phase-quadrant pattern in Experiment 011 is **not validated as a
predictive mechanism** by this pre-specified interaction test. No alternative
phase basis, regularization strength, or subset of EBID features was tuned after
seeing the result. The 011 timescale finding remains the stronger observation:
longer trajectory windows improve plain-EBID transfer, whereas simple endpoint
phase interactions do not explain that improvement.

Thirty-four tests pass after adding the Experiment 012 guardrail tests.
