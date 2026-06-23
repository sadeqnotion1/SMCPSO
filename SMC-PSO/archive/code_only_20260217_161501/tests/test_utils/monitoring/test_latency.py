#======================================================================================\\
#===================== tests/test_utils/monitoring/test_latency.py ====================\\
#======================================================================================\\

"""
Comprehensive tests for real-time latency monitoring.

Tests cover:
- LatencyMonitor initialization and parameter validation
- start() and end() timing methods
- stats() median and p95 calculation
- missed_rate() deadline violation tracking
- enforce() weakly-hard (m,k) constraint checking
- reset() and get_recent_stats() utility methods
- Integration scenarios for real-time control loops
"""

import pytest
import time
import numpy as np
from src.utils.monitoring.realtime.latency import LatencyMonitor


# =====================================================================================
# Tests for LatencyMonitor Initialization
# =====================================================================================

class TestLatencyMonitorInit:
    """Test LatencyMonitor initialization."""

    def test_initialization_with_dt_and_margin(self):
        """Test initialization with explicit dt and margin."""
        monitor = LatencyMonitor(dt=0.01, margin=0.8)

        assert monitor.dt == 0.01
        assert monitor.margin == 0.8
        assert monitor.samples == []

    def test_initialization_default_margin(self):
        """Test initialization with default margin (0.9)."""
        monitor = LatencyMonitor(dt=0.02)

        assert monitor.dt == 0.02
        assert monitor.margin == 0.9
        assert monitor.samples == []

    def test_dt_converted_to_float(self):
        """Test that dt is converted to float."""
        monitor = LatencyMonitor(dt=10)  # Integer

        assert isinstance(monitor.dt, float)
        assert monitor.dt == 10.0

    def test_margin_converted_to_float(self):
        """Test that margin is converted to float."""
        monitor = LatencyMonitor(dt=0.01, margin=1)  # Integer

        assert isinstance(monitor.margin, float)
        assert monitor.margin == 1.0


# =====================================================================================
# Tests for start()
# =====================================================================================

class TestLatencyMonitorStart:
    """Test LatencyMonitor start() method."""

    def test_start_returns_timestamp(self):
        """Test that start() returns a valid timestamp."""
        monitor = LatencyMonitor(dt=0.01)

        timestamp = monitor.start()

        assert isinstance(timestamp, float)
        assert timestamp > 0

    def test_start_returns_current_time(self):
        """Test that start() returns recent timestamp."""
        monitor = LatencyMonitor(dt=0.01)

        before = time.perf_counter()
        timestamp = monitor.start()
        after = time.perf_counter()

        # Timestamp should be between before and after
        assert before <= timestamp <= after

    def test_multiple_start_calls_independent(self):
        """Test that multiple start() calls return different timestamps."""
        monitor = LatencyMonitor(dt=0.01)

        timestamp1 = monitor.start()
        time.sleep(0.001)  # Small delay
        timestamp2 = monitor.start()

        assert timestamp2 > timestamp1


# =====================================================================================
# Tests for end()
# =====================================================================================

class TestLatencyMonitorEnd:
    """Test LatencyMonitor end() method."""

    def test_end_no_deadline_miss(self):
        """Test end() with latency below deadline."""
        monitor = LatencyMonitor(dt=0.01, margin=0.9)

        start_time = monitor.start()
        # Negligible delay
        missed = monitor.end(start_time)

        assert missed is False

    def test_end_deadline_miss(self):
        """Test end() with latency exceeding deadline."""
        monitor = LatencyMonitor(dt=0.001, margin=0.9)  # 1ms deadline

        start_time = monitor.start()
        time.sleep(0.002)  # Sleep 2ms (exceeds 0.001 * 0.9 = 0.9ms)
        missed = monitor.end(start_time)

        assert missed is True

    def test_end_records_sample(self):
        """Test that end() records latency sample."""
        monitor = LatencyMonitor(dt=0.01)

        start_time = monitor.start()
        monitor.end(start_time)

        assert len(monitor.samples) == 1
        assert monitor.samples[0] >= 0

    def test_end_multiple_calls_record_all(self):
        """Test that multiple end() calls record all samples."""
        monitor = LatencyMonitor(dt=0.01)

        for _ in range(5):
            start_time = monitor.start()
            monitor.end(start_time)

        assert len(monitor.samples) == 5

    def test_end_boundary_at_margin(self):
        """Test deadline check at exact margin boundary."""
        monitor = LatencyMonitor(dt=1.0, margin=0.5)

        # Simulate latency exactly at margin (0.5s)
        # Note: Actual timing may vary slightly due to computation overhead
        start_time = time.perf_counter() - 0.49  # Slightly below margin
        missed = monitor.end(start_time)

        # Should NOT be missed (latency < dt * margin)
        assert missed is False

    def test_end_just_above_margin(self):
        """Test deadline check just above margin."""
        monitor = LatencyMonitor(dt=1.0, margin=0.5)

        # Simulate latency just above margin (0.51s)
        start_time = time.perf_counter() - 0.51
        missed = monitor.end(start_time)

        # Should be missed
        assert missed is True

    def test_end_zero_latency(self):
        """Test end() with zero latency (instant execution)."""
        monitor = LatencyMonitor(dt=0.01)

        # Same timestamp for start and end
        now = time.perf_counter()
        missed = monitor.end(now)

        assert missed is False
        assert len(monitor.samples) == 1

    def test_end_large_latency_multiple_periods(self):
        """Test end() with latency exceeding multiple dt periods."""
        monitor = LatencyMonitor(dt=0.001, margin=0.9)

        start_time = monitor.start()
        time.sleep(0.01)  # 10x the deadline
        missed = monitor.end(start_time)

        assert missed is True


