# Audit Card — M4 Slice 6 (simulation/strategies + package wiring / Trap D) — FINAL M4 SLICE

**Verdict:** PORT AS-IS (banner-normalize only). 3 files ported, 0 functional edits.
**Scope:** `src/simulation/strategies/` (MonteCarloStrategy) + the fully-wired
`src/simulation/__init__.py` (Trap D close). Closes out M4.
**Base:** beta HEAD = Slice 5 `a1834d5ac87583b4e8cac6fbd2a9eb4108c41eed`.

## Files (3)
| File | Action | Norm sha256 (12) | Diff vs source |
|---|---|---|---|
| `strategies/__init__.py` | NEW | `8f6fee91fbd3` | banner+EOL only |
| `strategies/monte_carlo.py` | NEW | `c7ea679557a1` | banner+EOL only |
| `__init__.py` | REPLACE (docstring-only -> fully wired original) | `8ad30c37a4d6` | banner+EOL only |

Normalization = CRLF->LF + strip trailing backslash/space on `#=` banner lines. Each file is
byte-identical to the ORIGINAL source after normalization (the original source `#=` banners
carried trailing `\\\` slashes + CRLF). NB: source is CRLF here, so the byte delta is larger
than Slice 5's 9-byte figure, but it is still confined to banner + line-ending normalization
(`chg_lines=3` per file = the 3 banner lines).

## Lens A (AI-slop) — PASS
- `MonteCarloStrategy` is small, single-purpose, numpy-only; no hallucinated citation tokens.
- `_run_parallel_simulations` is explicitly a "simplified" sequential loop (documented in the
  source as a placeholder that "would integrate with the parallel orchestrator"). NOT slop—
  it is honest, working, deterministic code. Left as-is (CODE WINS; do not invent a real
  multiprocessing path the source never had).
- `strategies/__init__.py` carries commented-out placeholders for future strategies
  (sensitivity / parametric / optimization). Preserved verbatim — they document intent and
  match the original. No dead imports are active.

## Lens B (correctness) — PASS
- `monte_carlo.py` imports only `numpy` + `..core.interfaces.SimulationStrategy` (no heavy
  deps, no numba, no back-import of orchestrators/results -> no import cycle).
- Trap D wiring: every name the original `__init__` re-exports resolves in beta:
  - core (9): SimulationEngine, Integrator, Orchestrator, SimulationStrategy, SafetyGuard,
    ResultContainer, SimulationContext, StateSpaceUtilities, TimeManager.
  - orchestrators (4): Sequential/Batch/Parallel/RealTime.
  - integrators (4): ForwardEuler, RungeKutta4, DormandPrince45, ZeroOrderHold.
  - safety (4): apply_safety_guards, SafetyViolationError, SafetyMonitor, PerformanceMonitor.
  - results (3): StandardResultContainer, BatchResultContainer, ResultProcessor.
  - strategies (1): MonteCarloStrategy.
  - legacy aliases: get_step_fn / step / run_simulation (orchestrators.sequential),
    simulate = orchestrators.batch.simulate_batch, rk45_step
    (integrators.adaptive.runge_kutta:177), _guard_no_nan/_guard_energy/_guard_bounds
    (safety.guards).
  - factory fns: create_simulation_engine, run_monte_carlo_analysis.
- IMPORT SIDE-EFFECT CHANGE (expected / intended): through Slice 5 the package was import
  side-effect free. Slice 6 makes `import src.simulation` EAGERLY import core + orchestrators
  + integrators + safety + results + strategies (this is the original design, and the whole
  point of the final-wiring slice). It now requires `scipy` at import (integrators pull it).
  Verified clean: no circular import (submodule imports never re-enter the package __init__).

## Findings
- **S6-1 (Trap D close):** package-level re-exports + legacy aliases were DEFERRED through
  Slices 4-5; now wired by shipping the original `__init__` (banner-normalized drop-in).
  No caller currently depends on the package-level surface — `grep` for `from src.simulation
  import` / `from ..simulation import` across BOTH repos returned EMPTY
  (`simulation_pkg_importers_*.txt`, 0 bytes). So Trap D is cosmetic-risk, but we reproduce
  the exact original surface for forward-compat (PSO/optimizer layers in later milestones).
- **S5-2 (now UNBLOCKED, still DEFERRED here):** the legacy `orchestrators/sequential.py`
  helpers (`get_step_fn`/`step`/`_load_full_step`/`_load_lowrank_step`) lazily reference
  `src.config.schemas` + `...plant.models.dip_full`/`dip_lowrank`. Beta has SINCE grown
  `src/config/` (incl. `schemas.py`) and `src/plant/` (incl. `models/`), so the remap is now
  feasible — BUT it (a) edits an already-shipped, byte-clean file, and (b) needs the actual
  beta plant-model + config-schema symbol names, which were not pulled (only an `ls`).
  Treated as a focused follow-up (own audit + parity), NOT bundled into this slice.
  sequential.py stays byte-identical on `main`.
- **S6-2:** `MonteCarloStrategy._run_parallel_simulations` does not actually parallelize
  (sequential placeholder). Documented, not "fixed" — matches source; a real parallel path
  would belong to a future enhancement, not a migration port.

## Gate (offline harness)
- **19/19 tests** pass: 12 strategies (MonteCarloStrategy behavior, sampling, error paths)
  + 7 package-surface (Trap D: full `__all__`, alias identities, factory fns, end-to-end
  `run_monte_carlo_analysis`, idempotent re-import).
- **STRUCTURAL parity: OK** (banner+EOL-only, `chg_lines=3`/file).
- **BEHAVIORAL: OK** (MonteCarlo statistics vs numpy reference).
- P0 = 0, P1 = 0. No `src.core` imports introduced.

## Carry-forward (post-M4)
- **S5-2 remap** follow-up: pull `src/plant/models/**` + `src/config/schemas.py` symbol names,
  then remap the dead lazy paths in `orchestrators/sequential.py` (own slice).
- Before retiring the legacy `engines/`/`src/core/*` (M6/M9): grep repo for importers of
  `src.simulation.engines` / `src.core.vector_sim` / `src.core.simulation_runner`.
