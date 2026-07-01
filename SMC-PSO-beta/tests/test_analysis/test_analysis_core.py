#=====================================================================================
#================ tests/test_analysis/test_analysis_core.py ==========================
#=====================================================================================
"""Regression tests for M8-S1: src/analysis/core/ (foundation of the analysis module).

core/ has no cross-module dependencies (numpy only), so it can be imported and
exercised on its own before the rest of M8 lands. The top-level src/analysis/__init__.py
is intentionally NOT part of this slice (it is the lazy loader shipped in M8-S6); until
then src.analysis behaves as a namespace package and src.analysis.core imports directly.

These tests pin:
* the public surface of analysis.core imports,
* control performance metrics against analytically known values (ISE/IAE/ITAE),
* SimulationData dimensional validation,
* ConfidenceInterval geometry,
* that the honest 'not-yet-implemented' calculators WARN + return NaN rather than
  fabricating values (this is the contract that distinguishes core from the
  performance/robustness placeholders being fixed in M8-S4).
"""
import numpy as np
import pytest

from src.analysis.core import (
    AnalysisStatus, AnalysisResult, SimulationData, MetricResult,
    PerformanceMetrics, ConfidenceInterval, ComparisonResult,
    BaseMetricCalculator, ControlPerformanceMetrics, StabilityMetrics,
    RobustnessMetrics, create_comprehensive_metrics,
    create_simulation_data_from_arrays,
)


def _make_constant_error_data(n=101):
    """Unit-step error held at 1.0 over t in [0, 1]; single output channel."""
    times = np.linspace(0.0, 1.0, n)
    states = np.ones((n, 1))              # output = 1.0
    controls = np.full((n - 1, 1), 2.0)   # constant control effort
    reference = np.zeros((n, 1))          # reference = 0 -> error = 1.0
    return SimulationData(times=times, states=states, controls=controls, reference=reference)


def test_control_metrics_match_analytic_values():
    data = _make_constant_error_data()
    calc = ControlPerformanceMetrics()
    # error == 1 over [0,1]: ISE=IAE=1.0, ITAE=integral(t)=0.5
    ise = calc._compute_metric('ise', data, reference=data.reference, output_indices=[0])
    iae = calc._compute_metric('iae', data, reference=data.reference, output_indices=[0])
    itae = calc._compute_metric('itae', data, reference=data.reference, output_indices=[0])
    assert ise == pytest.approx(1.0, abs=1e-6)
    assert iae == pytest.approx(1.0, abs=1e-6)
    assert itae == pytest.approx(0.5, abs=1e-6)
    # RMS control effort of a constant 2.0 signal is 2.0
    assert calc._compute_metric('control_effort', data) == pytest.approx(2.0, abs=1e-9)
    assert calc._compute_metric('peak_control', data) == pytest.approx(2.0, abs=1e-9)


def test_comprehensive_metrics_returns_finite_control_metrics():
    data = _make_constant_error_data()
    pm = create_comprehensive_metrics(data, reference=data.reference, output_indices=[0])
    assert isinstance(pm, PerformanceMetrics)
    d = pm.to_dict()
    for key in ('ise', 'iae', 'itae', 'mse', 'mae', 'rmse'):
        assert key in d and np.isfinite(d[key])


def test_simulation_data_validates_dimensions():
    times = np.linspace(0, 1, 10)
    bad_states = np.ones((7, 1))          # wrong length
    controls = np.ones((9, 1))
    with pytest.raises(ValueError):
        SimulationData(times=times, states=bad_states, controls=controls)


def test_confidence_interval_geometry():
    ci = ConfidenceInterval(lower=1.0, upper=3.0, confidence_level=0.95)
    assert ci.width == pytest.approx(2.0)
    assert ci.center == pytest.approx(2.0)
    assert ci.contains(2.0) and not ci.contains(5.0)


def test_base_calculator_raises_not_implemented():
    base = BaseMetricCalculator(validate_inputs=False)
    with pytest.raises(NotImplementedError):
        base._compute_metric('anything', _make_constant_error_data())


def test_honest_placeholders_warn_and_return_nan_not_fake():
    data = _make_constant_error_data()
    rob = RobustnessMetrics()
    with pytest.warns(UserWarning):
        val = rob._compute_metric('sensitivity_norm', data)
    assert np.isnan(val)  # honest NaN, NOT a fabricated number


def test_analysis_result_status_helpers():
    r = AnalysisResult(status=AnalysisStatus.SUCCESS, message='ok', data={})
    assert r.is_success() and not r.has_errors()
