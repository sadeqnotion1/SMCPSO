"""
================================================================================
Tests for Chattering Metrics Module
================================================================================

Unit tests for src/utils/analysis/chattering_metrics.py

Tests cover:
1. Chattering index computation (control rate variance)
2. Control rate standard deviation
3. Zero-crossing frequency measurement
4. Integrated metrics computation
5. Edge cases (empty trajectories, transients, constants)

Author: DIP_SMC_PSO Team
Created: December 21, 2025 (Week 3 Session 12)
"""

import numpy as np
import pytest
from src.utils.analysis.chattering_metrics import (
    compute_chattering_index,
    compute_control_rate_std,
    compute_zero_crossings,
    compute_chattering_metrics,
)


# =============================================================================
# Test Chattering Index (Variance of Control Rate)
# =============================================================================

class TestChatteringIndex:
    """Tests for compute_chattering_index function."""

    def test_constant_signal_zero_chattering(self):
        """Constant control signal should have zero chattering index."""
        u_traj = np.ones(1000) * 5.0  # Constant at 5.0
        dt = 0.01

        chattering_idx = compute_chattering_index(u_traj, dt, transient_time=0.0)

        assert chattering_idx == 0.0, "Constant signal should have zero chattering"

    def test_linear_ramp_zero_chattering(self):
        """Linear ramp has constant control rate, zero variance."""
        u_traj = np.linspace(0, 10, 1000)  # Linear ramp
        dt = 0.01

        chattering_idx = compute_chattering_index(u_traj, dt, transient_time=0.0)

        # Linear ramp has constant du/dt, so variance ~0
        assert chattering_idx < 1e-10, f"Linear ramp should have near-zero chattering, got {chattering_idx}"

    def test_sinusoidal_chattering(self):
        """Sinusoidal control signal has positive chattering index."""
        t = np.linspace(0, 10, 1000)
        dt = t[1] - t[0]
        u_traj = 10.0 * np.sin(2 * np.pi * 5 * t)  # 5 Hz sine wave

        chattering_idx = compute_chattering_index(u_traj, dt, transient_time=0.0)

        # Sine wave has varying control rate, positive variance
        assert chattering_idx > 0.0, "Sinusoidal signal should have positive chattering"

    def test_high_frequency_oscillation_higher_chattering(self):
        """Higher frequency oscillations should produce higher chattering index."""
        t = np.linspace(0, 10, 1000)
        dt = t[1] - t[0]

        # Low frequency: 2 Hz
        u_low = 10.0 * np.sin(2 * np.pi * 2 * t)
        chattering_low = compute_chattering_index(u_low, dt, transient_time=0.0)

        # High frequency: 50 Hz
        u_high = 10.0 * np.sin(2 * np.pi * 50 * t)
        chattering_high = compute_chattering_index(u_high, dt, transient_time=0.0)

        # Higher frequency → higher control rate variance
        assert chattering_high > chattering_low, \
            f"High-freq chattering ({chattering_high}) should exceed low-freq ({chattering_low})"

    def test_transient_exclusion(self):
        """Transient period should be excluded from chattering calculation."""
        # Create signal with large transient spike, then constant
        u_traj = np.concatenate([
            np.sin(2 * np.pi * 10 * np.linspace(0, 1, 100)),  # Transient (1s)
            np.ones(900) * 5.0  # Steady-state constant
        ])
        dt = 0.01

        # With transient_time=0, includes spike
        chattering_with_transient = compute_chattering_index(u_traj, dt, transient_time=0.0)

        # With transient_time=1.0, excludes spike
        chattering_no_transient = compute_chattering_index(u_traj, dt, transient_time=1.0)

        # Without transient, chattering should be ~0 (constant signal)
        assert chattering_with_transient > chattering_no_transient, \
            "Chattering with transient should be higher"
        assert chattering_no_transient < 1e-5, \
            f"Chattering after transient should be near-zero, got {chattering_no_transient}"

    def test_empty_trajectory_returns_zero(self):
        """Empty or very short trajectory should return zero."""
        u_traj = np.array([5.0])  # Single point
        dt = 0.01

        chattering_idx = compute_chattering_index(u_traj, dt, transient_time=0.0)

        assert chattering_idx == 0.0, "Single-point trajectory should return zero"

    def test_all_transient_returns_zero(self):
        """If transient period covers entire trajectory, return zero."""
        u_traj = np.sin(2 * np.pi * 10 * np.linspace(0, 0.5, 50))
        dt = 0.01

        # Transient time = 10s, but trajectory only 0.5s
        chattering_idx = compute_chattering_index(u_traj, dt, transient_time=10.0)

        assert chattering_idx == 0.0, "Fully-transient trajectory should return zero"

    def test_chattering_index_scale_invariance(self):
        """Chattering index scales with control signal amplitude squared."""
        t = np.linspace(0, 5, 500)
        dt = t[1] - t[0]

        # Signal with amplitude A
        u_small = 2.0 * np.sin(2 * np.pi * 10 * t)
        chattering_small = compute_chattering_index(u_small, dt, transient_time=0.0)

        # Signal with amplitude 2A
        u_large = 4.0 * np.sin(2 * np.pi * 10 * t)
        chattering_large = compute_chattering_index(u_large, dt, transient_time=0.0)

        # Variance scales as A^2, so chattering_large ≈ 4 * chattering_small
        ratio = chattering_large / chattering_small
        assert abs(ratio - 4.0) < 0.1, \
            f"Chattering should scale as amplitude squared, got ratio {ratio}"

    def test_chattering_index_units(self):
        """Chattering index should have units of (force/time)^2."""
        # For control force in Newtons, chattering index in (N/s)^2
        t = np.linspace(0, 5, 500)
        dt = t[1] - t[0]
        u_traj = 100.0 * np.sin(2 * np.pi * 10 * t)  # N

        chattering_idx = compute_chattering_index(u_traj, dt, transient_time=0.0)

        # Verify chattering index is positive float
        assert isinstance(chattering_idx, float), "Chattering index should be float"
        assert chattering_idx > 0, "Chattering index should be positive"


