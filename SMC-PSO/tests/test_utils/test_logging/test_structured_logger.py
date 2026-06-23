"""
Unit tests for StructuredLogger

Tests logging functionality, context management, performance tracking,
and exception logging.

Author: DIP-SMC-PSO Project
Date: 2025-11-11
"""

import pytest
import json
import time
import logging
from pathlib import Path
from unittest.mock import Mock, patch

from src.utils.infrastructure.logging import StructuredLogger, LoggingConfig
from src.utils.infrastructure.logging.config import ConsoleHandlerConfig, FileHandlerConfig


@pytest.fixture
def test_config():
    """Create test logging configuration."""
    config = LoggingConfig()
    config.console.enabled = False  # Disable console for tests
    config.file.enabled = False  # Disable file for tests
    return config


@pytest.fixture
def logger(test_config):
    """Create test logger."""
    return StructuredLogger("Test.Component", config=test_config, auto_setup=False)


class TestStructuredLoggerInit:
    """Tests for logger initialization."""

    def test_init_basic(self, test_config):
        """Test basic initialization."""
        logger = StructuredLogger("Test.Component", config=test_config, auto_setup=False)
        assert logger.component_name == "Test.Component"
        assert logger.config == test_config
        assert logger._context == {}

    def test_init_with_auto_setup(self):
        """Test initialization with auto setup."""
        config = LoggingConfig()
        config.file.directory = "test_logs"
        logger = StructuredLogger("Test.Component", config=config, auto_setup=True)
        assert len(logger.logger.handlers) > 0

    def test_component_level_from_config(self):
        """Test that component level is set from configuration."""
        config = LoggingConfig()
        config.default_level = "INFO"
        config.component_levels = {"Test.Component": "DEBUG"}

        logger = StructuredLogger("Test.Component", config=config, auto_setup=False)
        assert logger.logger.level == logging.DEBUG


class TestLogEvent:
    """Tests for log_event method."""

    def test_log_event_basic(self, logger):
        """Test basic event logging."""
        # Mock handler
        mock_handler = Mock()
        logger.logger.addHandler(mock_handler)
        logger.logger.setLevel(logging.INFO)

        # Log event
        logger.log_event("test_event", level="INFO", value=42)

        # Verify handler called
        assert mock_handler.handle.called
        record = mock_handler.handle.call_args[0][0]
        assert record.event == "test_event"
        assert record.data == {"value": 42}

    def test_log_event_with_duration(self, logger):
        """Test event logging with duration."""
        mock_handler = Mock()
        logger.logger.addHandler(mock_handler)
        logger.logger.setLevel(logging.INFO)

        logger.log_event("test_event", level="INFO", duration_ms=1.23)

        record = mock_handler.handle.call_args[0][0]
        assert record.duration_ms == 1.23

    def test_log_event_with_context(self, logger):
        """Test event logging includes persistent context."""
        logger.set_context(run_id="test_run", iteration=100)

        mock_handler = Mock()
        logger.logger.addHandler(mock_handler)
        logger.logger.setLevel(logging.INFO)

        logger.log_event("test_event", level="INFO")

        record = mock_handler.handle.call_args[0][0]
        assert record.metadata["run_id"] == "test_run"
        assert record.metadata["iteration"] == 100

    def test_log_levels(self, logger):
        """Test different log levels."""
        mock_handler = Mock()
        logger.logger.addHandler(mock_handler)

        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in levels:
            logger.logger.setLevel(logging.DEBUG)
            logger.log_event(f"test_{level.lower()}", level=level)

        assert mock_handler.handle.call_count == len(levels)


class TestLogPerformance:
    """Tests for log_performance method."""

    def test_log_performance(self, logger):
        """Test performance logging."""
        mock_handler = Mock()
        logger.logger.addHandler(mock_handler)
        logger.logger.setLevel(logging.DEBUG)

        logger.log_performance(
            "control_computation",
            duration_ms=1.23,
            iterations=10
        )

        record = mock_handler.handle.call_args[0][0]
        assert record.event == "control_computation_performance"
        assert record.duration_ms == 1.23
        assert record.data["iterations"] == 10


class TestLogException:
    """Tests for log_exception method."""

    def test_log_exception_basic(self, logger):
        """Test basic exception logging."""
        mock_handler = Mock()
        logger.logger.addHandler(mock_handler)
        logger.logger.setLevel(logging.ERROR)

        try:
            raise ValueError("Test error")
        except ValueError as e:
            logger.log_exception(e)

        record = mock_handler.handle.call_args[0][0]
        assert record.event == "exception_occurred"
        assert record.exc_info is not None

    def test_log_exception_with_context(self, logger):
        """Test exception logging with context."""
        mock_handler = Mock()
        logger.logger.addHandler(mock_handler)
        logger.logger.setLevel(logging.ERROR)

        try:
            raise ValueError("Test error")
        except ValueError as e:
            logger.log_exception(e, context={"state": [0.1, 0.2]})

        record = mock_handler.handle.call_args[0][0]
        assert record.error_context == {"state": [0.1, 0.2]}


