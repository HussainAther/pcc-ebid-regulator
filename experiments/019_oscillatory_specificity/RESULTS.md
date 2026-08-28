# Experiment 019 — Oscillatory non-PCC specificity control

## Question

Does the stabilized canonical-EBID advantage from Experiment 017 remain enriched for PCC after the comparison system is itself cyclic/oscillatory?

The control is a three-component simplex system driven by an **external periodic bias**. It has matched PCC reference periods and matched absolute observation windows, but no endogenous pairwise dominance or rock-paper-scissors/PCC interaction matrix.

The locked observation scales are `0.60` and `1.00` PCC reference cycles. Evaluation uses the same leave-one-seed-family-out structure, unseen-noise test split, future horizon, ridge readout, target, sample counts, and frozen canonical EBID feature family as Experiments 017–018.

## Results

| PCC-reference observation scale | PCC mean EBID gain | Oscillatory non-PCC mean gain | PCC − oscillatory margin | Paired family bootstrap interval |
|---:|---:|---:|---:|---:|
| 0.60 | +15.3% | **+49.3%** | **−34.0 pp** | **−46.3 to −21.8 pp** |
| 1.00 | +23.6% | **+22.8%** | **+0.8 pp** | **−12.4 to +13.4 pp** |

At `0.60`, EBID improves the oscillatory benchmark in **8/8** held-out families, versus 6/8 for PCC. The family-level oscillatory gains range from roughly +40% to +60%.

At `1.00`, EBID improves the oscillatory benchmark in **7/8** held-out families. PCC is positive in 8/8 families, but the mean PCC-minus-control margin is effectively zero and its bootstrap interval comfortably crosses zero.

## Interpretation

Experiment 019 **does not support PCC specificity against a matched oscillatory control**.

The strong PCC-versus-directional-benchmark separation in Experiment 018 was therefore substantially driven by the fact that the earlier control was non-oscillatory. Once generic cyclicity and matched timescale structure are introduced, frozen canonical EBID is at least as useful for the non-PCC oscillator as it is for PCC at the two previously stabilized observation scales.

This narrows the regulator-line claim:

- canonical EBID can carry real cross-family information about future regulator difficulty;
- that information is not explained merely by endpoint geometry or action-space dimensionality;
- but the current evidence does **not** show that this predictive value is unique to PCC rather than a more general property of oscillatory compositional dynamics.

The `0.60` result is especially strong falsification pressure: the non-PCC oscillator outperforms PCC by about 34 percentage points in relative MAE reduction, with the paired bootstrap interval entirely below zero.

## Claim boundary

Do **not** claim a PCC-specific EBID regulator law from Experiments 009–019. A better current statement is that canonical EBID is a potentially useful dynamical-history descriptor whose regulator-demand value can become enriched or depleted depending on the dynamical class used as the comparator.

A useful next step is to move from binary specificity (`PCC` versus one control) to a **matched dynamical-class panel**: PCC, exogenous oscillator, damped oscillator, directional flow, and possibly a neutral/random compositional process. The question would then be which dynamical properties actually predict EBID's incremental regulator value.