# =====================================================================================
# Tests for stats()
# =====================================================================================

class TestLatencyMonitorStats:
    """Test LatencyMonitor stats() method."""

    def test_stats_empty_samples(self):
        """Test stats() with no samples returns (0, 0)."""
        monitor = LatencyMonitor(dt=0.01)

        median, p95 = monitor.stats()

        assert median == 0.0
        assert p95 == 0.0

    def test_stats_single_sample(self):
        """Test stats() with single sample."""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.005]

        median, p95 = monitor.stats()

        assert median == 0.005
        assert p95 == 0.005

    def test_stats_multiple_samples(self):
        """Test stats() with multiple samples."""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.001, 0.002, 0.003, 0.004, 0.005]

        median, p95 = monitor.stats()

        # Median of [1,2,3,4,5] is 3
        assert median == 0.003
        # p95 should be close to max
        assert p95 >= 0.004

    def test_stats_large_sample_set(self):
        """Test stats() with large sample set."""
        monitor = LatencyMonitor(dt=0.01)
        # 100 samples uniformly distributed
        monitor.samples = [i * 0.0001 for i in range(100)]

        median, p95 = monitor.stats()

        # Median should be around middle (0.0050)
        assert 0.004 <= median <= 0.006
        # p95 should be around 95th sample
        assert p95 >= 0.009

    def test_stats_extreme_values(self):
        """Test stats() with extreme outliers."""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.001] * 95 + [1.0] * 5  # 95% fast, 5% very slow

        median, p95 = monitor.stats()

        # Median should be 0.001 (majority)
        assert median == 0.001
        # p95 interpolates between 95th sample (0.001) and 96th sample (1.0)
        # With linear interpolation: ~0.05
        assert p95 >= 0.04  # Should be around 0.051


# =====================================================================================
# Tests for missed_rate()
# =====================================================================================

class TestLatencyMonitorMissedRate:
    """Test LatencyMonitor missed_rate() method."""

    def test_missed_rate_empty_samples(self):
        """Test missed_rate() with no samples returns 0.0."""
        monitor = LatencyMonitor(dt=0.01)

        rate = monitor.missed_rate()

        assert rate == 0.0

    def test_missed_rate_no_misses(self):
        """Test missed_rate() when all samples meet deadline."""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.001, 0.002, 0.003, 0.004, 0.005]

        rate = monitor.missed_rate()

        assert rate == 0.0

    def test_missed_rate_all_misses(self):
        """Test missed_rate() when all samples miss deadline."""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.02, 0.03, 0.04, 0.05]  # All > 0.01

        rate = monitor.missed_rate()

        assert rate == 1.0

    def test_missed_rate_partial_misses(self):
        """Test missed_rate() with partial misses."""
        monitor = LatencyMonitor(dt=0.01)
        # 2 misses out of 10 samples
        monitor.samples = [0.005] * 8 + [0.02, 0.03]

        rate = monitor.missed_rate()

        assert rate == 0.2  # 2/10

    def test_missed_rate_boundary_samples(self):
        """Test missed_rate() with samples exactly at dt."""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.01, 0.01, 0.01]  # Exactly at deadline

        rate = monitor.missed_rate()

        # Should NOT count as miss (> not >=)
        assert rate == 0.0


