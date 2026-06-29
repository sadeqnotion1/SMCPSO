"""M4 Slice 4 - safety package import + S2-3 reconciliation."""
import src.simulation.safety as safety
from src.simulation.core.interfaces import PerformanceMonitor as CorePerformanceMonitor

EXPECTED = [
    "apply_safety_guards", "guard_no_nan", "guard_energy", "guard_bounds",
    "SafetyViolationError", "StateConstraints", "ControlConstraints",
    "EnergyConstraints", "ConstraintChecker", "PerformanceMonitor",
    "SafetyMonitor", "SystemHealthMonitor", "SafetyRecovery",
    "EmergencyStop", "StateLimiter",
]

def test_all_exports_present():
    for name in EXPECTED:
        assert hasattr(safety, name), f"missing export: {name}"
    assert set(safety.__all__) == set(EXPECTED)

def test_s2_3_performance_monitor_is_core_abc():
    # S2-3: safety.PerformanceMonitor is a re-export of the core ABC, NOT a duplicate.
    assert safety.PerformanceMonitor is CorePerformanceMonitor

def test_concrete_monitor_subclasses_core_abc():
    from src.simulation.safety.monitors import SimulationPerformanceMonitor
    assert issubclass(SimulationPerformanceMonitor, CorePerformanceMonitor)
