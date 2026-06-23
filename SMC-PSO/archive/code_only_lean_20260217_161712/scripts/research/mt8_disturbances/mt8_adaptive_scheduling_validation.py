"""
MT-8 Adaptive Gain Scheduling Validation

Tests adaptive gain scheduling across wide initial condition range (±0.05 to ±0.3 rad) to
address the MT-7 generalization failure (50.4x chattering increase at large perturbations).

Compares:
1. Fixed gains (MT-8 robust PSO optimized)
2. Adaptive gain scheduling (aggressive for small errors, conservative for large)

Test Matrix:
- Initial conditions: ±0.05, ±0.1, ±0.2, ±0.3 rad for [θ1, θ2]
- Controllers: Classical, STA, Adaptive, Hybrid
- Trials: 20 per initial condition
- Metrics: chattering, settling time, overshoot, convergence

Usage:
    python scripts/mt8_adaptive_scheduling_validation.py --controller classical_smc --trials 20
    python scripts/mt8_adaptive_scheduling_validation.py --controller all --trials 50
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config
from src.controllers.factory import create_controller
from src.controllers.adaptive_gain_scheduler import AdaptiveGainScheduler, GainScheduleConfig
from src.plant.core.dynamics import DIPDynamics

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_simulation(
    controller,
    dynamics: DIPDynamics,
    initial_condition: np.ndarray,
    sim_time: float = 10.0,
    dt: float = 0.01
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Run single simulation with given controller and initial condition."""

    # Time array
    t_arr = np.arange(0, sim_time, dt)
    n_steps = len(t_arr)

    # State and control arrays
    x_arr = np.zeros((n_steps, 6))
    u_arr = np.zeros(n_steps)

    x = initial_condition.copy()
    x_arr[0] = x

    # Controller state
    state_vars = controller.initialize_state()
    history = controller.initialize_history()

    for i in range(1, n_steps):
        # Compute control
        result = controller.compute_control(x, state_vars, history)
        u = float(result.u)

        # Saturate
        u = np.clip(u, -150.0, 150.0)

        # Step dynamics
        x = dynamics.step(x, u, dt)

        x_arr[i] = x
        u_arr[i] = u

    return t_arr, x_arr, u_arr


def compute_metrics(t: np.ndarray, x: np.ndarray, u: np.ndarray) -> Dict:
    """Compute performance metrics."""
    theta1 = x[:, 1]
    theta2 = x[:, 2]

    # Settling time (5° threshold)
    threshold = np.radians(5.0)
    settled_mask = (np.abs(theta1) < threshold) & (np.abs(theta2) < threshold)

    settling_time = 10.0
    for i in range(len(settled_mask) - 50):
        if np.all(settled_mask[i:i+50]):
            settling_time = t[i]
            break

    # Max overshoot
    max_overshoot = np.degrees(np.max(np.abs(np.concatenate([theta1, theta2]))))

    # Convergence check
    converged = settling_time < 9.0 and max_overshoot < 30.0

    # Chattering metric: mean absolute control derivative
    du = np.diff(u)
    chattering = np.mean(np.abs(du))

    # Control effort
    control_effort = np.sqrt(np.mean(u**2))

    return {
        'settling_time': settling_time,
        'max_overshoot': max_overshoot,
        'chattering': chattering,
        'control_effort': control_effort,
        'converged': converged
    }


