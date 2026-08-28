# Hypotheses and Falsification Criteria

This file separates conjectures from established regulator theory.

## H1 — Requisite variety under endogenous instability

**Hypothesis.** As PCC coupling/instability increases, the minimum finite action
repertoire required to keep regulation error below a fixed criterion increases
or becomes more state/trajectory dependent.

**Support would look like:** a reproducible positive association between an
instability descriptor and the empirical minimum regulator variety across
initial conditions and controller families.

**Falsification pressure:** the threshold is invariant to PCC instability, is
fully explained by trivial scaling of action magnitude, or disappears under
matched controls.

## H2 — EBID as a predictor of regulatory demand

**Hypothesis.** An EBID-derived instability statistic predicts regulator demand
better than static state imbalance alone.

**Support would look like:** out-of-sample prediction of requisite variety or
failure probability after controlling for initial state and coupling strength.

**Falsification pressure:** EBID adds no predictive information beyond simpler
baselines.

**Current evidence.** Experiment 008 tests an explicitly *EBID-adjacent*, not
canonical, PCC interaction-activity statistic. After second-order controls for
simplex state and coupling strength, activity improves PCC out-of-sample R² by
about `+0.052`. However, the analogous activity statistic improves the matched
non-PCC benchmark by about `+0.118`. Therefore H2 is **not supported as a
PCC-specific claim under this operationalization**. A canonical EBID statistic
would need to outperform this generic dynamic-activity control.

## H3 — Model adequacy in cyclic PCC regimes

**Hypothesis.** With regulatory action capacity held fixed, a regulator that
represents the relevant PCC transition structure achieves lower long-run error
than a state-only regulator in sufficiently cyclic regimes.

**Support would look like:** an advantage that grows with cycling strength and
survives capacity-matched ablations.

**Falsification pressure:** state-only/history-only controllers match or beat the
PCC-aware model consistently, or any advantage is attributable only to greater
compute, memory, or action capacity.

## H4 — Cycle phase as regulator-relevant information

**Hypothesis.** In non-convergent cyclic regimes, cycle phase carries regulatory
information not recoverable from a coarse state summary alone.

Experiment 008 provides a first weak test. Adding simplex phase to a coarse
imbalance/strength model improves PCC cross-validated R² by about `+0.024`, but
also improves the non-PCC benchmark by about `+0.011`. This is at most weak,
non-specific evidence; H4 remains **unconfirmed**.


## H5 — Structural intervention dimensionality

**Hypothesis.** When the environment can switch among qualitatively distinct PCC
interaction structures, a regulator with access to multiple independent
intervention directions will outperform one restricted to a single component,
and at some fixed performance criteria the minimum intervention dimensionality
will increase with environmental structural variety.

**Current evidence.** Experiment 005 provides threshold-dependent support for a
raw intervention-dimensionality effect. Experiment 006 shows that the effect
survives exact matching of candidate-action cardinality and mean action norm:
the best 2D regulators reduce mean error by roughly 95–98% relative to the best
1D regulators across the tested PCC cells.

Experiment 007 provides an important specificity failure. A non-PCC benchmark
on the same three-component simplex, using exogenous directional selection with
no cyclic pairwise interaction, reproduces the effect almost exactly: its median
2D relative error reduction is 97.2% (range 93.4–98.5%), compared with a median
PCC-minus-benchmark difference of about -0.4 percentage points across matched
cells. Thus the large 1D-to-2D performance jump is best interpreted at present
as **generic compositional controllability geometry**, not a PCC-specific
requisite-variety result.

The narrower statement that multi-direction intervention access matters remains
well supported computationally. The stronger PCC-specific portion of H5 is
**not supported** by Experiment 007.

**Falsification pressure.** The generic dimensionality effect would be weakened
if it disappears after tighter action-entropy/effective-outcome matching or under
stochastic perturbations. A PCC-specific claim now requires some additional PCC
quantity (for example EBID, cycle phase, or topology-dependent prediction) to
explain regulator demand beyond this non-PCC geometric baseline.

## H6 — Canonical EBID adds regulator-demand information beyond local geometry

**Hypothesis.** A frozen canonical EBID entropy-rate feature family adds
held-out predictive information about future regulation difficulty after
controlling for nonlinear endpoint geometry, generic vector-field activity,
cycle phase / known structure, and a matched quadratic-distance trajectory
baseline.

