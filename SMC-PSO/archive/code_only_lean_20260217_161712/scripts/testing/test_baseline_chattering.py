#!/usr/bin/env python3
"""
Quick test to verify chattering metric calculation with phase53 gains + fixed boundary layer.
Compare against Agent A baseline: chattering_index = 6.37
"""

import json
import sys
from pathlib import Path

import numpy as np

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.config import load_config
from src.controllers.smc.classic_smc import ClassicalSMC
from src.core.dynamics import DIPDynamics
from src.core.simulation_runner import run_simulation
from src.controllers.smc.algorithms.classical.boundary_layer import BoundaryLayer

# Load config and optimized gains
config = load_config(project_root / "config.yaml")

with open(project_root / "optimization_results/phase53/optimized_gains_classical_smc_phase53.json", 'r') as f:
    gains_data = json.load(f)

optimized_gains = gains_data['classical_smc']

print("=" * 80)
print("BASELINE CHATTERING TEST")
print("=" * 80)
print(f"Optimized gains: {optimized_gains}")
print(f"Fixed boundary layer: 0.3 (from config.yaml)")
print()

# Test with 10 random initial conditions
np.random.seed(42)
chattering_values = []

for i in range(10):
    # Random initial condition
    theta1_init = np.random.uniform(-0.3, 0.3)
    theta2_init = np.random.uniform(-0.3, 0.3)
    theta1_dot_init = np.random.uniform(-0.5, 0.5)
    theta2_dot_init = np.random.uniform(-0.5, 0.5)

    initial_state = np.array([
        0.0,
        theta1_init,
        theta2_init,
        0.0,
        theta1_dot_init,
        theta2_dot_init
    ])

    # Create controller with FIXED boundary layer (no adaptation)
    controller = ClassicalSMC(
        gains=optimized_gains,
        max_force=150.0,
        boundary_layer=0.3,
        boundary_layer_slope=0.0,  # NO ADAPTATION
        switch_method='tanh'
    )

    # Create dynamics
    dynamics = DIPDynamics(config.physics)

    # Run simulation
    t_arr, x_arr, u_arr = run_simulation(
        controller=controller,
        dynamics_model=dynamics,
        sim_time=10.0,
        dt=0.01,
        initial_state=initial_state,
        u_max=150.0
    )

    # Compute chattering index
    boundary_layer = BoundaryLayer(
        thickness=0.3,
        slope=0.0,
        switch_method='tanh'
    )
    chattering_index = boundary_layer.get_chattering_index(u_arr, dt=0.01)
    chattering_values.append(chattering_index)

    print(f"Run {i+1}: chattering_index = {chattering_index:.4f}")

# Statistics
mean_chattering = np.mean(chattering_values)
std_chattering = np.std(chattering_values)

print()
print("=" * 80)
print(f"Mean chattering: {mean_chattering:.4f} ± {std_chattering:.4f}")
print(f"Agent A baseline: 6.37 ± 1.20")
print(f"Difference: {mean_chattering - 6.37:.4f}")
print("=" * 80)
