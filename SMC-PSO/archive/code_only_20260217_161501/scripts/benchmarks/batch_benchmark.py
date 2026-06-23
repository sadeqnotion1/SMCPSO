"""
================================================================================
Batch Benchmark Script - MT-5 (Comprehensive Controller Comparison)
================================================================================

Comprehensive benchmark of all existing SMC controllers using Monte Carlo
simulation. This script implements MT-5 from ROADMAP_EXISTING_PROJECT.md.

Methodology:
- 100 Monte Carlo runs per controller (varied initial conditions)
- Metrics: settling time, overshoot, energy (∫u²dt), chattering frequency
- Statistical analysis: mean, std, 95% confidence intervals
- Performance comparison matrix across all controllers

Existing Controllers (6 total):
1. Classical SMC
2. STA SMC (Super-Twisting Algorithm)
3. Adaptive SMC
4. Hybrid Adaptive-STA SMC
5. Swing-Up SMC
6. MPC Controller (if available)

Author: DIP_SMC_PSO Team
Created: October 2025 (Week 2, Task MT-5)
Reference: .ai/planning/research/ROADMAP_EXISTING_PROJECT.md
"""

import json
import csv
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
import sys
import time

# Local imports
from src.controllers.factory import create_controller, list_available_controllers
from src.core.dynamics import DIPDynamics
from src.config import load_config
from src.utils.analysis.chattering import compute_chattering_metrics
from src.core.simulation_runner import run_simulation


@dataclass
class SimulationMetrics:
    """Metrics collected from a single simulation run."""
    settling_time: float  # Time to reach within 2% of final value [s]
    overshoot: float      # Maximum overshoot percentage [%]
    energy: float         # Control energy ∫u²dt [N²·s]
    chattering_freq: float  # Dominant chattering frequency [Hz]
    chattering_amp: float   # Chattering amplitude (RMS) [N]
    success: bool         # Whether simulation succeeded (no divergence)


@dataclass
class ControllerResults:
    """Aggregated results for one controller across all runs."""
    controller_name: str
    n_runs: int
    n_success: int
    success_rate: float

    # Settling time statistics
    settling_time_mean: float
    settling_time_std: float
    settling_time_ci_lower: float
    settling_time_ci_upper: float

    # Overshoot statistics
    overshoot_mean: float
    overshoot_std: float
    overshoot_ci_lower: float
    overshoot_ci_upper: float

    # Energy statistics
    energy_mean: float
    energy_std: float
    energy_ci_lower: float
    energy_ci_upper: float

    # Chattering statistics
    chattering_freq_mean: float
    chattering_freq_std: float
    chattering_amp_mean: float
    chattering_amp_std: float


def generate_initial_conditions(n_samples: int, seed: int = 42) -> np.ndarray:
    """
    Generate random initial conditions for Monte Carlo simulation.

    State vector: [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]

    Args:
        n_samples: Number of initial condition samples to generate
        seed: Random seed for reproducibility

    Returns:
        Array of shape (n_samples, 6) with random initial conditions
    """
    rng = np.random.RandomState(seed)

    # Define variation ranges (small perturbations around equilibrium)
    x_range = (-0.05, 0.05)         # Cart position [m]
    theta1_range = (-0.05, 0.05)    # Pendulum 1 angle [rad] (~2.9 degrees)
    theta2_range = (-0.05, 0.05)    # Pendulum 2 angle [rad]
    x_dot_range = (-0.02, 0.02)     # Cart velocity [m/s]
    theta1_dot_range = (-0.05, 0.05)  # Pendulum 1 angular velocity [rad/s]
    theta2_dot_range = (-0.05, 0.05)  # Pendulum 2 angular velocity [rad/s]

    # Generate samples
    initial_conditions = np.zeros((n_samples, 6))
    initial_conditions[:, 0] = rng.uniform(*x_range, n_samples)
    initial_conditions[:, 1] = rng.uniform(*theta1_range, n_samples)
    initial_conditions[:, 2] = rng.uniform(*theta2_range, n_samples)
    initial_conditions[:, 3] = rng.uniform(*x_dot_range, n_samples)
    initial_conditions[:, 4] = rng.uniform(*theta1_dot_range, n_samples)
    initial_conditions[:, 5] = rng.uniform(*theta2_dot_range, n_samples)

    return initial_conditions


