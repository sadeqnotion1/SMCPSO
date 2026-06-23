#======================================================================================\\\
#=================== src/optimization/algorithms/memory_efficient_pso.py ============\\\
#======================================================================================\\\

"""
Memory-efficient PSO optimizer with production-grade memory management.

This module provides a memory-optimized version of the PSO optimizer specifically
designed to handle large-scale optimization runs without memory leaks or excessive
memory consumption. Implements bounded collections, automatic cleanup, and
real-time memory monitoring for production deployment.

Key Features:
- Bounded history collections prevent unbounded memory growth
- Automatic memory cleanup every N iterations
- Real-time memory usage monitoring and alerting
- Graceful degradation under memory pressure
- Comprehensive memory usage statistics
"""

import gc
import logging
import psutil
import threading
import time
import weakref
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union
from collections import deque
import numpy as np

from .pso_optimizer import PSOTuner


@dataclass
class MemoryConfig:
    """Memory management configuration for PSO optimization."""

    # History limits
    max_cost_history: int = 100
    max_position_history: int = 50
    max_metrics_history: int = 200

    # Cleanup settings
    cleanup_frequency: int = 25  # iterations
    force_gc_frequency: int = 100  # iterations
    emergency_cleanup_threshold_mb: float = 1000.0  # MB

    # Memory monitoring
    memory_check_frequency: int = 10  # iterations
    memory_warning_threshold_mb: float = 500.0  # MB
    memory_critical_threshold_mb: float = 800.0  # MB

    # Performance settings
    enable_memory_monitoring: bool = True
    enable_automatic_cleanup: bool = True
    enable_history_compression: bool = True

    # Recovery settings
    emergency_recovery_enabled: bool = True
    memory_pressure_adaptation: bool = True


