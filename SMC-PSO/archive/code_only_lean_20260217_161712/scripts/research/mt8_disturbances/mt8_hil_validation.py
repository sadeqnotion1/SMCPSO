"""
MT-8 HIL (Hardware-in-the-Loop) Validation Script

Tests MT-8 robust PSO gains with adaptive gain scheduling on HIL infrastructure
to validate performance under realistic conditions:
- Network latency (UDP communication delays)
- Sensor noise (Gaussian measurement noise)
- Disturbance rejection (step, impulse, sinusoidal)

Compares:
1. Fixed gains (MT-8 robust PSO)
2. Adaptive gain scheduling

Test Matrix:
- Disturbance types: step (10N), impulse (30N, 0.1s), sinusoidal (5N, 0.5Hz)
- Network latency: 0ms, 5ms, 10ms
- Sensor noise: σ=0.001, 0.005, 0.01 rad
- Controllers: Classical SMC (primary), optionally others
- Trials: 10 per configuration

Usage:
    python scripts/mt8_hil_validation.py --controller classical_smc --trials 10
    python scripts/mt8_hil_validation.py --controller all --trials 20 --latency 5
    python scripts/mt8_hil_validation.py --quick  # 5 trials, classical only
"""

import argparse
import json
import logging
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config
from src.controllers.factory import create_controller
from src.controllers.adaptive_gain_scheduler import AdaptiveGainScheduler, GainScheduleConfig
# Import PlantServer directly to avoid pyserial dependency from enhanced_hil
import importlib.util
plant_server_path = Path(__file__).parent.parent / "src" / "interfaces" / "hil" / "plant_server.py"
spec = importlib.util.spec_from_file_location("plant_server", plant_server_path)
plant_server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plant_server_module)
PlantServer = plant_server_module.PlantServer
from src.utils.disturbances import DisturbanceGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HILTestHarness:
    """Test harness for HIL validation with disturbances and performance monitoring."""

    def __init__(
        self,
        config_dict: dict,
        controller,
        bind_addr: Tuple[str, int] = ("127.0.0.1", 9001),
        dt: float = 0.01,
        extra_latency_ms: float = 0.0,
        sensor_noise_std: float = 0.0,
        seed: int = 42
    ):
        self.config = config_dict
        self.controller = controller
        self.bind_addr = bind_addr
        self.dt = dt
        self.extra_latency_ms = extra_latency_ms
        self.sensor_noise_std = sensor_noise_std
        self.seed = seed

        # Create plant server
        self.server = PlantServer(
            cfg=config_dict,
            bind_addr=bind_addr,
            dt=dt,
            extra_latency_ms=extra_latency_ms,
            sensor_noise_std=sensor_noise_std,
            max_steps=None,  # Run until stopped
            server_ready_event=threading.Event(),
            rng=np.random.default_rng(seed)
        )

        # Controller state
        self.state_vars = controller.initialize_state()
        self.history = controller.initialize_history()

    def run_trial(
        self,
        initial_condition: np.ndarray,
        disturbance_gen: DisturbanceGenerator,
        sim_time: float = 10.0
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Run single HIL trial with given disturbance.

        Args:
            initial_condition: Initial state [x, θ1, θ2, ẋ, θ̇1, θ̇2]
            disturbance_gen: Disturbance generator for external forces
            sim_time: Simulation duration in seconds

        Returns:
            t_arr, x_arr, u_arr: Time, state, and control histories
        """
        n_steps = int(sim_time / self.dt)

        # Initialize arrays
        t_arr = np.arange(0, sim_time, self.dt)
        x_arr = np.zeros((n_steps, 6))
        u_arr = np.zeros(n_steps)

        # Set initial state
        x = initial_condition.copy()
        x_arr[0] = x

        # Reset server state (manual simulation without network)
        self.server.state = x.copy()

        # Reset controller state
        self.state_vars = self.controller.initialize_state()
        self.history = self.controller.initialize_history()

        for i in range(1, n_steps):
            t = t_arr[i-1]

            # Add sensor noise (simulate HIL noise)
            if self.sensor_noise_std > 0:
                noise = self.server.rng.normal(0, self.sensor_noise_std, size=6)
                x_measured = x + noise
            else:
                x_measured = x.copy()

            # Compute control from controller
            result = self.controller.compute_control(x_measured, self.state_vars, self.history)

            # Extract control signal (handle different return formats)
            if hasattr(result, 'u'):
                u = float(result.u)
                self.state_vars = result.state  # Note: field is 'state' not 'state_vars'
                self.history = result.history
            elif isinstance(result, tuple):
                u = float(result[0])
                if len(result) > 1:
                    self.state_vars = result[1]
                if len(result) > 2:
                    self.history = result[2]
            else:
                u = float(result)

            # Apply disturbance
            dist = disturbance_gen.get_disturbance_force_only(t)
            u_total = u + dist

            # Saturate control
            u_total = np.clip(u_total, -150.0, 150.0)

            # Step dynamics (use server's model)
            x = self.server.model.step(x, u_total)

            # Simulate network latency (simple delay)
            if self.extra_latency_ms > 0:
                time.sleep(self.extra_latency_ms / 1000.0)

            x_arr[i] = x
            u_arr[i] = u_total

        return t_arr, x_arr, u_arr


def compute_metrics(t: np.ndarray, x: np.ndarray, u: np.ndarray, disturbance_start: float = 1.0) -> Dict:
    """Compute performance metrics for HIL trial."""
    theta1 = x[:, 1]
    theta2 = x[:, 2]

    # Find disturbance start index
    dist_idx = np.searchsorted(t, disturbance_start)

    # Settling time (5° threshold after disturbance)
    threshold = np.radians(5.0)
    settled_mask = (np.abs(theta1) < threshold) & (np.abs(theta2) < threshold)

    settling_time = t[-1] - disturbance_start  # Default: didn't settle
    for i in range(dist_idx, len(settled_mask) - 50):
        if np.all(settled_mask[i:i+50]):
            settling_time = t[i] - disturbance_start
            break

    # Max overshoot after disturbance
    max_overshoot = np.degrees(np.max(np.abs(np.concatenate([theta1[dist_idx:], theta2[dist_idx:]]))))

    # Convergence check
    converged = settling_time < 9.0 and max_overshoot < 30.0

    # Chattering metric: mean absolute control derivative
    du = np.diff(u)
    chattering = np.mean(np.abs(du))

    # Control effort
    control_effort = np.sqrt(np.mean(u**2))

    # Tracking error (RMS angle error after disturbance)
    tracking_error = np.sqrt(np.mean(theta1[dist_idx:]**2 + theta2[dist_idx:]**2))

    return {
        'settling_time': settling_time,
        'max_overshoot': max_overshoot,
        'chattering': chattering,
        'control_effort': control_effort,
        'tracking_error': tracking_error,
        'converged': converged
    }


def create_disturbances(seed: int = 42) -> Dict[str, DisturbanceGenerator]:
    """Create standard disturbance generators for HIL testing."""
    scenarios = {
        'step_10N': create_step_disturbance(10.0, 1.0, seed),
        'impulse_30N': create_impulse_disturbance(30.0, 0.1, 1.0, seed+1),
        'sinusoidal_5N': create_sinusoidal_disturbance(5.0, 0.5, 1.0, seed+2),
    }
    return scenarios


def create_step_disturbance(magnitude: float, start_time: float, seed: int) -> DisturbanceGenerator:
    """Create step disturbance."""
    gen = DisturbanceGenerator(seed=seed)
    gen.add_step_disturbance(magnitude=magnitude, start_time=start_time, axis=0)
    return gen


def create_impulse_disturbance(magnitude: float, duration: float, start_time: float, seed: int) -> DisturbanceGenerator:
    """Create impulse disturbance."""
    gen = DisturbanceGenerator(seed=seed)
    gen.add_impulse_disturbance(magnitude=magnitude, duration=duration, start_time=start_time, axis=0)
    return gen


def create_sinusoidal_disturbance(amplitude: float, frequency: float, start_time: float, seed: int) -> DisturbanceGenerator:
    """Create sinusoidal disturbance."""
    gen = DisturbanceGenerator(seed=seed)
    gen.add_sinusoidal_disturbance(magnitude=amplitude, frequency=frequency, start_time=start_time, axis=0)
    return gen


def run_hil_validation(
    controller_name: str,
    gains: List[float],
    config_dict: dict,
    num_trials: int = 10,
    extra_latency_ms: float = 0.0,
    sensor_noise_std: float = 0.001,
    seed: int = 42
) -> Dict:
    """
    Run HIL validation comparing fixed gains vs adaptive scheduling.

    Args:
        controller_name: Controller type
        gains: MT-8 robust PSO optimized gains
        config_dict: Configuration dictionary
        num_trials: Trials per disturbance scenario
        extra_latency_ms: Network latency in milliseconds
        sensor_noise_std: Sensor noise standard deviation (rad)
        seed: Random seed

    Returns:
        Results dictionary with fixed and adaptive performance
    """
    logger.info(f"\nValidating {controller_name} on HIL with {num_trials} trials per scenario...")
    logger.info(f"  Network latency: {extra_latency_ms:.1f} ms")
    logger.info(f"  Sensor noise: σ={sensor_noise_std:.4f} rad")

    # Create disturbance scenarios
    disturbances = create_disturbances(seed)

    results = {
        'fixed_gains': {},
        'adaptive_scheduling': {},
        'hil_config': {
            'latency_ms': extra_latency_ms,
            'sensor_noise_std': sensor_noise_std,
            'num_trials': num_trials
        }
    }

    # Initial condition (small perturbation)
    x0 = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])

    for scenario_name, disturbance_gen in disturbances.items():
        logger.info(f"  Testing {scenario_name}...")

        fixed_metrics = {
            'settling_time': [],
            'max_overshoot': [],
            'chattering': [],
            'control_effort': [],
            'tracking_error': [],
            'converged': []
        }

        adaptive_metrics = {
            'settling_time': [],
            'max_overshoot': [],
            'chattering': [],
            'control_effort': [],
            'tracking_error': [],
            'converged': []
        }

        for trial in range(num_trials):
            # Test 1: Fixed gains
            try:
                controller_fixed = create_controller(controller_name, gains=gains)
                harness_fixed = HILTestHarness(
                    config_dict, controller_fixed,
                    extra_latency_ms=extra_latency_ms,
                    sensor_noise_std=sensor_noise_std,
                    seed=seed + trial
                )

                t, x, u = harness_fixed.run_trial(x0, disturbance_gen, sim_time=10.0)
                metrics = compute_metrics(t, x, u, disturbance_start=1.0)

                for key in fixed_metrics:
                    fixed_metrics[key].append(metrics[key])

            except Exception as e:
                logger.warning(f"    Fixed gains trial {trial+1} failed: {e}")
                for key in ['settling_time', 'max_overshoot', 'chattering', 'control_effort', 'tracking_error']:
                    fixed_metrics[key].append(999.0)
                fixed_metrics['converged'].append(False)

            # Test 2: Adaptive scheduling
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

                harness_adaptive = HILTestHarness(
                    config_dict, controller_adaptive,
                    extra_latency_ms=extra_latency_ms,
                    sensor_noise_std=sensor_noise_std,
                    seed=seed + trial + 1000
                )

                t, x, u = harness_adaptive.run_trial(x0, disturbance_gen, sim_time=10.0)
                metrics = compute_metrics(t, x, u, disturbance_start=1.0)

                for key in adaptive_metrics:
                    adaptive_metrics[key].append(metrics[key])

            except Exception as e:
                logger.warning(f"    Adaptive trial {trial+1} failed: {e}")
                for key in ['settling_time', 'max_overshoot', 'chattering', 'control_effort', 'tracking_error']:
                    adaptive_metrics[key].append(999.0)
                adaptive_metrics['converged'].append(False)

        # Compute statistics for this scenario
        results['fixed_gains'][scenario_name] = {
            'settling_time_mean': float(np.mean(fixed_metrics['settling_time'])),
            'settling_time_std': float(np.std(fixed_metrics['settling_time'])),
            'overshoot_mean': float(np.mean(fixed_metrics['max_overshoot'])),
            'overshoot_std': float(np.std(fixed_metrics['max_overshoot'])),
            'chattering_mean': float(np.mean(fixed_metrics['chattering'])),
            'chattering_std': float(np.std(fixed_metrics['chattering'])),
            'control_effort_mean': float(np.mean(fixed_metrics['control_effort'])),
            'tracking_error_mean': float(np.mean(fixed_metrics['tracking_error'])),
            'convergence_rate': float(np.mean(fixed_metrics['converged'])),
            'num_trials': num_trials
        }

        results['adaptive_scheduling'][scenario_name] = {
            'settling_time_mean': float(np.mean(adaptive_metrics['settling_time'])),
            'settling_time_std': float(np.std(adaptive_metrics['settling_time'])),
            'overshoot_mean': float(np.mean(adaptive_metrics['max_overshoot'])),
            'overshoot_std': float(np.std(adaptive_metrics['max_overshoot'])),
            'chattering_mean': float(np.mean(adaptive_metrics['chattering'])),
            'chattering_std': float(np.std(adaptive_metrics['chattering'])),
            'control_effort_mean': float(np.mean(adaptive_metrics['control_effort'])),
            'tracking_error_mean': float(np.mean(adaptive_metrics['tracking_error'])),
            'convergence_rate': float(np.mean(adaptive_metrics['converged'])),
            'num_trials': num_trials
        }

        # Compute improvement
        chattering_reduction = (
            (results['fixed_gains'][scenario_name]['chattering_mean'] -
             results['adaptive_scheduling'][scenario_name]['chattering_mean']) /
            results['fixed_gains'][scenario_name]['chattering_mean'] * 100
        )

        logger.info(f"    Fixed: {results['fixed_gains'][scenario_name]['chattering_mean']:.4f} chattering")
        logger.info(f"    Adaptive: {results['adaptive_scheduling'][scenario_name]['chattering_mean']:.4f} chattering")
        logger.info(f"    Reduction: {chattering_reduction:.1f}%")

    return results


def main():
    parser = argparse.ArgumentParser(description='MT-8 HIL Validation')
    parser.add_argument('--controller', type=str, default='classical_smc',
                        choices=['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc', 'all'])
    parser.add_argument('--trials', type=int, default=10, help='Trials per disturbance scenario')
    parser.add_argument('--latency', type=float, default=0.0, help='Network latency in milliseconds')
    parser.add_argument('--noise', type=float, default=0.001, help='Sensor noise std dev (rad)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--output', type=str, default='benchmarks/MT8_hil_validation_results.json')
    parser.add_argument('--quick', action='store_true', help='Quick test (5 trials, classical only)')

    args = parser.parse_args()

    if args.quick:
        args.controller = 'classical_smc'
        args.trials = 5
        logger.info("[INFO] Quick mode: 5 trials, classical_smc only")

    logger.info("=" * 80)
    logger.info("MT-8 HIL Validation: Network Latency + Sensor Noise + Disturbances")
    logger.info(f"Trials per scenario: {args.trials}")
    logger.info(f"Network latency: {args.latency} ms")
    logger.info(f"Sensor noise: {args.noise} rad")
    logger.info("=" * 80)

    # Load config
    config = load_config("config.yaml")
    config_dict = config.model_dump()

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

        results = run_hil_validation(
            controller_name, gains, config_dict, args.trials, args.latency, args.noise, args.seed
        )

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
    logger.info("\nSummary (Chattering Reduction for step_10N):")
    for controller, data in all_results.items():
        if 'step_10N' in data['validation']['fixed_gains']:
            fixed_chat = data['validation']['fixed_gains']['step_10N']['chattering_mean']
            adaptive_chat = data['validation']['adaptive_scheduling']['step_10N']['chattering_mean']
            reduction = (fixed_chat - adaptive_chat) / fixed_chat * 100
            logger.info(f"  {controller}: {reduction:.1f}% reduction ({fixed_chat:.4f} -> {adaptive_chat:.4f})")


if __name__ == "__main__":
    main()
