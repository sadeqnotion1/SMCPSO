#======================================================================================\
#================= src/optimization/core/robust_cost_evaluator.py ==================\
#======================================================================================\
"""
Robust Cost Evaluator for Multi-Scenario Controller Optimization

This module extends ControllerCostEvaluator with multi-scenario support to address
overfitting issues (MT-7). Instead of evaluating controller performance on a single
initial condition, RobustCostEvaluator tests across diverse scenarios to ensure
robust performance across the full operating envelope.

Problem Addressed (MT-7):
- Single-scenario PSO: 50.4x chattering degradation on realistic perturbations
- Single-scenario PSO: 9.8% success rate on ±0.3 rad initial conditions
- Root cause: Optimization never encounters challenging scenarios during training

Solution:
- Multi-scenario evaluation: 15 diverse initial conditions per fitness computation
- Scenario distribution: 20% nominal (±0.05 rad), 30% moderate (±0.15 rad),
  50% large (±0.3 rad)
- Robust fitness: J = mean_cost + α × worst_cost (α=0.3 default)

Expected Results:
- Chattering degradation: 50.4x → <5x
- Success rate: 9.8% → >85%
- Runtime: 10-15x longer (parallelizable to 2-3x)

Usage:
    from src.optimization.core.robust_cost_evaluator import RobustCostEvaluator

    evaluator = RobustCostEvaluator(
        controller_factory=controller_factory,
        config=config,
        n_scenarios=15,
        worst_case_weight=0.3,
        seed=42
    )

    # Single controller
    cost = evaluator.evaluate_single(gains)

    # Population (for PSO/GA/DE)
    costs = evaluator.evaluate_batch_robust(population)

Author: Claude Code + AI-assisted development
Date: November 2025
"""

from __future__ import annotations

import logging
import numpy as np
from typing import Callable, Optional, Any, List, Dict
from pathlib import Path

from src.config import ConfigSchema, load_config
from src.optimization.core.cost_evaluator import ControllerCostEvaluator


logger = logging.getLogger(__name__)


