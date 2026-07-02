#======================================================================================
#===================== tests/test_analysis/test_performance.py ========================
#======================================================================================

"""Targeted tests for src.analysis.performance (M8-S4).

Covers the M8-S4 audit fixes:
- M8-SCHED-1: performance/__init__ decoupled from src.benchmarks re-exports.
- M8-SCHED-2: control_analysis MPC import is lazy-guarded (package still imports).
- M8-SCHED-4: robustness.py re-simulations are real linear state-space re-sims
  (scipy), not the nominal data returned unchanged; they degrade honestly when
  system matrices are unavailable.
- M8-SCHED-3: stability_analysis falls back to a local regularizer when
  src.plant.core is unavailable.
Plus faithful-port sanity for the control metric helpers.
"""

import importlib
import sys

import numpy as np
import pytest

from src.analysis.core.interfaces import DataProtocol  # noqa: F401  (protocol reference)
from src.analysis.performance.control_analysis import (
    ControlAnalyzer,
    check_controllability_observability,
)
from src.analysis.performance.control_metrics import (
    compute_ise,
    compute_itae,
    compute_rms_control_effort,
)
from src.analysis.performance.robustness import (
    RobustnessAnalyzer,
    RobustnessAnalysisConfig,
)
from src.analysis.performance.stability_analysis import (
    StabilityAnalyzer,
    _FallbackRegularizer,
)


class _Data:
    """Minimal DataProtocol implementation for tests."""

    def __init__(self, times, states, controls):
        self.times = np.asarray(times, dtype=float)
        self.states = np.asarray(states, dtype=float)
        self.controls = np.asarray(controls, dtype=float)

    def get_time_range(self):
        return (float(self.times[0]), float(self.times[-1]))

    def get_sampling_rate(self):
        dt = float(np.mean(np.diff(self.times)))
        return 1.0 / dt if dt > 0 else 0.0


def _lti():
    A = np.array([[-1.0, 0.5], [0.0, -2.0]])
    B = np.array([[1.0], [0.5]])
    C = np.eye(2)
    D = np.zeros((2, 1))
    return A, B, C, D


def _nominal_data():
    t = np.linspace(0.0, 5.0, 100)
    u = np.sin(t)
    states = np.zeros((100, 2))
    states[0] = np.array([1.0, 0.5])
    return _Data(t, states, u)


# --------------------------------------------------------------------------- #
# M8-SCHED-1: __init__ decoupling
# --------------------------------------------------------------------------- #
def test_performance_init_exports_control_analyzer():
    mod = importlib.import_module("src.analysis.performance")
    assert hasattr(mod, "ControlAnalyzer")
    assert mod.__all__ == ["ControlAnalyzer"]


def test_performance_init_drops_benchmarks_reexports():
    mod = importlib.import_module("src.analysis.performance")
    # Re-exports were dropped to decouple from src.benchmarks (M8-SCHED-1).
    assert not hasattr(mod, "calculate_control_metrics")
    assert not hasattr(mod, "StabilityMetrics")


# --------------------------------------------------------------------------- #
# control_analysis
# --------------------------------------------------------------------------- #
def test_control_analyzer_controllable_double_integrator():
    analyzer = ControlAnalyzer()
    A = np.array([[0.0, 1.0], [0.0, 0.0]])
    B = np.array([[0.0], [1.0]])
    assert bool(analyzer.is_controllable(A, B)) is True


def test_control_analyzer_observable_double_integrator():
    analyzer = ControlAnalyzer()
    A = np.array([[0.0, 1.0], [0.0, 0.0]])
    C = np.array([[1.0, 0.0]])
    assert bool(analyzer.is_observable(A, C)) is True


def test_check_controllability_observability_double_integrator():
    A = np.array([[0.0, 1.0], [0.0, 0.0]])
    B = np.array([[0.0], [1.0]])
    C = np.array([[1.0, 0.0]])
    is_ctrl, is_obsv = check_controllability_observability(A, B, C)
    assert bool(is_ctrl) is True
    assert bool(is_obsv) is True


# --------------------------------------------------------------------------- #
# control_metrics (faithful port sanity)
# --------------------------------------------------------------------------- #
def test_compute_ise_exact():
    t = np.array([0.0, 1.0, 2.0])
    x = np.ones((1, 3, 1))
    assert compute_ise(t, x) == pytest.approx(2.0)


def test_compute_itae_exact():
    t = np.array([0.0, 1.0, 2.0])
    x = np.ones((1, 3, 1))
    assert compute_itae(t, x) == pytest.approx(1.0)


def test_compute_rms_control_effort_exact():
    u = np.ones((1, 4))
    assert compute_rms_control_effort(u) == pytest.approx(1.0)


# --------------------------------------------------------------------------- #
# M8-SCHED-4: robustness re-simulations are real
# --------------------------------------------------------------------------- #
def _analyzer():
    cfg = RobustnessAnalysisConfig(
        monte_carlo_samples=0,
        include_worst_case_analysis=False,
        include_statistical_analysis=False,
        parallel_processing=False,
    )
    return RobustnessAnalyzer(cfg)


