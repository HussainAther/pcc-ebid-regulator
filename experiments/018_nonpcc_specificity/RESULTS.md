# Experiment 018 — matched non-PCC cross-family specificity

## Question

After Experiment 017 stabilized canonical-EBID transfer at `0.60` and `1.00` PCC reference cycles, are those gains enriched for PCC relative to a matched generic compositional benchmark?

## Locked comparison

The canonical EBID feature family, standardized ridge readout (`alpha=0.10`), eight seed families, noise split, strengths, horizon, target, family holdout structure, and sample counts are unchanged. The non-PCC benchmark is directional rather than cyclic, so the PCC intrinsic period is used only as a shared **absolute observation-time ruler**. No benchmark cycle period is invented.

At each ratio, seven benchmark seed families and three non-primary benchmark regimes are used for calibration at training noise levels. The eighth family's primary `pressure_bias` regime is evaluated at unseen noise levels, exactly paralleling Experiment 017's held-out canonical-PCC evaluation.

## Results

| PCC reference-cycle coverage | PCC EBID gain | Benchmark EBID gain | PCC-specificity margin | Paired margin 95% CI |
|---:|---:|---:|---:|---:|
| 0.60 | +15.3% | -5.7% | **+21.0 pp** | **+5.8 to +37.8 pp** |
| 1.00 | +23.6% | -203.5% | **+227.0 pp** | **+186.2 to +271.0 pp** |

At `0.60`, benchmark EBID improves only 3/8 held-out families and its mean effect is not distinguishable from zero. PCC improves 6/8 families and has a bootstrap-positive mean effect.

At `1.00`, benchmark EBID is harmful in all 8/8 held-out families. This is not a tiny-denominator artifact: benchmark baseline MAE is approximately `0.06–0.12`, whereas the EBID-augmented model rises to approximately `0.21–0.32` MAE. Long directional-selection trajectories become strongly low-entropy / corner-concentrated, and the frozen entropy-rate feature family transfers poorly across the held-out directional regime.

## Interpretation

Experiment 018 supports a **PCC-enriched specificity claim at the two observation scales that survived Experiment 017 cross-family calibration**. In this matched toy comparison, canonical EBID adds predictive information about future regulator difficulty for PCC that is absent—or actively misleading—in generic directional compositional dynamics.

The result is strongest at `1.00` PCC reference cycle, where PCC improves in all 8/8 held-out families while benchmark EBID worsens in all 8/8 families.

## Claim boundary

This does **not** establish that EBID is uniquely informative for all PCC systems, that one cycle is a universal threshold, or that every non-PCC system should show negative EBID transfer. The benchmark is one deliberately simple non-transitive-free compositional control. The appropriate claim is narrower:

> Under matched family-level OOD calibration and matched observation durations, the stabilized EBID gains at `0.60` and `1.00` PCC reference cycles are substantially enriched for PCC relative to the current generic directional benchmark.

A stronger next test would compare PCC against additional oscillatory but non-PCC controls so that cyclicity itself is not confounded with PCC structure.