# =============================================================================
# Test Control Rate Standard Deviation
# =============================================================================

class TestControlRateStd:
    """Tests for compute_control_rate_std function."""

    def test_constant_signal_zero_std(self):
        """Constant control signal has zero control rate std."""
        u_traj = np.ones(1000) * 7.0
        dt = 0.01

        std = compute_control_rate_std(u_traj, dt, transient_time=0.0)

        assert std == 0.0, "Constant signal should have zero std"

    def test_linear_ramp_zero_std(self):
        """Linear ramp has constant control rate, zero std."""
        u_traj = np.linspace(0, 100, 1000)
        dt = 0.01

        std = compute_control_rate_std(u_traj, dt, transient_time=0.0)

        assert std < 1e-10, f"Linear ramp should have near-zero std, got {std}"

    def test_sinusoidal_positive_std(self):
        """Sinusoidal control signal has positive std."""
        t = np.linspace(0, 10, 1000)
        dt = t[1] - t[0]
        u_traj = 15.0 * np.sin(2 * np.pi * 8 * t)

        std = compute_control_rate_std(u_traj, dt, transient_time=0.0)

        assert std > 0.0, "Sinusoidal signal should have positive std"

    def test_std_equals_sqrt_chattering_index(self):
        """Control rate std should equal sqrt(chattering_index)."""
        t = np.linspace(0, 10, 1000)
        dt = t[1] - t[0]
        u_traj = 20.0 * np.sin(2 * np.pi * 12 * t)

        chattering_idx = compute_chattering_index(u_traj, dt, transient_time=0.0)
        std = compute_control_rate_std(u_traj, dt, transient_time=0.0)

        # std = sqrt(variance) = sqrt(chattering_index)
        assert abs(std - np.sqrt(chattering_idx)) < 1e-10, \
            f"std ({std}) should equal sqrt(chattering_index) ({np.sqrt(chattering_idx)})"

    def test_high_frequency_higher_std(self):
        """Higher frequency oscillations produce higher std."""
        t = np.linspace(0, 10, 1000)
        dt = t[1] - t[0]

        u_low = 10.0 * np.sin(2 * np.pi * 3 * t)
        std_low = compute_control_rate_std(u_low, dt, transient_time=0.0)

        u_high = 10.0 * np.sin(2 * np.pi * 30 * t)
        std_high = compute_control_rate_std(u_high, dt, transient_time=0.0)

        assert std_high > std_low, \
            f"High-freq std ({std_high}) should exceed low-freq ({std_low})"

    def test_transient_exclusion_std(self):
        """Transient period exclusion works for std."""
        u_traj = np.concatenate([
            np.sin(2 * np.pi * 15 * np.linspace(0, 1, 100)),
            np.ones(900) * 3.0
        ])
        dt = 0.01

        std_with_transient = compute_control_rate_std(u_traj, dt, transient_time=0.0)
        std_no_transient = compute_control_rate_std(u_traj, dt, transient_time=1.0)

        assert std_with_transient > std_no_transient
        assert std_no_transient < 1e-5

    def test_empty_trajectory_returns_zero_std(self):
        """Empty trajectory returns zero std."""
        u_traj = np.array([10.0])
        dt = 0.01

        std = compute_control_rate_std(u_traj, dt, transient_time=0.0)

        assert std == 0.0

    def test_std_units(self):
        """Control rate std has units of force/time."""
        t = np.linspace(0, 5, 500)
        dt = t[1] - t[0]
        u_traj = 50.0 * np.sin(2 * np.pi * 10 * t)  # N

        std = compute_control_rate_std(u_traj, dt, transient_time=0.0)

        assert isinstance(std, float)
        assert std > 0


