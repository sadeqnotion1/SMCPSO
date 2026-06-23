#!/usr/bin/env python
"""
Phase 2 Chattering PSO Optimization

Optimizes boundary layer parameters (epsilon_min, alpha) for Classical SMC
and Adaptive SMC, and adaptation dynamics parameters for Hybrid Adaptive
STA-SMC to minimize chattering while maintaining control performance.

Approach:
- Use Phase 53 optimized gains (FIXED) for stability
- Optimize 2D boundary layer parameters for Classical/Adaptive SMC
- Optimize 4D adaptation dynamics for Hybrid Adaptive STA-SMC
- Based on successful MT-6 methodology (3.7% chattering reduction)

Controllers:
1. Classical SMC: 6 gains [k1, k2, lam1, lam2, K, kd]
   - Params: boundary_layer (epsilon) + boundary_layer_slope (alpha)
2. Adaptive SMC: 5 gains [k1, k2, lam1, lam2, gamma]
   - Params: boundary_layer (epsilon) + dead_zone (alpha)
3. Hybrid Adaptive STA: 4 gains [k1, k2, lam1, lam2]
   - Params: gamma1 + gamma2 + adapt_rate_limit + gain_leak

PSO Parameters:
- Parameters (Classical/Adaptive): epsilon_min in [0.01, 0.05], alpha in [0.0, 2.0]
- Parameters (Hybrid Set 2 - after bug fix): gamma1 in [0.01, 0.1], gamma2 in [0.005, 0.05],
  adapt_rate_limit in [0.1, 1.0], gain_leak in [1e-4, 1e-3]
- Fixed (Hybrid): sat_soft_width=0.05, dead_zone=0.01, k1_max=100.0, u_int_max=100.0
- Swarm: 30 particles, 50 iterations
- Fitness: 70% chattering + 15% settling + 15% overshoot + 5.0*reset_rate
- Monte Carlo: 5 runs per fitness evaluation

Emergency Reset Bug Fix (Dec 30, 2025):
- Original issue: Reset triggered at 0.9*k_max (45) but gains clipped at k_max (50)
- Result: Infinite reset loop -> 91% emergency reset rate -> chattering 56-58
- Fix: Relaxed threshold to 1.5*k_max (75), increased limits (k1_max=100, u_int_max=100)
- Expected: Chattering <0.1 (similar to Adaptive SMC)
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
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config import load_config
from src.controllers.smc.classic_smc import ClassicalSMC
from src.controllers.smc.adaptive_smc import AdaptiveSMC
from src.controllers.smc.hybrid_adaptive_sta_smc import HybridAdaptiveSTASMC
from src.core.dynamics import DIPDynamics
from src.core.simulation_runner import run_simulation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def _format_param_value(value: float) -> str:
    if value != 0.0 and abs(value) < 1e-3:
        return f"{value:.2e}"
    return f"{value:.4f}"


class ChatteringBoundaryLayerPSO:
    """PSO optimizer for controller-specific parameters to reduce chattering."""

    def __init__(self,
                 controller_type: str,
                 optimized_gains: List[float],
                 n_particles: int = 30,
                 n_iterations: int = 50,
                 n_monte_carlo_runs: int = 5,
                 seed: int = 42):
        """
        Initialize PSO optimizer.

        Args:
            controller_type: Controller type ('classical_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc')
            optimized_gains: Phase53 optimized gains (fixed)
            n_particles: Swarm size
            n_iterations: Number of PSO iterations
            n_monte_carlo_runs: Monte Carlo runs per fitness evaluation
            seed: Random seed for reproducibility
        """
        self.controller_type = controller_type
        self.optimized_gains = optimized_gains
        self.n_particles = n_particles
        self.n_iterations = n_iterations
        self.n_monte_carlo_runs = n_monte_carlo_runs
        self.seed = seed

        # PSO parameter bounds depend on controller type.
        if controller_type == 'hybrid_adaptive_sta_smc':
            # Set 2: Narrower ranges after emergency reset bug fix (0.9*k_max -> 1.5*k_max)
            self.param_names = ["gamma1", "gamma2", "adapt_rate_limit", "gain_leak"]
            self.bounds_min = np.array([0.01, 0.005, 0.1, 1e-4])
            self.bounds_max = np.array([0.1, 0.05, 1.0, 1e-3])
        else:
            # Classical/Adaptive: standard ranges
            self.param_names = ["epsilon_min", "alpha"]
            self.bounds_min = np.array([0.01, 0.0])    # Minimum values
            self.bounds_max = np.array([0.05, 2.0])     # Maximum values
        self.param_dim = len(self.param_names)

        # PSO hyperparameters
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

        logger.info(f"Initialized ChatteringBoundaryLayerPSO for {controller_type}")
        logger.info(f"  Swarm: {n_particles} particles, {n_iterations} iterations")
        bounds_str = ", ".join(
            f"{name} in [{_format_param_value(low)}, {_format_param_value(high)}]"
            for name, low, high in zip(self.param_names, self.bounds_min, self.bounds_max)
        )
        logger.info(f"  Bounds: {bounds_str}")
        logger.info(f"  Optimized gains: {optimized_gains}")

    def _initialize_swarm(self):
        """Initialize particle positions and velocities."""
        self.positions = np.random.uniform(
            low=self.bounds_min,
            high=self.bounds_max,
            size=(self.n_particles, self.param_dim)
        )

        velocity_scale = 0.1 * (self.bounds_max - self.bounds_min)
        self.velocities = np.random.uniform(
            low=-velocity_scale,
            high=velocity_scale,
            size=(self.n_particles, self.param_dim)
        )

        self.personal_best_positions = self.positions.copy()
        self.personal_best_scores = np.full(self.n_particles, float('inf'))

        logger.info("Swarm initialized")

    def _format_params(self, params: np.ndarray) -> str:
        parts = []
        for name, value in zip(self.param_names, params):
            parts.append(f"{name}={_format_param_value(float(value))}")
        return ", ".join(parts)

    def _estimate_emergency_reset_rate(self, controls: np.ndarray, controller: Any) -> float:
        history = getattr(controller, "_last_history", None)
        if not isinstance(history, dict):
            return 0.0
        reset_flags = history.get("emergency_reset")
        if isinstance(reset_flags, list) and len(reset_flags) > 0:
            return float(np.mean(np.asarray(reset_flags, dtype=float)))

        k1_hist = history.get("k1")
        k2_hist = history.get("k2")
        if not isinstance(k1_hist, list) or not isinstance(k2_hist, list):
            return 0.0
        if len(k1_hist) == 0 or len(k2_hist) == 0 or len(controls) == 0:
            return 0.0

        # Heuristic: emergency reset forces u=0 and gains to ~5% of their initial values.
        try:
            k1_init = float(getattr(controller, "k1_init", 0.0))
            k2_init = float(getattr(controller, "k2_init", 0.0))
        except Exception:
            return 0.0
        if k1_init <= 0.0 or k2_init <= 0.0:
            return 0.0
        k1_thresh = 0.06 * k1_init
        k2_thresh = 0.06 * k2_init

        k1_arr = np.asarray(k1_hist, dtype=float)
        k2_arr = np.asarray(k2_hist, dtype=float)
        u_arr = np.asarray(controls, dtype=float)
        min_len = min(len(k1_arr), len(k2_arr), len(u_arr))
        if min_len == 0:
            return 0.0
        reset_mask = (
            (np.abs(u_arr[:min_len]) < 1e-6) &
            (k1_arr[:min_len] <= k1_thresh) &
            (k2_arr[:min_len] <= k2_thresh)
        )
        return float(np.mean(reset_mask))

    def _compute_fitness(self, params: np.ndarray) -> Dict[str, float]:
        """
        Compute fitness for given controller parameters.

        Runs Monte Carlo simulations and computes:
        - chattering_index (70% weight)
        - settling_time penalty (15% weight)
        - overshoot penalty (15% weight)
        - emergency reset penalty for hybrid controller (optional)

        Args:
            params: Controller-specific parameter vector

        Returns:
            Dictionary with metrics and fitness score
        """
        chattering_values = []
        settling_values = []
        overshoot_values = []
        energy_values = []
        reset_rates = []

        for run_idx in range(self.n_monte_carlo_runs):
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

            try:
                # Create controller with boundary layer
                controller = self._create_controller_with_params(params)

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

                # Chattering index (FFT-based)
                chattering_index = self._compute_chattering_index(controls, dt=0.01)
                chattering_values.append(chattering_index)

                # Settling time
                theta1 = states[:, 1]
                theta2 = states[:, 2]
                settling_mask = (np.abs(theta1) < 0.05) & (np.abs(theta2) < 0.05)

                settling_time = 10.0
                for i in range(len(settling_mask) - 50):  # 0.5s = 50 samples
                    if np.all(settling_mask[i:i+50]):
                        settling_time = time[i]
                        break
                settling_values.append(settling_time)

                # Overshoot
                max_overshoot = max(np.max(np.abs(theta1)), np.max(np.abs(theta2)))
                overshoot_values.append(max_overshoot)

                # Control energy
                control_energy = np.trapz(controls**2, time[:-1])
                energy_values.append(control_energy)

                if self.controller_type == 'hybrid_adaptive_sta_smc':
                    reset_rates.append(self._estimate_emergency_reset_rate(controls, controller))

            except Exception as e:
                logger.warning(f"Simulation failed for params ({self._format_params(params)}): {e}")
                # Penalize failed simulations
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
        chattering_term = 0.70 * mean_chattering
        settling_penalty = 0.15 * max(0, mean_settling - 5.0)
        overshoot_penalty = 0.15 * max(0, mean_overshoot - 0.3) * 10.0

        mean_reset_rate = float(np.mean(reset_rates)) if reset_rates else 0.0
        reset_penalty = 5.0 * mean_reset_rate

        fitness = chattering_term + settling_penalty + overshoot_penalty + reset_penalty

        return {
            'fitness': fitness,
            'chattering_index': mean_chattering,
            'settling_time': mean_settling,
            'overshoot': mean_overshoot,
            'control_energy': mean_energy,
            'chattering_std': np.std(chattering_values),
            'settling_std': np.std(settling_values),
            'overshoot_std': np.std(overshoot_values),
            'emergency_reset_rate': mean_reset_rate,
            'reset_penalty': reset_penalty
        }

    def _create_controller_with_params(self, params: np.ndarray):
        """Create controller with specified parameters."""
        if self.controller_type == 'classical_smc':
            epsilon, alpha = params
            return ClassicalSMC(
                gains=self.optimized_gains,
                max_force=150.0,
                boundary_layer=epsilon,
                boundary_layer_slope=alpha,
                switch_method='tanh'
            )
        elif self.controller_type == 'adaptive_smc':
            epsilon, alpha = params
            return AdaptiveSMC(
                gains=self.optimized_gains,
                dt=0.01,
                max_force=150.0,
                leak_rate=0.001,
                adapt_rate_limit=5.0,
                K_min=5.0,
                K_max=50.0,
                smooth_switch=True,
                boundary_layer=epsilon,      # Param 1: boundary layer thickness
                dead_zone=alpha,             # Param 2: dead zone (renamed from alpha)
                K_init=10.0,
                alpha=0.5                    # Fixed proportional weight (NOT optimization param)
            )
        elif self.controller_type == 'hybrid_adaptive_sta_smc':
            gamma1, gamma2, adapt_rate_limit, gain_leak = params
            # Set 2: Fixed parameters after emergency reset bug fix
            return HybridAdaptiveSTASMC(
                gains=self.optimized_gains,
                dt=0.01,
                max_force=150.0,
                k1_init=10.0,
                k2_init=5.0,
                gamma1=gamma1,
                gamma2=gamma2,
                adapt_rate_limit=adapt_rate_limit,
                gain_leak=gain_leak,
                sat_soft_width=0.05,         # Increased from 0.03
                dead_zone=0.01,              # Increased from 0.0
                damping_gain=3.0,
                k1_max=100.0,                # Increased from 50.0
                u_int_max=100.0              # Increased from 50.0
            )
        else:
            raise ValueError(f"Unknown controller type: {self.controller_type}")

    def _compute_chattering_index(self, controls: np.ndarray, dt: float = 0.01) -> float:
        """
        Compute chattering index using FFT analysis.

        Chattering is high-frequency oscillations, quantified as:
        - FFT power in high-frequency range (>10 Hz)
        - Normalized by total signal power

        Args:
            controls: Control signal array
            dt: Time step

        Returns:
            Chattering index (higher = more chattering)
        """
        # Compute FFT
        n = len(controls)
        fft_vals = np.fft.fft(controls)
        fft_freq = np.fft.fftfreq(n, dt)

        # Power spectrum (magnitude squared)
        power = np.abs(fft_vals)**2

        # High-frequency range (>10 Hz)
        high_freq_mask = np.abs(fft_freq) > 10.0

        # Chattering index: ratio of high-freq power to total power
        total_power = np.sum(power)
        high_freq_power = np.sum(power[high_freq_mask])

        if total_power > 0:
            chattering_index = (high_freq_power / total_power) * 100.0
        else:
            chattering_index = 0.0

        return chattering_index

    def _update_velocities_and_positions(self):
        """Update particle velocities and positions using PSO update rules."""
        for i in range(self.n_particles):
            r1 = np.random.random(self.param_dim)
            r2 = np.random.random(self.param_dim)

            cognitive_component = self.c1 * r1 * (self.personal_best_positions[i] - self.positions[i])
            social_component = self.c2 * r2 * (self.global_best_position - self.positions[i])
            self.velocities[i] = (
                self.w * self.velocities[i] +
                cognitive_component +
                social_component
            )

            self.positions[i] += self.velocities[i]
            self.positions[i] = np.clip(self.positions[i], self.bounds_min, self.bounds_max)

    def optimize(self) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Run PSO optimization.

        Returns:
            Best parameters and optimization history
        """
        logger.info("=" * 80)
        logger.info(f"Starting PSO Optimization for {self.controller_type}")
        logger.info("=" * 80)

        self._initialize_swarm()

        for iteration in range(self.n_iterations):
            logger.info(f"\nIteration {iteration + 1}/{self.n_iterations}")

            iteration_scores = []

            for i in range(self.n_particles):
                params = self.positions[i]

                metrics = self._compute_fitness(params)
                fitness = metrics['fitness']
                iteration_scores.append(fitness)

                reset_rate = metrics.get('emergency_reset_rate', 0.0)
                reset_str = ""
                if self.controller_type == 'hybrid_adaptive_sta_smc':
                    reset_str = f", reset_rate={reset_rate:.3f}"

                logger.info(
                    f"  Particle {i+1}: {self._format_params(params)} | "
                    f"Fitness={fitness:.4f} (chattering={metrics['chattering_index']:.2f}, "
                    f"settling={metrics['settling_time']:.2f}s{reset_str})"
                )

                if fitness < self.personal_best_scores[i]:
                    self.personal_best_scores[i] = fitness
                    self.personal_best_positions[i] = self.positions[i].copy()

                if fitness < self.global_best_score:
                    self.global_best_score = fitness
                    self.global_best_position = self.positions[i].copy()
                    logger.info(f"  [NEW GLOBAL BEST] {fitness:.4f}")

            best_iter = np.min(iteration_scores)
            mean_iter = np.mean(iteration_scores)
            self.iteration_history.append({
                'iteration': iteration + 1,
                'best_fitness': best_iter,
                'mean_fitness': mean_iter,
                'global_best_fitness': self.global_best_score,
                **{
                    f"best_{name}": float(value)
                    for name, value in zip(self.param_names, self.global_best_position)
                }
            })

            logger.info(
                f"  Iteration Summary: Best={best_iter:.4f}, Mean={mean_iter:.4f}, "
                f"Global Best={self.global_best_score:.4f}"
            )

            if iteration < self.n_iterations - 1:
                self._update_velocities_and_positions()

        logger.info("=" * 80)
        logger.info("PSO Optimization Complete")
        logger.info(f"Best Parameters: {self._format_params(self.global_best_position)}")
        logger.info(f"Best Fitness: {self.global_best_score:.4f}")
        logger.info("=" * 80)

        return self.global_best_position, {
            'iteration_history': self.iteration_history,
            'final_best_fitness': self.global_best_score
        }

    def validate_best_parameters(self,
                                params: np.ndarray,
                                n_runs: int = 100) -> pd.DataFrame:
        """
        Validate best parameters with extensive Monte Carlo runs.

        Args:
            params: Optimized parameter vector
            n_runs: Number of validation runs

        Returns:
            DataFrame with validation results
        """
        logger.info("=" * 80)
        logger.info(f"Validating Best Parameters (n={n_runs} runs)")
        logger.info(f"  {self._format_params(params)}")
        logger.info("=" * 80)

        results = []

        for run_idx in range(n_runs):
            if (run_idx + 1) % 10 == 0:
                logger.info(f"  Validation run {run_idx + 1}/{n_runs}")

            theta1_init = np.random.uniform(-0.3, 0.3)
            theta2_init = np.random.uniform(-0.3, 0.3)
            theta1_dot_init = np.random.uniform(-0.5, 0.5)
            theta2_dot_init = np.random.uniform(-0.5, 0.5)

            initial_state = np.array([
                0.0, theta1_init, theta2_init, 0.0, theta1_dot_init, theta2_dot_init
            ])

            try:
                controller = self._create_controller_with_params(params)
                dynamics = DIPDynamics(self.config.physics)

                t_arr, x_arr, u_arr = run_simulation(
                    controller=controller,
                    dynamics_model=dynamics,
                    sim_time=10.0,
                    dt=0.01,
                    initial_state=initial_state,
                    u_max=150.0
                )

                time = t_arr
                states = x_arr
                controls = u_arr

                chattering_index = self._compute_chattering_index(controls, dt=0.01)

                theta1 = states[:, 1]
                theta2 = states[:, 2]
                settling_mask = (np.abs(theta1) < 0.05) & (np.abs(theta2) < 0.05)

                settling_time = 10.0
                for i in range(len(settling_mask) - 50):
                    if np.all(settling_mask[i:i+50]):
                        settling_time = time[i]
                        break

                max_overshoot = max(np.max(np.abs(theta1)), np.max(np.abs(theta2)))
                control_energy = np.trapz(controls**2, time[:-1])
                reset_rate = 0.0
                if self.controller_type == 'hybrid_adaptive_sta_smc':
                    reset_rate = self._estimate_emergency_reset_rate(controls, controller)

                results.append({
                    'run': run_idx + 1,
                    'chattering_index': chattering_index,
                    'settling_time': settling_time,
                    'overshoot': max_overshoot,
                    'control_energy': control_energy,
                    'emergency_reset_rate': reset_rate,
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
                    'emergency_reset_rate': np.nan,
                    'theta1_init': theta1_init,
                    'theta2_init': theta2_init,
                    'success': False
                })

        df = pd.DataFrame(results)

        successful_runs = df[df['success']]
        n_successful = len(successful_runs)

        logger.info("\nValidation Statistics:")
        logger.info(f"  Successful runs: {n_successful}/{n_runs}")

        if n_successful > 0:
            metrics = ['chattering_index', 'settling_time', 'overshoot', 'control_energy']
            if self.controller_type == 'hybrid_adaptive_sta_smc':
                metrics.append('emergency_reset_rate')
            for metric in metrics:
                mean_val = successful_runs[metric].mean()
                std_val = successful_runs[metric].std()
                ci = 1.96 * std_val / np.sqrt(n_successful)
                logger.info(f"  {metric}: {mean_val:.4f} +- {std_val:.4f} (95% CI: +-{ci:.4f})")

        return df


