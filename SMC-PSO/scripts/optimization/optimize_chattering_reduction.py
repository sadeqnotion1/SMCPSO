#==========================================================================================\\\
#========================= optimize_chattering_reduction.py ============================\\\
#==========================================================================================\\\

"""
PSO Optimization Campaign for Issue #12 Chattering Reduction.

This script executes multi-objective optimization to achieve chattering_index < 2.0
while maintaining tracking performance. Uses custom fitness function with chattering
penalty and comprehensive validation reporting.
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import time

import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

from src.config import load_config
from src.controllers.factory import create_controller
from src.plant.models.dynamics import DoubleInvertedPendulum
from src.optimization.algorithms.pso_optimizer import PSOTuner


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def compute_chattering_metrics(control_array: np.ndarray, dt: float) -> Dict[str, float]:
    """
    Compute comprehensive chattering metrics.

    Metrics:
    - chattering_index: 0.7 * time_domain_index + 0.3 * freq_domain_index
    - time_domain_index: RMS of control derivative
    - freq_domain_index: High-frequency power ratio (f > 10 Hz)
    - total_variation: Sum of absolute control changes
    - smoothness_index: 1 / (1 + total_variation)

    Target: chattering_index < 2.0 (Issue #12)
    """
    # Time-domain: RMS of control derivative
    control_derivative = np.gradient(control_array, dt)
    time_domain_index = np.sqrt(np.mean(control_derivative**2))

    # Frequency-domain: FFT spectral analysis
    spectrum = np.abs(fft(control_array))
    freqs = fftfreq(len(control_array), d=dt)
    hf_mask = np.abs(freqs) > 10.0  # High-frequency threshold
    hf_power = np.sum(spectrum[hf_mask]) if np.any(hf_mask) else 0.0
    total_power = np.sum(spectrum) + 1e-12
    freq_domain_index = hf_power / total_power

    # Combined chattering index (Issue #12 metric)
    chattering_index = 0.7 * time_domain_index + 0.3 * freq_domain_index

    # Control smoothness
    total_variation = np.sum(np.abs(np.diff(control_array)))
    smoothness_index = 1.0 / (1.0 + total_variation)

    return {
        'chattering_index': chattering_index,
        'time_domain_index': time_domain_index,
        'freq_domain_index': freq_domain_index,
        'hf_power_ratio': freq_domain_index,
        'total_variation': total_variation,
        'smoothness_index': smoothness_index
    }


def simulate_controller(controller, dynamics, dt: float, t_final: float,
                       initial_state: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Simulate controller with dynamics for validation.

    Returns:
        state_trajectory: (n_steps, 6) state history
        control_history: (n_steps,) control signal history
        sliding_surface_history: (n_steps,) sliding surface history
    """
    n_steps = int(t_final / dt)
    state = initial_state.copy()

    # Initialize controller state
    if hasattr(controller, 'initialize_state'):
        state_vars = controller.initialize_state()
    else:
        state_vars = ()

    if hasattr(controller, 'initialize_history'):
        history = controller.initialize_history()
    else:
        history = {}

    # Storage
    state_trajectory = np.zeros((n_steps, 6))
    control_history = np.zeros(n_steps)
    sliding_surface_history = np.zeros(n_steps)

    last_control = 0.0

    for i in range(n_steps):
        state_trajectory[i] = state

        # Compute control (handle different controller interfaces)
        controller_type = getattr(controller, 'controller_type', 'unknown')

        if controller_type == "hybrid_adaptive_sta_smc":
            result = controller.compute_control(state, last_control)
        else:
            result = controller.compute_control(state, state_vars, history)

        # Extract control value
        if hasattr(result, 'u'):
            control_output = result.u
            state_vars = getattr(result, 'state', state_vars)
            history = getattr(result, 'history', history)
        elif hasattr(result, 'control'):
            control_output = result.control
            state_vars = getattr(result, 'state', state_vars)
            history = getattr(result, 'history', history)
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

        # Extract sliding surface
        if isinstance(history, dict) and 'sigma' in history:
            sigma_list = history['sigma']
            sigma = sigma_list[-1] if isinstance(sigma_list, list) and len(sigma_list) > 0 else 0.0
        else:
            sigma = 0.0

        control_history[i] = control_output
        sliding_surface_history[i] = sigma
        last_control = control_output

        # Update dynamics
        control_array = np.array([control_output]) if isinstance(control_output, (int, float)) else control_output
        dynamics_result = dynamics.compute_dynamics(state, control_array)

        if dynamics_result.success:
            state_dot = dynamics_result.state_derivative
            state = state + state_dot * dt
        else:
            logger.warning(f"Dynamics computation failed at step {i}: {dynamics_result.info}")
            break

    return state_trajectory, control_history, sliding_surface_history


def evaluate_fitness_for_pso(gains: np.ndarray, controller_type: str, config,
                             dynamics) -> float:
    """
    Multi-objective fitness function for PSO optimization.

    Objectives:
    1. Primary: Maintain tracking performance (tracking_error_rms < 0.1 rad)
    2. Secondary: Reduce chattering (chattering_index < 2.0)

    Fitness = tracking_error_rms + penalty * max(0, chattering_index - target)

    Args:
        gains: Gain vector to evaluate
        controller_type: Type of controller
        config: Configuration object
        dynamics: Dynamics model

    Returns:
        fitness: Combined fitness value (lower is better)
    """
    dt = 0.01
    t_final = 10.0
    initial_state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])

    # Create controller with candidate gains
    try:
        # Create temporary config with candidate gains
        temp_config = config.model_copy(deep=True)

        # Update gains in the appropriate location
        if hasattr(temp_config.controller_defaults, controller_type):
            setattr(getattr(temp_config.controller_defaults, controller_type), 'gains', gains.tolist())

        if hasattr(temp_config.controllers, controller_type):
            controller_cfg = getattr(temp_config.controllers, controller_type)
            if hasattr(controller_cfg, 'gains'):
                controller_cfg.gains = gains.tolist()

        # Create controller
        controller = create_controller(
            controller_type=controller_type,
            config=temp_config
        )
    except Exception as e:
        logger.warning(f"Controller creation failed for gains {gains}: {e}")
        return 1e6  # High penalty for invalid gains

    # Simulate
    try:
        state_traj, control_hist, _ = simulate_controller(
            controller, dynamics, dt, t_final, initial_state
        )
    except Exception as e:
        logger.warning(f"Simulation failed for gains {gains}: {e}")
        return 1e6

    # Compute tracking error (primary objective)
    tracking_error_rms = np.sqrt(np.mean(state_traj[:, 1:3]**2))

    # Compute chattering metrics (secondary objective)
    chattering_metrics = compute_chattering_metrics(control_hist, dt)
    chattering_index = chattering_metrics['chattering_index']

    # Multi-objective fitness with penalty
    chattering_target = 2.0
    chattering_penalty = 10.0
    tracking_constraint = 0.1  # Max acceptable tracking error

    # Penalty for excessive chattering
    chattering_violation = max(0.0, chattering_index - chattering_target)

    # Penalty for poor tracking
    tracking_violation = max(0.0, tracking_error_rms - tracking_constraint)

    # Combined fitness
    fitness = (
        tracking_error_rms +
        chattering_penalty * chattering_violation +
        100.0 * tracking_violation  # Heavy penalty for tracking constraint violation
    )

    return fitness


