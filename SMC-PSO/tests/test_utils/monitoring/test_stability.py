#======================================================================================\\\
#=================== tests/test_utils/monitoring/test_stability.py ====================\\\
#======================================================================================\\\

"""
Comprehensive tests for stability monitoring system.

Tests cover:
- LyapunovDecreaseMonitor: LDR computation, alert triggering, transient handling
- SaturationMonitor: Saturation duty, rate limits, alert conditions
- DynamicsConditioningMonitor: Matrix conditioning, fallback tracking
- StabilityMonitoringSystem: Integrated monitoring, violation tracking, reporting
"""

import pytest
import numpy as np

from src.utils.monitoring.realtime.stability import (
    LyapunovDecreaseMonitor,
    SaturationMonitor,
    DynamicsConditioningMonitor,
    StabilityMonitoringSystem
)


# =====================================================================================
# Tests for LyapunovDecreaseMonitor
# =====================================================================================

class TestLyapunovDecreaseMonitor:
    """Test Lyapunov Decrease Ratio monitoring."""

    def test_initialization(self):
        """Test monitor initialization with default parameters."""
        monitor = LyapunovDecreaseMonitor()

        assert monitor.window_size_ms == 300.0
        assert monitor.dt == 0.01
        assert monitor.ldr_threshold == 0.95
        assert monitor.transient_time == 1.0
        assert monitor.window_samples > 0
        assert monitor.sample_count.get() == 0

    def test_initialization_custom_params(self):
        """Test monitor initialization with custom parameters."""
        monitor = LyapunovDecreaseMonitor(
            window_size_ms=500.0,
            dt=0.02,
            ldr_threshold=0.9,
            transient_time=2.0
        )

        assert monitor.window_size_ms == 500.0
        assert monitor.dt == 0.02
        assert monitor.ldr_threshold == 0.9
        assert monitor.transient_time == 2.0

    def test_transient_period(self):
        """Test behavior during transient period."""
        monitor = LyapunovDecreaseMonitor(dt=0.01, transient_time=0.5)

        # During transient period (first 50 samples)
        for i in range(30):
            sigma = np.array([1.0, 0.5])
            result = monitor.update(sigma)

            assert result['status'] == 'transient'
            assert result['alert'] == False
            assert result['ldr'] == 1.0

    def test_ldr_computation_decreasing(self):
        """Test LDR computation with consistently decreasing Lyapunov function."""
        monitor = LyapunovDecreaseMonitor(
            window_size_ms=100.0,
            dt=0.01,
            transient_time=0.1
        )

        # Skip transient period
        for _ in range(15):
            monitor.update(np.array([1.0, 0.5]))

        # Create decreasing sigma values
        for i in range(50):
            decay = np.exp(-0.1 * i)
            sigma = np.array([decay, 0.5 * decay])
            result = monitor.update(sigma)

        # LDR should be close to 100% (all decreasing)
        assert result['ldr'] >= 0.95
        assert result['alert'] == False
        assert result['status'] == 'monitoring'

    def test_ldr_computation_increasing(self):
        """Test LDR computation with increasing Lyapunov function (alert condition)."""
        monitor = LyapunovDecreaseMonitor(
            window_size_ms=100.0,
            dt=0.01,
            ldr_threshold=0.95,
            transient_time=0.1
        )

        # Skip transient period
        for _ in range(15):
            monitor.update(np.array([0.1, 0.05]))

        # Create increasing sigma values (unstable)
        for i in range(50):
            growth = 0.1 + 0.01 * i
            sigma = np.array([growth, 0.5 * growth])
            result = monitor.update(sigma)

        # LDR should be low (mostly increasing)
        assert result['ldr'] < 0.5
        assert result['alert'] == True

    def test_sigma_dot_sigma_computation(self):
        """Test sigma*sigma_dot reachability analysis."""
        monitor = LyapunovDecreaseMonitor(dt=0.01, transient_time=0.1)

        # Skip transient
        for _ in range(15):
            monitor.update(np.array([1.0, 0.5]))

        # Decreasing sigma (should have negative sigma_dot_sigma)
        sigma1 = np.array([1.0, 0.5])
        monitor.update(sigma1)
        sigma2 = np.array([0.9, 0.4])
        result = monitor.update(sigma2)

        # sigma*sigma_dot should be negative for decreasing
        assert result['sigma_dot_sigma'] < 0

    def test_reset_functionality(self):
        """Test monitor reset."""
        monitor = LyapunovDecreaseMonitor()

        # Add some data
        for _ in range(50):
            monitor.update(np.array([1.0, 0.5]))

        # Reset
        monitor.reset()

        assert monitor.sample_count.get() == 0
        assert monitor.alert_count.get() == 0
        assert len(monitor.sigma_history) == 0
        assert len(monitor.lyapunov_history) == 0

    def test_alert_counting(self):
        """Test alert counter increments."""
        monitor = LyapunovDecreaseMonitor(
            window_size_ms=100.0,
            dt=0.01,
            ldr_threshold=0.95,
            transient_time=0.1
        )

        # Skip transient
        for _ in range(15):
            monitor.update(np.array([0.1, 0.05]))

        initial_alerts = monitor.alert_count.get()

        # Create unstable behavior
        for i in range(50):
            growth = 0.1 + 0.02 * i
            sigma = np.array([growth, 0.5 * growth])
            monitor.update(sigma)

        # Alert count should have increased
        assert monitor.alert_count.get() > initial_alerts


