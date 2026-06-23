"""
Unit tests for fault injection models.

Tests each fault type independently to verify correct behavior.
"""

import pytest
import numpy as np
from src.utils.testing.fault_injection.fault_models import (
    GaussianNoiseFault,
    BiasFault,
    DropoutFault,
    QuantizationFault,
    SaturationFault,
    DeadZoneFault,
    LagFault,
    JitterFault,
    GainErrorFault,
    SystemUncertaintyFault,
    DriftFault,
    DisturbanceFault
)


class TestGaussianNoiseFault:
    """Tests for GaussianNoiseFault."""

    def test_snr_calculation(self):
        """Verify SNR is approximately correct."""
        signal = np.ones(10000)  # Constant signal, RMS=1.0
        fault = GaussianNoiseFault(snr_db=20, seed=42)

        noisy = fault.inject(signal)
        noise = noisy - signal
        actual_snr = 20 * np.log10(np.std(signal) / (np.std(noise) + 1e-10))

        # Allow 2 dB tolerance due to finite sample size
        assert abs(actual_snr - 20) < 2.0

    def test_enabled_disabled(self):
        """Test enable/disable functionality."""
        signal = np.ones(100)
        fault = GaussianNoiseFault(snr_db=10, enabled=False)

        noisy = fault.inject(signal)
        assert np.allclose(noisy, signal)  # No corruption when disabled

        fault.enable()
        noisy = fault.inject(signal)
        assert not np.allclose(noisy, signal)  # Corruption when enabled

    def test_reproducibility(self):
        """Test that same seed produces same noise."""
        signal = np.ones(100)
        fault1 = GaussianNoiseFault(snr_db=30, seed=42)
        fault2 = GaussianNoiseFault(snr_db=30, seed=42)

        noisy1 = fault1.inject(signal)
        noisy2 = fault2.inject(signal)

        assert np.allclose(noisy1, noisy2)


class TestBiasFault:
    """Tests for BiasFault."""

    def test_constant_bias(self):
        """Verify constant offset is added."""
        signal = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        bias_magnitude = 0.5
        fault = BiasFault(bias_magnitude=bias_magnitude)

        biased = fault.inject(signal)
        expected = signal + bias_magnitude

        assert np.allclose(biased, expected)

    def test_target_specific_states(self):
        """Test biasing only specific state indices."""
        signal = np.array([1.0, 2.0, 3.0, 4.0])
        fault = BiasFault(bias_magnitude=1.0, target=[0, 2])  # Bias indices 0 and 2

        biased = fault.inject(signal)

        # Indices 0 and 2 should be biased, 1 and 3 unchanged
        assert biased[0] == signal[0] + 1.0
        assert biased[1] == signal[1]
        assert biased[2] == signal[2] + 1.0
        assert biased[3] == signal[3]


class TestDropoutFault:
    """Tests for DropoutFault."""

    def test_dropout_rate(self):
        """Verify dropout occurs at approximately specified rate."""
        signal_sequence = [np.array([float(i)]) for i in range(1000)]
        fault = DropoutFault(dropout_rate=0.1, seed=42)

        dropout_count = 0
        for i, signal in enumerate(signal_sequence):
            corrupted = fault.inject(signal)
            if i > 0 and np.allclose(corrupted, signal_sequence[i-1]):
                dropout_count += 1

        # Expect ~10% dropout (within reasonable tolerance)
        assert 50 < dropout_count < 150  # 5-15% range

    def test_hold_last_valid(self):
        """Verify dropout holds last valid value."""
        fault = DropoutFault(dropout_rate=1.0, seed=42)  # Always drop
        fault._last_valid = np.array([5.0])

        signal = np.array([10.0])
        corrupted = fault.inject(signal)

        assert np.allclose(corrupted, np.array([5.0]))  # Held last valid


class TestQuantizationFault:
    """Tests for QuantizationFault."""

    def test_quantization_levels(self):
        """Verify quantization produces discrete levels."""
        signal = np.linspace(0, 1, 100)
        fault = QuantizationFault(bit_depth=8, signal_range=1.0)

        quantized = fault.inject(signal)
        unique_values = np.unique(quantized)

        # 8-bit should have at most 256 unique levels
        assert len(unique_values) <= 256

    def test_quantum_size(self):
        """Verify quantum step size is correct."""
        fault = QuantizationFault(bit_depth=12, signal_range=2.0)
        expected_quantum = 2.0 / (2**12 - 1)

        assert abs(fault.quantum - expected_quantum) < 1e-9


class TestSaturationFault:
    """Tests for SaturationFault."""

    def test_saturation_limits(self):
        """Verify clipping at specified limits."""
        signal = np.array([-15.0, -5.0, 0.0, 5.0, 15.0])
        fault = SaturationFault(limit_pct=80, nominal_range=10.0)  # Limits at ±8.0

        saturated = fault.inject(signal)
        expected = np.array([-8.0, -5.0, 0.0, 5.0, 8.0])

        assert np.allclose(saturated, expected)

    def test_no_saturation_within_limits(self):
        """Verify no modification within limits."""
        signal = np.array([-5.0, 0.0, 5.0])
        fault = SaturationFault(limit_pct=80, nominal_range=10.0)

        saturated = fault.inject(signal)

        assert np.allclose(saturated, signal)


class TestDeadZoneFault:
    """Tests for DeadZoneFault."""

    def test_dead_zone_zeroing(self):
        """Verify signals in dead zone are zeroed."""
        signal = np.array([-0.5, -0.05, 0.0, 0.05, 0.5])
        fault = DeadZoneFault(dead_zone_width=0.1, center=0.0)

        corrupted = fault.inject(signal)

        # [-0.05, 0.0, 0.05] should be zeroed, others unchanged
        assert corrupted[0] == -0.5
        assert corrupted[1] == 0.0
        assert corrupted[2] == 0.0
        assert corrupted[3] == 0.0
        assert corrupted[4] == 0.5


