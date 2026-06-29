#======================================================================================
#================== tests/test_simulation/test_orchestrators.py =======================
#======================================================================================

"""Unit tests for the simulation orchestrators subpackage (M4 Slice 5).

These tests exercise the orchestrators against a lightweight in-memory fake
context + dynamics model, so they do not require config.yaml, the plant package,
or any heavy runtime dependencies. They validate wiring against the real
Slice 2 core, Slice 3 integrators, Slice 4 safety, and Slice 5 results.
"""

import numpy as np
import pytest

from src.simulation.orchestrators import (
    BaseOrchestrator,
    SequentialOrchestrator,
    BatchOrchestrator,
    ParallelOrchestrator,
    RealTimeOrchestrator,
)
from src.simulation.results import StandardResultContainer, BatchResultContainer
from src.simulation.integrators.fixed_step.euler import ForwardEuler
from src.simulation.integrators.fixed_step.runge_kutta import RungeKutta2, RungeKutta4
from src.simulation.integrators.adaptive.runge_kutta import DormandPrince45


K_DECAY = 0.7


class _FakeConfig:
    def model_dump_json(self):
        return "{}"


class _FakeDynamics:
    def compute_dynamics(self, x, u):
        return -K_DECAY * np.asarray(x, dtype=float)


class _FakeContext:
    def __init__(self, _config_json=None, method="rk4", dt=0.01):
        self.config = _FakeConfig()
        self._dyn = _FakeDynamics()
        self._method = method
        self._dt = dt

    def get_config(self):
        return self.config

    def get_dynamics_model(self):
        return self._dyn

    def get_simulation_parameters(self):
        return {"dt": self._dt, "integration_method": self._method}


def _rk4_reference(x0, dt, k=K_DECAY):
    f = lambda x: -k * x
    k1 = f(x0)
    k2 = f(x0 + dt / 2 * k1)
    k3 = f(x0 + dt / 2 * k2)
    k4 = f(x0 + dt * k3)
    return x0 + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def test_orchestrators_package_exports():
    import src.simulation.orchestrators as o
    assert set(o.__all__) == {
        "BaseOrchestrator", "SequentialOrchestrator", "BatchOrchestrator",
        "ParallelOrchestrator", "RealTimeOrchestrator",
    }


def test_integrator_selection():
    assert isinstance(SequentialOrchestrator(_FakeContext(method="euler")).get_integrator(), ForwardEuler)
    assert isinstance(SequentialOrchestrator(_FakeContext(method="rk2")).get_integrator(), RungeKutta2)
    assert isinstance(SequentialOrchestrator(_FakeContext(method="rk4")).get_integrator(), RungeKutta4)
    assert isinstance(SequentialOrchestrator(_FakeContext(method="rk45")).get_integrator(), DormandPrince45)
    assert isinstance(SequentialOrchestrator(_FakeContext(method="???")).get_integrator(), RungeKutta4)


def test_sequential_shapes_and_result_type():
    orch = SequentialOrchestrator(_FakeContext())
    x0 = np.array([1.0, -2.0, 0.5, 0.0])
    horizon = 10
    controls = np.zeros(horizon)
    result = orch.execute(x0, controls, dt=0.01, horizon=horizon, safety_guards=False)
    assert isinstance(result, StandardResultContainer)
    assert result.get_states().shape == (horizon + 1, 4)
    assert result.get_times().shape == (horizon + 1,)
    assert result.controls.shape == (horizon,)
    assert result.get_states()[0].tolist() == x0.tolist()


def test_sequential_rk4_numeric_matches_reference():
    orch = SequentialOrchestrator(_FakeContext(method="rk4", dt=0.05))
    x0 = np.array([2.0, -1.0])
    result = orch.execute(x0, np.zeros(3), dt=0.05, horizon=3, safety_guards=False)
    expected = _rk4_reference(x0, 0.05)
    assert np.allclose(result.get_states()[1], expected, rtol=1e-12, atol=1e-12)


def test_sequential_safety_guard_path_runs_with_finite_states():
    orch = SequentialOrchestrator(_FakeContext())
    result = orch.execute(np.array([0.1, 0.2]), np.zeros(5), dt=0.01, horizon=5, safety_guards=True)
    assert result.get_states().shape == (6, 2)


def test_sequential_stop_fn_truncates():
    orch = SequentialOrchestrator(_FakeContext())
    stop = lambda s: True
    result = orch.execute(np.array([1.0, 1.0]), np.zeros(5), dt=0.01, horizon=5,
                          safety_guards=False, stop_fn=stop)
    assert result.get_states().shape[0] == 1


def test_input_validation():
    orch = SequentialOrchestrator(_FakeContext())
    with pytest.raises(TypeError):
        orch.execute([1, 2], np.zeros(3), dt=0.01, horizon=3)
    with pytest.raises(ValueError):
        orch.execute(np.array([1.0]), np.zeros(3), dt=-1.0, horizon=3)
    with pytest.raises(ValueError):
        orch.execute(np.array([np.nan]), np.zeros(3), dt=0.01, horizon=3)


def test_batch_execute_shapes():
    orch = BatchOrchestrator(_FakeContext())
    initial = np.array([[1.0, 0.0], [0.0, 1.0], [2.0, -1.0]])
    horizon = 6
    controls = np.zeros((3, horizon))
    result = orch.execute(initial, controls, dt=0.01, horizon=horizon, safety_guards=False)
    assert isinstance(result, BatchResultContainer)
    assert result.get_batch_count() == 3
    assert result.get_states(0).shape == (horizon + 1, 2)


def test_simulate_batch_helper_uses_context():
    import src.simulation.orchestrators.batch as batch_mod
    import src.simulation.core.simulation_context as ctx_mod
    orig = ctx_mod.SimulationContext
    ctx_mod.SimulationContext = lambda *a, **k: _FakeContext()
    try:
        initial = np.array([[1.0, 0.0], [0.0, 2.0]])
        controls = np.zeros((2, 4))
        traj = batch_mod.simulate_batch(initial, controls, dt=0.01, horizon=4)
    finally:
        ctx_mod.SimulationContext = orig
    assert traj.shape[0] == 2


def test_parallel_single_delegates_sequential():
    orch = ParallelOrchestrator(_FakeContext())
    result = orch.execute(np.array([1.0, 0.0]), np.zeros(5), dt=0.01, horizon=5, safety_guards=False)
    assert isinstance(result, StandardResultContainer)
    assert result.get_states().shape == (6, 2)


def test_parallel_batch_runs():
    orch = ParallelOrchestrator(_FakeContext(), max_workers=2)
    initial = np.array([[1.0, 0.0], [0.0, 1.0]])
    result = orch.execute(initial, np.zeros((2, 5)), dt=0.01, horizon=5, safety_guards=False)
    assert isinstance(result, BatchResultContainer)
    assert result.get_batch_count() == 2


def test_real_time_fast_factor_returns_timing():
    orch = RealTimeOrchestrator(_FakeContext(), real_time_factor=1e6)
    result = orch.execute(np.array([0.5, -0.5]), np.zeros(4), dt=0.01, horizon=4, safety_guards=False)
    assert isinstance(result, StandardResultContainer)
    assert "timing" in result.metadata
    assert result.metadata["timing"]["real_time_factor"] == 1e6
