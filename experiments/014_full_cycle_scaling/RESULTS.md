# Experiment 014 — Full-cycle observation scaling

## Question

Does frozen canonical EBID become reliably beneficial for hard joint-OOD regulator-difficulty prediction once observations cover a substantial fraction or multiple of the intrinsic PCC cycle?

## Design

Canonical EBID is unchanged. Intrinsic cycle periods are estimated independently from long, noise-free canonical PCC trajectories at each coupling strength. Observation windows are then set to `0.10`, `0.25`, `0.50`, `0.75`, `1.00`, and `1.50` times that reference period. Training uses non-canonical PCC topologies at low/no noise; testing holds out canonical PCC at unseen higher noise. Future regulation error is measured over 40 steps.

Two readouts are reported. The **ratio-local** analysis fits each cycle fraction separately and is the primary sufficiency test, because long-window examples cannot calibrate short-window EBID coefficients. A secondary **global-calibration** analysis fits across all ratios while controlling for observation duration and cycle fraction.

## Reference periods

Median estimated periods are approximately `1177`, `652`, `317`, and `242` steps for strengths `0.5`, `1.0`, `2.0`, and `3.0`.

## Primary result: ratio-local calibration

| Observation fraction | EBID relative MAE reduction | Bootstrap 95% interval |
|---:|---:|---:|
| 0.10 cycle | -743.7% | -1590.8% to -286.1% |
| 0.25 cycle | -17.2% | -32.8% to +5.7% |
| 0.50 cycle | +11.7% | -43.8% to +45.0% |
| 0.75 cycle | **+33.5%** | **+6.6% to +52.4%** |
| 1.00 cycle | +20.2% | -1.0% to +37.4% |
| 1.50 cycles | **+25.4%** | **+2.7% to +44.2%** |

The first pre-specified ratio with a bootstrap interval entirely above zero is `0.75` cycles. The pattern is not perfectly monotonic: one full cycle is positive in point estimate but borderline by bootstrap, while 1.5 cycles is clearly positive.

## Secondary result: global calibration across observation scales

When a single model is trained across all observation fractions, EBID improves MAE at every tested ratio, including 0.10 cycle. This shows that long-window calibration can teach a readout that transfers EBID information into short-window cases. Therefore `0.75 cycle` should **not** be interpreted as a universal physical threshold.

## Interpretation

Experiment 014 supports a narrower claim than a critical-cycle theorem. When each observation scale must stand on its own, very short windows are insufficient and performance becomes reliably positive only in the substantial-cycle regime, first at about 0.75 cycles in this experiment. However, cross-timescale calibration removes that apparent threshold. The evidence therefore supports **cycle-coverage-dependent identifiability/calibration of EBID**, not a fixed intrinsic cutoff at 0.75 cycles.

The appropriate next test is an independent-seed replication concentrated around the transition band (`0.4–1.2` cycles) with more samples and a lower-variance pre-specified readout, followed by a non-PCC specificity control only if the transition reproduces.
