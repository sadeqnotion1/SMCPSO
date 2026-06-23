"""
Debug script for Phase 2.1 - Single trial with verbose logging.
Tests one simulation to understand k1/k2 adaptation behavior.
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import load_config
from src.controllers.factory import create_controller
from src.plant.core.dynamics import DIPDynamics

# Load config
config = load_config()
dynamics = DIPDynamics(config.physics)

# Test gains (MT-8 robust PSO)
test_gains = [10.149, 12.839, 6.815, 2.750]
print(f"Creating controller with gains: {test_gains}")
print(f"  c1={test_gains[0]}, lambda1={test_gains[1]}")
print(f"  c2={test_gains[2]}, lambda2={test_gains[3]}")

# Create controller
controller = create_controller(
    'hybrid_adaptive_sta_smc',
    config=config,
    gains=test_gains
)

print(f"\nController created successfully!")
print(f"Controller type: {type(controller).__name__}")
print(f"Controller attributes: {dir(controller)}")

# Check if controller has gain attributes
if hasattr(controller, 'c1'):
    print(f"\nController gains:")
    print(f"  c1 = {controller.c1}")
    print(f"  c2 = {controller.c2}")
    print(f"  lambda1 = {controller.lambda1}")
    print(f"  lambda2 = {controller.lambda2}")

if hasattr(controller, 'k1_init'):
    print(f"\nAdaptive gain init values:")
    print(f"  k1_init = {controller.k1_init}")
    print(f"  k2_init = {controller.k2_init}")
    print(f"  k1_max = {controller.k1_max}")
    print(f"  k2_max = {controller.k2_max}")

# Initialize controller state
if hasattr(controller, 'initialize_state'):
    state_vars = controller.initialize_state()
    print(f"\nInitial state: {state_vars}")
else:
    state_vars = ()

if hasattr(controller, 'initialize_history'):
    history = controller.initialize_history()
    print(f"History keys: {history.keys()}")
else:
    history = {}

# Initial condition
initial_state = np.array([0.0, 0.05, 0.05, 0.0, 0.0, 0.0])
print(f"\nInitial state: {initial_state}")

# Short simulation (1 second)
dt = 0.01
duration = 1.0
steps = int(duration / dt)

# Storage
k1_traj = np.zeros(steps)
k2_traj = np.zeros(steps)
s_traj = np.zeros(steps)
u_traj = np.zeros(steps)
time = np.arange(steps) * dt

state = initial_state.copy()
last_u = 0.0

print(f"\nRunning {steps} steps...")

for i in range(steps):
    # Compute control
    output = controller.compute_control(state, last_u, history)

    # Extract values
    if hasattr(output, 'u'):
        u = output.u
        k1, k2, u_int = output.state
        s = output.sigma
    else:
        u = output
        k1, k2, s = 0.0, 0.0, 0.0

    # Store
    k1_traj[i] = k1
    k2_traj[i] = k2
    s_traj[i] = s
    u_traj[i] = u

    # Print first few steps
    if i < 5 or i % 20 == 0:
        print(f"Step {i}: k1={k1:.4f}, k2={k2:.4f}, s={s:.4f}, u={u:.2f}")

    # Step dynamics
    control_array = np.array([u])
    result = dynamics.compute_dynamics(state, control_array)
    if result.success:
        state = state + result.state_derivative * dt

    last_u = u

print(f"\nFinal values:")
print(f"  k1_final = {k1_traj[-1]:.6f}")
print(f"  k2_final = {k2_traj[-1]:.6f}")
print(f"  s_final = {s_traj[-1]:.6f}")
print(f"  Mean |s| = {np.mean(np.abs(s_traj)):.6f}")

# Plot trajectories
fig, axes = plt.subplots(4, 1, figsize=(10, 10))

axes[0].plot(time, k1_traj)
axes[0].set_ylabel('k1')
axes[0].set_title('Adaptive Gain k1')
axes[0].grid(True)

axes[1].plot(time, k2_traj)
axes[1].set_ylabel('k2')
axes[1].set_title('Adaptive Gain k2')
axes[1].grid(True)

axes[2].plot(time, s_traj)
axes[2].set_ylabel('|s| (rad)')
axes[2].set_title('Sliding Surface')
axes[2].grid(True)

axes[3].plot(time, u_traj)
axes[3].set_ylabel('u (N)')
axes[3].set_xlabel('Time (s)')
axes[3].set_title('Control Input')
axes[3].grid(True)

plt.tight_layout()
plt.savefig('benchmarks/research/phase2_1/debug_single_trial.png', dpi=150)
print(f"\nPlot saved to: benchmarks/research/phase2_1/debug_single_trial.png")
plt.close()

print("\n[OK] Debug complete!")
