# Experiment 006 — Capacity-matched intervention dimensionality

## Question

Does the two-channel advantage from Experiment 005 survive when one- and
two-channel regulators have the same number of candidate actions and the same
mean intervention magnitude?

## Design

- Active topology is known perfectly by the regulator.
- Candidate-action cardinality is matched at `K = 5, 9, 17`.
- Mean L2 norm of each repertoire is matched between 1D and 2D action sets.
- One-dimensional families: `P`, `C`, `Ch`.
- Two-dimensional families: `P+C`, `P+Ch`, `C+Ch`.
- Structural variety uses 1, 2, and 4 available topologies.
- Topology dwell times: `20`, `50`.
- Three distinct initial compositions are tested.

For one-channel regulators, K scalar levels are spread across the accessible
axis. For two-channel regulators, the same K consists of a zero action plus
angularly distributed actions in the accessible coordinate plane; the radius
is scaled so the mean action norm matches the one-channel repertoire.

## Result

The advantage survives capacity matching. Across all tested cells, the best 2D
family reduces mean error by roughly 95–98% relative to the best 1D family.
With four topologies and dwell 50, for example, K=9 gives mean errors of
`0.239551` (best 1D) versus `0.005250` (best 2D), a 97.8% reduction.

However, the 2D advantage is already very large with one topology. Experiment
006 therefore supports the claim that **qualitatively distinct intervention
directions matter beyond raw action cardinality**, but does not establish that
increasing topology count monotonically increases the value of dimensionality.

## Interpretation rule

Support for H5 is strengthened if the best 2D regulator retains a substantial
error advantage after these capacity controls across topologies, dwell times,
action-set sizes, and initial states. That condition is met here.

A 2D win here is still not a theorem about requisite variety. It establishes a
computational intervention-geometry effect in this PCC toy model.
