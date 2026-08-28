# Experiment 011 — topology-dependent EBID transfer diagnosis

Canonical EBID is kept frozen from Experiments 009–010. This experiment asks why
canonical PCC failed the hardest joint noise+topology OOD cell in Experiment 010.
The diagnostic sweep varies observation-window length (`10, 25, 50` steps),
future horizon (`20, 40, 80` steps), interaction strength (`0.5, 1, 2, 3`), and
cycle phase. Training uses the other three topologies at low/no noise and testing
uses the held-out canonical or reverse topology at unseen higher noise.

## Main result

The canonical-PCC failure is strongly timescale-dependent rather than a uniform
topology failure.

- With a **50-step observation window**, EBID improves held-out canonical PCC at
  all three tested horizons: `+40.5%` (20-step horizon), `+9.8%` (40), and
  `+32.2%` (80) relative MAE reduction.
- With **10- or 25-step observation windows**, canonical transfer is often
  negative. The worst cells occur at the 40-step horizon (`-142.1%` and
  `-109.1%`, respectively).
- Across all nine window×horizon cells, canonical EBID is beneficial in `4/9`;
  the median effect is approximately `-3.1%`.
- Reverse topology is also not uniformly robust (`5/9` positive cells), showing
  that the issue is broader than a unique pathology of canonical orientation.

## Phase and strength diagnostics

For held-out canonical PCC, the phase split is suggestive:

- Q1 and Q4 have positive median EBID gains (about `+11.7%` and `+20.1%`) and are
  positive in `7/9` window×horizon cells.
- Q2 and Q3 have negative median gains (about `-17.3%` and `-17.9%`) and are
  positive in only `4/9` cells.

Strength is less decisive and non-monotonic. Strength `3.0` has the most
favorable median (`+21.4%`), while the lower/intermediate strengths have
negative medians. This does not support a simple monotonic coupling-strength
explanation.

## Interpretation

Experiment 011 narrows the Experiment 010 failure considerably. The frozen EBID
feature family appears to require enough observed trajectory to estimate its
entropy-rate descriptors reliably under joint distribution shift. Short-window
features can extrapolate badly, especially when predicting an intermediate
future horizon. Longer observation restores positive transfer for canonical PCC
across all tested horizons.

This is evidence for a **timescale/phase dependence of EBID transfer**, not a
universal regulator-demand predictor. The fixed phase-quadrant result is
suggestive and should be replicated with denser trajectories and independent
seeds before being promoted to a mechanistic claim.
