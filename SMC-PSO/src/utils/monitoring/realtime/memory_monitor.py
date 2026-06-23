#======================================================================================\\\
#==================== src/utils/monitoring/memory_monitor.py ==========================\\\
#======================================================================================\\\

"""
Production memory monitoring for controllers (Issue #15).

Provides real-time memory leak detection and alerting for production
deployments of SMC controllers. Monitors memory growth trends and triggers
alerts when thresholds are exceeded.
"""

import psutil
import logging
import time
from typing import Callable, Optional, List, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class MemoryAlert:
    """Memory alert data structure."""
    timestamp: float
    rss_mb: float
    growth_mb: float
    threshold_mb: float
    message: str
    severity: str  # 'warning', 'critical'


class ProductionMemoryMonitor:
    """Real-time memory monitoring for production deployments.

    Usage Example:
        >>> monitor = ProductionMemoryMonitor(threshold_mb=500.0)
        >>> # In control loop:
        >>> alert = monitor.check_memory()
        >>> if alert:
        >>>     print(f"Memory alert: {alert.message}")
    """

    def __init__(
        self,
        threshold_mb: float = 500.0,
        alert_callback: Optional[Callable[[MemoryAlert], None]] = None,
        trend_window: int = 100
    ):
        """Initialize production memory monitor.

        Args:
            threshold_mb: Memory growth threshold in MB to trigger alerts
            alert_callback: Optional callback function for alerts
            trend_window: Number of samples for trend analysis
        """
        self.threshold_mb = threshold_mb
        self.alert_callback = alert_callback or self._default_alert
        self.process = psutil.Process()
        self.baseline_mb = self.process.memory_info().rss / 1024 / 1024
        self.logger = logging.getLogger(__name__)

        # Trend tracking
        self.trend_window = trend_window
        self.memory_history: List[Tuple[float, float]] = []  # (timestamp, rss_mb)
        self.last_gc_time = time.time()
        self.gc_interval = 3600.0  # Suggest GC every hour

    def check_memory(self) -> Optional[MemoryAlert]:
        """Check current memory usage against threshold.

        Returns:
            MemoryAlert if threshold exceeded, None otherwise
        """
        current_mb = self.process.memory_info().rss / 1024 / 1024
        growth_mb = current_mb - self.baseline_mb
        timestamp = time.time()

        # Update history
        self.memory_history.append((timestamp, current_mb))
        if len(self.memory_history) > self.trend_window:
            self.memory_history.pop(0)

        # Check threshold
        if growth_mb > self.threshold_mb:
            severity = 'critical' if growth_mb > self.threshold_mb * 1.5 else 'warning'
            alert = MemoryAlert(
                timestamp=timestamp,
                rss_mb=current_mb,
                growth_mb=growth_mb,
                threshold_mb=self.threshold_mb,
                message=f"Memory threshold exceeded: {growth_mb:.1f} MB growth (threshold: {self.threshold_mb:.1f} MB)",
                severity=severity
            )
            self.alert_callback(alert)
            return alert

        # Suggest GC if interval passed
        if time.time() - self.last_gc_time > self.gc_interval:
            self.logger.info(f"Memory monitor suggests garbage collection (current: {current_mb:.1f} MB)")
            self.last_gc_time = time.time()

        return None

    def analyze_trend(self) -> dict:
        """Analyze memory growth trend.

        Returns:
            Dictionary with trend statistics
        """
        if len(self.memory_history) < 10:
            return {'insufficient_data': True}

        times = np.array([t for t, _ in self.memory_history])
        memory = np.array([m for _, m in self.memory_history])

        # Linear regression for trend
        times_norm = times - times[0]
        if times_norm[-1] == 0:
            growth_rate = 0.0
        else:
            coeffs = np.polyfit(times_norm, memory, 1)
            growth_rate = coeffs[0]  # MB per second

        return {
            'current_mb': memory[-1],
            'baseline_mb': self.baseline_mb,
            'growth_mb': memory[-1] - self.baseline_mb,
            'growth_rate_mb_per_hour': growth_rate * 3600.0,
            'samples': len(self.memory_history),
            'time_span_hours': (times[-1] - times[0]) / 3600.0,
            'monotonic_growth': all(memory[i] <= memory[i+1] for i in range(len(memory)-1))
        }

    def reset_baseline(self) -> None:
        """Reset baseline to current memory usage."""
        self.baseline_mb = self.process.memory_info().rss / 1024 / 1024
        self.memory_history.clear()
        self.logger.info(f"Memory baseline reset to {self.baseline_mb:.1f} MB")

    def get_memory_report(self) -> str:
        """Generate human-readable memory report.

        Returns:
            Formatted memory report string
        """
        trend = self.analyze_trend()

        if trend.get('insufficient_data'):
            return "Insufficient data for memory report"

        report = [
            "=== Memory Monitor Report ===",
            f"Current RSS: {trend['current_mb']:.1f} MB",
            f"Baseline: {trend['baseline_mb']:.1f} MB",
            f"Growth: {trend['growth_mb']:.1f} MB",
            f"Growth Rate: {trend['growth_rate_mb_per_hour']:.2f} MB/hour",
            f"Time Span: {trend['time_span_hours']:.2f} hours",
            f"Samples: {trend['samples']}",
            f"Monotonic Growth: {'Yes' if trend['monotonic_growth'] else 'No'}",
            f"Threshold: {self.threshold_mb:.1f} MB",
            "=============================="
        ]

        return "\n".join(report)

    def _default_alert(self, alert: MemoryAlert) -> None:
        """Default alert handler."""
        if alert.severity == 'critical':
            self.logger.error(alert.message)
        else:
            self.logger.warning(alert.message)


