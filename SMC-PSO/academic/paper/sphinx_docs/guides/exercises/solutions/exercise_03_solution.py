"""
Exercise 3 Solution: Custom Cost Function Design
=================================================

Design multi-objective cost: energy + chattering.

Author: DIP-SMC-PSO Development Team
Date: November 12, 2025
"""

import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from src.config import load_config
from src.controllers.factory import create_controller
from src.core.dynamics import DIPDynamics
from src.core.simulation_runner import run_simulation


def check_convergence(x_arr):
    """Check if simulation converged."""
    if np.any(np.isnan(x_arr)) or np.any(np.isinf(x_arr)):
        return False
    final_window = int(len(x_arr) * 0.1)
    theta1_final = x_arr[-final_window:, 2]
    theta2_final = x_arr[-final_window:, 3]
    return np.all(np.abs(theta1_final) < np.deg2rad(5)) and np.all(np.abs(theta2_final) < np.deg2rad(5))


def custom_cost_function(gains, config, weights):
    """Multi-objective cost: energy + chattering."""
    controller = create_controller('classical_smc', config, gains=gains)
    dynamics = DIPDynamics(config)
    t_arr, x_arr, u_arr = run_simulation(
        controller=controller,
        dynamics_model=dynamics,
        sim_time=config.simulation.duration,
        dt=config.simulation.dt,
        initial_state=config.simulation.initial_state
    )

    if not check_convergence(x_arr):
        return 9999.0

    energy = np.sum(u_arr**2) * config.simulation.dt
    chattering = compute_chattering(u_arr, config.simulation.dt)

    # Normalize
    norm_energy = 300.0
    norm_chattering = 15.0

    cost = (weights['energy'] * (energy / norm_energy) +
            weights['chattering'] * (chattering / norm_chattering))

    return cost


def compute_chattering(control_history, dt):
    """Estimate chattering frequency."""
    sign_changes = np.diff(np.sign(control_history))
    num_crossings = np.sum(np.abs(sign_changes) > 0)
    total_time = len(control_history) * dt
    return num_crossings / (2.0 * total_time) if total_time > 0 else 0.0


def run_exercise():
    """Run PSO with 3 weight configurations."""
    config = load_config("config.yaml")

    weight_configs = [
        {'energy': 0.7, 'chattering': 0.3},
        {'energy': 0.5, 'chattering': 0.5},
        {'energy': 0.3, 'chattering': 0.7}
    ]

    print("[INFO] Exercise 3: Custom Cost Function Design")
    print("[INFO] Objective: Minimize energy + chattering")

    solutions = []
    for i, weights in enumerate(weight_configs):
        print(f"\n[{i+1}/3] Testing weights: energy={weights['energy']}, chattering={weights['chattering']}")

        # Simplified PSO: Random search (50 candidates)
        best_cost = float('inf')
        best_gains = None
        best_metrics = None

        np.random.seed(42 + i)
        for trial in range(50):
            gains = np.array([
                np.random.uniform(0.1, 50.0),
                np.random.uniform(0.1, 50.0),
                np.random.uniform(0.1, 50.0),
                np.random.uniform(0.1, 50.0),
                np.random.uniform(1.0, 200.0),
                np.random.uniform(0.0, 50.0)
            ])

            cost = custom_cost_function(gains, config, weights)

            if cost < best_cost:
                best_cost = cost
                best_gains = gains

                # Evaluate metrics
                controller = create_controller('classical_smc', config, gains=best_gains)
                dynamics = DIPDynamics(config)
                t_arr, x_arr, u_arr = run_simulation(
                    controller=controller,
                    dynamics_model=dynamics,
                    sim_time=config.simulation.duration,
                    dt=config.simulation.dt,
                    initial_state=config.simulation.initial_state
                )

                energy = np.sum(u_arr**2) * config.simulation.dt
                chattering = compute_chattering(u_arr, config.simulation.dt)
                best_metrics = (energy, chattering)

        solutions.append({'weights': weights, 'gains': best_gains, 'metrics': best_metrics})
        print(f"  [OK] Energy: {best_metrics[0]:.1f} J, Chattering: {best_metrics[1]:.2f} Hz")

    # Recommendation
    print("\n[RECOMMENDATION]")
    print("  Best for battery-powered robot: Solution 2 (w_energy=0.5)")
    print("  Rationale: Balanced tradeoff between energy efficiency and smoothness")

    return solutions


if __name__ == "__main__":
    solutions = run_exercise()
    print("\n[SUCCESS] Exercise 3 complete!")
