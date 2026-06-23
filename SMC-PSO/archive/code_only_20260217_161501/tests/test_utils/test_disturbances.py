"""
================================================================================
Unit Tests for Disturbance Generation Module
================================================================================

Unit tests for src/utils/disturbances.py

Tests cover:
1. DisturbanceConfig validation
2. Step disturbances (constant force)
3. Impulse disturbances (brief spike)
4. Sinusoidal disturbances (periodic)
5. Random disturbances (Gaussian noise)
6. Combined disturbances (multiple types)
7. Factory functions (scenario creation)
8. Edge cases and error handling

Author: DIP_SMC_PSO Team
Created: December 21, 2025 (Session 14 - Push to 20% Coverage)
"""

import pytest
import numpy as np
from src.utils.disturbances import (
    DisturbanceType,
    DisturbanceConfig,
    DisturbanceGenerator,
    create_step_scenario,
    create_impulse_scenario,
    create_sinusoidal_scenario,
    create_random_scenario,
    create_combined_scenario,
)


# =============================================================================
# Test DisturbanceConfig Validation
# =============================================================================

def test_config_valid_step():
    """Valid step disturbance configuration."""
    config = DisturbanceConfig(
        type=DisturbanceType.STEP,
        magnitude=10.0,
        start_time=2.0,
        duration=float('inf'),
        axis=0
    )
    assert config.magnitude == 10.0
    assert config.start_time == 2.0
    assert config.duration == float('inf')
    assert config.axis == 0


def test_config_valid_impulse():
    """Valid impulse disturbance configuration."""
    config = DisturbanceConfig(
        type=DisturbanceType.IMPULSE,
        magnitude=50.0,
        start_time=1.0,
        duration=0.1,
        axis=1
    )
    assert config.magnitude == 50.0
    assert config.duration == 0.1
    assert config.axis == 1


def test_config_negative_magnitude_raises():
    """Negative magnitude should raise ValueError."""
    with pytest.raises(ValueError, match="magnitude must be non-negative"):
        DisturbanceConfig(
            type=DisturbanceType.STEP,
            magnitude=-10.0,
            axis=0
        )


def test_config_negative_start_time_raises():
    """Negative start time should raise ValueError."""
    with pytest.raises(ValueError, match="Start time must be non-negative"):
        DisturbanceConfig(
            type=DisturbanceType.STEP,
            magnitude=10.0,
            start_time=-1.0,
            axis=0
        )


def test_config_zero_duration_raises():
    """Zero duration (non-infinite) should raise ValueError."""
    with pytest.raises(ValueError, match="Duration must be positive or infinite"):
        DisturbanceConfig(
            type=DisturbanceType.IMPULSE,
            magnitude=10.0,
            duration=0.0,
            axis=0
        )


def test_config_negative_duration_raises():
    """Negative duration should raise ValueError."""
    with pytest.raises(ValueError, match="Duration must be positive or infinite"):
        DisturbanceConfig(
            type=DisturbanceType.IMPULSE,
            magnitude=10.0,
            duration=-0.5,
            axis=0
        )


def test_config_invalid_axis_raises():
    """Invalid axis (not 0, 1, 2) should raise ValueError."""
    with pytest.raises(ValueError, match="Axis must be 0.*1.*2"):
        DisturbanceConfig(
            type=DisturbanceType.STEP,
            magnitude=10.0,
            axis=5
        )


def test_config_all_axes_valid():
    """All three axes (0, 1, 2) should be valid."""
    for axis in [0, 1, 2]:
        config = DisturbanceConfig(
            type=DisturbanceType.STEP,
            magnitude=10.0,
            axis=axis
        )
        assert config.axis == axis


# =============================================================================
# Test DisturbanceGenerator - Step Disturbances
# =============================================================================

def test_step_before_start_time():
    """Step disturbance should be zero before start time."""
    gen = DisturbanceGenerator()
    gen.add_step_disturbance(magnitude=20.0, start_time=2.0, axis=0)

    # Before step
    d_cart, d_link1, d_link2 = gen.get_disturbance(t=1.0)
    assert d_cart == 0.0
    assert d_link1 == 0.0
    assert d_link2 == 0.0


def test_step_after_start_time():
    """Step disturbance should equal magnitude after start time."""
    gen = DisturbanceGenerator()
    gen.add_step_disturbance(magnitude=20.0, start_time=2.0, axis=0)

    # After step
    d_cart, d_link1, d_link2 = gen.get_disturbance(t=3.0)
    assert d_cart == 20.0
    assert d_link1 == 0.0
    assert d_link2 == 0.0


def test_step_at_exact_start_time():
    """Step disturbance should be active at exact start time."""
    gen = DisturbanceGenerator()
    gen.add_step_disturbance(magnitude=15.0, start_time=2.0, axis=0)

    # Exactly at start time
    d_cart, _, _ = gen.get_disturbance(t=2.0)
    assert d_cart == 15.0


