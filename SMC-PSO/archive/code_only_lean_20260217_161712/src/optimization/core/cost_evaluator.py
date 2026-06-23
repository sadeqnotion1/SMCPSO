#======================================================================================\
#==================== src/optimization/core/cost_evaluator.py ====================\
#======================================================================================\
"""
Shared Cost Evaluation for Controller Optimization

This module provides a unified cost evaluator for all optimization algorithms
(PSO, GA, DE, etc.). It replaces placeholder cost functions with real simulation-based
evaluation, ensuring fair comparison across optimizers.

Key Features:
- Real trajectory simulation via simulate_system_batch()
- Multi-metric cost: ISE, control effort, control slew, sliding variable energy
- Instability detection and penalties
- Physics uncertainty support (multi-scenario evaluation)
- Normalization for balanced cost components

Usage:
    from src.optimization.core.cost_evaluator import ControllerCostEvaluator

    evaluator = ControllerCostEvaluator(controller_factory, config, seed=42)

    # Evaluate single controller
    cost = evaluator.evaluate_single(gains)

    # Evaluate batch (for population-based optimizers)
    costs = evaluator.evaluate_batch(population)

Author: Claude Code + AI-assisted development
Date: November 2025
"""

from __future__ import annotations

import logging
import numpy as np
from typing import Callable, Optional, Any, Tuple
from pathlib import Path

from src.config import ConfigSchema, load_config
from src.utils.seed import create_rng
from src.simulation.engines.vector_sim import simulate_system_batch


logger = logging.getLogger(__name__)