class MemoryTracker:
    """Real-time memory usage tracker for PSO optimization."""

    def __init__(self, pid: Optional[int] = None):
        self.process = psutil.Process(pid)
        self.initial_memory = self.get_current_memory_mb()
        self.peak_memory = self.initial_memory
        self.memory_samples = deque(maxlen=100)
        self.last_gc_memory = self.initial_memory

        # Thread-safe logging
        self.logger = logging.getLogger(f"{__name__}.MemoryTracker")

    def get_current_memory_mb(self) -> float:
        """Get current memory usage in MB."""
        try:
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB

            # Update peak memory
            if memory_mb > self.peak_memory:
                self.peak_memory = memory_mb

            # Store sample
            self.memory_samples.append((time.time(), memory_mb))

            return memory_mb
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0

    def get_memory_growth_mb(self) -> float:
        """Get memory growth since initialization."""
        return self.get_current_memory_mb() - self.initial_memory

    def get_memory_growth_since_gc_mb(self) -> float:
        """Get memory growth since last garbage collection."""
        return self.get_current_memory_mb() - self.last_gc_memory

    def record_gc_event(self) -> None:
        """Record garbage collection event."""
        self.last_gc_memory = self.get_current_memory_mb()

    def get_memory_trend(self, window_seconds: float = 60.0) -> Dict[str, float]:
        """Analyze memory usage trend over time window."""
        current_time = time.time()
        cutoff_time = current_time - window_seconds

        # Filter samples within window
        recent_samples = [
            (t, mem) for t, mem in self.memory_samples
            if t >= cutoff_time
        ]

        if len(recent_samples) < 2:
            return {'trend_mb_per_sec': 0.0, 'volatility': 0.0}

        # Calculate trend (linear regression slope)
        times = np.array([t - recent_samples[0][0] for t, _ in recent_samples])
        memories = np.array([mem for _, mem in recent_samples])

        if len(times) > 1:
            trend = np.polyfit(times, memories, 1)[0]  # MB per second
            volatility = np.std(memories)
        else:
            trend = 0.0
            volatility = 0.0

        return {
            'trend_mb_per_sec': trend,
            'volatility': volatility,
            'samples_count': len(recent_samples)
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive memory usage summary."""
        current_mb = self.get_current_memory_mb()
        trend = self.get_memory_trend()

        return {
            'current_mb': current_mb,
            'initial_mb': self.initial_memory,
            'peak_mb': self.peak_memory,
            'growth_mb': self.get_memory_growth_mb(),
            'growth_since_gc_mb': self.get_memory_growth_since_gc_mb(),
            'trend_mb_per_sec': trend['trend_mb_per_sec'],
            'memory_volatility': trend['volatility'],
            'total_samples': len(self.memory_samples)
        }


class BoundedHistory:
    """Bounded history collection with automatic size management."""

    def __init__(self, maxlen: int, compression_enabled: bool = False):
        self.maxlen = maxlen
        self.compression_enabled = compression_enabled
        self._data = deque(maxlen=maxlen)
        self._compressed_data = []
        self._compression_ratio = 2  # Compress by factor of 2

    def append(self, item: Any) -> None:
        """Add item to history with automatic compression."""
        self._data.append(item)

        # Trigger compression if enabled and queue is full
        if (self.compression_enabled and
            len(self._data) == self.maxlen and
            len(self._data) % self._compression_ratio == 0):
            self._compress_oldest()

    def _compress_oldest(self) -> None:
        """Compress oldest data to free up space."""
        # Simple compression: subsample oldest data
        if len(self._data) >= self._compression_ratio:
            # Move every Nth item to compressed storage
            for i in range(0, self._compression_ratio):
                if self._data:
                    self._compressed_data.append(self._data.popleft())

            # Limit compressed data size
            max_compressed = self.maxlen // 2
            if len(self._compressed_data) > max_compressed:
                self._compressed_data = self._compressed_data[-max_compressed:]

    def get_recent(self, n: Optional[int] = None) -> List[Any]:
        """Get recent items from history."""
        if n is None:
            return list(self._data)
        return list(self._data)[-n:]

    def get_all(self) -> List[Any]:
        """Get all items including compressed data."""
        return list(self._compressed_data) + list(self._data)

    def clear(self) -> None:
        """Clear all history data."""
        self._data.clear()
        self._compressed_data.clear()

    def __len__(self) -> int:
        return len(self._data) + len(self._compressed_data)

    def get_memory_estimate_mb(self) -> float:
        """Estimate memory usage of stored data."""
        # Rough estimate based on object count and average size
        total_objects = len(self._data) + len(self._compressed_data)
        # Assume average object size ~1KB (conservative estimate)
        return total_objects * 1024 / 1024 / 1024  # Convert to MB


class MemoryEfficientPSOTuner(PSOTuner):
    """
    Memory-optimized PSO tuner for production use.

    This class extends the base PSOTuner with comprehensive memory management
    capabilities to prevent memory leaks and handle large-scale optimization
    runs efficiently.

    Features:
    - Bounded history collections
    - Automatic memory cleanup
    - Real-time memory monitoring
    - Emergency recovery mechanisms
    - Memory pressure adaptation
    """

    def __init__(self,
                 controller_factory: Callable[[np.ndarray], Any],
                 config: Union[str, Dict, Any],
                 memory_config: Optional[MemoryConfig] = None,
                 **kwargs):
        """
        Initialize memory-efficient PSO tuner.

        Parameters
        ----------
        controller_factory : Callable
            Factory function for creating controllers
        config : str, Dict, or ConfigSchema
            PSO configuration
        memory_config : MemoryConfig, optional
            Memory management configuration
        **kwargs
            Additional arguments passed to base PSOTuner
        """

        # Initialize base PSO tuner
        super().__init__(controller_factory, config, **kwargs)

        # Memory management setup
        self.memory_config = memory_config or MemoryConfig()
        self.memory_tracker = None
        if self.memory_config.enable_memory_monitoring:
            self.memory_tracker = MemoryTracker()

        # Bounded history collections
        self.cost_history = BoundedHistory(
            self.memory_config.max_cost_history,
            self.memory_config.enable_history_compression
        )
        self.position_history = BoundedHistory(
            self.memory_config.max_position_history,
            self.memory_config.enable_history_compression
        )

        # Iteration tracking
        self.iteration_count = 0
        self.last_cleanup_iteration = 0
        self.last_gc_iteration = 0

        # Memory alerts
        self.memory_alerts = deque(maxlen=50)

        # Weak reference tracking for cleanup
        self._controller_refs = weakref.WeakSet()

        # Thread safety for memory operations
        self._memory_lock = threading.RLock()

        self.logger = logging.getLogger(f"{__name__}.MemoryEfficientPSOTuner")

        if self.memory_tracker:
            self.logger.info(f"Memory-efficient PSO initialized. "
                           f"Initial memory: {self.memory_tracker.initial_memory:.1f} MB")

    def optimise(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Run PSO optimization with memory management.

        Overrides base optimize method to add memory monitoring
        and cleanup throughout the optimization process.
        """

        if self.memory_tracker:
            start_memory = self.memory_tracker.get_current_memory_mb()
            self.logger.info(f"Starting PSO optimization. "
                           f"Memory: {start_memory:.1f} MB")

        try:
            # Call parent optimize method
            result = super().optimise(*args, **kwargs)

            # Add memory statistics to result
            if self.memory_tracker:
                memory_summary = self.memory_tracker.get_summary()
                result['memory_statistics'] = memory_summary

                self.logger.info(f"PSO optimization completed. "
                               f"Memory growth: {memory_summary['growth_mb']:.1f} MB, "
                               f"Peak: {memory_summary['peak_mb']:.1f} MB")

            return result

        except Exception:
            # Emergency cleanup on failure
            if self.memory_config.emergency_recovery_enabled:
                self._emergency_memory_cleanup()
            raise

        finally:
            # Final cleanup
            self._perform_memory_cleanup(force=True)

    def _fitness(self, particles: np.ndarray) -> np.ndarray:
        """
        Memory-aware fitness evaluation with monitoring and cleanup.

        Overrides base fitness method to add memory management
        and periodic cleanup during fitness evaluation.
        """

        self.iteration_count += 1

        # Memory monitoring
        memory_before = None
        if self.memory_tracker and self.iteration_count % self.memory_config.memory_check_frequency == 0:
            memory_before = self.memory_tracker.get_current_memory_mb()

        try:
            # Standard fitness evaluation
            fitness_values = super()._fitness(particles)

            # Store bounded history
            with self._memory_lock:
                if hasattr(self, '_last_best_cost'):
                    self.cost_history.append(self._last_best_cost)
                if hasattr(self, '_last_best_position'):
                    self.position_history.append(self._last_best_position)

            # Periodic memory management
            self._periodic_memory_management()

            return fitness_values

        except Exception as e:
            self.logger.warning(f"Fitness evaluation failed at iteration {self.iteration_count}: {e}")

            # Emergency memory cleanup on failure
            if self.memory_config.emergency_recovery_enabled:
                self._emergency_memory_cleanup()

            raise

        finally:
            # Post-fitness memory monitoring
            if memory_before is not None and self.memory_tracker:
                memory_after = self.memory_tracker.get_current_memory_mb()
                memory_growth = memory_after - memory_before

                if memory_growth > self.memory_config.emergency_cleanup_threshold_mb / 10:
                    self.logger.warning(f"High memory growth in fitness evaluation: "
                                      f"{memory_growth:.1f} MB")
                    self._check_memory_pressure()

    def _periodic_memory_management(self) -> None:
        """Perform periodic memory management tasks."""

        # Scheduled cleanup
        if (self.memory_config.enable_automatic_cleanup and
            self.iteration_count - self.last_cleanup_iteration >= self.memory_config.cleanup_frequency):
            self._perform_memory_cleanup()
            self.last_cleanup_iteration = self.iteration_count

        # Forced garbage collection
        if (self.iteration_count - self.last_gc_iteration >= self.memory_config.force_gc_frequency):
            self._force_garbage_collection()
            self.last_gc_iteration = self.iteration_count

        # Memory pressure check
        if (self.memory_tracker and
            self.iteration_count % self.memory_config.memory_check_frequency == 0):
            self._check_memory_pressure()

    def _perform_memory_cleanup(self, force: bool = False) -> None:
        """Perform comprehensive memory cleanup."""

        with self._memory_lock:
            cleanup_stats = {'objects_cleaned': 0, 'memory_freed_mb': 0.0}

            memory_before = 0.0
            if self.memory_tracker:
                memory_before = self.memory_tracker.get_current_memory_mb()

            # Clean bounded histories
            if force:
                # Aggressive cleanup - clear more history
                self.cost_history._data = deque(
                    list(self.cost_history._data)[-self.memory_config.max_cost_history // 2:],
                    maxlen=self.cost_history.maxlen
                )
                self.position_history._data = deque(
                    list(self.position_history._data)[-self.memory_config.max_position_history // 2:],
                    maxlen=self.position_history.maxlen
                )

            # Clear controller references
            self._controller_refs.clear()

            # Clear memory alerts if too many
            if len(self.memory_alerts) > 30:
                while len(self.memory_alerts) > 20:
                    self.memory_alerts.popleft()
                cleanup_stats['objects_cleaned'] += 10

            # Force garbage collection
            collected = gc.collect()
            cleanup_stats['objects_cleaned'] += collected

            # Calculate memory freed
            if self.memory_tracker:
                memory_after = self.memory_tracker.get_current_memory_mb()
                cleanup_stats['memory_freed_mb'] = max(0, memory_before - memory_after)
                self.memory_tracker.record_gc_event()

            if force or cleanup_stats['objects_cleaned'] > 0:
                self.logger.debug(f"Memory cleanup completed: "
                                f"{cleanup_stats['objects_cleaned']} objects, "
                                f"{cleanup_stats['memory_freed_mb']:.1f} MB freed")

    def _force_garbage_collection(self) -> None:
        """Force garbage collection and update tracking."""
        collected = gc.collect()

        if self.memory_tracker:
            self.memory_tracker.record_gc_event()

        if collected > 0:
            self.logger.debug(f"Garbage collection: {collected} objects collected")

    def _check_memory_pressure(self) -> None:
        """Check for memory pressure and take appropriate action."""

        if not self.memory_tracker:
            return

        current_memory = self.memory_tracker.get_current_memory_mb()
        memory_growth = self.memory_tracker.get_memory_growth_mb()

        # Warning threshold
        if current_memory > self.memory_config.memory_warning_threshold_mb:
            alert = {
                'type': 'memory_warning',
                'memory_mb': current_memory,
                'growth_mb': memory_growth,
                'iteration': self.iteration_count,
                'timestamp': time.time()
            }
            self.memory_alerts.append(alert)

            self.logger.warning(f"Memory warning: {current_memory:.1f} MB used, "
                              f"{memory_growth:.1f} MB growth")

        # Critical threshold
        if current_memory > self.memory_config.memory_critical_threshold_mb:
            alert = {
                'type': 'memory_critical',
                'memory_mb': current_memory,
                'growth_mb': memory_growth,
                'iteration': self.iteration_count,
                'timestamp': time.time()
            }
            self.memory_alerts.append(alert)

            self.logger.error(f"Memory critical: {current_memory:.1f} MB used, "
                            f"{memory_growth:.1f} MB growth")

            # Trigger emergency cleanup
            if self.memory_config.emergency_recovery_enabled:
                self._emergency_memory_cleanup()

        # Emergency threshold
        if current_memory > self.memory_config.emergency_cleanup_threshold_mb:
            self.logger.critical(f"Memory emergency: {current_memory:.1f} MB used - "
                               f"triggering emergency cleanup")
            self._emergency_memory_cleanup()

    def _emergency_memory_cleanup(self) -> None:
        """Emergency memory cleanup for critical situations."""

        self.logger.warning("Performing emergency memory cleanup")

        with self._memory_lock:
            # Aggressive history cleanup
            self.cost_history.clear()
            self.position_history.clear()

            # Clear all weak references
            self._controller_refs.clear()

            # Clear alerts except most recent
            while len(self.memory_alerts) > 5:
                self.memory_alerts.popleft()

            # Multiple garbage collection passes
            for i in range(3):
                collected = gc.collect()
                if collected == 0:
                    break
                self.logger.debug(f"Emergency GC pass {i+1}: {collected} objects collected")

            if self.memory_tracker:
                self.memory_tracker.record_gc_event()
                memory_after = self.memory_tracker.get_current_memory_mb()
                self.logger.info(f"Emergency cleanup completed. "
                               f"Memory: {memory_after:.1f} MB")

    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory usage statistics."""

        stats = {
            'iteration_count': self.iteration_count,
            'last_cleanup_iteration': self.last_cleanup_iteration,
            'cost_history_size': len(self.cost_history),
            'position_history_size': len(self.position_history),
            'memory_alerts_count': len(self.memory_alerts),
            'controller_refs_count': len(self._controller_refs)
        }

        if self.memory_tracker:
            stats.update(self.memory_tracker.get_summary())

        # History memory estimates
        stats['cost_history_memory_mb'] = self.cost_history.get_memory_estimate_mb()
        stats['position_history_memory_mb'] = self.position_history.get_memory_estimate_mb()

        return stats

    def get_memory_alerts(self, alert_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get memory alerts, optionally filtered by type."""

        alerts = list(self.memory_alerts)

        if alert_type:
            alerts = [alert for alert in alerts if alert.get('type') == alert_type]

        return alerts

    def reset_memory_tracking(self) -> None:
        """Reset memory tracking statistics."""

        with self._memory_lock:
            if self.memory_tracker:
                self.memory_tracker = MemoryTracker()

            self.memory_alerts.clear()
            self.iteration_count = 0
            self.last_cleanup_iteration = 0
            self.last_gc_iteration = 0

            self.logger.info("Memory tracking reset")

    def __del__(self):
        """Cleanup on deletion."""
        try:
            self._perform_memory_cleanup(force=True)
        except Exception:
            pass  # Ignore cleanup errors during destruction