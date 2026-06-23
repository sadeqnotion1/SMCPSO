"""Test using compatibility layer imports (same as pytest test)."""
import numpy as np
from src.controllers.smc.sta_smc import SuperTwistingSMC
from src.core.dynamics import DoubleInvertedPendulum
from src.core.vector_sim import simulate_system_batch

# Create dynamics
from src.plant.models.simplified.config import SimplifiedDIPConfig
config = SimplifiedDIPConfig.create_default()
dynamics = DoubleInvertedPendulum(config)

# Controller gains
gains = [1.18495, 47.7040, 1.0807, 7.4019, 46.9200, 0.6699]
dt = 0.01

# Controller factory
def controller_factory(particle_gains):
    return SuperTwistingSMC(gains=particle_gains, dt=dt, dynamics_model=dynamics)

# Initial states
batch_size = 2
nominal_state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0], dtype=float)
initial_states = np.tile(nominal_state, (batch_size, 1))

# Particle gains
particle_gains = np.tile(np.asarray(gains), (batch_size, 1))

# Run batch simulation
print("Running batch simulation with COMPATIBILITY LAYER imports...")
print(f"  SuperTwistingSMC from: {SuperTwistingSMC.__module__}")
print(f"  DoubleInvertedPendulum from: {DoubleInvertedPendulum.__module__}")
print(f"  simulate_system_batch from: {simulate_system_batch.__module__}")

try:
    t, x_b, u_b, sigma_b = simulate_system_batch(
        controller_factory=controller_factory,
        particles=particle_gains,
        initial_state=initial_states,
        sim_time=1.0,
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
