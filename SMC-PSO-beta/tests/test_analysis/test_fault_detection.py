#======================================================================================
#================= tests/test_analysis/test_fault_detection.py =========================
#======================================================================================

"""Regression tests for the ported ``src/analysis/fault_detection/`` package (M8-S2).

Covers the primary FDIsystem residual/CUSUM/persistence logic, the statistical and
EWMA threshold adapters, the residual-generator factory surface, and the enhanced
fault detector. Also pins the M8-S2 fail-loud contract: ParameterEstimationGenerator
must raise instead of fabricating random parameter estimates.
"""

import numpy as np
import pytest

from src.analysis.fault_detection.fdi import (
    FDIsystem,
    FaultDetectionInterface,
    DynamicsProtocol,
)
from src.analysis.fault_detection.fdi_system import (
    FaultType,
    DetectionMethod,
    FaultDetectionConfig,
    EnhancedFaultDetector,
    create_enhanced_fault_detector,
)
from src.analysis.fault_detection.residual_generators import (
    ResidualGeneratorConfig,
    ResidualGeneratorFactory,
    ParameterEstimationGenerator,
    create_residual_generator,
)
from src.analysis.fault_detection.threshold_adapters import (
    ThresholdAdapterConfig,
    StatisticalThresholdAdapter,
    EWMAThresholdAdapter,
)


class _IdentityModel:
    """Minimal DynamicsProtocol implementation: predicts an unchanged state."""

    def step(self, state, u, dt):
        return np.asarray(state, dtype=float).copy()


# --------------------------------------------------------------------------- FDIsystem

def test_fdi_reports_ok_when_measurement_matches_prediction():
    fdi = FDIsystem(residual_threshold=0.5, persistence_counter=3)
    model = _IdentityModel()
    meas = np.array([1.0, 2.0, 3.0])
    status0, r0 = fdi.check(0.0, meas, 0.0, 0.01, model)
    assert status0 == "OK" and r0 == 0.0  # first sample seeds the state
    status1, r1 = fdi.check(0.01, meas, 0.0, 0.01, model)
    assert status1 == "OK"
    assert r1 == pytest.approx(0.0, abs=1e-9)


def test_fdi_trips_fault_after_persistent_violations():
    fdi = FDIsystem(residual_threshold=0.5, persistence_counter=3)
    model = _IdentityModel()
    fdi.check(0.0, np.array([0.0, 0.0, 0.0]), 0.0, 0.01, model)  # seed
    statuses = []
    for i in range(1, 6):
        meas = np.array([float(i), 0.0, 0.0])  # grows away from frozen prediction
        status, _ = fdi.check(i * 0.01, meas, 0.0, 0.01, model)
        statuses.append(status)
    assert "FAULT" in statuses
    assert fdi.tripped_at is not None


def test_fdi_rejects_nonpositive_dt():
    fdi = FDIsystem()
    with pytest.raises(ValueError):
        fdi.check(0.0, np.array([0.0, 0.0, 0.0]), 0.0, 0.0, _IdentityModel())


def test_fdi_detection_statistics_are_finite():
    fdi = FDIsystem(residual_threshold=0.5, persistence_counter=3)
    model = _IdentityModel()
    fdi.check(0.0, np.array([0.0, 0.0, 0.0]), 0.0, 0.01, model)
    fdi.check(0.01, np.array([0.1, 0.0, 0.0]), 0.0, 0.01, model)
    stats = fdi.get_detection_statistics()
    assert stats["total_samples"] >= 1
    assert np.isfinite(stats["mean_residual"])
    assert stats["fault_status"] in ("OK", "FAULT")


def test_fdi_exposes_check_interface_and_protocols_importable():
    assert hasattr(FDIsystem(), "check")
    assert FaultDetectionInterface is not None
    assert DynamicsProtocol is not None


# --------------------------------------------------------------- threshold adapters

def test_statistical_threshold_adapter_returns_finite_bounded_threshold():
    cfg = ThresholdAdapterConfig(adaptation_window_size=20)
    adapter = StatisticalThresholdAdapter(cfg)
    rng = np.random.default_rng(0)
    thr = None
    for x in rng.normal(0.1, 0.02, size=30):
        thr = adapter.update(float(abs(x)))
    assert np.isfinite(thr)
    assert cfg.min_threshold <= thr <= cfg.max_threshold
    assert np.isfinite(adapter.current_threshold)


def test_ewma_threshold_adapter_returns_finite_bounded_threshold():
    cfg = ThresholdAdapterConfig()
    adapter = EWMAThresholdAdapter(cfg)
    rng = np.random.default_rng(1)
    thr = None
    for x in rng.normal(0.1, 0.02, size=30):
        thr = adapter.update(float(abs(x)))
    assert np.isfinite(thr)
    assert cfg.min_threshold <= thr <= cfg.max_threshold


# ------------------------------------------------------------- residual generators

def test_residual_generator_factory_surface():
    methods = ResidualGeneratorFactory.get_available_methods()
    assert set(methods) == {
        "observer",
        "kalman",
        "parity",
        "parameter_estimation",
        "adaptive",
    }


def test_create_residual_generator_rejects_unknown_method():
    with pytest.raises(ValueError):
        create_residual_generator("does_not_exist")


def test_parameter_estimation_fails_loud_instead_of_fabricating():
    # M8-S2 fail-loud contract: no fabricated (random) parameter estimates.
    gen = create_residual_generator(
        "parameter_estimation",
        ResidualGeneratorConfig(),
        nominal_parameters={"m": 1.0, "k": 2.0},
    )
    assert isinstance(gen, ParameterEstimationGenerator)
    with pytest.raises(NotImplementedError):
        gen._estimate_parameters(
            np.zeros((5, 2)), np.zeros((4, 1)), np.linspace(0.0, 1.0, 5)
        )


# ------------------------------------------------------------- enhanced detector

def test_fault_enums_expose_expected_values():
    assert FaultType.SENSOR_FAULT.value == "sensor_fault"
    assert DetectionMethod.STATISTICAL.value == "statistical"


def test_enhanced_fault_detector_constructs_and_resets():
    detector = create_enhanced_fault_detector()
    assert isinstance(detector, EnhancedFaultDetector)
    assert isinstance(detector.detector_type, str)
    assert isinstance(FaultDetectionConfig(), FaultDetectionConfig)
    detector.reset()  # must not raise