class ControllerMemoryTracker:
    """Specialized memory tracker for SMC controller instantiations.

    Tracks memory usage per controller type and provides diagnostics
    for memory leak detection during repeated instantiation.

    Usage:
        >>> tracker = ControllerMemoryTracker()
        >>> for i in range(1000):
        >>>     controller = ClassicalSMC(...)
        >>>     tracker.track_instantiation("classical", controller)
        >>>     controller.cleanup()
        >>> report = tracker.get_report()
    """

    def __init__(self):
        """Initialize controller memory tracker."""
        self.process = psutil.Process()
        self.controller_counts: dict = {}
        self.initial_memory_mb = self.process.memory_info().rss / 1024 / 1024
        self.snapshots: List[Tuple[str, int, float]] = []  # (controller_type, count, memory_mb)
        self.logger = logging.getLogger(__name__)

    def track_instantiation(self, controller_type: str, controller: object) -> None:
        """Track a controller instantiation.

        Args:
            controller_type: Type of controller ('classical', 'adaptive', etc.)
            controller: Controller instance
        """
        # Update count
        self.controller_counts[controller_type] = self.controller_counts.get(controller_type, 0) + 1

        # Take snapshot every 100 instantiations
        if self.controller_counts[controller_type] % 100 == 0:
            current_mb = self.process.memory_info().rss / 1024 / 1024
            self.snapshots.append((controller_type, self.controller_counts[controller_type], current_mb))

    def get_report(self) -> dict:
        """Generate memory tracking report.

        Returns:
            Dictionary with memory statistics per controller type
        """
        current_mb = self.process.memory_info().rss / 1024 / 1024
        total_growth = current_mb - self.initial_memory_mb

        report = {
            'initial_memory_mb': self.initial_memory_mb,
            'current_memory_mb': current_mb,
            'total_growth_mb': total_growth,
            'total_instantiations': sum(self.controller_counts.values()),
            'by_controller': {}
        }

        for controller_type, count in self.controller_counts.items():
            # Find snapshots for this controller type
            type_snapshots = [(c, m) for t, c, m in self.snapshots if t == controller_type]

            if type_snapshots:
                memory_per_1000 = (type_snapshots[-1][1] - self.initial_memory_mb) / (count / 1000.0)
            else:
                memory_per_1000 = 0.0

            report['by_controller'][controller_type] = {
                'count': count,
                'memory_per_1000_instantiations_mb': memory_per_1000,
                'snapshots': len(type_snapshots)
            }

        return report

    def check_leak_threshold(self, threshold_mb_per_1000: float = 1.0) -> dict:
        """Check if any controller type exceeds leak threshold.

        Args:
            threshold_mb_per_1000: Maximum acceptable memory growth per 1000 instantiations

        Returns:
            Dictionary with leak detection results
        """
        report = self.get_report()
        leaks = {}

        for controller_type, stats in report['by_controller'].items():
            if stats['memory_per_1000_instantiations_mb'] > threshold_mb_per_1000:
                leaks[controller_type] = {
                    'memory_per_1000_mb': stats['memory_per_1000_instantiations_mb'],
                    'threshold_mb': threshold_mb_per_1000,
                    'exceeded_by_mb': stats['memory_per_1000_instantiations_mb'] - threshold_mb_per_1000
                }

        return {
            'has_leaks': len(leaks) > 0,
            'leaks': leaks,
            'total_instantiations': report['total_instantiations'],
            'total_growth_mb': report['total_growth_mb']
        }


# Example usage for integration tests
def monitor_controller_loop(
    controller_class,
    config: dict,
    iterations: int = 10000,
    cleanup_interval: int = 100
) -> dict:
    """Monitor memory usage during a controller control loop.

    Args:
        controller_class: Controller class to instantiate
        config: Configuration dictionary for controller
        iterations: Number of control iterations
        cleanup_interval: Call cleanup() every N iterations

    Returns:
        Dictionary with monitoring results
    """
    import gc
    import numpy as np

    monitor = ProductionMemoryMonitor(threshold_mb=100.0)
    alerts: List[MemoryAlert] = []

    def collect_alert(alert: MemoryAlert) -> None:
        alerts.append(alert)

    monitor.alert_callback = collect_alert

    controller = controller_class(**config)

    for i in range(iterations):
        # Simulate control loop
        state = np.random.randn(6)
        state_vars = controller.initialize_state()
        history = controller.initialize_history()
        _ = controller.compute_control(state, state_vars, history)

        # Periodic cleanup
        if i % cleanup_interval == 0 and i > 0:
            controller.cleanup()
            gc.collect()

        # Check memory (alert logged internally by monitor)
        _ = monitor.check_memory()

    # Final cleanup
    controller.cleanup()

    trend = monitor.analyze_trend()

    return {
        'iterations': iterations,
        'alerts': len(alerts),
        'final_memory_mb': trend['current_mb'],
        'growth_mb': trend['growth_mb'],
        'growth_rate_mb_per_hour': trend['growth_rate_mb_per_hour'],
        'passed': trend['growth_mb'] < 50.0  # 50MB tolerance
    }


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    monitor = ProductionMemoryMonitor(threshold_mb=100.0)

    for i in range(1000):
        alert = monitor.check_memory()
        if alert:
            print(f"Alert at iteration {i}: {alert.message}")

    print(monitor.get_memory_report())
