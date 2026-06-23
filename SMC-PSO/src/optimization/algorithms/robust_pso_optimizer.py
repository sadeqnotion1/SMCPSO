#======================================================================================\
#=============== src/optimization/algorithms/robust_pso_optimizer.py ================\
#======================================================================================\
"""
Robust PSO Optimizer - Multi-Scenario Extension of PSOTuner

This module extends PSOTuner with multi-scenario robust optimization to prevent
overfitting to narrow initial condition ranges (MT-7 issue).

Problem Addressed:
- MT-7: PSO gains optimized on ±0.05 rad show 50.4x chattering degradation
  and 90.2% failure rate on ±0.3 rad perturbations
- Root cause: Single-scenario optimization never encounters challenging conditions

Solution:
- Replace single-scenario fitness with RobustCostEvaluator
- Evaluate each particle across 15 diverse initial conditions
- Aggregate: J = mean + 0.3 × worst_case

Expected Results:
- Chattering degradation: 50.4x → <5x
- Success rate: 9.8% → >85%
- Runtime: ~10-15x longer (parallelizable)

Usage:
    from src.optimization.algorithms.robust_pso_optimizer import RobustPSOTuner
    from src.controllers.factory import create_controller
    from src.config import load_config

    config = load_config("config.yaml")
    config.pso.robustness.enabled = True  # Enable robust PSO

    controller_factory = lambda gains: create_controller(
        'classical_smc', config=config, gains=gains
    )

    tuner = RobustPSOTuner(controller_factory, config=config, seed=42)
    result = tuner.optimise()

    print(f"Best gains: {result['best_pos']}")
    print(f"Best cost: {result['best_cost']}")

Author: Claude Code + AI-assisted development
Date: November 2025
"""

from __future__ import annotations

import logging
from typing import Any, Union, Optional
from pathlib import Path
import numpy as np

from src.config import ConfigSchema, load_config
from src.optimization.algorithms.pso_optimizer import PSOTuner
from src.optimization.core.robust_cost_evaluator import RobustCostEvaluator


logger = logging.getLogger(__name__)


class RobustPSOTuner(PSOTuner):
    """PSO tuner with multi-scenario robust optimization.

    Extends PSOTuner by replacing the single-scenario fitness function with
    multi-scenario robust evaluation. Maintains backward compatibility - can
    fall back to single-scenario PSO if robustness is disabled.

    Attributes:
        robust_enabled: Whether robust optimization is active
        robust_evaluator: RobustCostEvaluator instance (if enabled)
        n_scenarios: Number of scenarios for robust evaluation
        worst_case_weight: Weight for worst-case penalty (α)
    """

    def __init__(
        self,
        controller_factory,
        config: Union[ConfigSchema, str, Path],
        seed: Optional[int] = None,
        rng: Optional[np.random.Generator] = None,
        instability_penalty_factor: float = 100.0,
        robust_enabled: Optional[bool] = None,
    ) -> None:
        """Initialize Robust PSO Tuner.

        Parameters
        ----------
        controller_factory : Callable[[np.ndarray], Controller]
            Factory function for creating controllers
        config : ConfigSchema or path-like
            System configuration
        seed : int, optional
            Random seed for reproducibility
        rng : numpy.random.Generator, optional
            External random number generator
        instability_penalty_factor : float, default=100.0
            Scale factor for instability penalties
        robust_enabled : bool, optional
            Override for robustness setting. If None, uses config.pso.robustness.enabled
        """
        # Initialize base PSOTuner
        super().__init__(
            controller_factory=controller_factory,
            config=config,
            seed=seed,
            rng=rng,
            instability_penalty_factor=instability_penalty_factor
        )

        # Check if robust optimization is enabled
        robustness_config = getattr(self.cfg.pso, 'robustness', None)

        if robust_enabled is not None:
            # Explicit override
            self.robust_enabled = robust_enabled
        elif robustness_config and getattr(robustness_config, 'enabled', False):
            # Enabled in config
            self.robust_enabled = True
        else:
            # Default: disabled (backward compatible)
            self.robust_enabled = False

        # Initialize robust evaluator if enabled
        if self.robust_enabled:
            if robustness_config is None:
                raise ValueError(
                    "Robust PSO enabled but pso.robustness config section missing. "
                    "Add robustness configuration to config.yaml"
                )

            # Extract robustness parameters from config
            n_scenarios = getattr(robustness_config, 'n_scenarios', 15)
            worst_case_weight = getattr(robustness_config, 'worst_case_weight', 0.3)

            scenario_distribution = None
            if hasattr(robustness_config, 'scenario_distribution'):
                dist_cfg = robustness_config.scenario_distribution
                scenario_distribution = {
                    'nominal': getattr(dist_cfg, 'nominal_fraction', 0.2),
                    'moderate': getattr(dist_cfg, 'moderate_fraction', 0.3),
                    'large': getattr(dist_cfg, 'large_fraction', 0.5)
                }

            nominal_range = getattr(robustness_config, 'nominal_range', 0.05)
            moderate_range = getattr(robustness_config, 'moderate_range', 0.15)
            large_range = getattr(robustness_config, 'large_range', 0.3)

            robust_seed = getattr(robustness_config, 'seed', None) or seed

            # Create robust cost evaluator
            self.robust_evaluator = RobustCostEvaluator(
                controller_factory=controller_factory,
                config=self.cfg,
                seed=robust_seed,
                n_scenarios=n_scenarios,
                worst_case_weight=worst_case_weight,
                scenario_distribution=scenario_distribution,
                nominal_range=nominal_range,
                moderate_range=moderate_range,
                large_range=large_range
            )

            self.n_scenarios = n_scenarios
            self.worst_case_weight = worst_case_weight

            logger.info(
                "RobustPSOTuner initialized: robust_enabled=True, "
                "n_scenarios=%d, α=%.2f",
                n_scenarios, worst_case_weight
            )
        else:
            self.robust_evaluator = None
            logger.info("RobustPSOTuner initialized: robust_enabled=False (standard PSO)")

    def _fitness(self, particles: np.ndarray) -> np.ndarray:
        """Override fitness function to use robust evaluator.

        Parameters
        ----------
        particles : np.ndarray, shape (B, n_params)
            Population of gain vectors

        Returns
        -------
        costs : np.ndarray, shape (B,)
            Fitness values (lower is better)
        """
        if self.robust_enabled:
            # Multi-scenario robust evaluation
            return self.robust_evaluator.evaluate_batch_robust(particles)
        else:
            # Fall back to original single-scenario PSO
            return super()._fitness(particles)


def create_robust_pso_tuner(
    controller_factory,
    config: Union[ConfigSchema, str, Path],
    seed: Optional[int] = None,
    robust_enabled: bool = True
) -> RobustPSOTuner:
    """Factory function for creating RobustPSOTuner with defaults.

    Convenience function for quick setup.

    Parameters
    ----------
    controller_factory : Callable
        Factory for creating controllers
    config : ConfigSchema or path-like
        System configuration
    seed : int, optional
        Random seed
    robust_enabled : bool, default=True
        Whether to enable robust optimization

    Returns
    -------
    tuner : RobustPSOTuner
        Configured tuner instance
    """
    return RobustPSOTuner(
        controller_factory=controller_factory,
        config=config,
        seed=seed,
        robust_enabled=robust_enabled
    )
