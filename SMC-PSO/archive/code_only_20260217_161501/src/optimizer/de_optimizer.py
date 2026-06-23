#======================================================================================\
#============================= src/optimizer/de_optimizer.py ===========================\
#======================================================================================\
"""
Differential Evolution (DE) tuner for sliding-mode controllers.
This module provides a high-level DETuner class that wraps the modular
DifferentialEvolution implementation for controller parameter optimization.
It follows the same interface pattern as PSOTuner/GATuner for consistency.

Key features:
- Multiple DE strategies: rand/1/bin, best/1/bin, currentToBest/1/bin
- Adaptive parameter adjustment (F and CR)
- Constraint handling via penalty methods
- Batch fitness evaluation for performance
- Compatible with all controller types

Usage:
    from src.optimizer.de_optimizer import DETuner
    from src.controllers.factory import create_controller
    from src.config import load_config

    config = load_config("config.yaml")
    controller_factory = lambda gains: create_controller('classical_smc', config=config, gains=gains)

    tuner = DETuner(controller_factory, config=config, seed=42)
    best_gains, best_cost = tuner.optimize(
        population_size=50,
        max_generations=100,
        dimension=6,
        lower_bounds=np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1]),
        upper_bounds=np.array([100, 100, 100, 100, 100, 100])
    )

Author: Claude Code + AI-assisted development
Date: November 2025
"""

import numpy as np
import logging
from typing import Callable, Optional, Tuple, Any
from dataclasses import dataclass

from src.optimization.core.interfaces import ParameterSpace
from src.optimization.core.cost_evaluator import ControllerCostEvaluator
from src.optimization.algorithms.evolutionary.differential import DifferentialEvolution


logger = logging.getLogger(__name__)


@dataclass
class DEConfig:
    """Configuration for Differential Evolution optimizer."""
    population_size: int = 50
    mutation_factor: float = 0.8
    crossover_probability: float = 0.7
    strategy: str = 'best/1/bin'  # Options: rand/1/bin, best/1/bin, currentToBest/1/bin
    max_iterations: int = 100
    tolerance: float = 1e-6
    adaptive_parameters: bool = True
    verbose: bool = False


