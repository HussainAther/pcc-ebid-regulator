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

## Experiment 018 — matched non-PCC cross-family specificity — complete

- [x] Restrict the test to the Experiment-017 bootstrap-positive ratios (`0.60`, `1.00`).
- [x] Keep canonical EBID, ridge alpha, family structure, noise split, horizon, target, and sample counts fixed.
- [x] Use the PCC intrinsic period only as a shared absolute observation-time ruler for the non-cyclic benchmark.
- [x] Run leave-one-family-out benchmark calibration with the same train/test structure.
- [x] Compute paired family-level PCC-minus-benchmark specificity margins and bootstrap intervals.
- [x] Show positive PCC enrichment at both locked ratios.

### Recommended Experiment 019 — oscillatory non-PCC specificity control

Construct a matched three-component **oscillatory but non-PCC** control (for example, a linear/stable rotational flow projected to the simplex or another explicitly non-nontransitive oscillator) and repeat the locked `0.60` / `1.00` cross-family protocol. Primary question: does canonical EBID remain enriched for PCC once generic cyclicity and timescale structure are present in the control?

### Experiment 019 — oscillatory non-PCC specificity control

- [x] Build an externally forced cyclic three-component benchmark with no endogenous PCC/RPS interaction.
- [x] Match its forcing period to the PCC intrinsic reference period at each strength.
- [x] Reuse the locked `0.60` / `1.00` observation scales and leave-one-family-out OOD protocol.
- [x] Keep canonical EBID, target, horizon, ridge readout, noise split, and sample counts fixed.
- [x] Compute paired family-level PCC-minus-oscillator specificity margins.
- [x] Show that PCC specificity does **not** survive the oscillatory control.

### Recommended Experiment 020 — matched dynamical-class panel

Replace one-control-at-a-time specificity with a small pre-specified panel spanning distinct mechanisms: canonical PCC, externally forced oscillator, damped oscillator, directional compositional flow, and neutral/noisy simplex dynamics. Use the same cross-family protocol and frozen EBID features. Primary question: which dynamical properties (oscillation, damping, endogenous non-transitivity, persistence, entropy cycling) explain EBID's incremental regulator-demand value? This should be analyzed as a class-level comparison rather than another search for a single favorable comparator.

## Experiment 021 — matched trajectory-statistics panel

Replace coarse class labels with continuous, pre-specified trajectory descriptors measured before the prediction horizon: entropy excursion, entropy-rate variance, state displacement, path length, return/persistence, spectral concentration, and net directional drift. Test which descriptors predict the *incremental* EBID gain across class × family × scale while keeping EBID itself frozen. This is the next step before proposing a general dynamical condition for EBID usefulness.

## Experiment 021 — matched trajectory-statistics panel — complete

- [x] Reuse the frozen 016–020 trajectories/summaries and family-level EBID gains.
- [x] Exclude canonical EBID/entropy features from the explanatory descriptor set.
- [x] Build all 80 class × family × scale fold summaries.
- [x] Quantify descriptor–EBID-gain associations with family-cluster bootstrap intervals.
- [x] Test leave-one-family-out prediction against scale-only and class+scale baselines.
- [x] Test strict leave-one-dynamical-class-out extrapolation.
- [x] Preserve the negative cross-class result instead of promoting an interpolation model to a universal law.

### Recommended Experiment 022 — prospective raw-path invariants

Generate a matched prospective panel in which the raw observation paths are retained for every dynamical class. Pre-specify mechanism-agnostic descriptors unavailable in the frozen summary datasets: total path length, net displacement/path-length ratio, recurrence/return probability, lagged autocorrelation, spectral concentration, turning-angle persistence, and entropy-free state-space occupancy. Use leave-one-class-out as the primary validation protocol. The target question is whether richer path geometry can predict EBID usefulness in a truly unseen dynamical class.

## Experiment 022 — prospective raw-path invariants — complete

- [x] Regenerate a matched five-class panel prospectively.
- [x] Retain every raw observation trajectory in compressed `.npz` archives.
- [x] Pre-specify mechanism-agnostic, non-EBID path invariants.
- [x] Keep canonical EBID and regulator-demand readout frozen.
- [x] Make leave-one-dynamical-class-out prediction the primary test.
- [x] Run a secondary leave-one-family-out known-class control.
- [x] Preserve the negative result without post-hoc feature selection.

