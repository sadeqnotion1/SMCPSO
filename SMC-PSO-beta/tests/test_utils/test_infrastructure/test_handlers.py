"""Tests for src.utils.infrastructure.logging.handlers.

Covers size-rotating writes, combined handler write + size rotation, daily
handler dated filename, and async handler flush-through to the base handler.
"""

import logging
import time

import pytest

from src.utils.infrastructure.logging.handlers import (
    DailyRotatingFileHandler,
    SizeRotatingFileHandler,
    AsyncHandler,
    CombinedRotatingFileHandler,
)
from src.utils.infrastructure.logging.formatters import JSONFormatter


def _emit(handler, msg="hello", level=logging.INFO):
    record = logging.LogRecord(
        name="Test", level=level, pathname="", lineno=0, msg=msg, args=(), exc_info=None
    )
    record.event = "unit_test"
    record.data = {"msg": msg}
    handler.emit(record)
    return record


def test_size_rotating_handler_writes_file(tmp_path):
    handler = SizeRotatingFileHandler(
        base_directory=str(tmp_path), component="sizer", max_bytes=10_000,
        backup_count=2, compress=False,
    )
    handler.setFormatter(JSONFormatter())
    _emit(handler)
    handler.flush()
    handler.close()
    assert (tmp_path / "sizer.log").exists()


def test_daily_rotating_handler_creates_dated_file(tmp_path):
    handler = DailyRotatingFileHandler(
        base_directory=str(tmp_path), component="daily", backup_count=3, compress=False,
    )
    handler.setFormatter(JSONFormatter())
    _emit(handler)
    handler.flush()
    handler.close()
    matches = list(tmp_path.glob("daily_*.log"))
    assert len(matches) == 1


def test_combined_handler_writes_and_rotates_on_size(tmp_path):
    handler = CombinedRotatingFileHandler(
        base_directory=str(tmp_path), component="combo", max_bytes=200,
        backup_count=5, retention_days=30, compress=False,
    )
    handler.setFormatter(JSONFormatter())
    # Emit enough records to exceed the tiny max_bytes and force size rotation.
    for i in range(50):
        _emit(handler, msg=f"message-number-{i}")
    handler.flush()
    assert handler.rotation_count >= 1
    handler.close()
    produced = list(tmp_path.glob("combo_*.log*"))
    assert len(produced) >= 2


def test_async_handler_flushes_to_base(tmp_path):
    base = SizeRotatingFileHandler(
        base_directory=str(tmp_path), component="async", max_bytes=100_000,
        backup_count=1, compress=False,
    )
    base.setFormatter(JSONFormatter())
    handler = AsyncHandler(base_handler=base, queue_size=100, flush_interval_ms=10)
    # INFO is queued; explicit flush drains it to the base handler.
    _emit(handler, msg="queued-info", level=logging.INFO)
    handler.flush()
    # ERROR triggers an immediate flush path inside emit().
    _emit(handler, msg="urgent-error", level=logging.ERROR)
    handler.flush()
    handler.close()
    log_path = tmp_path / "async.log"
    assert log_path.exists()
    contents = log_path.read_text()
    assert "queued-info" in contents
    assert "urgent-error" in contents
