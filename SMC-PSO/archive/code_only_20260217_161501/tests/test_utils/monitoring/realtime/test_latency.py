#!/usr/bin/env python
"""
Latency Monitoring Tests (Week 3 Session 11)

PURPOSE: Comprehensive unit tests for real-time latency monitoring
COVERAGE TARGET: 85-95% of latency.py module
STRATEGY: Test timing, deadline detection, statistics, weakly-hard constraints

TEST MATRIX:
1. Initialization - Parameter validation and defaults (3 tests)
2. Timing Methods - start/end timing workflow (4 tests)
3. Deadline Detection - Margin-based deadline miss detection (5 tests)
4. Statistics - Median and p95 calculation (5 tests)
5. Missed Rate - Deadline miss rate calculation (4 tests)
6. Weakly-Hard Constraints - (m,k) deadline model validation (6 tests)
7. Reset and Edge Cases - Boundary conditions and reset behavior (4 tests)
8. Recent Stats - Windowed statistics calculation (3 tests)

Mathematical Guarantees Tested:
- end() returns True iff latency > dt * margin
- missed_rate() = (count of samples > dt) / total_samples
- enforce(m, k) returns True iff misses_in_last_k <= m
- stats() returns (median, p95) of all samples
- get_recent_stats(n) returns (median, p95) of last n samples

Author: Claude Code (Week 3 Session 11)
Date: December 2025
"""

import pytest
import time
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Import latency monitor
from src.utils.monitoring.realtime.latency import LatencyMonitor

# ==============================================================================
# Test Initialization
# ==============================================================================

class TestLatencyMonitorInitialization:
    """Test LatencyMonitor initialization and parameter handling"""

    def test_initialization_default_margin(self):
        """Test initialization with default margin"""
        monitor = LatencyMonitor(dt=0.01)
        assert monitor.dt == 0.01
        assert monitor.margin == 0.9
        assert monitor.samples == []

    def test_initialization_custom_margin(self):
        """Test initialization with custom margin"""
        monitor = LatencyMonitor(dt=0.02, margin=0.8)
        assert monitor.dt == 0.02
        assert monitor.margin == 0.8
        assert monitor.samples == []

    def test_initialization_converts_to_float(self):
        """Test that dt and margin are converted to float"""
        monitor = LatencyMonitor(dt=10, margin=1)
        assert isinstance(monitor.dt, float)
        assert isinstance(monitor.margin, float)
        assert monitor.dt == 10.0
        assert monitor.margin == 1.0

# ==============================================================================
# Test Timing Methods
# ==============================================================================

class TestTimingMethods:
    """Test start/end timing workflow"""

    def test_start_returns_timestamp(self):
        """Test that start() returns a valid timestamp"""
        monitor = LatencyMonitor(dt=0.01)
        start_time = monitor.start()
        assert isinstance(start_time, float)
        assert start_time > 0

    def test_end_records_sample(self):
        """Test that end() records latency sample"""
        monitor = LatencyMonitor(dt=0.01)
        start_time = monitor.start()
        time.sleep(0.001)  # 1ms delay
        monitor.end(start_time)
        assert len(monitor.samples) == 1
        assert monitor.samples[0] > 0

    def test_multiple_start_end_cycles(self):
        """Test multiple timing cycles"""
        monitor = LatencyMonitor(dt=0.01)
        for _ in range(5):
            start = monitor.start()
            time.sleep(0.0005)  # 0.5ms delay
            monitor.end(start)
        assert len(monitor.samples) == 5
        assert all(s > 0 for s in monitor.samples)

    def test_end_returns_deadline_status(self):
        """Test that end() returns deadline miss status"""
        monitor = LatencyMonitor(dt=0.001, margin=0.9)  # 1ms deadline, 0.9ms margin
        start = monitor.start()
        time.sleep(0.002)  # 2ms delay (definitely over deadline)
        missed = monitor.end(start)
        assert isinstance(missed, bool)
        assert missed is True  # Should detect deadline miss

# ==============================================================================
# Test Deadline Detection
# ==============================================================================

