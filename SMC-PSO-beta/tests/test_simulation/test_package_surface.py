"""M4 Slice 6 - Trap D: the simulation package re-exports the full original surface
and the legacy compatibility aliases, and imports cleanly (eager wiring).
"""
import importlib

import src.simulation as sim


EXPECTED_ALL = {
    # core interfaces
    "SimulationEngine", "Integrator", "Orchestrator", "SimulationStrategy",
    "SafetyGuard", "ResultContainer", "SimulationContext",
    "StateSpaceUtilities", "TimeManager",
    # orchestrators
    "SequentialOrchestrator", "BatchOrchestrator", "ParallelOrchestrator", "RealTimeOrchestrator",
    # integrators
    "ForwardEuler", "RungeKutta4", "DormandPrince45", "ZeroOrderHold",
    # safety
    "apply_safety_guards", "SafetyViolationError", "SafetyMonitor", "PerformanceMonitor",
    # results
    "StandardResultContainer", "BatchResultContainer", "ResultProcessor",
    # strategies
    "MonteCarloStrategy",
    # legacy aliases
    "get_step_fn", "step", "run_simulation", "simulate", "rk45_step",
    "_guard_no_nan", "_guard_energy", "_guard_bounds",
    # factory convenience
    "create_simulation_engine", "run_monte_carlo_analysis",
}


def test_all_names_in_dunder_all():
    assert EXPECTED_ALL.issubset(set(sim.__all__)), EXPECTED_ALL - set(sim.__all__)


def test_all_names_are_attributes():
    for name in EXPECTED_ALL:
        assert hasattr(sim, name), f"missing package attribute: {name}"


def test_legacy_aliases_bind_to_real_targets():
    from src.simulation.orchestrators import batch as batch_mod
    from src.simulation.orchestrators import sequential as seq_mod
    from src.simulation.safety import guards as guards_mod
    from src.simulation.integrators.adaptive import runge_kutta as rk_mod
    assert sim.simulate is batch_mod.simulate_batch
    assert sim.get_step_fn is seq_mod.get_step_fn
    assert sim.step is seq_mod.step
    assert sim.run_simulation is seq_mod.run_simulation
    assert sim.rk45_step is rk_mod.rk45_step
    assert sim._guard_no_nan is guards_mod.guard_no_nan
    assert sim._guard_energy is guards_mod.guard_energy
    assert sim._guard_bounds is guards_mod.guard_bounds


def test_strategy_reexport_identity():
    from src.simulation.strategies import MonteCarloStrategy as MCS
    assert sim.MonteCarloStrategy is MCS


def test_core_reexport_identity():
    from src.simulation.core import SimulationContext as Ctx, TimeManager as TM
    assert sim.SimulationContext is Ctx
    assert sim.TimeManager is TM


def test_factory_functions_callable():
    assert callable(sim.create_simulation_engine)
    assert callable(sim.run_monte_carlo_analysis)


def test_run_monte_carlo_analysis_end_to_end():
    import numpy as np
    class _R:
        def __init__(self, s): self._s = np.asarray(s, float)
        def get_states(self): return self._s
    def sim_fn(params, **kwargs):
        return _R([[0.0, 0.0], [params.get("x", 1.0), 2.0]])
    out = sim.run_monte_carlo_analysis(
        sim_fn, n_samples=8,
        distributions={"x": {"type": "constant", "value": 4.0}},
    )
    assert out["success_rate"] == 1.0
    assert out["n_total"] == 8
    assert abs(out["statistics"]["final_state_0"]["mean"] - 4.0) < 1e-9


def test_reimport_is_idempotent():
    m1 = importlib.import_module("src.simulation")
    m2 = importlib.reload(m1)
    assert hasattr(m2, "MonteCarloStrategy")
