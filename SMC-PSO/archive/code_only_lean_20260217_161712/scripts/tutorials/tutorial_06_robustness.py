"""
Tutorial 06: Robustness Analysis Workflow
==========================================

Executable code examples for Tutorial 06.

This script demonstrates:
1. Disturbance rejection testing (step, impulse, torque disturbances)
2. Parameter sweep analysis (single parameter variation)
3. Monte Carlo statistical validation (multi-parameter uncertainty)

Usage:
    python tutorial_06_robustness.py

Author: DIP-SMC-PSO Development Team
Date: November 12, 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# Add project root to path (so we can import src package)
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config

# Config file path (at project root)
CONFIG_PATH = PROJECT_ROOT / "config.yaml"
from src.controllers.factory import create_controller
from src.core.dynamics import DIPDynamics
from src.core.simulation_runner import run_simulation


# ============================================================================
# HELPER CLASS: Simulation Result Wrapper
# ============================================================================

class SimulationResult:
    """Wrapper for simulation results with calculated metrics."""
    def __init__(self, t_arr, x_arr, u_arr):
        self.time = t_arr
        self.state_history = x_arr
        self.control_history = u_arr

        # Calculate metrics
        # State order: [x, x_dot, theta1, theta1_dot, theta2, theta2_dot]
        theta1 = x_arr[:, 2]
        self.max_theta1 = np.max(np.abs(theta1))

        # Simple settling time: when theta1 stays within 2% of zero
        threshold = 0.02
        settled = np.abs(theta1) < threshold
        settled_idx = np.where(settled)[0]
        self.settling_time = t_arr[settled_idx[0]] if len(settled_idx) > 0 else t_arr[-1]

        # Check convergence: no NaN/Inf and final state close to equilibrium
        self.converged = (
            not np.any(np.isnan(x_arr)) and
            not np.any(np.isinf(x_arr)) and
            np.abs(theta1[-1]) < 0.1
        )


# ============================================================================
# SECTION 1: DISTURBANCE FUNCTIONS
# ============================================================================

def step_disturbance(t, state, params):
    """
    Apply step disturbance to cart (horizontal force).

    Parameters
    ----------
    t : float
        Current simulation time (seconds)
    state : ndarray
        Current system state [x, x_dot, theta1, theta2, theta1_dot, theta2_dot]
    params : dict
        Disturbance parameters (magnitude, start_time, duration)

    Returns
    -------
    disturbance : ndarray
        Disturbance forces [F_cart, tau_theta1, tau_theta2, 0, 0, 0]
    """
    magnitude = params.get('magnitude', 50.0)
    start_time = params.get('start_time', 2.0)
    duration = params.get('duration', 0.5)

    if start_time <= t < (start_time + duration):
        disturbance = np.array([magnitude, 0.0, 0.0, 0.0, 0.0, 0.0])
    else:
        disturbance = np.zeros(6)

    return disturbance


# ============================================================================
# SECTION 2: PARAMETER SWEEP ANALYSIS
# ============================================================================

def parameter_sweep(controller_type='classical_smc',
                    param_name='cart_mass',
                    variation_range=None,
                    plot=True):
    """
    Sweep single parameter and measure performance degradation.

    Parameters
    ----------
    controller_type : str
        Controller to test
    param_name : str
        Parameter to vary ('cart_mass', 'link1_length', etc.)
    variation_range : ndarray or None
        Scaling factors (1.0 = nominal, 0.8 = -20%, 1.2 = +20%)
    plot : bool
        Whether to plot results

    Returns
    -------
    results : dict
        Performance metrics for each parameter value
    """
    if variation_range is None:
        variation_range = np.linspace(0.8, 1.2, 9)  # ±20% in 5% steps

    config = load_config(str(CONFIG_PATH))

    # Get nominal parameter value
    nominal_value = getattr(config.physics, param_name)

    # Storage for results
    settling_times = []
    overshoots = []
    energies = []

    print(f"[INFO] Parameter Sweep: {param_name}")
    print(f"[INFO] Controller: {controller_type}")
    print(f"[INFO] Variation range: {(variation_range[0]-1)*100:.0f}% to {(variation_range[-1]-1)*100:.0f}%")

    for i, scale_factor in enumerate(variation_range):
        # Modify parameter
        setattr(config.physics, param_name, nominal_value * scale_factor)

        # Create controller and dynamics
        # Extract gains from config for the specific controller type
        controller_config = getattr(config.controllers, controller_type)
        gains = controller_config.gains if hasattr(controller_config, 'gains') and controller_config.gains else None
        controller = create_controller(controller_type, config=config, gains=gains)
        dynamics = DIPDynamics(config.physics)

        # Run simulation
        t_arr, x_arr, u_arr = run_simulation(
            controller=controller,
            dynamics_model=dynamics,
            sim_time=config.simulation.duration,
            dt=config.simulation.dt,
            initial_state=config.simulation.initial_state
        )
        result = SimulationResult(t_arr, x_arr, u_arr)

        # Record metrics
        settling_times.append(result.settling_time)
        overshoots.append(result.max_theta1)
        energies.append(np.sum(result.control_history**2) * config.simulation.dt)

        # Progress indicator
        print(f"  [{i+1}/{len(variation_range)}] Scale: {scale_factor:.2f} | "
              f"Settling: {result.settling_time:.2f}s | "
              f"Overshoot: {np.rad2deg(result.max_theta1):.2f}°")

        # Restore nominal value
        setattr(config.physics, param_name, nominal_value)

    results = {
        'variation_range': variation_range,
        'settling_times': np.array(settling_times),
        'overshoots': np.array(overshoots),
        'energies': np.array(energies)
    }

    if plot:
        plot_parameter_sweep(results, controller_type, param_name)

    return results


def plot_parameter_sweep(results, controller_type, param_name):
    """
    Plot performance metrics vs parameter variation.
    """
    fig, axes = plt.subplots(3, 1, figsize=(10, 12))

    variation_pct = (results['variation_range'] - 1.0) * 100

    # Find nominal index (closest to scale_factor=1.0)
    nominal_idx = np.argmin(np.abs(results['variation_range'] - 1.0))

    # Plot 1: Settling Time
    axes[0].plot(variation_pct, results['settling_times'], 'o-',
                 linewidth=2, markersize=8, color='steelblue')
    axes[0].axvline(0, color='k', linestyle='--', linewidth=1, label='Nominal')
    axes[0].axhspan(results['settling_times'][nominal_idx] * 0.9,
                    results['settling_times'][nominal_idx] * 1.1,
                    alpha=0.2, color='green', label='±10% Tolerance')
    axes[0].set_ylabel('Settling Time (s)', fontsize=12, fontweight='bold')
    axes[0].set_title(f'Parameter Sensitivity: {param_name} | Controller: {controller_type.upper()}',
                      fontsize=14, fontweight='bold')
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)

    # Plot 2: Overshoot
    axes[1].plot(variation_pct, np.rad2deg(results['overshoots']), 'o-',
                 linewidth=2, markersize=8, color='coral')
    axes[1].axvline(0, color='k', linestyle='--', linewidth=1)
    axes[1].axhspan(np.rad2deg(results['overshoots'][nominal_idx]) * 0.85,
                    np.rad2deg(results['overshoots'][nominal_idx]) * 1.15,
                    alpha=0.2, color='green', label='±15% Tolerance')
    axes[1].set_ylabel('Overshoot (deg)', fontsize=12, fontweight='bold')
    axes[1].legend(fontsize=10)
    axes[1].grid(True, alpha=0.3)

    # Plot 3: Control Effort
    axes[2].plot(variation_pct, results['energies'], 'o-',
                 linewidth=2, markersize=8, color='mediumseagreen')
    axes[2].axvline(0, color='k', linestyle='--', linewidth=1)
    axes[2].axhspan(results['energies'][nominal_idx] * 0.8,
                    results['energies'][nominal_idx] * 1.2,
                    alpha=0.2, color='green', label='±20% Tolerance')
    axes[2].set_ylabel('Control Effort (J)', fontsize=12, fontweight='bold')
    axes[2].set_xlabel(f'{param_name} Variation (%)', fontsize=12, fontweight='bold')
    axes[2].legend(fontsize=10)
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()

    # Save figure
    output_dir = Path(__file__).parent.parent.parent / ".artifacts" / "tutorial_06"
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"parameter_sweep_{controller_type}_{param_name}.png"
    fig.savefig(output_dir / filename, dpi=300, bbox_inches='tight')
    print(f"[OK] Saved: {output_dir / filename}")

    plt.show()


# ============================================================================
# SECTION 3: MONTE CARLO ROBUSTNESS ANALYSIS
# ============================================================================

def monte_carlo_robustness(controller_type='classical_smc',
                           n_runs=100,
                           uncertainty_level='moderate',
                           seed=42,
                           plot=True):
    """
    Monte Carlo robustness analysis with parameter uncertainty.

    Parameters
    ----------
    controller_type : str
        Controller to test
    n_runs : int
        Number of Monte Carlo samples (100 minimum, 1000 for publication)
    uncertainty_level : str
        Uncertainty level ('low', 'moderate', 'high')
        - low: ±5% uniform
        - moderate: ±10% uniform
        - high: ±20% uniform
    seed : int
        Random seed for reproducibility
    plot : bool
        Whether to plot results

    Returns
    -------
    statistics : dict
        Performance statistics (mean, std, percentiles, CI)
    data : tuple
        Raw data arrays (settling_times, overshoots, energies)
    """
    np.random.seed(seed)

    # Define uncertainty ranges
    uncertainty_ranges = {
        'low': 0.05,
        'moderate': 0.10,
        'high': 0.20
    }
    uncertainty = uncertainty_ranges[uncertainty_level]

    config = load_config(str(CONFIG_PATH))

    # Parameters to vary (most influential)
    param_names = ['cart_mass', 'link1_length', 'link1_mass',
                   'link2_length', 'link2_mass']
    nominal_values = {name: getattr(config.physics, name) for name in param_names}

    # Storage for results
    settling_times = []
    overshoots = []
    energies = []
    converged_count = 0

    print(f"\n[INFO] Monte Carlo Robustness Analysis")
    print(f"[INFO] Controller: {controller_type}")
    print(f"[INFO] Runs: {n_runs}")
    print(f"[INFO] Uncertainty: {uncertainty_level} (±{uncertainty*100:.0f}%)")
    print(f"[INFO] Parameters varied: {', '.join(param_names)}")
    print(f"[INFO] Starting simulation...")

    # Extract gains from config once (outside loop for efficiency)
    controller_config = getattr(config.controllers, controller_type)
    gains = controller_config.gains if hasattr(controller_config, 'gains') and controller_config.gains else None

    for run in range(n_runs):
        # Sample parameters from uniform distribution
        for param_name in param_names:
            nominal = nominal_values[param_name]
            scale_factor = 1.0 + np.random.uniform(-uncertainty, uncertainty)
            setattr(config.physics, param_name, nominal * scale_factor)

        # Create controller and dynamics
        controller = create_controller(controller_type, config=config, gains=gains)
        dynamics = DIPDynamics(config.physics)

        # Run simulation
        t_arr, x_arr, u_arr = run_simulation(
            controller=controller,
            dynamics_model=dynamics,
            sim_time=config.simulation.duration,
            dt=config.simulation.dt,
            initial_state=config.simulation.initial_state
        )
        result = SimulationResult(t_arr, x_arr, u_arr)

        # Check convergence
        if result.converged:
            settling_times.append(result.settling_time)
            overshoots.append(result.max_theta1)
            energies.append(np.sum(result.control_history**2) * config.simulation.dt)
            converged_count += 1

        # Progress indicator
        if (run + 1) % 20 == 0:
            print(f"  Progress: {run+1}/{n_runs} ({(run+1)/n_runs*100:.0f}%) | "
                  f"Converged: {converged_count}/{run+1} ({converged_count/(run+1)*100:.1f}%)")

        # Restore nominal values
        for param_name in param_names:
            setattr(config.physics, param_name, nominal_values[param_name])

    # Convert to numpy arrays
    settling_times = np.array(settling_times)
    overshoots = np.array(overshoots)
    energies = np.array(energies)

    # Compute statistics
    statistics = {
        'n_runs': n_runs,
        'converged_count': converged_count,
        'convergence_rate': converged_count / n_runs * 100,
        'settling_time': {
            'mean': np.mean(settling_times),
            'std': np.std(settling_times),
            'min': np.min(settling_times),
            'max': np.max(settling_times),
            'p5': np.percentile(settling_times, 5),
            'p50': np.percentile(settling_times, 50),  # median
            'p95': np.percentile(settling_times, 95),
            'ci_95': (np.percentile(settling_times, 2.5),
                     np.percentile(settling_times, 97.5))
        },
        'overshoot': {
            'mean': np.mean(overshoots),
            'std': np.std(overshoots),
            'min': np.min(overshoots),
            'max': np.max(overshoots),
            'p5': np.percentile(overshoots, 5),
            'p50': np.percentile(overshoots, 50),
            'p95': np.percentile(overshoots, 95),
            'ci_95': (np.percentile(overshoots, 2.5),
                     np.percentile(overshoots, 97.5))
        },
        'energy': {
            'mean': np.mean(energies),
            'std': np.std(energies),
            'min': np.min(energies),
            'max': np.max(energies),
            'p5': np.percentile(energies, 5),
            'p50': np.percentile(energies, 50),
            'p95': np.percentile(energies, 95),
            'ci_95': (np.percentile(energies, 2.5),
                     np.percentile(energies, 97.5))
        }
    }

    print(f"\n[RESULTS] Monte Carlo Statistics:")
    print(f"  Convergence Rate: {statistics['convergence_rate']:.1f}% "
          f"({statistics['converged_count']}/{statistics['n_runs']})")
    print(f"\n  Settling Time:")
    print(f"    Mean: {statistics['settling_time']['mean']:.2f}s "
          f"± {statistics['settling_time']['std']:.2f}s")
    print(f"    Median: {statistics['settling_time']['p50']:.2f}s")
    print(f"    95% CI: [{statistics['settling_time']['ci_95'][0]:.2f}s, "
          f"{statistics['settling_time']['ci_95'][1]:.2f}s]")
    print(f"    Range: [{statistics['settling_time']['min']:.2f}s, "
          f"{statistics['settling_time']['max']:.2f}s]")

    if plot:
        plot_monte_carlo_results(statistics, settling_times, overshoots, energies,
                                 controller_type, uncertainty_level)

    return statistics, (settling_times, overshoots, energies)


def plot_monte_carlo_results(statistics, settling_times, overshoots, energies,
                              controller_type, uncertainty_level):
    """
    Plot Monte Carlo results: histograms and boxplots.
    """
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))

    # Row 1: Histograms
    # Settling Time Histogram
    axes[0, 0].hist(settling_times, bins=30, edgecolor='black', alpha=0.7, color='steelblue')
    axes[0, 0].axvline(statistics['settling_time']['mean'], color='r',
                       linestyle='--', linewidth=2,
                       label=f"Mean: {statistics['settling_time']['mean']:.2f}s")
    axes[0, 0].axvline(statistics['settling_time']['p50'], color='g',
                       linestyle='-.', linewidth=2,
                       label=f"Median: {statistics['settling_time']['p50']:.2f}s")
    axes[0, 0].set_xlabel('Settling Time (s)', fontsize=11)
    axes[0, 0].set_ylabel('Frequency', fontsize=11)
    axes[0, 0].set_title('Settling Time Distribution', fontsize=12, fontweight='bold')
    axes[0, 0].legend(fontsize=9)
    axes[0, 0].grid(True, alpha=0.3)

    # Overshoot Histogram
    axes[0, 1].hist(np.rad2deg(overshoots), bins=30, edgecolor='black', alpha=0.7, color='coral')
    axes[0, 1].axvline(np.rad2deg(statistics['overshoot']['mean']), color='r',
                       linestyle='--', linewidth=2,
                       label=f"Mean: {np.rad2deg(statistics['overshoot']['mean']):.2f}°")
    axes[0, 1].axvline(np.rad2deg(statistics['overshoot']['p50']), color='g',
                       linestyle='-.', linewidth=2,
                       label=f"Median: {np.rad2deg(statistics['overshoot']['p50']):.2f}°")
    axes[0, 1].set_xlabel('Overshoot (deg)', fontsize=11)
    axes[0, 1].set_ylabel('Frequency', fontsize=11)
    axes[0, 1].set_title('Overshoot Distribution', fontsize=12, fontweight='bold')
    axes[0, 1].legend(fontsize=9)
    axes[0, 1].grid(True, alpha=0.3)

    # Energy Histogram
    axes[0, 2].hist(energies, bins=30, edgecolor='black', alpha=0.7, color='mediumseagreen')
    axes[0, 2].axvline(statistics['energy']['mean'], color='r',
                       linestyle='--', linewidth=2,
                       label=f"Mean: {statistics['energy']['mean']:.1f} J")
    axes[0, 2].axvline(statistics['energy']['p50'], color='g',
                       linestyle='-.', linewidth=2,
                       label=f"Median: {statistics['energy']['p50']:.1f} J")
    axes[0, 2].set_xlabel('Control Effort (J)', fontsize=11)
    axes[0, 2].set_ylabel('Frequency', fontsize=11)
    axes[0, 2].set_title('Control Effort Distribution', fontsize=12, fontweight='bold')
    axes[0, 2].legend(fontsize=9)
    axes[0, 2].grid(True, alpha=0.3)

    # Row 2: Boxplots
    # Settling Time Boxplot
    bp1 = axes[1, 0].boxplot([settling_times], vert=True, patch_artist=True,
                             labels=[controller_type.upper()],
                             boxprops=dict(facecolor='lightblue', color='black'),
                             medianprops=dict(color='red', linewidth=2),
                             whiskerprops=dict(color='black'),
                             capprops=dict(color='black'))
    axes[1, 0].set_ylabel('Settling Time (s)', fontsize=11, fontweight='bold')
    axes[1, 0].set_title('Settling Time Spread', fontsize=12, fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3, axis='y')

    # Overshoot Boxplot
    bp2 = axes[1, 1].boxplot([np.rad2deg(overshoots)], vert=True, patch_artist=True,
                             labels=[controller_type.upper()],
                             boxprops=dict(facecolor='lightcoral', color='black'),
                             medianprops=dict(color='red', linewidth=2),
                             whiskerprops=dict(color='black'),
                             capprops=dict(color='black'))
    axes[1, 1].set_ylabel('Overshoot (deg)', fontsize=11, fontweight='bold')
    axes[1, 1].set_title('Overshoot Spread', fontsize=12, fontweight='bold')
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    # Energy Boxplot
    bp3 = axes[1, 2].boxplot([energies], vert=True, patch_artist=True,
                             labels=[controller_type.upper()],
                             boxprops=dict(facecolor='lightgreen', color='black'),
                             medianprops=dict(color='red', linewidth=2),
                             whiskerprops=dict(color='black'),
                             capprops=dict(color='black'))
    axes[1, 2].set_ylabel('Control Effort (J)', fontsize=11, fontweight='bold')
    axes[1, 2].set_title('Control Effort Spread', fontsize=12, fontweight='bold')
    axes[1, 2].grid(True, alpha=0.3, axis='y')

    fig.suptitle(f'Monte Carlo Robustness Analysis: {controller_type.upper()} | '
                 f'Uncertainty: {uncertainty_level.capitalize()} (N={statistics["n_runs"]})',
                 fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()

    # Save figure
    output_dir = Path(__file__).parent.parent.parent / ".artifacts" / "tutorial_06"
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"monte_carlo_{controller_type}_{uncertainty_level}.png"
    fig.savefig(output_dir / filename, dpi=300, bbox_inches='tight')
    print(f"[OK] Saved: {output_dir / filename}")

    plt.show()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function - runs all tutorial examples.
    """
    print("=" * 80)
    print("Tutorial 06: Robustness Analysis Workflow")
    print("=" * 80)

    # Example 1: Parameter Sweep
    print("\n[EXAMPLE 1] Parameter Sweep Analysis")
    print("-" * 80)
    results_sweep = parameter_sweep(
        controller_type='classical_smc',
        param_name='cart_mass',
        variation_range=np.linspace(0.8, 1.2, 9),
        plot=True
    )

    # Compute degradation
    nominal_idx = 4
    worst_idx = -1
    settling_degradation = (results_sweep['settling_times'][worst_idx] /
                           results_sweep['settling_times'][nominal_idx] - 1.0) * 100
    print(f"\n[RESULT] Worst-Case Degradation (+20% mass): {settling_degradation:.1f}%")

    # Example 2: Monte Carlo Analysis
    print("\n[EXAMPLE 2] Monte Carlo Robustness Analysis")
    print("-" * 80)
    stats_mc, data_mc = monte_carlo_robustness(
        controller_type='classical_smc',
        n_runs=100,
        uncertainty_level='moderate',
        seed=42,
        plot=True
    )

    print("\n[INFO] Tutorial 06 examples completed successfully!")
    print("[INFO] Check .artifacts/tutorial_06/ for generated figures")


if __name__ == "__main__":
    main()