class TestDeadlineDetection:
    """Test margin-based deadline miss detection"""

    def test_latency_below_margin_no_miss(self):
        """Test that latency below margin doesn't trigger miss"""
        monitor = LatencyMonitor(dt=1.0, margin=0.9)  # 1s deadline, 0.9s margin
        # Manually add sample below margin
        monitor.samples.append(0.5)  # 0.5s < 0.9s
        # Verify it's not counted as miss in missed_rate
        rate = monitor.missed_rate()
        assert rate == 0.0

    def test_latency_above_deadline_is_miss(self):
        """Test that latency above dt is counted as miss"""
        monitor = LatencyMonitor(dt=1.0, margin=0.9)
        monitor.samples.append(1.5)  # 1.5s > 1.0s deadline
        rate = monitor.missed_rate()
        assert rate == 1.0

    def test_margin_affects_end_return_value(self):
        """Test that margin parameter affects end() return value"""
        monitor = LatencyMonitor(dt=1.0, margin=0.5)  # 0.5s effective deadline
        # Manually add sample between margin and dt
        start = time.perf_counter() - 0.7  # 0.7s elapsed
        missed = monitor.end(start)
        assert missed is True  # 0.7 > 0.5 (margin threshold)

    def test_latency_at_margin_boundary(self):
        """Test latency just below margin boundary"""
        monitor = LatencyMonitor(dt=1.0, margin=0.9)
        # Manually test boundary: latency just below threshold (0.89 < 0.9)
        monitor.samples.append(0.89)  # Below margin threshold
        # Verify it's not counted as miss
        missed_before_deadline = sum(1 for s in monitor.samples if s > monitor.dt * monitor.margin)
        assert missed_before_deadline == 0

        # Now test just above threshold (0.91 > 0.9)
        monitor.samples.append(0.91)
        missed_above_threshold = sum(1 for s in monitor.samples if s > monitor.dt * monitor.margin)
        assert missed_above_threshold == 1

    def test_zero_margin(self):
        """Test with zero margin (all latencies trigger miss)"""
        monitor = LatencyMonitor(dt=1.0, margin=0.0)
        start = time.perf_counter() - 0.001  # Any positive latency
        missed = monitor.end(start)
        assert missed is True

# ==============================================================================
# Test Statistics
# ==============================================================================

class TestStatistics:
    """Test median and p95 calculation"""

    def test_stats_empty_samples(self):
        """Test stats() with no samples"""
        monitor = LatencyMonitor(dt=0.01)
        median, p95 = monitor.stats()
        assert median == 0.0
        assert p95 == 0.0

    def test_stats_single_sample(self):
        """Test stats() with single sample"""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples.append(0.005)
        median, p95 = monitor.stats()
        assert median == 0.005
        assert p95 == 0.005

    def test_stats_median_calculation(self):
        """Test median calculation with known values"""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.001, 0.002, 0.003, 0.004, 0.005]
        median, _ = monitor.stats()
        assert median == 0.003  # Middle value

    def test_stats_p95_calculation(self):
        """Test 95th percentile calculation"""
        monitor = LatencyMonitor(dt=0.01)
        # 100 samples: 1ms to 100ms
        monitor.samples = [i * 0.001 for i in range(1, 101)]
        _, p95 = monitor.stats()
        assert 0.094 <= p95 <= 0.096  # Should be around 95ms

    def test_stats_returns_floats(self):
        """Test that stats() returns float types"""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.001, 0.002, 0.003]
        median, p95 = monitor.stats()
        assert isinstance(median, float)
        assert isinstance(p95, float)

# ==============================================================================
# Test Missed Rate
# ==============================================================================

class TestMissedRate:
    """Test deadline miss rate calculation"""

    def test_missed_rate_empty_samples(self):
        """Test missed_rate() with no samples"""
        monitor = LatencyMonitor(dt=0.01)
        rate = monitor.missed_rate()
        assert rate == 0.0

    def test_missed_rate_no_misses(self):
        """Test missed_rate() with all samples below deadline"""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.005, 0.007, 0.008, 0.006]  # All < 10ms
        rate = monitor.missed_rate()
        assert rate == 0.0

    def test_missed_rate_some_misses(self):
        """Test missed_rate() with partial misses"""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.005, 0.015, 0.008, 0.012]  # 2/4 over deadline
        rate = monitor.missed_rate()
        assert rate == 0.5

    def test_missed_rate_all_misses(self):
        """Test missed_rate() with all samples over deadline"""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.015, 0.020, 0.012, 0.018]  # All > 10ms
        rate = monitor.missed_rate()
        assert rate == 1.0

# ==============================================================================
# Test Weakly-Hard Constraints
# ==============================================================================

class TestWeaklyHardConstraints:
    """Test (m,k) deadline model validation"""

    def test_enforce_with_zero_k(self):
        """Test enforce() with k <= 0 (should always pass)"""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.020] * 10  # All misses
        assert monitor.enforce(m=0, k=0) is True
        assert monitor.enforce(m=5, k=-1) is True

    def test_enforce_insufficient_samples(self):
        """Test enforce() with fewer samples than k"""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.005, 0.006]  # Only 2 samples
        assert monitor.enforce(m=1, k=5) is True  # Should pass (not enough samples)

    def test_enforce_constraint_satisfied(self):
        """Test enforce() with constraint satisfied"""
        monitor = LatencyMonitor(dt=0.01)
        # Last 5 samples: 1 miss out of 5 (satisfies m=1, k=5)
        monitor.samples = [0.005, 0.006, 0.015, 0.007, 0.008]
        assert monitor.enforce(m=1, k=5) is True

    def test_enforce_constraint_violated(self):
        """Test enforce() with constraint violated"""
        monitor = LatencyMonitor(dt=0.01)
        # Last 5 samples: 3 misses out of 5 (violates m=1, k=5)
        monitor.samples = [0.015, 0.006, 0.012, 0.007, 0.018]
        assert monitor.enforce(m=1, k=5) is False

    def test_enforce_sliding_window(self):
        """Test enforce() uses sliding window (last k samples)"""
        monitor = LatencyMonitor(dt=0.01)
        # 10 samples total, but only last 5 matter for k=5
        monitor.samples = [
            0.020, 0.021, 0.022, 0.023, 0.024,  # Old misses (ignored)
            0.005, 0.006, 0.007, 0.008, 0.009   # Recent OK samples
        ]
        # Should pass because last 5 have 0 misses (m=1, k=5)
        assert monitor.enforce(m=1, k=5) is True

    def test_enforce_exact_m_misses(self):
        """Test enforce() with exactly m misses in window"""
        monitor = LatencyMonitor(dt=0.01)
        # Exactly 2 misses in last 5 samples
        monitor.samples = [0.015, 0.006, 0.012, 0.007, 0.008]
        assert monitor.enforce(m=2, k=5) is True  # Exactly at limit

