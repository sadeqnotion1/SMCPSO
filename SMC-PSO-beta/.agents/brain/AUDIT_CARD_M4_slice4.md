# Audit Card - M4 Slice 4: src/simulation/safety/ (+ Trap C closure)

**Date:** 2026-06-29
**Scope:** Port `src/simulation/safety/` (guards, constraints, monitors, recovery);
DROP the `src/simulation/context/` twin (Trap C). Reconcile watch-item S2-3.
**Source HEAD reconciled against:** beta `ed82b3c` (Slice 3).
**Method:** Banner-normalized port (CRLF->LF, strip trailing `\` on `#=` lines).
ZERO functional edits - non-banner content byte-identical to source (machine-verified, 5/5 files).

## Ported files (5)
- `safety/__init__.py`, `safety/guards.py`, `safety/constraints.py`,
  `safety/monitors.py`, `safety/recovery.py`

## Public API (15, from safety/__init__.__all__)
apply_safety_guards, guard_no_nan, guard_energy, guard_bounds, SafetyViolationError,
StateConstraints, ControlConstraints, EnergyConstraints, ConstraintChecker,
PerformanceMonitor, SafetyMonitor, SystemHealthMonitor, SafetyRecovery,
EmergencyStop, StateLimiter
(plus non-exported: NaNGuard, EnergyGuard, BoundsGuard, SafetyGuardManager,
create_default_guards, SimulationPerformanceMonitor, RecoveryStrategy, Constraint,
_guard_no_nan/_guard_energy/_guard_bounds aliases)

## Trap C - RESOLVED (context/ twin dropped)
The canonical Slice-2 `core/simulation_context.py` is a STRICT SUPERSET of
`context/simulation_context.py`: it has every twin method (get_dynamics_model,
get_config, create_controller, create_fdi) PLUS register_component, get_component,
create_simulation_engine, get_simulation_parameters, and a newer dynamics loader
(full/light fallback + wrap_physics_config; twin used the old `dip_full` path).
`context/safety_guards.py` (`_guard_*`, raise RuntimeError) is superseded by
`safety/guards.py` (`guard_*`, raise SafetyViolationError <: RuntimeError) with
IDENTICAL frozen substrings. => Nothing unique lost; `context/` is NOT ported.
The source package `__init__` already imports SimulationContext from `.core`, not
`.context`, confirming `.core` is canonical.

## Watch-item S2-3 - RESOLVED (false alarm)
`safety.PerformanceMonitor` is a RE-EXPORT of `core.interfaces.PerformanceMonitor`
(ABC), pulled in via `monitors.py` (`from ..core.interfaces import PerformanceMonitor`).
There is NO duplicate class. The concrete implementation is `SimulationPerformanceMonitor`.
Proven by test: `safety.PerformanceMonitor is core.interfaces.PerformanceMonitor`.

## Findings
- **S4-1 (P3, Lens A - DO NOT TOUCH):** error messages contain literal placeholders
  `<i>`, `<val>`, `<max>`, `<t>`. These look like unfilled template tokens but are
  INTENTIONAL frozen test-matching substrings (documented in context twin docstring:
  "do not modify the substrings"). Preserved verbatim. Flagged so a future cleanup
  does not naively "fix" them and break acceptance tests.
- **S4-2 (P3, Lens B - semantics):** guards define "energy" as sum-of-squares of the
  state vector (||state||^2), NOT physical kinetic+potential energy. Self-consistent
  and matches source; `EnergyConstraints` (constraints.py) does take real kinetic/
  potential separately. Future: route the energy guard through the plant energy
  function (state_space) for a physically meaningful bound. Kept for parity.
- **S4-3 (P3, Lens B - minor):** `EnergyGuard.check` uses `np.sum(state**2)` (no axis)
  vs legacy `guard_energy` `np.sum(x*x, axis=-1)` (per-batch). Identical for a single
  state vector; differ only for batched input. Kept (parity).
- **S4-4 (P3, Lens A - hack):** `apply_safety_guards` approximates time as
  `step_idx * 0.01` (hard-coded dt) when calling guard_bounds. Matches source; kept.
  Revisit when engines wire real `t` (Slice 5).
- **Trap D:** package-level `simulation/__init__` re-exports still DEFERRED (orchestrators/
  results/strategies not yet ported). `__init__` updated with a docstring note only;
  still side-effect free. Safety re-exports (+ `_guard_*` package aliases) land in Slice 6.

## Gate
- P0 = 0, P1 = 0.
- Structural parity vs --source: OK (banner-only diff, 5/5).
- Behavioral parity: guard frozen substrings OK; recovery semantics OK; S2-3 OK.
- Tests: see gate run (5 test files, test_safety_*).
- No `src.core` imports; only relative dep is `..core.interfaces`.
- Trap A: N/A (safety operates on whatever ordering the caller supplies; guards are
  order-agnostic elementwise checks).

## Carry-forward
- S3-2 (P2): `core/time_domain.AdaptiveTimeStep` 1/4 hard-code -> route through
  ErrorController (Slice 5).
- Trap-E: `engines/adaptive_integrator.py` citation tokens (Slice 5).
- S4-2: physical energy guard (post-M4 improvement).
- Trap D: wire package-level re-exports once Slices 5-6 land.
