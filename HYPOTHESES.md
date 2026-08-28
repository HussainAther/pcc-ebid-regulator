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

**Current evidence.** Experiment 005 provides threshold-dependent support. At a
mean-error criterion of `0.100`, one topology passes with one intervention
channel, whereas two-to-four switching topologies require two channels across
all tested dwell times. Experiment 006 strengthens the intervention-dimensionality
part of H5: after exactly matching candidate-action cardinality and mean action
norm, the best 2D regulators still reduce mean error by roughly 95–98% relative
to the best 1D regulators across tested cells and three initial conditions.
However, the 2D advantage is already comparably large with one topology, so the
stronger claim that increasing structural variety monotonically *causes* the
need for additional dimensionality is not supported by Experiment 006.

**Falsification pressure.** The dimensionality effect disappears after matching
action entropy/cardinality and intervention magnitude, fails across initial
conditions or stochastic perturbations, or is reproduced entirely by a simpler
non-PCC control benchmark.