class TestLagFault:
    """Tests for LagFault."""

    def test_lag_filtering(self):
        """Verify first-order lag behavior."""
        fault = LagFault(time_constant=0.1, dt=0.01)

        # Step input
        signal_step = np.array([10.0])
        output1 = fault.inject(signal_step)  # First step
        output2 = fault.inject(signal_step)  # Second step

        # Output should gradually approach input
        assert output1 < signal_step  # Not yet at input
        assert output2 > output1  # Increasing
        assert output2 < signal_step  # Still below input

    def test_lag_steady_state(self):
        """Verify lag reaches steady state eventually."""
        fault = LagFault(time_constant=0.01, dt=0.001)
        signal = np.array([5.0])

        # Iterate many times
        for _ in range(100):
            output = fault.inject(signal)

        # Should be very close to input after many iterations
        assert abs(output - signal) < 0.1


class TestJitterFault:
    """Tests for JitterFault."""

    def test_jitter_amplitude(self):
        """Verify jitter adds oscillations."""
        signal = np.array([10.0])
        fault = JitterFault(jitter_amplitude=0.1, jitter_frequency=50.0)

        outputs = []
        for _ in range(100):
            output = fault.inject(signal, dt=0.001)
            outputs.append(output)

        outputs = np.array(outputs).flatten()

        # Jitter should cause variation around nominal
        assert np.std(outputs) > 0.1  # Some variation present


class TestGainErrorFault:
    """Tests for GainErrorFault."""

    def test_gain_variation_range(self):
        """Verify gain errors are within specified tolerance."""
        nominal_gains = np.array([10.0, 5.0, 8.0, 3.0, 15.0, 2.0])
        tolerance_pct = 10.0
        fault = GainErrorFault(tolerance_pct=tolerance_pct, seed=42)

        corrupted_gains = fault.inject(nominal_gains)
        relative_errors = (corrupted_gains - nominal_gains) / nominal_gains * 100.0

        # All errors should be within ±tolerance
        assert np.all(np.abs(relative_errors) <= tolerance_pct * 1.1)  # Small margin

    def test_reproducibility(self):
        """Test that same seed produces same gain errors."""
        nominal_gains = np.array([10.0, 5.0, 8.0])
        fault1 = GainErrorFault(tolerance_pct=10, seed=123)
        fault2 = GainErrorFault(tolerance_pct=10, seed=123)

        corrupted1 = fault1.inject(nominal_gains)
        corrupted2 = fault2.inject(nominal_gains)

        assert np.allclose(corrupted1, corrupted2)


class TestSystemUncertaintyFault:
    """Tests for SystemUncertaintyFault."""

    def test_parameter_variations(self):
        """Verify specified parameters are varied."""
        params = {
            'mass_cart': 1.0,
            'mass_pole1': 0.1,
            'inertia_pole1': 0.05,
            'other_param': 2.0
        }

        variations = {
            'mass_cart': 10.0,  # ±10%
            'inertia_pole1': 15.0  # ±15%
        }

        fault = SystemUncertaintyFault(param_variations=variations, seed=42)
        corrupted_params = fault.inject_parameters(params)

        # Check varied parameters are within tolerance
        assert abs(corrupted_params['mass_cart'] - params['mass_cart']) <= 0.1 * params['mass_cart']
        assert abs(corrupted_params['inertia_pole1'] - params['inertia_pole1']) <= 0.15 * params['inertia_pole1']

        # Check unchanged parameters
        assert corrupted_params['mass_pole1'] == params['mass_pole1']
        assert corrupted_params['other_param'] == params['other_param']


class TestDriftFault:
    """Tests for DriftFault."""

    def test_linear_drift(self):
        """Verify linear drift increases over time."""
        signal = np.array([10.0])
        fault = DriftFault(drift_rate=0.1, drift_pattern='linear')

        output1 = fault.inject(signal, dt=1.0)  # t=1s
        output2 = fault.inject(signal, dt=1.0)  # t=2s

        # Linear drift should increase linearly
        assert output2 > output1
        drift1 = output1 - signal
        drift2 = output2 - signal
        assert abs((drift2 - drift1) / drift1 - 1.0) < 0.2  # Approximately linear


class TestDisturbanceFault:
    """Tests for DisturbanceFault."""

    def test_step_disturbance(self):
        """Verify step disturbance adds constant after start time."""
        signal = np.array([0.0])
        fault = DisturbanceFault(
            disturbance_type='step',
            magnitude=5.0,
            start_time=1.0,
            end_time=3.0
        )

        before = fault.inject(signal, time=0.5)
        during = fault.inject(signal, time=2.0)
        after = fault.inject(signal, time=4.0)

        assert np.allclose(before, signal)  # No disturbance before start
        assert np.allclose(during, signal + 5.0)  # Disturbance during
        assert np.allclose(after, signal)  # No disturbance after end

    def test_periodic_disturbance(self):
        """Verify periodic disturbance oscillates."""
        signal = np.array([0.0])
        fault = DisturbanceFault(
            disturbance_type='periodic',
            magnitude=1.0,
            frequency=1.0,  # 1 Hz
            start_time=0.0,
            end_time=10.0
        )

        outputs = []
        for t in np.linspace(0, 1, 100):
            output = fault.inject(signal, time=t)
            outputs.append(output.item())

        outputs = np.array(outputs)

        # Should oscillate (check for zero crossings)
        zero_crossings = np.sum(np.diff(np.sign(outputs)) != 0)
        assert zero_crossings >= 1  # At least one zero crossing in 1 second


# Run tests if executed directly
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