def validate_adaptive_scheduling(
    controller_name: str,
    gains: List[float],
    dynamics: DIPDynamics,
    num_trials: int = 20,
    seed: int = 42
) -> Dict:
    """
    Run validation comparing fixed gains vs adaptive gain scheduling.

    Args:
        controller_name: Controller type
        gains: MT-8 robust PSO optimized gains
        dynamics: System dynamics
        num_trials: Trials per initial condition
        seed: Random seed

    Returns:
        Results dictionary with fixed and adaptive performance
    """

    logger.info(f"\nValidating {controller_name} with {num_trials} trials per initial condition...")

    # Initial condition magnitudes to test (wide range from MT-7)
    ic_magnitudes = [0.05, 0.1, 0.2, 0.3]  # radians

    results = {
        'fixed_gains': {},
        'adaptive_scheduling': {}
    }

    rng = np.random.RandomState(seed)

    for ic_mag in ic_magnitudes:
        logger.info(f"  Testing IC magnitude: ±{ic_mag:.2f} rad...")

        # Storage for this magnitude
        fixed_metrics = {
            'settling_time': [],
            'max_overshoot': [],
            'chattering': [],
            'control_effort': [],
            'converged': []
        }

        adaptive_metrics = {
            'settling_time': [],
            'max_overshoot': [],
            'chattering': [],
            'control_effort': [],
            'converged': []
        }

        for trial in range(num_trials):
            # Random initial condition: [x, θ1, θ2, x_dot, θ1_dot, θ2_dot]
            theta1_0 = rng.uniform(-ic_mag, ic_mag)
            theta2_0 = rng.uniform(-ic_mag, ic_mag)
            x0 = np.array([0.0, theta1_0, theta2_0, 0.0, 0.0, 0.0])

            # Test 1: Fixed gains (MT-8 robust PSO)
            try:
                controller_fixed = create_controller(controller_name, gains=gains)
                t, x, u = run_simulation(controller_fixed, dynamics, x0)
                metrics = compute_metrics(t, x, u)

                fixed_metrics['settling_time'].append(metrics['settling_time'])
                fixed_metrics['max_overshoot'].append(metrics['max_overshoot'])
                fixed_metrics['chattering'].append(metrics['chattering'])
                fixed_metrics['control_effort'].append(metrics['control_effort'])
                fixed_metrics['converged'].append(metrics['converged'])

            except Exception as e:
                logger.warning(f"    Fixed gains trial {trial+1} failed: {e}")
                fixed_metrics['settling_time'].append(10.0)
                fixed_metrics['max_overshoot'].append(999.0)
                fixed_metrics['chattering'].append(999.0)
                fixed_metrics['control_effort'].append(999.0)
                fixed_metrics['converged'].append(False)

            # Test 2: Adaptive gain scheduling
            try:
                controller_base = create_controller(controller_name, gains=gains)
                controller_adaptive = AdaptiveGainScheduler(
                    controller_base,
                    config=GainScheduleConfig(
                        small_error_threshold=0.1,
                        large_error_threshold=0.2,
                        conservative_scale=0.5,
                        hysteresis_width=0.01
                    )
                )

                t, x, u = run_simulation(controller_adaptive, dynamics, x0)
                metrics = compute_metrics(t, x, u)

                adaptive_metrics['settling_time'].append(metrics['settling_time'])
                adaptive_metrics['max_overshoot'].append(metrics['max_overshoot'])
                adaptive_metrics['chattering'].append(metrics['chattering'])
                adaptive_metrics['control_effort'].append(metrics['control_effort'])
                adaptive_metrics['converged'].append(metrics['converged'])

            except Exception as e:
                logger.warning(f"    Adaptive scheduling trial {trial+1} failed: {e}")
                adaptive_metrics['settling_time'].append(10.0)
                adaptive_metrics['max_overshoot'].append(999.0)
                adaptive_metrics['chattering'].append(999.0)
                adaptive_metrics['control_effort'].append(999.0)
                adaptive_metrics['converged'].append(False)

        # Compute statistics for this magnitude
        results['fixed_gains'][f'ic_{ic_mag:.2f}'] = {
            'settling_time_mean': float(np.mean(fixed_metrics['settling_time'])),
            'settling_time_std': float(np.std(fixed_metrics['settling_time'])),
            'overshoot_mean': float(np.mean(fixed_metrics['max_overshoot'])),
            'overshoot_std': float(np.std(fixed_metrics['max_overshoot'])),
            'chattering_mean': float(np.mean(fixed_metrics['chattering'])),
            'chattering_std': float(np.std(fixed_metrics['chattering'])),
            'control_effort_mean': float(np.mean(fixed_metrics['control_effort'])),
            'convergence_rate': float(np.mean(fixed_metrics['converged'])),
            'num_trials': num_trials
        }

        results['adaptive_scheduling'][f'ic_{ic_mag:.2f}'] = {
            'settling_time_mean': float(np.mean(adaptive_metrics['settling_time'])),
            'settling_time_std': float(np.std(adaptive_metrics['settling_time'])),
            'overshoot_mean': float(np.mean(adaptive_metrics['max_overshoot'])),
            'overshoot_std': float(np.std(adaptive_metrics['max_overshoot'])),
            'chattering_mean': float(np.mean(adaptive_metrics['chattering'])),
            'chattering_std': float(np.std(adaptive_metrics['chattering'])),
            'control_effort_mean': float(np.mean(adaptive_metrics['control_effort'])),
            'convergence_rate': float(np.mean(adaptive_metrics['converged'])),
            'num_trials': num_trials
        }

        # Compute improvement
        chattering_reduction = (
            (results['fixed_gains'][f'ic_{ic_mag:.2f}']['chattering_mean'] -
             results['adaptive_scheduling'][f'ic_{ic_mag:.2f}']['chattering_mean']) /
            results['fixed_gains'][f'ic_{ic_mag:.2f}']['chattering_mean'] * 100
        )

        logger.info(f"    Fixed: {results['fixed_gains'][f'ic_{ic_mag:.2f}']['chattering_mean']:.4f} chattering")
        logger.info(f"    Adaptive: {results['adaptive_scheduling'][f'ic_{ic_mag:.2f}']['chattering_mean']:.4f} chattering")
        logger.info(f"    Reduction: {chattering_reduction:.1f}%")

    return results


