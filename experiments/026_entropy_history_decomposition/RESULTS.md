# Experiment 026 — Entropy-history decomposition

## Question

Experiment 025 showed that the canonical EBID feature family strongly predicts the direct 40-step control-benefit target across unseen dynamical classes. But most of that gain appeared to come from initial/mean/end entropy rather than entropy-rate terms.

Experiment 026 asks a stricter question:

> After the current endpoint state is represented nonlinearly — including the exact endpoint entropy transform — does *trajectory entropy history* still add information about future controllability?

The frozen Experiment-025 dataset and target are reused. No dynamics, control policy, EBID definition, or outcome is changed.

## Nested models

Two tracks are evaluated under leave-one-dynamical-class-out cross-validation.

### Track A — nonlinear state baseline

- M0: nonlinear current state / geometry (polynomial state terms through degree 3, strength and scale interactions, log/square-root transforms, center distance)
- M1: M0 + endpoint entropy `H_end`
- M2: M1 + historical entropy `H_initial`, `H_mean`
- M3: M2 + remaining canonical EBID rate / deficit-rate terms

### Track B — exact endpoint-entropy sanity control

M0 already contains the exact deterministic entropy of the endpoint state. Therefore adding `H_end` cannot provide new information by construction. The test becomes:

- M0: strong nonlinear state + exact endpoint entropy
- M2: M0 + `H_initial`, `H_mean`
- M3: M2 + canonical rate / deficit-rate terms

This is the primary interpretation track.

## Primary leave-one-class-out result

Using the exact endpoint-entropy state baseline:

| Held-out class | entropy-history increment | rate increment | full history+rate gain |
|---|---:|---:|---:|
| PCC | **+7.3%** | **+2.5%** | **+9.6%** |
| persistent oscillator | +3.7% | -1.5% | +2.3% |
| damped oscillator | +0.1% | +5.2% | +5.3% |
| directional flow | **+9.2%** | +3.8% | **+12.7%** |
| neutral diffusion | **-10.6%** | +0.2% | **-10.4%** |
| **pooled** | **+4.3%** | **+2.4%** | **+6.6%** |

The pooled held-out predictions improve from approximately `R² = 0.801` for the exact-current-state baseline to `R² = 0.829` with the full history/rate family.

A paired bootstrap over the pooled leave-one-class-out predictions gives:

- history increment (`H_initial`, `H_mean` beyond exact current-state entropy): approximately **+3.2% to +5.3%** MAE reduction;
- rate increment beyond entropy history: approximately **+1.7% to +3.0%**.

## Known-class, held-out-family result

When mechanisms are represented during calibration but a complete seed family is unseen:

- entropy history beyond exact endpoint entropy: **+3.1%**;
- rate terms beyond entropy history: **+3.5%**;
- total history + rate gain: **+6.6%**;
- `R²` improves from approximately `0.897` to `0.909`.

## Representation sanity check

In the weaker nonlinear-state track, simply adding `H_end` improves pooled MAE by about **5.9%**. But `H_end` is a deterministic function of `(P,C,Ch)`. Therefore that gain is not new dynamical information; it shows that supplying the entropy transform explicitly makes the finite ridge readout's representation easier.

Once exact endpoint entropy is included in the state baseline, the residual transferable temporal contribution is much smaller: about **4.3% history + 2.4% rates pooled**, rather than the ~27% level/history effect seen in Experiment 025.

## Interpretation

Experiment 026 supports a narrower claim than Experiment 025:

> Canonical entropy *history* contains modest additional information about future controllability beyond an exact current-state entropy representation, but the effect is mechanism-dependent and is not uniformly beneficial across unseen dynamical classes.

For PCC, the historical contribution remains positive and meaningful (~7.3% before rate terms). However, neutral diffusion is a clear counterexample: historical entropy worsens transfer.

Therefore the large Experiment-025 effect should not be interpreted as primarily temporal EBID information. Much of it reflects the usefulness of entropy as a nonlinear representation of current composition. Genuine temporal information survives, but at a substantially smaller effect size.
