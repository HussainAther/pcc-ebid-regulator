# Experiment 005 — Multi-channel regulator variety

Experiment 004 showed that structural topology switching raises the regulation
error floor, while simply adding more levels to one scalar Control action does
not reliably help. Experiment 005 therefore changes the operational definition
of regulator variety.

The regulator receives access to component-specific interventions on:

- Pressure (P)
- Control (C)
- Chaos (Ch)

For each accessible channel, the controller may apply `-a`, `0`, or `+a` in a
log-compositional intervention. A one-channel regulator therefore has 3
candidate actions, a two-channel regulator 9, and a three-channel regulator 27.
The controller is granted oracle knowledge of the active topology so that the
experiment isolates intervention access rather than model uncertainty.

Because `P + C + Ch = 1`, the state is compositional and the effective tangent
space has only two independent relative directions. Three-channel access is
therefore an explicit saturation/redundancy check, not an assumed third
independent control dimension.

Run:

```bash
python experiments/005_multichannel_variety/run.py
```

Outputs are written to `results/005_multichannel_variety/`.