def run_single_simulation(
    controller,
    dynamics: DIPDynamics,
    initial_state: np.ndarray,
    sim_time: float = 10.0,
    dt: float = 0.01
) -> SimulationMetrics:
    """
    Run a single simulation with given controller and initial state.

    Args:
        controller: Controller instance
        dynamics: Dynamics model
        initial_state: Initial state vector [6]
        sim_time: Simulation duration [s]
        dt: Time step [s]

    Returns:
        SimulationMetrics with computed metrics
    """
    # Use the existing run_simulation function
    try:
        t_arr, x_arr, u_arr = run_simulation(
            controller=controller,
            dynamics_model=dynamics,
            sim_time=sim_time,
            dt=dt,
            initial_state=initial_state,
            u_max=150.0  # Max force from config
        )
        success = True
    except Exception as e:
        print(f"   [WARN] Simulation failed: {e}")
        success = False

    # Compute metrics if simulation succeeded
    if success and len(x_arr) > 10:  # Need at least some data points
        # Extract state components
        theta1_history = x_arr[:, 1]  # State component 1: theta1
        theta2_history = x_arr[:, 2]  # State component 2: theta2
        control_history = u_arr       # Control trajectory

        # Settling time (2% criterion for both pendulums)
        settling_threshold = 0.02  # 2% of initial angle (approx 1.15 degrees)
        settling_idx = len(theta1_history) - 1  # Default to end
        for i in range(len(theta1_history)):
            if (np.abs(theta1_history[i]) < settling_threshold and
                np.abs(theta2_history[i]) < settling_threshold):
                # Check if it stays within bounds for next 100 steps
                end_idx = min(i + 100, len(theta1_history))
                if (np.all(np.abs(theta1_history[i:end_idx]) < settling_threshold) and
                    np.all(np.abs(theta2_history[i:end_idx]) < settling_threshold)):
                    settling_idx = i
                    break
        settling_time = settling_idx * dt

        # Overshoot (maximum deviation from equilibrium)
        max_theta1 = np.max(np.abs(theta1_history))
        max_theta2 = np.max(np.abs(theta2_history))
        initial_angle = max(np.abs(initial_state[1]), np.abs(initial_state[2]))
        if initial_angle > 1e-6:  # Avoid division by zero
            overshoot = ((max(max_theta1, max_theta2) - initial_angle) / initial_angle) * 100.0
        else:
            overshoot = 0.0

        # Energy (∫u²dt)
        energy = np.sum(control_history**2) * dt

        # Chattering metrics using FFT analysis
        try:
            chattering = compute_chattering_metrics(
                control_history,
                dt,
                freq_min=10.0,
                freq_max=500.0
            )
            chattering_freq = chattering.get('peak_frequency', 0.0) or 0.0
            chattering_amp = chattering.get('chattering_index', 0.0) or 0.0
        except Exception as e:
            print(f"   [WARN] Chattering analysis failed: {e}")
            chattering_freq = 0.0
            chattering_amp = 0.0

    else:
        # Failed simulation - use sentinel values
        settling_time = sim_time
        overshoot = 100.0  # Maximum overshoot
        energy = 1e6       # High energy penalty
        chattering_freq = 0.0
        chattering_amp = 0.0

    return SimulationMetrics(
        settling_time=settling_time,
        overshoot=overshoot,
        energy=energy,
        chattering_freq=chattering_freq,
        chattering_amp=chattering_amp,
        success=success
    )


