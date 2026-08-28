# Experiment 015 — Transition-band replication

## Question

Does the locally calibrated canonical-EBID benefit seen near substantial-cycle coverage in Experiment 014 replicate with independent seeds, denser `0.4–1.2` cycle sampling, more trajectories, and a lower-variance pre-specified readout?

## Locked design

Canonical EBID is unchanged. Reference periods are re-estimated from independent long noise-free canonical-PCC trajectories. Observation fractions are fixed at `0.40, 0.50, ..., 1.20` cycles. Each ratio is calibrated separately. Training uses the three non-canonical PCC topologies at low/no noise; testing holds out canonical PCC at unseen higher noise. The future horizon remains 40 steps.

To reduce the coefficient instability seen in the small OLS fits of Experiment 014, both the baseline and EBID models use the same standardized ridge readout with fixed `alpha = 0.10`; only the frozen EBID columns differ. Replication is doubled from 2 to 4 trajectories per cell. No ratio or regularization parameter is selected from the results.

## Result

| Observation fraction | EBID relative MAE reduction | Bootstrap 95% interval |
|---:|---:|---:|
| 0.40 | +2.0% | -17.1% to +17.9% |
| 0.50 | +11.5% | -8.0% to +29.1% |
| 0.60 | **-47.8%** | **-70.6% to -28.0%** |
| 0.70 | +0.5% | -18.8% to +17.1% |
| 0.80 | -8.4% | -31.0% to +11.0% |
| 0.90 | +1.7% | -23.5% to +19.9% |
| 1.00 | **+30.2%** | **+11.9% to +46.7%** |
| 1.10 | -7.9% | -38.8% to +11.3% |
| 1.20 | **+37.9%** | **+20.6% to +50.5%** |

Only `1.00` and `1.20` cycles have bootstrap intervals entirely above zero. The first reliable ratio is therefore `1.00` cycle in this replication, not `0.75` cycles as in Experiment 014.

## Interpretation

Experiment 015 **does not replicate a smooth or monotonic transition near 0.75 cycles**. It does replicate the broader observation-scale dependence: some substantial/full-cycle windows support useful EBID transfer, while neighboring windows can be neutral or harmful. The strongly negative `0.60` cell and negative `1.10` cell directly contradict a simple rule of the form `T_obs/T_cycle > rho*`.

The appropriate claim is therefore narrower: local EBID transfer is observation-scale-sensitive, and full-cycle-scale coverage can support strong OOD benefit, but the current toy system does not exhibit a single stable critical cycle fraction. Any stronger threshold/resonance interpretation requires independent replication designed around the non-monotonic pattern rather than post-hoc smoothing.
