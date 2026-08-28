# Experiment 024 — Finite-horizon controllability / response memory

## Question

Can deeper regulator-facing quantities explain when canonical EBID improves prediction of future regulation difficulty across unseen dynamical mechanisms?

The experiment uses the prospective raw paths and frozen EBID-gain targets from Experiment 022. For the held-out high-noise trajectories only, the deterministic transition rule is probed with identical standardized perturbations and intervention choices. Alternative futures are rolled forward for 5 and 20 steps.

## Frozen descriptors

The explanatory variables contain no EBID or entropy terms. They summarize:

- perturbation-memory amplification at 5 and 20 steps;
- bounded response anisotropy at 5 and 20 steps;
- action-conditioned future spread at 5 and 20 steps;
- variability of the action-conditioned spread;
- 20-step / 5-step persistence ratios for memory and intervention spread.

The first implementation used an unbounded singular-value ratio for anisotropy. This became numerically pathological when a response direction was nearly singular. Before scientific interpretation, it was replaced by the bounded contrast `(max-min)/(max+min)`. The underlying finite-horizon probes and evaluation protocol were unchanged.

## Primary result: leave one dynamical class out

| Held-out class | Finite-horizon vs scale-only MAE change |
|---|---:|
| PCC | -58.9% |
| Persistent oscillator | +17.0% |
| Damped oscillator | +23.1% |
| Directional flow | -524.6% |
| Neutral diffusion | -14.4% |
| **All classes** | **-56.4%** |

Overall finite-horizon-model `R² ≈ -2.03`.

Thus the descriptors do not provide a universal cross-class predictor of EBID usefulness.

## Secondary result: known classes, new family

When dynamical classes are represented during calibration and only the seed family is unseen, adding the finite-horizon descriptors changes MAE by only **+0.3%** relative to class + observation scale. This is effectively neutral.

## Descriptive associations

The strongest fold-level correlations with EBID gain are moderate rather than decisive. For example, variability in action-spread anisotropy is negatively associated with EBID gain (about `r=-0.42`), while mean finite-horizon memory anisotropy is positively associated (about `r=+0.40`). These associations do not extrapolate reliably to unseen mechanisms.

## Interpretation

Experiment 024 extends the negative sequence from Experiments 021–023. The missing general principle is not recovered simply by moving from path morphology and one-step sensitivity to handcrafted 5–20-step controllability summaries.

This does **not** show that controllability is irrelevant. It shows that these low-dimensional summaries do not explain the cross-mechanism variation in EBID's incremental regulator value.

A better next test is direct rather than meta-predictive: ask whether instantaneous/windowed EBID predicts **action-conditioned future difficulty or reachable-set contraction within trajectories**, and whether that relationship transfers across mechanisms.