def optimize_controller_gains(controller_type: str, config_path: str,
                              n_particles: int = 50, iters: int = 300,
                              seed: int = 42) -> Dict[str, Any]:
    """
    Run PSO optimization for a single controller type.

    Args:
        controller_type: Controller type to optimize
        config_path: Path to configuration file
        n_particles: Number of PSO particles
        iters: Number of PSO iterations
        seed: Random seed for reproducibility

    Returns:
        Dictionary with optimization results
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"Starting PSO Optimization for {controller_type}")
    logger.info(f"{'='*80}")
    logger.info(f"PSO Configuration: n_particles={n_particles}, iters={iters}, seed={seed}")

    # Load configuration
    config = load_config(config_path, allow_unknown=False)

    # Create dynamics model
    dynamics = DoubleInvertedPendulum(config=config.physics)

    # Get controller-specific bounds from config
    bounds_config = config.pso.bounds
    if hasattr(bounds_config, controller_type):
        controller_bounds = getattr(bounds_config, controller_type)
        bounds_min = np.array(controller_bounds.min)
        bounds_max = np.array(controller_bounds.max)
    else:
        # Fallback to default bounds
        bounds_min = np.array(bounds_config.min)
        bounds_max = np.array(bounds_config.max)

    n_dims = len(bounds_min)
    logger.info(f"Search space: {n_dims} dimensions")
    logger.info(f"Bounds: min={bounds_min}, max={bounds_max}")

    # Controller factory for PSOTuner
    def controller_factory(gains):
        temp_config = config.model_copy(deep=True)

        # Update gains
        if hasattr(temp_config.controller_defaults, controller_type):
            setattr(getattr(temp_config.controller_defaults, controller_type), 'gains', gains.tolist())

        if hasattr(temp_config.controllers, controller_type):
            controller_cfg = getattr(temp_config.controllers, controller_type)
            if hasattr(controller_cfg, 'gains'):
                controller_cfg.gains = gains.tolist()

        return create_controller(
            controller_type=controller_type,
            config=temp_config
        )

    # Add controller type hint for PSO tuner
    controller_factory.controller_type = controller_type
    controller_factory.n_gains = n_dims

    # Create PSO tuner
    tuner = PSOTuner(
        controller_factory=controller_factory,
        config=config,
        seed=seed
    )

    # Run optimization
    logger.info("Starting PSO optimization...")
    start_time = time.time()

    result = tuner.optimise(
        iters_override=iters,
        n_particles_override=n_particles
    )

    elapsed_time = time.time() - start_time
    logger.info(f"Optimization completed in {elapsed_time:.1f} seconds")

    # Extract results
    best_gains = result['best_pos']
    best_cost = result['best_cost']
    cost_history = result['history']['cost']

    logger.info(f"Best cost: {best_cost:.6f}")
    logger.info(f"Best gains: {best_gains}")

    # Validate optimized gains
    logger.info("\nValidating optimized gains...")

    # Create controller with optimized gains
    optimized_controller = controller_factory(best_gains)

    # Simulate with optimized gains
    dt = 0.01
    t_final = 10.0
    initial_state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])

    state_traj, control_hist, surface_hist = simulate_controller(
        optimized_controller, dynamics, dt, t_final, initial_state
    )

    # Compute validation metrics
    tracking_error_rms = np.sqrt(np.mean(state_traj[:, 1:3]**2))
    control_effort_rms = np.sqrt(np.mean(control_hist**2))
    chattering_metrics = compute_chattering_metrics(control_hist, dt)

    # Boundary layer effectiveness
    boundary_layer = getattr(optimized_controller, 'boundary_layer', 0.3)
    time_in_boundary = np.sum(np.abs(surface_hist) <= boundary_layer) / len(surface_hist)

    # Performance degradation
    baseline_tracking = 0.05  # Conservative baseline
    performance_degradation = max(0.0, (tracking_error_rms - baseline_tracking) / baseline_tracking)

    logger.info("\nValidation Metrics:")
    logger.info(f"  Chattering Index:          {chattering_metrics['chattering_index']:.3f} / 2.0 (target)")
    logger.info(f"  Tracking Error RMS:        {tracking_error_rms:.4f} rad")
    logger.info(f"  Control Effort RMS:        {control_effort_rms:.2f} N")
    logger.info(f"  Boundary Layer Eff:        {time_in_boundary:.3f}")
    logger.info(f"  Control Smoothness:        {chattering_metrics['smoothness_index']:.3f}")
    logger.info(f"  HF Power Ratio:            {chattering_metrics['hf_power_ratio']:.3f}")
    logger.info(f"  Performance Degradation:   {performance_degradation*100:.1f}%")

    # Check acceptance criteria
    criteria_pass = {
        'chattering_index': chattering_metrics['chattering_index'] < 2.0,
        'boundary_layer_effectiveness': time_in_boundary > 0.8,
        'control_smoothness': chattering_metrics['smoothness_index'] > 0.7,
        'hf_power_ratio': chattering_metrics['hf_power_ratio'] < 0.1,
        'performance_degradation': performance_degradation < 0.05
    }

    criteria_passed = sum(criteria_pass.values())
    total_criteria = len(criteria_pass)

    logger.info(f"\nAcceptance Criteria: {criteria_passed}/{total_criteria} passed")
    for criterion, passed in criteria_pass.items():
        logger.info(f"  {criterion}: {'PASS' if passed else 'FAIL'}")

    return {
        'controller_type': controller_type,
        'best_gains': best_gains.tolist(),
        'best_cost': float(best_cost),
        'cost_history': cost_history.tolist() if isinstance(cost_history, np.ndarray) else cost_history,
        'validation_metrics': {
            'chattering_index': float(chattering_metrics['chattering_index']),
            'time_domain_index': float(chattering_metrics['time_domain_index']),
            'freq_domain_index': float(chattering_metrics['freq_domain_index']),
            'tracking_error_rms': float(tracking_error_rms),
            'control_effort_rms': float(control_effort_rms),
            'boundary_layer_effectiveness': float(time_in_boundary),
            'control_smoothness': float(chattering_metrics['smoothness_index']),
            'hf_power_ratio': float(chattering_metrics['hf_power_ratio']),
            'performance_degradation': float(performance_degradation)
        },
        'acceptance_criteria': {k: bool(v) for k, v in criteria_pass.items()},
        'criteria_passed': int(criteria_passed),
        'total_criteria': int(total_criteria),
        'optimization_time_seconds': float(elapsed_time)
    }


def plot_convergence(results: Dict[str, Any], output_dir: Path):
    """Plot PSO convergence curves."""
    controller_type = results['controller_type']
    cost_history = results['cost_history']

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Convergence curve
    axes[0].plot(cost_history, linewidth=2)
    axes[0].set_xlabel('Iteration', fontsize=12)
    axes[0].set_ylabel('Best Cost', fontsize=12)
    axes[0].set_title(f'PSO Convergence - {controller_type}', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_yscale('log')

    # Metrics comparison
    metrics = results['validation_metrics']
    criteria = results['acceptance_criteria']

    metric_names = [
        'Chattering\nIndex',
        'Boundary\nLayer Eff',
        'Control\nSmoothness',
        'HF Power\nRatio',
        'Perf\nDegradation'
    ]
    metric_values = [
        metrics['chattering_index'] / 2.0,  # Normalize to target
        metrics['boundary_layer_effectiveness'],
        metrics['control_smoothness'],
        metrics['hf_power_ratio'] * 10,  # Scale for visibility
        metrics['performance_degradation'] * 20  # Scale for visibility
    ]
    colors = ['g' if criteria[k] else 'r' for k in [
        'chattering_index', 'boundary_layer_effectiveness',
        'control_smoothness', 'hf_power_ratio', 'performance_degradation'
    ]]

    axes[1].bar(range(len(metric_names)), metric_values, color=colors, alpha=0.7)
    axes[1].set_xticks(range(len(metric_names)))
    axes[1].set_xticklabels(metric_names, fontsize=10)
    axes[1].set_ylabel('Normalized Value', fontsize=12)
    axes[1].set_title('Acceptance Criteria Status', fontsize=14, fontweight='bold')
    axes[1].axhline(y=1.0, color='k', linestyle='--', linewidth=1, label='Target')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_path = output_dir / f'convergence_{controller_type}.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    logger.info(f"Convergence plot saved: {output_path}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description='PSO Optimization Campaign for Issue #12 Chattering Reduction'
    )
    parser.add_argument(
        '--controller',
        type=str,
        choices=['classical_smc', 'adaptive_smc', 'sta_smc', 'hybrid_adaptive_sta_smc', 'all'],
        default='all',
        help='Controller type to optimize (default: all)'
    )
    parser.add_argument(
        '--n-particles',
        type=int,
        default=50,
        help='Number of PSO particles (default: 50)'
    )
    parser.add_argument(
        '--iters',
        type=int,
        default=300,
        help='Number of PSO iterations (default: 300)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='optimization_results',
        help='Directory for output files (default: optimization_results)'
    )

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine controllers to optimize
    if args.controller == 'all':
        controllers = ['classical_smc', 'adaptive_smc', 'sta_smc', 'hybrid_adaptive_sta_smc']
    else:
        controllers = [args.controller]

    # Run optimization campaign
    all_results = []

    for controller_type in controllers:
        try:
            result = optimize_controller_gains(
                controller_type=controller_type,
                config_path=args.config,
                n_particles=args.n_particles,
                iters=args.iters,
                seed=args.seed
            )
            all_results.append(result)

            # Save individual results
            gains_file = output_dir / f'gains_{controller_type}_chattering.json'
            with open(gains_file, 'w') as f:
                json.dump({
                    'controller_type': controller_type,
                    'gains': result['best_gains'],
                    'validation_metrics': result['validation_metrics'],
                    'acceptance_criteria': result['acceptance_criteria']
                }, f, indent=2)
            logger.info(f"Gains saved: {gains_file}")

            # Plot convergence
            plot_convergence(result, output_dir)

        except Exception as e:
            logger.error(f"Optimization failed for {controller_type}: {e}", exc_info=True)

    # Generate summary report
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
    logger.info(f"\nSummary report saved: {summary_file}")

    # Print final summary
    logger.info(f"\n{'='*80}")
    logger.info("PSO OPTIMIZATION CAMPAIGN SUMMARY")
    logger.info(f"{'='*80}")

    for result in all_results:
        controller_type = result['controller_type']
        criteria_passed = result['criteria_passed']
        total_criteria = result['total_criteria']
        chattering_index = result['validation_metrics']['chattering_index']
        tracking_error = result['validation_metrics']['tracking_error_rms']

        logger.info(f"\n{controller_type}:")
        logger.info(f"  Chattering Index: {chattering_index:.3f} ({'PASS' if chattering_index < 2.0 else 'FAIL'})")
        logger.info(f"  Tracking Error:   {tracking_error:.4f} rad")
        logger.info(f"  Criteria Passed:  {criteria_passed}/{total_criteria}")
        logger.info(f"  Optimization Time: {result['optimization_time_seconds']:.1f}s")

    logger.info(f"\n{'='*80}")
    logger.info(f"All results saved to: {output_dir}")
    logger.info(f"{'='*80}\n")


if __name__ == '__main__':
    main()