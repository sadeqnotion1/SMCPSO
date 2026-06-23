#======================================================================================\\\
#================ tests/test_analysis/validation/test_metrics.py ================\\\
#======================================================================================\\\

"""
Comprehensive tests for analysis validation metrics.

Tests cover:
- Basic statistical metrics computation
- Performance metrics (MSE, RMSE, MAE, max error)
- Control metrics (effort, variation, settling time)
- Stability metrics (deviations, Lyapunov estimates)
- Frequency domain metrics (FFT, dominant frequency, bandwidth)
- Statistical significance testing (t-test, Mann-Whitney, KS)
- Robustness metrics (perturbation analysis)
- Comprehensive metrics integration
"""

import pytest
import numpy as np
from unittest.mock import patch
import warnings

from src.analysis.validation.metrics import (
    compute_basic_metrics,
    compute_performance_metrics,
    compute_control_metrics,
    compute_stability_metrics,
    compute_frequency_metrics,
    compute_statistical_significance,
    compute_robustness_metrics,
    compute_comprehensive_metrics
)


# =====================================================================================
# Tests for compute_basic_metrics
# =====================================================================================

class TestComputeBasicMetrics:
    """Test basic statistical metrics computation."""

    def test_empty_array(self):
        """Test metrics computation with empty array."""
        data = np.array([])
        metrics = compute_basic_metrics(data)

        assert metrics['mean'] == 0.0
        assert metrics['std'] == 0.0
        assert metrics['min'] == 0.0
        assert metrics['max'] == 0.0
        assert metrics['median'] == 0.0
        assert metrics['count'] == 0

    def test_single_value(self):
        """Test metrics with single value."""
        data = np.array([5.0])
        metrics = compute_basic_metrics(data)

        assert metrics['mean'] == 5.0
        assert metrics['std'] == 0.0
        assert metrics['min'] == 5.0
        assert metrics['max'] == 5.0
        assert metrics['median'] == 5.0
        assert metrics['count'] == 1

    def test_normal_data(self):
        """Test metrics with normal data."""
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        metrics = compute_basic_metrics(data)

        assert metrics['mean'] == 3.0
        assert metrics['std'] == pytest.approx(np.std([1, 2, 3, 4, 5]))
        assert metrics['min'] == 1.0
        assert metrics['max'] == 5.0
        assert metrics['median'] == 3.0
        assert metrics['count'] == 5

    def test_negative_values(self):
        """Test metrics with negative values."""
        data = np.array([-5.0, -2.0, 0.0, 2.0, 5.0])
        metrics = compute_basic_metrics(data)

        assert metrics['mean'] == 0.0
        assert metrics['min'] == -5.0
        assert metrics['max'] == 5.0
        assert metrics['median'] == 0.0

    def test_return_types(self):
        """Test that all return values are floats."""
        data = np.array([1.0, 2.0, 3.0])
        metrics = compute_basic_metrics(data)

        assert isinstance(metrics['mean'], float)
        assert isinstance(metrics['std'], float)
        assert isinstance(metrics['min'], float)
        assert isinstance(metrics['max'], float)
        assert isinstance(metrics['median'], float)
        assert isinstance(metrics['count'], int)


# =====================================================================================
# Tests for compute_performance_metrics
# =====================================================================================

class TestComputePerformanceMetrics:
    """Test performance metrics computation."""

    def test_length_mismatch_raises_error(self):
        """Test that mismatched array lengths raise ValueError."""
        reference = np.array([1.0, 2.0, 3.0])
        actual = np.array([1.0, 2.0])

        with pytest.raises(ValueError, match="same length"):
            compute_performance_metrics(reference, actual)

    def test_empty_arrays(self):
        """Test with empty arrays."""
        reference = np.array([])
        actual = np.array([])
        metrics = compute_performance_metrics(reference, actual)

        assert metrics['mse'] == 0.0
        assert metrics['rmse'] == 0.0
        assert metrics['mae'] == 0.0
        assert metrics['max_error'] == 0.0

    def test_perfect_match(self):
        """Test with perfectly matching data."""
        reference = np.array([1.0, 2.0, 3.0, 4.0])
        actual = np.array([1.0, 2.0, 3.0, 4.0])
        metrics = compute_performance_metrics(reference, actual)

        assert metrics['mse'] == 0.0
        assert metrics['rmse'] == 0.0
        assert metrics['mae'] == 0.0
        assert metrics['max_error'] == 0.0

    def test_known_error(self):
        """Test with known error values."""
        reference = np.array([0.0, 0.0, 0.0, 0.0])
        actual = np.array([1.0, 2.0, 3.0, 4.0])
        metrics = compute_performance_metrics(reference, actual)

        # MSE = (1 + 4 + 9 + 16) / 4 = 7.5
        assert metrics['mse'] == pytest.approx(7.5)
        assert metrics['rmse'] == pytest.approx(np.sqrt(7.5))
        # MAE = (1 + 2 + 3 + 4) / 4 = 2.5
        assert metrics['mae'] == pytest.approx(2.5)
        assert metrics['max_error'] == 4.0

    def test_negative_errors(self):
        """Test with negative errors."""
        reference = np.array([5.0, 5.0, 5.0])
        actual = np.array([3.0, 4.0, 7.0])
        metrics = compute_performance_metrics(reference, actual)

        # Errors: -2, -1, +2
        # MSE = (4 + 1 + 4) / 3 = 3.0
        assert metrics['mse'] == pytest.approx(3.0)
        # MAE = (2 + 1 + 2) / 3 = 1.667
        assert metrics['mae'] == pytest.approx(5.0 / 3.0)
        assert metrics['max_error'] == 2.0


