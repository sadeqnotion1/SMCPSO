#======================================================================================\
#========================== src/optimizer/cmaes_optimizer.py ==========================\
#======================================================================================\
"""
CMA-ES (Covariance Matrix Adaptation Evolution Strategy) tuner for controllers.

This module provides a high-level CMAESTuner class that wraps the CMA-ES algorithm
for controller parameter optimization. CMA-ES is state-of-the-art for continuous
optimization and often outperforms PSO/GA/DE on complex landscapes.

Key features:
- Self-adapting covariance matrix (learns problem structure)
- Invariance properties (rotation, scaling, translation)
- Derandomized step-size adaptation (CSA)
- Excellent convergence on multimodal/ill-conditioned problems
- Follows same interface as PSO/GA/DE tuners

Usage:
    from src.optimizer.cmaes_optimizer import CMAESTuner
    from src.controllers.factory import create_controller
    from src.config import load_config

    config = load_config("config.yaml")
    controller_factory = lambda gains: create_controller('classical_smc', config=config, gains=gains)

    tuner = CMAESTuner(controller_factory, config=config, seed=42)
    best_gains, best_cost = tuner.optimize(
        population_size=50,
        max_generations=100,
        dimension=6,
        lower_bounds=np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1]),
        upper_bounds=np.array([100, 100, 100, 100, 100, 100])
    )

References:
    Hansen, N., & Ostermeier, A. (2001). Completely Derandomized Self-Adaptation
    in Evolution Strategies. Evolutionary Computation, 9(2), 159-195.

    Hansen, N. (2016). The CMA Evolution Strategy: A Tutorial.
    arXiv:1604.00772

Author: Claude Code + AI-assisted development
Date: November 2025
"""

import numpy as np
import logging
from typing import Callable, Optional, Tuple, Any
from dataclasses import dataclass

try:
    import cma
    CMAES_AVAILABLE = True
except ImportError:
    CMAES_AVAILABLE = False
    cma = None

from src.optimization.core.cost_evaluator import ControllerCostEvaluator


logger = logging.getLogger(__name__)


@dataclass
class CMAESConfig:
    """Configuration for CMA-ES optimizer."""
    population_size: Optional[int] = None  # None = auto (4 + 3*log(N))
    sigma0: float = 0.3  # Initial step size (fraction of search space)
    max_iterations: int = 100
    tolerance: float = 1e-9  # Function value tolerance
    tolfunhist: float = 1e-12  # Function history tolerance
    verbose: int = 0  # -1=quiet, 0=warnings, 1=info, 2=debug