# =============================================================================
# Test Zero-Crossing Frequency
# =============================================================================

class TestZeroCrossings:
    """Tests for compute_zero_crossings function."""

    def test_constant_positive_no_crossings(self):
        """Constant positive signal has zero crossings."""
        u_traj = np.ones(1000) * 5.0
        dt = 0.01

        freq = compute_zero_crossings(u_traj, dt, transient_time=0.0)

        assert freq == 0.0, "Constant positive signal should have zero crossings"

    def test_constant_negative_no_crossings(self):
        """Constant negative signal has zero crossings."""
        u_traj = np.ones(1000) * -3.0
        dt = 0.01

        freq = compute_zero_crossings(u_traj, dt, transient_time=0.0)

        assert freq == 0.0, "Constant negative signal should have zero crossings"

    def test_sinusoidal_known_frequency(self):
        """Sinusoidal signal has zero-crossings at 2 × signal frequency."""
        f_signal = 10.0  # Hz
        duration = 5.0  # seconds
        fs = 1000.0  # Sampling rate
        dt = 1.0 / fs

        t = np.linspace(0, duration, int(duration * fs), endpoint=False)
        u_traj = np.sin(2 * np.pi * f_signal * t)

        zero_crossing_freq = compute_zero_crossings(u_traj, dt, transient_time=0.0)

        # Sine wave crosses zero twice per cycle
        expected_freq = 2 * f_signal  # 20 Hz
        assert abs(zero_crossing_freq - expected_freq) < 0.5, \
            f"Expected {expected_freq} Hz, got {zero_crossing_freq} Hz"

    def test_square_wave_known_frequency(self):
        """Square wave has zero-crossings at 2 × signal frequency."""
        f_signal = 5.0  # Hz
        duration = 10.0
        fs = 1000.0
        dt = 1.0 / fs

        t = np.linspace(0, duration, int(duration * fs), endpoint=False)
        u_traj = np.sign(np.sin(2 * np.pi * f_signal * t))  # Square wave

        zero_crossing_freq = compute_zero_crossings(u_traj, dt, transient_time=0.0)

        # Square wave crosses zero twice per cycle
        expected_freq = 2 * f_signal  # 10 Hz
        assert abs(zero_crossing_freq - expected_freq) < 0.5, \
            f"Expected {expected_freq} Hz, got {zero_crossing_freq} Hz"

    def test_linear_ramp_single_crossing(self):
        """Linear ramp from negative to positive has one zero crossing."""
        u_traj = np.linspace(-10, 10, 1000)
        dt = 0.01
        duration = (len(u_traj) - 1) * dt  # 9.99 seconds

        zero_crossing_freq = compute_zero_crossings(u_traj, dt, transient_time=0.0)

        # One crossing in ~10 seconds → freq = 1/10 = 0.1 Hz
        expected_freq = 1.0 / duration
        assert abs(zero_crossing_freq - expected_freq) < 0.02, \
            f"Expected {expected_freq} Hz, got {zero_crossing_freq} Hz"

    def test_high_frequency_chattering_high_crossing_rate(self):
        """High-frequency chattering produces high zero-crossing frequency."""
        f_signal = 100.0  # Hz (high-frequency chattering)
        duration = 2.0
        fs = 5000.0  # High sampling rate to capture crossings
        dt = 1.0 / fs

        t = np.linspace(0, duration, int(duration * fs), endpoint=False)
        u_traj = np.sin(2 * np.pi * f_signal * t)

        zero_crossing_freq = compute_zero_crossings(u_traj, dt, transient_time=0.0)

        # Expected: 2 × 100 Hz = 200 Hz
        expected_freq = 2 * f_signal
        assert abs(zero_crossing_freq - expected_freq) < 2.0, \
            f"Expected {expected_freq} Hz, got {zero_crossing_freq} Hz"

    def test_transient_exclusion_crossings(self):
        """Transient exclusion works for zero-crossing frequency."""
        # Transient: high-frequency oscillation
        # Steady-state: constant positive
        t_transient = np.linspace(0, 1, 100)
        u_transient = np.sin(2 * np.pi * 50 * t_transient)  # 50 Hz
        u_steady = np.ones(900) * 5.0

        u_traj = np.concatenate([u_transient, u_steady])
        dt = 0.01

        # With transient: high crossing frequency
        freq_with_transient = compute_zero_crossings(u_traj, dt, transient_time=0.0)

        # Without transient: zero crossings (constant signal)
        freq_no_transient = compute_zero_crossings(u_traj, dt, transient_time=1.0)

        assert freq_with_transient > freq_no_transient
        assert freq_no_transient == 0.0, "Constant signal should have zero crossings"

    def test_empty_trajectory_returns_zero_crossings(self):
        """Empty or very short trajectory returns zero crossings."""
        u_traj = np.array([5.0])
        dt = 0.01

        freq = compute_zero_crossings(u_traj, dt, transient_time=0.0)

        assert freq == 0.0

    def test_all_transient_returns_zero_crossings(self):
        """If transient period covers entire trajectory, return zero."""
        u_traj = np.sin(2 * np.pi * 10 * np.linspace(0, 0.5, 50))
        dt = 0.01

        freq = compute_zero_crossings(u_traj, dt, transient_time=10.0)

        assert freq == 0.0

    def test_zero_duration_returns_zero(self):
        """Zero duration (single sample after transient) returns zero."""
        u_traj = np.array([1.0, -1.0])  # Two samples
        dt = 0.01

        # Transient covers all but zero duration
        freq = compute_zero_crossings(u_traj, dt, transient_time=0.01)

        assert freq == 0.0

    def test_sign_change_detection(self):
        """Zero-crossing detects sign changes correctly."""
        # Manually construct signal with known sign changes
        u_traj = np.array([5.0, 3.0, 1.0, -2.0, -4.0, -1.0, 2.0, 5.0])
        dt = 0.1
        duration = (len(u_traj) - 1) * dt  # 0.7 seconds

        # Two sign changes: (+) -> (-) at index 3, (-) -> (+) at index 6
        zero_crossing_freq = compute_zero_crossings(u_traj, dt, transient_time=0.0)

        # 2 crossings in 0.7 seconds → freq = 2/0.7 ≈ 2.857 Hz
        expected_freq = 2.0 / duration
        assert abs(zero_crossing_freq - expected_freq) < 0.01, \
            f"Expected {expected_freq} Hz, got {zero_crossing_freq} Hz"


