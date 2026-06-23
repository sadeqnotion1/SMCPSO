#!/usr/bin/env python
"""
PSO Optimization for STA-SMC Lyapunov Stability (Week 18 Phase 4C).

Re-optimizes STA-SMC gains for conftest.py physics parameters to ensure
Lyapunov function V = 0.5 * sigma^2 decreases monotonically.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import argparse  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402
from pyswarms.single import GlobalBestPSO  # noqa: E402

from src.config import load_config  # noqa: E402
from src.controllers.sta_smc import SuperTwistingSMC  # noqa: E402
from src.core.dynamics import DoubleInvertedPendulum  # noqa: E402
from src.core.vector_sim import simulate_system_batch  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def lyapunov_fitness(particles: np.ndarray) -> np.ndarray:
    """
    Fitness function based on Lyapunov stability criterion.

    Evaluates each particle's gains by:
    1. Running batch simulation with multiple initial conditions
    2. Computing Lyapunov function V = 0.5 * sigma^2
    3. Penalizing non-monotonic decrease
    4. Rewarding faster convergence to near-zero V

    Args:
        particles: Shape (n_particles, 6) array of STA-SMC gains

    Returns:
        fitness: Shape (n_particles,) array where lower is better
    """
    # Load conftest.py physics params from config.yaml
    config = load_config("config.yaml")
    physics_cfg = config.physics

    # Use the same approach as the test: PhysicsConfig from src.config
    from src.config import PhysicsConfig
    if not isinstance(physics_cfg, PhysicsConfig):
        physics_params = physics_cfg.model_dump()
        physics_config = PhysicsConfig(**physics_params)
    else:
        physics_config = physics_cfg

    dynamics = DoubleInvertedPendulum(physics_config)

    # Simulation params
    dt = 0.001
    sim_time = 1.0  # 1 second simulation

    # Controller factory for batch simulation
    def controller_factory(gains):
        return SuperTwistingSMC(gains=gains, dt=dt, dynamics_model=dynamics)

    # Create batch of initial states with noise
    batch_size = 10  # Multiple initial conditions per particle
    nominal_state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0], dtype=float)

    fitness_values = []

    for particle_gains in particles:
        try:
            # Create batch of initial states
            initial_states = np.tile(nominal_state, (batch_size, 1))
            initial_states += np.random.uniform(-0.01, 0.01, initial_states.shape)

            # Create batch of identical gains for this particle
            particle_gains_batch = np.tile(particle_gains, (batch_size, 1))

            # Run batch simulation
            t, x_b, u_b, sigma_b = simulate_system_batch(
                controller_factory=controller_factory,
                particles=particle_gains_batch,
                initial_state=initial_states,
                sim_time=sim_time,
                dt=dt
            )

            # Compute Lyapunov function history: V = 0.5 * sigma^2
            V_history = 0.5 * sigma_b**2

            # Check for monotonic decrease (with tolerance)
            delta_V = np.diff(V_history, axis=1)
            max_increase = np.max(delta_V)

            # Penalize non-monotonic behavior
            monotonic_penalty = 0.0
            if max_increase > 1e-5:
                monotonic_penalty = 1000.0 * max_increase

            # Final value penalty (want V -> 0)
            final_V = np.max(V_history[:, -1])
            convergence_penalty = 1000.0 * final_V

            # Mean V penalty (lower mean = faster convergence)
            mean_V = np.mean(V_history)

            # Total fitness (lower is better)
            fitness = monotonic_penalty + convergence_penalty + mean_V

        except Exception as e:
            logger.warning(f"Simulation failed for gains {particle_gains}: {e}")
            fitness = 1e6  # High penalty for invalid gains

        fitness_values.append(fitness)

    return np.array(fitness_values)


def optimize_sta_lyapunov(n_particles=50, iters=100, seed=42):
    """Run PSO optimization for STA-SMC Lyapunov stability."""
    logger.info("="*80)
    logger.info("PSO Optimization for STA-SMC Lyapunov Stability")
    logger.info("="*80)
    logger.info("Target: Conftest.py physics parameters")
    logger.info("Objective: Monotonic Lyapunov decrease")
    logger.info(f"PSO Config: {n_particles} particles, {iters} iterations, seed={seed}")
    logger.info("")

    # STA-SMC bounds (6 gains)
    # [K1_gain, K2_gain, k1_surface, k2_surface, lambda1, lambda2]
    bounds = (
        np.array([0.5, 0.5, 0.5, 0.5, 0.1, 0.1]),  # Lower bounds
        np.array([50.0, 50.0, 20.0, 20.0, 50.0, 10.0])  # Upper bounds
    )

    # PSO hyperparameters (standard configuration)
    options = {'c1': 2.0, 'c2': 2.0, 'w': 0.7}

    # Initialize optimizer
    np.random.seed(seed)
    optimizer = GlobalBestPSO(
        n_particles=n_particles,
        dimensions=6,
        options=options,
        bounds=bounds
    )

    # Run optimization
    logger.info("Starting PSO optimization...")
    start_time = time.time()

    best_cost, best_gains = optimizer.optimize(
        lyapunov_fitness,
        iters=iters,
        verbose=True
    )

    elapsed = time.time() - start_time
    logger.info(f"\nOptimization completed in {elapsed:.1f}s")
    logger.info(f"Best fitness: {best_cost:.6f}")
    logger.info(f"Best gains: {best_gains}")

    # Save results
    results = {
        'best_gains': best_gains.tolist(),
        'best_fitness': float(best_cost),
        'n_particles': n_particles,
        'iters': iters,
        'seed': seed,
        'elapsed_time': elapsed,
        'cost_history': [float(c) for c in optimizer.cost_history],
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    output_file = "gains_sta_lyapunov_optimized.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"\nResults saved to: {output_file}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Optimize STA-SMC for Lyapunov stability')
    parser.add_argument('--n-particles', type=int, default=50, help='Number of PSO particles')
    parser.add_argument('--iters', type=int, default=100, help='Number of PSO iterations')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')

    args = parser.parse_args()

    results = optimize_sta_lyapunov(
        n_particles=args.n_particles,
        iters=args.iters,
        seed=args.seed
    )

    logger.info("\n" + "="*80)
    logger.info("Next steps:")
    logger.info("1. Run: python scripts/optimization/validate_lyapunov_gains.py")
    logger.info("2. Update test_lyapunov.py with optimized gains")
    logger.info("3. Remove @pytest.mark.xfail decorator")
    logger.info("="*80)
