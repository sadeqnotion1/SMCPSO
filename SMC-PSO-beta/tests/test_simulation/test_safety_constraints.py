"""M4 Slice 4 - safety constraints."""
import numpy as np
from src.simulation.safety.constraints import (
    StateConstraints, ControlConstraints, EnergyConstraints, ConstraintChecker,
)

def test_state_constraints():
    sc = StateConstraints(lower_bounds=np.array([0.0]), upper_bounds=np.array([1.0]))
    ok, msg = sc.check_all(np.array([0.5]))
    assert ok and msg == ""
    ok, msg = sc.check_all(np.array([-1.0]))
    assert not ok and "lower" in msg.lower()
    ok, msg = sc.check_all(np.array([2.0]))
    assert not ok and "upper" in msg.lower()

def test_control_constraints_amplitude_and_rate():
    cc = ControlConstraints(min_control=-5.0, max_control=5.0, rate_limit=100.0)
    ok, _ = cc.check_all(1.0, dt=0.01)
    assert ok
    ok, msg = cc.check_all(-10.0, dt=0.01)
    assert not ok and "below minimum" in msg
    ok, msg = cc.check_all(10.0, dt=0.01)
    assert not ok and "above maximum" in msg
    cc2 = ControlConstraints(rate_limit=10.0)
    cc2.check_all(0.0, dt=0.01)
    ok, msg = cc2.check_all(5.0, dt=0.01)  # rate = 500 > 10
    assert not ok and "rate limit" in msg

def test_energy_constraints():
    ec = EnergyConstraints(max_kinetic=10.0, max_potential=10.0, max_total=15.0)
    ok, _ = ec.check_all(5.0, 5.0)
    assert ok
    ok, msg = ec.check_all(20.0, 1.0)
    assert not ok and "Kinetic" in msg
    ok, msg = ec.check_all(8.0, 8.0)  # total 16 > 15
    assert not ok and "Total" in msg

def test_constraint_checker_passthrough():
    chk = ConstraintChecker()
    assert chk.check_state(np.array([1.0])) == (True, "")
    assert chk.check_control(1.0) == (True, "")
    assert chk.check_energy(1.0, 1.0) == (True, "")
    chk2 = ConstraintChecker(
        state_constraints=StateConstraints(upper_bounds=np.array([1.0])),
    )
    ok, _ = chk2.check_state(np.array([2.0]))
    assert not ok
