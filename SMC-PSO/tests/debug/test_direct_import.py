"""Direct import test to bypass pytest caching."""
import sys

# Force reload of modules
if 'src.simulation.engines.vector_sim' in sys.modules:
    del sys.modules['src.simulation.engines.vector_sim']
if 'src.controllers.smc.sta_smc' in sys.modules:
    del sys.modules['src.controllers.smc.sta_smc']
if 'src.plant.models.simplified.dynamics' in sys.modules:
    del sys.modules['src.plant.models.simplified.dynamics']

import numpy as np
from src.controllers.smc.sta_smc import SuperTwistingSMC
from src.core.dynamics import DoubleInvertedPendulum
from src.core.vector_sim import simulate_system_batch
from src.plant.models.simplified.config import SimplifiedDIPConfig

# Check if our fix is there
print(f"SuperTwistingSMC has dynamics_model: {hasattr(SuperTwistingSMC, 'dynamics_model')}")

# Create controller and check
config = SimplifiedDIPConfig.create_default()
dynamics = DoubleInvertedPendulum(config)
gains = [1.18495, 47.7040, 1.0807, 7.4019, 46.9200, 0.6699]
dt = 0.01

ctrl = SuperTwistingSMC(gains=gains, dt=dt, dynamics_model=dynamics)
print(f"Controller instance has dynamics_model: {hasattr(ctrl, 'dynamics_model')}")
print(f"Controller dynamics_model value: {getattr(ctrl, 'dynamics_model', None)}")
print(f"Controller dyn value: {getattr(ctrl, 'dyn', None)}")

# Run batch simulation
def controller_factory(particle_gains):
    return SuperTwistingSMC(gains=particle_gains, dt=dt, dynamics_model=dynamics)

batch_size = 2
nominal_state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0], dtype=float)
initial_states = np.tile(nominal_state, (batch_size, 1))
particle_gains = np.tile(np.asarray(gains), (batch_size, 1))

print("\nRunning batch simulation...")
t, x_b, u_b, sigma_b = simulate_system_batch(
    controller_factory=controller_factory,
    particles=particle_gains,
    initial_state=initial_states,
    sim_time=1.0,
    dt=dt
)

print(f"Simulation completed with {sigma_b.shape[1]} steps")