def test_simulate_perturbed_system_returns_resimulated_data():
    an = _analyzer()
    data = _nominal_data()
    matrices = _lti()
    res = an._simulate_perturbed_system(data, matrices)
    assert res is not None
    assert res is not data  # no longer the nominal data returned unchanged
    assert res.states.shape == (100, 2)
    # Re-simulation from x0 must reproduce the initial state exactly.
    assert np.allclose(res.states[0], data.states[0])
    # And it must produce a non-trivial (non-zero) trajectory.
    assert not np.allclose(res.states, 0.0)


def test_parameter_perturbation_changes_trajectory():
    an = _analyzer()
    data = _nominal_data()
    A, B, C, D = _lti()
    nominal = an._simulate_perturbed_system(data, (A, B, C, D))
    A_pert = A.copy()
    A_pert[0, 0] -= 0.5
    perturbed = an._simulate_perturbed_system(data, (A_pert, B, C, D))
    assert perturbed is not None
    assert not np.allclose(perturbed.states, nominal.states)


def test_simulate_with_initial_conditions_requires_matrices():
    an = _analyzer()
    data = _nominal_data()
    ic = np.array([2.0, 1.0])
    # Without system matrices the method degrades honestly (no fabricated data).
    assert an._simulate_with_initial_conditions(data, ic) is None
    # With matrices it re-simulates from the supplied initial condition.
    res = an._simulate_with_initial_conditions(data, ic, system_matrices=_lti())
    assert res is not None
    assert np.allclose(res.states[0], ic)


def test_apply_disturbance_requires_matrices_and_adds_to_input():
    an = _analyzer()
    data = _nominal_data()
    disturbance = np.full_like(data.controls, 0.2)
    assert an._apply_disturbance_to_data(data, disturbance) is None
    res = an._apply_disturbance_to_data(data, disturbance, system_matrices=_lti())
    assert res is not None
    # Disturbance is added to the input signal.
    assert np.allclose(res.controls, data.controls + 0.2)
    # And it propagates through the model, changing the trajectory.
    nominal = an._simulate_perturbed_system(data, _lti())
    assert not np.allclose(res.states, nominal.states)


def test_sensitivity_is_real_with_matrices():
    """M8-SCHED-4 regression: perturbation now actually changes performance."""
    an = _analyzer()
    data = _nominal_data()
    sens = an._perform_sensitivity_analysis(
        data,
        system_matrices=_lti(),
        parameter_ranges={"A_0_0": (-1.5, -0.5)},
    )
    param = sens["parameter_sensitivity"]
    assert "A_0_0" in param
    low, high = param["A_0_0"]["performance_range"]
    # Under the old placeholder both were the nominal value (equal -> zero
    # sensitivity). Real re-simulation makes them differ.
    assert low != high
    # Initial-condition and disturbance sensitivity now populate too.
    assert any(k.startswith("initial_state_") for k in sens["initial_condition_sensitivity"])
    assert any(k.startswith("disturbance_") for k in sens["disturbance_sensitivity"])


def test_sensitivity_degrades_honestly_without_matrices():
    an = _analyzer()
    data = _nominal_data()
    sens = an._perform_sensitivity_analysis(
        data,
        parameter_ranges={"A_0_0": (-1.5, -0.5)},
    )
    # No fabricated numbers when the model is unavailable.
    assert "error" in sens["parameter_sensitivity"]
    assert sens["initial_condition_sensitivity"] == {}
    assert sens["disturbance_sensitivity"] == {}


# --------------------------------------------------------------------------- #
# M8-SCHED-3: stability plant.core fallback
# --------------------------------------------------------------------------- #
def test_fallback_regularizer_ridge_on_ill_conditioned():
    reg = _FallbackRegularizer(regularization_alpha=1e-3, max_condition_number=1e6)
    well = np.eye(2)
    assert np.allclose(reg.regularize_matrix(well), well)
    ill = np.array([[1.0, 1.0], [1.0, 1.0]])  # singular -> infinite condition
    out = reg.regularize_matrix(ill)
    assert not np.allclose(out, ill)
    assert out[0, 0] > ill[0, 0]


def test_analytical_lyapunov_uses_fallback_without_plantcore(monkeypatch):
    # Force the optional dependency to be unavailable so the fallback path runs.
    monkeypatch.setitem(sys.modules, "src.plant.core.numerical_stability", None)
    an = StabilityAnalyzer()
    A = np.array([[-1.0, 0.0], [0.0, -2.0]])
    result = an._analyze_analytical_lyapunov(A)
    assert isinstance(result, dict)
    assert "error" not in result


def test_analytical_lyapunov_stable_matrix():
    an = StabilityAnalyzer()
    A = np.array([[-1.0, 0.0], [0.0, -2.0]])
    result = an._analyze_analytical_lyapunov(A)
    assert isinstance(result, dict)
    assert "error" not in result
