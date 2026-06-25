"""Tests for the public import surface of src.utils.infrastructure.

Validates that the infrastructure package re-exports logging, memory, and
threading, and that each subpackage exposes its documented API.
"""


def test_infrastructure_public_surface():
    import src.utils.infrastructure as infra
    assert hasattr(infra, "logging")
    assert hasattr(infra, "memory")
    assert hasattr(infra, "threading")
    assert set(infra.__all__) == {"logging", "memory", "threading"}


def test_logging_public_surface():
    from src.utils.infrastructure.logging import (
        StructuredLogger,
        load_config,
        LoggingConfig,
        get_component_level,
        JSONFormatter,
        HumanReadableFormatter,
        MetricFormatter,
        DailyRotatingFileHandler,
        SizeRotatingFileHandler,
        AsyncHandler,
        CombinedRotatingFileHandler,
    )
    for symbol in (
        StructuredLogger, load_config, LoggingConfig, get_component_level,
        JSONFormatter, HumanReadableFormatter, MetricFormatter,
        DailyRotatingFileHandler, SizeRotatingFileHandler, AsyncHandler,
        CombinedRotatingFileHandler,
    ):
        assert symbol is not None


def test_memory_public_surface():
    from src.utils.infrastructure.memory import MemoryPool
    assert MemoryPool.__name__ == "MemoryPool"


def test_threading_public_surface():
    from src.utils.infrastructure.threading import (
        AtomicCounter,
        AtomicFlag,
        ThreadSafeDict,
    )
    assert AtomicCounter().get() == 0
    assert AtomicFlag().get() is False
    d = ThreadSafeDict()
    d["k"] = 1
    assert d.get("k") == 1
