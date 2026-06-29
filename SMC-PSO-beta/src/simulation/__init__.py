#======================================================================================
#============================= src/simulation/__init__.py =============================
#======================================================================================
"""Simulation framework package (M4).

Shipped so far:
  - Slice 2: `core` subpackage (interfaces, simulation_context, state_space, time_domain).
  - Slice 3: `integrators` subpackage (fixed-step, adaptive, discrete + factory).
            Import it explicitly: `from src.simulation.integrators import create_integrator`.

The full source `__init__` also re-exported orchestrators, safety, results and
strategies plus legacy compatibility aliases (get_step_fn, step, run_simulation,
simulate, rk45_step, _guard_*). Those package-level re-exports remain DEFERRED
until the slices that introduce them land:
  - Slice 4 safety, Slice 5 engines/orchestrators, Slice 6 results/strategies.
Re-exporting them now would raise ImportError (Trap D). Keep this package import
side-effect free until then. (`rk45_step` already lives inside
`integrators.adaptive.runge_kutta`; only the package-level alias is deferred.)
"""
