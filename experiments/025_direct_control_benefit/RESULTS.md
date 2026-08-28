# Experiment 025 — Direct EBID to controlled-future coupling

## Question

Does frozen canonical EBID predict how much a standardized regulator can improve the future, rather than merely predicting whether EBID helps another predictor?

For each prospective Experiment-022 observation endpoint, we compare:

1. a 40-step deterministic uncontrolled future; and
2. a 40-step optimistic greedy controlled future using the same 9-action, two-channel repertoire for every dynamical class.

The primary target is

`relative control benefit = (uncontrolled mean error - oracle mean error) / uncontrolled mean error`.

## Strong baseline

The baseline contains observation scale, endpoint composition, coupling strength, the full quadratic-distance trajectory feature family, and generic activity history. Canonical EBID is then added without modification.

## Leave-one-dynamical-class-out result

| Held-out class | EBID MAE reduction | EBID model R² | Mean control benefit |
|---|---:|---:|---:|
| PCC | +26.1% | 0.852 | 0.566 |
| persistent oscillator | +19.5% | 0.678 | 0.453 |
| damped oscillator | +31.7% | 0.709 | 0.598 |
| directional flow | +38.8% | 0.626 | 0.107 |
| neutral diffusion | +28.0% | 0.679 | 0.707 |
| **pooled** | **+28.8%** | **0.863** | **0.486** |

Paired bootstrap intervals for the MAE improvement are entirely positive for every held-out class; the pooled interval is approximately `+27.0%` to `+30.6%`.

## Known-class, held-out-family result

When dynamical classes are represented during calibration but a complete seed family is unseen, adding EBID reduces MAE by **27.4%** and increases R² from approximately `0.788` to `0.892`.

## Critical ablation

The full EBID improvement should not be interpreted as evidence that entropy-*rate* terms drive the result.

Pooled across held-out classes:

- strong non-entropic baseline → + entropy initial/mean/end: **+26.6%** MAE reduction;
- entropy-level/history model → + remaining rate/deficit-rate features: only **+3.0%** additional reduction;
- full EBID family versus baseline: **+28.8%**.

For PCC specifically, the additional rate-feature increment beyond entropy initial/mean/end is only about **+1.4%**.

## Interpretation

Experiment 025 is the first experiment in the later regulator sequence to show a strong positive result on the *direct regulator quantity itself* rather than on the meta-question of predicting EBID usefulness. Entropy history transfers across unseen mechanisms as a predictor of how much an optimistic regulator can improve future error.

The result is broader than PCC and appears to be driven primarily by entropy level/history rather than the canonical rate terms. Therefore it supports a general entropy-history/control-benefit relationship in this matched simplex panel, not a PCC-specific EBID-rate law.
