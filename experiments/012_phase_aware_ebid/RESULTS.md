# Experiment 012 — Phase-aware canonical EBID calibration

## Question

Experiment 011 suggested that canonical EBID transfer varied with observed cycle
phase: Q1/Q4 cells were more often favorable than Q2/Q3. Experiment 012 asks a
stricter predictive question: **does a pre-specified continuous phase-aware
readout of the frozen EBID features improve joint-OOD prediction?**

Canonical EBID itself is unchanged. The phase-aware model adds only first-harmonic
interaction terms

\[
E_j\sin\phi,\qquad E_j\cos\phi
\]

for each of the 11 frozen EBID features \(E_j\). There is no feature selection,
phase-bin fitting, or outcome-driven alteration of EBID.

The experiment reuses the exact Experiment 011 trajectories/outcomes and the
same hard evaluation protocol: train on the other three topologies at low/no
noise and test on the held-out topology at unseen noise levels.

## Result

The pre-specified phase interactions **do not rescue canonical EBID transfer**.
For held-out canonical PCC, phase-aware EBID improves MAE in only **1 of 9**
observation-window × future-horizon cells. The median relative MAE change is
approximately **-183%** (negative means worse than plain EBID).

| Observation | Horizon | Phase-aware vs plain EBID MAE reduction |
|---:|---:|---:|
| 10 | 20 | -224.4% |
| 10 | 40 | +46.6% |
| 10 | 80 | -334.6% |
| 25 | 20 | -182.6% |
| 25 | 40 | -252.6% |
| 25 | 80 | -97.3% |
| 50 | 20 | -312.7% |
| 50 | 40 | -38.3% |
| 50 | 80 | -77.1% |

The lone positive canonical cell (observation 10, horizon 40) has a paired
bootstrap 95% interval that crosses zero (approximately -15% to +66%), so it is
not robust evidence of rescue.

The failure is not unique to canonical PCC. Phase-aware EBID is positive in only
1/9 reverse cells, 0/9 no-pressure-control cells, and 1/9 no-control-chaos cells.
This broad degradation is consistent with the added interaction parameters being
unstable under the small, hard distribution-shift training problem.

## Interpretation

Experiment 012 **does not support a phase-conditioned EBID prediction claim**.
The Q1/Q4 vs Q2/Q3 separation observed in Experiment 011 should therefore be
kept as a descriptive diagnostic, not promoted to a predictive mechanism.

This result does **not** falsify the stronger and better-supported timescale
finding from Experiment 011: plain, frozen EBID still transferred much more
reliably with the 50-step observation window. It specifically falsifies the
simple idea that adding endpoint phase × EBID interactions is sufficient to
explain or repair the short-window OOD failures.

A future model may test phase-aware prediction again only with an independently
specified regularization/cross-fitting protocol or a mechanistically derived
phase representation. Those would be new experiments, not post-hoc repairs to
Experiment 012.
