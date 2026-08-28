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
