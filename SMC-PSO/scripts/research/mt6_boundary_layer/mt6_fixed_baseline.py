"""
================================================================================
MT-6 Fixed Boundary Layer Baseline Benchmark
================================================================================

Establishes performance baseline for Classical SMC with FIXED boundary layer.
This script collects comprehensive metrics for 100 Monte Carlo simulations
with fixed boundary layer parameters (ε=0.02, slope=0.0).

Task: MT-6 Agent A - Fixed Boundary Layer Baseline
Reference: ROADMAP_EXISTING_PROJECT.md

Methodology:
- 100 Monte Carlo runs with random initial conditions
- Fixed boundary layer: ε=0.02, slope=0.0 (no adaptation)
- Metrics: chattering index, settling time, overshoot, control energy, RMS control
- Statistical analysis: mean, std, 95% CI
- Results saved to: benchmarks/MT6_fixed_baseline.csv

Author: Agent A
Created: October 18, 2025
"""

import json
import csv
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
import sys
import time
from scipy import stats

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Local imports
from src.controllers.factory import create_controller
from src.core.dynamics import DIPDynamics
from src.config import load_config
from src.core.simulation_runner import run_simulation


@dataclass
class MT6Metrics:
    """Metrics collected from a single MT-6 simulation run."""
    run_id: int
    chattering_index: float      # Chattering index from BoundaryLayer.get_chattering_index()
    settling_time: float          # Time to |θ1|, |θ2| < 0.05 rad [s]
    overshoot_theta1: float       # Max |θ1| during transient [rad]
    overshoot_theta2: float       # Max |θ2| during transient [rad]
    control_energy: float         # ∫u²dt [N²·s]
    rms_control: float            # RMS control effort [N]
    success: bool                 # Whether simulation succeeded


def generate_initial_conditions_mt6(n_samples: int, seed: int = 42) -> np.ndarray:
    """
    Generate random initial conditions for MT-6 Monte Carlo simulation.

    State vector: [x, theta1, theta2, x_dot, theta1_dot, theta2_dot]

    Ranges:
    - θ1, θ2 ∈ [-0.3, 0.3] rad (~17 degrees)
    - velocities ∈ [-0.5, 0.5] rad/s or m/s
    - cart position starts at x=0

    Args:
        n_samples: Number of initial condition samples
        seed: Random seed for reproducibility (42 per instructions)

    Returns:
        Array of shape (n_samples, 6) with random initial conditions
    """
    rng = np.random.RandomState(seed)

    initial_conditions = np.zeros((n_samples, 6))
    initial_conditions[:, 0] = 0.0  # Cart starts at origin
    initial_conditions[:, 1] = rng.uniform(-0.3, 0.3, n_samples)  # theta1
    initial_conditions[:, 2] = rng.uniform(-0.3, 0.3, n_samples)  # theta2
    initial_conditions[:, 3] = rng.uniform(-0.5, 0.5, n_samples)  # x_dot
    initial_conditions[:, 4] = rng.uniform(-0.5, 0.5, n_samples)  # theta1_dot
    initial_conditions[:, 5] = rng.uniform(-0.5, 0.5, n_samples)  # theta2_dot

    return initial_conditions


