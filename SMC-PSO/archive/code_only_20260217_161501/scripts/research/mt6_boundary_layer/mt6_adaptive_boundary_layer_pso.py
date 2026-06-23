#!/usr/bin/env python3
"""
MT-6 Adaptive Boundary Layer PSO Optimization (Agent B)

Optimizes adaptive boundary layer parameters (ε_min, α) for Classical SMC
to minimize chattering while maintaining control performance.

Task: Find optimal (ε_min, α) that minimizes chattering_index
Baseline: Fixed boundary layer chattering_index = 6.37 (Agent A)
Target: ≥30% reduction (chattering < 4.46)

PSO Parameters:
- Parameter 1: ε_min (base thickness) ∈ [0.015, 0.05] (adjusted bounds, Oct 18)
- Parameter 2: α (slope for adaptation) ∈ [0.0, 2.0] (expanded for stronger adaptation)
- Swarm: 15 particles, 20 iterations
- Fitness: 70% chattering + 15% settling + 15% overshoot
- Controller gains: Default [5.0, 5.0, 5.0, 0.5, 0.5, 0.5] (matching Agent A baseline)

Note: Initial run with bounds [0.005, 0.03] × [0.0, 1.0] resulted in 352% WORSE
chattering (28.83 vs 6.37). Adjusted bounds to explore larger ε_min values
near the fixed baseline (0.02) and allow stronger adaptive slopes.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd
from scipy import stats

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.config import load_config
from src.controllers.factory import create_controller
from src.core.dynamics import DIPDynamics
from src.core.simulation_runner import run_simulation
from src.controllers.smc.algorithms.classical.boundary_layer import BoundaryLayer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.logs/benchmarks/mt6_adaptive_optimization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AdaptiveBoundaryLayerPSO:
    """PSO optimizer for adaptive boundary layer parameters."""

    def __init__(self,
                 optimized_gains: List[float],
                 baseline_chattering: float = 6.37,
                 n_particles: int = 15,
                 n_iterations: int = 20,
                 n_monte_carlo_runs: int = 5,
                 seed: int = 42):
        """
        Initialize PSO optimizer.

        Args:
            optimized_gains: Phase53 optimized gains [k1, k2, lam1, lam2, K, kd]
            baseline_chattering: Baseline chattering_index from Agent A
            n_particles: Swarm size
            n_iterations: Number of PSO iterations
            n_monte_carlo_runs: Monte Carlo runs per fitness evaluation
            seed: Random seed for reproducibility
        """
        self.optimized_gains = optimized_gains
        self.baseline_chattering = baseline_chattering
        self.n_particles = n_particles
        self.n_iterations = n_iterations
        self.n_monte_carlo_runs = n_monte_carlo_runs
        self.seed = seed

        # PSO parameter bounds: [ε_min, α]
        # ADJUSTED BOUNDS (Oct 18): Previous bounds [0.005, 0.03] were too restrictive
        # New range includes fixed baseline ε=0.02 and allows stronger adaptation
        self.bounds_min = np.array([0.015, 0.0])    # Minimum values (raised from 0.005)
        self.bounds_max = np.array([0.05, 2.0])     # Maximum values (expanded from 0.03, 1.0)

        # PSO hyperparameters (standard values)
        self.w = 0.7    # Inertia weight
        self.c1 = 2.0   # Cognitive coefficient
        self.c2 = 2.0   # Social coefficient

        # Load configuration
        self.config = load_config(project_root / "config.yaml")

        # Set random seed
        np.random.seed(seed)

        # Initialize swarm
        self.positions = None
        self.velocities = None
        self.personal_best_positions = None
        self.personal_best_scores = None
        self.global_best_position = None
        self.global_best_score = float('inf')

        # History tracking
        self.iteration_history = []

        logger.info(f"Initialized AdaptiveBoundaryLayerPSO:")
        logger.info(f"  Swarm: {n_particles} particles, {n_iterations} iterations")
        logger.info(f"  Bounds: eps_min in [{self.bounds_min[0]:.3f}, {self.bounds_max[0]:.3f}], "
                   f"alpha in [{self.bounds_min[1]:.1f}, {self.bounds_max[1]:.1f}]")
        logger.info(f"  Baseline chattering: {baseline_chattering:.2f}")
        logger.info(f"  Optimized gains: {optimized_gains}")

    def _initialize_swarm(self):
        """Initialize particle positions and velocities."""
        # Random positions within bounds
        self.positions = np.random.uniform(
            low=self.bounds_min,
            high=self.bounds_max,
            size=(self.n_particles, 2)
        )

        # Random velocities (scaled to 10% of bounds)
        velocity_scale = 0.1 * (self.bounds_max - self.bounds_min)
        self.velocities = np.random.uniform(
            low=-velocity_scale,
            high=velocity_scale,
            size=(self.n_particles, 2)
        )

        # Initialize personal bests
        self.personal_best_positions = self.positions.copy()
        self.personal_best_scores = np.full(self.n_particles, float('inf'))

        logger.info("Swarm initialized")

    def _compute_fitness(self, epsilon_min: float, alpha: float) -> Dict[str, float]:
        """
        Compute fitness for given boundary layer parameters.

        Runs Monte Carlo simulations and computes:
        - chattering_index (70% weight)
        - settling_time penalty (15% weight)
        - overshoot penalty (15% weight)

        Args:
            epsilon_min: Base boundary layer thickness
            alpha: Adaptive slope coefficient

        Returns:
            Dictionary with metrics and fitness score
        """
        # Monte Carlo statistics
        chattering_values = []
        settling_values = []
        overshoot_values = []
        energy_values = []

        for run_idx in range(self.n_monte_carlo_runs):
            # Random initial conditions (same as Agent A)
            theta1_init = np.random.uniform(-0.3, 0.3)
            theta2_init = np.random.uniform(-0.3, 0.3)
            theta1_dot_init = np.random.uniform(-0.5, 0.5)
            theta2_dot_init = np.random.uniform(-0.5, 0.5)

            initial_state = np.array([
                0.0,  # x
                theta1_init,
                theta2_init,
                0.0,  # x_dot
                theta1_dot_init,
                theta2_dot_init
            ])

            # Create controller with adaptive boundary layer
            # Use ClassicalSMCConfig for proper parameter passing
            from src.controllers.smc.algorithms.classical.config import ClassicalSMCConfig

            controller_config = ClassicalSMCConfig(
                gains=self.optimized_gains,
                max_force=150.0,
                dt=0.01,
                boundary_layer=epsilon_min,
                boundary_layer_slope=alpha,
                switch_method='tanh'
            )

            try:
                # Use the config class directly with ClassicalSMC
                from src.controllers.smc.classic_smc import ClassicalSMC
                controller = ClassicalSMC(
                    gains=controller_config.gains,
                    max_force=controller_config.max_force,
                    boundary_layer=controller_config.boundary_layer,
                    boundary_layer_slope=controller_config.boundary_layer_slope,
                    switch_method=controller_config.switch_method
                )

                # Create dynamics model
                dynamics = DIPDynamics(self.config.physics)

                # Run simulation
                t_arr, x_arr, u_arr = run_simulation(
                    controller=controller,
                    dynamics_model=dynamics,
                    sim_time=10.0,
                    dt=0.01,
                    initial_state=initial_state,
                    u_max=150.0
                )

                # Extract metrics
                time = t_arr
                states = x_arr
                controls = u_arr

                # Chattering index (using BoundaryLayer utility)
                boundary_layer = BoundaryLayer(
                    thickness=epsilon_min,
                    slope=alpha,
                    switch_method='tanh'
                )
                chattering_index = boundary_layer.get_chattering_index(controls, dt=0.01)
                chattering_values.append(chattering_index)

                # Settling time (first time |θ1|, |θ2| < 0.05 rad for 0.5s)
                theta1 = states[:, 1]
                theta2 = states[:, 2]
                settling_mask = (np.abs(theta1) < 0.05) & (np.abs(theta2) < 0.05)

                settling_time = 10.0  # Default: didn't settle
                for i in range(len(settling_mask) - 50):  # 0.5s = 50 samples
                    if np.all(settling_mask[i:i+50]):
                        settling_time = time[i]
                        break
                settling_values.append(settling_time)

                # Overshoot (maximum angle magnitude)
                max_overshoot = max(np.max(np.abs(theta1)), np.max(np.abs(theta2)))
                overshoot_values.append(max_overshoot)

                # Control energy (integral of u^2)
                # Note: controls has length n-1, so use time[:-1] for integration
                control_energy = np.trapz(controls**2, time[:-1])
                energy_values.append(control_energy)

            except Exception as e:
                logger.warning(f"Simulation failed for eps={epsilon_min:.4f}, alpha={alpha:.4f}: {e}")
                # Penalize failed simulations heavily
                chattering_values.append(100.0)
                settling_values.append(20.0)
                overshoot_values.append(5.0)
                energy_values.append(1e6)

        # Compute statistics
        mean_chattering = np.mean(chattering_values)
        mean_settling = np.mean(settling_values)
        mean_overshoot = np.mean(overshoot_values)
        mean_energy = np.mean(energy_values)

        # Fitness function (minimize)
        # Primary: chattering_index (70% weight)
        chattering_term = 0.70 * mean_chattering

        # Constraint: settling_time penalty (15% weight)
        settling_penalty = 0.15 * max(0, mean_settling - 5.0)  # Penalty if > 5s

        # Constraint: overshoot penalty (15% weight)
        overshoot_penalty = 0.15 * max(0, mean_overshoot - 0.3) * 10.0  # Penalty if > 0.3 rad

        fitness = chattering_term + settling_penalty + overshoot_penalty

        return {
            'fitness': fitness,
            'chattering_index': mean_chattering,
            'settling_time': mean_settling,
            'overshoot': mean_overshoot,
            'control_energy': mean_energy,
            'chattering_std': np.std(chattering_values),
            'settling_std': np.std(settling_values),
            'overshoot_std': np.std(overshoot_values)
        }

    def _update_velocities_and_positions(self):
        """Update particle velocities and positions using PSO update rules."""
        for i in range(self.n_particles):
            # Random coefficients
            r1 = np.random.random(2)
            r2 = np.random.random(2)

            # Velocity update
            cognitive_component = self.c1 * r1 * (self.personal_best_positions[i] - self.positions[i])
            social_component = self.c2 * r2 * (self.global_best_position - self.positions[i])
            self.velocities[i] = (
                self.w * self.velocities[i] +
                cognitive_component +
                social_component
            )

            # Position update
            self.positions[i] += self.velocities[i]

            # Enforce bounds
            self.positions[i] = np.clip(self.positions[i], self.bounds_min, self.bounds_max)

    def optimize(self) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Run PSO optimization.

        Returns:
            Best parameters [ε_min, α] and optimization history
        """
        logger.info("=" * 80)
        logger.info("Starting PSO Optimization")
        logger.info("=" * 80)

        self._initialize_swarm()

        for iteration in range(self.n_iterations):
            logger.info(f"\nIteration {iteration + 1}/{self.n_iterations}")

            iteration_scores = []

            # Evaluate all particles
            for i in range(self.n_particles):
                epsilon_min, alpha = self.positions[i]

                # Compute fitness
                metrics = self._compute_fitness(epsilon_min, alpha)
                fitness = metrics['fitness']
                iteration_scores.append(fitness)

                logger.info(
                    f"  Particle {i+1}: eps={epsilon_min:.4f}, alpha={alpha:.4f} | "
                    f"Fitness={fitness:.4f} (chattering={metrics['chattering_index']:.2f}, "
                    f"settling={metrics['settling_time']:.2f}s)"
                )

                # Update personal best
                if fitness < self.personal_best_scores[i]:
                    self.personal_best_scores[i] = fitness
                    self.personal_best_positions[i] = self.positions[i].copy()

                # Update global best
                if fitness < self.global_best_score:
                    self.global_best_score = fitness
                    self.global_best_position = self.positions[i].copy()
                    logger.info(f"  *** NEW GLOBAL BEST: {fitness:.4f} ***")

            # Log iteration summary
            best_iter = np.min(iteration_scores)
            mean_iter = np.mean(iteration_scores)
            self.iteration_history.append({
                'iteration': iteration + 1,
                'best_fitness': best_iter,
                'mean_fitness': mean_iter,
                'global_best_fitness': self.global_best_score,
                'best_epsilon_min': self.global_best_position[0],
                'best_alpha': self.global_best_position[1]
            })

            logger.info(
                f"  Iteration Summary: Best={best_iter:.4f}, Mean={mean_iter:.4f}, "
                f"Global Best={self.global_best_score:.4f}"
            )

            # Update swarm
            if iteration < self.n_iterations - 1:  # Don't update after last iteration
                self._update_velocities_and_positions()

        logger.info("=" * 80)
        logger.info("PSO Optimization Complete")
        logger.info(f"Best Parameters: eps_min={self.global_best_position[0]:.4f}, "
                   f"alpha={self.global_best_position[1]:.4f}")
        logger.info(f"Best Fitness: {self.global_best_score:.4f}")
        logger.info("=" * 80)

        return self.global_best_position, {
            'iteration_history': self.iteration_history,
            'final_best_fitness': self.global_best_score
        }

    def validate_best_parameters(self,
                                epsilon_min: float,
                                alpha: float,
                                n_runs: int = 100) -> pd.DataFrame:
        """
        Validate best parameters with extensive Monte Carlo runs.

        Args:
            epsilon_min: Optimized base thickness
            alpha: Optimized slope coefficient
            n_runs: Number of Monte Carlo validation runs

        Returns:
            DataFrame with validation results
        """
        logger.info("=" * 80)
        logger.info(f"Validating Best Parameters (n={n_runs} runs)")
        logger.info(f"  eps_min={epsilon_min:.4f}, alpha={alpha:.4f}")
        logger.info("=" * 80)

        results = []

        for run_idx in range(n_runs):
            if (run_idx + 1) % 10 == 0:
                logger.info(f"  Validation run {run_idx + 1}/{n_runs}")

            # Random initial conditions
            theta1_init = np.random.uniform(-0.3, 0.3)
            theta2_init = np.random.uniform(-0.3, 0.3)
            theta1_dot_init = np.random.uniform(-0.5, 0.5)
            theta2_dot_init = np.random.uniform(-0.5, 0.5)

            initial_state = np.array([
                0.0,
                theta1_init,
                theta2_init,
                0.0,
                theta1_dot_init,
                theta2_dot_init
            ])

            # Create controller
            from src.controllers.smc.algorithms.classical.config import ClassicalSMCConfig
            from src.controllers.smc.classic_smc import ClassicalSMC

            controller_config = ClassicalSMCConfig(
                gains=self.optimized_gains,
                max_force=150.0,
                dt=0.01,
                boundary_layer=epsilon_min,
                boundary_layer_slope=alpha,
                switch_method='tanh'
            )

            try:
                controller = ClassicalSMC(
                    gains=controller_config.gains,
                    max_force=controller_config.max_force,
                    boundary_layer=controller_config.boundary_layer,
                    boundary_layer_slope=controller_config.boundary_layer_slope,
                    switch_method=controller_config.switch_method
                )
                dynamics = DIPDynamics(self.config.physics)

                t_arr, x_arr, u_arr = run_simulation(
                    controller=controller,
                    dynamics_model=dynamics,
                    sim_time=10.0,
                    dt=0.01,
                    initial_state=initial_state,
                    u_max=150.0
                )

                # Extract metrics
                time = t_arr
                states = x_arr
                controls = u_arr

                # Chattering index
                boundary_layer = BoundaryLayer(
                    thickness=epsilon_min,
                    slope=alpha,
                    switch_method='tanh'
                )
                chattering_index = boundary_layer.get_chattering_index(controls, dt=0.01)

                # Settling time
                theta1 = states[:, 1]
                theta2 = states[:, 2]
                settling_mask = (np.abs(theta1) < 0.05) & (np.abs(theta2) < 0.05)

                settling_time = 10.0
                for i in range(len(settling_mask) - 50):
                    if np.all(settling_mask[i:i+50]):
                        settling_time = time[i]
                        break

                # Overshoot
                max_overshoot = max(np.max(np.abs(theta1)), np.max(np.abs(theta2)))

                # Control energy
                # Note: controls has length n-1, so use time[:-1] for integration
                control_energy = np.trapz(controls**2, time[:-1])

                results.append({
                    'run': run_idx + 1,
                    'chattering_index': chattering_index,
                    'settling_time': settling_time,
                    'overshoot': max_overshoot,
                    'control_energy': control_energy,
                    'theta1_init': theta1_init,
                    'theta2_init': theta2_init,
                    'success': True
                })

            except Exception as e:
                logger.warning(f"Validation run {run_idx + 1} failed: {e}")
                results.append({
                    'run': run_idx + 1,
                    'chattering_index': np.nan,
                    'settling_time': np.nan,
                    'overshoot': np.nan,
                    'control_energy': np.nan,
                    'theta1_init': theta1_init,
                    'theta2_init': theta2_init,
                    'success': False
                })

        df = pd.DataFrame(results)

        # Compute statistics
        successful_runs = df[df['success']]
        n_successful = len(successful_runs)

        logger.info("\nValidation Statistics:")
        logger.info(f"  Successful runs: {n_successful}/{n_runs}")

        if n_successful > 0:
            for metric in ['chattering_index', 'settling_time', 'overshoot', 'control_energy']:
                mean_val = successful_runs[metric].mean()
                std_val = successful_runs[metric].std()
                ci = 1.96 * std_val / np.sqrt(n_successful)
                logger.info(f"  {metric}: {mean_val:.4f} ± {std_val:.4f} (95% CI: ±{ci:.4f})")

        return df


