#======================================================================================
# tests/test_utils/test_monitoring/test_package_import.py
#======================================================================================
"""Package-level import + public surface smoke test.

[P1 MON-DEP-1] The umbrella import `import src.utils.monitoring` pulls in
realtime -> memory_monitor -> psutil unconditionally, so this test requires
psutil. visualization/examples remain optional (guarded by try/except)."""
import pytest

pytest.importorskip("psutil")


def test_monitoring_public_surface():
    import src.utils.monitoring as mon
    assert hasattr(mon, "StabilityMonitoringSystem")
    assert hasattr(mon, "DiagnosticChecklist")
    assert hasattr(mon, "InstabilityType")
    assert hasattr(mon, "realtime")
    assert hasattr(mon, "metrics")


def test_submodule_surfaces_import_without_psutil_dependency():
    # These submodules must import without requiring psutil.
    from src.utils.monitoring.metrics import data_model
    from src.utils.monitoring.realtime import latency, stability, diagnostics
    assert data_model.MetricsSnapshot is not None
    assert latency.LatencyMonitor is not None
    assert stability.StabilityMonitoringSystem is not None
    assert diagnostics.DiagnosticChecklist is not None
