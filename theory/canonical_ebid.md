# Canonical EBID operationalization used here

Experiment 009 freezes the entropy-rate feature family from the parent PCC/EBID
manuscript rather than inventing a regulator-specific statistic after seeing
outcomes.

For a three-component composition trajectory,

\[
H(t)=-\sum_i x_i(t)\log x_i(t),\qquad
D(t)=\log 3-H(t).
\]

The parent manuscript's early-window entropy feature set is:

- initial entropy,
- mean entropy,
- end-window entropy,
- entropy drop,
- entropy slope,
- mean entropy rate,
- minimum entropy rate,
- entropy-rate variance,
- deficit growth,
- maximum deficit rate,
- deficit-rate variance.

`src/pcc_ebid_regulator/ebid.py` is the frozen implementation used by
Experiment 009. Finite differences use one simulation step as the time unit.
No feature was added, removed, or retuned after inspecting Experiment 009's
regulation-error outcomes.

## Important local-geometry control

The parent EBID manuscript explicitly states that near the symmetric interior
equilibrium, entropy deficit is locally quadratic and therefore shares leading
geometry with quadratic distance / Lyapunov-like observables. Experiment 009
therefore also computes

\[
Q(t)=\|x(t)-x^*\|^2
\]

and matched finite-time trajectory/rate summaries. The primary EBID test is its
incremental held-out predictive value **after this quadratic trajectory
baseline**, not merely after a static state baseline.

## Claim boundary

This repo treats EBID as a predictive observable layer, not as a replacement
for Lyapunov theory. A positive Experiment 009 result means only that the frozen
entropy-rate feature family carries additional finite-time information about
future regulator difficulty in this toy setting.