# =====================================================================================
# Tests for SaturationMonitor
# =====================================================================================

class TestSaturationMonitor:
    """Test saturation and rate limit monitoring."""

    def test_initialization(self):
        """Test monitor initialization."""
        monitor = SaturationMonitor()

        assert monitor.max_force == 150.0
        assert monitor.dt == 0.01
        assert monitor.duty_threshold == 0.2
        assert monitor.rate_hit_threshold == 0.01
        assert monitor.sample_count.get() == 0

    def test_transient_period(self):
        """Test behavior during transient period."""
        monitor = SaturationMonitor(dt=0.01, transient_time=0.5)

        for _ in range(30):
            result = monitor.update(50.0)

            assert result['status'] == 'transient'
            assert result['alert'] == False

    def test_no_saturation(self):
        """Test with control forces well below saturation."""
        monitor = SaturationMonitor(
            max_force=100.0,
            dt=0.01,
            transient_time=0.1
        )

        # Skip transient
        for _ in range(15):
            monitor.update(10.0)

        # Apply moderate forces
        for _ in range(100):
            result = monitor.update(50.0)

        assert result['duty'] == 0.0
        assert result['alert'] == False

    def test_saturation_duty_calculation(self):
        """Test saturation duty calculation."""
        monitor = SaturationMonitor(
            max_force=100.0,
            dt=0.01,
            duty_threshold=0.3,
            transient_time=0.1
        )

        # Skip transient
        for _ in range(15):
            monitor.update(10.0)

        # Apply 50% saturated forces in window
        for i in range(100):
            if i % 2 == 0:
                force = 99.0  # Saturated (99% of max)
            else:
                force = 10.0  # Not saturated
            result = monitor.update(force)

        # Duty should be approximately 50%
        assert result['duty'] == pytest.approx(0.5, abs=0.05)

    def test_saturation_alert_triggering(self):
        """Test alert triggering on high saturation duty."""
        monitor = SaturationMonitor(
            max_force=100.0,
            dt=0.01,
            duty_threshold=0.2,
            transient_time=0.1
        )

        # Skip transient
        for _ in range(15):
            monitor.update(10.0)

        # Apply sustained saturation (should trigger alert)
        for _ in range(100):
            result = monitor.update(99.0)

        assert result['duty'] > 0.9
        assert result['alert'] == True

    def test_rate_limit_detection(self):
        """Test rate limit hit detection."""
        monitor = SaturationMonitor(
            max_force=100.0,
            dt=0.01,
            transient_time=0.1
        )

        # Skip transient
        for _ in range(15):
            monitor.update(10.0)

        # Create rate limit hits (large force changes)
        max_rate = 100.0 / 0.01  # 10000
        for i in range(50):
            if i % 2 == 0:
                force = 0.0
            else:
                force = 100.0  # Rate = 10000 (at limit)
            result = monitor.update(force)

        # Should detect rate hits
        assert result['rate_hit_rate'] > 0

    def test_continuous_saturation_tracking(self):
        """Test continuous saturation time tracking."""
        monitor = SaturationMonitor(
            max_force=100.0,
            dt=0.01,
            transient_time=0.1
        )

        # Skip transient
        for _ in range(15):
            monitor.update(10.0)

        # Apply continuous saturation for 30 steps (0.3s)
        for _ in range(30):
            result = monitor.update(99.0)

        # Continuous saturation should be tracked
        assert result['continuous_saturation_ms'] > 200  # > 200ms triggers alert
        assert result['alert'] == True

    def test_reset_functionality(self):
        """Test monitor reset."""
        monitor = SaturationMonitor()

        for _ in range(50):
            monitor.update(99.0)

        monitor.reset()

        assert monitor.sample_count.get() == 0
        assert monitor.saturation_count.get() == 0
        assert monitor.rate_hit_count.get() == 0
        assert monitor.continuous_saturation_time == 0.0