class RobustCostEvaluator(ControllerCostEvaluator):
    """Multi-scenario cost evaluator for robust controller optimization.

    Extends ControllerCostEvaluator with the ability to evaluate controller performance
    across diverse initial conditions, preventing overfitting to narrow training scenarios.

    Attributes:
        n_scenarios: Number of initial condition scenarios
        worst_case_weight: Weight for worst-case penalty in cost aggregation (α)
        scenarios: List of initial condition arrays
        scenario_distribution: Fraction of nominal/moderate/large perturbations
        nominal_range: Maximum nominal perturbation (rad)
        moderate_range: Maximum moderate perturbation (rad)
        large_range: Maximum large perturbation (rad)
    """

    def __init__(self,
                 controller_factory: Callable,
                 config: Any,
                 seed: Optional[int] = None,
                 n_scenarios: int = 15,
                 worst_case_weight: float = 0.3,
                 scenario_distribution: Optional[Dict[str, float]] = None,
                 nominal_range: float = 0.05,
                 moderate_range: float = 0.15,
                 large_range: float = 0.3):
        """Initialize robust cost evaluator.

        Parameters
        ----------
        controller_factory : Callable[[np.ndarray], Controller]
            Factory function that creates a controller given gains
        config : ConfigSchema or path-like
            System configuration
        seed : int, optional
            Random seed for scenario generation
        n_scenarios : int, default=15
            Number of initial condition scenarios to evaluate
        worst_case_weight : float, default=0.3
            Weight α for worst-case penalty: J = mean + α*max
        scenario_distribution : dict, optional
            Fraction of nominal/moderate/large scenarios.
            Default: {'nominal': 0.2, 'moderate': 0.3, 'large': 0.5}
        nominal_range : float, default=0.05
            Maximum nominal angle perturbation (rad)
        moderate_range : float, default=0.15
            Maximum moderate angle perturbation (rad)
        large_range : float, default=0.3
            Maximum large angle perturbation (rad)
        """
        # Initialize base evaluator
        super().__init__(controller_factory, config, seed)

        # Robust optimization parameters
        self.n_scenarios = n_scenarios
        self.worst_case_weight = worst_case_weight
        self.nominal_range = nominal_range
        self.moderate_range = moderate_range
        self.large_range = large_range

        # Scenario distribution
        if scenario_distribution is None:
            self.scenario_distribution = {
                'nominal': 0.2,
                'moderate': 0.3,
                'large': 0.5
            }
        else:
            self.scenario_distribution = scenario_distribution

        # Validate distribution
        total_frac = sum(self.scenario_distribution.values())
        if not np.isclose(total_frac, 1.0):
            raise ValueError(
                f"Scenario distribution must sum to 1.0, got {total_frac}"
            )

        # Generate scenarios
        self.scenarios = self._generate_scenarios()

        logger.info(
            "RobustCostEvaluator initialized: n_scenarios=%d, α=%.2f, "
            "distribution=%s",
            self.n_scenarios, self.worst_case_weight, self.scenario_distribution
        )

    def _generate_scenarios(self) -> List[np.ndarray]:
        """Generate diverse initial condition scenarios.

        Creates a set of initial conditions distributed across nominal, moderate,
        and large perturbations according to scenario_distribution.

        Returns
        -------
        scenarios : List[np.ndarray]
            List of initial condition arrays, each shape (6,) for DIP:
            [x, θ1, θ2, x_dot, θ1_dot, θ2_dot]
        """
        scenarios = []

        # Calculate scenario counts
        n_nominal = int(self.n_scenarios * self.scenario_distribution['nominal'])
        n_moderate = int(self.n_scenarios * self.scenario_distribution['moderate'])
        n_large = self.n_scenarios - n_nominal - n_moderate  # Remainder

        logger.debug(
            "Generating scenarios: %d nominal, %d moderate, %d large",
            n_nominal, n_moderate, n_large
        )

        # 1. Nominal scenarios (±0.05 rad)
        for _ in range(n_nominal):
            ic = np.array([
                0.0,  # Cart at origin
                self.rng.uniform(-self.nominal_range, self.nominal_range),  # θ1
                self.rng.uniform(-self.nominal_range, self.nominal_range),  # θ2
                0.0,  # At rest
                0.0,
                0.0
            ])
            scenarios.append(ic)

        # 2. Moderate scenarios (±0.15 rad)
        for _ in range(n_moderate):
            ic = np.array([
                0.0,
                self.rng.uniform(-self.moderate_range, self.moderate_range),  # θ1
                self.rng.uniform(-self.moderate_range, self.moderate_range),  # θ2
                self.rng.uniform(-0.2, 0.2),  # Small velocity
                self.rng.uniform(-0.2, 0.2),
                self.rng.uniform(-0.2, 0.2)
            ])
            scenarios.append(ic)

        # 3. Large scenarios (±0.3 rad) - MT-7 failure zone
        for _ in range(n_large):
            ic = np.array([
                0.0,
                self.rng.uniform(-self.large_range, self.large_range),  # θ1
                self.rng.uniform(-self.large_range, self.large_range),  # θ2
                self.rng.uniform(-0.5, 0.5),  # Realistic velocity
                self.rng.uniform(-0.5, 0.5),
                self.rng.uniform(-0.5, 0.5)
            ])
            scenarios.append(ic)

        logger.info("Generated %d scenarios for robust evaluation", len(scenarios))
        return scenarios

    def evaluate_batch_robust(self, population: np.ndarray) -> np.ndarray:
        """Evaluate population across all scenarios (robust fitness).

        This is the core robust optimization method. For each individual in the
        population, evaluates cost on all scenarios and aggregates using:
            J_robust = mean(costs) + α × max(costs)

        Parameters
        ----------
        population : np.ndarray, shape (n_individuals, n_params)
            Population of gain parameter sets

        Returns
        -------
        costs : np.ndarray, shape (n_individuals,)
            Robust cost for each individual
        """
        B = population.shape[0]

        # Storage for costs across scenarios
        # Shape: (B, n_scenarios)
        scenario_costs = np.zeros((B, self.n_scenarios))

        # Evaluate each scenario
        for j, scenario_ic in enumerate(self.scenarios):
            # Evaluate population on this scenario
            costs_j = self._evaluate_scenario(population, scenario_ic)
            scenario_costs[:, j] = costs_j

        # Aggregate costs: mean + α*worst
        mean_cost = scenario_costs.mean(axis=1)
        worst_cost = scenario_costs.max(axis=1)
        robust_cost = mean_cost + self.worst_case_weight * worst_cost

        # Log statistics
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "Robust cost stats: mean=%.4f±%.4f, worst=%.4f±%.4f, "
                "robust=%.4f±%.4f",
                mean_cost.mean(), mean_cost.std(),
                worst_cost.mean(), worst_cost.std(),
                robust_cost.mean(), robust_cost.std()
            )

        return robust_cost

    def _evaluate_scenario(self, population: np.ndarray,
                          scenario_ic: np.ndarray) -> np.ndarray:
        """Evaluate population on a single scenario (initial condition).

        Parameters
        ----------
        population : np.ndarray, shape (B, n_params)
            Population of gain parameters
        scenario_ic : np.ndarray, shape (6,)
            Initial condition for this scenario

        Returns
        -------
        costs : np.ndarray, shape (B,)
            Cost for each individual on this scenario
        """
        B = population.shape[0]

        # Validate gains (check bounds, NaN, etc.)
        valid_mask = np.all(np.isfinite(population), axis=1)
        violation_mask = ~valid_mask

        if violation_mask.all():
            # All invalid - return penalties
            return np.full(B, self.instability_penalty, dtype=float)

        valid_particles = population[valid_mask]

        # Import here to avoid circular dependency
        from src.simulation.engines.vector_sim import simulate_system_batch

        # Run simulation with this scenario's initial condition
        try:
            t, x_b, u_b, sigma_b = simulate_system_batch(
                controller_factory=self.controller_factory,
                particles=valid_particles,
                sim_time=self.sim_cfg.duration,
                dt=self.sim_cfg.dt,
                u_max=self.u_max,
                initial_state=scenario_ic,  # Override IC for this scenario!
            )
        except Exception as e:
            logger.warning("Simulation failed for scenario: %s", e)
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

    def evaluate_single_robust(self, gains: np.ndarray) -> float:
        """Evaluate single controller across all scenarios.

        Convenience method for single-controller robust evaluation.

        Parameters
        ----------
        gains : np.ndarray, shape (n_params,)
            Controller gain vector

        Returns
        -------
        cost : float
            Robust cost (mean + α*worst across scenarios)
        """
        population = gains.reshape(1, -1)
        costs = self.evaluate_batch_robust(population)
        return costs[0]

    def get_scenario_breakdown(self, gains: np.ndarray) -> Dict[str, Any]:
        """Get detailed cost breakdown across scenarios for analysis.

        Useful for debugging and understanding which scenarios are challenging.

        Parameters
        ----------
        gains : np.ndarray, shape (n_params,)
            Controller gains to evaluate

        Returns
        -------
        breakdown : dict
            Dictionary with keys:
            - 'scenario_costs': List of costs for each scenario
            - 'mean_cost': Average cost
            - 'worst_cost': Maximum cost
            - 'best_cost': Minimum cost
            - 'robust_cost': Aggregated robust cost
            - 'scenario_ics': List of initial conditions
        """
        population = gains.reshape(1, -1)

        # Evaluate each scenario
        scenario_costs = []
        for scenario_ic in self.scenarios:
            cost = self._evaluate_scenario(population, scenario_ic)[0]
            scenario_costs.append(cost)

        mean_cost = np.mean(scenario_costs)
        worst_cost = np.max(scenario_costs)
        best_cost = np.min(scenario_costs)
        robust_cost = mean_cost + self.worst_case_weight * worst_cost

        return {
            'scenario_costs': scenario_costs,
            'mean_cost': mean_cost,
            'worst_cost': worst_cost,
            'best_cost': best_cost,
            'robust_cost': robust_cost,
            'scenario_ics': self.scenarios,
            'n_scenarios': self.n_scenarios,
            'worst_case_weight': self.worst_case_weight
        }


def create_robust_cost_evaluator(
    controller_factory: Callable,
    config: Any,
    seed: Optional[int] = None,
    n_scenarios: int = 15,
    worst_case_weight: float = 0.3
) -> RobustCostEvaluator:
    """Factory function to create a robust cost evaluator.

    Convenience function with sensible defaults.

    Parameters
    ----------
    controller_factory : Callable
        Factory for creating controllers
    config : ConfigSchema or path-like
        System configuration
    seed : int, optional
        Random seed
    n_scenarios : int, default=15
        Number of scenarios
    worst_case_weight : float, default=0.3
        Worst-case penalty weight

    Returns
    -------
    evaluator : RobustCostEvaluator
        Configured robust cost evaluator
    """
    return RobustCostEvaluator(
        controller_factory=controller_factory,
        config=config,
        seed=seed,
        n_scenarios=n_scenarios,
        worst_case_weight=worst_case_weight
    )