def main():
    parser = argparse.ArgumentParser(description='MT-8 Adaptive Gain Scheduling Validation')
    parser.add_argument('--controller', type=str, default='classical_smc',
                        choices=['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc', 'all'])
    parser.add_argument('--trials', type=int, default=20, help='Trials per initial condition')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--output', type=str, default='benchmarks/MT8_adaptive_scheduling_results.json')

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("MT-8 Adaptive Gain Scheduling Validation")
    logger.info(f"Trials per IC: {args.trials}")
    logger.info("=" * 80)

    config = load_config("config.yaml")
    dynamics = DIPDynamics(config.physics)

    controllers = ['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc'] if args.controller == 'all' else [args.controller]

    all_results = {}

    for controller_name in controllers:
        logger.info(f"\n{'='*80}")
        logger.info(f"Controller: {controller_name}")
        logger.info(f"{'='*80}")

        # Load MT-8 robust gains from config
        gains_dict = getattr(config.controller_defaults, controller_name)
        gains = list(gains_dict.gains)

        logger.info(f"Using MT-8 robust gains: {[round(g, 3) for g in gains]}")

        results = validate_adaptive_scheduling(controller_name, gains, dynamics, args.trials, args.seed)

        all_results[controller_name] = {
            'gains': gains,
            'validation': results,
            'num_trials': args.trials,
            'seed': args.seed
        }

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2)

    logger.info(f"\n{'='*80}")
    logger.info(f"Results saved to: {args.output}")
    logger.info(f"{'='*80}")

    # Summary
    logger.info("\nSummary (Chattering Reduction at ±0.3 rad):")
    for controller, data in all_results.items():
        fixed_chat = data['validation']['fixed_gains']['ic_0.30']['chattering_mean']
        adaptive_chat = data['validation']['adaptive_scheduling']['ic_0.30']['chattering_mean']
        reduction = (fixed_chat - adaptive_chat) / fixed_chat * 100
        logger.info(f"  {controller}: {reduction:.1f}% reduction ({fixed_chat:.4f} -> {adaptive_chat:.4f})")


if __name__ == "__main__":
    main()
