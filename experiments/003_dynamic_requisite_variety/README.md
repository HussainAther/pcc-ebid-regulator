# Experiment 003 — Dynamic requisite variety under parameter drift

This experiment asks whether nonstationarity increases the finite action
repertoire needed to maintain a fixed regulation-error criterion.

To isolate **action variety** from **model adequacy**, the regulator receives the
current true coupling strength at every step. This is an intentionally
optimistic oracle controller, not a realistic adaptive regulator.

Two drift families are tested:

1. sinusoidal coupling strength with varied amplitude and period;
2. mean-reverting stochastic random-walk coupling strength across repeated seeds.

The primary output is the empirical minimum repertoire size that satisfies
several predeclared mean-error criteria. If the minimum repertoire is unchanged
across drift levels, H1 is not supported in this model even under
nonstationarity.
