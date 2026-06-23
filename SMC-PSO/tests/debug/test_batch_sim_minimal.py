"""Minimal batch simulation test to debug Lyapunov issue."""
import numpy as np
from src.controllers.smc.sta_smc import SuperTwistingSMC
from src.plant.models.simplified.dynamics import SimplifiedDIPDynamics
from src.plant.models.simplified.config import SimplifiedDIPConfig
from src.simulation.engines.vector_sim import simulate_system_batch

# Create dynamics model
config = SimplifiedDIPConfig.create_default()
dynamics = SimplifiedDIPDynamics(config)

# Controller gains (from Lyapunov test)
gains = [1.18495, 47.7040, 1.0807, 7.4019, 46.9200, 0.6699]
dt = 0.01

# Controller factory
def controller_factory(particle_gains):
    return SuperTwistingSMC(gains=particle_gains, dt=dt, dynamics_model=dynamics)

# Initial states
batch_size = 2  # Use smaller batch for debugging
nominal_state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0], dtype=float)
initial_states = np.tile(nominal_state, (batch_size, 1))

# Particle gains
particle_gains = np.tile(np.asarray(gains), (batch_size, 1))

# Run batch simulation
print("Running batch simulation...")
print(f"  Batch size: {batch_size}")
print(f"  Initial states shape: {initial_states.shape}")
print(f"  Particle gains shape: {particle_gains.shape}")

try:
    t, x_b, u_b, sigma_b = simulate_system_batch(
        controller_factory=controller_factory,
        particles=particle_gains,
        initial_state=initial_states,
        sim_time=1.0,  # 1 second
        dt=dt
    )

    print("\nBatch simulation completed!")
    print(f"  Time points: {len(t)}")
    print(f"  States shape: {x_b.shape}")
    print(f"  Controls shape: {u_b.shape}")
    print(f"  Sigma shape: {sigma_b.shape}")

    if sigma_b.shape[1] == 0:
        print("\n[ERROR] sigma_b is empty! Simulation returned 0 steps.")
    else:
        print(f"\n  Sigma first 3 steps:\n{sigma_b[:, :min(3, sigma_b.shape[1])]}")
        print(f"  Sigma last 3 steps:\n{sigma_b[:, max(0, sigma_b.shape[1]-3):]}")

except Exception as e:
    print(f"\n[ERROR] Batch simulation failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
