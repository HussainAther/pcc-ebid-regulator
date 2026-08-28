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

## Experiment 010 — stochastic / out-of-distribution EBID replication — complete

- [x] Keep canonical EBID frozen from Experiment 009.
- [x] Add matched tangent-plane stochastic perturbations to PCC and benchmark.
- [x] Train on low/no noise and test on unseen higher noise.
- [x] Evaluate leave-one-topology/regime-out transfer.
- [x] Evaluate joint unseen-noise + held-out-structure transfer.
- [x] Report relative MAE reduction alongside OOD R-squared.
- [x] Preserve the canonical-PCC joint-OOD failure in the claim boundary.

## Recommended Experiment 011 — diagnose topology-dependent EBID transfer

1. Keep EBID frozen again; do not add or remove features.
2. Focus on why canonical PCC fails the joint OOD test while the other three
   topologies benefit strongly.
3. Sweep observation-window length, prediction horizon, strength, and phase.
4. Test whether failure is concentrated in particular cycle phases or strengths.
5. Compare canonical PCC against its reverse topology under exactly paired
   stochastic trajectories.
6. Treat disappearance of the OOD advantage under these diagnostics as evidence
   that Experiment 010 was regime-specific rather than general.

## Experiment 011 — diagnose topology-dependent EBID transfer — complete

- [x] Keep canonical EBID frozen.
- [x] Sweep observation windows 10, 25, and 50 steps.
- [x] Sweep future horizons 20, 40, and 80 steps.
- [x] Diagnose held-out canonical and reverse topologies under unseen noise.
- [x] Stratify transfer by interaction strength and fixed simplex-phase quadrant.
- [x] Preserve negative short-window cells and mixed reverse-topology transfer.

## Recommended Experiment 012 — phase-aware but pre-specified EBID calibration

1. Keep the canonical EBID feature family unchanged.
2. Pre-specify phase-aware calibration (e.g. phase interaction terms) using only
   training data; do not alter EBID itself.
3. Compare against a duration-matched generic entropy-rate baseline.
4. Use independent seeds and denser phase coverage.
5. Test whether phase-aware calibration rescues short-window OOD transfer without
   degrading long-window or non-PCC controls.

## Experiment 012 — phase-aware but pre-specified EBID calibration — complete

- [x] Keep the 11 canonical EBID features unchanged.
- [x] Reuse Experiment 011 data rather than regenerate favorable trajectories.
- [x] Pre-specify first-harmonic `EBID × sin(phase)` and `EBID × cos(phase)` terms.
- [x] Evaluate under held-out topology + unseen-noise joint OOD transfer.
- [x] Use relative MAE and paired bootstrap intervals.
- [x] Preserve the negative result: phase-aware calibration does not rescue the
      short-window failures and usually worsens transfer.

## Recommended Experiment 013 — observation-timescale sufficiency test

1. Treat Experiment 011's observation-window result, not its phase split, as the
   main surviving mechanistic lead.
2. Keep EBID and the plain readout frozen from Experiments 009–011.
3. Sweep a denser, pre-specified observation-duration grid (for example 5–80
   steps) with independent trajectory seeds.
4. Express duration both in raw steps and in estimated fractions of a cycle.
5. Test whether EBID transfer improves at a reproducible fraction-of-cycle
   threshold across coupling strengths/topologies.
6. Include the matched quadratic and non-PCC controls to distinguish a generic
   "more history helps" effect from an EBID/PCC-specific timescale effect.

### Experiment 014 — full-cycle observation scaling

Extend the timescale test beyond the sub-cycle regime. Use observation windows defined directly as fractions of the independently estimated intrinsic period (for example 0.1, 0.25, 0.5, 0.75, 1.0, and 1.5 cycles), keep canonical EBID frozen, and repeat the hard joint-OOD transfer test. Reinstate the matched non-PCC benchmark only if PCC shows a stable transition. Primary target: determine whether EBID benefit becomes consistently positive once observations cover a substantial fraction or multiple of a PCC cycle.

## Experiment 014 — full-cycle observation scaling — complete