class TestContext:
    """Tests for context management."""

    def test_set_context(self, logger):
        """Test setting persistent context."""
        logger.set_context(run_id="test", trial=5)
        assert logger._context["run_id"] == "test"
        assert logger._context["trial"] == 5

    def test_clear_context(self, logger):
        """Test clearing context."""
        logger.set_context(run_id="test")
        logger.clear_context()
        assert logger._context == {}

    def test_temporary_context(self, logger):
        """Test temporary context manager."""
        logger.set_context(run_id="original")

        with logger.context(experiment="temp"):
            assert logger._context["experiment"] == "temp"
            assert logger._context["run_id"] == "original"

        # Context should be restored
        assert "experiment" not in logger._context
        assert logger._context["run_id"] == "original"

    def test_context_in_log_event(self, logger):
        """Test that context appears in logged events."""
        mock_handler = Mock()
        logger.logger.addHandler(mock_handler)
        logger.logger.setLevel(logging.INFO)

        with logger.context(experiment="test"):
            logger.log_event("test_event")

        record = mock_handler.handle.call_args[0][0]
        assert record.metadata["experiment"] == "test"


class TestTimedContext:
    """Tests for timed context manager."""

    def test_timed_context(self, logger):
        """Test timed operation logging."""
        mock_handler = Mock()
        logger.logger.addHandler(mock_handler)
        logger.logger.setLevel(logging.INFO)

        with logger.timed("test_operation"):
            time.sleep(0.001)

        record = mock_handler.handle.call_args[0][0]
        assert record.event == "test_operation"
        assert record.duration_ms > 0

    def test_timed_context_with_data(self, logger):
        """Test timed operation with additional data."""
        mock_handler = Mock()
        logger.logger.addHandler(mock_handler)
        logger.logger.setLevel(logging.INFO)

        with logger.timed("test_operation", iteration=100):
            pass

        record = mock_handler.handle.call_args[0][0]
        assert record.data["iteration"] == 100


class TestIsEnabled:
    """Tests for is_enabled method."""

    def test_is_enabled_true(self, logger):
        """Test is_enabled returns True when level is enabled."""
        logger.logger.setLevel(logging.DEBUG)
        assert logger.is_enabled("DEBUG")
        assert logger.is_enabled("INFO")

    def test_is_enabled_false(self, logger):
        """Test is_enabled returns False when level is disabled."""
        logger.logger.setLevel(logging.WARNING)
        assert not logger.is_enabled("DEBUG")
        assert not logger.is_enabled("INFO")


class TestPerformanceTracking:
    """Tests for performance statistics."""

    def test_performance_stats_tracking(self, logger):
        """Test that performance stats are tracked."""
        mock_handler = Mock()
        logger.logger.addHandler(mock_handler)
        logger.logger.setLevel(logging.INFO)

        # Log some events
        for i in range(10):
            logger.log_event("test_event", value=i)

        stats = logger.get_performance_stats()
        assert stats["log_count"] == 10
        assert stats["avg_latency_ms"] > 0
        assert stats["max_latency_ms"] > 0

    def test_performance_stats_empty(self, logger):
        """Test performance stats with no logs."""
        stats = logger.get_performance_stats()
        assert stats["log_count"] == 0
        assert stats["avg_latency_ms"] == 0
        assert stats["max_latency_ms"] == 0


class TestContextManager:
    """Tests for logger as context manager."""

    def test_context_manager(self, logger):
        """Test logger works as context manager."""
        mock_handler = Mock()
        logger.logger.addHandler(mock_handler)

        with logger as log:
            log.logger.setLevel(logging.INFO)
            log.log_event("test_event")

        # Verify flush was called on exit
        assert mock_handler.flush.called


class TestFlush:
    """Tests for flush functionality."""

    def test_flush(self, logger):
        """Test flush calls all handlers."""
        mock_handler1 = Mock()
        mock_handler2 = Mock()
        logger.logger.addHandler(mock_handler1)
        logger.logger.addHandler(mock_handler2)

        logger.flush()

        assert mock_handler1.flush.called
        assert mock_handler2.flush.called


# Integration tests

class TestLoggingIntegration:
    """Integration tests for logging system."""

    def test_end_to_end_logging(self, tmp_path):
        """Test end-to-end logging to file."""
        # Create config with file output
        config = LoggingConfig()
        config.console.enabled = False
        config.file.enabled = True
        config.file.directory = str(tmp_path)
        config.async_handler.enabled = False  # Synchronous for testing

        logger = StructuredLogger("Test.Component", config=config)

        # Log some events
        logger.log_event("test_event", value=42)
        logger.flush()

        # Verify log file exists
        log_files = list(tmp_path.glob("*.log"))
        assert len(log_files) > 0

        # Verify log content (JSON format)
        log_file = log_files[0]
        with open(log_file, 'r') as f:
            log_line = f.readline()
            log_entry = json.loads(log_line)

            assert log_entry["event"] == "test_event"
            assert log_entry["data"]["value"] == 42
            assert log_entry["component"] == "Test.Component"

    def test_multiple_components(self, tmp_path):
        """Test logging from multiple components."""
        config = LoggingConfig()
        config.console.enabled = False
        config.file.enabled = True
        config.file.directory = str(tmp_path)
        config.async_handler.enabled = False

        logger1 = StructuredLogger("Controller.ClassicalSMC", config=config)
        logger2 = StructuredLogger("Optimizer.PSO", config=config)

        logger1.log_event("event1")
        logger2.log_event("event2")

        logger1.flush()
        logger2.flush()

        # Verify separate log files
        log_files = list(tmp_path.glob("*.log"))
        assert len(log_files) >= 2  # At least controller and optimizer logs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