def load_phase53_gains(controller_type: str) -> List[float]:
    """Load Phase 53 optimized gains for specified controller type."""
    gain_files = {
        'classical_smc': project_root / 'academic/paper/experiments/classical_smc/optimization/phases/phase53/optimized_gains_classical_smc_phase53.json',
        'adaptive_smc': project_root / 'academic/paper/experiments/adaptive_smc/optimization/phases/phase53/optimized_gains_adaptive_smc_phase53.json',
        'hybrid_adaptive_sta_smc': project_root / 'academic/paper/experiments/hybrid_adaptive_sta/optimization/phases/phase53/optimized_gains_hybrid_phase53.json'
    }

    if controller_type not in gain_files:
        raise ValueError(f"Unknown controller type: {controller_type}")

    with open(gain_files[controller_type], 'r') as f:
        data = json.load(f)

    # Extract gains from JSON
    if controller_type == 'classical_smc':
        gains = data['classical_smc']
    elif controller_type == 'adaptive_smc':
        gains = data['adaptive_smc']
    else:  # hybrid
        gains = data['hybrid_adaptive_sta_smc']

    logger.info(f"Loaded Phase 53 gains for {controller_type}: {gains}")
    return gains


def run_optimization_for_controller(controller_type: str,
                                    output_dir: Path,
                                    n_particles: int = 30,
                                    n_iterations: int = 50,
                                    seed: int = 42) -> Dict[str, Any]:
    """
    Run controller-specific chattering optimization for specified controller.

    Args:
        controller_type: Controller type
        output_dir: Output directory for results
        n_particles: PSO swarm size
        n_iterations: PSO iterations
        seed: Random seed

    Returns:
        Dictionary with optimization results
    """
    logger.info("\n" + "=" * 80)
    logger.info(f"OPTIMIZING CHATTERING PARAMETERS FOR: {controller_type.upper()}")
    logger.info("=" * 80)

    # Load Phase 53 optimized gains
    gains = load_phase53_gains(controller_type)

    # Create optimizer
    optimizer = ChatteringBoundaryLayerPSO(
        controller_type=controller_type,
        optimized_gains=gains,
        n_particles=n_particles,
        n_iterations=n_iterations,
        n_monte_carlo_runs=5,
        seed=seed
    )

    # Run optimization
    best_params, history = optimizer.optimize()
    best_param_map = {
        name: float(value) for name, value in zip(optimizer.param_names, best_params)
    }

    # Save iteration history
    iteration_df = pd.DataFrame(history['iteration_history'])
    iteration_csv = output_dir / f"{controller_type}_boundary_layer_optimization.csv"
    iteration_csv.parent.mkdir(parents=True, exist_ok=True)
    iteration_df.to_csv(iteration_csv, index=False)
    logger.info(f"\nSaved iteration history to: {iteration_csv}")

    # Validate with 100 runs
    logger.info("\nRunning validation (100 runs)...")
    validation_df = optimizer.validate_best_parameters(best_params, n_runs=100)

    # Save validation results
    validation_csv = output_dir / f"{controller_type}_boundary_layer_validation.csv"
    validation_df.to_csv(validation_csv, index=False)
    logger.info(f"Saved validation results to: {validation_csv}")

    # Compute statistics
    successful = validation_df[validation_df['success']]
    n_successful = len(successful)

    if n_successful > 0:
        mean_chattering = successful['chattering_index'].mean()
        std_chattering = successful['chattering_index'].std()
        ci_chattering = 1.96 * std_chattering / np.sqrt(n_successful)

        mean_settling = successful['settling_time'].mean()
        std_settling = successful['settling_time'].std()
        ci_settling = 1.96 * std_settling / np.sqrt(n_successful)

        mean_overshoot = successful['overshoot'].mean()
        std_overshoot = successful['overshoot'].std()
        ci_overshoot = 1.96 * std_overshoot / np.sqrt(n_successful)

        mean_energy = successful['control_energy'].mean()
        std_energy = successful['control_energy'].std()

        summary_stats = {
            'n_runs': int(n_successful),
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
        }

        if controller_type == 'hybrid_adaptive_sta_smc':
            mean_reset = successful['emergency_reset_rate'].mean()
            std_reset = successful['emergency_reset_rate'].std()
            ci_reset = 1.96 * std_reset / np.sqrt(n_successful)
            summary_stats['emergency_reset_rate'] = {
                'mean': float(mean_reset),
                'std': float(std_reset),
                'ci_95': float(ci_reset)
            }

        # Summary
        summary = {
            'controller_type': controller_type,
            'phase53_gains': gains,
            'best_parameters': best_param_map,
            'pso_optimization': {
                'n_particles': n_particles,
                'n_iterations': n_iterations,
                'final_fitness': history['final_best_fitness']
            },
            'validation_statistics': summary_stats
        }

        # Save summary
        summary_file = output_dir / f"{controller_type}_boundary_layer_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Saved summary to: {summary_file}")

        logger.info("\n" + "=" * 80)
        logger.info(f"RESULTS FOR {controller_type.upper()}")
        logger.info("=" * 80)
        best_param_str = ", ".join(
            f"{name}={_format_param_value(value)}" for name, value in best_param_map.items()
        )
        logger.info(f"Best Parameters: {best_param_str}")
        logger.info(f"Chattering Index: {mean_chattering:.4f} +- {std_chattering:.4f}")
        logger.info(f"Settling Time: {mean_settling:.4f} +- {std_settling:.4f}s")
        logger.info(f"Overshoot: {mean_overshoot:.4f} +- {std_overshoot:.4f} rad")
        if controller_type == 'hybrid_adaptive_sta_smc':
            logger.info(f"Emergency Reset Rate: {mean_reset:.4f} +- {std_reset:.4f}")
        logger.info("=" * 80)

        return summary
    else:
        logger.error(f"All validation runs failed for {controller_type}!")
        return None


