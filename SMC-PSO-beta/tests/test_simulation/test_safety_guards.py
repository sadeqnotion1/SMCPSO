"""M4 Slice 4 - safety guards."""
import numpy as np
import pytest
from src.simulation.safety.guards import (
    apply_safety_guards, guard_no_nan, guard_energy, guard_bounds,
    SafetyViolationError, NaNGuard, EnergyGuard, BoundsGuard,
    SafetyGuardManager, create_default_guards,
)

def test_violation_error_is_runtimeerror():
    e = SafetyViolationError("m", "t", 3)
    assert isinstance(e, RuntimeError)
    assert e.violation_type == "t" and e.step_idx == 3

def test_guard_no_nan_ok_and_raise():
    guard_no_nan(np.array([1.0, 2.0, 3.0]), 0)
    with pytest.raises(SafetyViolationError) as ei:
        guard_no_nan(np.array([1.0, np.nan]), 7)
    assert "NaN detected in state at step <i>" in str(ei.value)

def test_guard_energy():
    guard_energy(np.array([1.0, 1.0]), None)
    guard_energy(np.array([1.0, 1.0]), {"max": 10.0})
    with pytest.raises(SafetyViolationError) as ei:
        guard_energy(np.array([3.0, 3.0]), {"max": 10.0})
    assert "Energy check failed: total_energy=<val> exceeds <max>" in str(ei.value)

def test_guard_bounds():
    guard_bounds(np.array([0.0]), None, 0.0)
    guard_bounds(np.array([0.5]), (0.0, 1.0), 0.1)
    with pytest.raises(SafetyViolationError) as ei:
        guard_bounds(np.array([2.0]), (0.0, 1.0), 0.2)
    assert "State bounds violated at t=<t>" in str(ei.value)

def test_nan_guard_class():
    g = NaNGuard()
    # NaNGuard.check returns a numpy bool (np.all(...)); assert truthiness, not identity.
    assert g.check(np.array([1.0, 2.0]), 0)
    assert not g.check(np.array([np.inf]), 0)
    assert "NaN" in g.get_violation_message()

def test_energy_guard_class():
    g = EnergyGuard(max_energy=10.0)
    assert g.check(np.array([1.0, 1.0]), 0) is True
    assert g.check(np.array([3.0, 3.0]), 0) is False
    assert "Energy violation" in g.get_violation_message()

def test_bounds_guard_class():
    g = BoundsGuard(np.array([0.0]), np.array([1.0]))
    assert g.check(np.array([0.5]), 0) is True
    assert g.check(np.array([2.0]), 0) is False

def test_manager_check_all_raises():
    m = SafetyGuardManager()
    m.add_guard(NaNGuard())
    assert m.check_all(np.array([1.0]), 0) is True
    m.add_guard(EnergyGuard(1.0))
    with pytest.raises(SafetyViolationError):
        m.check_all(np.array([5.0]), 1)
    m.clear_guards()
    assert m.guards == []

def test_apply_and_default_guards_no_config():
    class Cfg: pass
    apply_safety_guards(np.array([1.0, 2.0]), 0, Cfg())
    with pytest.raises(SafetyViolationError):
        apply_safety_guards(np.array([np.nan]), 0, Cfg())
    mgr = create_default_guards(Cfg())
    assert mgr.check_all(np.array([1.0, 2.0]), 0) is True