def test_step_on_different_axes():
    """Step disturbances should apply to correct axes."""
    gen = DisturbanceGenerator()

    # Cart force
    gen.add_step_disturbance(magnitude=10.0, start_time=1.0, axis=0)
    d_cart, d_link1, d_link2 = gen.get_disturbance(t=2.0)
    assert d_cart == 10.0
    assert d_link1 == 0.0
    assert d_link2 == 0.0

    # Link 1 torque
    gen.clear_disturbances()
    gen.add_step_disturbance(magnitude=15.0, start_time=1.0, axis=1)
    d_cart, d_link1, d_link2 = gen.get_disturbance(t=2.0)
    assert d_cart == 0.0
    assert d_link1 == 15.0
    assert d_link2 == 0.0

    # Link 2 torque
    gen.clear_disturbances()
    gen.add_step_disturbance(magnitude=20.0, start_time=1.0, axis=2)
    d_cart, d_link1, d_link2 = gen.get_disturbance(t=2.0)
    assert d_cart == 0.0
    assert d_link1 == 0.0
    assert d_link2 == 20.0


def test_step_persistence():
    """Step disturbance should persist indefinitely."""
    gen = DisturbanceGenerator()
    gen.add_step_disturbance(magnitude=10.0, start_time=1.0, axis=0)

    # Should be active at t=100s
    d_cart, _, _ = gen.get_disturbance(t=100.0)
    assert d_cart == 10.0


# =============================================================================
# Test DisturbanceGenerator - Impulse Disturbances
# =============================================================================

def test_impulse_before_start():
    """Impulse should be zero before start time."""
    gen = DisturbanceGenerator()
    gen.add_impulse_disturbance(magnitude=50.0, start_time=2.0, duration=0.1, axis=0)

    d_cart, _, _ = gen.get_disturbance(t=1.0)
    assert d_cart == 0.0


def test_impulse_during_duration():
    """Impulse should equal magnitude during duration."""
    gen = DisturbanceGenerator()
    gen.add_impulse_disturbance(magnitude=50.0, start_time=2.0, duration=0.1, axis=0)

    # During impulse
    d_cart, _, _ = gen.get_disturbance(t=2.05)
    assert d_cart == 50.0


def test_impulse_after_duration():
    """Impulse should be zero after duration."""
    gen = DisturbanceGenerator()
    gen.add_impulse_disturbance(magnitude=50.0, start_time=2.0, duration=0.1, axis=0)

    # After impulse (t > start + duration)
    d_cart, _, _ = gen.get_disturbance(t=2.2)
    assert d_cart == 0.0


def test_impulse_at_boundaries():
    """Impulse boundaries should be inclusive at both start and end."""
    gen = DisturbanceGenerator()
    gen.add_impulse_disturbance(magnitude=40.0, start_time=2.0, duration=0.1, axis=0)

    # At start (inclusive)
    d_start, _, _ = gen.get_disturbance(t=2.0)
    assert d_start == 40.0

    # Just before end
    d_before_end, _, _ = gen.get_disturbance(t=2.09)
    assert d_before_end == 40.0

    # At exact end (inclusive: t <= start + duration)
    d_end, _, _ = gen.get_disturbance(t=2.1)
    assert d_end == 40.0  # Boundary is inclusive

    # Just after end (exclusive: t > start + duration)
    d_after, _, _ = gen.get_disturbance(t=2.11)
    assert d_after == 0.0


def test_impulse_short_duration():
    """Very short impulse (0.01s) should work."""
    gen = DisturbanceGenerator()
    gen.add_impulse_disturbance(magnitude=100.0, start_time=1.0, duration=0.01, axis=0)

    # During brief impulse
    d_cart, _, _ = gen.get_disturbance(t=1.005)
    assert d_cart == 100.0


# =============================================================================
# Test DisturbanceGenerator - Sinusoidal Disturbances
# =============================================================================

def test_sinusoidal_zero_at_start():
    """Sinusoidal disturbance should start at zero."""
    gen = DisturbanceGenerator()
    gen.add_sinusoidal_disturbance(magnitude=15.0, frequency=1.0, start_time=2.0, axis=0)

    # At start: sin(0) = 0
    d_cart, _, _ = gen.get_disturbance(t=2.0)
    assert abs(d_cart) < 1e-10


def test_sinusoidal_peak_at_quarter_period():
    """Sinusoidal disturbance should peak at quarter period."""
    gen = DisturbanceGenerator()
    gen.add_sinusoidal_disturbance(magnitude=10.0, frequency=1.0, start_time=0.0, axis=0)

    # At t=0.25s (quarter period for f=1Hz): sin(π/2) = 1
    d_cart, _, _ = gen.get_disturbance(t=0.25)
    assert abs(d_cart - 10.0) < 1e-6


