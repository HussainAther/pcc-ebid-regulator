# Experiment 016 — Cross-seed EBID scale map

## Question

Do the diagnostic observation-scale effects from Experiment 015 reproduce across fully independent simulation seed families when canonical EBID, cycle-period references, noise split, horizon, and ridge readout are all held fixed?

## Locked design

- Cycle fractions: `0.50, 0.60, 0.75, 1.00, 1.10, 1.20`
- Eight independent seed families
- Two trajectories per structure × strength × noise cell in each family
- Frozen Experiment-015 reference cycle periods
- Frozen canonical EBID feature family
- Fixed standardized ridge readout (`alpha = 0.10`)
- Held-out canonical topology and unseen noise (`sigma = 0.01, 0.02`)
- Family-level relative MAE reduction is the primitive effect size
- Bootstrap intervals are computed over the eight independent family-level gains

The complete sweep contains 7,680 simulated trajectories and 48 independent family×ratio evaluations.

## Results

| Cycle fraction | Mean EBID gain | Median | Positive families | Bootstrap CI for mean | Interpretation |
|---:|---:|---:|---:|---:|---|
| 0.50 | -9.2% | +16.4% | 5/8 | -48.3% to +26.8% | mixed |
| 0.60 | **+18.9%** | +16.9% | **7/8** | **+4.4% to +33.6%** | reliably positive |
| 0.75 | **-42.2%** | -27.6% | 3/8 | **-98.1% to -0.1%** | reliably harmful |
| 1.00 | -7.0% | -7.6% | 3/8 | -30.3% to +13.8% | mixed |
| 1.10 | +8.2% | +3.6% | 6/8 | -3.4% to +20.3% | mixed |
| 1.20 | +9.4% | +4.5% | 6/8 | -6.9% to +25.5% | mixed |

The family-to-family spread is large. For example, the 0.50-cycle gain ranges from about `-112%` to `+61%`, and the 0.75-cycle gain ranges from about `-217%` to `+25%`.

## Interpretation

Experiment 016 **does not replicate the Experiment-015 scale map**.

The two most important sign reversals are:

1. Experiment 015 found `0.60` cycles strongly harmful (`-47.8%`). Across eight independent seed families here, `0.60` is the **only ratio with a bootstrap-positive mean gain** (`+18.9%`, 7/8 families positive).
2. Experiment 014 had identified `0.75` cycles as the first reliably favorable local-calibration point. Across seed families here, `0.75` is instead **reliably harmful on average** (`-42.2%`).

Likewise, the Experiment-015 positive cells at `1.00` and `1.20` cycles do not become stable cross-family effects: `1.00` is negative on average, while `1.20` is positive but bootstrap-uncertain.

Therefore the current evidence supports **seed-family / dataset-realization sensitivity**, not a reproducible privileged cycle fraction. Observation scale still changes EBID transfer, but the sign and magnitude of that change are not stable enough to interpret as a deterministic timescale law.

## Claim boundary

Do **not** claim:

- a universal `0.75`-cycle threshold;
- a reproducible `1.0–1.2`-cycle sweet spot;
- a `0.60`-cycle failure region;
- resonance or cycle matching.

The strongest defensible statement is:

> In this toy joint-OOD regulator-difficulty task, canonical EBID transfer is observation-scale sensitive but also strongly dataset-realization sensitive. The non-monotonic scale map from any single simulated dataset is not stable across independent seed families.

## Next experiment

Use **leave-one-seed-family-out calibration** at the same six locked ratios. Train each ratio-specific baseline/EBID readout on seven complete seed families and test on the eighth, rotating the held-out family. This will separate readout instability from genuine trajectory-family heterogeneity while preserving fully out-of-family evaluation.
