# ============================================================================
# PSO Optimization for SMC Gain Tuning
# ============================================================================
# Demonstrates automated controller parameter tuning using Particle Swarm
# Optimization (PSO) to minimize tracking error + control effort

import numpy as np
from pyswarms.single import GlobalBestPSO


def cost_function(gains_array, **kwargs):
    """
    Cost function for PSO: evaluates controller performance.

    Parameters:
        gains_array: Array of shape (n_particles, n_dims) where each row
                     contains [k1, k2, lambda1, lambda2, K, epsilon]
        kwargs: Additional arguments (dynamics, simulation params, etc.)

    Returns:
        costs: Array of shape (n_particles,) containing cost for each particle
    """
    costs = []

    for gains in gains_array:
        # Run simulation with these gains
        tracking_error = simulate_with_gains(gains)  # Simplified placeholder
        control_effort = compute_control_effort(gains)
        chattering_penalty = compute_chattering(gains)

        # Multi-objective cost: weighted sum
        cost = (
            1.0 * tracking_error      # Prioritize tracking accuracy
            + 0.1 * control_effort    # Penalize excessive control
            + 0.5 * chattering_penalty  # Moderate chattering reduction
        )
        costs.append(cost)

    return np.array(costs)


def optimize_smc_gains():
    """
    Optimize SMC gains using PSO.
    """
    # Define search space bounds
    # [k1, k2, lambda1, lambda2, K, epsilon]
    min_bounds = [1.0, 0.5, 1.0, 0.5, 5.0, 0.01]
    max_bounds = [20.0, 10.0, 20.0, 10.0, 30.0, 0.1]
    bounds = (min_bounds, max_bounds)

    # PSO hyperparameters
    options = {
        'c1': 2.0,  # Cognitive parameter (personal best attraction)
        'c2': 2.0,  # Social parameter (global best attraction)
        'w': 0.9    # Inertia weight (exploration vs exploitation)
    }

    # Initialize PSO optimizer
    optimizer = GlobalBestPSO(
        n_particles=30,
        dimensions=6,
        options=options,
        bounds=bounds
    )

    # Run optimization
    best_cost, best_gains = optimizer.optimize(
        cost_function,
        iters=100,  # Number of iterations
        verbose=True
    )

    print(f"[OK] Optimization complete!")
    print(f"Best cost: {best_cost:.6f}")
    print(f"Best gains: k1={best_gains[0]:.3f}, k2={best_gains[1]:.3f}, "
          f"lambda1={best_gains[2]:.3f}, lambda2={best_gains[3]:.3f}, "
          f"K={best_gains[4]:.3f}, epsilon={best_gains[5]:.4f}")

    return best_gains


# Placeholder functions (simplified for demonstration)
def simulate_with_gains(gains):
    """Simulate system and return tracking error."""
    # In actual code: run full simulation with given gains
    return np.random.rand()  # Placeholder


def compute_control_effort(gains):
    """Compute control effort metric."""
    return np.sum(gains[:4]) * 0.01  # Placeholder


def compute_chattering(gains):
    """Compute chattering metric."""
    epsilon = gains[5]
    return 1.0 / epsilon if epsilon > 0.001 else 1000.0  # Smaller epsilon = more chattering


# Example usage
if __name__ == "__main__":
    print("[INFO] Starting PSO optimization for SMC gains...")
    best_gains = optimize_smc_gains()
    print(f"[INFO] Optimized gains ready for deployment")