# =====================================================================================
# Tests for compute_control_metrics
# =====================================================================================

class TestComputeControlMetrics:
    """Test control-specific metrics computation."""

    def test_empty_control_signals(self):
        """Test with empty control signal array."""
        control_signals = np.array([])
        metrics = compute_control_metrics(control_signals)

        assert metrics['control_effort'] == 0.0
        assert metrics['max_control'] == 0.0
        assert metrics['control_variation'] == 0.0
        assert metrics['settling_time'] == 0.0

    def test_single_control_value(self):
        """Test with single control value."""
        control_signals = np.array([10.0])
        metrics = compute_control_metrics(control_signals)

        assert metrics['control_effort'] == 10.0
        assert metrics['max_control'] == 10.0
        assert metrics['control_variation'] == 0.0

    def test_control_effort_calculation(self):
        """Test control effort (sum of absolute values)."""
        control_signals = np.array([1.0, -2.0, 3.0, -4.0])
        metrics = compute_control_metrics(control_signals)

        # Effort = |1| + |-2| + |3| + |-4| = 10
        assert metrics['control_effort'] == 10.0
        assert metrics['max_control'] == 4.0

    def test_control_variation_calculation(self):
        """Test control variation (total variation)."""
        control_signals = np.array([0.0, 1.0, 3.0, 2.0, 5.0])
        metrics = compute_control_metrics(control_signals)

        # Variation = |1-0| + |3-1| + |2-3| + |5-2| = 1 + 2 + 1 + 3 = 7
        assert metrics['control_variation'] == 7.0

    def test_settling_time_without_time_vector(self):
        """Test settling time defaults to 0 without time vector."""
        control_signals = np.array([1.0, 2.0, 3.0, 3.0, 3.0])
        metrics = compute_control_metrics(control_signals)

        assert metrics['settling_time'] == 0.0

    def test_settling_time_with_time_vector(self):
        """Test settling time calculation with time vector."""
        # Signal settles to 5.0 after index 2
        control_signals = np.array([0.0, 2.0, 4.5, 5.0, 5.0, 5.0])
        time_vector = np.array([0.0, 0.01, 0.02, 0.03, 0.04, 0.05])
        metrics = compute_control_metrics(control_signals, time_vector)

        # Tolerance = 0.05 * 5.0 = 0.25
        # Last time outside tolerance is index 2 (4.5 vs 5.0 = 0.5 > 0.25)
        # Settling time should be time[3] = 0.03
        assert metrics['settling_time'] == pytest.approx(0.03)

    def test_settling_time_small_final_value(self):
        """Test settling time with small final value (uses absolute tolerance)."""
        control_signals = np.array([1.0, 0.5, 0.1, 0.01, 0.01])
        time_vector = np.array([0.0, 0.01, 0.02, 0.03, 0.04])
        metrics = compute_control_metrics(control_signals, time_vector)

        # Final value = 0.01, tolerance = 0.05 (absolute)
        # Signal settles when it reaches within 0.05 of 0.01
        assert metrics['settling_time'] >= 0.0


# =====================================================================================
# Tests for compute_stability_metrics
# =====================================================================================

