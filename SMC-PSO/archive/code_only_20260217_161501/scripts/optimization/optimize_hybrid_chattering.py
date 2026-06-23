#==========================================================================================\\\
#=================== scripts/optimization/optimize_hybrid_chattering.py ==================\\\
#==========================================================================================\\\

"""
Specialized PSO optimization for hybrid_adaptive_sta_smc with custom bounds.
The hybrid controller gains [c1, λ1, c2, λ2] require asymmetric bounds:
- c1, c2: surface weights [5.0, 30.0]
- λ1, λ2: slope parameters [0.1, 5.0] (smaller than c parameters)
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import argparse  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402
from typing import Dict, Any  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402
from pyswarms.single import GlobalBestPSO  # noqa: E402

from src.config import load_config  # noqa: E402
from src.controllers.factory import create_controller  # noqa: E402
from src.plant.models.dynamics import DoubleInvertedPendulum  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def evaluate_hybrid_gains(gains: np.ndarray, config: Any, dynamics: Any, initial_state: np.ndarray, dt: float, n_steps: int) -> Dict[str, float]:
    """
    Evaluate hybrid controller with given gains and return chattering + tracking metrics.

    Returns:
        Dictionary with fitness, chattering_index, tracking_error_rms, etc.
        Returns penalty values (1e6) if simulation fails.
    """
    # Create controller with these gains
    try:
        temp_config = config.model_copy(deep=True)

        # Update both sources for gains
        if hasattr(temp_config.controller_defaults, 'hybrid_adaptive_sta_smc'):
            default_ctrl_config = getattr(temp_config.controller_defaults, 'hybrid_adaptive_sta_smc')
            updated_default = default_ctrl_config.model_copy(update={'gains': gains.tolist()})
            setattr(temp_config.controller_defaults, 'hybrid_adaptive_sta_smc', updated_default)

        if hasattr(temp_config.controllers, 'hybrid_adaptive_sta_smc'):
            ctrl_config = getattr(temp_config.controllers, 'hybrid_adaptive_sta_smc')
            updated_ctrl = ctrl_config.model_copy(update={'gains': gains.tolist()})
            setattr(temp_config.controllers, 'hybrid_adaptive_sta_smc', updated_ctrl)

        controller = create_controller(controller_type='hybrid_adaptive_sta_smc', config=temp_config)
    except Exception as e:
        logger.error(f"Controller creation failed with gains {gains}: {e}")
        return {'fitness': 1e6, 'tracking_error_rms': 1e6, 'chattering_index': 1e6,
                'control_effort_rms': 1e6, 'smoothness_index': 0.0,
                'time_domain_index': 1e6, 'freq_domain_index': 1.0}

    # Initialize controller state
    state_vars = controller.initialize_state() if hasattr(controller, 'initialize_state') else ()
    history = controller.initialize_history() if hasattr(controller, 'initialize_history') else {}

    # Simulate
    state = initial_state.copy()
    control_history = []
    state_trajectory = []
    simulation_failed = False

    for i in range(n_steps):
        state_trajectory.append(state.copy())

        # Compute control
        try:
            result = controller.compute_control(state, state_vars, history)

            # Extract control value
            if hasattr(result, 'u'):
                control_output = result.u
                state_vars = getattr(result, 'state', state_vars)
                history = getattr(result, 'history', history)
            elif hasattr(result, 'control'):
                control_output = result.control
            elif isinstance(result, (int, float, np.floating, np.integer)):
                control_output = float(result)
            elif isinstance(result, tuple):
                control_output = float(result[0])
                if len(result) > 1:
                    state_vars = result[1]
                if len(result) > 2:
                    history = result[2]
            else:
                control_output = float(result)

        except Exception as e:
            logger.debug(f"Control computation failed at step {i}: {e}")
            simulation_failed = True
            break

        control_history.append(control_output)

        # Update dynamics
        control_array = np.array([control_output])
        state = dynamics.sanitize_state(state)
        dynamics_result = dynamics.compute_dynamics(state, control_array)

        if dynamics_result.success:
            state_dot = dynamics_result.state_derivative
            state = state + state_dot * dt

            # Check for instability
            if np.any(np.abs(state) > 1e3) or not np.all(np.isfinite(state)):
                simulation_failed = True
                break
        else:
            simulation_failed = True
            break

    if simulation_failed or len(control_history) < n_steps // 2:
        return {'fitness': 1e6, 'tracking_error_rms': 1e6, 'chattering_index': 1e6,
                'control_effort_rms': 1e6, 'smoothness_index': 0.0,
                'time_domain_index': 1e6, 'freq_domain_index': 1.0}

    # Calculate metrics
    control_array = np.array(control_history)
    state_array = np.array(state_trajectory[:len(control_history)])

    # Tracking error (RMS of angular positions)
    theta1 = state_array[:, 1]
    theta2 = state_array[:, 2]
    tracking_error_rms = float(np.sqrt(np.mean(theta1**2 + theta2**2)))

    # Chattering index (sum of absolute control changes)
    control_diff = np.diff(control_array)
    chattering_index = float(np.sum(np.abs(control_diff)))

    # Control effort
    control_effort_rms = float(np.sqrt(np.mean(control_array**2)))

    # Smoothness (inverse of max control derivative)
    max_derivative = float(np.max(np.abs(control_diff)) / dt if len(control_diff) > 0 else 1e6)
    smoothness_index = 1.0 / (max_derivative + 1e-6)

    # Fitness = weighted sum targeting chattering reduction
    fitness = (chattering_index * 1.0 +             # Primary: reduce chattering
               tracking_error_rms * 100.0 +         # Keep stable tracking
               control_effort_rms * 0.1 +           # Moderate control effort
               (1.0 - smoothness_index) * 50.0)     # Encourage smoothness

    return {
        'fitness': fitness,
        'tracking_error_rms': tracking_error_rms,
        'chattering_index': chattering_index,
        'control_effort_rms': control_effort_rms,
        'smoothness_index': smoothness_index,
        'time_domain_index': tracking_error_rms,
        'freq_domain_index': 1.0 - smoothness_index
    }


def pso_cost_function(particle_positions: np.ndarray, config: Any, dynamics: Any, initial_state: np.ndarray, dt: float, n_steps: int) -> np.ndarray:
    """
    PSO cost function that evaluates all particles in swarm.

    Args:
        particle_positions: Array of shape (n_particles, 4) with gain vectors

    Returns:
        Array of shape (n_particles,) with fitness values
    """
    n_particles = particle_positions.shape[0]
    costs = np.zeros(n_particles)

    for i in range(n_particles):
        gains = particle_positions[i, :]
        result = evaluate_hybrid_gains(gains, config, dynamics, initial_state, dt, n_steps)
        costs[i] = result['fitness']

    return costs


def main():
    parser = argparse.ArgumentParser(description='PSO optimization for hybrid_adaptive_sta_smc with custom bounds')
    parser.add_argument('--n-particles', type=int, default=30, help='Number of PSO particles')
    parser.add_argument('--iters', type=int, default=150, help='Number of PSO iterations')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--output', type=str, default='gains_hybrid_adaptive_sta_smc_chattering.json', help='Output JSON file')
    args = parser.parse_args()

    # Set seed
    np.random.seed(args.seed)

    logger.info("")
    logger.info("PSO Optimization: hybrid_adaptive_sta_smc (Custom Bounds)")
    logger.info("=" * 80)
    logger.info(f"Config: n_particles={args.n_particles}, iters={args.iters}, seed={args.seed}")

    # Load config
    config = load_config('config.yaml', allow_unknown=False)

    # Custom bounds for hybrid controller [c1, λ1, c2, λ2]
    # c1, c2: surface weights (larger)
    # λ1, λ2: slope parameters (smaller)
    lb = np.array([5.0, 0.5, 5.0, 0.1])  # Lower bounds
    ub = np.array([30.0, 10.0, 30.0, 5.0])  # Upper bounds
    bounds = (lb, ub)

    logger.info("Search space: 4D [c1, λ1, c2, λ2]")
    logger.info("  c1, c2 bounds: [5.0, 30.0] (surface weights)")
    logger.info("  λ1 bounds: [0.5, 10.0] (slope parameter)")
    logger.info("  λ2 bounds: [0.1, 5.0] (slope parameter)")

    # Setup dynamics and initial state
    dynamics = DoubleInvertedPendulum(config=config.physics)
    dt = 0.01
    t_sim = 15.0
    n_steps = int(t_sim / dt)

    # Small initial disturbance (0.02 rad ≈ 1.15 degrees)
    initial_state = np.array([0.0, 0.02, 0.02, 0.0, 0.0, 0.0])

    # PSO optimizer
    options = {'c1': 2.0, 'c2': 2.0, 'w': 0.7}
    optimizer = GlobalBestPSO(
        n_particles=args.n_particles,
        dimensions=4,
        options=options,
        bounds=bounds
    )

    logger.info("Starting PSO optimization...")
    start_time = time.time()

    # Run optimization
    best_cost, best_gains = optimizer.optimize(
        pso_cost_function,
        iters=args.iters,
        config=config,
        dynamics=dynamics,
        initial_state=initial_state,
        dt=dt,
        n_steps=n_steps
    )

    elapsed = time.time() - start_time

    # Evaluate best gains to get detailed metrics
    best_result = evaluate_hybrid_gains(best_gains, config, dynamics, initial_state, dt, n_steps)

    logger.info("")
    logger.info("=" * 80)
    logger.info("")
    logger.info("hybrid_adaptive_sta_smc:")
    logger.info(f"  Chattering:  {best_result['chattering_index']:.3f} (target < 2.0)")
    logger.info(f"  Tracking:    {best_result['tracking_error_rms']:.4f} rad")
    logger.info(f"  Control RMS: {best_result['control_effort_rms']:.2f} N")
    logger.info(f"  Smoothness:  {best_result['smoothness_index']:.4f}")

    # Check pass/fail
    criteria_passed = 0
    if best_result['chattering_index'] < 2.0:
        criteria_passed += 1
    if best_result['tracking_error_rms'] < 0.1:
        criteria_passed += 1
    if best_result['control_effort_rms'] < 100.0:
        criteria_passed += 1
    if best_result['smoothness_index'] > 0.001:
        criteria_passed += 1

    logger.info(f"  Criteria:    {criteria_passed}/4 passed")
    logger.info(f"  Time:        {elapsed:.1f}s")
    logger.info("")
    logger.info("=" * 80)

    # Save results
    output_data = {
        'controller': 'hybrid_adaptive_sta_smc',
        'gains': best_gains.tolist(),
        'metrics': best_result,
        'pso_config': {
            'n_particles': args.n_particles,
            'iters': args.iters,
            'seed': args.seed,
            'bounds': {'lower': lb.tolist(), 'upper': ub.tolist()}
        },
        'elapsed_time': elapsed
    }

    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)

    logger.info(f"Results saved to: {args.output}")


if __name__ == '__main__':
    main()