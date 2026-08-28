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

This remains a planned experiment. It should not be stated as a result.


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