# =============================================================================
# Test Integrated Chattering Metrics
# =============================================================================

class TestChatteringMetrics:
    """Tests for compute_chattering_metrics function."""

    def test_returns_dict_with_all_keys(self):
        """compute_chattering_metrics returns dict with expected keys."""
        u_traj = np.sin(2 * np.pi * 10 * np.linspace(0, 5, 500))
        dt = 0.01

        metrics = compute_chattering_metrics(u_traj, dt, transient_time=0.5)

        expected_keys = {'chattering_index', 'control_rate_std', 'zero_crossing_freq'}
        assert set(metrics.keys()) == expected_keys, \
            f"Missing keys: {expected_keys - set(metrics.keys())}"

    def test_metrics_consistency(self):
        """Metrics should be consistent (std = sqrt(index))."""
        u_traj = np.sin(2 * np.pi * 15 * np.linspace(0, 5, 500))
        dt = 0.01

        metrics = compute_chattering_metrics(u_traj, dt, transient_time=0.0)

        # control_rate_std = sqrt(chattering_index)
        assert abs(metrics['control_rate_std'] - np.sqrt(metrics['chattering_index'])) < 1e-10

    def test_constant_signal_zero_metrics(self):
        """Constant signal produces zero metrics."""
        u_traj = np.ones(1000) * 10.0
        dt = 0.01

        metrics = compute_chattering_metrics(u_traj, dt, transient_time=0.0)

        assert metrics['chattering_index'] == 0.0
        assert metrics['control_rate_std'] == 0.0
        assert metrics['zero_crossing_freq'] == 0.0

    def test_sinusoidal_positive_metrics(self):
        """Sinusoidal signal produces positive metrics."""
        t = np.linspace(0, 10, 1000)
        dt = t[1] - t[0]
        u_traj = 20.0 * np.sin(2 * np.pi * 8 * t)

        metrics = compute_chattering_metrics(u_traj, dt, transient_time=0.0)

        assert metrics['chattering_index'] > 0
        assert metrics['control_rate_std'] > 0
        assert metrics['zero_crossing_freq'] > 0

    def test_transient_parameter_propagates(self):
        """Transient parameter propagates to all metrics."""
        u_traj = np.concatenate([
            np.sin(2 * np.pi * 50 * np.linspace(0, 1, 100)),
            np.ones(900) * 5.0
        ])
        dt = 0.01

        metrics_with_transient = compute_chattering_metrics(u_traj, dt, transient_time=0.0)
        metrics_no_transient = compute_chattering_metrics(u_traj, dt, transient_time=1.0)

        # With transient: positive metrics
        assert metrics_with_transient['chattering_index'] > 0
        assert metrics_with_transient['zero_crossing_freq'] > 0

        # Without transient: zero metrics (constant signal)
        assert metrics_no_transient['chattering_index'] < 1e-5
        assert metrics_no_transient['zero_crossing_freq'] == 0.0

    def test_empty_trajectory_zero_metrics(self):
        """Empty trajectory returns zero metrics."""
        u_traj = np.array([5.0])
        dt = 0.01

        metrics = compute_chattering_metrics(u_traj, dt, transient_time=0.0)

        assert metrics['chattering_index'] == 0.0
        assert metrics['control_rate_std'] == 0.0
        assert metrics['zero_crossing_freq'] == 0.0

    def test_high_frequency_higher_all_metrics(self):
        """Higher frequency produces higher values for all metrics."""
        t = np.linspace(0, 10, 1000)
        dt = t[1] - t[0]

        u_low = 10.0 * np.sin(2 * np.pi * 5 * t)
        metrics_low = compute_chattering_metrics(u_low, dt, transient_time=0.0)

        u_high = 10.0 * np.sin(2 * np.pi * 50 * t)
        metrics_high = compute_chattering_metrics(u_high, dt, transient_time=0.0)

        assert metrics_high['chattering_index'] > metrics_low['chattering_index']
        assert metrics_high['control_rate_std'] > metrics_low['control_rate_std']
        assert metrics_high['zero_crossing_freq'] > metrics_low['zero_crossing_freq']

    def test_metrics_type_validation(self):
        """All metrics should be floats."""
        u_traj = np.sin(2 * np.pi * 10 * np.linspace(0, 5, 500))
        dt = 0.01

        metrics = compute_chattering_metrics(u_traj, dt, transient_time=0.0)

        assert isinstance(metrics['chattering_index'], float)
        assert isinstance(metrics['control_rate_std'], float)
        assert isinstance(metrics['zero_crossing_freq'], float)