class CMAESTuner:
    """High-level wrapper for CMA-ES optimization of controller gains.

    CMA-ES (Covariance Matrix Adaptation Evolution Strategy) is a state-of-the-art
    derivative-free optimizer particularly effective for:
    - Multimodal objective landscapes
    - Ill-conditioned problems
    - Noisy fitness evaluations
    - Problems with unknown/changing curvature

    This class provides a simplified interface for optimizing controller parameters
    using CMA-ES, with the same API as PSOTuner/GATuner/DETuner.

    Attributes:
        controller_factory: Callable that creates a controller given gains
        config: System configuration object
        seed: Random seed for reproducibility
        cmaes_config: CMA-ES-specific configuration
    """

    def __init__(self,
                 controller_factory: Callable,
                 config: Any,
                 seed: Optional[int] = None,
                 cmaes_config: Optional[CMAESConfig] = None):
        """Initialize CMA-ES tuner.

        Parameters
        ----------
        controller_factory : Callable[[np.ndarray], Controller]
            Factory function that creates a controller given gain parameters
        config : Config
            System configuration (dynamics, simulation settings)
        seed : int, optional
            Random seed for reproducibility
        cmaes_config : CMAESConfig, optional
            CMA-ES configuration (defaults to CMAESConfig())
        """
        if not CMAES_AVAILABLE:
            raise ImportError(
                "CMA-ES requires the 'cma' package. Install with: pip install cma"
            )

        self.controller_factory = controller_factory
        self.config = config
        self.seed = seed
        self.cmaes_config = cmaes_config or CMAESConfig()

        # Setup random number generator
        self.rng = np.random.default_rng(seed)

        # Create shared cost evaluator (handles all simulation and cost computation)
        self.cost_evaluator = ControllerCostEvaluator(
            controller_factory=controller_factory,
            config=config,
            seed=seed
        )

        logger.info("CMAESTuner initialized: sigma0=%.2f, max_iter=%d",
                   self.cmaes_config.sigma0, self.cmaes_config.max_iterations)

    def optimize(self,
                 population_size: Optional[int] = None,
                 max_generations: int = 100,
                 dimension: int = 6,
                 lower_bounds: Optional[np.ndarray] = None,
                 upper_bounds: Optional[np.ndarray] = None,
                 sigma0: Optional[float] = None) -> Tuple[np.ndarray, float]:
        """Run CMA-ES to optimize controller gains.

        Parameters
        ----------
        population_size : int, optional
            Population size (lambda). If None, uses default: 4 + floor(3*log(N))
        max_generations : int
            Maximum number of generations
        dimension : int
            Number of gain parameters to optimize
        lower_bounds : np.ndarray, optional
            Lower bounds for each parameter (default: all 0.1)
        upper_bounds : np.ndarray, optional
            Upper bounds for each parameter (default: all 100.0)
        sigma0 : float, optional
            Initial step size (fraction of search range, default: 0.3)

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

        lower_bounds = np.asarray(lower_bounds)
        upper_bounds = np.asarray(upper_bounds)

        # Initial guess (center of search space)
        x0 = (lower_bounds + upper_bounds) / 2.0

        # Initial step size (fraction of search range)
        if sigma0 is None:
            sigma0 = self.cmaes_config.sigma0

        search_range = upper_bounds - lower_bounds
        sigma = sigma0 * np.mean(search_range)

        # CMA-ES options
        opts = {
            'bounds': [lower_bounds.tolist(), upper_bounds.tolist()],
            'seed': self.seed if self.seed is not None else np.random.randint(0, 2**31),
            'maxiter': max_generations,
            'tolfun': self.cmaes_config.tolerance,
            'tolfunhist': self.cmaes_config.tolfunhist,
            'verbose': self.cmaes_config.verbose,
        }

        # Set population size if provided
        if population_size is not None:
            opts['popsize'] = population_size
        elif self.cmaes_config.population_size is not None:
            opts['popsize'] = self.cmaes_config.population_size

        logger.info("Starting CMA-ES optimization: dim=%d, sigma0=%.3f, max_gen=%d",
                   dimension, sigma, max_generations)

        # Define objective function (minimization)
        def objective(gains: np.ndarray) -> float:
            """Cost function: simulates controller and computes performance metric.

            Uses shared ControllerCostEvaluator for real simulation-based
            cost computation (same as PSO, GA, DE).
            """
            return self.cost_evaluator.evaluate_single(gains)

        # Run CMA-ES
        es = cma.CMAEvolutionStrategy(x0, sigma, opts)

        generation = 0
        while not es.stop() and generation < max_generations:
            # Generate new population
            solutions = es.ask()

            # Evaluate fitness (batch evaluation for efficiency)
            population = np.array(solutions)
            fitness_values = self.cost_evaluator.evaluate_batch(population)

            # Update CMA-ES state
            es.tell(solutions, fitness_values.tolist())

            # Log progress
            if generation % 10 == 0 and logger.isEnabledFor(logging.INFO):
                best_cost = es.result.fbest
                logger.info("Generation %d: Best cost = %.6f", generation, best_cost)

            generation += 1

        # Extract results
        result = es.result
        best_gains = result.xbest
        best_cost = result.fbest

        logger.info("CMA-ES optimization complete: best_cost=%.6f, generations=%d",
                   best_cost, generation)

        # Log stop condition
        if es.stop():
            stop_dict = es.stop()
            logger.info("CMA-ES stop condition: %s", list(stop_dict.keys()))

        return best_gains, best_cost


def main():
    """Example usage of CMAESTuner."""
    import sys
    sys.path.insert(0, str(__file__).replace('src/optimizer/cmaes_optimizer.py', ''))

    from src.controllers.factory import create_controller
    from src.config import load_config

    # Load config
    config = load_config("config.yaml")

    # Create controller factory
    controller_factory = lambda gains: create_controller(
        'classical_smc', config=config, gains=gains
    )

    # Create tuner
    tuner = CMAESTuner(controller_factory, config=config, seed=42)

    # Optimize
    best_gains, best_cost = tuner.optimize(
        population_size=30,
        max_generations=50,
        dimension=6,
        lower_bounds=np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1]),
        upper_bounds=np.array([50, 50, 50, 50, 50, 50]),
        sigma0=0.3
    )

    print("\n[CMA-ES] Optimization Results:")
    print(f"  Best Cost: {best_cost:.6f}")
    print(f"  Best Gains: {best_gains}")


if __name__ == "__main__":
    main()