**Experiment 009 evidence.** On the preregistered-style matched dataset,
canonical EBID raises PCC cross-validated R² from about `0.717` to `0.792` after
the quadratic trajectory control, an increment of about `+0.075`. The same
feature family also helps the non-PCC benchmark (`+0.047`), so EBID is not a
uniquely PCC observable. The PCC-minus-benchmark incremental margin is about
`+0.028` in the fixed fold partition. Across 30 repeated 8-fold assignments,
the median margin is about `+0.021` and is positive in `96.7%` of repeats
(range approximately `-0.002` to `+0.044`).

This is **provisional support** for H6 in the current deterministic toy system,
not evidence of a universal PCC-specific law. The non-PCC gain and the one
slightly negative repeated-CV margin both matter. Replication under stochastic
perturbations, alternative horizons, and externally fixed datasets is required.

## H7 — Canonical EBID survives stochastic and structural distribution shift

**Hypothesis.** The frozen canonical EBID feature family retains incremental
predictive value for future regulator difficulty when evaluated on unseen
process-noise levels and held-out PCC structures, beyond endpoint geometry,
generic activity, phase, and quadratic trajectory controls.

**Experiment 010 evidence.** Under unseen noise (`sigma = 0.01, 0.02`) after
training only on `sigma = 0, 0.002, 0.005`, adding EBID reduces PCC MAE by about
`43.9%` (paired bootstrap 95% interval approximately `35.1%–51.3%`) while
increasing matched benchmark MAE by about `13.0%`. In leave-one-structure-out
tests, EBID reduces PCC MAE for all four topologies by about `7–20%`, although
the reverse-topology interval narrowly includes zero. In the stricter joint
noise+structure OOD test, EBID helps three of four PCC topologies strongly
(`36–65%` relative MAE reduction) but does not help canonical PCC (`-2.5%`).

This is **partial support**, not universal replication. The canonical joint-OOD
failure is direct falsification pressure on any claim that EBID is uniformly
sufficient across PCC structures and shifts.

## H8 — EBID transfer is timescale- and phase-dependent

**Hypothesis.** The topology-dependent joint-OOD failures of canonical EBID are
partly caused by insufficient observation of the cyclic trajectory: longer
observation windows should improve transfer, and residual failures may cluster
by cycle phase rather than interaction strength alone.

**Experiment 011 evidence.** With canonical EBID frozen, held-out canonical PCC
shows positive joint-OOD MAE reduction at all three tested future horizons when
the observation window is 50 steps (`+40.5%`, `+9.8%`, `+32.2%`). In contrast,
10- and 25-step observation windows are often harmful, including large negative
transfer at the 40-step horizon. Across fixed simplex-phase quadrants, Q1/Q4 are
positive in 7/9 window×horizon cells while Q2/Q3 are positive in only 4/9.
Interaction strength is non-monotonic and therefore does not explain the failure
by itself.

This is **partial support** for a timescale/phase-dependent interpretation, not
a universal phase law. Reverse topology is also mixed, so canonical orientation
alone is not the cause.

## H9 — Simple phase-aware EBID readout rescues OOD transfer

**Hypothesis.** If the phase pattern observed in Experiment 011 is genuinely
predictive, then adding pre-specified first-harmonic interactions between the
frozen canonical EBID features and simplex phase should reduce joint-OOD
prediction error, particularly in the short-window canonical-PCC regimes that
plain EBID struggled with.

**Experiment 012 evidence.** This hypothesis is **not supported**. With EBID
unchanged and phase represented only by pre-specified `sin(phase)` and
`cos(phase)` interactions, the phase-aware model improves held-out canonical PCC
MAE in only `1/9` observation-window × horizon cells (`1/6` short-window cells
and `0/3` 50-step cells). The single positive canonical cell has a bootstrap
interval crossing zero. The same phase-aware model is also broadly harmful in
the other held-out PCC structures.

The fixed phase-quadrant separation from Experiment 011 should therefore remain
a descriptive lead rather than a predictive phase law. The stronger timescale
result from Experiment 011 remains intact: this experiment tests the readout,
not the frozen EBID definition or the observation-window effect itself.

## H10 — Cycle-fraction sufficiency for EBID transfer

**Hypothesis.** Frozen canonical EBID should become reliably beneficial for hard joint-OOD regulator-difficulty prediction once the observation window spans a sufficient fraction of the intrinsic PCC cycle.

