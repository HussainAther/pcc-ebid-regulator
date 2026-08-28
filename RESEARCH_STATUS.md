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

### Experiment 013 — observation-timescale sufficiency

A dense sub-cycle observation sweep does **not** reproduce Experiment 011 as a simple EBID sufficiency threshold. Independent long-trajectory estimates place the tested 5–80 step windows at only ~0.004–0.285 intrinsic cycles. EBID transfer remained negative in most windows and normalized ratio bins, becoming only slightly positive (+3.3% relative MAE reduction) in the 0.20–0.30 bin. The defensible conclusion is that EBID transfer is timescale-sensitive, but no critical cycle fraction has yet been identified. Longer observations spanning actual fractions/multiples of a cycle are required.

### Experiment 014 — full-cycle observation scaling

Experiment 014 extends the observation-timescale test from the sub-cycle regime to windows defined directly as `0.10–1.50` intrinsic PCC cycles. Under the primary ratio-local calibration, EBID is strongly harmful at `0.10` cycle, negative at `0.25`, uncertain at `0.50`, and first reliably beneficial at `0.75` cycle (`+33.5%` relative MAE reduction, bootstrap interval fully above zero). `1.50` cycles is also reliably positive; `1.00` cycle is positive but borderline. A secondary model calibrated jointly across all observation scales is positive at every ratio, including `0.10`, showing that the apparent transition is calibration-dependent rather than a universal dynamical threshold. Current claim: substantial cycle coverage improves local EBID transfer stability, but no fixed critical cycle fraction has been established.

## Experiment 015 update — dense transition does not replicate as a threshold

Experiment 015 independently repeated the ratio-local full-cycle test over `0.4–1.2` cycles with twice the per-cell replication and a fixed standardized ridge readout. Reliable positive EBID transfer occurs at `1.00` cycle (`+30.2%` relative MAE reduction; bootstrap 95% interval about `+11.9%` to `+46.7%`) and `1.20` cycles (`+37.9%`; about `+20.6%` to `+50.5%`). However, `0.60` cycles is strongly harmful (`-47.8%`; interval entirely below zero), and `1.10` cycles is negative. The first reliable ratio therefore shifts from `0.75` in Experiment 014 to `1.00` in Experiment 015, and the curve is not monotonic.

**Claim boundary:** the repository now supports observation-scale sensitivity of local EBID readout, including favorable full-cycle-scale regimes, but does not support a universal or smoothly increasing critical cycle fraction. A cross-seed replication of the scale map is required before interpreting the non-monotonic pattern mechanistically.

## Experiment 016 update — cross-seed scale map is not stable

Experiment 016 repeats the six diagnostic cycle fractions (`0.50`, `0.60`, `0.75`, `1.00`, `1.10`, `1.20`) across eight fully independent simulation seed families while freezing the Experiment-015 reference periods, canonical EBID feature family, unseen-noise split, horizon, and standardized ridge readout. The full sweep contains 7,680 trajectories and 48 family×ratio evaluations.

The Experiment-015 pattern does **not** replicate. Across seed families, `0.60` cycles is the only ratio with a bootstrap-positive mean EBID gain (`+18.9%`, 7/8 families positive), despite being strongly harmful in Experiment 015. Conversely, `0.75` cycles is reliably harmful on average (`-42.2%`) despite being the first cleanly favorable point in Experiment 014. `1.00` cycles is negative on average and `1.20` is positive but uncertain. The family-level gain distributions are broad.

**Claim boundary:** observation scale remains relevant, but no particular cycle fraction, full-cycle region, or non-monotonic scale pattern is currently reproducible across simulation realizations. The next priority is leave-one-seed-family-out calibration to determine whether this instability comes mainly from fitting each small family separately or from genuine family-level differences in the dynamics/EBID relationship.

## Experiment 017 — leave-one-seed-family-out calibration

Experiment 017 directly tests whether Experiment 016's extreme seed-family variability was caused by calibrating each small family independently. Using the same frozen EBID features, cycle ratios, period references, noise split, horizon, and ridge alpha, each ratio-specific model is trained on seven complete simulation families and tested on the eighth.

The better-conditioned calibration reduces family-level dispersion substantially. `0.60` cycles remains reliably positive (`+15.3%` mean relative MAE reduction; bootstrap interval fully above zero), while `1.00` cycle becomes the strongest cross-family result (`+23.6%`, 8/8 held-out families positive, bootstrap interval about `+14.6%` to `+32.9%`). The prior `0.75`-cycle harmful effect collapses to near zero. Thus a meaningful portion of the Experiment-016 jaggedness was readout-estimation noise rather than stable dynamical heterogeneity.

