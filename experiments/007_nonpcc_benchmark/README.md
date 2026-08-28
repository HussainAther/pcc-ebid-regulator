# Experiment 007 — Non-PCC compositional specificity benchmark

## Question

Is the large capacity-matched 2D intervention advantage from Experiment 006
specific to PCC/non-transitive interaction, or does the same effect occur in a
simpler three-component compositional control problem?

## Benchmark

The benchmark uses the same Pressure/Control/Chaos simplex, target, intervention
semantics, action cardinalities, mean action norms, initial conditions, and
switching dwell times as Experiment 006. The endogenous PCC interaction matrix
is removed. Instead, each regime applies a fixed exogenous fitness/bias vector
(`pressure_bias`, `control_bias`, `chaos_bias`, or `mixed_bias`). There is no
rock-paper-scissors cycle and no state-dependent pairwise interaction.

## Specificity rule

If the 95–98% 2D advantage from Experiment 006 is reproduced at similar scale in
this non-PCC benchmark, the dimensionality result should be interpreted mainly
as generic compositional controllability geometry rather than a PCC-specific
requisite-variety phenomenon. A materially stronger or differently scaling PCC
effect would motivate a specificity claim.