class TestComputeStabilityMetrics:
    """Test stability-related metrics computation."""

    def test_empty_states(self):
        """Test with empty state array."""
        states = np.array([]).reshape(0, 6)
        metrics = compute_stability_metrics(states)

        assert metrics['max_deviation'] == 0.0
        assert metrics['final_deviation'] == 0.0
        assert metrics['stability_margin'] == 0.0
        assert metrics['lyapunov_estimate'] == 0.0

    def test_zero_deviation_from_origin(self):
        """Test zero deviation from origin reference."""
        states = np.zeros((10, 6))
        metrics = compute_stability_metrics(states)

        assert metrics['max_deviation'] == 0.0
        assert metrics['final_deviation'] == 0.0
        assert metrics['stability_margin'] == pytest.approx(1.0)

    def test_deviation_calculation(self):
        """Test deviation calculation from custom reference."""
        states = np.array([[1.0, 0.0], [2.0, 0.0], [1.5, 0.0]])
        reference_state = np.array([0.0, 0.0])
        metrics = compute_stability_metrics(states, reference_state)

        # Deviations: 1.0, 2.0, 1.5
        assert metrics['max_deviation'] == 2.0
        assert metrics['final_deviation'] == 1.5
        assert metrics['stability_margin'] == pytest.approx(1.0 / 3.0)

    def test_nan_handling(self):
        """Test graceful handling of NaN values."""
        states = np.array([[1.0, 2.0], [np.nan, np.nan], [3.0, 4.0]])
        metrics = compute_stability_metrics(states)

        # Should use nanmax to ignore NaN
        assert np.isfinite(metrics['max_deviation'])
        assert np.isfinite(metrics['final_deviation'])

    def test_lyapunov_estimate_insufficient_data(self):
        """Test Lyapunov estimate with insufficient data."""
        states = np.array([[1.0, 0.0], [1.1, 0.0], [1.2, 0.0]])  # Only 3 points
        metrics = compute_stability_metrics(states)

        # Not enough data for Lyapunov estimate
        assert metrics['lyapunov_estimate'] == 0.0

    def test_lyapunov_estimate_with_growth(self):
        """Test Lyapunov estimate with growing deviations."""
        # Create growing deviations: e^(0.1*t)
        t = np.linspace(0, 2, 20)
        deviations = np.exp(0.1 * t)
        states = deviations[:, np.newaxis] * np.array([[1.0, 0.0]])
        metrics = compute_stability_metrics(states)

        # Lyapunov exponent should be positive for growing system
        assert metrics['lyapunov_estimate'] > 0


# =====================================================================================
# Tests for compute_frequency_metrics
# =====================================================================================

class TestComputeFrequencyMetrics:
    """Test frequency domain metrics computation."""

    def test_insufficient_signal_length(self):
        """Test with signal too short for FFT."""
        signal = np.array([1.0])
        metrics = compute_frequency_metrics(signal, sampling_rate=100.0)

        assert metrics['dominant_frequency'] == 0.0
        assert metrics['bandwidth'] == 0.0
        assert len(metrics['power_spectrum']) == 0
        assert len(metrics['frequencies']) == 0

    def test_dc_signal(self):
        """Test with DC (constant) signal."""
        signal = np.ones(100)
        metrics = compute_frequency_metrics(signal, sampling_rate=100.0)

        # DC signal has dominant frequency at 0
        assert metrics['dominant_frequency'] == 0.0
        assert len(metrics['power_spectrum']) > 0
        assert len(metrics['frequencies']) > 0

    def test_sinusoidal_signal(self):
        """Test with known sinusoidal signal."""
        # 10 Hz sine wave, sampled at 100 Hz
        fs = 100.0
        t = np.linspace(0, 1, int(fs))
        freq = 10.0
        signal = np.sin(2 * np.pi * freq * t)

        metrics = compute_frequency_metrics(signal, sampling_rate=fs)

        # Dominant frequency should be close to 10 Hz
        assert metrics['dominant_frequency'] == pytest.approx(freq, abs=1.0)

    def test_frequency_bands(self):
        """Test power computation in frequency bands."""
        fs = 100.0
        t = np.linspace(0, 1, int(fs))
        signal = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 30 * t)

        frequency_bands = [(0, 20), (20, 40)]
        metrics = compute_frequency_metrics(signal, sampling_rate=fs,
                                           frequency_bands=frequency_bands)

        # Should have band power metrics
        assert 'band_0_power' in metrics
        assert 'band_1_power' in metrics
        # Band 0 (0-20 Hz) should have more power (10 Hz component)
        assert metrics['band_0_power'] > metrics['band_1_power']

    def test_bandwidth_calculation(self):
        """Test bandwidth calculation (90% power)."""
        fs = 100.0
        t = np.linspace(0, 2, int(2 * fs))
        # Narrow-band signal
        signal = np.sin(2 * np.pi * 10 * t)

        metrics = compute_frequency_metrics(signal, sampling_rate=fs)

        # Bandwidth should be non-zero and finite
        assert metrics['bandwidth'] >= 0.0
        assert np.isfinite(metrics['bandwidth'])


