# Experiment 002: Model Content and Regulation

## Question

When action capacity is held fixed, does a regulator with a better model of the
PCC dynamics achieve lower long-run regulation error?

## Controllers

All controllers receive the same nine-action repertoire.

1. `state_only` — reacts only to present Control deviation.
2. `short_history` — extrapolates a one-step trend from recent state history.
3. `correct_pcc_model` — evaluates actions through the true PCC transition model.
4. `weak_pcc_model` — uses the right topology but underestimates coupling strength.
5. `strong_pcc_model` — uses the right topology but overestimates coupling strength.

This is deliberately not yet a full test of the Good Regulator Theorem. It is a
model-content ablation asking whether correct dynamical representation matters
in the toy PCC regime.

## Prediction

If PCC dynamics matter to regulation, the correctly specified predictive model
should outperform state-only and misspecified alternatives increasingly as the
true coupling strength rises.

## Falsification signal

The proposed bridge is weakened if model content has no reproducible effect, or
if a simpler matched-capacity controller performs as well as the PCC-aware
model across cyclic regimes.

Run:

```bash
python experiments/002_good_regulator/run.py
```
