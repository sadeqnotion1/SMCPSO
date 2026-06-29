"""M4 Slice 4 - safety recovery."""
import numpy as np
from src.simulation.safety.recovery import (
    SafetyRecovery, EmergencyStop, StateLimiter,
)

def test_emergency_stop_zeros_control():
    st, ctrl, ok = EmergencyStop().recover(np.array([1.0, 2.0]), 9.0, {})
    assert ok and ctrl == 0.0
    assert np.allclose(st, np.array([1.0, 2.0]))

def test_state_limiter_clips():
    sl = StateLimiter(np.array([0.0]), np.array([1.0]))
    st, ctrl, ok = sl.recover(np.array([5.0]), 4.0, {})
    assert ok and np.allclose(st, np.array([1.0])) and ctrl == 2.0

def test_recovery_dispatch():
    rec = SafetyRecovery()
    st, ctrl, ok = rec.apply_recovery(np.array([1.0]), 3.0, {"type": "unknown"})
    assert ok and ctrl == 0.0  # default EmergencyStop
    rec.register_strategy("bounds_violation", StateLimiter(np.array([0.0]), np.array([1.0])))
    st, ctrl, ok = rec.apply_recovery(np.array([9.0]), 4.0, {"type": "bounds_violation"})
    assert np.allclose(st, np.array([1.0])) and ctrl == 2.0
