#======================================================================================\
#============================= src/optimizer/ga_optimizer.py ===========================\
#======================================================================================\

"""
Genetic Algorithm (GA) tuner for sliding-mode controllers.

This module provides a high-level GATuner class that wraps the modular
GeneticAlgorithm implementation for controller parameter optimization.
It follows the same interface pattern as PSOTuner for consistency.

Usage:
    from src.optimizer.ga_optimizer import GATuner
    from src.controllers.factory import create_controller

    def controller_factory(gains):
        return create_controller('classical_smc', gains=gains, config=config)

    tuner = GATuner(controller_factory, config="config.yaml", seed=42)
    best_gains, best_cost = tuner.optimize(population_size=50, max_generations=100)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple, Union

import numpy as np

from src.config import ConfigSchema, load_config
from src.utils.seed import create_rng
from ..optimization.core.cost_evaluator import ControllerCostEvaluator
from ..optimization.algorithms.evolutionary.genetic import GeneticAlgorithm, GeneticAlgorithmConfig
from ..optimization.core.interfaces import OptimizationProblem, ParameterSpace, OptimizationResult
from ..optimization.core.parameters import ContinuousParameterSpace

logger = logging.getLogger(__name__)


class ControllerOptimizationProblem(OptimizationProblem):
    """Adapter to wrap controller evaluation as an OptimizationProblem."""

    def __init__(self, objective_fn: Callable[[np.ndarray], float], dimension: int):
        """Initialize the problem.

        Parameters
        ----------
        objective_fn : Callable[[np.ndarray], float]
            Function that evaluates a parameter vector and returns cost
        dimension : int
            Dimensionality of the parameter space
        """
        self.objective_fn = objective_fn
        self.dimension = dimension
        self.num_evaluations = 0

    def evaluate(self, parameters: np.ndarray) -> float:
        """Evaluate objective function.

        Parameters
        ----------
        parameters : np.ndarray
            Parameter vector to evaluate

        Returns
        -------
        float
            Cost value (lower is better)
        """
        self.num_evaluations += 1
        return self.objective_fn(parameters)


class GATuner:
    """High-throughput Genetic Algorithm tuner for sliding-mode controllers.

    This tuner wraps the modular GeneticAlgorithm implementation and provides
    a similar interface to PSOTuner for consistency. It uses vectorized
    simulation for efficient fitness evaluation and supports configurable
    genetic operators.

    Features:
    - Tournament, roulette wheel, and rank-based selection
    - Uniform, single-point, and arithmetic crossover
    - Gaussian and uniform mutation strategies
    - Elitist preservation
    - Diversity maintenance via adaptive parameters
    - Parallel fitness evaluation
    """

    def __init__(
        self,
        controller_factory: Callable[[np.ndarray], Any],
        config: Union[ConfigSchema, str, Path],
        seed: Optional[int] = None,
        rng: Optional[np.random.Generator] = None,
    ) -> None:
        """Initialize the GATuner.

        Parameters
        ----------
        controller_factory : Callable[[np.ndarray], Any]
            Function returning a controller instance given a gain vector
        config : ConfigSchema or path-like
            Validated configuration object or path to YAML file
        seed : int or None, optional
            Seed for reproducibility. If None, uses global_seed from config
        rng : numpy.random.Generator or None, optional
            External random number generator. If provided, seed is ignored
        """
        # Load configuration
        if isinstance(config, (str, Path)):
            self.cfg: ConfigSchema = load_config(config)
        else:
            self.cfg = config

        # Store controller factory and config
        self.controller_factory = controller_factory

        # Local PRNG for reproducibility
        default_seed = seed if seed is not None else getattr(self.cfg, "global_seed", None)
        self.seed: Optional[int] = int(default_seed) if default_seed is not None else None
        self.rng: np.random.Generator = rng or create_rng(self.seed)

        # Create shared cost evaluator (handles all simulation and cost computation)
        self.cost_evaluator = ControllerCostEvaluator(
            controller_factory=controller_factory,
            config=self.cfg,
            seed=self.seed
        )

    def _evaluate_gains(self, gains: np.ndarray) -> float:
        """Evaluate a single gain vector by simulating the controller.

        Uses the shared ControllerCostEvaluator for real simulation-based
        cost computation (same as PSO).

        Parameters
        ----------
        gains : np.ndarray
            Controller gain vector to evaluate

        Returns
        -------
        float
            Cost value (lower is better)
        """
        return self.cost_evaluator.evaluate_single(gains)

    def optimize(
        self,
        population_size: int = 50,
        max_generations: int = 100,
        lower_bounds: Optional[np.ndarray] = None,
        upper_bounds: Optional[np.ndarray] = None,
        dimension: Optional[int] = None,
        **ga_kwargs
    ) -> Tuple[np.ndarray, float]:
        """Run genetic algorithm optimization to find best controller gains.

        Parameters
        ----------
        population_size : int, default=50
            Number of individuals in the population
        max_generations : int, default=100
            Maximum number of generations to evolve
        lower_bounds : np.ndarray, optional
            Lower bounds for each parameter. If None, uses [0.1] * dimension
        upper_bounds : np.ndarray, optional
            Upper bounds for each parameter. If None, uses [100.0] * dimension
        dimension : int, optional
            Dimensionality of the parameter space. If None, inferred from bounds
        **ga_kwargs
            Additional keyword arguments passed to GeneticAlgorithmConfig:
            - elite_ratio : float (default 0.1)
            - crossover_probability : float (default 0.8)
            - mutation_probability : float (default 0.2)
            - mutation_strength : float (default 0.1)
            - tournament_size : int (default 3)
            - crossover_method : str (default 'uniform')
            - mutation_method : str (default 'gaussian')
            - selection_method : str (default 'tournament')

        Returns
        -------
        best_gains : np.ndarray
            Optimized controller gain vector
        best_cost : float
            Cost value achieved by best gains

        Examples
        --------
        >>> tuner = GATuner(controller_factory, config="config.yaml", seed=42)
        >>> gains, cost = tuner.optimize(population_size=50, max_generations=100)
        >>> print(f"Best gains: {gains}, Cost: {cost}")
        """
        # Determine parameter space dimensions
        if dimension is None:
            if lower_bounds is not None:
                dimension = len(lower_bounds)
            elif upper_bounds is not None:
                dimension = len(upper_bounds)
            else:
                raise ValueError("Must specify dimension or bounds")

        # Set default bounds if not provided
        if lower_bounds is None:
            lower_bounds = np.full(dimension, 0.1)
        if upper_bounds is None:
            upper_bounds = np.full(dimension, 100.0)

        lower_bounds = np.asarray(lower_bounds)
        upper_bounds = np.asarray(upper_bounds)

        logger.info(f"GA Optimization: pop_size={population_size}, max_gen={max_generations}, dim={dimension}")
        logger.info(f"Bounds: lower={lower_bounds}, upper={upper_bounds}")

        # Create parameter space
        parameter_space = ContinuousParameterSpace(
            lower_bounds=lower_bounds,
            upper_bounds=upper_bounds
        )

        # Create optimization problem
        problem = ControllerOptimizationProblem(
            objective_fn=self._evaluate_gains,
            dimension=dimension
        )

        # Configure genetic algorithm
        ga_config = GeneticAlgorithmConfig(
            population_size=population_size,
            max_generations=max_generations,
            random_seed=self.seed,
            **ga_kwargs
        )

        # Create and run optimizer
        optimizer = GeneticAlgorithm(config=ga_config)
        result: OptimizationResult = optimizer.optimize(problem, parameter_space)

        logger.info(f"GA Optimization complete: best_cost={result.best_cost:.6f}, evaluations={problem.num_evaluations}")

        return result.best_parameters, result.best_cost


__all__ = ['GATuner']