**Current claim boundary:** canonical EBID has reproducible out-of-family predictive value at selected observation scales under stabilized cross-family calibration, especially around one intrinsic cycle, but the scale profile remains non-monotonic and is not yet PCC-specific. A matched non-PCC leave-family-out specificity control is now the priority.

## Experiment 018 — matched non-PCC cross-family specificity

Experiment 018 returns to the specificity question only at the two observation scales that survived Experiment 017 (`0.60` and `1.00` PCC reference cycles). The benchmark uses the same absolute observation durations defined by the PCC intrinsic-period ruler, but its dynamics are generic exogenous directional selection rather than non-transitive PCC interaction. EBID remains frozen and the leave-one-family-out ridge protocol is unchanged.

The comparison is strongly PCC-enriched. At `0.60`, PCC improves by `+15.3%` while the benchmark averages `-5.7%`; the paired specificity margin is `+21.0` percentage points with a bootstrap interval entirely above zero. At `1.00`, PCC improves by `+23.6%` in 8/8 held-out families, while benchmark EBID worsens all 8/8 families (`-203.5%` mean relative change), producing a very large positive paired specificity margin.

The `1.00` benchmark failure is not caused by a near-zero baseline MAE: baseline errors remain around `0.06–0.12`, while EBID-augmented errors rise to roughly `0.21–0.32`. The directional benchmark's long trajectories collapse toward low-entropy simplex corners, making the frozen entropy-rate readout strongly non-transferable across regimes.

Current status: **PCC-enriched EBID transfer is supported relative to the current directional compositional benchmark at the two stabilized scales.** This does not establish uniqueness to PCC. The next specificity control should be oscillatory but non-PCC, to test whether the advantage is due to cyclic dynamics generally rather than PCC/non-transitivity specifically.

## Experiment 019 — oscillatory non-PCC specificity

**Status:** complete; negative specificity result.

An externally forced three-component oscillator was matched to PCC reference periods and evaluated at the two cross-family-stable observation scales from Experiment 017 (`0.60`, `1.00`). It contains no endogenous PCC/RPS interaction.

At `0.60`, frozen canonical EBID reduces held-out-family prediction MAE by `49.3%` in the oscillatory control (8/8 families positive), substantially exceeding the PCC gain of `15.3%`. The paired PCC-minus-control margin is `-34.0` percentage points with a bootstrap interval entirely below zero. At `1.00`, the control gain is `22.8%` (7/8 positive), essentially matching PCC's `23.6%`; the paired margin is `+0.8` pp with an interval crossing zero.

**Current conclusion:** the strong Experiment-018 separation does not generalize from a directional control to an oscillatory one. EBID's stabilized regulator-demand signal is therefore not currently PCC-specific; generic cyclic dynamics can reproduce or exceed it. This is a major narrowing result and should supersede any broad interpretation of Experiment 018 as evidence for uniqueness to PCC.

### Experiment 020 — dynamical-class panel

A five-class panel (PCC, persistent oscillator, damped oscillator, directional flow, neutral diffusion) shows that canonical EBID's incremental regulator-demand value is neither unique to PCC nor reducible to the presence of oscillation. At 0.60 PCC-reference cycles, mean EBID gains are +15.3%, +49.3%, +57.7%, -5.7%, and +12.6%, respectively. At 1.00 cycle they are +23.6%, +22.8%, -7.8%, -203.5%, and +36.0%. This supports a broader trajectory-history dependence but does not identify one causal dynamical property.

### Experiment 021: continuous trajectory-statistics panel
Using 80 frozen class × family × scale folds from Experiments 016–020, non-EBID trajectory summaries predict EBID's incremental regulator value across held-out seed families. Relative to observation scale alone they reduce MAE by 32.0%; relative to a stronger class+scale baseline they reduce MAE by 22.5%, with cross-family R² ≈ 0.74. The strongest rank association is endpoint-imbalance variability (rho ≈ +0.50), followed by mean dynamical activity (rho ≈ +0.33). However, leave-one-class-out extrapolation fails: the descriptor model increases MAE by about 67% overall. Current conclusion: trajectory statistics carry within-class information about EBID usefulness, but no universal cross-class mapping has been demonstrated.

### Experiment 022 — prospective raw-path invariants

Experiment 022 prospectively regenerates all five dynamical classes under one matched protocol and retains every observation trajectory in compressed raw-path archives. Eight pre-specified, non-EBID path descriptors (path length, net displacement, efficiency, recurrence, autocorrelation, spectral concentration, turning persistence, and occupancy) are used to predict the held-out-family EBID gain.

