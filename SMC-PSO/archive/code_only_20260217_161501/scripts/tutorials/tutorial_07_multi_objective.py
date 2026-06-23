"""
Tutorial 07: Multi-Objective PSO Optimization
==============================================

Executable code examples for Tutorial 07.

This script demonstrates:
1. Multi-objective cost function design (settling time + energy + chattering)
2. Pareto frontier generation (weight sweep)
3. PSO convergence diagnostics (diversity, improvement rate)
4. Constraint handling (penalty functions)

Usage:
    python tutorial_07_multi_objective.py

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
# SECTION 1: OBJECTIVE FUNCTIONS
# ============================================================================

def compute_chattering_frequency(control_history, dt):
    """
    Estimate chattering frequency from control input zero-crossings.

    Parameters
    ----------
    control_history : ndarray, shape (N,)
        Control input trajectory
    dt : float
        Time step

    Returns
    -------
    chattering_freq : float
        Average chattering frequency (Hz)
    """
    # Count zero-crossings (sign changes)
    sign_changes = np.diff(np.sign(control_history))
    num_crossings = np.sum(np.abs(sign_changes) > 0)

    # Frequency = crossings per second / 2 (full cycle = 2 crossings)
    total_time = len(control_history) * dt
    chattering_freq = num_crossings / (2.0 * total_time) if total_time > 0 else 0.0

    return chattering_freq


def compute_control_effort(control_history, dt):
    """
    Compute total control effort (integral of squared control input).

    Parameters
    ----------
    control_history : ndarray, shape (N,)
        Control input trajectory
    dt : float
        Time step

    Returns
    -------
    energy : float
        Total control effort (J or dimensionless)
    """
    energy = np.sum(control_history**2) * dt
    return energy


# ============================================================================
# SECTION 2: MULTI-OBJECTIVE COST FUNCTION
# ============================================================================

def multi_objective_cost_function(gains, controller_type, weights):
    """
    Multi-objective cost function for PSO.

    Parameters
    ----------
    gains : ndarray
        Controller gains to evaluate
    controller_type : str
        Controller type ('classical_smc', 'adaptive_smc', etc.)
    weights : dict
        Objective weights {'settling': w1, 'energy': w2, 'chattering': w3}

    Returns
    -------
    cost : float
        Weighted cost (lower is better)
    """
    config = load_config(str(CONFIG_PATH))

    # Create controller with candidate gains
    try:
        controller = create_controller(controller_type, config=config, gains=gains)
    except Exception as e:
        print(f"[ERROR] Controller creation failed: {e}")
        return 9999.0

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
    if not result.converged:
        return 9999.0  # Large penalty for divergence

    # Compute objectives
    settling_time = result.settling_time
    energy = compute_control_effort(result.control_history, config.simulation.dt)
    chattering = compute_chattering_frequency(result.control_history, config.simulation.dt)

    # Normalization factors (typical values)
    norm_settling = 5.0
    norm_energy = 300.0
    norm_chattering = 15.0

    # Weighted sum
    cost = (weights.get('settling', 0.0) * (settling_time / norm_settling) +
            weights.get('energy', 0.0) * (energy / norm_energy) +
            weights.get('chattering', 0.0) * (chattering / norm_chattering))

    # Constraint: Settling time timeout (hard limit)
    if settling_time > 15.0:
        cost += 100.0  # Large penalty

    return cost


# ============================================================================
# SECTION 3: PARETO FRONTIER GENERATION
# ============================================================================

def generate_pareto_frontier_settling_chattering(controller_type='classical_smc',
                                                  n_points=11):
    """
    Generate Pareto frontier for settling time vs chattering trade-off.

    Parameters
    ----------
    controller_type : str
        Controller to optimize
    n_points : int
        Number of points on Pareto frontier

    Returns
    -------
    pareto_solutions : list of dict
        Each dict contains: weights, gains, settling_time, chattering
    """
    print(f"\n[INFO] Generating Pareto Frontier ({n_points} points)")
    print(f"[INFO] Controller: {controller_type}")
    print(f"[INFO] Trade-off: Settling Time vs Chattering")

    # Weight sweep
    weight_range = np.linspace(0, 1, n_points)
    pareto_solutions = []

    # Simplified PSO implementation (for demonstration)
    # In production, use full PSO from src.optimizer.pso_optimizer
    config = load_config(str(CONFIG_PATH))

    for i, w_settling in enumerate(weight_range):
        w_chattering = 1.0 - w_settling

        print(f"\n[{i+1}/{n_points}] Optimizing: w_settling={w_settling:.2f}, "
              f"w_chattering={w_chattering:.2f}")

        # Define weights
        weights = {
            'settling': w_settling,
            'energy': 0.0,  # Not optimizing energy for this case study
            'chattering': w_chattering
        }

        # Simplified PSO: Random search over 50 candidates
        # (In production, use full PSO optimizer)
        best_cost = float('inf')
        best_gains = None
        best_result = None

        np.random.seed(42 + i)  # Reproducible

        for trial in range(50):
            # Random gains within bounds
            if controller_type == 'classical_smc':
                gains = np.array([
                    np.random.uniform(0.1, 50.0),  # k1
                    np.random.uniform(0.1, 50.0),  # k2
                    np.random.uniform(0.1, 50.0),  # lambda1
                    np.random.uniform(0.1, 50.0),  # lambda2
                    np.random.uniform(1.0, 200.0), # K
                    np.random.uniform(0.0, 50.0)   # epsilon
                ])
            else:
                # Adaptive SMC (5 gains)
                gains = np.array([
                    np.random.uniform(0.1, 50.0),  # k1
                    np.random.uniform(0.1, 50.0),  # k2
                    np.random.uniform(0.1, 50.0),  # lambda1
                    np.random.uniform(0.1, 50.0),  # lambda2
                    np.random.uniform(1.0, 200.0)  # K
                ])

            # Evaluate cost
            cost = multi_objective_cost_function(gains, controller_type, weights)

            if cost < best_cost:
                best_cost = cost
                best_gains = gains

                # Re-simulate for metrics
                controller = create_controller(controller_type, config=config, gains=best_gains)
                dynamics = DIPDynamics(config.physics)
                t_arr, x_arr, u_arr = run_simulation(
                    controller=controller,
                    dynamics_model=dynamics,
                    sim_time=config.simulation.duration,
                    dt=config.simulation.dt,
                    initial_state=config.simulation.initial_state
                )
                best_result = SimulationResult(t_arr, x_arr, u_arr)

        # Record solution
        if best_result is not None:
            solution = {
                'w_settling': w_settling,
                'w_chattering': w_chattering,
                'gains': best_gains,
                'settling_time': best_result.settling_time,
                'chattering': compute_chattering_frequency(
                    best_result.control_history, config.simulation.dt
                ),
                'energy': compute_control_effort(
                    best_result.control_history, config.simulation.dt
                )
            }
            pareto_solutions.append(solution)

            print(f"  [OK] Settling: {solution['settling_time']:.2f}s, "
                  f"Chattering: {solution['chattering']:.2f} Hz, "
                  f"Energy: {solution['energy']:.1f} J")

    return pareto_solutions


def plot_pareto_frontier(pareto_solutions, controller_type):
    """
    Plot Pareto frontier (settling time vs chattering).
    """
    settling_times = [sol['settling_time'] for sol in pareto_solutions]
    chattering_freqs = [sol['chattering'] for sol in pareto_solutions]
    energies = [sol['energy'] for sol in pareto_solutions]

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Plot 1: Settling vs Chattering (Primary Pareto Frontier)
    sc = axes[0].scatter(settling_times, chattering_freqs,
                        c=range(len(pareto_solutions)),
                        cmap='viridis', s=150, edgecolor='black', linewidth=2)

    # Annotate points
    for i, sol in enumerate(pareto_solutions):
        axes[0].annotate(f"w={sol['w_settling']:.1f}",
                        (sol['settling_time'], sol['chattering']),
                        textcoords="offset points", xytext=(0, 12),
                        ha='center', fontsize=9, fontweight='bold')

    # Connect points (Pareto frontier line)
    axes[0].plot(settling_times, chattering_freqs, 'k--', alpha=0.4, linewidth=1.5)

    axes[0].set_xlabel('Settling Time (s)', fontsize=13, fontweight='bold')
    axes[0].set_ylabel('Chattering Frequency (Hz)', fontsize=13, fontweight='bold')
    axes[0].set_title(f'Pareto Frontier: Settling Time vs Chattering\n{controller_type.upper()}',
                     fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)

    # Colorbar
    cbar1 = plt.colorbar(sc, ax=axes[0])
    cbar1.set_label('Weight Priority (0=Chattering, 1=Settling)', fontsize=10)

    # Plot 2: Energy vs Settling (Secondary Trade-off)
    sc2 = axes[1].scatter(settling_times, energies,
                         c=range(len(pareto_solutions)),
                         cmap='plasma', s=150, edgecolor='black', linewidth=2)

    # Annotate points
    for i, sol in enumerate(pareto_solutions):
        axes[1].annotate(f"w={sol['w_settling']:.1f}",
                        (sol['settling_time'], sol['energy']),
                        textcoords="offset points", xytext=(0, 12),
                        ha='center', fontsize=9, fontweight='bold')

    # Connect points
    axes[1].plot(settling_times, energies, 'k--', alpha=0.4, linewidth=1.5)

    axes[1].set_xlabel('Settling Time (s)', fontsize=13, fontweight='bold')
    axes[1].set_ylabel('Control Effort (J)', fontsize=13, fontweight='bold')
    axes[1].set_title(f'Secondary Trade-off: Settling Time vs Energy\n{controller_type.upper()}',
                     fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3)

    # Colorbar
    cbar2 = plt.colorbar(sc2, ax=axes[1])
    cbar2.set_label('Weight Priority (0=Chattering, 1=Settling)', fontsize=10)

    plt.tight_layout()

    # Save figure
    output_dir = Path(__file__).parent.parent.parent / ".artifacts" / "tutorial_07"
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"pareto_frontier_{controller_type}.png"
    fig.savefig(output_dir / filename, dpi=300, bbox_inches='tight')
    print(f"\n[OK] Saved: {output_dir / filename}")

    plt.show()


# ============================================================================
# SECTION 4: PSO CONVERGENCE DIAGNOSTICS
# ============================================================================

class PSODiagnostics:
    """
    Track PSO convergence metrics during optimization.
    """
    def __init__(self):
        self.gbest_history = []
        self.diversity_history = []
        self.improvement_history = []

    def update(self, iteration, gbest_cost, particles):
        """
        Record metrics for current iteration.

        Parameters
        ----------
        iteration : int
            Current iteration number
        gbest_cost : float
            Best cost so far
        particles : ndarray, shape (n_particles, n_dims)
            Particle positions
        """
        # Record gbest cost
        self.gbest_history.append(gbest_cost)

        # Compute diversity (average distance from center)
        center = np.mean(particles, axis=0)
        distances = np.linalg.norm(particles - center, axis=1)
        diversity = np.mean(distances)
        self.diversity_history.append(diversity)

        # Compute improvement rate
        if iteration > 0:
            prev_cost = self.gbest_history[-2]
            improvement = (prev_cost - gbest_cost) / prev_cost if prev_cost > 0 else 0.0
        else:
            improvement = 0.0
        self.improvement_history.append(improvement)

    def diagnose(self):
        """
        Analyze convergence and identify issues.

        Returns
        -------
        diagnosis : dict
            Convergence status and recommendations
        """
        diagnosis = {
            'converged': False,
            'premature': False,
            'stagnant': False,
            'recommendations': []
        }

        # Check for convergence (improvement < 0.1% for last 20 iterations)
        if len(self.improvement_history) > 20:
            recent_improvements = self.improvement_history[-20:]
            if all(imp < 0.001 for imp in recent_improvements):
                diagnosis['converged'] = True

        # Check for premature convergence (diversity drops fast early)
        if len(self.diversity_history) > 10:
            early_diversity = self.diversity_history[:5]
            mid_diversity = self.diversity_history[5:10]
            if np.mean(mid_diversity) < 0.1 * np.mean(early_diversity):
                diagnosis['premature'] = True
                diagnosis['recommendations'].append(
                    "Premature convergence detected. Try increasing inertia weight or swarm size."
                )

        # Check for stagnation (no improvement for 20+ iterations)
        if len(self.improvement_history) > 20:
            recent_improvements = self.improvement_history[-20:]
            if all(imp < 1e-6 for imp in recent_improvements):
                diagnosis['stagnant'] = True
                diagnosis['recommendations'].append(
                    "PSO stagnated. Consider restarting with new random seeds or adaptive inertia."
                )

        return diagnosis

    def plot(self):
        """
        Plot convergence diagnostics.
        """
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))

        iterations = np.arange(len(self.gbest_history))

        # Plot 1: Best Cost
        axes[0].plot(iterations, self.gbest_history, linewidth=2, color='steelblue')
        axes[0].set_xlabel('Iteration', fontsize=11, fontweight='bold')
        axes[0].set_ylabel('Best Cost', fontsize=11, fontweight='bold')
        axes[0].set_title('Convergence: Best Cost', fontsize=12, fontweight='bold')
        axes[0].grid(True, alpha=0.3)

        # Plot 2: Diversity
        axes[1].plot(iterations, self.diversity_history, linewidth=2, color='coral')
        axes[1].set_xlabel('Iteration', fontsize=11, fontweight='bold')
        axes[1].set_ylabel('Swarm Diversity', fontsize=11, fontweight='bold')
        axes[1].set_title('Exploration: Swarm Diversity', fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3)

        # Plot 3: Improvement Rate
        axes[2].plot(iterations[1:], self.improvement_history[1:], linewidth=2, color='mediumseagreen')
        axes[2].axhline(0.001, color='k', linestyle='--', linewidth=1, label='0.1% Threshold')
        axes[2].set_xlabel('Iteration', fontsize=11, fontweight='bold')
        axes[2].set_ylabel('Improvement Rate', fontsize=11, fontweight='bold')
        axes[2].set_title('Progress: Improvement Rate', fontsize=12, fontweight='bold')
        axes[2].legend(fontsize=9)
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()

        # Save figure
        output_dir = Path(__file__).parent.parent.parent / ".artifacts" / "tutorial_07"
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / "pso_convergence_diagnostics.png", dpi=300, bbox_inches='tight')
        print(f"[OK] Saved: {output_dir / 'pso_convergence_diagnostics.png'}")

        plt.show()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function - runs all tutorial examples.
    """
    print("=" * 80)
    print("Tutorial 07: Multi-Objective PSO Optimization")
    print("=" * 80)

    # Example 1: Generate Pareto Frontier (Settling Time vs Chattering)
    print("\n[EXAMPLE 1] Pareto Frontier Generation")
    print("-" * 80)
    pareto_solutions = generate_pareto_frontier_settling_chattering(
        controller_type='classical_smc',
        n_points=11
    )

    # Plot Pareto frontier
    plot_pareto_frontier(pareto_solutions, 'classical_smc')

    # Analyze Pareto solutions
    print("\n[ANALYSIS] Pareto Solutions Summary:")
    print(f"{'Weight':<10} {'Settling (s)':<15} {'Chattering (Hz)':<18} {'Energy (J)':<12}")
    print("-" * 70)
    for sol in pareto_solutions:
        print(f"{sol['w_settling']:<10.2f} {sol['settling_time']:<15.2f} "
              f"{sol['chattering']:<18.2f} {sol['energy']:<12.1f}")

    # Example 2: PSO Convergence Diagnostics
    print("\n[EXAMPLE 2] PSO Convergence Diagnostics")
    print("-" * 80)
    print("[INFO] Simulating PSO with mock data for demonstration...")

    # Create mock PSO convergence data
    diagnostics = PSODiagnostics()
    n_iters = 50
    for i in range(n_iters):
        # Mock gbest cost (exponential decay)
        gbest_cost = 1.0 * np.exp(-i / 20.0) + 0.1

        # Mock particle positions (converging to center)
        n_particles = 30
        n_dims = 6
        particles = np.random.randn(n_particles, n_dims) * (1.0 - i / n_iters)

        diagnostics.update(i, gbest_cost, particles)

    # Diagnose convergence
    diagnosis = diagnostics.diagnose()
    print(f"\n[DIAGNOSIS]")
    print(f"  Converged: {diagnosis['converged']}")
    print(f"  Premature: {diagnosis['premature']}")
    print(f"  Stagnant: {diagnosis['stagnant']}")
    if diagnosis['recommendations']:
        print(f"  Recommendations:")
        for rec in diagnosis['recommendations']:
            print(f"    - {rec}")

    # Plot convergence diagnostics
    diagnostics.plot()

    print("\n[INFO] Tutorial 07 examples completed successfully!")
    print("[INFO] Check .artifacts/tutorial_07/ for generated figures")


if __name__ == "__main__":
    main()