def run_mt6_simulation(
    controller,
    dynamics: DIPDynamics,
    initial_state: np.ndarray,
    run_id: int,
    sim_time: float = 10.0,
    dt: float = 0.01
) -> MT6Metrics:
    """
    Run a single MT-6 simulation with fixed boundary layer.

    Args:
        controller: Classical SMC controller instance
        dynamics: Dynamics model
        initial_state: Initial state vector [6]
        run_id: Run identifier
        sim_time: Simulation duration [s] (10s per instructions)
        dt: Time step [s] (0.01s per instructions)

    Returns:
        MT6Metrics with computed metrics
    """
    try:
        # Use direct simulation loop instead of run_simulation
        # (run_simulation has integration issues with the controller)
        n_steps = int(sim_time / dt)
        t_arr = np.zeros(n_steps + 1)
        x_arr = np.zeros((n_steps + 1, 6))
        u_arr = np.zeros(n_steps)

        # Initial conditions
        x_arr[0] = initial_state
        t_arr[0] = 0.0

        # Initialize controller state
        ctrl_state = None
        history = {}
        if hasattr(controller, 'initialize_state'):
            ctrl_state = controller.initialize_state()
        if hasattr(controller, 'initialize_history'):
            history = controller.initialize_history()

        # Simulation loop
        for i in range(n_steps):
            t = i * dt
            x = x_arr[i]

            # Compute control
            if hasattr(controller, 'compute_control'):
                result = controller.compute_control(x, ctrl_state, history)
                if isinstance(result, dict):
                    u = result.get('u', 0.0)
                else:
                    u = float(result)
            elif hasattr(controller, '__call__'):
                u = controller(t, x)
            else:
                raise RuntimeError(f"Controller {type(controller).__name__} has no compute_control or __call__ method")

            # Saturate control
            u = np.clip(u, -150.0, 150.0)
            u_arr[i] = u

            # Step dynamics
            x_next = dynamics.step(x, u, dt)
            x_arr[i + 1] = x_next
            t_arr[i + 1] = (i + 1) * dt

            # Check for NaN/Inf
            if not np.all(np.isfinite(x_next)):
                print(f"   [WARN] Run {run_id} diverged at step {i}")
                # Truncate arrays
                t_arr = t_arr[:i+2]
                x_arr = x_arr[:i+2]
                u_arr = u_arr[:i+1]
                break

        success = True

        # Debug first run
        if run_id == 1:
            print(f"   [DEBUG] Completed {len(u_arr)} steps")
            print(f"   [DEBUG] Control stats: min={np.min(u_arr):.4f}, max={np.max(u_arr):.4f}, mean={np.mean(u_arr):.4f}")

    except Exception as e:
        print(f"   [WARN] Run {run_id} failed: {e}")
        import traceback
        traceback.print_exc()
        return MT6Metrics(
            run_id=run_id,
            chattering_index=np.nan,
            settling_time=np.nan,
            overshoot_theta1=np.nan,
            overshoot_theta2=np.nan,
            control_energy=np.nan,
            rms_control=np.nan,
            success=False
        )

    # Extract state components
    theta1_history = x_arr[:, 1]
    theta2_history = x_arr[:, 2]
    control_history = u_arr

    # 1. Chattering Index (using BoundaryLayer.get_chattering_index method)
    from src.controllers.smc.algorithms.classical.boundary_layer import BoundaryLayer
    boundary_layer = BoundaryLayer(thickness=0.02, slope=0.0)  # Fixed params
    chattering_index = boundary_layer.get_chattering_index(control_history, dt)

    # 2. Settling Time (when |θ1|, |θ2| < 0.05 rad and stays there)
    settling_threshold = 0.05  # 0.05 rad (~2.9 degrees)
    settling_time = sim_time  # Default to max if never settles
    for i in range(len(theta1_history)):
        if (np.abs(theta1_history[i]) < settling_threshold and
            np.abs(theta2_history[i]) < settling_threshold):
            # Check if it stays within bounds for next 50 steps (0.5s)
            end_idx = min(i + 50, len(theta1_history))
            if (np.all(np.abs(theta1_history[i:end_idx]) < settling_threshold) and
                np.all(np.abs(theta2_history[i:end_idx]) < settling_threshold)):
                settling_time = i * dt
                break

    # 3. Overshoot (max |θ1|, |θ2| during entire trajectory)
    overshoot_theta1 = np.max(np.abs(theta1_history))
    overshoot_theta2 = np.max(np.abs(theta2_history))

    # 4. Control Energy (∫u²dt)
    control_energy = np.sum(control_history**2) * dt

    # 5. RMS Control Effort
    rms_control = np.sqrt(np.mean(control_history**2))

    return MT6Metrics(
        run_id=run_id,
        chattering_index=chattering_index,
        settling_time=settling_time,
        overshoot_theta1=overshoot_theta1,
        overshoot_theta2=overshoot_theta2,
        control_energy=control_energy,
        rms_control=rms_control,
        success=success
    )


