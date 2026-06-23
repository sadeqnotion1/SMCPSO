#==========================================================================================\\\
#====================== scripts/optimization/optimize_chattering_focused.py ==============\\\
#==========================================================================================\\\

"""
PSO Optimization Focused on Chattering Reduction (Issue #12 - Corrected Version).

Key Difference from optimize_chattering_direct.py:
- Fitness = chattering_index (direct minimization)
- No tracking penalty dominating the fitness
- Constraints: tracking < 0.1 rad enforced via high penalty

This is the CORRECT fitness function for chattering reduction!
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
from scipy.fft import fft, fftfreq  # noqa: E402
from pyswarms.single import GlobalBestPSO  # noqa: E402

from src.config import load_config  # noqa: E402
from src.controllers.factory import create_controller  # noqa: E402
from src.plant.models.dynamics import DoubleInvertedPendulum  # noqa: E402


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def simulate_and_compute_metrics(controller_type: str, gains: np.ndarray, config: Any,
                                  dynamics, dt: float = 0.01, t_final: float = 15.0) -> Dict[str, float]:
    """
    Simulate controller and compute chattering-focused metrics.

    Returns metrics dictionary with:
    - chattering_index: PRIMARY metric (time + freq domain chattering)
    - tracking_error_rms: CONSTRAINT (must be < 0.1 rad)
    - control_effort_rms: Secondary metric
    """
    n_steps = int(t_final / dt)

    # Create controller with candidate gains
    try:
        temp_config = config.model_copy(deep=True)

        # Update both sources for gains
        if hasattr(temp_config.controller_defaults, controller_type):
            default_ctrl_config = getattr(temp_config.controller_defaults, controller_type)
            updated_default = default_ctrl_config.model_copy(update={'gains': gains.tolist()})
            setattr(temp_config.controller_defaults, controller_type, updated_default)

        if hasattr(temp_config.controllers, controller_type):
            ctrl_config = getattr(temp_config.controllers, controller_type)
            updated_ctrl = ctrl_config.model_copy(update={'gains': gains.tolist()})
            setattr(temp_config.controllers, controller_type, updated_ctrl)

        controller = create_controller(controller_type=controller_type, config=temp_config)
    except Exception as e:
        logger.error(f"Controller creation failed with gains {gains}: {e}")
        return {'fitness': 1e6, 'tracking_error_rms': 1e6, 'chattering_index': 1e6,
                'control_effort_rms': 1e6}

    # Initialize controller state
    if hasattr(controller, 'initialize_state'):
        state_vars = controller.initialize_state()
    else:
        state_vars = ()
    if hasattr(controller, 'initialize_history'):
        history = controller.initialize_history()
    else:
        history = {}

    # Initial state (small disturbance)
    initial_state = np.array([0.0, 0.02, 0.02, 0.0, 0.0, 0.0])
    state = initial_state.copy()
    control_history = []
    state_trajectory = []
    simulation_failed = False

    for i in range(n_steps):
        state_trajectory.append(state.copy())

        # Compute control
        try:
            result = controller.compute_control(state, state_vars, history)

            # Extract control value (handle all return types including numpy arrays)
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
            elif isinstance(result, np.ndarray):
                # Handle numpy array output (e.g., ModularHybridSMC)
                control_output = float(result.flat[0]) if result.size > 0 else 0.0
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
                'control_effort_rms': 1e6}

    # Convert to arrays
    control_hist = np.array(control_history)
    state_traj = np.array(state_trajectory[:len(control_history)])

    # Compute metrics
    # 1. Tracking error (pendulum angles only)
    tracking_error_rms = np.sqrt(np.mean(state_traj[:, 1:3]**2))

    # 2. Chattering index (PRIMARY OBJECTIVE)
    control_derivative = np.gradient(control_hist, dt)
    time_domain_index = np.sqrt(np.mean(control_derivative**2))

    spectrum = np.abs(fft(control_hist))
    freqs = fftfreq(len(control_hist), d=dt)
    hf_mask = np.abs(freqs) > 10.0
    hf_power = np.sum(spectrum[hf_mask]) if np.any(hf_mask) else 0.0
    total_power = np.sum(spectrum) + 1e-12
    freq_domain_index = hf_power / total_power

    chattering_index = 0.7 * time_domain_index + 0.3 * freq_domain_index

    # 3. Control effort
    control_effort_rms = np.sqrt(np.mean(control_hist**2))

    # CORRECTED FITNESS FUNCTION
    # Primary objective: minimize chattering directly
    # Constraint: tracking must be reasonable (< 0.1 rad)
    if tracking_error_rms > 0.1:
        # Heavy penalty for poor tracking
        tracking_constraint_penalty = (tracking_error_rms - 0.1) * 1000.0
    else:
        tracking_constraint_penalty = 0.0

    # Direct chattering minimization
    fitness = chattering_index + tracking_constraint_penalty

    return {
        'fitness': float(fitness),
        'tracking_error_rms': float(tracking_error_rms),
        'chattering_index': float(chattering_index),
        'time_domain_index': float(time_domain_index),
        'freq_domain_index': float(freq_domain_index),
        'control_effort_rms': float(control_effort_rms)
    }


def objective_function_factory(controller_type: str, config, dynamics):
    """Create PSO objective function for given controller type."""

    def objective_function(particle_positions: np.ndarray) -> np.ndarray:
        n_particles = particle_positions.shape[0]
        costs = np.zeros(n_particles)

        for i in range(n_particles):
            gains = particle_positions[i, :]
            result = simulate_and_compute_metrics(controller_type, gains, config, dynamics)
            costs[i] = result['fitness']

        return costs

    return objective_function


def main():
    parser = argparse.ArgumentParser(description='Chattering-focused PSO optimization (CORRECTED)')
    parser.add_argument('--controller', type=str, required=True,
                        choices=['classical_smc', 'adaptive_smc', 'sta_smc', 'hybrid_adaptive_sta_smc'],
                        help='Controller type')
    parser.add_argument('--n-particles', type=int, default=30, help='Number of PSO particles')
    parser.add_argument('--iters', type=int, default=150, help='Number of PSO iterations')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--output', type=str, default=None, help='Output JSON file')
    parser.add_argument('--config-path', type=str, default='config.yaml', help='Config file path')

    args = parser.parse_args()

    controller_type = args.controller
    n_particles = args.n_particles
    iters = args.iters
    seed = args.seed
    config_path = args.config_path

    if args.output is None:
        args.output = f'gains_{controller_type}_chattering_v2.json'

    logger.info("")
    logger.info(f"PSO Optimization: {controller_type} (CHATTERING-FOCUSED)")
    logger.info(f"{'='*80}")
    logger.info(f"Config: n_particles={n_particles}, iters={iters}, seed={seed}")

    # Load configuration and create dynamics
    config = load_config(config_path, allow_unknown=False)
    dynamics = DoubleInvertedPendulum(config=config.physics)

    # Get bounds
    bounds_config = config.pso.bounds
    if hasattr(bounds_config, controller_type):
        ctrl_bounds = getattr(bounds_config, controller_type)
        bounds_min = np.array(ctrl_bounds.min)
        bounds_max = np.array(ctrl_bounds.max)
    else:
        bounds_min = np.array(bounds_config.min)
        bounds_max = np.array(bounds_config.max)

    n_dims = len(bounds_min)
    logger.info(f"Search space: {n_dims}D, bounds: [{bounds_min[0]:.1f}, {bounds_max[0]:.1f}]")
    logger.info("FITNESS FUNCTION: chattering_index + tracking_penalty (if > 0.1)")

    # Create objective function
    objective_func = objective_function_factory(controller_type, config, dynamics)

    # PSO options
    options = {'c1': 2.0, 'c2': 2.0, 'w': 0.7}

    # Initialize PSO
    np.random.seed(seed)
    bounds = (bounds_min, bounds_max)

    optimizer = GlobalBestPSO(
        n_particles=n_particles,
        dimensions=n_dims,
        options=options,
        bounds=bounds
    )

    # Run optimization
    logger.info("Starting PSO optimization...")
    start_time = time.time()

    best_cost, best_gains = optimizer.optimize(objective_func, iters=iters)

    elapsed = time.time() - start_time

    # Evaluate best gains for detailed metrics
    best_result = simulate_and_compute_metrics(controller_type, best_gains, config, dynamics)

    logger.info("")
    logger.info(f"{'='*80}")
    logger.info("")
    logger.info(f"{controller_type}:")
    logger.info(f"  Chattering Index:  {best_result['chattering_index']:.3f} (target < 2.0)")
    logger.info(f"  Tracking Error:    {best_result['tracking_error_rms']:.4f} rad")
    logger.info(f"  Control Effort:    {best_result['control_effort_rms']:.2f} N")
    logger.info(f"  Time Domain:       {best_result['time_domain_index']:.2f}")
    logger.info(f"  Freq Domain:       {best_result['freq_domain_index']:.4f}")
    logger.info(f"  Best Gains:        {best_gains.tolist()}")
    logger.info(f"  Elapsed Time:      {elapsed:.1f}s")
    logger.info("")
    logger.info(f"{'='*80}")

    # Save results
    output_data = {
        'controller': controller_type,
        'gains': best_gains.tolist(),
        'metrics': best_result,
        'pso_config': {
            'n_particles': n_particles,
            'iters': iters,
            'seed': seed,
            'fitness_function': 'chattering_index + tracking_penalty'
        },
        'elapsed_time': elapsed
    }

    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)

    logger.info(f"Results saved to: {args.output}")


if __name__ == '__main__':
    main()