# =====================================================================================
# Tests for enforce()
# =====================================================================================

class TestLatencyMonitorEnforce:
    """Test LatencyMonitor enforce() weakly-hard constraint."""

    def test_enforce_empty_samples(self):
        """Test enforce() with no samples (constraint satisfied)."""
        monitor = LatencyMonitor(dt=0.01)

        result = monitor.enforce(m=2, k=10)

        assert result is True

    def test_enforce_k_zero(self):
        """Test enforce() with k <= 0 (trivially satisfied)."""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.02] * 100  # All misses

        result = monitor.enforce(m=0, k=0)

        assert result is True

    def test_enforce_not_enough_samples(self):
        """Test enforce() with fewer samples than k (constraint satisfied)."""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.005, 0.006]  # Only 2 samples

        result = monitor.enforce(m=1, k=10)

        # n=2 < k=10, assume satisfied
        assert result is True

    def test_enforce_no_misses_in_window(self):
        """Test enforce() with no deadline misses in window."""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.005] * 10  # All fast

        result = monitor.enforce(m=2, k=5)

        assert result is True

    def test_enforce_exactly_m_misses(self):
        """Test enforce() with exactly m misses (constraint satisfied)."""
        monitor = LatencyMonitor(dt=0.01)
        # Last 5 samples: 2 misses
        monitor.samples = [0.005] * 10 + [0.02, 0.005, 0.03, 0.005, 0.005]

        result = monitor.enforce(m=2, k=5)

        assert result is True

    def test_enforce_more_than_m_misses(self):
        """Test enforce() with more than m misses (constraint violated)."""
        monitor = LatencyMonitor(dt=0.01)
        # Last 5 samples: 3 misses (> m=2)
        monitor.samples = [0.005] * 10 + [0.02, 0.03, 0.04, 0.005, 0.005]

        result = monitor.enforce(m=2, k=5)

        assert result is False

    def test_enforce_sliding_window(self):
        """Test enforce() sliding window behavior."""
        monitor = LatencyMonitor(dt=0.01)

        # Add samples incrementally
        for i in range(20):
            if i % 5 == 0:
                monitor.samples.append(0.02)  # Miss every 5th sample
            else:
                monitor.samples.append(0.005)

        # Last 10 samples (indices 10-19) have 2 misses (at indices 10, 15)
        result = monitor.enforce(m=2, k=10)
        assert result is True

        # Add two more misses to exceed constraint
        monitor.samples.append(0.02)
        monitor.samples.append(0.02)

        # Last 10 samples now have 3 misses (indices 15, 20, 21)
        result = monitor.enforce(m=2, k=10)
        assert result is False

    def test_enforce_no_misses_allowed(self):
        """Test enforce() with m=0 (no misses allowed)."""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.005] * 10

        # No misses - satisfied
        result = monitor.enforce(m=0, k=5)
        assert result is True

        # Add one miss
        monitor.samples.append(0.02)

        # Now violated (last 5 samples have 1 miss > 0)
        result = monitor.enforce(m=0, k=5)
        assert result is False


# =====================================================================================
# Tests for reset()
# =====================================================================================

class TestLatencyMonitorReset:
    """Test LatencyMonitor reset() method."""

    def test_reset_clears_samples(self):
        """Test that reset() clears all samples."""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.001, 0.002, 0.003]

        monitor.reset()

        assert monitor.samples == []

    def test_reset_preserves_config(self):
        """Test that reset() preserves dt and margin."""
        monitor = LatencyMonitor(dt=0.05, margin=0.8)
        monitor.samples = [0.001] * 10

        monitor.reset()

        assert monitor.dt == 0.05
        assert monitor.margin == 0.8

    def test_stats_after_reset(self):
        """Test stats() after reset returns (0, 0)."""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.001] * 10

        monitor.reset()
        median, p95 = monitor.stats()

        assert median == 0.0
        assert p95 == 0.0


# =====================================================================================
# Tests for get_recent_stats()
# =====================================================================================