**Experiment 013 status: not supported over the sampled sub-cycle range.** A dense 5–80 step sweep, corresponding to roughly 0.004–0.285 intrinsic cycles across tested strengths, did not show a stable monotonic onset. EBID was worse than the controlled baseline in most windows; the 0.20–0.30 cycle-ratio bin was only slightly positive. The experiment therefore does not establish a critical cycle fraction. The next test must extend to observation windows covering at least ~0.5–1.5 cycles.

## H11 — Substantial cycle coverage stabilizes local EBID transfer

**Hypothesis.** When canonical EBID is calibrated separately at each observation scale, hard joint-OOD transfer should become reliably beneficial only after the observation window covers a substantial fraction of the intrinsic PCC cycle.

**Experiment 014 status: partial support.** Ratio-local fits are strongly harmful at `0.10` cycle, negative at `0.25`, weakly positive but uncertain at `0.50`, and first become bootstrap-positive at `0.75` cycle (`+33.5%` relative MAE reduction; 95% interval approximately `+6.6%` to `+52.4%`). `1.50` cycles is also reliably positive, while `1.00` cycle is positive but borderline. However, a single model calibrated across all observation ratios is positive even at `0.10` cycle. Thus the data support cycle-coverage-dependent **local identifiability/calibration**, not a universal physical threshold at `0.75` cycles.

## H12 — The substantial-cycle transition replicates densely

**Hypothesis.** The transition toward reliable local canonical-EBID transfer seen in Experiment 014 should reproduce with independent seeds, denser `0.4–1.2` cycle coverage, more samples, and a fixed lower-variance readout, with a stable first reliable region near the substantial-cycle regime.

**Experiment 015 status: not supported as a smooth threshold; partial support for observation-scale dependence.** With four replicates per cell and a fixed standardized ridge readout, the first bootstrap-positive ratio shifts from `0.75` in Experiment 014 to `1.00` cycle (`+30.2%`, 95% interval approximately `+11.9%` to `+46.7%`). `1.20` cycles is also strongly positive (`+37.9%`, approximately `+20.6%` to `+50.5%`). However, the curve is non-monotonic: `0.60` cycles is strongly harmful (`-47.8%`) and `1.10` cycles is negative. Thus a single critical cycle-fraction threshold does not replicate. The surviving result is observation-scale sensitivity with favorable full-cycle-scale regions, not a universal cutoff.

## H13 — The non-monotonic EBID scale map is reproducible across seed families

**Hypothesis.** The diagnostic observation-scale pattern from Experiment 015 — including harmful transfer near `0.60` cycles and favorable transfer near `1.00–1.20` cycles — should retain its sign structure across fully independent simulation seed families when the EBID definition, cycle-period references, noise split, horizon, and ridge readout are fixed.

**Experiment 016 status: not supported.** Across eight independent seed families, the scale map changes substantially. `0.60` cycles becomes the only bootstrap-positive mean effect (`+18.9%`, 7/8 families positive), while `0.75` cycles is bootstrap-negative on average (`-42.2%`). `1.00` cycles is negative on average, and `1.20` is positive but uncertain. Family-to-family variation is large at every ratio.

The repository therefore does **not** support a reproducible privileged cycle fraction or a stable full-cycle sweet spot. The surviving claim is weaker: EBID transfer is observation-scale sensitive, but the observed scale map is strongly dependent on the particular simulated trajectory family. A leave-one-seed-family-out calibration test is needed to distinguish unstable small-sample readout fitting from genuine family-level dynamical heterogeneity.

## H14 — Cross-family calibration stabilizes EBID transfer

**Hypothesis.** If the extreme family-to-family sign reversals in Experiment 016 are primarily a small-sample calibration artifact, then fitting the frozen baseline/EBID readouts on seven complete simulation families and evaluating on the eighth should reduce gain variance and reveal more stable ratio-specific transfer effects.

**Experiment 017 evidence.** Supported in part. Cross-family calibration sharply reduces the dispersion of family-level EBID gains and removes several Experiment-016 reversals. At `0.60` cycles the mean held-out-family gain is `+15.3%` with a bootstrap interval entirely above zero. At `1.00` cycle the mean gain is `+23.6%`, the bootstrap interval is about `+14.6%` to `+32.9%`, and all 8/8 held-out families improve. `0.75` moves from strongly harmful in Experiment 016 to approximately neutral. However, `1.10` remains slightly negative and `1.20` is only borderline positive.