# =====================================================================================
# Tests for DynamicsConditioningMonitor
# =====================================================================================

class TestDynamicsConditioningMonitor:
    """Test dynamics matrix conditioning monitoring."""

    def test_initialization(self):
        """Test monitor initialization."""
        monitor = DynamicsConditioningMonitor()

        assert monitor.condition_threshold == 1e7
        assert monitor.spike_threshold == 1e9
        assert monitor.fallback_threshold == 3
        assert monitor.sample_count.get() == 0

    def test_well_conditioned_matrix(self):
        """Test with well-conditioned matrix."""
        monitor = DynamicsConditioningMonitor(condition_threshold=1e7)

        # Well-conditioned identity matrix
        for _ in range(50):
            mass_matrix = np.eye(2)
            result = monitor.update(mass_matrix)

        assert result['median_condition'] < 10.0
        assert result['alert'] == False

    def test_poorly_conditioned_matrix(self):
        """Test with poorly conditioned matrix."""
        monitor = DynamicsConditioningMonitor(condition_threshold=1e3)

        # Nearly singular matrix
        poorly_conditioned = np.array([[1.0, 0.9999], [0.9999, 1.0]])

        for _ in range(50):
            result = monitor.update(poorly_conditioned)

        # Condition number should be high
        assert result['median_condition'] > 1e3
        assert result['median_alert'] == True
        assert result['alert'] == True

    def test_condition_spike_detection(self):
        """Test detection of condition number spikes."""
        monitor = DynamicsConditioningMonitor(
            condition_threshold=1e7,
            spike_threshold=1e4  # Lower threshold for test
        )

        # Mostly good matrices with occasional spike
        for i in range(100):
            if i == 50:
                # Spike with nearly singular matrix (higher condition number)
                mass_matrix = np.array([[1.0, 0.999999], [0.999999, 1.0]])
            else:
                # Good matrix
                mass_matrix = np.eye(2)

            result = monitor.update(mass_matrix)

        # Should detect spike in p99
        assert result['p99_condition'] > monitor.spike_threshold
        assert result['spike_alert'] == True

    def test_fallback_inversion_tracking(self):
        """Test fallback inversion counter."""
        monitor = DynamicsConditioningMonitor(fallback_threshold=5)

        mass_matrix = np.eye(2)

        # Trigger fallbacks
        for i in range(10):
            result = monitor.update(mass_matrix, used_fallback=(i < 7))

        assert result['fallback_count'] == 7
        assert result['fallback_alert'] == True
        assert result['alert'] == True

    def test_singular_matrix_handling(self):
        """Test handling of singular/invalid matrices."""
        monitor = DynamicsConditioningMonitor()

        # Singular matrix (determinant = 0)
        singular_matrix = np.array([[1.0, 1.0], [1.0, 1.0]])

        result = monitor.update(singular_matrix)

        # Should handle gracefully with very high condition number
        assert result['current_condition'] > 1e10
        assert 'alert' in result

    def test_reset_functionality(self):
        """Test monitor reset."""
        monitor = DynamicsConditioningMonitor()

        for i in range(50):
            monitor.update(np.eye(2), used_fallback=(i % 3 == 0))

        monitor.reset()

        assert monitor.sample_count.get() == 0
        assert monitor.fallback_count.get() == 0
        assert len(monitor.condition_history) == 0