def test_sinusoidal_frequency_scaling():
    """Higher frequency should oscillate faster."""
    gen_low = DisturbanceGenerator()
    gen_low.add_sinusoidal_disturbance(magnitude=10.0, frequency=1.0, start_time=0.0, axis=0)

    gen_high = DisturbanceGenerator()
    gen_high.add_sinusoidal_disturbance(magnitude=10.0, frequency=2.0, start_time=0.0, axis=0)

    # At t=0.125s:
    # f=1Hz: sin(2π * 1 * 0.125) = sin(π/4) ≈ 0.707
    # f=2Hz: sin(2π * 2 * 0.125) = sin(π/2) = 1.0
    d_low, _, _ = gen_low.get_disturbance(t=0.125)
    d_high, _, _ = gen_high.get_disturbance(t=0.125)

    assert abs(d_low - 10.0 * np.sin(np.pi / 4)) < 1e-6
    assert abs(d_high - 10.0) < 1e-6


def test_sinusoidal_before_start_time():
    """Sinusoidal disturbance should be zero before start."""
    gen = DisturbanceGenerator()
    gen.add_sinusoidal_disturbance(magnitude=10.0, frequency=1.0, start_time=2.0, axis=0)

    d_cart, _, _ = gen.get_disturbance(t=1.0)
    assert d_cart == 0.0


def test_sinusoidal_after_duration():
    """Sinusoidal disturbance should be zero after duration."""
    gen = DisturbanceGenerator()
    gen.add_sinusoidal_disturbance(magnitude=10.0, frequency=1.0, start_time=1.0, duration=2.0, axis=0)

    # After duration (t > 1.0 + 2.0)
    d_cart, _, _ = gen.get_disturbance(t=4.0)
    assert d_cart == 0.0


# =============================================================================
# Test DisturbanceGenerator - Random Disturbances
# =============================================================================

def test_random_disturbance_with_seed():
    """Random disturbance should be reproducible with seed."""
    gen1 = DisturbanceGenerator(seed=42)
    gen1.add_random_disturbance(std_dev=5.0, axis=0)

    gen2 = DisturbanceGenerator(seed=42)
    gen2.add_random_disturbance(std_dev=5.0, axis=0)

    # Same seed → same random values
    d1, _, _ = gen1.get_disturbance(t=1.0)
    d2, _, _ = gen2.get_disturbance(t=1.0)
    assert d1 == d2


def test_random_disturbance_different_each_call():
    """Random disturbance should vary with time (different RNG calls)."""
    gen = DisturbanceGenerator(seed=42)
    gen.add_random_disturbance(std_dev=5.0, axis=0)

    # Different time points → different random samples
    values = [gen.get_disturbance(t=float(i))[0] for i in range(10)]

    # Not all values should be identical
    assert len(set(values)) > 1


def test_random_disturbance_zero_mean():
    """Random disturbance should have approximately zero mean (large sample)."""
    gen = DisturbanceGenerator(seed=42)
    gen.add_random_disturbance(std_dev=5.0, axis=0)

    # Large sample
    samples = [gen.get_disturbance(t=float(i))[0] for i in range(1000)]
    mean = np.mean(samples)

    # Should be close to zero (within 3 sigma / sqrt(n))
    assert abs(mean) < 0.5  # 5 * 3 / sqrt(1000) ≈ 0.47


def test_random_disturbance_before_start():
    """Random disturbance should be zero before start time."""
    gen = DisturbanceGenerator(seed=42)
    gen.add_random_disturbance(std_dev=5.0, start_time=2.0, axis=0)

    d_cart, _, _ = gen.get_disturbance(t=1.0)
    assert d_cart == 0.0


# =============================================================================
# Test DisturbanceGenerator - Combined Disturbances
# =============================================================================

def test_multiple_disturbances_sum():
    """Multiple disturbances on same axis should sum."""
    gen = DisturbanceGenerator()
    gen.add_step_disturbance(magnitude=10.0, start_time=1.0, axis=0)
    gen.add_step_disturbance(magnitude=5.0, start_time=1.0, axis=0)

    # Both active at t=2s
    d_cart, _, _ = gen.get_disturbance(t=2.0)
    assert d_cart == 15.0


def test_multiple_disturbances_different_axes():
    """Disturbances on different axes should not interfere."""
    gen = DisturbanceGenerator()
    gen.add_step_disturbance(magnitude=10.0, start_time=0.0, axis=0)
    gen.add_step_disturbance(magnitude=20.0, start_time=0.0, axis=1)
    gen.add_step_disturbance(magnitude=30.0, start_time=0.0, axis=2)

    d_cart, d_link1, d_link2 = gen.get_disturbance(t=1.0)
    assert d_cart == 10.0
    assert d_link1 == 20.0
    assert d_link2 == 30.0


