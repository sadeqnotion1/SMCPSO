#======================================================================================
# tests/test_utils/test_monitoring/test_memory_monitor.py
#======================================================================================
"""Unit tests for ProductionMemoryMonitor.

NOTE [P1 MON-DEP-1]: memory_monitor imports `psutil` at module top, and
realtime/__init__.py imports memory_monitor UNCONDITIONALLY. Therefore
`import src.utils.monitoring` requires psutil to be installed. These tests
are skipped when psutil is unavailable; add psutil to the beta requirements
so production/CI always has it (see AUDIT card)."""
import pytest

psutil = pytest.importorskip("psutil")

from src.utils.monitoring.realtime.memory_monitor import (
    ProductionMemoryMonitor, MemoryAlert,
)


def test_no_alert_under_threshold():
    mon = ProductionMemoryMonitor(threshold_mb=10_000_000.0)
    assert mon.check_memory() is None


def test_trend_insufficient_then_report():
    mon = ProductionMemoryMonitor(threshold_mb=10_000_000.0)
    assert mon.analyze_trend().get('insufficient_data') is True
    for _ in range(15):
        mon.check_memory()
    trend = mon.analyze_trend()
    assert 'growth_rate_mb_per_hour' in trend
    assert isinstance(mon.get_memory_report(), str)


def test_alert_callback_fires():
    captured = []
    mon = ProductionMemoryMonitor(threshold_mb=-1.0, alert_callback=captured.append)
    alert = mon.check_memory()
    assert isinstance(alert, MemoryAlert)
    assert captured and captured[0] is alert
