# Experiment 020 — Dynamical-class panel

## Question
Which broad dynamical classes make frozen canonical EBID useful for predicting future regulation difficulty?

The panel uses the same leave-one-family-out protocol at the two stabilized PCC observation scales (0.60 and 1.00 PCC reference cycles). Earlier results are reused unchanged for PCC, persistent exogenous oscillation, and directional flow. New matched simulations are added for a damped oscillator and neutral stochastic diffusion.

## Mean relative MAE reduction from adding EBID

| Class | 0.60 cycle | 1.00 cycle |
|---|---:|---:|
| PCC | +15.3% | +23.6% |
| Persistent exogenous oscillator | +49.3% | +22.8% |
| Damped exogenous oscillator | +57.7% | -7.8% |
| Directional flow | -5.7% | -203.5% |
| Neutral stochastic diffusion | +12.6% | +36.0% |

At 0.60 cycles, damped and persistent oscillators show the largest robust gains; PCC and neutral diffusion show smaller but positive gains; directional flow is near zero/slightly harmful.

At 1.00 cycle, PCC and the persistent oscillator remain positive, neutral diffusion is strongly positive, the damped oscillator is mixed, and directional flow is strongly harmful.

## Interpretation
The panel rejects a simple class rule such as "EBID is useful because PCC is cyclic" or even "EBID is useful whenever trajectories oscillate." A non-oscillatory neutral diffusion process can also benefit substantially, while a damped oscillator changes from strongly beneficial at 0.60 to mixed at 1.00.

The more defensible conclusion is that EBID usefulness depends on the relationship between observed trajectory history and the future regulation problem. Persistent cycling is one route to informative entropy-rate history, but it is neither necessary nor sufficient in this panel.

This experiment is descriptive across only five toy dynamical classes. The binary class labels in `class_properties.csv` are organizational metadata, not enough data for a meaningful causal regression over dynamical properties.