**Result:** simple raw-path invariants do not generalize. They worsen cross-class MAE by about 47% and known-class held-out-family MAE by about 34%.

## Recommended Experiment 023 — predictive / response invariants

Move beyond path morphology. Prospectively estimate quantities that encode the **transition law and response structure** without using EBID itself, for example:

- one-step forecast error from a common local linear model,
- finite-time local Jacobian / sensitivity norm,
- response amplification to matched infinitesimal perturbations,
- state-action coupling / controllability proxy,
- innovation variance after local prediction,
- short-horizon predictability decay.

Use the same five-class panel and make leave-one-dynamical-class-out EBID-gain prediction the primary endpoint. The purpose is to test whether EBID usefulness is organized by **forecastability and response structure**, rather than raw path shape.

## Experiment 024 — finite-horizon controllability / response memory

**Motivation:** Experiments 022–023 show that static path morphology and local response invariants do not generalize across dynamical mechanisms.

**Primary question:** Does EBID become useful when the observed history predicts the *set and separation of controlled future trajectories* rather than merely local next-step response?

Pre-specify a small mechanism-agnostic family of finite-horizon quantities, for example:

- multi-step perturbation amplification,
- action-conditioned reachable-set volume,
- contraction / expansion of trajectories under a fixed intervention repertoire,
- decay time of perturbation memory,
- action-conditioned forecast variance.

Use leave-one-dynamical-class-out prediction as the primary endpoint and retain the frozen canonical EBID definition.

## Experiment 024 — finite-horizon controllability / response memory

**Status:** complete; cross-class hypothesis not supported.

Five- and twenty-step perturbation-memory and action-spread descriptors do not generalize EBID usefulness to unseen dynamical mechanisms. Leave-one-class-out MAE worsens by 56.4% overall; known-class family transfer is approximately neutral.

## Experiment 025 — direct EBID-to-controlled-future coupling

**Priority:** next.

Stop adding meta-level handcrafted descriptors. Instead, within each observed trajectory window, pair frozen canonical EBID with directly computed future regulator quantities under a standardized intervention repertoire:

1. uncontrolled future error;
2. best achievable finite-horizon controlled error;
3. control benefit (`uncontrolled - best controlled`);
4. reachable-set contraction toward the target;
5. action ranking stability / ambiguity.

Primary tests:

- Does EBID predict these action-conditioned future quantities beyond current state/geometry?
- Does the incremental EBID relationship transfer across seed families?
- Does its sign/strength transfer across dynamical classes?

This is closer to the regulator-theorem question than another attempt to infer EBID usefulness from scalar path summaries.

## Experiment 025 — direct EBID-to-controlled-future coupling

**Status:** complete; positive cross-class result with a strong ablation caveat.

Frozen canonical EBID reduces leave-one-class-out MAE for standardized future control benefit by 28.8% beyond endpoint geometry, quadratic trajectory history, and generic activity. However, 26.6 percentage points of the baseline-relative gain are already obtained from initial/mean/end entropy; rate features add only ~3% further pooled improvement.

## Recommended Experiment 026 — entropy-history versus EBID-rate decomposition

The direct-control result should now be decomposed prospectively rather than expanded with new handcrafted descriptors. Pre-specify four nested representations:

1. state/geometry + generic dynamics;
2. + endpoint entropy only;
3. + entropy history levels (initial/mean/end);
4. + canonical EBID rate/deficit-rate terms.

Use the same direct control-benefit target and leave-one-class-out / leave-one-family-out protocols. Add nonlinear geometry controls so endpoint entropy cannot win merely by providing a convenient nonlinear basis for composition. The primary question is whether *history* or *rates* add anything beyond an equivalently expressive state representation.

## Experiment 027 — matched-history sufficiency / history scrambling

Directly test whether the residual Experiment-026 temporal signal depends on *ordered trajectory history* rather than summary statistics alone. Keep endpoint state and endpoint entropy fixed while comparing true histories with pre-specified history controls (time reversal, within-window permutation where admissible, and matched initial/mean entropy summaries). Primary question: does preserving temporal ordering improve direct control-benefit prediction beyond the same entropy marginals?
