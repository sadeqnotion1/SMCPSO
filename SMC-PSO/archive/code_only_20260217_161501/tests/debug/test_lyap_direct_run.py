"""Run Lyapunov test directly without pytest."""
import numpy as np
from src.controllers.smc.sta_smc import SuperTwistingSMC
from src.plant.models.simplified.dynamics import SimplifiedDIPDynamics
from src.plant.models.simplified.config import SimplifiedDIPConfig
from src.simulation.engines.vector_sim import simulate_system_batch

# Create dynamics (same as test fixture)
config = SimplifiedDIPConfig.create_default()
dynamics = SimplifiedDIPDynamics(config)

# Test parameters (same as test)
gains = [1.18495, 47.7040, 1.0807, 7.4019, 46.9200, 0.6699]
sim_steps = 1000
dt = 0.001
sim_time = sim_steps * dt

# Controller factory (same as test)
def controller_factory(particle_gains):
    ctrl = SuperTwistingSMC(gains=particle_gains, dt=dt, dynamics_model=dynamics)
    return ctrl

# Set up batch (same as test)
batch_size = 10
nominal_state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0], dtype=float)
initial_states = np.tile(nominal_state, (batch_size, 1))
initial_states += np.random.uniform(-0.01, 0.01, initial_states.shape)

# Particle gains (same as test)
particle_gains = np.tile(np.asarray(gains), (batch_size, 1))

# Run batch simulation (same as test)
print("Running batch simulation...")
t, x_b, u_b, sigma_b = simulate_system_batch(
    controller_factory=controller_factory,
    particles=particle_gains,
    initial_state=initial_states,
    sim_time=sim_time,
    dt=dt
)

# Check results
print("\nResults:")
print(f"  sigma_b.shape: {sigma_b.shape}")

if sigma_b.shape[1] == 0:
    print("\n[FAIL] sigma_b is empty (0 steps)!")
    import sys
    sys.exit(1)

print(f"\n[PASS] Got {sigma_b.shape[1]} steps")

# Calculate Lyapunov function (same as test)
V_history = 0.5 * sigma_b**2

# Check assertions (same as test)
tolerance = 1e-5
delta_V = np.diff(V_history, axis=1)

try:
    assert np.all(delta_V <= tolerance), \
        f"Lyapunov function did not decrease monotonically. Max increase: {np.max(delta_V):.2e}"
    print("[PASS] Lyapunov function decreased monotonically")
except AssertionError as e:
    print(f"[FAIL] {e}")

try:
    assert np.all(V_history[:, -1] < 1e-6), \
        f"Final V did not converge. Max final V: {np.max(V_history[:, -1]):.2e}"
    print("[PASS] Final V converged to < 1e-6")
except AssertionError as e:
    print(f"[FAIL] {e}")