def compute_statistics(data: List[float]) -> Dict[str, float]:
    """
    Compute summary statistics with 95% confidence intervals.

    Args:
        data: List of metric values

    Returns:
        Dictionary with mean, std, 95% CI
    """
    if not data or len(data) == 0:
        return {'mean': np.nan, 'std': np.nan, 'ci_lower': np.nan, 'ci_upper': np.nan}

    data_clean = [x for x in data if np.isfinite(x)]
    if len(data_clean) == 0:
        return {'mean': np.nan, 'std': np.nan, 'ci_lower': np.nan, 'ci_upper': np.nan}

    mean = np.mean(data_clean)
    std = np.std(data_clean, ddof=1)  # Sample std

    # 95% confidence interval (using t-distribution)
    n = len(data_clean)
    if n > 1:
        sem = stats.sem(data_clean)  # Standard error of mean
        ci = stats.t.interval(0.95, n-1, loc=mean, scale=sem)
        ci_lower, ci_upper = ci
    else:
        ci_lower = ci_upper = mean

    return {
        'mean': float(mean),
        'std': float(std),
        'ci_lower': float(ci_lower),
        'ci_upper': float(ci_upper)
    }


def main():
    """Main execution for MT-6 Fixed Boundary Layer Baseline."""
    print("=" * 80)
    print("MT-6 Fixed Boundary Layer Baseline Benchmark")
    print("=" * 80)
    print()

    # Configuration
    n_runs = 100
    seed = 42
    sim_time = 10.0
    dt = 0.01

    # Fixed boundary layer parameters (critical for MT-6)
    boundary_layer_thickness = 0.02
    boundary_layer_slope = 0.0  # No adaptation

    print(f"Configuration:")
    print(f"  Runs: {n_runs}")
    print(f"  Random seed: {seed}")
    print(f"  Simulation time: {sim_time}s")
    print(f"  Time step: {dt}s")
    print(f"  Boundary layer thickness (epsilon): {boundary_layer_thickness}")
    print(f"  Boundary layer slope (alpha): {boundary_layer_slope} (FIXED)")
    print()

    # Load configuration (allow unknown keys for streamlit config)
    config = load_config("D:/Projects/main/config.yaml", allow_unknown=True)

    # Create dynamics model
    dynamics = DIPDynamics(config.physics)
    print(f"Dynamics: {dynamics.__class__.__name__}")

    # Create Classical SMC controller with FIXED boundary layer
    # Note: We override the config boundary layer with our fixed parameters
    from src.controllers.smc.algorithms.classical.controller import ClassicalSMC
    from src.controllers.smc.algorithms.classical.config import ClassicalSMCConfig

    # Get default gains from config
    default_gains = list(config.controller_defaults.classical_smc.gains)

    # Create controller with fixed boundary layer
    controller = ClassicalSMC(
        gains=default_gains,
        max_force=150.0,
        boundary_layer=boundary_layer_thickness,  # FIXED: 0.02
        dynamics_model=dynamics,
        dt=dt,
        boundary_layer_slope=boundary_layer_slope  # FIXED: 0.0 (no adaptation)
    )
    print(f"Controller: Classical SMC (Fixed Boundary Layer)")
    print()

    # Generate initial conditions
    print("Generating initial conditions...")
    initial_conditions = generate_initial_conditions_mt6(n_runs, seed)
    print(f"Generated {n_runs} initial conditions (theta in [-0.3, 0.3] rad, vel in [-0.5, 0.5])")
    print()

    # Run Monte Carlo simulations
    print("Running Monte Carlo simulations...")
    start_time = time.time()
    results: List[MT6Metrics] = []

    for i in range(n_runs):
        if (i + 1) % 10 == 0:
            elapsed = time.time() - start_time
            eta = (elapsed / (i + 1)) * (n_runs - i - 1)
            print(f"  Progress: {i+1}/{n_runs} ({100*(i+1)/n_runs:.1f}%) | "
                  f"Elapsed: {elapsed:.1f}s | ETA: {eta:.1f}s")

        initial_state = initial_conditions[i]
        metrics = run_mt6_simulation(
            controller, dynamics, initial_state, run_id=i+1,
            sim_time=sim_time, dt=dt
        )
        results.append(metrics)

    elapsed_total = time.time() - start_time
    print(f"\nCompleted {n_runs} runs in {elapsed_total:.1f}s ({elapsed_total/n_runs:.2f}s per run)")
    print()

    # Filter successful runs
    successful_results = [r for r in results if r.success]
    n_success = len(successful_results)
    success_rate = 100.0 * n_success / n_runs

    print(f"Success rate: {n_success}/{n_runs} ({success_rate:.1f}%)")
    print()

    # Compute summary statistics
    print("Computing summary statistics...")
    chattering_stats = compute_statistics([r.chattering_index for r in successful_results])
    settling_stats = compute_statistics([r.settling_time for r in successful_results])
    overshoot1_stats = compute_statistics([r.overshoot_theta1 for r in successful_results])
    overshoot2_stats = compute_statistics([r.overshoot_theta2 for r in successful_results])
    energy_stats = compute_statistics([r.control_energy for r in successful_results])
    rms_stats = compute_statistics([r.rms_control for r in successful_results])

    # Print summary table
    print()
    print("=" * 80)
    print("SUMMARY STATISTICS (N={} successful runs)".format(n_success))
    print("=" * 80)
    print()
    print(f"{'Metric':<25} {'Mean':<12} {'Std':<12} {'95% CI':<25}")
    print("-" * 80)
    print(f"{'Chattering Index':<25} "
          f"{chattering_stats['mean']:<12.4f} "
          f"{chattering_stats['std']:<12.4f} "
          f"[{chattering_stats['ci_lower']:.4f}, {chattering_stats['ci_upper']:.4f}]")
    print(f"{'Settling Time [s]':<25} "
          f"{settling_stats['mean']:<12.4f} "
          f"{settling_stats['std']:<12.4f} "
          f"[{settling_stats['ci_lower']:.4f}, {settling_stats['ci_upper']:.4f}]")
    print(f"{'Overshoot theta1 [rad]':<25} "
          f"{overshoot1_stats['mean']:<12.4f} "
          f"{overshoot1_stats['std']:<12.4f} "
          f"[{overshoot1_stats['ci_lower']:.4f}, {overshoot1_stats['ci_upper']:.4f}]")
    print(f"{'Overshoot theta2 [rad]':<25} "
          f"{overshoot2_stats['mean']:<12.4f} "
          f"{overshoot2_stats['std']:<12.4f} "
          f"[{overshoot2_stats['ci_lower']:.4f}, {overshoot2_stats['ci_upper']:.4f}]")
    print(f"{'Control Energy [N^2*s]':<25} "
          f"{energy_stats['mean']:<12.4f} "
          f"{energy_stats['std']:<12.4f} "
          f"[{energy_stats['ci_lower']:.4f}, {energy_stats['ci_upper']:.4f}]")
    print(f"{'RMS Control [N]':<25} "
          f"{rms_stats['mean']:<12.4f} "
          f"{rms_stats['std']:<12.4f} "
          f"[{rms_stats['ci_lower']:.4f}, {rms_stats['ci_upper']:.4f}]")
    print("=" * 80)
    print()

    # Save results to CSV
    output_dir = Path("D:/Projects/main/benchmarks")
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "MT6_fixed_baseline.csv"

    print(f"Saving results to: {csv_path}")
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['run_id', 'chattering_index', 'settling_time',
                     'overshoot_theta1', 'overshoot_theta2',
                     'control_energy', 'rms_control', 'success']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(asdict(result))

    print(f"[OK] Saved {len(results)} results to CSV")
    print()

    # Save summary statistics to JSON
    summary_path = output_dir / "MT6_fixed_baseline_summary.json"
    summary_data = {
        'configuration': {
            'n_runs': n_runs,
            'n_success': n_success,
            'success_rate': success_rate,
            'seed': seed,
            'sim_time': sim_time,
            'dt': dt,
            'boundary_layer_thickness': boundary_layer_thickness,
            'boundary_layer_slope': boundary_layer_slope
        },
        'statistics': {
            'chattering_index': chattering_stats,
            'settling_time': settling_stats,
            'overshoot_theta1': overshoot1_stats,
            'overshoot_theta2': overshoot2_stats,
            'control_energy': energy_stats,
            'rms_control': rms_stats
        }
    }

    with open(summary_path, 'w') as f:
        json.dump(summary_data, f, indent=2)

    print(f"[OK] Saved summary statistics to: {summary_path}")
    print()
    print("=" * 80)
    print("MT-6 Fixed Baseline Benchmark Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