class ControllerCostEvaluator:
    """Unified cost evaluator for controller optimization algorithms.

    This class encapsulates the cost computation logic shared across all optimizers
    (PSO, GA, DE). It simulates controller performance and computes a multi-objective
    cost based on state error, control effort, control slew, and stability metrics.

    Attributes:
        controller_factory: Callable that creates a controller given gains
        config: System configuration (physics, simulation, cost weights)
        seed: Random seed for reproducibility
        instability_penalty: Penalty for unstable/divergent simulations
    """

    def __init__(self,
                 controller_factory: Callable,
                 config: Any,
                 seed: Optional[int] = None,
                 instability_penalty_factor: float = 100.0):
        """Initialize cost evaluator.

        Parameters
        ----------
        controller_factory : Callable[[np.ndarray], Controller]
            Factory function that creates a controller given gain parameters
        config : ConfigSchema or path-like
            System configuration object or path to YAML file
        seed : int, optional
            Random seed for reproducibility
        instability_penalty_factor : float, optional
            Scale factor for instability penalty (default: 100.0)
        """
        # Load configuration if path provided
        if isinstance(config, (str, Path)):
            self.cfg: ConfigSchema = load_config(config)
        else:
            self.cfg = config

        self.controller_factory = controller_factory
        self.physics_cfg = self.cfg.physics
        self.sim_cfg = self.cfg.simulation
        self.cost_cfg = self.cfg.cost_function
        self.uncertainty_cfg = getattr(self.cfg, "physics_uncertainty", None)

        # Random number generator
        default_seed = seed if seed is not None else getattr(self.cfg, "global_seed", None)
        self.seed: Optional[int] = int(default_seed) if default_seed is not None else None
        self.rng: np.random.Generator = create_rng(self.seed)

        # Cost weights
        self.weights = self.cost_cfg.weights

        # Normalization thresholds
        norms = getattr(self.cost_cfg, "normalisation", None)
        if norms is not None:
            self.norm_ise = float(getattr(norms, "state_error", 1.0))
            self.norm_u = float(getattr(norms, "control_effort", 1.0))
            self.norm_du = float(getattr(norms, "control_rate", 1.0))
            self.norm_sigma = float(getattr(norms, "sliding", 1.0))
        else:
            self.norm_ise = self.norm_u = self.norm_du = self.norm_sigma = 1.0

        # Instability penalty
        explicit_penalty = getattr(self.cost_cfg, "instability_penalty", None)
        if explicit_penalty is not None:
            self.instability_penalty = float(explicit_penalty)
        else:
            denom_sum = self.norm_ise + self.norm_u + self.norm_du + self.norm_sigma
            if not np.isfinite(denom_sum) or denom_sum <= 0.0:
                denom_sum = 1.0
            self.instability_penalty = float(instability_penalty_factor * denom_sum)

        # Extract u_max from config or use default
        try:
            baseline_ctrl = controller_factory(np.ones(6))  # Dummy gains
            self.u_max = float(getattr(baseline_ctrl, "max_force", 150.0))
        except Exception:
            self.u_max = 150.0

        logger.info("ControllerCostEvaluator initialized: instability_penalty=%.2f, u_max=%.2f",
                   self.instability_penalty, self.u_max)

    def evaluate_single(self, gains: np.ndarray) -> float:
        """Evaluate cost for a single set of controller gains.

        Parameters
        ----------
        gains : np.ndarray, shape (n_params,)
            Controller gain parameters

        Returns
        -------
        cost : float
            Scalar cost value (lower is better)
        """
        # Convert to 2D array for batch evaluation
        population = gains.reshape(1, -1)
        costs = self.evaluate_batch(population)
        return costs[0]

    def evaluate_batch(self, population: np.ndarray) -> np.ndarray:
        """Evaluate cost for a batch of controller gains (population).

        Parameters
        ----------
        population : np.ndarray, shape (n_individuals, n_params)
            Population of gain parameter sets

        Returns
        -------
        costs : np.ndarray, shape (n_individuals,)
            Cost for each individual in the population
        """
        B = population.shape[0]

        # Validate gains (check bounds, NaN, etc.)
        valid_mask = np.all(np.isfinite(population), axis=1)
        violation_mask = ~valid_mask

        if violation_mask.all():
            # All invalid - return penalties
            return np.full(B, self.instability_penalty, dtype=float)

        valid_particles = population[valid_mask]

        # Run simulation
        try:
            t, x_b, u_b, sigma_b = simulate_system_batch(
                controller_factory=self.controller_factory,
                particles=valid_particles,
                sim_time=self.sim_cfg.duration,
                dt=self.sim_cfg.dt,
                u_max=self.u_max,
            )
        except Exception as e:
            logger.warning("Simulation failed: %s", e)
            return np.full(B, self.instability_penalty, dtype=float)

        # Compute costs from trajectories
        J_valid = self._compute_cost_from_traj(t, x_b, u_b, sigma_b)

        # Detect NaN/instability
        nan_mask = (
            (~np.all(np.isfinite(x_b), axis=(1, 2)))
            | (~np.all(np.isfinite(u_b), axis=1))
            | (~np.all(np.isfinite(sigma_b), axis=1))
        )

        if nan_mask.any():
            J_valid[nan_mask] = self.instability_penalty

        # Merge valid and invalid costs
        if violation_mask.any():
            J_full = np.full(B, self.instability_penalty, dtype=float)
            J_full[valid_mask] = J_valid
            return J_full

        return J_valid

    def _compute_cost_from_traj(self, t: np.ndarray, x_b: np.ndarray,
                                u_b: np.ndarray, sigma_b: np.ndarray) -> np.ndarray:
        """Compute cost from simulated trajectories.

        Cost combines:
        - State error (ISE): Integrated squared error across all states
        - Control effort: Integrated squared control input
        - Control slew: Integrated squared control rate
        - Sliding variable energy: Integrated squared sliding variable

        Instability penalties are applied when trajectories fail early.

        Parameters
        ----------
        t : np.ndarray, shape (N+1,)
            Time vector
        x_b : np.ndarray, shape (B, N+1, n_states)
            State trajectories for batch
        u_b : np.ndarray, shape (B, N+1)
            Control trajectories
        sigma_b : np.ndarray, shape (B, N+1)
            Sliding variable trajectories

        Returns
        -------
        costs : np.ndarray, shape (B,)
            Cost for each trajectory
        """
        dt = np.diff(t)
        dt_b = dt[None, :]
        N = len(dt)
        B = x_b.shape[0]

        if N == 0:
            return np.zeros(B, dtype=float)

        # Instability detection
        fall_mask = np.abs(x_b[:, :, 1]) > (0.5 * np.pi)  # Pendulum angle > 90 deg
        explodes_mask = np.any(np.abs(x_b) > 1e6, axis=2)
        unstable_mask = fall_mask | explodes_mask

        # Find first failure timestep for each trajectory
        temp = np.full((B, N + 1), N + 1)
        temp[unstable_mask] = np.tile(np.arange(N + 1), (B, 1))[unstable_mask]
        failure_steps = np.min(temp, axis=1)

        # Mask to only integrate up to failure point
        time_mask = (np.arange(N)[None, :] < (failure_steps - 1)[:, None])

        # State error (ISE): integrate squared error across all state variables
        ise = np.sum((x_b[:, :-1, :] ** 2 * dt_b[:, :, None]) * time_mask[:, :, None], axis=(1, 2))
        ise_n = self._normalise(ise, self.norm_ise)

        # Control effort
        u_b_trunc = u_b[:, :N] if u_b.shape[1] > N else u_b
        u_sq = np.sum((u_b_trunc ** 2 * dt_b) * time_mask, axis=1)
        u_n = self._normalise(u_sq, self.norm_u)

        # Control slew (rate)
        du = np.diff(u_b, axis=1, prepend=u_b[:, 0:1])
        du_trunc = du[:, :N] if du.shape[1] > N else du
        du_sq = np.sum((du_trunc ** 2 * dt_b) * time_mask, axis=1)
        du_n = self._normalise(du_sq, self.norm_du)

        # Sliding variable energy
        sigma_b_trunc = sigma_b[:, :N] if sigma_b.shape[1] > N else sigma_b
        sigma_sq = np.sum((sigma_b_trunc ** 2 * dt_b) * time_mask, axis=1)
        sigma_n = self._normalise(sigma_sq, self.norm_sigma)

        # Weighted combination
        w = self.weights
        cost = (
            w.state_error * ise_n +
            w.control_effort * u_n +
            w.control_rate * du_n +
            w.sliding * sigma_n
        )

        # Apply instability penalty for trajectories that failed early
        failed_early = (failure_steps < N)
        if np.any(failed_early):
            # Graded penalty based on when failure occurred
            penalty_scale = 1.0 + (N - failure_steps[failed_early]) / N
            cost[failed_early] = cost[failed_early] * penalty_scale

        return cost

    def _normalise(self, values: np.ndarray, threshold: float) -> np.ndarray:
        """Normalize cost component to prevent numerical issues.

        Parameters
        ----------
        values : np.ndarray
            Raw cost values
        threshold : float
            Normalization threshold

        Returns
        -------
        normalized : np.ndarray
            Normalized values
        """
        if threshold > 1e-12:
            return values / threshold
        return values


def create_cost_evaluator(controller_factory: Callable,
                          config: Any,
                          seed: Optional[int] = None) -> ControllerCostEvaluator:
    """Factory function to create a cost evaluator.

    Convenience function for creating evaluators with default settings.

    Parameters
    ----------
    controller_factory : Callable
        Factory function for creating controllers
    config : ConfigSchema or path-like
        System configuration
    seed : int, optional
        Random seed

    Returns
    -------
    evaluator : ControllerCostEvaluator
        Configured cost evaluator instance
    """
    return ControllerCostEvaluator(controller_factory, config, seed)
