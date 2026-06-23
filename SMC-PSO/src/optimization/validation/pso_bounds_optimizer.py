#======================================================================================\\\
#================ src/optimization/validation/pso_bounds_optimizer.py =================\\\
#======================================================================================\\\

"""
Advanced PSO Parameter Bounds Optimization for Controller Factory Integration.

This module provides optimized parameter bounds validation and dynamic adjustment
for PSO optimization across all SMC controller types, addressing GitHub Issue #6
factory integration requirements.

Features:
- Dynamic bounds optimization based on controller physics
- Multi-objective parameter space analysis
- Convergence-aware bounds adjustment
- Statistical validation of parameter effectiveness
- Performance-driven bounds refinement
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from src.controllers.factory import SMCType, create_smc_for_pso, get_gain_bounds_for_pso
from src.optimization.algorithms.pso_optimizer import PSOTuner
from src.config import load_config
from src.utils.seed import set_global_seed
from src.utils.numerical_stability import EPSILON_DIV


class BoundsOptimizationStrategy(Enum):
    """Strategy for optimizing parameter bounds."""
    PHYSICS_BASED = "physics_based"      # Based on controller physics constraints
    PERFORMANCE_DRIVEN = "performance"    # Based on empirical performance data
    CONVERGENCE_FOCUSED = "convergence"   # Optimized for PSO convergence properties
    HYBRID = "hybrid"                     # Combination of all strategies


@dataclass
class ControllerBoundsSpec:
    """Specification for controller parameter bounds."""
    controller_type: SMCType
    parameter_names: List[str]
    physics_bounds: Tuple[List[float], List[float]]
    performance_bounds: Tuple[List[float], List[float]]
    convergence_bounds: Tuple[List[float], List[float]]
    recommended_bounds: Tuple[List[float], List[float]]
    bounds_confidence: float
    validation_metrics: Dict[str, float]


@dataclass
class BoundsValidationResult:
    """Result of bounds validation analysis."""
    controller_type: SMCType
    original_bounds: Tuple[List[float], List[float]]
    optimized_bounds: Tuple[List[float], List[float]]
    improvement_ratio: float
    convergence_improvement: float
    performance_improvement: float
    validation_successful: bool
    optimization_time: float
    detailed_metrics: Dict[str, Any]


class PSOBoundsOptimizer:
    """
    Advanced PSO parameter bounds optimizer for controller factory integration.

    Optimizes PSO parameter bounds for maximum convergence efficiency and
    control performance across all SMC controller types.
    """

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize PSO bounds optimizer."""
        self.config = load_config(config_path)
        self.logger = logging.getLogger(__name__)

        # Set deterministic seed for reproducible optimization
        set_global_seed(42)

        # Controller specifications
        self.controller_specs = self._initialize_controller_specifications()

        # Optimization parameters
        self.bounds_search_resolution = 20  # Points per dimension for bounds search
        self.validation_trials = 5  # Number of PSO trials per bounds configuration
        self.max_bounds_expansion = 3.0  # Maximum factor for bounds expansion
        self.min_bounds_contraction = 0.3  # Minimum factor for bounds contraction

        # Performance tracking
        self.optimization_history = []
        self.validation_results = {}

    def _initialize_controller_specifications(self) -> Dict[SMCType, Dict[str, Any]]:
        """Initialize controller-specific parameter specifications."""
        specs = {}

        # Classical SMC: [k1, k2, λ1, λ2, K, kd]
        specs[SMCType.CLASSICAL] = {
            'parameter_names': ['k1', 'k2', 'lambda1', 'lambda2', 'K', 'kd'],
            'physics_constraints': {
                'k1': (0.1, 100.0),      # Position gain: stability requirement
                'k2': (0.1, 100.0),      # Velocity gain: stability requirement
                'lambda1': (0.1, 50.0),  # Surface gain 1: convergence requirement
                'lambda2': (0.1, 50.0),  # Surface gain 2: convergence requirement
                'K': (1.0, 200.0),       # Switching gain: robustness requirement
                'kd': (0.01, 20.0)       # Boundary layer: chattering reduction
            },
            'performance_priorities': ['stability', 'tracking', 'chattering_reduction'],
            'convergence_sensitivity': [0.8, 0.8, 0.9, 0.9, 0.6, 0.3]  # PSO sensitivity
        }

        # Adaptive SMC: [k1, k2, λ1, λ2, γ]
        specs[SMCType.ADAPTIVE] = {
            'parameter_names': ['k1', 'k2', 'lambda1', 'lambda2', 'gamma'],
            'physics_constraints': {
                'k1': (0.5, 80.0),       # Position gain
                'k2': (0.5, 80.0),       # Velocity gain
                'lambda1': (0.2, 40.0),  # Surface gain 1
                'lambda2': (0.2, 40.0),  # Surface gain 2
                'gamma': (0.1, 15.0)     # Adaptation rate: balance speed vs stability
            },
            'performance_priorities': ['adaptation_speed', 'stability', 'robustness'],
            'convergence_sensitivity': [0.7, 0.7, 0.8, 0.8, 0.9]
        }

        # Super-Twisting SMC: [K1, K2, λ1, λ2, c1, c2]
        specs[SMCType.SUPER_TWISTING] = {
            'parameter_names': ['K1', 'K2', 'lambda1', 'lambda2', 'c1', 'c2'],
            'physics_constraints': {
                'K1': (2.0, 120.0),      # Primary twisting gain: K1 > K2 required
                'K2': (1.0, 80.0),       # Secondary twisting gain
                'lambda1': (0.5, 35.0),  # Surface gain 1
                'lambda2': (0.5, 35.0),  # Surface gain 2
                'c1': (0.1, 30.0),       # Twisting parameter 1
                'c2': (0.1, 30.0)        # Twisting parameter 2
            },
            'performance_priorities': ['finite_time_convergence', 'chattering_elimination', 'robustness'],
            'convergence_sensitivity': [0.9, 0.8, 0.7, 0.7, 0.6, 0.6],
            'coupling_constraints': [('K1', 'K2', 'K1 > K2')]  # K1 must be greater than K2
        }

        # Hybrid Adaptive STA-SMC: [c1, λ1, c2, λ2]
        specs[SMCType.HYBRID] = {
            'parameter_names': ['c1', 'lambda1', 'c2', 'lambda2'],
            'physics_constraints': {
                'c1': (1.0, 60.0),       # First surface coefficient
                'lambda1': (0.3, 30.0),  # First surface damping
                'c2': (1.0, 60.0),       # Second surface coefficient
                'lambda2': (0.3, 30.0)   # Second surface damping
            },
            'performance_priorities': ['mode_switching_efficiency', 'stability', 'tracking'],
            'convergence_sensitivity': [0.8, 0.9, 0.8, 0.9]
        }

        return specs

    def optimize_bounds_for_controller(
        self,
        controller_type: SMCType,
        strategy: BoundsOptimizationStrategy = BoundsOptimizationStrategy.HYBRID,
        max_optimization_time: float = 300.0
    ) -> BoundsValidationResult:
        """
        Optimize PSO parameter bounds for specific controller type.

        Args:
            controller_type: Controller type to optimize
            strategy: Optimization strategy to use
            max_optimization_time: Maximum time for optimization (seconds)

        Returns:
            BoundsValidationResult with optimization results
        """
        self.logger.info(f"Optimizing PSO bounds for {controller_type.value} using {strategy.value} strategy")

        start_time = time.time()

        # Get current bounds
        original_lower, original_upper = get_gain_bounds_for_pso(controller_type)
        original_bounds = (original_lower, original_upper)

        # Get controller specifications
        self.controller_specs[controller_type]

        # Generate bounds candidates based on strategy
        bounds_candidates = self._generate_bounds_candidates(
            controller_type, strategy, max_optimization_time * 0.8
        )

        # Evaluate bounds candidates
        bounds_performance = self._evaluate_bounds_candidates(
            controller_type, bounds_candidates, max_optimization_time * 0.2
        )

        # Select optimal bounds
        optimal_bounds = self._select_optimal_bounds(bounds_performance, strategy)

        # Validate optimized bounds
        validation_metrics = self._validate_optimized_bounds(
            controller_type, original_bounds, optimal_bounds
        )

        optimization_time = time.time() - start_time

        # Calculate improvement metrics
        improvement_ratio = self._calculate_improvement_ratio(
            bounds_performance, original_bounds, optimal_bounds
        )

        # Create validation result
        result = BoundsValidationResult(
            controller_type=controller_type,
            original_bounds=original_bounds,
            optimized_bounds=optimal_bounds,
            improvement_ratio=improvement_ratio,
            convergence_improvement=validation_metrics.get('convergence_improvement', 0.0),
            performance_improvement=validation_metrics.get('performance_improvement', 0.0),
            validation_successful=validation_metrics.get('validation_successful', False),
            optimization_time=optimization_time,
            detailed_metrics=validation_metrics
        )

        self.logger.info(
            f"Bounds optimization completed for {controller_type.value}: "
            f"Improvement ratio: {improvement_ratio:.3f}, Time: {optimization_time:.1f}s"
        )

        return result

    def _generate_bounds_candidates(
        self,
        controller_type: SMCType,
        strategy: BoundsOptimizationStrategy,
        max_time: float
    ) -> List[Tuple[List[float], List[float]]]:
        """Generate candidate bounds configurations for evaluation."""
        controller_spec = self.controller_specs[controller_type]
        physics_constraints = controller_spec['physics_constraints']
        param_names = controller_spec['parameter_names']

        candidates = []

        if strategy in [BoundsOptimizationStrategy.PHYSICS_BASED, BoundsOptimizationStrategy.HYBRID]:
            # Physics-based bounds
            physics_lower = [physics_constraints[name][0] for name in param_names]
            physics_upper = [physics_constraints[name][1] for name in param_names]
            candidates.append((physics_lower, physics_upper))

            # Conservative physics bounds (tighter)
            conservative_lower = [lower_val * 1.5 for lower_val in physics_lower]
            conservative_upper = [u * 0.8 for u in physics_upper]
            candidates.append((conservative_lower, conservative_upper))

            # Aggressive physics bounds (wider)
            aggressive_lower = [lower_val * 0.7 for lower_val in physics_lower]
            aggressive_upper = [u * 1.3 for u in physics_upper]
            candidates.append((aggressive_lower, aggressive_upper))

        if strategy in [BoundsOptimizationStrategy.PERFORMANCE_DRIVEN, BoundsOptimizationStrategy.HYBRID]:
            # Performance-driven bounds based on empirical data
            performance_bounds = self._generate_performance_driven_bounds(controller_type)
            candidates.extend(performance_bounds)

        if strategy in [BoundsOptimizationStrategy.CONVERGENCE_FOCUSED, BoundsOptimizationStrategy.HYBRID]:
            # Convergence-focused bounds
            convergence_bounds = self._generate_convergence_focused_bounds(controller_type)
            candidates.extend(convergence_bounds)

        # Remove duplicates and invalid bounds
        valid_candidates = []
        for lower, upper in candidates:
            if len(lower) == len(param_names) and len(upper) == len(param_names):
                if all(lower_val < upper_val for lower_val, upper_val in zip(lower, upper)):
                    # Check for duplicates
                    is_duplicate = any(
                        np.allclose(lower, existing[0]) and np.allclose(upper, existing[1])
                        for existing in valid_candidates
                    )
                    if not is_duplicate:
                        valid_candidates.append((lower, upper))

        self.logger.info(f"Generated {len(valid_candidates)} valid bounds candidates for {controller_type.value}")
        return valid_candidates

    def _generate_performance_driven_bounds(self, controller_type: SMCType) -> List[Tuple[List[float], List[float]]]:
        """Generate bounds based on empirical performance data."""
        # These bounds are derived from performance analysis of successful optimizations
        performance_bounds_db = {
            SMCType.CLASSICAL: [
                # High performance configuration
                ([5.0, 3.0, 8.0, 5.0, 15.0, 2.0], [25.0, 20.0, 25.0, 20.0, 80.0, 8.0]),
                # Balanced configuration
                ([2.0, 2.0, 5.0, 3.0, 10.0, 1.0], [40.0, 30.0, 30.0, 25.0, 120.0, 12.0]),
                # Robust configuration
                ([8.0, 5.0, 10.0, 8.0, 20.0, 3.0], [35.0, 25.0, 20.0, 15.0, 100.0, 10.0])
            ],
            SMCType.ADAPTIVE: [
                # Fast adaptation
                ([3.0, 2.0, 5.0, 3.0, 1.0], [30.0, 25.0, 20.0, 18.0, 8.0]),
                # Stable adaptation
                ([5.0, 4.0, 8.0, 6.0, 0.5], [25.0, 20.0, 15.0, 12.0, 5.0])
            ],
            SMCType.SUPER_TWISTING: [
                # Strong twisting
                ([8.0, 4.0, 5.0, 3.0, 2.0, 1.0], [60.0, 30.0, 20.0, 15.0, 15.0, 12.0]),
                # Gentle twisting
                ([4.0, 2.0, 3.0, 2.0, 1.0, 0.5], [40.0, 20.0, 15.0, 12.0, 10.0, 8.0])
            ],
            SMCType.HYBRID: [
                # Balanced hybrid
                ([5.0, 2.0, 5.0, 2.0], [35.0, 15.0, 35.0, 15.0]),
                # Performance hybrid
                ([8.0, 3.0, 8.0, 3.0], [45.0, 20.0, 45.0, 20.0])
            ]
        }

        return performance_bounds_db.get(controller_type, [])

    def _generate_convergence_focused_bounds(self, controller_type: SMCType) -> List[Tuple[List[float], List[float]]]:
        """Generate bounds optimized for PSO convergence properties."""
        controller_spec = self.controller_specs[controller_type]
        sensitivity = controller_spec['convergence_sensitivity']
        param_names = controller_spec['parameter_names']
        physics_constraints = controller_spec['physics_constraints']

        bounds_variants = []

        # Create bounds based on parameter sensitivity to PSO convergence
        for variant_factor in [0.6, 0.8, 1.2, 1.5]:  # Different scaling factors
            lower = []
            upper = []

            for i, param_name in enumerate(param_names):
                phys_lower, phys_upper = physics_constraints[param_name]
                param_sensitivity = sensitivity[i]

                # Scale bounds inversely to sensitivity (more sensitive = tighter bounds)
                sensitivity_scaling = 1.0 / (param_sensitivity + 0.1)
                range_factor = variant_factor * sensitivity_scaling

                center = (phys_lower + phys_upper) / 2
                half_range = (phys_upper - phys_lower) / 2 * range_factor

                param_lower = max(phys_lower, center - half_range)
                param_upper = min(phys_upper, center + half_range)

                lower.append(param_lower)
                upper.append(param_upper)

            bounds_variants.append((lower, upper))

        return bounds_variants

    def _evaluate_bounds_candidates(
        self,
        controller_type: SMCType,
        bounds_candidates: List[Tuple[List[float], List[float]]],
        max_time: float
    ) -> Dict[Tuple[List[float], List[float]], Dict[str, float]]:
        """Evaluate bounds candidates through PSO performance testing."""
        self.logger.info(f"Evaluating {len(bounds_candidates)} bounds candidates for {controller_type.value}")

        bounds_performance = {}
        time_per_candidate = max_time / max(len(bounds_candidates), 1)

        # Use parallel evaluation for efficiency
        with ThreadPoolExecutor(max_workers=min(4, len(bounds_candidates))) as executor:
            future_to_bounds = {
                executor.submit(
                    self._evaluate_single_bounds_candidate,
                    controller_type, bounds, time_per_candidate
                ): bounds
                for bounds in bounds_candidates
            }

            for future in as_completed(future_to_bounds):
                bounds = future_to_bounds[future]
                try:
                    performance = future.result()
                    bounds_performance[bounds] = performance
                except Exception as e:
                    self.logger.warning(f"Bounds evaluation failed for {bounds}: {e}")
                    bounds_performance[bounds] = {
                        'convergence_rate': 0.0,
                        'final_cost': float('inf'),
                        'success_rate': 0.0,
                        'evaluation_error': str(e)
                    }

        return bounds_performance

    def _evaluate_single_bounds_candidate(
        self,
        controller_type: SMCType,
        bounds: Tuple[List[float], List[float]],
        max_time: float
    ) -> Dict[str, float]:
        """Evaluate a single bounds candidate through PSO trials."""
        lower_bounds, upper_bounds = bounds

        # Create temporary PSO configuration with these bounds
        temp_config = self.config.model_copy(deep=True)

        # Update PSO bounds in config
        if hasattr(temp_config, 'pso') and hasattr(temp_config.pso, 'bounds'):
            temp_config.pso.bounds = list(zip(lower_bounds, upper_bounds))

        # Performance metrics
        convergence_rates = []
        final_costs = []
        success_count = 0

        trials_per_bounds = min(self.validation_trials, max(1, int(max_time / 30)))  # At least 30s per trial

        for trial in range(trials_per_bounds):
            try:
                # Create controller factory with bounds
                def bounded_factory(gains):
                    return create_smc_for_pso(
                        smc_type=controller_type,
                        gains=gains,
                        max_force=150.0,
                        dt=0.001
                    )

                # Run PSO optimization
                tuner = PSOTuner(
                    controller_factory=bounded_factory,
                    config=temp_config,
                    seed=42 + trial
                )

                # Quick PSO run for bounds evaluation
                result = tuner.optimise(
                    iters_override=15,  # Short run for evaluation
                    n_particles_override=10
                )

                # Extract performance metrics
                cost_history = result.get('history', {}).get('cost', [])
                if len(cost_history) >= 2:
                    # Issue #13: Standardized division protection
                    convergence_rate = (cost_history[0] - cost_history[-1]) / max(cost_history[0], EPSILON_DIV)
                    convergence_rates.append(max(0.0, convergence_rate))
                    final_costs.append(result['best_cost'])
                    success_count += 1

            except Exception as e:
                self.logger.debug(f"PSO trial {trial} failed for bounds {bounds}: {e}")
                continue

        # Calculate aggregate metrics
        if success_count > 0:
            avg_convergence_rate = np.mean(convergence_rates)
            avg_final_cost = np.mean(final_costs)
            success_rate = success_count / trials_per_bounds
        else:
            avg_convergence_rate = 0.0
            avg_final_cost = float('inf')
            success_rate = 0.0

        return {
            'convergence_rate': avg_convergence_rate,
            'final_cost': avg_final_cost,
            'success_rate': success_rate,
            'trials_completed': success_count
        }

    def _select_optimal_bounds(
        self,
        bounds_performance: Dict[Tuple[List[float], List[float]], Dict[str, float]],
        strategy: BoundsOptimizationStrategy
    ) -> Tuple[List[float], List[float]]:
        """Select optimal bounds based on performance metrics and strategy."""
        if not bounds_performance:
            raise ValueError("No bounds performance data available")

        # Define scoring weights based on strategy
        strategy_weights = {
            BoundsOptimizationStrategy.PHYSICS_BASED: {
                'convergence_rate': 0.3,
                'final_cost': 0.4,
                'success_rate': 0.3
            },
            BoundsOptimizationStrategy.PERFORMANCE_DRIVEN: {
                'convergence_rate': 0.2,
                'final_cost': 0.6,
                'success_rate': 0.2
            },
            BoundsOptimizationStrategy.CONVERGENCE_FOCUSED: {
                'convergence_rate': 0.6,
                'final_cost': 0.2,
                'success_rate': 0.2
            },
            BoundsOptimizationStrategy.HYBRID: {
                'convergence_rate': 0.4,
                'final_cost': 0.4,
                'success_rate': 0.2
            }
        }

        weights = strategy_weights[strategy]

        # Calculate scores for each bounds configuration
        bounds_scores = {}

        for bounds, performance in bounds_performance.items():
            # Normalize metrics (higher is better for all)
            normalized_convergence = min(1.0, performance['convergence_rate'])
            normalized_cost = 1.0 / (1.0 + performance['final_cost'])  # Inverse for cost
            normalized_success = performance['success_rate']

            # Calculate weighted score
            score = (
                weights['convergence_rate'] * normalized_convergence +
                weights['final_cost'] * normalized_cost +
                weights['success_rate'] * normalized_success
            )

            bounds_scores[bounds] = score

        # Select bounds with highest score
        optimal_bounds = max(bounds_scores.keys(), key=lambda b: bounds_scores[b])

        self.logger.info(
            f"Selected optimal bounds with score {bounds_scores[optimal_bounds]:.3f}: "
            f"Lower: {optimal_bounds[0]}, Upper: {optimal_bounds[1]}"
        )

        return optimal_bounds

    def _calculate_improvement_ratio(
        self,
        bounds_performance: Dict[Tuple[List[float], List[float]], Dict[str, float]],
        original_bounds: Tuple[List[float], List[float]],
        optimal_bounds: Tuple[List[float], List[float]]
    ) -> float:
        """Calculate improvement ratio from bounds optimization."""
        # Get performance of original bounds if available
        original_performance = bounds_performance.get(original_bounds)
        optimal_performance = bounds_performance.get(optimal_bounds)

        if original_performance is None or optimal_performance is None:
            return 1.0  # No improvement data available

        # Calculate improvement in key metrics
        # Issue #13: Standardized division protection
        convergence_improvement = (
            optimal_performance['convergence_rate'] / max(original_performance['convergence_rate'], EPSILON_DIV)
        )

        cost_improvement = (
            original_performance['final_cost'] / max(optimal_performance['final_cost'], EPSILON_DIV)
        )

        success_improvement = (
            optimal_performance['success_rate'] / max(original_performance['success_rate'], EPSILON_DIV)
        )

        # Geometric mean of improvements
        improvement_ratio = (convergence_improvement * cost_improvement * success_improvement) ** (1/3)

        return min(10.0, improvement_ratio)  # Cap at 10x improvement

    def _validate_optimized_bounds(
        self,
        controller_type: SMCType,
        original_bounds: Tuple[List[float], List[float]],
        optimized_bounds: Tuple[List[float], List[float]]
    ) -> Dict[str, Any]:
        """Validate optimized bounds through comprehensive testing."""
        self.logger.info(f"Validating optimized bounds for {controller_type.value}")

        validation_metrics = {
            'validation_successful': False,
            'convergence_improvement': 0.0,
            'performance_improvement': 0.0,
            'stability_maintained': False,
            'bounds_reasonable': False
        }

        try:
            # Test 1: Bounds reasonableness check
            lower_opt, upper_opt = optimized_bounds
            lower_orig, upper_orig = original_bounds

            # Check bounds are not too extreme
            bounds_reasonable = True
            for i, (l_opt, u_opt, l_orig, u_orig) in enumerate(zip(lower_opt, upper_opt, lower_orig, upper_orig)):
                # Issue #13: Standardized division protection
                expansion_factor = (u_opt - l_opt) / max(u_orig - l_orig, EPSILON_DIV)
                if expansion_factor > self.max_bounds_expansion or expansion_factor < self.min_bounds_contraction:
                    bounds_reasonable = False
                    break

            validation_metrics['bounds_reasonable'] = bounds_reasonable

            # Test 2: Comparative PSO performance
            if bounds_reasonable:
                original_performance = self._evaluate_single_bounds_candidate(
                    controller_type, original_bounds, 60.0
                )
                optimized_performance = self._evaluate_single_bounds_candidate(
                    controller_type, optimized_bounds, 60.0
                )

                # Calculate improvements
                # Issue #13: Standardized division protection
                convergence_improvement = (
                    optimized_performance['convergence_rate'] - original_performance['convergence_rate']
                ) / max(original_performance['convergence_rate'], EPSILON_DIV)

                performance_improvement = (
                    original_performance['final_cost'] - optimized_performance['final_cost']
                ) / max(original_performance['final_cost'], EPSILON_DIV)

                validation_metrics['convergence_improvement'] = convergence_improvement
                validation_metrics['performance_improvement'] = performance_improvement

                # Test 3: Stability maintained
                stability_maintained = (
                    optimized_performance['success_rate'] >= 0.5 and
                    optimized_performance['final_cost'] < float('inf')
                )
                validation_metrics['stability_maintained'] = stability_maintained

                # Overall validation success
                validation_metrics['validation_successful'] = (
                    bounds_reasonable and
                    stability_maintained and
                    (convergence_improvement > -0.1 or performance_improvement > 0.0)  # Not significantly worse
                )

        except Exception as e:
            self.logger.error(f"Bounds validation failed: {e}")
            validation_metrics['validation_error'] = str(e)

        return validation_metrics

    def optimize_all_controller_bounds(
        self,
        strategy: BoundsOptimizationStrategy = BoundsOptimizationStrategy.HYBRID
    ) -> Dict[SMCType, BoundsValidationResult]:
        """Optimize bounds for all controller types."""
        self.logger.info(f"Optimizing PSO bounds for all controllers using {strategy.value} strategy")

        results = {}

        for controller_type in [SMCType.CLASSICAL, SMCType.ADAPTIVE, SMCType.SUPER_TWISTING, SMCType.HYBRID]:
            try:
                result = self.optimize_bounds_for_controller(controller_type, strategy)
                results[controller_type] = result

                self.logger.info(
                    f"✓ {controller_type.value}: Bounds optimization completed "
                    f"(Improvement: {result.improvement_ratio:.2f}x)"
                )

            except Exception as e:
                self.logger.error(f"✗ {controller_type.value}: Bounds optimization failed - {e}")
                results[controller_type] = BoundsValidationResult(
                    controller_type=controller_type,
                    original_bounds=([], []),
                    optimized_bounds=([], []),
                    improvement_ratio=0.0,
                    convergence_improvement=0.0,
                    performance_improvement=0.0,
                    validation_successful=False,
                    optimization_time=0.0,
                    detailed_metrics={'error': str(e)}
                )

        return results

    def export_optimized_bounds_config(
        self,
        optimization_results: Dict[SMCType, BoundsValidationResult],
        output_path: str = "optimized_pso_bounds.json"
    ) -> Dict[str, Any]:
        """Export optimized bounds as configuration file."""
        export_config = {
            'metadata': {
                'optimization_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'optimization_strategy': 'hybrid',
                'total_optimization_time': sum(r.optimization_time for r in optimization_results.values()),
                'overall_success_rate': sum(1 for r in optimization_results.values() if r.validation_successful) / len(optimization_results)
            },
            'optimized_bounds': {},
            'performance_summary': {}
        }

        for controller_type, result in optimization_results.items():
            controller_key = controller_type.value

            if result.validation_successful:
                lower_bounds, upper_bounds = result.optimized_bounds
                export_config['optimized_bounds'][controller_key] = {
                    'lower_bounds': lower_bounds,
                    'upper_bounds': upper_bounds,
                    'bounds_pairs': list(zip(lower_bounds, upper_bounds))
                }
            else:
                # Fall back to original bounds
                lower_bounds, upper_bounds = result.original_bounds
                export_config['optimized_bounds'][controller_key] = {
                    'lower_bounds': lower_bounds,
                    'upper_bounds': upper_bounds,
                    'bounds_pairs': list(zip(lower_bounds, upper_bounds)),
                    'note': 'Optimization failed, using original bounds'
                }

            export_config['performance_summary'][controller_key] = {
                'improvement_ratio': result.improvement_ratio,
                'convergence_improvement': result.convergence_improvement,
                'performance_improvement': result.performance_improvement,
                'optimization_successful': result.validation_successful,
                'optimization_time_seconds': result.optimization_time
            }

        # Save to file
        output_file = Path(output_path)
        with open(output_file, 'w') as f:
            json.dump(export_config, f, indent=2)

        self.logger.info(f"Optimized bounds configuration exported to {output_file}")
        return export_config


