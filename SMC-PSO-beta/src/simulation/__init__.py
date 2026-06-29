#======================================================================================
#============================= src/simulation/__init__.py =============================
#======================================================================================
"""Simulation framework package (M4).

Shipped so far:
  - Slice 2: `core` subpackage (interfaces, simulation_context, state_space, time_domain).
  - Slice 3: `integrators` subpackage (fixed-step, adaptive, discrete + factory).
            Import it explicitly: `from src.simulation.integrators import create_integrator`.
  - Slice 4: `safety` subpackage (guards, constraints, monitors, recovery).
            Import it explicitly: `from src.simulation.safety import apply_safety_guards`.
            Trap C: the legacy `context/` twin was intentionally DROPPED (superseded by
            `core.SimulationContext` + `safety.guards`); do not reintroduce it.
  - Slice 5: `results` subpackage (containers, processors, exporters, validators) and
            `orchestrators` subpackage (base, sequential, batch, parallel, real_time).
            Import them explicitly:
              `from src.simulation.results import StandardResultContainer`
              `from src.simulation.orchestrators import SequentialOrchestrator`
            Trap F: the legacy `engines/` twin (adaptive_integrator, simulation_runner,
            vector_sim) was intentionally DROPPED. It duplicated the integrators +
            orchestrators layers, was reachable only through the deprecated
            `src/core/*` shims, and still imported the removed `context/` package.
            Do not reintroduce it; the canonical wiring runs through orchestrators +
            integrators (see `core.simulation_context.create_simulation_engine`).

The full source `__init__` also re-exported these symbols at the package level plus
legacy compatibility aliases (get_step_fn, step, run_simulation, simulate, rk45_step,
_guard_*). Those package-level re-exports remain DEFERRED until Slice 6 (strategies +
final wiring), to keep this package import side-effect free until the last piece lands
(Trap D). Re-exporting them now is unnecessary: the orchestrator legacy functions live
in `orchestrators.sequential` / `orchestrators.batch`, `rk45_step` lives in
`integrators.adaptive.runge_kutta`, and the safety guards live in `safety.guards`.
"""
