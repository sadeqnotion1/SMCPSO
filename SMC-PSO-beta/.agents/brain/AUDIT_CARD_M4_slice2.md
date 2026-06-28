# Audit Card — M4 Slice 2: simulation/core

**Milestone:** M4 (controllers base + sim core) · **Slice:** 2 of 6 · **Verdict:** PASS (gate green)

## Scope ported
`src/simulation/core/`: `interfaces.py`, `simulation_context.py`, `state_space.py`,
`time_domain.py`, `__init__.py` + a minimal `src/simulation/__init__.py`.
Source: `SMC-PSO/src/simulation/core/`. Target was greenfield (beta had no `src/simulation/`).

## Lens A — AI-slop / code defects
- No hallucinated citation tokens (`【…†L…】`) in `core/` (Trap E was confined to
  `control_primitives.py`, resolved in Slice 1). Swept all five files: clean.
- Banners normalized to the Slice 1 `base.py` style (dropped the `\\\` suffixes).
- No dead imports introduced; `core/__init__` exports match the source surface.

## Lens B — scientific / correctness
| ID | Sev | Finding | Resolution |
|----|-----|---------|------------|
| S2-1 | P1 | `compute_energy()` docstring claimed "total energy" but returns **kinetic only**, and silently assumes the **grouped** state order (second half = velocities). Wrong if fed an interleaved state (Trap A). | Docstring corrected; grouped assumption **pinned by a test**. Math unchanged → parity preserved. |
| S2-2 | P2 | `AdaptiveTimeStep.update_step_size` hard-codes the error exponent `1/4` regardless of integrator order. | Deferred to **Slice 3** (integrators), where it is consumed; watch-item logged. |
| S2-3 | P2 | `interfaces.PerformanceMonitor` shares a name the source `simulation/__init__` imports from `.safety`. | No real collision (distinct module path; not re-exported by `core/__init__`). Revisit in **Slice 4**. |

## Trap decisions
- **Trap A (state ordering):** core speaks the canonical **GROUPED** order. Only `compute_energy`
  is order-sensitive in this slice; pinned by `test_compute_energy_grouped_convention_trap_a`.
- **Trap B (deprecated `src/core/`):** not ported; grep confirms `src/simulation` has no `src/core` imports.
- **Trap C (duplication inside simulation/):** ported the `core/` `SimulationContext`; the `context/`
  twin is **not** ported (its drop + safety canonicalization belongs to Slice 4).
- **Trap D (legacy compat shims in `simulation/__init__`):** shipped a **minimal** package `__init__`
  with no subpackage re-exports or legacy aliases (`get_step_fn`, `step`, `run_simulation`, `simulate`,
  `rk45_step`, `_guard_*`). Those are reintroduced when Slices 3-6 provide them.
- **Trap F:** kept `core` as a subpackage (matches source); graph node `runner` -> `src/simulation/`.

## Minimal anchored edits (vs source)
1. `simulation_context.py`: moved `from src.utils.config_compatibility import wrap_physics_config`
   from module top-level into `_initialize_dynamics_model` (lazy). Lets `import src.simulation.core`
   succeed before utils/factory are ported; call-time behavior identical.
2. `state_space.py`: `compute_energy` docstring fix (S2-1). No behavior change.
3. Minimal `simulation/__init__.py` (Trap D).
Everything else is byte-equivalent to source modulo banner normalization.

## Gate evidence
- Import smoke: `import src.simulation.core` OK with only `src.config` present (no
  orchestrators/integrators/safety/factory/utils pulled in).
- Unit tests: **24 passed, 0 failed** (`tests/test_simulation/`).
- Parity: `parity_check_m4_slice2.py` → **PARITY OK** (state_space + time_domain behavior == source).
- Deprecated-twin grep: clean (no `src/core` imports).

## Gate checklist
- [x] P0 = 0, P1 = 0
- [x] Parity vs source
- [x] Tests green; Trap A asserted by a test
- [x] No imports from deprecated `src/core/`
- [x] Findings logged to `AUDIT_LEDGER.md`
