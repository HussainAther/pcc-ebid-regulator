# Experiment 017 — Leave-one-seed-family-out calibration

## Question

Was the jagged cross-seed scale map in Experiment 016 mainly caused by fitting each small seed family separately, or does canonical EBID remain genuinely unstable when the readout is calibrated on substantially more independent trajectory families?

## Locked design

- Reuse the complete Experiment-016 dataset; no favorable trajectories are regenerated.
- Cycle fractions remain fixed at `0.50, 0.60, 0.75, 1.00, 1.10, 1.20`.
- Eight independent simulation seed families.
- At each ratio and fold, train on seven complete families using the same noncanonical structures and low-noise training split as Experiment 016.
- Evaluate only on the eighth family's canonical topology at unseen noise (`sigma = 0.01, 0.02`).
- Frozen canonical EBID features.
- Same standardized ridge readout (`alpha = 0.10`).
- Each fold has 504 training trajectories and 16 fully out-of-family test trajectories.
- Relative MAE reduction is the primary effect size; family-level means are bootstrapped across the eight held-out families.

## Results

| Cycle fraction | Mean EBID gain | Positive held-out families | Bootstrap CI for mean | Interpretation |
|---:|---:|---:|---:|---|
| 0.50 | +9.7% | 6/8 | -4.9% to +24.6% | positive but uncertain |
| 0.60 | **+15.3%** | 6/8 | **+4.5% to +26.2%** | reliably positive |
| 0.75 | +1.8% | 5/8 | -8.2% to +11.0% | near neutral |
| 1.00 | **+23.6%** | **8/8** | **+14.6% to +32.9%** | robustly positive |
| 1.10 | -3.0% | 3/8 | -9.6% to +2.7% | near neutral / slightly negative |
| 1.20 | +5.1% | 7/8 | -0.1% to +10.2% | positive but borderline |

Pooling calibration across seven families dramatically reduces family-to-family spread. For example, at `0.75` cycles the standard deviation of family gains falls from about `0.78` in Experiment 016 to about `0.15` here; at `1.00` cycle it falls from about `0.34` to `0.14`.

The largest qualitative reversals relative to Experiment 016 are:

1. `0.75` cycles moves from a mean `-42.2%` EBID effect to essentially neutral (`+1.8%`).
2. `1.00` cycle moves from `-7.0%` to **+23.6%**, with EBID helping all 8 held-out families.
3. `0.50` cycles moves from `-9.2%` to `+9.7%`, though the mean remains uncertain.
4. `0.60` remains reliably positive under both local and cross-family calibration.

## Interpretation

Experiment 017 shows that a substantial part of the jagged Experiment-016 scale map came from **small-sample readout instability**. Better-conditioned calibration across independent simulation families collapses several extreme sign reversals and reveals two ratios with reproducible average benefit: `0.60` and especially `1.00` cycle.

However, this is still **not** evidence for a monotonic cycle-coverage threshold. `1.10` is slightly negative, `0.75` is neutral, and `1.20` is only borderline. The result is therefore better described as a stable **ratio-dependent transfer profile under cross-family calibration**, not a universal law of cycle fraction.

The strongest new finding is:

> With the EBID definition, period references, noise split, horizon, and ridge readout frozen, canonical EBID improves out-of-family regulator-difficulty prediction at `1.00` cycle in all eight held-out simulation families, with a mean relative MAE reduction of about 23.6%.

## Claim boundary

Do **not** claim:

- a universal one-cycle threshold;
- monotonic improvement with cycle coverage;
- that the `1.00`-cycle effect is PCC-specific until a matched non-PCC control is rerun under the same leave-family-out protocol;
- that family heterogeneity is absent. Some ratios remain mixed even after calibration is stabilized.

## Recommended Experiment 018

Reintroduce the matched non-PCC compositional benchmark at the two cross-family-positive PCC ratios (`0.60` and `1.00`), using the same leave-one-family-out calibration protocol and frozen feature/readout families. The key specificity question is whether the stabilized EBID advantage is larger for PCC than for generic compositional dynamics when both are tested out of family and out of noise distribution.