class TestLatencyMonitorRecentStats:
    """Test LatencyMonitor get_recent_stats() method."""

    def test_get_recent_stats_empty_samples(self):
        """Test get_recent_stats() with no samples."""
        monitor = LatencyMonitor(dt=0.01)

        median, p95 = monitor.get_recent_stats(n=10)

        assert median == 0.0
        assert p95 == 0.0

    def test_get_recent_stats_n_greater_than_len(self):
        """Test get_recent_stats() when n > len(samples)."""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.001, 0.002, 0.003]

        median, p95 = monitor.get_recent_stats(n=10)

        # Should use all 3 samples
        assert median == 0.002
        assert p95 >= 0.002

    def test_get_recent_stats_n_less_than_len(self):
        """Test get_recent_stats() when n < len(samples)."""
        monitor = LatencyMonitor(dt=0.01)
        # 10 samples: [0.001, 0.002, ..., 0.010]
        monitor.samples = [(i + 1) * 0.001 for i in range(10)]

        median, p95 = monitor.get_recent_stats(n=5)

        # Should use last 5 samples: [0.006, 0.007, 0.008, 0.009, 0.010]
        # Median is 0.008
        assert median == 0.008
        assert p95 >= 0.009

    def test_get_recent_stats_n_equals_len(self):
        """Test get_recent_stats() when n equals len(samples)."""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.001, 0.002, 0.003, 0.004, 0.005]

        median, p95 = monitor.get_recent_stats(n=5)

        # Should use all samples
        assert median == 0.003
        assert p95 >= 0.004

    def test_get_recent_stats_default_n(self):
        """Test get_recent_stats() with default n=100."""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.001] * 50

        median, p95 = monitor.get_recent_stats()  # Default n=100

        # Should use all 50 samples
        assert median == 0.001
        assert p95 == 0.001


# =====================================================================================
# Integration Tests
# =====================================================================================

class TestLatencyMonitorIntegration:
    """Test integration scenarios and workflows."""

    def test_complete_workflow(self):
        """Test complete latency monitoring workflow."""
        monitor = LatencyMonitor(dt=0.01, margin=0.9)

        # Simulate 10 control loop iterations
        for _ in range(10):
            start = monitor.start()
            time.sleep(0.001)  # Simulate work (< 0.01)
            monitor.end(start)

        # All should meet deadline
        assert monitor.missed_rate() == 0.0

        # Get statistics
        median, p95 = monitor.stats()
        assert median > 0.0
        assert p95 > 0.0

    def test_multiple_iterations_with_misses(self):
        """Test multiple iterations with some deadline misses."""
        monitor = LatencyMonitor(dt=0.005, margin=0.9)

        miss_count = 0
        for i in range(20):
            start = monitor.start()
            if i % 5 == 0:
                time.sleep(0.006)  # Intentional miss
            else:
                time.sleep(0.001)  # Fast
            missed = monitor.end(start)
            if missed:
                miss_count += 1

        # Should have ~4 misses (indices 0, 5, 10, 15)
        assert miss_count >= 3
        assert monitor.missed_rate() > 0.0

    def test_weakly_hard_constraint_validation(self):
        """Test weakly-hard constraint in realistic scenario."""
        monitor = LatencyMonitor(dt=0.01, margin=0.9)

        # Add fast samples
        for _ in range(50):
            monitor.samples.append(0.005)

        # Constraint should be satisfied
        assert monitor.enforce(m=5, k=10) is True

        # Add 6 misses in last 10 samples
        for _ in range(6):
            monitor.samples.append(0.02)

        # Constraint violated (6 > 5)
        assert monitor.enforce(m=5, k=10) is False

    def test_reset_and_reuse(self):
        """Test resetting monitor and reusing."""
        monitor = LatencyMonitor(dt=0.01)

        # First run
        for _ in range(10):
            start = monitor.start()
            monitor.end(start)

        assert len(monitor.samples) == 10

        # Reset
        monitor.reset()
        assert len(monitor.samples) == 0

        # Second run
        for _ in range(5):
            start = monitor.start()
            monitor.end(start)

        assert len(monitor.samples) == 5

    def test_recent_stats_sliding_window(self):
        """Test recent stats for sliding window analysis."""
        monitor = LatencyMonitor(dt=0.01)

        # Add 100 fast samples
        monitor.samples = [0.001] * 100

        # Recent stats should show fast execution
        median1, p95_1 = monitor.get_recent_stats(n=10)
        assert median1 == 0.001

        # Add 10 slow samples
        monitor.samples.extend([0.008] * 10)

        # Recent stats should now show slower execution
        median2, p95_2 = monitor.get_recent_stats(n=10)
        assert median2 == 0.008
        assert median2 > median1