# =====================================================================================
# Tests for StabilityMonitoringSystem
# =====================================================================================

class TestStabilityMonitoringSystem:
    """Test integrated stability monitoring system."""

    def test_initialization_default_config(self):
        """Test system initialization with default config."""
        system = StabilityMonitoringSystem()

        assert system.ldr_monitor is not None
        assert system.saturation_monitor is not None
        assert system.conditioning_monitor is not None
        assert system.episode_count.get() == 0

    def test_initialization_custom_config(self):
        """Test system initialization with custom config."""
        config = {
            'dt': 0.02,
            'max_force': 200.0,
            'ldr_threshold': 0.9,
            'duty_threshold': 0.3
        }

        system = StabilityMonitoringSystem(config)

        assert system.ldr_monitor.dt == 0.02
        assert system.saturation_monitor.max_force == 200.0
        assert system.ldr_monitor.ldr_threshold == 0.9
        assert system.saturation_monitor.duty_threshold == 0.3

    def test_integrated_update_no_alerts(self):
        """Test integrated update with no alerts."""
        config = {'dt': 0.01, 'max_force': 150.0, 'transient_time': 0.1}
        system = StabilityMonitoringSystem(config)

        # Skip transient
        for _ in range(15):
            system.update(
                sigma=np.array([0.5, 0.25]),
                control_force=50.0,
                mass_matrix=np.eye(2)
            )

        # Stable operation with consistently decreasing sigma
        for i in range(100):
            decay = np.exp(-0.05 * i)  # Faster decay to ensure LDR > 0.95
            result = system.update(
                sigma=np.array([0.5, 0.25]) * decay,
                control_force=50.0,
                mass_matrix=np.eye(2)
            )

        # Final result should have no alerts
        assert result['alert'] == False
        assert result['ldr']['alert'] == False
        assert result['saturation']['alert'] == False
        assert result['conditioning']['alert'] == False

    def test_integrated_update_ldr_alert(self):
        """Test LDR alert propagates to system level."""
        config = {
            'dt': 0.01,
            'max_force': 150.0,
            'ldr_threshold': 0.95,
            'transient_time': 0.1
        }
        system = StabilityMonitoringSystem(config)

        # Skip transient
        for _ in range(15):
            system.update(
                sigma=np.array([0.1, 0.05]),
                control_force=50.0,
                mass_matrix=np.eye(2)
            )

        # Create unstable LDR condition
        for i in range(50):
            growth = 0.1 + 0.02 * i
            result = system.update(
                sigma=np.array([growth, 0.5 * growth]),
                control_force=50.0,
                mass_matrix=np.eye(2)
            )

        assert result['ldr']['alert'] == True
        assert result['alert'] == True

    def test_integrated_update_saturation_alert(self):
        """Test saturation alert propagates to system level."""
        config = {'dt': 0.01, 'max_force': 100.0, 'transient_time': 0.1}
        system = StabilityMonitoringSystem(config)

        # Skip transient
        for _ in range(15):
            system.update(
                sigma=np.array([0.1, 0.05]),
                control_force=10.0,
                mass_matrix=np.eye(2)
            )

        # Create saturation condition
        for _ in range(100):
            result = system.update(
                sigma=np.array([0.1, 0.05]),
                control_force=99.0,  # Saturated
                mass_matrix=np.eye(2)
            )

        assert result['saturation']['alert'] == True
        assert result['alert'] == True

    def test_integrated_update_conditioning_alert(self):
        """Test conditioning alert propagates to system level."""
        config = {
            'dt': 0.01,
            'max_force': 150.0,
            'condition_threshold': 1e3
        }
        system = StabilityMonitoringSystem(config)

        # Create conditioning issue
        poorly_conditioned = np.array([[1.0, 0.9999], [0.9999, 1.0]])

        for _ in range(50):
            result = system.update(
                sigma=np.array([0.1, 0.05]),
                control_force=50.0,
                mass_matrix=poorly_conditioned
            )

        assert result['conditioning']['alert'] == True
        assert result['alert'] == True

    def test_violation_history_tracking(self):
        """Test violation history is tracked."""
        config = {'dt': 0.01, 'max_force': 100.0, 'transient_time': 0.1}
        system = StabilityMonitoringSystem(config)

        # Skip transient
        for _ in range(15):
            system.update(
                sigma=np.array([0.1, 0.05]),
                control_force=10.0,
                mass_matrix=np.eye(2)
            )

        initial_violations = len(system.violation_history)

        # Create violations
        for _ in range(50):
            system.update(
                sigma=np.array([0.1, 0.05]),
                control_force=99.0,  # Saturated
                mass_matrix=np.eye(2)
            )

        assert len(system.violation_history) > initial_violations

    def test_stability_report_generation(self):
        """Test stability report generation."""
        config = {'dt': 0.01, 'max_force': 150.0}
        system = StabilityMonitoringSystem(config)

        # Run some simulation
        for i in range(100):
            system.update(
                sigma=np.array([0.1, 0.05]),
                control_force=50.0 if i < 50 else 148.0,
                mass_matrix=np.eye(2)
            )

        report = system.get_stability_report()

        assert 'episode_count' in report
        assert 'total_violations' in report
        assert 'violation_rate' in report
        assert 'stability_score' in report
        assert 0.0 <= report['stability_score'] <= 1.0

    def test_episode_management(self):
        """Test episode counting and management."""
        system = StabilityMonitoringSystem()

        initial_count = system.episode_count.get()

        system.start_new_episode()
        assert system.episode_count.get() == initial_count + 1

        system.start_new_episode()
        assert system.episode_count.get() == initial_count + 2

    def test_system_reset(self):
        """Test full system reset."""
        system = StabilityMonitoringSystem()

        # Add data
        for i in range(50):
            system.update(
                sigma=np.array([0.1 + 0.01 * i, 0.05]),
                control_force=148.0,
                mass_matrix=np.eye(2)
            )

        # Reset
        system.reset()

        assert system.ldr_monitor.sample_count.get() == 0
        assert system.saturation_monitor.sample_count.get() == 0
        assert system.conditioning_monitor.sample_count.get() == 0
        assert system.episode_count.get() == 0
        assert len(system.violation_history) == 0

    def test_multiple_alert_types(self):
        """Test handling of multiple simultaneous alerts."""
        config = {
            'dt': 0.01,
            'max_force': 100.0,
            'ldr_threshold': 0.95,
            'condition_threshold': 1e3,
            'transient_time': 0.1
        }
        system = StabilityMonitoringSystem(config)

        # Skip transient
        for _ in range(15):
            system.update(
                sigma=np.array([0.1, 0.05]),
                control_force=10.0,
                mass_matrix=np.eye(2)
            )

        # Create multiple violation types simultaneously
        poorly_conditioned = np.array([[1.0, 0.9999], [0.9999, 1.0]])

        for i in range(50):
            growth = 0.1 + 0.02 * i
            result = system.update(
                sigma=np.array([growth, 0.5 * growth]),  # LDR violation
                control_force=99.0,  # Saturation
                mass_matrix=poorly_conditioned  # Conditioning issue
            )

        # All three alert types should be present
        assert result['ldr']['alert'] == True
        assert result['saturation']['alert'] == True
        assert result['conditioning']['alert'] == True
        assert result['alert'] == True

        # Violation history should have entries with multiple alert types
        recent_violation = system.violation_history[-1]
        assert recent_violation['ldr_alert'] == True
        assert recent_violation['saturation_alert'] == True
        assert recent_violation['conditioning_alert'] == True