def compute_statistics(metrics: List[SimulationMetrics]) -> Dict[str, float]:
    """
    Compute statistical summary from list of metrics.

    Args:
        metrics: List of SimulationMetrics from multiple runs

    Returns:
        Dictionary with mean, std, and 95% confidence intervals
    """
    # Filter successful runs only
    successful_metrics = [m for m in metrics if m.success]
    n_success = len(successful_metrics)

    if n_success == 0:
        # All runs failed - return sentinel values
        return {
            'n_success': 0,
            'success_rate': 0.0,
            'settling_time_mean': 1e6,
            'settling_time_std': 0.0,
            'settling_time_ci_lower': 1e6,
            'settling_time_ci_upper': 1e6,
            'overshoot_mean': 100.0,
            'overshoot_std': 0.0,
            'overshoot_ci_lower': 100.0,
            'overshoot_ci_upper': 100.0,
            'energy_mean': 1e6,
            'energy_std': 0.0,
            'energy_ci_lower': 1e6,
            'energy_ci_upper': 1e6,
            'chattering_freq_mean': 0.0,
            'chattering_freq_std': 0.0,
            'chattering_amp_mean': 0.0,
            'chattering_amp_std': 0.0
        }

    # Extract arrays for successful runs
    settling_times = np.array([m.settling_time for m in successful_metrics])
    overshoots = np.array([m.overshoot for m in successful_metrics])
    energies = np.array([m.energy for m in successful_metrics])
    chattering_freqs = np.array([m.chattering_freq for m in successful_metrics])
    chattering_amps = np.array([m.chattering_amp for m in successful_metrics])

    # Compute statistics
    def stats_with_ci(data: np.ndarray) -> Tuple[float, float, float, float]:
        """Compute mean, std, and 95% CI."""
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        n = len(data)
        # 95% confidence interval (t-distribution, approximate with normal for n>30)
        ci_delta = 1.96 * std / np.sqrt(n)
        return mean, std, mean - ci_delta, mean + ci_delta

    settling_mean, settling_std, settling_ci_l, settling_ci_u = stats_with_ci(settling_times)
    overshoot_mean, overshoot_std, overshoot_ci_l, overshoot_ci_u = stats_with_ci(overshoots)
    energy_mean, energy_std, energy_ci_l, energy_ci_u = stats_with_ci(energies)
    chattering_freq_mean, chattering_freq_std, _, _ = stats_with_ci(chattering_freqs)
    chattering_amp_mean, chattering_amp_std, _, _ = stats_with_ci(chattering_amps)

    return {
        'n_success': n_success,
        'success_rate': n_success / len(metrics),
        'settling_time_mean': settling_mean,
        'settling_time_std': settling_std,
        'settling_time_ci_lower': settling_ci_l,
        'settling_time_ci_upper': settling_ci_u,
        'overshoot_mean': overshoot_mean,
        'overshoot_std': overshoot_std,
        'overshoot_ci_lower': overshoot_ci_l,
        'overshoot_ci_upper': overshoot_ci_u,
        'energy_mean': energy_mean,
        'energy_std': energy_std,
        'energy_ci_lower': energy_ci_l,
        'energy_ci_upper': energy_ci_u,
        'chattering_freq_mean': chattering_freq_mean,
        'chattering_freq_std': chattering_freq_std,
        'chattering_amp_mean': chattering_amp_mean,
        'chattering_amp_std': chattering_amp_std
    }


def benchmark_controller(
    controller_name: str,
    config: Any,
    dynamics: DIPDynamics,
    initial_conditions: np.ndarray,
    n_runs: int = 100
) -> ControllerResults:
    """
    Benchmark a single controller across multiple initial conditions.

    Args:
        controller_name: Name of controller to benchmark
        config: Configuration object
        dynamics: Dynamics model
        initial_conditions: Array of initial states (n_runs, 6)
        n_runs: Number of Monte Carlo runs

    Returns:
        ControllerResults with aggregated statistics
    """
    print(f"\n[BENCH] Benchmarking {controller_name}...")

    # Create controller
    try:
        controller = create_controller(controller_name, config)
    except Exception as e:
        print(f"   [FAIL] Could not create controller: {e}")
        # Return failed results
        return ControllerResults(
            controller_name=controller_name,
            n_runs=n_runs,
            n_success=0,
            success_rate=0.0,
            settling_time_mean=1e6, settling_time_std=0.0,
            settling_time_ci_lower=1e6, settling_time_ci_upper=1e6,
            overshoot_mean=100.0, overshoot_std=0.0,
            overshoot_ci_lower=100.0, overshoot_ci_upper=100.0,
            energy_mean=1e6, energy_std=0.0,
            energy_ci_lower=1e6, energy_ci_upper=1e6,
            chattering_freq_mean=0.0, chattering_freq_std=0.0,
            chattering_amp_mean=0.0, chattering_amp_std=0.0
        )

    # Run simulations
    metrics = []
    start_time = time.time()

    for i in range(n_runs):
        if (i + 1) % 10 == 0:
            print(f"   Run {i+1}/{n_runs}...")

        # Reset controller for each run
        if hasattr(controller, 'reset'):
            controller.reset()

        # Run simulation
        metric = run_single_simulation(
            controller,
            dynamics,
            initial_conditions[i],
            sim_time=10.0,
            dt=0.01
        )
        metrics.append(metric)

    elapsed = time.time() - start_time
    print(f"   [OK] Completed {n_runs} runs in {elapsed:.1f}s")

    # Compute statistics
    stats = compute_statistics(metrics)

    # Create results object
    results = ControllerResults(
        controller_name=controller_name,
        n_runs=n_runs,
        n_success=stats['n_success'],
        success_rate=stats['success_rate'],
        settling_time_mean=stats['settling_time_mean'],
        settling_time_std=stats['settling_time_std'],
        settling_time_ci_lower=stats['settling_time_ci_lower'],
        settling_time_ci_upper=stats['settling_time_ci_upper'],
        overshoot_mean=stats['overshoot_mean'],
        overshoot_std=stats['overshoot_std'],
        overshoot_ci_lower=stats['overshoot_ci_lower'],
        overshoot_ci_upper=stats['overshoot_ci_upper'],
        energy_mean=stats['energy_mean'],
        energy_std=stats['energy_std'],
        energy_ci_lower=stats['energy_ci_lower'],
        energy_ci_upper=stats['energy_ci_upper'],
        chattering_freq_mean=stats['chattering_freq_mean'],
        chattering_freq_std=stats['chattering_freq_std'],
        chattering_amp_mean=stats['chattering_amp_mean'],
        chattering_amp_std=stats['chattering_amp_std']
    )

    print(f"   Success rate: {results.success_rate*100:.1f}%")
    print(f"   Settling time: {results.settling_time_mean:.3f} +/- {results.settling_time_std:.3f}s")
    print(f"   Overshoot: {results.overshoot_mean:.2f} +/- {results.overshoot_std:.2f}%")
    print(f"   Energy: {results.energy_mean:.2f} +/- {results.energy_std:.2f} N^2·s")

    return results