class DETuner:
    """High-level wrapper for Differential Evolution optimization of controller gains.

    This class provides a simplified interface for optimizing controller parameters
    using the Differential Evolution algorithm. It handles fitness function creation,
    parameter space setup, and result extraction.

    Attributes:
        controller_factory: Callable that creates a controller given gains
        config: System configuration object
        seed: Random seed for reproducibility
        de_config: DE-specific configuration
    """

    def __init__(self,
                 controller_factory: Callable,
                 config: Any,
                 seed: Optional[int] = None,
                 de_config: Optional[DEConfig] = None):
        """Initialize DE tuner.

        Parameters
        ----------
        controller_factory : Callable[[np.ndarray], Controller]
            Factory function that creates a controller given gain parameters
        config : Config
            System configuration (dynamics, simulation settings)
        seed : int, optional
            Random seed for reproducibility
        de_config : DEConfig, optional
            DE configuration (defaults to DEConfig())
        """
        self.controller_factory = controller_factory
        self.config = config
        self.seed = seed
        self.de_config = de_config or DEConfig()

        # Setup random number generator
        self.rng = np.random.default_rng(seed)

        # Create shared cost evaluator (handles all simulation and cost computation)
        self.cost_evaluator = ControllerCostEvaluator(
            controller_factory=controller_factory,
            config=config,
            seed=seed
        )

        logger.info("DETuner initialized with strategy=%s, population_size=%d",
                   self.de_config.strategy, self.de_config.population_size)

    def optimize(self,
                 population_size: int = 50,
                 max_generations: int = 100,
                 dimension: int = 6,
                 lower_bounds: Optional[np.ndarray] = None,
                 upper_bounds: Optional[np.ndarray] = None,
                 strategy: str = 'best/1/bin',
                 mutation_factor: float = 0.8,
                 crossover_probability: float = 0.7,
                 adaptive_parameters: bool = True) -> Tuple[np.ndarray, float]:
        """Run Differential Evolution to optimize controller gains.

        Parameters
        ----------
        population_size : int
            Population size (recommended: 10-20 * dimension)
        max_generations : int
            Maximum number of generations
        dimension : int
            Number of gain parameters to optimize
        lower_bounds : np.ndarray, optional
            Lower bounds for each parameter (default: all 0.1)
        upper_bounds : np.ndarray, optional
            Upper bounds for each parameter (default: all 100.0)
        strategy : str
            DE strategy ('rand/1/bin', 'best/1/bin', 'currentToBest/1/bin')
        mutation_factor : float
            Differential weight F (0 < F <= 2)
        crossover_probability : float
            Crossover probability CR (0 <= CR <= 1)
        adaptive_parameters : bool
            Whether to adapt F and CR during evolution

        Returns
        -------
        best_gains : np.ndarray
            Optimized gain parameters
        best_cost : float
            Best objective function value achieved
        """
        # Set default bounds if not provided
        if lower_bounds is None:
            lower_bounds = np.full(dimension, 0.1)
        if upper_bounds is None:
            upper_bounds = np.full(dimension, 100.0)

        # Create parameter space
        param_space = ParameterSpace(lower_bounds, upper_bounds)

        # Create DE optimizer
        de = DifferentialEvolution(
            parameter_space=param_space,
            population_size=population_size,
            mutation_factor=mutation_factor,
            crossover_probability=crossover_probability,
            strategy=strategy,
            max_iterations=max_generations,
            tolerance=self.de_config.tolerance,
            adaptive_parameters=adaptive_parameters
        )

        # Define optimization problem (fitness function)
        from src.optimization.core.interfaces import OptimizationProblem

        def objective(gains: np.ndarray) -> float:
            """Cost function: simulates controller and computes performance metric.

            Uses shared ControllerCostEvaluator for real simulation-based
            cost computation (same as PSO and GA).
            """
            return self.cost_evaluator.evaluate_single(gains)

        def batch_objective(population: np.ndarray) -> np.ndarray:
            """Batch evaluation of fitness for entire population."""
            return self.cost_evaluator.evaluate_batch(population)

        # Create problem wrapper
        class ControllerOptimizationProblem(OptimizationProblem):
            def __init__(self, obj_func, batch_func):
                self.obj_func = obj_func
                self.batch_func = batch_func
                self.constraints = []

            def evaluate_objective(self, x: np.ndarray) -> float:
                return self.obj_func(x)

            def evaluate_objective_batch(self, population: np.ndarray) -> np.ndarray:
                return self.batch_func(population)

            def check_constraints(self, x: np.ndarray) -> Tuple[bool, list]:
                return True, []

        problem = ControllerOptimizationProblem(objective, batch_objective)

        # Run optimization
        logger.info("Starting DE optimization: %d generations, pop_size=%d, strategy=%s",
                   max_generations, population_size, strategy)

        result = de.optimize(problem, rng=self.rng, verbose=self.de_config.verbose)

        logger.info("DE optimization complete: best_cost=%.6f, iterations=%d",
                   result.fun, result.nit)

        return result.x, result.fun


def main():
    """Example usage of DETuner."""
    import sys
    sys.path.insert(0, str(__file__).replace('src/optimizer/de_optimizer.py', ''))

    from src.controllers.factory import create_controller
    from src.config import load_config

    # Load config
    config = load_config("config.yaml")

    # Create controller factory
    controller_factory = lambda gains: create_controller(
        'classical_smc', config=config, gains=gains
    )

    # Create tuner
    tuner = DETuner(controller_factory, config=config, seed=42)

    # Optimize
    best_gains, best_cost = tuner.optimize(
        population_size=30,
        max_generations=50,
        dimension=6,
        lower_bounds=np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1]),
        upper_bounds=np.array([50, 50, 50, 50, 50, 50]),
        strategy='best/1/bin',
        adaptive_parameters=True
    )

    print("\n[DE] Optimization Results:")
    print(f"  Best Cost: {best_cost:.6f}")
    print(f"  Best Gains: {best_gains}")


if __name__ == "__main__":
    main()
