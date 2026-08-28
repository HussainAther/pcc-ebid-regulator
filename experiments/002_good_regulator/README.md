# Experiment 002: Model Content and Regulation

Compare matched-capacity regulators with different internal representations:

1. current state only,
2. state + short history,
3. state + known PCC interaction topology,
4. state + topology + estimated cycle phase.

Primary outcome: long-run regulation error under cyclic PCC dynamics.

The important control is parameter/memory capacity: a topology-aware regulator should not win merely because it was given a larger model.