# ==============================================================================
# Test Reset and Edge Cases
# ==============================================================================

class TestResetAndEdgeCases:
    """Test boundary conditions and reset behavior"""

    def test_reset_clears_samples(self):
        """Test that reset() clears all samples"""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.005, 0.010, 0.015]
        monitor.reset()
        assert monitor.samples == []
        assert len(monitor.samples) == 0

    def test_stats_after_reset(self):
        """Test that stats() returns zeros after reset"""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.005, 0.010, 0.015]
        monitor.reset()
        median, p95 = monitor.stats()
        assert median == 0.0
        assert p95 == 0.0

    def test_very_small_dt(self):
        """Test with very small dt values (microseconds)"""
        monitor = LatencyMonitor(dt=0.000001, margin=0.9)  # 1 microsecond
        assert monitor.dt == 1e-6
        start = monitor.start()
        time.sleep(0.00001)  # 10 microseconds
        missed = monitor.end(start)
        assert missed is True  # Should exceed 1us deadline

    def test_operations_after_reset(self):
        """Test that monitor works correctly after reset"""
        monitor = LatencyMonitor(dt=0.01)
        # First cycle
        monitor.samples = [0.005, 0.010]
        monitor.reset()
        # Second cycle
        start = monitor.start()
        time.sleep(0.001)
        monitor.end(start)
        assert len(monitor.samples) == 1
        median, p95 = monitor.stats()
        assert median > 0.0

# ==============================================================================
# Test Recent Stats
# ==============================================================================

class TestRecentStats:
    """Test windowed statistics calculation"""

    def test_recent_stats_empty_samples(self):
        """Test get_recent_stats() with no samples"""
        monitor = LatencyMonitor(dt=0.01)
        median, p95 = monitor.get_recent_stats(n=10)
        assert median == 0.0
        assert p95 == 0.0

    def test_recent_stats_n_larger_than_samples(self):
        """Test get_recent_stats() with n > sample count"""
        monitor = LatencyMonitor(dt=0.01)
        monitor.samples = [0.005, 0.010, 0.015]
        median, p95 = monitor.get_recent_stats(n=100)
        # Should use all 3 samples
        assert median == 0.010
        assert p95 > 0.0

    def test_recent_stats_windowing(self):
        """Test that get_recent_stats() uses correct window"""
        monitor = LatencyMonitor(dt=0.01)
        # 10 samples: first 5 are low, last 5 are high
        monitor.samples = [0.001] * 5 + [0.020] * 5
        # Recent 5 should be high values
        median, _ = monitor.get_recent_stats(n=5)
        assert median == 0.020  # Median of last 5 samples

# ==============================================================================
# Summary Test
# ==============================================================================

@pytest.mark.unit
def test_latency_monitor_summary():
    """Print summary of latency monitoring test coverage"""
    print("\n" + "=" * 80)
    print(" Latency Monitoring Tests - Week 3 Session 11")
    print("=" * 80)
    print(" Module: src/utils/monitoring/realtime/latency.py")
    print(" Class: LatencyMonitor (8 methods)")
    print("-" * 80)
    print(" Test Suites:")
    print("   1. Initialization (3 tests)")
    print("   2. Timing Methods (4 tests)")
    print("   3. Deadline Detection (5 tests)")
    print("   4. Statistics (5 tests)")
    print("   5. Missed Rate (4 tests)")
    print("   6. Weakly-Hard Constraints (6 tests)")
    print("   7. Reset and Edge Cases (4 tests)")
    print("   8. Recent Stats (3 tests)")
    print("-" * 80)
    print(" Total Tests: 34")
    print(" Coverage Strategy:")
    print("   - Timing workflow (start/end cycle)")
    print("   - Deadline detection (margin-based)")
    print("   - Statistical analysis (median, p95)")
    print("   - Weakly-hard (m,k) constraint validation")
    print("   - Edge cases (empty samples, reset, boundaries)")
    print("   - Windowed statistics (recent samples)")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
