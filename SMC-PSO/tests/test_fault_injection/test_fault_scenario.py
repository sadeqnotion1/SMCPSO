"""
Regression tests for fault scenario simulation runner compatibility.
"""

from types import SimpleNamespace

import numpy as np

from src.utils.testing.fault_injection import FaultScenario


class _DummyPlant:
    """Minimal plant model for fault-scenario interface tests."""

    def step(self, state: np.ndarray, control: float, dt: float) -> np.ndarray:
        next_state = state.copy()
        # Very simple dynamics: cart velocity integrates control command.
        if next_state.shape[0] >= 4:
            next_state[3] = next_state[3] + float(control) * dt
            next_state[0] = next_state[0] + next_state[3] * dt
        return next_state


class _DictController:
    def compute_control(self, state: np.ndarray, state_vars, history):
        return {"u": 1.5}


class _ObjectController:
    def compute_control(self, state: np.ndarray, state_vars, history):
        return SimpleNamespace(u=2.0, state=state_vars, history=history)


class _ArrayController:
    def compute_control(self, state: np.ndarray, state_vars, history):
        return np.array([3.0, 0.0, 0.0], dtype=float)


class _LegacyHistoryController:
    def __init__(self):
        self.history_keys_seen = []

    def initialize_state(self):
        return (0.0,)

    def initialize_history(self):
        return {"k1": [], "k2": [], "u_int": [], "s": []}

    def compute_control(self, state: np.ndarray, state_vars, history):
        self.history_keys_seen.append(tuple(sorted(history.keys())))
        return SimpleNamespace(u=0.5, state=state_vars, history=history)


def _run_short_sim(controller) -> float:
    scenario = FaultScenario(name="compatibility", seed=42)
    plant = _DummyPlant()
    initial_state = np.zeros(6, dtype=float)
    result = scenario.run_simulation(
        controller=controller,
        plant=plant,
        initial_state=initial_state,
        duration=0.05,
        dt=0.01,
    )
    return float(np.mean(result.control_trajectory))


def test_run_simulation_accepts_dict_controller_output():
    avg_u = _run_short_sim(_DictController())
    assert abs(avg_u - 1.5) < 1e-12


def test_run_simulation_accepts_object_controller_output():
    avg_u = _run_short_sim(_ObjectController())
    assert abs(avg_u - 2.0) < 1e-12


def test_run_simulation_accepts_array_controller_output():
    avg_u = _run_short_sim(_ArrayController())
    assert abs(avg_u - 3.0) < 1e-12


def test_run_simulation_initializes_legacy_history_keys():
    controller = _LegacyHistoryController()
    _run_short_sim(controller)

    assert controller.history_keys_seen
    expected = ("k1", "k2", "s", "u_int")
    assert all(keys == expected for keys in controller.history_keys_seen)


def test_overshoot_uses_pendulum_angles_not_cart_position():
    scenario = FaultScenario(name="metrics", seed=1)

    # Large cart excursion, small pendulum angles.
    states = np.array([
        [50.0, 0.05, -0.05, 0.0, 0.0, 0.0],
        [75.0, 0.06, -0.02, 0.0, 0.0, 0.0],
    ])
    target = np.zeros(6, dtype=float)

    overshoot = scenario._compute_overshoot(states, target)
    expected_max_angle = 0.06
    expected = (expected_max_angle / np.pi) * 100.0
    assert abs(overshoot - expected) < 1e-12
