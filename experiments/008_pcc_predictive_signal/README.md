# Experiment 008 — PCC-specific predictive signal

## Question

After controlling for generic three-component simplex geometry, do candidate
PCC-related dynamic descriptors predict future regulation difficulty better
than corresponding descriptors in a non-PCC compositional benchmark?

## Design

- 320 shared initial states sampled from a Dirichlet distribution.
- Strengths: 0.5, 1.0, 1.5, 2.0, 3.0.
- PCC structural regimes: canonical, reverse, and two edge-removal topologies.
- Non-PCC controls: four exogenous directional-selection regimes.
- Fixed capacity: a 9-action, one-channel Control repertoire.
- Outcome: mean regulation error over the next 50 steps under a regime-aware
  greedy regulator.
- Candidate signals:
  - static imbalance / entropy deficit;
  - simplex phase;
  - instantaneous vector-field norm (`activity`).

`pcc_interaction_activity` is deliberately described as **EBID-adjacent**. It
is not asserted to be the canonical EBID statistic.

## Main comparison

Cross-validated linear prediction is evaluated from coarse static features and
from a nonlinear geometry control (second-order terms in P, C, and strength),
with and without the activity signal. The exact same analysis is run on the
non-PCC benchmark.