# =====================================================================================
# Tests for compute_statistical_significance
# =====================================================================================

class TestComputeStatisticalSignificance:
    """Test statistical significance testing."""

    def test_empty_arrays(self):
        """Test with empty arrays."""
        data1 = np.array([])
        data2 = np.array([1.0, 2.0, 3.0])
        metrics = compute_statistical_significance(data1, data2)

        assert metrics['statistic'] == 0.0
        assert metrics['p_value'] == 1.0
        assert metrics['significant'] is False

    def test_identical_distributions_ttest(self):
        """Test t-test with identical distributions."""
        data1 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        data2 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        metrics = compute_statistical_significance(data1, data2, test_type='ttest')

        # Identical data should have p-value close to 1.0
        assert metrics['p_value'] > 0.05
        assert metrics['significant'] is False

    def test_different_distributions_ttest(self):
        """Test t-test with clearly different distributions."""
        data1 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        data2 = np.array([10.0, 11.0, 12.0, 13.0, 14.0])
        metrics = compute_statistical_significance(data1, data2, test_type='ttest')

        # Very different data should have low p-value
        assert metrics['p_value'] < 0.05
        assert metrics['significant'] is True
        assert isinstance(metrics['statistic'], float)

    def test_mannwhitneyu_test(self):
        """Test Mann-Whitney U test."""
        data1 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        data2 = np.array([6.0, 7.0, 8.0, 9.0, 10.0])
        metrics = compute_statistical_significance(data1, data2, test_type='mannwhitney')

        assert 'statistic' in metrics
        assert 'p_value' in metrics
        assert isinstance(metrics['significant'], bool)

    def test_ks_test(self):
        """Test Kolmogorov-Smirnov test."""
        data1 = np.random.normal(0, 1, 50)
        data2 = np.random.normal(0, 1, 50)
        metrics = compute_statistical_significance(data1, data2, test_type='ks')

        assert 'statistic' in metrics
        assert 'p_value' in metrics
        assert isinstance(metrics['significant'], bool)

    def test_invalid_test_type(self):
        """Test with invalid test type (should handle gracefully with warning)."""
        data1 = np.array([1.0, 2.0, 3.0])
        data2 = np.array([4.0, 5.0, 6.0])

        # Invalid test type should trigger exception handling and return safe defaults
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            metrics = compute_statistical_significance(data1, data2, test_type='invalid')

        # Should return safe defaults on error
        assert metrics['statistic'] == 0.0
        assert metrics['p_value'] == 1.0
        assert metrics['significant'] is False

    def test_exception_handling(self):
        """Test exception handling in statistical tests."""
        # Create data that might cause issues
        data1 = np.array([1.0])
        data2 = np.array([1.0])

        # Should handle gracefully with warning
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            metrics = compute_statistical_significance(data1, data2, test_type='ttest')

        # Should return safe defaults on error
        assert 'p_value' in metrics
        assert 'statistic' in metrics


# =====================================================================================
# Tests for compute_robustness_metrics
# =====================================================================================

class TestComputeRobustnessMetrics:
    """Test robustness metrics computation."""

    def test_empty_perturbed_performances(self):
        """Test with no perturbations."""
        nominal = {'metric1': 1.0, 'metric2': 2.0}
        perturbed = []
        metrics = compute_robustness_metrics(nominal, perturbed)

        assert metrics == {}

    def test_no_matching_metrics(self):
        """Test with no matching metric names."""
        nominal = {'metric1': 1.0}
        perturbed = [{'metric2': 2.0}]
        metrics = compute_robustness_metrics(nominal, perturbed, metric_names=['metric1'])

        # No perturbed data for metric1
        assert 'metric1' not in metrics

    def test_single_perturbation(self):
        """Test with single perturbation."""
        nominal = {'rmse': 1.0}
        perturbed = [{'rmse': 1.5}]
        metrics = compute_robustness_metrics(nominal, perturbed)

        assert 'rmse' in metrics
        assert metrics['rmse']['mean_deviation'] == 0.5
        assert metrics['rmse']['max_deviation'] == 0.5
        assert metrics['rmse']['std_deviation'] == 0.0

    def test_multiple_perturbations(self):
        """Test with multiple perturbations."""
        nominal = {'mae': 2.0}
        perturbed = [
            {'mae': 2.5},
            {'mae': 3.0},
            {'mae': 1.5}
        ]
        metrics = compute_robustness_metrics(nominal, perturbed)

        # Deviations: 0.5, 1.0, 0.5
        assert metrics['mae']['mean_deviation'] == pytest.approx(2.0 / 3.0)
        assert metrics['mae']['max_deviation'] == 1.0

    def test_robustness_index_calculation(self):
        """Test robustness index calculation."""
        nominal = {'metric1': 10.0}
        perturbed = [{'metric1': 11.0}, {'metric1': 12.0}]
        metrics = compute_robustness_metrics(nominal, perturbed)

        # Mean deviation = 1.5, relative = 0.15, index = 1/(1+0.15)
        expected_index = 1.0 / (1.0 + 1.5 / 10.0)
        assert metrics['metric1']['robustness_index'] == pytest.approx(expected_index)

    def test_zero_nominal_value(self):
        """Test robustness with zero nominal value."""
        nominal = {'metric1': 0.0}
        perturbed = [{'metric1': 0.0001}, {'metric1': -0.0001}]
        metrics = compute_robustness_metrics(nominal, perturbed)

        # Should handle division by zero gracefully
        assert 'robustness_index' in metrics['metric1']
        assert 0.0 <= metrics['metric1']['robustness_index'] <= 1.0

    def test_specific_metric_names(self):
        """Test with specific metric names filter."""
        nominal = {'metric1': 1.0, 'metric2': 2.0}
        perturbed = [{'metric1': 1.1, 'metric2': 2.2}]
        metrics = compute_robustness_metrics(nominal, perturbed, metric_names=['metric1'])

        # Only metric1 should be analyzed
        assert 'metric1' in metrics
        assert 'metric2' not in metrics


