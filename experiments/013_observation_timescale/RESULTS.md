# Experiment 013 — Observation-timescale sufficiency

## Question

Does frozen canonical EBID become reliably useful for hard joint-OOD regulator-difficulty prediction once the observation window spans a reproducible fraction of the intrinsic PCC cycle?

## Design

- Canonical EBID is unchanged.
- Primary endpoint: future horizon = 40 steps, the strongest failure horizon in Experiment 011.
- Observation windows: 5, 10, ..., 80 steps.
- Intrinsic cycle period is estimated independently from long, noise-free canonical PCC companion trajectories at each coupling strength.
- The hard transfer test holds out canonical topology and tests on unseen noise levels (0.01, 0.02); training uses the other PCC topologies and lower/no noise.
- To avoid near-saturated per-window regressions, one nested predictor pair is fit across all observation lengths. Observation duration is included in both models, and EBID gain is then evaluated separately at each window.

## Reference cycle periods

Median period estimates were approximately 1156, 741, 326, and 281 steps for strengths 0.5, 1.0, 2.0, and 3.0 respectively. Thus the 5–80 step sweep spans only about 0.004–0.285 of a cycle across strengths.

## Result

The simple threshold hypothesis is **not supported** over the sampled range.

EBID is worse than the controlled baseline in most individual observation windows. Positive windows occur at 40 steps (+10.4%) and 75 steps (+30.3%), but neighboring windows revert negative, so there is no stable monotonic onset.

When samples are grouped by normalized observation/cycle ratio:

| T_obs / T_cycle | Relative MAE reduction from EBID |
|---|---:|
| 0.00–0.05 | -88.4% |
| 0.05–0.10 | -44.2% |
| 0.10–0.15 | -41.1% |
| 0.15–0.20 | -84.9% |
| 0.20–0.30 | +3.3% |

The highest observed ratio bin is only slightly positive. This does **not** establish a sufficiency threshold.

## Interpretation

Experiment 011's success at a 50-step observation window does not reproduce as a universal raw-window or normalized-cycle threshold. The stronger inference is that 011 identified a timescale-sensitive phenomenon, but not yet a simple critical fraction of one PCC cycle.

A key limitation is now explicit: even the longest 80-step observation is below 0.3 cycles for the tested strengths. A genuine cycle-fraction hypothesis therefore requires extending observations to approximately 0.5–1.5 intrinsic cycles rather than continuing to densify the sub-cycle regime.

The non-PCC specificity comparison was not promoted in this experiment because the primary PCC sufficiency criterion itself failed. It should be reinstated only after a stable PCC transition is demonstrated.
