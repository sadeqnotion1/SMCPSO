"""Tests for src.utils.infrastructure.logging.structured_logger.StructuredLogger.

Uses a handler-free config (console/file/async disabled) so tests do not touch
the filesystem. Covers event logging + perf stats, context managers, timing,
and exception logging.
"""

import pytest

from src.utils.infrastructure.logging.structured_logger import StructuredLogger
from src.utils.infrastructure.logging.config import (
    LoggingConfig,
    ConsoleHandlerConfig,
    FileHandlerConfig,
    AsyncHandlerConfig,
)


def _silent_config():
    return LoggingConfig(
        default_level="DEBUG",
        component_levels={},
        console=ConsoleHandlerConfig(enabled=False),
        file=FileHandlerConfig(enabled=False),
        async_handler=AsyncHandlerConfig(enabled=False),
    )


def _logger():
    return StructuredLogger("Controller.ClassicalSMC", config=_silent_config())


def test_log_event_updates_performance_stats():
    logger = _logger()
    logger.log_event("initialized", gains=[1.0, 2.0, 3.0])
    logger.log_event("control_computed", level="INFO", duration_ms=1.5, state_norm=0.02)
    stats = logger.get_performance_stats()
    assert stats["log_count"] == 2
    assert stats["max_latency_ms"] >= 0.0
    assert stats["total_latency_ms"] >= 0.0


def test_set_and_clear_context():
    logger = _logger()
    logger.set_context(run_id="abc123")
    assert logger._context["run_id"] == "abc123"
    logger.clear_context()
    assert logger._context == {}


def test_context_manager_restores_previous_context():
    logger = _logger()
    logger.set_context(run_id="base")
    with logger.context(experiment="stability", trial=5):
        assert logger._context["experiment"] == "stability"
        assert logger._context["trial"] == 5
        assert logger._context["run_id"] == "base"
    # Temporary keys are removed; base context is restored.
    assert "experiment" not in logger._context
    assert logger._context == {"run_id": "base"}


def test_timed_records_duration_event():
    logger = _logger()
    with logger.timed("control_computation", iteration=100):
        pass
    stats = logger.get_performance_stats()
    assert stats["log_count"] == 1


def test_log_exception_runs_without_error():
    logger = _logger()
    try:
        raise ValueError("test error")
    except ValueError as exc:
        logger.log_exception(exc, context={"state": [0.0, 1.0]})
    # No handlers attached, so nothing is written; the call must not raise.
    assert True


def test_is_enabled_reflects_level():
    logger = _logger()
    assert logger.is_enabled("DEBUG") is True


def test_context_manager_protocol_flushes():
    with _logger() as logger:
        logger.log_event("inside_with")
    assert logger.get_performance_stats()["log_count"] == 1
