"""Test dynamics_model property with pytest fixtures."""
import pytest
import numpy as np
from src.controllers.smc.sta_smc import SuperTwistingSMC
from src.plant.models.simplified.dynamics import SimplifiedDIPDynamics
from src.plant.models.simplified.config import SimplifiedDIPConfig

# Mimic the test's fixture
@pytest.fixture
def dynamics():
    config = SimplifiedDIPConfig.create_default()
    return SimplifiedDIPDynamics(config)

def test_dynamics_model_property(dynamics):
    """Test that dynamics_model property works correctly."""
    gains = [1.18495, 47.7040, 1.0807, 7.4019, 46.9200, 0.6699]
    dt = 0.01

    # Create controller the same way the test does
    ctrl = SuperTwistingSMC(gains=gains, dt=dt, dynamics_model=dynamics)

    # Check dynamics_model property
    dyn = getattr(ctrl, "dynamics_model", None)
    print(f"\ndynamics_model: {dyn}")
    print(f"dynamics_model type: {type(dyn)}")
    print(f"dynamics passed in: {dynamics}")
    print(f"Are they the same? {dyn is dynamics}")

    assert dyn is not None, "dynamics_model should not be None"
    assert dyn is dynamics, "dynamics_model should be the same object as passed in"

    # Test step method
    state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])
    u = 1.0
    next_state = dyn.step(state, u, dt)
    print(f"\nstep() worked: {next_state[:3]}")

    assert next_state is not None, "step should return a state"
    assert len(next_state) == 6, "step should return 6D state"

if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