**Claim boundary.** Experiment 017 supports the conclusion that readout-estimation instability explained a substantial part of Experiment 016's jagged scale map. It does **not** establish a universal one-cycle threshold or monotonic cycle-coverage law. The next specificity test must determine whether the stabilized `0.60`/`1.00` effects exceed matched non-PCC dynamics under the same leave-family-out protocol.

## H15 — Stabilized EBID transfer is enriched for PCC versus generic compositional dynamics

**Hypothesis.** At the two observation scales that remained bootstrap-positive after Experiment 017 cross-family calibration (`0.60` and `1.00` PCC reference cycles), frozen canonical EBID should add more predictive value for held-out PCC regulator difficulty than for a matched non-PCC compositional benchmark under the same leave-one-family-out protocol.

**Experiment 018 evidence.** Supported for the current benchmark. At `0.60`, PCC gains `+15.3%` relative MAE reduction while the benchmark averages `-5.7%`, giving a paired family-level specificity margin of `+21.0` percentage points (bootstrap interval about `+5.8` to `+37.8`). At `1.00`, PCC gains `+23.6%` while benchmark EBID is harmful in all 8/8 families and averages `-203.5%`, yielding a `+227.0` percentage-point specificity margin (about `+186.2` to `+271.0`).

**Claim boundary.** This supports PCC enrichment relative to the current generic directional-selection benchmark, not uniqueness to PCC among all cyclic or nonlinear systems. A matched oscillatory non-PCC control is needed to separate PCC structure from cyclicity itself.

## H16 — Stabilized EBID transfer is enriched for PCC versus generic oscillatory dynamics

**Hypothesis.** At the stabilized `0.60` and `1.00` PCC-reference observation scales, canonical EBID should add more held-out-family regulator-demand information for PCC than for a matched oscillatory but explicitly non-PCC compositional system.

**Experiment 019 status: not supported.** At `0.60`, the oscillatory non-PCC control gains `+49.3%` relative MAE reduction versus `+15.3%` for PCC, producing a paired PCC-minus-control margin of `-34.0` percentage points with a bootstrap interval entirely below zero (`-46.3` to `-21.8` pp). At `1.00`, PCC gains `+23.6%` and the oscillatory control gains `+22.8%`; the `+0.8` pp margin is indistinguishable from zero (`-12.4` to `+13.4` pp).

**Claim boundary.** Experiment 018 demonstrated enrichment versus a non-oscillatory directional benchmark, but Experiment 019 shows that the enrichment does not survive a matched oscillatory control. Current evidence therefore supports EBID as a useful dynamical-history predictor in some regulator tasks, but not as uniquely PCC-specific. The next specificity question should identify which dynamical-class properties — oscillation, damping, non-transitivity, exogenous versus endogenous cycling, etc. — govern EBID's incremental value.

## H17 — EBID benefit is organized by broad dynamical class

**Question.** Is the stabilized EBID regulator-demand benefit specific to PCC, generic to oscillators, or associated with a broader dynamical property?

**Experiment 020 result:** no single coarse class property explains the panel. Persistent and damped oscillators are strongly positive at 0.60 cycles, but the damped oscillator loses the benefit at 1.00; neutral diffusion is strongly positive at 1.00 despite having no deterministic oscillation; directional flow is harmful. Therefore "PCC-specific" and "oscillation-specific" versions of H17 are not supported. A broader trajectory-history explanation remains open.

## H17 — Continuous trajectory properties explain EBID regulator value
**Hypothesis.** Pre-horizon trajectory properties can predict the incremental value of canonical EBID for future regulator-demand prediction beyond coarse dynamical-class identity.

**Experiment 021 result: partially supported.** Across 80 frozen class × family × scale folds, non-EBID trajectory summaries improved leave-one-family-out prediction by 22.5% MAE beyond a class+scale baseline (cross-family R² ≈ 0.74). Endpoint-imbalance variability and mean activity were the strongest positive rank correlates. However, leave-one-class-out prediction failed badly, so the current descriptor mapping is not a universal cross-class law.

**Claim boundary.** H17 supports within-panel interpolation across unseen trajectory families, not extrapolation to an unseen dynamical mechanism. No causal interpretation is assigned to the individual descriptors.