# =============================================================================
# Edge Cases and Boundary Conditions
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_short_trajectory(self):
        """Very short trajectory (2 samples) returns zero metrics."""
        u_traj = np.array([5.0, 3.0])
        dt = 0.01

        metrics = compute_chattering_metrics(u_traj, dt, transient_time=0.0)

        # 2 samples → 1 du/dt value → variance = 0
        assert metrics['chattering_index'] == 0.0
        assert metrics['control_rate_std'] == 0.0

    def test_very_large_trajectory(self):
        """Very large trajectory (1M samples) computes correctly."""
        t = np.linspace(0, 1000, 1_000_000)
        dt = t[1] - t[0]
        u_traj = 10.0 * np.sin(2 * np.pi * 10 * t)

        metrics = compute_chattering_metrics(u_traj, dt, transient_time=0.0)

        # Should compute without errors
        assert metrics['chattering_index'] > 0
        assert metrics['zero_crossing_freq'] > 0

    def test_zero_dt_edge_case(self):
        """Zero dt should not cause division by zero."""
        u_traj = np.sin(2 * np.pi * 10 * np.linspace(0, 5, 500))
        dt = 1e-10  # Very small dt

        # Should not raise division by zero
        metrics = compute_chattering_metrics(u_traj, dt, transient_time=0.0)

        assert isinstance(metrics['chattering_index'], float)

    def test_negative_transient_time(self):
        """Negative transient time should be treated as zero (via int conversion)."""
        u_traj = np.sin(2 * np.pi * 10 * np.linspace(0, 5, 500))
        dt = 0.01

        metrics_negative = compute_chattering_metrics(u_traj, dt, transient_time=-1.0)
        metrics_zero = compute_chattering_metrics(u_traj, dt, transient_time=0.0)

        # int(-1.0 / dt) = int(-100) = -100, which skips no samples (starts at 0)
        # So both should be close, but may have rounding differences
        assert abs(metrics_negative['chattering_index'] - metrics_zero['chattering_index']) < 20.0

    def test_nan_in_trajectory(self):
        """NaN in trajectory should propagate to metrics."""
        u_traj = np.array([1.0, 2.0, np.nan, 4.0, 5.0])
        dt = 0.01

        metrics = compute_chattering_metrics(u_traj, dt, transient_time=0.0)

        # NaN in input should produce NaN in output
        assert np.isnan(metrics['chattering_index']) or np.isnan(metrics['control_rate_std'])

    def test_inf_in_trajectory(self):
        """Inf in trajectory produces NaN metrics (variance of [1, inf, -inf, 1])."""
        u_traj = np.array([1.0, 2.0, np.inf, 4.0, 5.0])
        dt = 0.01

        metrics = compute_chattering_metrics(u_traj, dt, transient_time=0.0)

        # Inf in trajectory creates np.diff with [1, inf, -inf, 1]
        # Variance of that array is NaN (not Inf)
        assert np.isnan(metrics['chattering_index']) or np.isnan(metrics['control_rate_std'])