# =====================================================================================
# Tests for compute_comprehensive_metrics
# =====================================================================================

class TestComputeComprehensiveMetrics:
    """Test comprehensive metrics integration."""

    def test_minimal_inputs(self):
        """Test with minimal inputs."""
        states = np.zeros((10, 6))
        controls = np.zeros(10)
        time_vector = np.linspace(0, 1, 10)

        metrics = compute_comprehensive_metrics(states, controls, time_vector)

        # Should have state metrics for each state dimension
        for i in range(6):
            assert f'state_{i}_metrics' in metrics

        # Should have control metrics
        assert 'control_metrics' in metrics

        # Should have stability metrics
        assert 'stability_metrics' in metrics

    def test_with_reference_states(self):
        """Test with reference state trajectory."""
        states = np.random.randn(10, 4)
        reference_states = np.zeros((10, 4))
        controls = np.random.randn(10)
        time_vector = np.linspace(0, 1, 10)

        metrics = compute_comprehensive_metrics(
            states, controls, time_vector,
            reference_states=reference_states
        )

        # Should have performance metrics for each state
        for i in range(4):
            assert f'state_{i}_performance' in metrics

    def test_with_reference_controls(self):
        """Test with reference control signals."""
        states = np.random.randn(10, 4)
        controls = np.random.randn(10)
        reference_controls = np.zeros(10)
        time_vector = np.linspace(0, 1, 10)

        metrics = compute_comprehensive_metrics(
            states, controls, time_vector,
            reference_controls=reference_controls
        )

        # Should have control performance metrics
        assert 'control_performance' in metrics

    def test_mismatched_reference_shapes(self):
        """Test with mismatched reference shapes (should be skipped)."""
        states = np.random.randn(10, 4)
        reference_states = np.zeros((5, 4))  # Wrong length
        controls = np.random.randn(10)
        time_vector = np.linspace(0, 1, 10)

        metrics = compute_comprehensive_metrics(
            states, controls, time_vector,
            reference_states=reference_states
        )

        # Should not have performance metrics due to shape mismatch
        assert 'state_0_performance' not in metrics

    def test_empty_arrays(self):
        """Test with empty arrays."""
        states = np.array([]).reshape(0, 4)
        controls = np.array([])
        time_vector = np.array([])

        metrics = compute_comprehensive_metrics(states, controls, time_vector)

        # Should return empty or minimal metrics
        assert isinstance(metrics, dict)

    def test_all_metrics_present(self):
        """Test that all expected metric categories are present."""
        states = np.random.randn(20, 6)
        controls = np.random.randn(20)
        reference_states = np.zeros((20, 6))
        reference_controls = np.zeros(20)
        time_vector = np.linspace(0, 2, 20)

        metrics = compute_comprehensive_metrics(
            states, controls, time_vector,
            reference_states=reference_states,
            reference_controls=reference_controls
        )

        # State metrics
        assert 'state_0_metrics' in metrics

        # Control metrics
        assert 'control_metrics' in metrics

        # Performance metrics
        assert 'state_0_performance' in metrics
        assert 'control_performance' in metrics

        # Stability metrics
        assert 'stability_metrics' in metrics