def test_clear_disturbances():
    """clear_disturbances() should remove all disturbances."""
    gen = DisturbanceGenerator()
    gen.add_step_disturbance(magnitude=10.0, start_time=0.0, axis=0)
    gen.add_impulse_disturbance(magnitude=50.0, start_time=2.0, duration=0.1, axis=1)

    # Clear all
    gen.clear_disturbances()

    # Should be zero everywhere
    d_cart, d_link1, d_link2 = gen.get_disturbance(t=3.0)
    assert d_cart == 0.0
    assert d_link1 == 0.0
    assert d_link2 == 0.0


def test_get_disturbance_force_only():
    """get_disturbance_force_only() should return only cart force."""
    gen = DisturbanceGenerator()
    gen.add_step_disturbance(magnitude=25.0, start_time=0.0, axis=0)
    gen.add_step_disturbance(magnitude=50.0, start_time=0.0, axis=1)

    d_force = gen.get_disturbance_force_only(t=1.0)
    assert d_force == 25.0  # Only cart force


# =============================================================================
# Test Factory Functions
# =============================================================================

def test_create_step_scenario():
    """create_step_scenario() should create step disturbance."""
    gen = create_step_scenario(magnitude=30.0, start_time=3.0)

    # Before step
    d_before, _, _ = gen.get_disturbance(t=2.0)
    assert d_before == 0.0

    # After step
    d_after, _, _ = gen.get_disturbance(t=4.0)
    assert d_after == 30.0


def test_create_impulse_scenario():
    """create_impulse_scenario() should create impulse disturbance."""
    gen = create_impulse_scenario(magnitude=60.0, start_time=2.0, duration=0.2)

    # During impulse
    d_during, _, _ = gen.get_disturbance(t=2.1)
    assert d_during == 60.0

    # After impulse
    d_after, _, _ = gen.get_disturbance(t=2.5)
    assert d_after == 0.0


def test_create_sinusoidal_scenario():
    """create_sinusoidal_scenario() should create sinusoidal disturbance."""
    gen = create_sinusoidal_scenario(magnitude=12.0, frequency=2.0)

    # At t=0.125s: sin(2π * 2 * 0.125) = sin(π/2) = 1
    d_peak, _, _ = gen.get_disturbance(t=0.125)
    assert abs(d_peak - 12.0) < 1e-6


def test_create_random_scenario():
    """create_random_scenario() should create random disturbance."""
    gen = create_random_scenario(std_dev=3.0)

    # Should return non-zero random value
    d_random, _, _ = gen.get_disturbance(t=1.0)
    # Can't test exact value (random), but should be finite
    assert np.isfinite(d_random)


def test_create_combined_scenario():
    """create_combined_scenario() should have multiple disturbances."""
    gen = create_combined_scenario()

    # At t=3s: step (20 N) + random noise
    d_cart, _, _ = gen.get_disturbance(t=3.0)

    # Should have step component (≈20 N, plus random noise)
    # Can't test exact value (random), but should be close to 20
    assert 10.0 < abs(d_cart) < 30.0  # Rough range check


# =============================================================================
# Test Edge Cases
# =============================================================================

def test_no_disturbances():
    """Generator with no disturbances should return zeros."""
    gen = DisturbanceGenerator()

    d_cart, d_link1, d_link2 = gen.get_disturbance(t=5.0)
    assert d_cart == 0.0
    assert d_link1 == 0.0
    assert d_link2 == 0.0


def test_zero_magnitude_disturbance():
    """Zero magnitude disturbance should have no effect."""
    gen = DisturbanceGenerator()
    gen.add_step_disturbance(magnitude=0.0, start_time=0.0, axis=0)

    d_cart, _, _ = gen.get_disturbance(t=1.0)
    assert d_cart == 0.0


def test_large_time_values():
    """Generator should handle large time values (t=1000s)."""
    gen = DisturbanceGenerator()
    gen.add_step_disturbance(magnitude=10.0, start_time=0.0, axis=0)

    d_cart, _, _ = gen.get_disturbance(t=1000.0)
    assert d_cart == 10.0


def test_very_small_time_steps():
    """Generator should handle very small time steps."""
    gen = DisturbanceGenerator()
    gen.add_step_disturbance(magnitude=5.0, start_time=1.0, axis=0)

    # Just before step
    d_before, _, _ = gen.get_disturbance(t=1.0 - 1e-10)
    assert d_before == 0.0

    # Just after step
    d_after, _, _ = gen.get_disturbance(t=1.0 + 1e-10)
    assert d_after == 5.0


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
