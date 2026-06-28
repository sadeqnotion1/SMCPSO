#======================================================================================
#============================= src/simulation/__init__.py =============================
#======================================================================================
"""Simulation framework package (M4).

M4 Slice 2 ships only the `core` subpackage (interfaces, simulation_context,
state_space, time_domain). The full source `__init__` re-exported orchestrators,
integrators, safety, results and strategies plus legacy compatibility aliases
(get_step_fn, step, run_simulation, simulate, rk45_step, _guard_*). Those names
are DEFERRED until the slices that introduce them land:
  - Slice 3 integrators, Slice 4 safety, Slice 5 engines/orchestrators,
    Slice 6 results/strategies.
Re-exporting them now would raise ImportError (Trap D). Keep this package import
side-effect free until then.
"""
