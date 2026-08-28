# Research Roadmap

## Phase 1 — Separate the classical questions

- [x] Isolate **action repertoire** as the Experiment 001 requisite-variety variable.
- [x] Isolate **internal model content** as the Experiment 002 Good-Regulator variable.
- [ ] Add repeated initial conditions and stochastic perturbations.
- [ ] Replace single arbitrary error threshold with threshold sensitivity curves.

## Phase 2 — Make EBID operational

- [ ] Import the canonical EBID definition from the parent PCC repository.
- [ ] Distinguish EBID from entropy deficit and other proxy observables.
- [ ] Test whether EBID predicts empirical regulator demand out of sample.
- [ ] Compare EBID against coupling strength, trajectory variance, entropy rate,
      Lyapunov-style proxies, and simple state imbalance.

## Phase 3 — Good Regulator / Internal Model tests

- [x] Correct-model versus state/history/misspecified-model baseline.
- [ ] Capacity-match model classes more rigorously.
- [x] Add topology ablation: correct cycle, reversed cycle, missing edge.
- [ ] Add explicit phase estimator and phase-aware controller.
- [x] Test robustness under scalar parameter drift.
- [x] Test topology switching.
- [ ] Test component-specific coupling drift.

## Phase 4 — Stronger cybernetic claims only if warranted

- [ ] Formalize a state-dependent or trajectory-conditioned variety quantity.
- [ ] Determine whether any result is genuinely new versus a direct consequence
      of existing stochastic/dynamic versions of requisite variety.
- [ ] Write theorem/proposition statements only after literature comparison and
      computational falsification survive.


## Phase 5 — Improve the meaning of regulator variety

- [x] Replace scalar action-level count with multiple qualitatively distinct action channels.
- [x] Give the regulator component-specific interventions on Pressure, Control, and Chaos.
- [x] Capacity-match action-set cardinality and mean intervention magnitude across 1D/2D repertoires.
- [ ] Capacity-match action entropy / effective distinguishable outcomes, not only raw cardinality.
- [x] Re-run topology switching with multi-channel regulators under common intervention semantics.
- [x] Revisit the structural requisite-variety claim with explicit threshold sensitivity.
- [x] Repeat the capacity-matched dimensionality test across multiple initial conditions.
- [ ] Repeat under stochastic state/process perturbations.
- [ ] Compare against non-PCC compositional control benchmarks to test specificity.

## Phase 6 — Specificity and geometric controls

- [x] Compare the capacity-matched 1D/2D effect against a non-PCC compositional benchmark.
- [x] Treat reproduction of the effect by the benchmark as a specificity failure rather than positive PCC evidence.
- [ ] Capacity-match effective action outcomes / action entropy, not only cardinality and mean norm.
- [ ] Add stochastic process perturbations to both PCC and benchmark systems.
- [ ] Search for PCC-specific predictors of regulator demand (EBID, cycle phase, topology uncertainty) beyond the geometric baseline.


## Experiment 008 — PCC-specific predictive signal — complete

- [x] Match PCC and non-PCC initial states and regulator capacity.
- [x] Control for static and nonlinear simplex geometry.
- [x] Test EBID-adjacent interaction activity.
- [x] Test simplex phase.
- [x] Compare incremental predictive value to an analogous non-PCC activity signal.
- [x] Preserve specificity failures in the claim boundary.

## Recommended Experiment 009 — canonical EBID incremental-value test

1. Import/freeze the canonical EBID definition from the parent PCC repository.
2. Compute canonical EBID on matched trajectories without changing its formula
   after seeing outcomes.
3. Predict future regulation error/failure using nested models:
   geometry -> generic activity -> phase/topology -> canonical EBID.
4. Evaluate held-out R² / calibration and compare against the non-PCC control.
5. Treat no incremental value as falsification pressure on H2 rather than
   redefining EBID post hoc.

## Experiment 009 — canonical EBID incremental-value test — complete

- [x] Freeze the parent manuscript's entropy-rate feature family before outcome analysis.
- [x] Add the parent manuscript's matched quadratic-distance trajectory baseline.
- [x] Control for nonlinear endpoint geometry, generic dynamic activity, phase, and known structure.
- [x] Compare incremental held-out value in PCC and a matched non-PCC benchmark.
- [x] Repeat the specificity comparison across 30 held-out fold assignments.
- [x] Preserve the non-PCC gain and occasional negative specificity split in the claim boundary.

## Recommended Experiment 010 — stochastic / out-of-distribution EBID replication

1. Add matched stochastic process perturbations to PCC and non-PCC dynamics.
2. Keep the Experiment 009 EBID feature definition completely frozen.
3. Train/calibrate on one noise-strength range and evaluate on held-out noise
   strengths and/or held-out topologies/regimes.
4. Compare EBID against the same geometry, generic-activity, phase/structure,
   and quadratic-trajectory controls.
5. Treat failure to replicate the Experiment 009 specificity margin as direct
   falsification pressure on H6.