The primary leave-one-dynamical-class-out test is negative: adding raw-path descriptors to observation scale worsens MAE by **47.1%** overall (`R² ≈ -1.38`), with no held-out class improved. Even the secondary leave-one-family-out test, where dynamical classes are represented and class identity is available, worsens MAE by **33.9%** beyond class+scale. Some descriptors correlate descriptively with EBID gain, but they do not form a transferable predictive rule.

Current conclusion: **trajectory morphology alone is insufficient**. If a general regulator principle exists, it likely requires information about transition predictability, local response/sensitivity, disturbance coupling, or action-conditioned dynamics rather than simple geometric summaries of the past path.

### Experiment 023 — predictive / response invariants

The prospective raw-path panel from Experiment 022 was augmented with non-EBID predictive and local-response descriptors: chronological linear forecast error, innovation variance, predictability decay, finite-difference Jacobian norms, perturbation amplification, and local anisotropy. These descriptors **do not solve** the cross-class generalization problem. Leave-one-dynamical-class-out MAE worsens by about **45.7%** relative to scale alone, and a known-class leave-one-family-out control worsens by about **9.0%** beyond class+scale.

Current claim boundary: neither simple path morphology nor simple local predictive/response statistics provide a universal mapping from observed dynamics to EBID regulator value. The next regulator question should move to finite-horizon, intervention-conditioned quantities such as controllability, reachability, response memory, or action-conditioned future uncertainty.

### Experiment 024 — finite-horizon controllability / response memory

Experiment 024 probes the held-out trajectories from the prospective five-class panel with standardized state perturbations and intervention branches rolled forward for 5 and 20 deterministic steps. The resulting non-EBID descriptors include perturbation-memory amplification, bounded response anisotropy, action-conditioned future spread, spread variability, and persistence ratios.

The primary leave-one-dynamical-class-out result is negative: adding these descriptors to observation scale worsens MAE by **56.4%** overall (`R² ≈ -2.03`). The model helps persistent and damped oscillators modestly but hurts PCC, neutral diffusion, and directional flow. In the easier known-class leave-one-family-out test, the added descriptors are essentially neutral (`+0.3%` MAE reduction beyond class+scale).

**Current claim boundary:** increasingly rich handcrafted trajectory/response summaries have not produced a universal meta-rule for EBID usefulness. The next priority is to test a more direct mechanistic relationship between EBID and action-conditioned future regulatory difficulty within trajectories, rather than predicting aggregate EBID gain from summary descriptors.

### Experiment 025 — direct EBID prediction of achievable control benefit

Experiment 025 changes the target from "when does EBID help a predictor?" to the regulator quantity itself. Each prospective observation endpoint is rolled forward for 40 deterministic steps both uncontrolled and under the same optimistic 9-action/two-channel greedy oracle. The target is the relative reduction in future regulation error achievable by that controller.

Against a strong baseline containing endpoint geometry, the matched quadratic trajectory family, and generic activity history, the full frozen canonical EBID feature family reduces leave-one-dynamical-class-out MAE by **28.8% pooled**. The gain is positive for all five unseen classes (roughly `+19.5%` to `+38.8%`), and the pooled EBID model reaches `R² ≈ 0.86`. Known-class leave-one-family-out transfer improves by **27.4%**.

The crucial ablation is that initial/mean/endpoint entropy already accounts for **26.6%** pooled improvement. The remaining entropy-rate/deficit-rate features add only about **3.0%** beyond those entropy summaries, and only about `1.4%` for PCC. Thus the direct positive result is best interpreted as a transferable **entropy-history → control-benefit** relationship, not evidence that EBID rate terms uniquely encode regulator demand.

## Experiment 026 — entropy-history decomposition

Experiment 026 reuses the direct control-benefit dataset from Experiment 025 and strengthens the current-state baseline. Because endpoint entropy is exactly determined by the current simplex state, a primary sanity track includes the exact endpoint-entropy transform in the state baseline before any temporal features are added.

Under leave-one-dynamical-class-out evaluation, `H_initial` and `H_mean` then add ~4.3% pooled MAE reduction, and the remaining canonical rate / deficit-rate terms add ~2.4% more. PCC shows a stronger ~7.3% history increment plus ~2.5% rate increment. Neutral diffusion is a counterexample, with entropy history worsening transfer by ~10.6%.

**Claim boundary:** Experiment 025's large entropy-family gain should not be described as a large temporal EBID effect. A substantial fraction is explained by explicit nonlinear endpoint-entropy representation. Modest temporal information survives after that control, but it is mechanism-dependent rather than universal.