def save_results(results: List[ControllerResults], output_dir: str = "benchmarks"):
    """
    Save benchmark results to CSV and JSON files.

    Args:
        results: List of ControllerResults
        output_dir: Output directory for results
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save CSV (performance matrix)
    csv_path = output_path / "comprehensive_benchmark.csv"
    with open(csv_path, 'w', newline='') as f:
        # Define columns (must match ControllerResults dataclass fields)
        fieldnames = [
            'controller_name', 'n_runs', 'n_success', 'success_rate',
            'settling_time_mean', 'settling_time_std', 'settling_time_ci_lower', 'settling_time_ci_upper',
            'overshoot_mean', 'overshoot_std', 'overshoot_ci_lower', 'overshoot_ci_upper',
            'energy_mean', 'energy_std', 'energy_ci_lower', 'energy_ci_upper',
            'chattering_freq_mean', 'chattering_freq_std',
            'chattering_amp_mean', 'chattering_amp_std'
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            writer.writerow(asdict(result))

    print(f"\n[OK] CSV saved to: {csv_path}")

    # Save JSON (full results with metadata)
    json_path = output_path / "comprehensive_benchmark.json"
    results_dict = {
        'metadata': {
            'script': 'scripts/batch_benchmark.py',
            'task': 'MT-5 Comprehensive Benchmark',
            'date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'n_controllers': len(results),
            'n_runs_per_controller': results[0].n_runs if results else 0
        },
        'results': [asdict(r) for r in results]
    }

    with open(json_path, 'w') as f:
        json.dump(results_dict, f, indent=2)

    print(f"[OK] JSON saved to: {json_path}")


def main():
    """Main execution: batch benchmark all existing controllers."""
    print("=" * 80)
    print("MT-5: Comprehensive Controller Benchmark")
    print("=" * 80)

    # Load configuration
    print("\n[1/5] Loading configuration...")
    config = load_config("config.yaml")
    print("   [OK] Configuration loaded")

    # Create dynamics model
    print("\n[2/5] Creating dynamics model...")
    dynamics = DIPDynamics(config.physics)
    print("   [OK] Dynamics model created")

    # Generate initial conditions
    print("\n[3/5] Generating initial conditions...")
    n_runs = 100
    initial_conditions = generate_initial_conditions(n_runs, seed=42)
    print(f"   [OK] Generated {n_runs} initial condition samples")

    # Get available controllers (exclude TSMC - it's new work from MT-1)
    available_controllers = list_available_controllers()
    existing_controllers = [c for c in available_controllers if c != 'tsmc_smc']

    print(f"\n[4/5] Running benchmarks for {len(existing_controllers)} controllers...")
    print(f"   Controllers: {', '.join(existing_controllers)}")

    # Benchmark each controller
    results = []
    for controller_name in existing_controllers:
        result = benchmark_controller(
            controller_name,
            config,
            dynamics,
            initial_conditions,
            n_runs=n_runs
        )
        results.append(result)

    # Save results
    print("\n[5/5] Saving results...")
    save_results(results, output_dir="benchmarks")

    print("\n" + "=" * 80)
    print("[SUCCESS] MT-5 Comprehensive Benchmark Complete!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Review: cat benchmarks/comprehensive_benchmark.csv")
    print("2. Analyze: python scripts/analyze_benchmark_results.py")
    print("3. Update: docs/tutorials/02-controller-comparison.md")
    print("4. Continue with MT-6 (Boundary Layer Optimization)")


if __name__ == "__main__":
    main()
