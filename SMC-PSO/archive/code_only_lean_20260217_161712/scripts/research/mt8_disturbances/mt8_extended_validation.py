"""
MT-8 Extended Validation: Test robust gains with sinusoidal and random disturbances

Validates generalization of robust PSO gains to UNSEEN disturbance types not used in fitness function.
PSO fitness only included: step (10N) + impulse (30N)
This script tests: sinusoidal (3 frequencies) + Gaussian noise (3 intensities)

Scenarios:
- Sinusoidal: low (0.5Hz, 5N), resonant (2Hz, 8N), high (5Hz, 3N)
- Random Gaussian: low (σ=2N), mid (σ=3N), high (σ=5N)

Usage:
    python scripts/mt8_extended_validation.py --controller all --trials 50
    python scripts/mt8_extended_validation.py --controller hybrid_adaptive_sta_smc --trials 100
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Callable

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config
from src.controllers.factory import create_controller
from src.plant.core.dynamics import DIPDynamics
from src.core.simulation_runner import SimulationRunner
from src.utils.disturbances import DisturbanceGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_sinusoidal_disturbance(amplitude: float, frequency: float, start_time: float = 1.0, seed: int = 42) -> DisturbanceGenerator:
    """Create sinusoidal disturbance using official DisturbanceGenerator."""
    gen = DisturbanceGenerator(seed=seed)
    gen.add_sinusoidal_disturbance(magnitude=amplitude, frequency=frequency, start_time=start_time, axis=0)
    return gen


def create_random_disturbance(std_dev: float, seed: int = 42) -> DisturbanceGenerator:
    """Create random Gaussian noise disturbance using official DisturbanceGenerator."""
    gen = DisturbanceGenerator(seed=seed)
    gen.add_random_disturbance(std_dev=std_dev, start_time=1.0, axis=0)
    return gen


def run_simulation_with_disturbance(
    controller_name: str,
    gains: List[float],
    dynamics: DIPDynamics,
    disturbance_gen: DisturbanceGenerator,
    sim_time: float = 10.0,
    dt: float = 0.01
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Run single simulation with external disturbance."""
    controller = create_controller(controller_name, gains=gains)

    # Initial conditions: small perturbation
    x0 = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])  # θ1=θ2=0.1 rad

    # Time array
    t_arr = np.arange(0, sim_time, dt)
    n_steps = len(t_arr)

    # State and control arrays
    x_arr = np.zeros((n_steps, 6))
    u_arr = np.zeros(n_steps)

    x = x0.copy()
    x_arr[0] = x

    # Controller state
    state_vars = controller.initialize_state()
    history = controller.initialize_history()

    for i in range(1, n_steps):
        t = t_arr[i-1]

        # Compute control
        result = controller.compute_control(x, state_vars, history)
        u = float(result.u)

        # Apply disturbance
        dist = disturbance_gen.get_disturbance_force_only(t)
        u_total = u + dist

        # Saturate
        u_total = np.clip(u_total, -150.0, 150.0)

        # Step dynamics
        x = dynamics.step(x, u_total, dt)

        x_arr[i] = x
        u_arr[i] = u_total

    return t_arr, x_arr, u_arr


def compute_metrics(t: np.ndarray, x: np.ndarray, u: np.ndarray, disturbance_start: float = 1.0) -> Dict:
    """Compute performance metrics."""
    theta1 = x[:, 1]
    theta2 = x[:, 2]

    # Find disturbance start index
    dist_idx = np.searchsorted(t, disturbance_start)

    # Settling time (5° threshold)
    threshold = np.radians(5.0)
    settled_mask = (np.abs(theta1) < threshold) & (np.abs(theta2) < threshold)

    settling_time = 10.0
    for i in range(dist_idx, len(settled_mask) - 50):
        if np.all(settled_mask[i:i+50]):
            settling_time = t[i] - disturbance_start
            break

    # Max overshoot after disturbance
    max_overshoot = np.degrees(np.max(np.abs(np.concatenate([theta1[dist_idx:], theta2[dist_idx:]]))))

    # Convergence check
    converged = settling_time < 9.0 and max_overshoot < 30.0

    # Control effort
    control_effort = np.sqrt(np.mean(u**2))

    return {
        'settling_time': settling_time,
        'max_overshoot': max_overshoot,
        'control_effort': control_effort,
        'converged': converged
    }