def run_pso_bounds_optimization() -> Dict[str, Any]:
    """Run complete PSO bounds optimization workflow."""
    print("=" * 80)
    print("PSO PARAMETER BOUNDS OPTIMIZATION - GitHub Issue #6")
    print("Advanced Bounds Validation and Factory Integration")
    print("=" * 80)

    # Initialize optimizer
    optimizer = PSOBoundsOptimizer()

    # Run optimization for all controllers
    print("\n🔍 Running bounds optimization for all SMC controller types...")
    optimization_results = optimizer.optimize_all_controller_bounds(
        strategy=BoundsOptimizationStrategy.HYBRID
    )

    # Export optimized configuration
    print("\n📤 Exporting optimized bounds configuration...")
    config_export = optimizer.export_optimized_bounds_config(optimization_results)

    # Print summary
    print("\n" + "=" * 60)
    print("PSO BOUNDS OPTIMIZATION SUMMARY")
    print("=" * 60)

    successful_optimizations = 0
    total_improvement = 0.0

    for controller_type, result in optimization_results.items():
        status = "✅ SUCCESS" if result.validation_successful else "❌ FAILED"
        improvement = result.improvement_ratio

        print(f"{controller_type.value:25} | {status} | Improvement: {improvement:.2f}x")

        if result.validation_successful:
            successful_optimizations += 1
            total_improvement += improvement

    success_rate = (successful_optimizations / len(optimization_results)) * 100
    avg_improvement = total_improvement / max(successful_optimizations, 1)

    print("\n" + "-" * 60)
    print(f"Overall Success Rate: {success_rate:.1f}%")
    print(f"Average Improvement: {avg_improvement:.2f}x")
    print(f"Total Optimization Time: {sum(r.optimization_time for r in optimization_results.values()):.1f}s")

    if success_rate >= 75:
        print("\n🎉 PSO BOUNDS OPTIMIZATION: SUCCESSFUL")
        print("✅ Enhanced parameter bounds for improved PSO convergence")
        print("✅ Factory integration optimization completed")
        print("✅ Configuration exported for production use")
    else:
        print("\n⚠️  PSO BOUNDS OPTIMIZATION: PARTIAL SUCCESS")
        print(f"✅ {successful_optimizations}/{len(optimization_results)} controllers optimized")
        print("⚠️  Some controllers may need manual bounds tuning")

    return {
        'optimization_results': optimization_results,
        'config_export': config_export,
        'summary': {
            'success_rate': success_rate,
            'average_improvement': avg_improvement,
            'successful_optimizations': successful_optimizations,
            'total_controllers': len(optimization_results)
        }
    }


if __name__ == "__main__":
    results = run_pso_bounds_optimization()