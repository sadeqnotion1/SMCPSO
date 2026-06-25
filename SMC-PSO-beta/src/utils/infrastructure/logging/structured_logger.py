"""
Structured Logger

Main logging API for the DIP-SMC-PSO project.

Provides high-level structured logging with automatic context injection,
performance tracking, and exception logging.

Author: DIP-SMC-PSO Project
Date: 2025-11-11
"""

import time
import logging
from typing import Dict, Any, Optional
from contextlib import contextmanager
from pathlib import Path

from .config import load_config, get_component_level, LoggingConfig
from .formatters import JSONFormatter, HumanReadableFormatter
from .handlers import (
    CombinedRotatingFileHandler,
    AsyncHandler
)


class StructuredLogger:
    """
    Structured logger for DIP-SMC-PSO components.

    Provides:
    - Structured event logging with automatic context injection
    - Performance tracking
    - Exception logging with context
    - Context managers for temporary context
    - Non-blocking async I/O
    """

    def __init__(
        self,
        component_name: str,
        config: Optional[LoggingConfig] = None,
        auto_setup: bool = True
    ):
        """
        Initialize structured logger.

        Args:
            component_name: Component name (e.g., "Controller.ClassicalSMC")
            config: Logging configuration (loads default if None)
            auto_setup: Automatically setup handlers
        """
        self.component_name = component_name
        self.config = config or load_config()

        # Get Python logger
        self.logger = logging.getLogger(component_name)

        # Set level based on configuration
        level_str = get_component_level(self.config, component_name)
        self.logger.setLevel(getattr(logging, level_str))

        # Persistent context
        self._context: Dict[str, Any] = {}

        # Setup handlers if requested
        if auto_setup:
            self._setup_handlers()

        # Performance monitoring
        self._log_count = 0
        self._total_latency_ms = 0.0
        self._max_latency_ms = 0.0

    def _setup_handlers(self):
        """Setup log handlers based on configuration."""
        # Clear existing handlers
        self.logger.handlers.clear()

        # Console handler
        if self.config.console.enabled:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, self.config.console.level))

            if self.config.console.format == "json":
                formatter = JSONFormatter(pretty_print=False)
            else:
                formatter = HumanReadableFormatter(
                    colorize=self.config.console.colorize
                )

            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # File handler (with async wrapper if enabled)
        if self.config.file.enabled:
            # Create base file handler
            file_handler = CombinedRotatingFileHandler(
                base_directory=self.config.file.directory,
                component=self._extract_component_for_filename(),
                max_bytes=self.config.file.max_bytes,
                backup_count=self.config.file.backup_count,
                retention_days=self.config.file.retention_days,
                compress=self.config.file.compress
            )
            file_handler.setLevel(getattr(logging, self.config.file.level))

            # JSON formatter for file output
            formatter = JSONFormatter(pretty_print=False)
            file_handler.setFormatter(formatter)

            # Wrap with async handler if enabled
            if self.config.async_handler.enabled:
                async_handler = AsyncHandler(
                    base_handler=file_handler,
                    queue_size=self.config.async_handler.queue_size,
                    flush_interval_ms=self.config.async_handler.flush_interval_ms,
                    flush_on_levels=self.config.async_handler.flush_on_levels
                )
                self.logger.addHandler(async_handler)
            else:
                self.logger.addHandler(file_handler)

        # Prevent propagation to root logger
        self.logger.propagate = False

    def _extract_component_for_filename(self) -> str:
        """
        Extract component name for filename.

        e.g., "Controller.ClassicalSMC" -> "controller"
        """
        parts = self.component_name.split(".")
        if len(parts) > 0:
            return parts[0].lower()
        return "default"

    def log_event(
        self,
        event: str,
        level: str = "INFO",
        duration_ms: Optional[float] = None,
        **data: Any
    ):
        """
        Log a structured event.

        Args:
            event: Event name (snake_case)
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            duration_ms: Optional operation duration in milliseconds
            **data: Event-specific data as keyword arguments

        Example:
            logger.log_event(
                "control_computed",
                level="INFO",
                duration_ms=1.23,
                state_norm=0.025,
                control_signal=15.3
            )
        """
        start = time.perf_counter()

        # Get log level
        log_level = getattr(logging, level)

        # Create log record
        record = self.logger.makeRecord(
            name=self.component_name,
            level=log_level,
            fn="",
            lno=0,
            msg="",
            args=(),
            exc_info=None
        )

        # Add structured data
        record.event = event
        record.data = data

        if duration_ms is not None:
            record.duration_ms = duration_ms

        # Add persistent context
        record.metadata = self._context.copy()

        # Log
        self.logger.handle(record)

        # Track performance
        latency_ms = (time.perf_counter() - start) * 1000
        self._log_count += 1
        self._total_latency_ms += latency_ms
        self._max_latency_ms = max(self._max_latency_ms, latency_ms)

    def log_performance(
        self,
        operation: str,
        duration_ms: float,
        **metrics: Any
    ):
        """
        Log performance metrics.

        Args:
            operation: Operation name
            duration_ms: Operation duration in milliseconds
            **metrics: Additional performance metrics

        Example:
            logger.log_performance(
                "control_computation",
                duration_ms=1.23,
                iterations=10,
                convergence_rate=0.95
            )
        """
        self.log_event(
            event=f"{operation}_performance",
            level="DEBUG",
            duration_ms=duration_ms,
            **metrics
        )

    def log_exception(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        level: str = "ERROR"
    ):
        """
        Log an exception with context.

        Args:
            exception: Exception to log
            context: Additional error context
            level: Log level (ERROR or CRITICAL)

        Example:
            try:
                result = compute_control(state)
            except ValueError as e:
                logger.log_exception(
                    e,
                    context={"state": state.tolist()},
                    level="ERROR"
                )
                raise
        """
        # Get log level
        log_level = getattr(logging, level)

        # Create log record with exception info
        record = self.logger.makeRecord(
            name=self.component_name,
            level=log_level,
            fn="",
            lno=0,
            msg="",
            args=(),
            exc_info=(type(exception), exception, exception.__traceback__)
        )

        # Add event and context
        record.event = "exception_occurred"
        record.data = {}

        if context:
            record.error_context = context

        # Add persistent context
        record.metadata = self._context.copy()

        # Log
        self.logger.handle(record)

    def set_context(self, **context: Any):
        """
        Set persistent context for all subsequent logs.

        Args:
            **context: Context key-value pairs

        Example:
            logger.set_context(
                run_id="abc123",
                controller_type="classical_smc",
                gains=[10.0, 5.0, 8.0]
            )
        """
        self._context.update(context)

    def clear_context(self):
        """Clear persistent context."""
        self._context.clear()

    @contextmanager
    def context(self, **temp_context: Any):
        """
        Context manager for temporary context.

        Args:
            **temp_context: Temporary context key-value pairs

        Example:
            with logger.context(experiment="stability_test", trial=5):
                logger.log_event("test_started")
                # ... test execution ...
                logger.log_event("test_completed")
        """
        # Save current context
        old_context = self._context.copy()

        # Add temporary context
        self._context.update(temp_context)

        try:
            yield self
        finally:
            # Restore old context
            self._context = old_context

    @contextmanager
    def timed(self, event: str, level: str = "INFO", **data: Any):
        """
        Context manager for timing operations.

        Args:
            event: Event name
            level: Log level
            **data: Additional event data

        Example:
            with logger.timed("control_computation", iteration=100):
                u = controller.compute_control(state)
        """
        start = time.perf_counter()

        try:
            yield self
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            self.log_event(event, level=level, duration_ms=duration_ms, **data)

    def is_enabled(self, level: str = "DEBUG") -> bool:
        """
        Check if a log level is enabled.

        Useful for avoiding expensive operations if logging is disabled.

        Args:
            level: Log level to check

        Returns:
            bool: True if level is enabled

        Example:
            if logger.is_enabled("DEBUG"):
                expensive_data = compute_expensive_debug_info()
                logger.log_event("debug_info", level="DEBUG", data=expensive_data)
        """
        log_level = getattr(logging, level)
        return self.logger.isEnabledFor(log_level)

    def flush(self):
        """Force flush all handlers."""
        for handler in self.logger.handlers:
            handler.flush()

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for this logger.

        Returns:
            dict: Performance statistics

        Example:
            stats = logger.get_performance_stats()
            print(f"Avg latency: {stats['avg_latency_ms']:.3f}ms")
        """
        avg_latency_ms = (
            self._total_latency_ms / self._log_count
            if self._log_count > 0
            else 0.0
        )

        return {
            "log_count": self._log_count,
            "avg_latency_ms": avg_latency_ms,
            "max_latency_ms": self._max_latency_ms,
            "total_latency_ms": self._total_latency_ms
        }

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - flush on exit."""
        self.flush()
        return False  # Don't suppress exceptions


# Example usage
if __name__ == "__main__":
    # Create logger
    logger = StructuredLogger("Controller.ClassicalSMC")

    # Set persistent context
    logger.set_context(
        run_id="test_run_001",
        controller_type="classical_smc"
    )

    # Log events
    logger.log_event(
        "initialized",
        level="INFO",
        gains=[10.0, 5.0, 8.0, 3.0, 15.0, 2.0],
        boundary_layer=0.1
    )

    # Timed operation
    with logger.timed("control_computation", iteration=100):
        time.sleep(0.001)  # Simulate computation

    # Temporary context
    with logger.context(experiment="test", trial=1):
        logger.log_event("experiment_started")

    # Exception logging
    try:
        raise ValueError("Test error")
    except ValueError as e:
        logger.log_exception(e, context={"test": "data"})

    # Get performance stats
    stats = logger.get_performance_stats()
    print(f"Logger stats: {stats}")

    # Flush
    logger.flush()
