"""Fresh Lyapunov test with forced module reload."""
import sys
import importlib

# Force reload of all relevant modules
modules_to_reload = [
    'src.simulation.engines.vector_sim',
    'src.controllers.smc.sta_smc',
    'src.plant.models.simplified.dynamics',
]

for mod in modules_to_reload:
    if mod in sys.modules:
        importlib.reload(sys.modules[mod])

# Now import after reload
import numpy as np  # noqa: E402
from src.controllers.smc.sta_smc import SuperTwistingSMC  # noqa: E402
from src.plant.models.simplified.dynamics import SimplifiedDIPDynamics  # noqa: E402
from src.plant.models.simplified.config import SimplifiedDIPConfig  # noqa: E402
from src.simulation.engines.vector_sim import simulate_system_batch  # noqa: E402

# Create dynamics
config = SimplifiedDIPConfig.create_default()
dynamics = SimplifiedDIPDynamics(config)

# Controller gains
gains = [1.18495, 47.7040, 1.0807, 7.4019, 46.9200, 0.6699]
dt = 0.001

# Controller factory
def controller_factory(particle_gains):
    return SuperTwistingSMC(gains=particle_gains, dt=dt, dynamics_model=dynamics)

# Initial states
batch_size = 10
nominal_state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0], dtype=float)
initial_states = np.tile(nominal_state, (batch_size, 1))
initial_states += np.random.uniform(-0.01, 0.01, initial_states.shape)

# Particle gains
particle_gains = np.tile(np.asarray(gains), (batch_size, 1))

# Run batch simulation
print("Running batch simulation with FRESH modules...")
t, x_b, u_b, sigma_b = simulate_system_batch(
    controller_factory=controller_factory,
    particles=particle_gains,
    initial_state=initial_states,
    sim_time=1.0,
    dt=dt
)

print("\nSimulation completed!")
print(f"  sigma_b shape: {sigma_b.shape}")

if sigma_b.shape[1] == 0:
    print("\n[FAIL] sigma_b is empty! Simulation returned 0 steps.")
    sys.exit(1)
else:
    print(f"\n[PASS] Got {sigma_b.shape[1]} steps")

    # Calculate Lyapunov function
    V_history = 0.5 * sigma_b**2

    # Check monotonic decrease
    delta_V = np.diff(V_history, axis=1)
    tolerance = 1e-5

    if np.all(delta_V <= tolerance):
        print("[PASS] Lyapunov function decreased monotonically")
    else:
        print(f"[FAIL] Lyapunov function increased. Max increase: {np.max(delta_V):.2e}")

    # Check convergence
    if np.all(V_history[:, -1] < 1e-6):
        print("[PASS] Final V converged to < 1e-6")
    else:
        print(f"[FAIL] Final V did not converge. Max final V: {np.max(V_history[:, -1]):.2e}")
