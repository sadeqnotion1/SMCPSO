#==========================================================================================\\\
#=========================== optimize_chattering_direct.py ===========================\\\
#==========================================================================================\\\

"""
Direct PSO Optimization for Chattering Reduction (Issue #12).

Implements custom fitness function with explicit chattering penalty without
relying on PSOTuner's complex cost normalization that causes cost=0.0 issues.
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
import matplotlib.pyplot as plt  # noqa: E402
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


def simulate_and_evaluate(gains: np.ndarray, controller_type: str, config,
                         dynamics, dt: float = 0.01, t_final: float = 15.0) -> Dict[str, float]:
    """
    Simulate controller and compute comprehensive metrics.

    Returns metrics dictionary with:
    - tracking_error_rms: RMS tracking error for pendulum angles
    - chattering_index: Combined time/freq domain chattering metric
    - control_effort_rms: RMS control effort
    - smoothness_index: Control smoothness (1 / (1 + TV))
    - fitness: Overall fitness value for PSO
    """
    initial_state = np.array([0.0, 0.02, 0.02, 0.0, 0.0, 0.0])
    n_steps = int(t_final / dt)

    # Create controller with candidate gains
    try:
        # Create a modified config with the new gains
        # We need to update BOTH controller_defaults AND controllers sections
        # because factory's _resolve_controller_gains checks both
        temp_config = config.model_copy(deep=True)

        # Update in controller_defaults (factory fallback)
        if hasattr(temp_config.controller_defaults, controller_type):
            default_ctrl_config = getattr(temp_config.controller_defaults, controller_type)
            updated_default = default_ctrl_config.model_copy(update={'gains': gains.tolist()})
            setattr(temp_config.controller_defaults, controller_type, updated_default)

        # Update in controllers (primary source)
        if hasattr(temp_config.controllers, controller_type):
            ctrl_config = getattr(temp_config.controllers, controller_type)
            updated_ctrl = ctrl_config.model_copy(update={'gains': gains.tolist()})
            setattr(temp_config.controllers, controller_type, updated_ctrl)

        controller = create_controller(controller_type=controller_type, config=temp_config)
    except Exception as e:
        logger.error(f"Controller creation failed with gains {gains}: {e}")
        import traceback
        traceback.print_exc()
        return {'fitness': 1e6, 'tracking_error_rms': 1e6, 'chattering_index': 1e6,
                'control_effort_rms': 1e6, 'smoothness_index': 0.0,
                'time_domain_index': 1e6, 'freq_domain_index': 1.0}

    # Initialize controller state
    if hasattr(controller, 'initialize_state'):
        state_vars = controller.initialize_state()
    else:
        state_vars = ()
    if hasattr(controller, 'initialize_history'):
        history = controller.initialize_history()
    else:
        history = {}

    # Simulate
    state = initial_state.copy()
    control_history = []
    state_trajectory = []
    last_control = 0.0
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
            elif isinstance(result, np.ndarray):
                # Handle numpy array output (e.g., ModularHybridSMC returns [control, 0, 0])
                control_output = float(result.flat[0]) if result.size > 0 else 0.0
            else:
                control_output = float(result)

        except Exception as e:
            logger.debug(f"Control computation failed at step {i}: {e}")
            simulation_failed = True
            break

        control_history.append(control_output)
        last_control = control_output  # noqa: F841 - kept for future use

        # Update dynamics
        control_array = np.array([control_output])

        # Sanitize state before dynamics computation to handle boundary violations gracefully
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

    # Convert to arrays
    state_traj = np.array(state_trajectory)
    control_hist = np.array(control_history)

    # Compute metrics
    # 1. Tracking error (pendulum angles only)
    tracking_error_rms = np.sqrt(np.mean(state_traj[:, 1:3]**2))

    # 2. Chattering index
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

    # 4. Smoothness
    total_variation = np.sum(np.abs(np.diff(control_hist)))
    smoothness_index = 1.0 / (1.0 + total_variation)

    # Multi-objective fitness with explicit penalties
    chattering_target = 2.0
    tracking_target = 0.1
    effort_target = 100.0

    # Primary objective: tracking performance
    tracking_penalty = max(0.0, tracking_error_rms - tracking_target) * 100.0

    # Secondary objective: chattering reduction
    chattering_penalty = max(0.0, chattering_index - chattering_target) * 10.0

    # Efficiency constraint
    effort_penalty = max(0.0, control_effort_rms - effort_target) * 0.1

    # Combined fitness (lower is better)
    fitness = tracking_error_rms + chattering_penalty + tracking_penalty + effort_penalty

    return {
        'fitness': float(fitness),
        'tracking_error_rms': float(tracking_error_rms),
        'chattering_index': float(chattering_index),
        'time_domain_index': float(time_domain_index),
        'freq_domain_index': float(freq_domain_index),
        'control_effort_rms': float(control_effort_rms),
        'smoothness_index': float(smoothness_index),
        'total_variation': float(total_variation)
    }


def objective_function_factory(controller_type: str, config, dynamics):
    """Create PSO objective function for given controller type."""

    def objective(particles: np.ndarray) -> np.ndarray:
        """Evaluate fitness for a batch of particles."""
        n_particles = particles.shape[0]
        costs = np.zeros(n_particles)

        for i, gains in enumerate(particles):
            result = simulate_and_evaluate(gains, controller_type, config, dynamics)
            costs[i] = result['fitness']

        return costs

    return objective


def optimize_controller(controller_type: str, config_path: str, n_particles: int = 50,
                       iters: int = 300, seed: int = 42) -> Dict[str, Any]:
    """Run direct PSO optimization for chattering reduction."""

    logger.info(f"\n{'='*80}")
    logger.info(f"PSO Optimization: {controller_type}")
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
    logger.info(f"Optimization completed in {elapsed:.1f}s")
    logger.info(f"Best fitness: {best_cost:.6f}")
    logger.info(f"Best gains: {best_gains}")

    # Validate optimized gains
    logger.info("\nValidating optimized gains...")
    validation_metrics = simulate_and_evaluate(best_gains, controller_type, config, dynamics)

    logger.info("\nValidation Metrics:")
    logger.info(f"  Chattering Index:       {validation_metrics['chattering_index']:.3f} / 2.0")
    logger.info(f"  Tracking Error RMS:     {validation_metrics['tracking_error_rms']:.4f} rad")
    logger.info(f"  Control Effort RMS:     {validation_metrics['control_effort_rms']:.2f} N")
    logger.info(f"  Control Smoothness:     {validation_metrics['smoothness_index']:.3f}")
    logger.info(f"  HF Power Ratio:         {validation_metrics['freq_domain_index']:.3f}")

    # Acceptance criteria
    criteria = {
        'chattering_index': validation_metrics['chattering_index'] < 2.0,
        'tracking_error': validation_metrics['tracking_error_rms'] < 0.1,
        'control_smoothness': validation_metrics['smoothness_index'] > 0.7,
        'hf_power_ratio': validation_metrics['freq_domain_index'] < 0.1
    }

    criteria_passed = sum(criteria.values())
    logger.info(f"\nAcceptance Criteria: {criteria_passed}/4 passed")
    for k, v in criteria.items():
        logger.info(f"  {k}: {'PASS' if v else 'FAIL'}")

    return {
        'controller_type': controller_type,
        'best_gains': best_gains.tolist(),
        'best_cost': float(best_cost),
        'cost_history': optimizer.cost_history,
        'validation_metrics': validation_metrics,
        'acceptance_criteria': criteria,
        'criteria_passed': criteria_passed,
        'optimization_time_seconds': elapsed
    }


def plot_results(result: Dict, output_dir: Path):
    """Plot optimization results."""
    controller_type = result['controller_type']

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Convergence curve
    cost_history = result['cost_history']
    axes[0].plot(cost_history, linewidth=2, color='blue')
    axes[0].set_xlabel('Iteration', fontsize=12)
    axes[0].set_ylabel('Best Cost', fontsize=12)
    axes[0].set_title(f'PSO Convergence - {controller_type}', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_yscale('log')

    # Metrics bar chart
    metrics = result['validation_metrics']
    criteria = result['acceptance_criteria']

    metric_names = ['Chattering\nIndex', 'Tracking\nError', 'Smoothness', 'HF Power']
    metric_values = [
        metrics['chattering_index'] / 2.0,
        metrics['tracking_error_rms'] / 0.1,
        metrics['smoothness_index'],
        metrics['freq_domain_index'] * 10
    ]
    colors = ['g' if criteria[k] else 'r' for k in [
        'chattering_index', 'tracking_error', 'control_smoothness', 'hf_power_ratio'
    ]]

    axes[1].bar(range(len(metric_names)), metric_values, color=colors, alpha=0.7)
    axes[1].set_xticks(range(len(metric_names)))
    axes[1].set_xticklabels(metric_names, fontsize=10)
    axes[1].set_ylabel('Normalized Value', fontsize=12)
    axes[1].set_title('Acceptance Criteria', fontsize=14, fontweight='bold')
    axes[1].axhline(y=1.0, color='k', linestyle='--', linewidth=1, label='Target')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_path = output_dir / f'convergence_{controller_type}_direct.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    logger.info(f"Plot saved: {output_path}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Direct PSO Optimization for Issue #12')
    parser.add_argument('--controller', type=str, default='classical_smc',
                       choices=['classical_smc', 'adaptive_smc', 'sta_smc', 'hybrid_adaptive_sta_smc', 'all'])
    parser.add_argument('--n-particles', type=int, default=50)
    parser.add_argument('--iters', type=int, default=300)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--config', type=str, default='config.yaml')
    parser.add_argument('--output-dir', type=str, default='optimization_results_direct')

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    controllers = ['classical_smc', 'adaptive_smc', 'sta_smc', 'hybrid_adaptive_sta_smc'] \
                  if args.controller == 'all' else [args.controller]

    all_results = []

    for ctrl_type in controllers:
        try:
            result = optimize_controller(
                controller_type=ctrl_type,
                config_path=args.config,
                n_particles=args.n_particles,
                iters=args.iters,
                seed=args.seed
            )
            all_results.append(result)

            # Save gains
            gains_file = output_dir / f'gains_{ctrl_type}_chattering.json'
            with open(gains_file, 'w') as f:
                json.dump({
                    'controller_type': ctrl_type,
                    'gains': result['best_gains'],
                    'validation_metrics': result['validation_metrics'],
                    'acceptance_criteria': result['acceptance_criteria']
                }, f, indent=2)
            logger.info(f"Gains saved: {gains_file}")

            # Plot results
            plot_results(result, output_dir)

        except Exception as e:
            logger.error(f"Optimization failed for {ctrl_type}: {e}", exc_info=True)

    # Save summary
    summary_file = output_dir / 'optimization_summary.json'
    with open(summary_file, 'w') as f:
        json.dump({
            'campaign_config': {
                'n_particles': args.n_particles,
                'iters': args.iters,
                'seed': args.seed,
                'controllers_optimized': controllers
            },
            'results': all_results
        }, f, indent=2)
    logger.info(f"\nSummary saved: {summary_file}")

    # Print summary
    logger.info(f"\n{'='*80}")
    logger.info("OPTIMIZATION CAMPAIGN SUMMARY")
    logger.info(f"{'='*80}")
    for result in all_results:
        ctrl = result['controller_type']
        chat_idx = result['validation_metrics']['chattering_index']
        track_err = result['validation_metrics']['tracking_error_rms']
        passed = result['criteria_passed']

        logger.info(f"\n{ctrl}:")
        logger.info(f"  Chattering:  {chat_idx:.3f} ({'PASS' if chat_idx < 2.0 else 'FAIL'})")
        logger.info(f"  Tracking:    {track_err:.4f} rad")
        logger.info(f"  Criteria:    {passed}/4 passed")
        logger.info(f"  Time:        {result['optimization_time_seconds']:.1f}s")

    logger.info(f"\n{'='*80}\n")


if __name__ == '__main__':
    main()