def validate_controller_extended(
    controller_name: str,
    gains: List[float],
    dynamics: DIPDynamics,
    num_trials: int = 50,
    seed: int = 42
) -> Dict:
    """Run extended validation with sinusoidal and random disturbances."""

    logger.info(f"\nValidating {controller_name} with {num_trials} trials per scenario...")

    scenarios = {
        'sinusoidal_low': create_sinusoidal_disturbance(amplitude=5.0, frequency=0.5, start_time=1.0, seed=seed),
        'sinusoidal_resonant': create_sinusoidal_disturbance(amplitude=8.0, frequency=2.0, start_time=1.0, seed=seed+1),
        'sinusoidal_high': create_sinusoidal_disturbance(amplitude=3.0, frequency=5.0, start_time=1.0, seed=seed+2),
        'random_gaussian_low': create_random_disturbance(std_dev=2.0, seed=seed+3),
        'random_gaussian_mid': create_random_disturbance(std_dev=3.0, seed=seed+4),
        'random_gaussian_high': create_random_disturbance(std_dev=5.0, seed=seed+5),
    }

    results = {}

    for scenario_name, disturbance_gen in scenarios.items():
        logger.info(f"  Testing {scenario_name}...")

        trial_metrics = {
            'settling_time': [],
            'max_overshoot': [],
            'control_effort': [],
            'converged': []
        }

        for trial in range(num_trials):
            try:
                t, x, u = run_simulation_with_disturbance(
                    controller_name, gains, dynamics, disturbance_gen, sim_time=10.0, dt=0.01
                )

                metrics = compute_metrics(t, x, u, disturbance_start=1.0)

                trial_metrics['settling_time'].append(metrics['settling_time'])
                trial_metrics['max_overshoot'].append(metrics['max_overshoot'])
                trial_metrics['control_effort'].append(metrics['control_effort'])
                trial_metrics['converged'].append(metrics['converged'])

            except Exception as e:
                logger.warning(f"    Trial {trial+1} failed: {e}")
                trial_metrics['settling_time'].append(10.0)
                trial_metrics['max_overshoot'].append(999.0)
                trial_metrics['control_effort'].append(999.0)
                trial_metrics['converged'].append(False)

        # Compute statistics
        settling_times = np.array(trial_metrics['settling_time'])
        overshoots = np.array(trial_metrics['max_overshoot'])
        control_efforts = np.array(trial_metrics['control_effort'])
        convergence_rate = np.mean(trial_metrics['converged'])

        results[scenario_name] = {
            'settling_time_mean': float(np.mean(settling_times)),
            'settling_time_std': float(np.std(settling_times)),
            'overshoot_mean': float(np.mean(overshoots)),
            'overshoot_std': float(np.std(overshoots)),
            'control_effort_mean': float(np.mean(control_efforts)),
            'control_effort_std': float(np.std(control_efforts)),
            'convergence_rate': float(convergence_rate),
            'num_trials': num_trials,
        }

        logger.info(f"    Overshoot: {results[scenario_name]['overshoot_mean']:.2f} ± {results[scenario_name]['overshoot_std']:.2f}°")
        logger.info(f"    Convergence: {convergence_rate*100:.1f}%")

    return results


def main():
    parser = argparse.ArgumentParser(description='MT-8 Extended Validation')
    parser.add_argument('--controller', type=str, default='all',
                        choices=['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc', 'all'])
    parser.add_argument('--trials', type=int, default=50, help='Trials per scenario')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--output', type=str, default='benchmarks/MT8_extended_validation_results.json')

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("MT-8 Extended Validation: Sinusoidal + Random Disturbances")
    logger.info(f"Trials per scenario: {args.trials}")
    logger.info("=" * 80)

    config = load_config("config.yaml")
    dynamics = DIPDynamics(config.physics)

    controllers = ['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc'] if args.controller == 'all' else [args.controller]

    all_results = {}

    for controller_name in controllers:
        logger.info(f"\n{'='*80}")
        logger.info(f"Controller: {controller_name}")
        logger.info(f"{'='*80}")

        # Load robust gains from config (now updated with MT-8 values)
        gains_dict = getattr(config.controller_defaults, controller_name)
        gains = list(gains_dict.gains)

        logger.info(f"Using MT-8 robust gains: {[round(g, 3) for g in gains]}")

        results = validate_controller_extended(controller_name, gains, dynamics, args.trials, args.seed)

        all_results[controller_name] = {
            'gains': gains,
            'validation': results,
            'num_trials': args.trials,
            'seed': args.seed,
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
    logger.info("\nSummary:")
    for controller, data in all_results.items():
        avg_conv = np.mean([v['convergence_rate'] for v in data['validation'].values()])
        avg_overshoot = np.mean([v['overshoot_mean'] for v in data['validation'].values()])
        logger.info(f"  {controller}: {avg_conv*100:.1f}% convergence, {avg_overshoot:.1f}° avg overshoot")


if __name__ == "__main__":
    main()
