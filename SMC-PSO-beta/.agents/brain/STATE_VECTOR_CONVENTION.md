# State-Vector Convention (canonical) — Trap A decision

> Status: **DECIDED** at the M4 boundary. This is the single source of truth for
> state ordering in `SMC-PSO-beta/`. Code that disagrees must convert at the boundary.

## Decision
**Canonical = GROUPED:**
```
[x, theta1, theta2, x_dot, theta1_dot, theta2_dot]
```
**Why:** Finding #2 wired the corrected plant physics (`physics_matrices.py`) into
the package, and that math operates in grouped order. The plant is the foundation,
so the plant's order wins; controllers adapt to it.

## Legacy order (do NOT use raw at the plant boundary)
The original controller code documented INTERLEAVED order:
```
[x, x_dot, theta1, theta1_dot, theta2, theta2_dot]
```

## Rule
- The plant, simulation core, integrators, and results all speak **grouped**.
- Any controller / legacy consumer that internally uses interleaved MUST convert
  at the boundary with the adapters in `src/plant/state_convention.py`:
  - `interleaved_to_grouped(state)` before handing a state to the plant.
  - `grouped_to_interleaved(state)` if a legacy routine needs interleaved input.
- Never index a state vector by hard-coded position without first confirming which
  convention that array is in.

## Enforcement
- `tests/test_plant/test_state_vector_convention.py` pins the layout and verifies
  the adapters are exact inverses. It must stay green.
- **M5 gate:** when controllers are wired to the plant, add an integration test
  that asserts a controller's state is converted to grouped before the plant call.
  The existing `test_full_dynamics_invariants.py` does NOT cover this — it tests the
  plant internally and passes under either convention.

## Status of Trap A
- [x] Canonical convention decided & documented (this file).
- [x] Adapters provided (`src/plant/state_convention.py`).
- [x] Guard test added.
- [ ] Controllers actually convert at the boundary — **deferred to M5** (no controllers wired yet).