def main():
    """Main execution function."""
    logger.info("=" * 80)
    logger.info("PHASE 2: CHATTERING PARAMETER OPTIMIZATION")
    logger.info("=" * 80)
    logger.info("\nOptimizing parameters for 3 controllers:")
    logger.info("  1. Classical SMC")
    logger.info("  2. Adaptive SMC")
    logger.info("  3. Hybrid Adaptive STA SMC")
    logger.info("\nApproach: fix Phase 53 gains, optimize controller-specific parameters")
    logger.info("=" * 80)

    # Output directory
    output_base = project_root / "academic/paper/experiments"

    # Controller configurations
    controllers = [
        ('classical_smc', output_base / 'classical_smc/boundary_layer'),
        ('adaptive_smc', output_base / 'adaptive_smc/boundary_layer'),
        ('hybrid_adaptive_sta_smc', output_base / 'hybrid_adaptive_sta/boundary_layer')
    ]

    # Run optimizations sequentially
    results = {}
    for controller_type, output_dir in controllers:
        try:
            result = run_optimization_for_controller(
                controller_type=controller_type,
                output_dir=output_dir,
                n_particles=30,
                n_iterations=50,
                seed=42
            )
            results[controller_type] = result
        except Exception as e:
            logger.error(f"Optimization failed for {controller_type}: {e}")
            results[controller_type] = None

    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 2 COMPLETE - CHATTERING OPTIMIZATION SUMMARY")
    logger.info("=" * 80)

    for controller_type, result in results.items():
        if result:
            logger.info(f"\n{controller_type.upper()}:")
            logger.info(f"  Chattering: {result['validation_statistics']['chattering_index']['mean']:.4f}")
            logger.info(f"  Settling: {result['validation_statistics']['settling_time']['mean']:.4f}s")
            logger.info(f"  Status: [OK] SUCCESSFUL")
        else:
            logger.info(f"\n{controller_type.upper()}:")
            logger.info(f"  Status: [ERROR] FAILED")

    logger.info("\n" + "=" * 80)
    logger.info("All optimizations complete. Results saved to academic/paper/experiments/")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