def main():
    """Main execution function."""
    logger.info("MT-6 Adaptive Boundary Layer PSO Optimization")
    logger.info("=" * 80)

    # 1. Use default gains (same as Agent A for fair comparison)
    # CRITICAL FIX: Previously used phase53 gains [23.67, 14.29, 8.87, 3.55, 6.52, 2.93]
    # which caused 23x higher chattering (143.40 vs 6.37). Now using same defaults
    # as Agent A to enable fair comparison where only boundary layer strategy differs.
    optimized_gains = [5.0, 5.0, 5.0, 0.5, 0.5, 0.5]  # [k1, k2, lam1, lam2, K, kd]
    logger.info(f"Using default gains (matching Agent A baseline): {optimized_gains}")

    # 2. Initialize PSO optimizer
    optimizer = AdaptiveBoundaryLayerPSO(
        optimized_gains=optimized_gains,
        baseline_chattering=6.37,  # Agent A baseline
        n_particles=15,
        n_iterations=20,
        n_monte_carlo_runs=5,
        seed=42
    )

    # 3. Run PSO optimization
    best_params, history = optimizer.optimize()
    epsilon_min_opt, alpha_opt = best_params

    # 4. Save PSO iteration history
    iteration_df = pd.DataFrame(history['iteration_history'])
    iteration_csv = project_root / "benchmarks/MT6_adaptive_optimization.csv"
    iteration_df.to_csv(iteration_csv, index=False)
    logger.info(f"\nSaved PSO iteration history to: {iteration_csv}")

    # 5. Validate with 100 Monte Carlo runs
    logger.info("\nRunning extensive validation (100 runs)...")
    validation_df = optimizer.validate_best_parameters(epsilon_min_opt, alpha_opt, n_runs=100)

    # 6. Save validation results
    validation_csv = project_root / "benchmarks/MT6_adaptive_validation.csv"
    validation_df.to_csv(validation_csv, index=False)
    logger.info(f"Saved validation results to: {validation_csv}")

    # 7. Compare against baseline
    successful_validation = validation_df[validation_df['success']]

    if len(successful_validation) > 0:
        mean_chattering = successful_validation['chattering_index'].mean()
        std_chattering = successful_validation['chattering_index'].std()
        ci_chattering = 1.96 * std_chattering / np.sqrt(len(successful_validation))

        mean_settling = successful_validation['settling_time'].mean()
        std_settling = successful_validation['settling_time'].std()
        ci_settling = 1.96 * std_settling / np.sqrt(len(successful_validation))

        mean_overshoot = successful_validation['overshoot'].mean()
        std_overshoot = successful_validation['overshoot'].std()
        ci_overshoot = 1.96 * std_overshoot / np.sqrt(len(successful_validation))

        mean_energy = successful_validation['control_energy'].mean()
        std_energy = successful_validation['control_energy'].std()

        # Compute improvement vs baseline
        baseline_chattering = 6.37
        chattering_reduction = ((baseline_chattering - mean_chattering) / baseline_chattering) * 100

        logger.info("\n" + "=" * 80)
        logger.info("FINAL RESULTS - COMPARISON WITH BASELINE")
        logger.info("=" * 80)
        logger.info(f"\nBest Parameters Found:")
        logger.info(f"  eps_min (base thickness): {epsilon_min_opt:.6f}")
        logger.info(f"  alpha (adaptive slope):   {alpha_opt:.6f}")

        logger.info(f"\nValidation Results (n={len(successful_validation)}):")
        logger.info(f"  Chattering Index: {mean_chattering:.4f} ± {std_chattering:.4f} (95% CI: ±{ci_chattering:.4f})")
        logger.info(f"  Settling Time:    {mean_settling:.4f} ± {std_settling:.4f}s (95% CI: ±{ci_settling:.4f}s)")
        logger.info(f"  Overshoot:        {mean_overshoot:.4f} ± {std_overshoot:.4f} rad (95% CI: ±{ci_overshoot:.4f} rad)")
        logger.info(f"  Control Energy:   {mean_energy:.2f} ± {std_energy:.2f}")

        logger.info(f"\nComparison with Agent A Baseline:")
        logger.info(f"  Baseline Chattering: {baseline_chattering:.2f}")
        logger.info(f"  Adaptive Chattering: {mean_chattering:.2f}")
        logger.info(f"  Improvement:         {chattering_reduction:+.1f}%")

        if chattering_reduction >= 30:
            logger.info(f"  ✓ SUCCESS: Achieved ≥30% chattering reduction target")
        else:
            logger.info(f"  ✗ Target not met: Required ≥30% reduction, achieved {chattering_reduction:.1f}%")

        # Statistical significance test (Welch's t-test)
        # Assume baseline has similar std (1.20) based on Agent A
        baseline_mean = 6.37
        baseline_std = 1.20
        baseline_n = 100

        # Welch's t-test
        t_stat = (mean_chattering - baseline_mean) / np.sqrt(
            (std_chattering**2 / len(successful_validation)) +
            (baseline_std**2 / baseline_n)
        )
        df_welch = (
            (std_chattering**2 / len(successful_validation) + baseline_std**2 / baseline_n)**2 /
            ((std_chattering**2 / len(successful_validation))**2 / (len(successful_validation) - 1) +
             (baseline_std**2 / baseline_n)**2 / (baseline_n - 1))
        )
        p_value = stats.t.cdf(t_stat, df_welch)  # One-tailed test (adaptive < fixed)

        logger.info(f"\nStatistical Significance (Welch's t-test):")
        logger.info(f"  t-statistic: {t_stat:.4f}")
        logger.info(f"  p-value:     {p_value:.6f}")
        logger.info(f"  Significant: {'Yes (p < 0.05)' if p_value < 0.05 else 'No (p ≥ 0.05)'}")

        # Summary table
        logger.info("\n" + "=" * 80)
        logger.info("COMPARISON TABLE")
        logger.info("=" * 80)
        logger.info(f"{'Metric':<20} | {'Fixed (Agent A)':<20} | {'Adaptive (Best)':<20} | {'Improvement':<15}")
        logger.info("-" * 80)
        logger.info(f"{'Chattering':<20} | {baseline_chattering:.2f} ± 1.20{' ':<10} | {mean_chattering:.2f} ± {std_chattering:.2f}{' ':<6} | {chattering_reduction:+.1f}%")
        logger.info(f"{'Settling (s)':<20} | {'>10.0':<20} | {mean_settling:.2f} ± {std_settling:.2f}{' ':<6} | {'N/A':<15}")
        logger.info(f"{'Overshoot (rad)':<20} | {'N/A':<20} | {mean_overshoot:.3f} ± {std_overshoot:.3f}{' ':<5} | {'N/A':<15}")
        logger.info("=" * 80)

        # Save summary to JSON
        summary = {
            'best_parameters': {
                'epsilon_min': float(epsilon_min_opt),
                'alpha': float(alpha_opt)
            },
            'validation_statistics': {
                'n_runs': int(len(successful_validation)),
                'chattering_index': {
                    'mean': float(mean_chattering),
                    'std': float(std_chattering),
                    'ci_95': float(ci_chattering)
                },
                'settling_time': {
                    'mean': float(mean_settling),
                    'std': float(std_settling),
                    'ci_95': float(ci_settling)
                },
                'overshoot': {
                    'mean': float(mean_overshoot),
                    'std': float(std_overshoot),
                    'ci_95': float(ci_overshoot)
                },
                'control_energy': {
                    'mean': float(mean_energy),
                    'std': float(std_energy)
                }
            },
            'comparison_with_baseline': {
                'baseline_chattering': baseline_chattering,
                'adaptive_chattering': float(mean_chattering),
                'chattering_reduction_percent': float(chattering_reduction),
                'target_achieved': chattering_reduction >= 30,
                'statistical_significance': {
                    't_statistic': float(t_stat),
                    'p_value': float(p_value),
                    'significant': p_value < 0.05
                }
            },
            'pso_optimization': {
                'n_particles': optimizer.n_particles,
                'n_iterations': optimizer.n_iterations,
                'final_fitness': history['final_best_fitness']
            }
        }

        summary_file = project_root / "benchmarks/MT6_adaptive_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"\nSaved summary to: {summary_file}")

    else:
        logger.error("All validation runs failed!")

    logger.info("\nMT-6 Adaptive Boundary Layer Optimization Complete")


if __name__ == "__main__":
    main()