- [x] Keep canonical EBID frozen.
- [x] Estimate intrinsic cycle periods independently from long noise-free trajectories.
- [x] Observe `0.10`, `0.25`, `0.50`, `0.75`, `1.00`, and `1.50` cycles.
- [x] Repeat hard held-out-canonical + unseen-noise prediction.
- [x] Use ratio-local calibration as the primary sufficiency test.
- [x] Report global cross-timescale calibration as a secondary analysis.
- [x] Preserve the non-monotonic/borderline one-cycle result and avoid claiming a universal threshold.

### Recommended Experiment 015 — transition-band replication

Repeat the ratio-local test with independent seeds and denser coverage around approximately `0.4–1.2` cycles, using more samples and a pre-specified lower-variance readout. The primary question is whether the first reliable positive region remains near the substantial-cycle regime rather than being a small-sample artifact. Reinstate the non-PCC benchmark only after this transition reproduces.

## Experiment 015 — transition-band replication — complete

- [x] Keep canonical EBID frozen.
- [x] Re-estimate intrinsic periods with an independent seed family.
- [x] Densely sample `0.4–1.2` cycles in `0.1` increments.
- [x] Double replication from 2 to 4 trajectories per cell.
- [x] Use the same fixed standardized ridge readout for baseline and EBID models.
- [x] Preserve the non-monotonic result: `1.0` and `1.2` cycles are reliably positive, while `0.6` is strongly harmful and `1.1` is negative.
- [x] Reject a smooth `~0.75`-cycle threshold interpretation.

### Recommended Experiment 016 — cross-seed scale map

Repeat a smaller set of diagnostic ratios (`0.5`, `0.6`, `0.75`, `1.0`, `1.1`, `1.2`) across several fully independent seed families, keeping periods, EBID, noise split, ridge alpha, and horizon fixed. Estimate the distribution of EBID gain at each cycle fraction rather than a single bootstrap conditional on one simulated dataset. Primary question: are the positive full-cycle cells and the harmful `0.6` cell reproducible across simulation realizations, or is the entire non-monotonic scale map dominated by dataset-level sampling variation? Do not introduce a non-PCC benchmark until this stability question is resolved.

## Experiment 016 — cross-seed scale map — complete

- [x] Keep canonical EBID and the fixed ridge readout unchanged.
- [x] Freeze the Experiment-015 intrinsic-period reference clock.
- [x] Repeat `0.50`, `0.60`, `0.75`, `1.00`, `1.10`, and `1.20` cycles across eight independent seed families.
- [x] Estimate one EBID gain per family×ratio, then bootstrap over independent families.
- [x] Preserve the sign reversals: `0.60` becomes reliably positive and `0.75` reliably negative.
- [x] Reject the Experiment-015 non-monotonic curve as a reproducible scale map.

### Recommended Experiment 017 — leave-one-seed-family-out calibration

At the same six locked cycle fractions, train each ratio-specific baseline and EBID readout on seven complete seed families and evaluate on the eighth, rotating the held-out family. This increases calibration sample size without allowing any trajectories from the held-out simulation family into training. Primary question: does cross-family calibration reveal a stable average timescale effect, or does EBID usefulness remain genuinely family-dependent even when readout estimation is well conditioned? Keep the EBID definition, period references, noise split, horizon, and ridge alpha frozen.

## Experiment 017 — leave-one-seed-family-out calibration — complete

- [x] Reuse the complete Experiment-016 dataset without regenerating trajectories.
- [x] Keep the six diagnostic cycle fractions fixed.
- [x] Train each ratio-specific readout on seven complete seed families and test on the eighth.
- [x] Keep canonical EBID, period references, unseen-noise split, horizon, and ridge alpha frozen.
- [x] Show that cross-family calibration substantially reduces gain variance.
- [x] Identify reproducible positive transfer at `0.60` cycles and especially `1.00` cycle.
- [x] Preserve the non-monotonic result and reject a universal one-cycle threshold.

### Recommended Experiment 018 — matched non-PCC cross-family specificity

At the two ratios with bootstrap-positive PCC gains (`0.60` and `1.00`), generate a matched non-PCC compositional benchmark with the same family structure, strength/noise grid, observation coverage, target, controller, and leave-one-family-out readout protocol. Keep canonical EBID frozen and compute the same entropy-rate feature family on both systems. Primary question: after calibration instability is controlled, is the EBID advantage at these ratios enriched for PCC relative to generic compositional dynamics?