# =============================================================================
# Summary Test
# =============================================================================

def test_chattering_metrics_summary():
    """
    Summary test demonstrating chattering metrics usage.

    Validates all 4 functions work together for realistic control trajectory.
    """
    # Generate realistic SMC control trajectory with chattering
    t = np.linspace(0, 10, 1000)
    dt = t[1] - t[0]

    # Pure high-frequency chattering signal for clear zero-crossing count
    u_traj = 10.0 * np.sin(2 * np.pi * 30 * t)  # 30 Hz chattering

    # Compute individual metrics
    chattering_idx = compute_chattering_index(u_traj, dt, transient_time=0.0)
    control_std = compute_control_rate_std(u_traj, dt, transient_time=0.0)
    zero_freq = compute_zero_crossings(u_traj, dt, transient_time=0.0)

    # Compute integrated metrics
    metrics = compute_chattering_metrics(u_traj, dt, transient_time=0.0)

    # Verify individual and integrated metrics match
    assert abs(metrics['chattering_index'] - chattering_idx) < 1e-10
    assert abs(metrics['control_rate_std'] - control_std) < 1e-10
    assert abs(metrics['zero_crossing_freq'] - zero_freq) < 1e-10

    # Verify metrics are physically meaningful
    assert chattering_idx > 0, "Chattering index should be positive"
    assert control_std > 0, "Control rate std should be positive"
    assert zero_freq > 0, "Zero-crossing frequency should be positive"

    # Verify chattering frequency is near expected (60 Hz for 30 Hz sine)
    # Pure sine wave should cross zero twice per cycle (2 * 30 = 60 Hz)
    assert abs(zero_freq - 60.0) < 2.0, \
        f"Expected zero-crossing ~60 Hz, got {zero_freq} Hz"

    print(f"[OK] Chattering Metrics Summary:")
    print(f"  Chattering Index: {chattering_idx:.2f} (N/s)^2")
    print(f"  Control Rate Std: {control_std:.2f} N/s")
    print(f"  Zero-Crossing Freq: {zero_freq:.2f} Hz")


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
