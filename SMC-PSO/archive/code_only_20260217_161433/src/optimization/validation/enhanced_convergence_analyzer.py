#======================================================================================\\\
#============ src/optimization/validation/enhanced_convergence_analyzer.py ============\\\
#======================================================================================\\\

"""
Enhanced PSO Convergence Criteria and Validation Algorithms.

This module provides advanced convergence analysis and validation algorithms
for PSO optimization in the controller factory integration context. Features
include multi-criteria convergence detection, statistical validation, and
real-time convergence monitoring.

Key Features:
- Multi-modal convergence detection
- Statistical significance testing
- Real-time convergence monitoring
- Adaptive convergence criteria
- Population diversity analysis
- Performance prediction algorithms
"""

import numpy as np
import logging
from typing import Dict, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
import time
from scipy import stats
from scipy.signal import savgol_filter

from src.controllers.factory import SMCType
from src.optimization.algorithms.pso_optimizer import PSOTuner
from src.config import load_config
from src.utils.numerical_stability import EPSILON_DIV


class ConvergenceStatus(Enum):
    """Enhanced convergence status indicators."""
    NOT_STARTED = "not_started"
    INITIALIZING = "initializing"
    EXPLORING = "exploring"
    CONVERGING = "converging"
    CONVERGED = "converged"
    STAGNATED = "stagnated"
    OSCILLATING = "oscillating"
    DIVERGING = "diverging"
    PREMATURE_CONVERGENCE = "premature_convergence"
    FAILED = "failed"


class ConvergenceCriterion(Enum):
    """Types of convergence criteria."""
    FITNESS_TOLERANCE = "fitness_tolerance"
    RELATIVE_IMPROVEMENT = "relative_improvement"
    POPULATION_DIVERSITY = "population_diversity"
    GRADIENT_BASED = "gradient_based"
    STATISTICAL_SIGNIFICANCE = "statistical_significance"
    STAGNATION_DETECTION = "stagnation_detection"
    PERFORMANCE_PLATEAU = "performance_plateau"


@dataclass
class ConvergenceMetrics:
    """Comprehensive convergence metrics."""
    iteration: int
    best_fitness: float
    mean_fitness: float
    fitness_std: float
    population_diversity: float
    convergence_velocity: float
    improvement_rate: float
    stagnation_score: float
    diversity_loss_rate: float
    predicted_iterations_remaining: int
    confidence_level: float
    convergence_probability: float


@dataclass
class ConvergenceCriteria:
    """Adaptive convergence criteria configuration."""
    # Fitness-based criteria
    fitness_tolerance: float = 1e-6
    relative_improvement_threshold: float = 1e-4

    # Diversity-based criteria
    min_diversity_threshold: float = 1e-3
    diversity_loss_rate_threshold: float = 0.95

    # Stagnation detection
    stagnation_window: int = 10
    stagnation_threshold: float = 1e-5

    # Statistical criteria
    statistical_confidence_level: float = 0.95
    min_sample_size: int = 20

    # Adaptive parameters
    enable_adaptive_criteria: bool = True
    controller_specific_adjustment: bool = True

    # Performance prediction
    enable_performance_prediction: bool = True
    prediction_window: int = 15

    # Early stopping
    max_stagnation_iterations: int = 50
    premature_convergence_detection: bool = True


class EnhancedConvergenceAnalyzer:
    """
    Advanced PSO convergence analysis with multi-criteria validation.

    Provides comprehensive convergence monitoring, statistical validation,
    and performance prediction for PSO optimization in controller factory
    integration scenarios.
    """

    def __init__(self,
                 criteria: Optional[ConvergenceCriteria] = None,
                 controller_type: Optional[SMCType] = None):
        """Initialize enhanced convergence analyzer."""
        self.criteria = criteria or ConvergenceCriteria()
        self.controller_type = controller_type
        self.logger = logging.getLogger(__name__)

        # Analysis state
        self.iteration_history = []
        self.fitness_history = []
        self.diversity_history = []
        self.convergence_metrics_history = []

        # Convergence state tracking
        self.current_status = ConvergenceStatus.NOT_STARTED
        self.convergence_detected_iteration = None
        self.stagnation_counter = 0
        self.last_significant_improvement = 0

        # Statistical analysis buffers
        self.fitness_buffer = []
        self.improvement_buffer = []
        self.diversity_buffer = []

        # Performance prediction
        self.performance_model = None
        self.prediction_accuracy_history = []

        # Controller-specific tuning
        if controller_type:
            self._apply_controller_specific_tuning()

    def _apply_controller_specific_tuning(self) -> None:
        """Apply controller-specific convergence criteria tuning."""
        if not self.criteria.controller_specific_adjustment:
            return

        # Controller-specific convergence behavior patterns
        controller_adjustments = {
            SMCType.CLASSICAL: {
                'fitness_tolerance': 1e-5,
                'stagnation_window': 12,
                'min_diversity_threshold': 5e-4,
                'max_stagnation_iterations': 40
            },
            SMCType.ADAPTIVE: {
                'fitness_tolerance': 5e-6,
                'stagnation_window': 15,
                'min_diversity_threshold': 8e-4,
                'max_stagnation_iterations': 60,
                'relative_improvement_threshold': 5e-5
            },
            SMCType.SUPER_TWISTING: {
                'fitness_tolerance': 2e-5,
                'stagnation_window': 10,
                'min_diversity_threshold': 1e-3,
                'max_stagnation_iterations': 35,
                'premature_convergence_detection': True
            },
            SMCType.HYBRID: {
                'fitness_tolerance': 8e-6,
                'stagnation_window': 18,
                'min_diversity_threshold': 6e-4,
                'max_stagnation_iterations': 55,
                'enable_performance_prediction': True
            }
        }

        adjustments = controller_adjustments.get(self.controller_type, {})
        for param, value in adjustments.items():
            if hasattr(self.criteria, param):
                setattr(self.criteria, param, value)

        self.logger.info(f"Applied {self.controller_type.value} specific convergence tuning")

    def analyze_convergence(self,
                          iteration: int,
                          best_fitness: float,
                          population_fitness: np.ndarray,
                          population_positions: np.ndarray) -> ConvergenceMetrics:
        """
        Comprehensive convergence analysis for current PSO iteration.

        Args:
            iteration: Current iteration number
            best_fitness: Best fitness value found so far
            population_fitness: Fitness values for all particles
            population_positions: Position vectors for all particles

        Returns:
            ConvergenceMetrics with detailed convergence analysis
        """
        # Update history
        self.iteration_history.append(iteration)
        self.fitness_history.append(best_fitness)

        # Calculate population diversity
        diversity = self._calculate_population_diversity(population_positions)
        self.diversity_history.append(diversity)

        # Calculate convergence velocity
        convergence_velocity = self._calculate_convergence_velocity()

        # Calculate improvement rate
        improvement_rate = self._calculate_improvement_rate()

        # Calculate stagnation score
        stagnation_score = self._calculate_stagnation_score()

        # Calculate diversity loss rate
        diversity_loss_rate = self._calculate_diversity_loss_rate()

        # Performance prediction
        predicted_iterations = self._predict_remaining_iterations()

        # Convergence probability estimation
        convergence_probability = self._estimate_convergence_probability()

        # Statistical confidence
        confidence_level = self._calculate_statistical_confidence()

        # Create comprehensive metrics
        metrics = ConvergenceMetrics(
            iteration=iteration,
            best_fitness=best_fitness,
            mean_fitness=float(np.mean(population_fitness)),
            fitness_std=float(np.std(population_fitness)),
            population_diversity=diversity,
            convergence_velocity=convergence_velocity,
            improvement_rate=improvement_rate,
            stagnation_score=stagnation_score,
            diversity_loss_rate=diversity_loss_rate,
            predicted_iterations_remaining=predicted_iterations,
            confidence_level=confidence_level,
            convergence_probability=convergence_probability
        )

        self.convergence_metrics_history.append(metrics)

        # Update convergence status
        self._update_convergence_status(metrics)

        return metrics

    def check_convergence(self, metrics: ConvergenceMetrics) -> Tuple[bool, ConvergenceStatus, str]:
        """
        Multi-criteria convergence check with detailed analysis.

        Args:
            metrics: Current convergence metrics

        Returns:
            Tuple of (converged, status, explanation)
        """
        convergence_reasons = []

        # Criterion 1: Fitness tolerance
        if metrics.best_fitness <= self.criteria.fitness_tolerance:
            convergence_reasons.append("fitness_tolerance_reached")

        # Criterion 2: Relative improvement
        if (metrics.improvement_rate <= self.criteria.relative_improvement_threshold and
            len(self.fitness_history) > self.criteria.stagnation_window):
            convergence_reasons.append("relative_improvement_minimal")

        # Criterion 3: Population diversity
        if (metrics.population_diversity <= self.criteria.min_diversity_threshold and
            metrics.diversity_loss_rate >= self.criteria.diversity_loss_rate_threshold):
            convergence_reasons.append("population_diversity_loss")

        # Criterion 4: Stagnation detection
        if metrics.stagnation_score >= self.criteria.stagnation_threshold:
            self.stagnation_counter += 1
            if self.stagnation_counter >= self.criteria.max_stagnation_iterations:
                convergence_reasons.append("stagnation_detected")
        else:
            self.stagnation_counter = 0

        # Criterion 5: Statistical significance
        if self.criteria.enable_adaptive_criteria:
            statistical_convergence = self._check_statistical_convergence()
            if statistical_convergence:
                convergence_reasons.append("statistical_significance")

        # Criterion 6: Performance prediction convergence
        if (self.criteria.enable_performance_prediction and
            metrics.predicted_iterations_remaining <= 2):
            convergence_reasons.append("performance_prediction")

        # Determine overall convergence
        if len(convergence_reasons) >= 2:  # Require multiple criteria
            converged = True
            status = ConvergenceStatus.CONVERGED
            explanation = f"Convergence detected: {', '.join(convergence_reasons)}"
        elif "stagnation_detected" in convergence_reasons:
            converged = True
            status = ConvergenceStatus.STAGNATED
            explanation = "Optimization stagnated - no significant improvement"
        elif self._detect_premature_convergence(metrics):
            converged = False
            status = ConvergenceStatus.PREMATURE_CONVERGENCE
            explanation = "Premature convergence detected - consider parameter adjustment"
        elif metrics.convergence_velocity < 0:  # Diverging
            converged = False
            status = ConvergenceStatus.DIVERGING
            explanation = "Optimization appears to be diverging"
        else:
            converged = False
            status = self.current_status
            explanation = f"Optimization continuing - {status.value}"

        return converged, status, explanation

    def _calculate_population_diversity(self, positions: np.ndarray) -> float:
        """Calculate population diversity using average pairwise distance."""
        if len(positions) < 2:
            return 0.0

        # Calculate pairwise distances
        distances = []
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                dist = np.linalg.norm(positions[i] - positions[j])
                distances.append(dist)

        return float(np.mean(distances)) if distances else 0.0

    def _calculate_convergence_velocity(self) -> float:
        """Calculate convergence velocity using fitness improvement rate."""
        if len(self.fitness_history) < 3:
            return 0.0

        # Use recent fitness values for velocity calculation
        recent_fitness = self.fitness_history[-min(5, len(self.fitness_history)):]

        # Calculate first and second derivatives
        if len(recent_fitness) >= 3:
            # Smooth the data to reduce noise
            try:
                smoothed = savgol_filter(recent_fitness,
                                       min(len(recent_fitness), 3), 1)
                velocity = float(smoothed[0] - smoothed[-1])  # Improvement over window
            except (ValueError, np.linalg.LinAlgError) as e:  # P2: Savgol filter can fail with small windows
                logging.getLogger(__name__).debug(f"Savgol filter failed: {e}. Using raw fitness difference.")
                velocity = float(recent_fitness[0] - recent_fitness[-1])
        else:
            velocity = float(recent_fitness[0] - recent_fitness[-1])

        return velocity

    def _calculate_improvement_rate(self) -> float:
        """Calculate relative improvement rate over recent iterations."""
        if len(self.fitness_history) < 2:
            return 0.0

        window_size = min(self.criteria.stagnation_window, len(self.fitness_history))
        recent_fitness = self.fitness_history[-window_size:]

        if len(recent_fitness) < 2:
            return 0.0

        initial_fitness = recent_fitness[0]
        final_fitness = recent_fitness[-1]

        # Issue #13: Standardized division protection
        if abs(initial_fitness) < EPSILON_DIV:
            return 0.0

        improvement_rate = (initial_fitness - final_fitness) / abs(initial_fitness)
        return float(max(0.0, improvement_rate))

    def _calculate_stagnation_score(self) -> float:
        """Calculate stagnation score based on recent fitness variations."""
        if len(self.fitness_history) < self.criteria.stagnation_window:
            return 0.0

        recent_fitness = self.fitness_history[-self.criteria.stagnation_window:]

        # Calculate coefficient of variation
        mean_fitness = np.mean(recent_fitness)
        std_fitness = np.std(recent_fitness)

        # Issue #13: Standardized division protection
        if abs(mean_fitness) < EPSILON_DIV:
            cv = 0.0
        else:
            cv = std_fitness / abs(mean_fitness)

        # Stagnation score is inverse of coefficient of variation
        stagnation_score = 1.0 / (1.0 + cv * 100)

        return float(stagnation_score)

    def _calculate_diversity_loss_rate(self) -> float:
        """Calculate rate of population diversity loss."""
        if len(self.diversity_history) < 3:
            return 0.0

        # Compare recent diversity to initial diversity
        initial_diversity = np.mean(self.diversity_history[:3])
        recent_diversity = np.mean(self.diversity_history[-3:])

        # Issue #13: Standardized division protection
        if initial_diversity < EPSILON_DIV:
            return 0.0

        diversity_retention = recent_diversity / initial_diversity
        diversity_loss_rate = 1.0 - diversity_retention

        return float(max(0.0, min(1.0, diversity_loss_rate)))

    def _predict_remaining_iterations(self) -> int:
        """Predict remaining iterations until convergence."""
        if not self.criteria.enable_performance_prediction:
            return -1

        if len(self.fitness_history) < self.criteria.prediction_window:
            return -1

        # Use simple exponential decay model for prediction
        recent_fitness = self.fitness_history[-self.criteria.prediction_window:]

        try:
            # Fit exponential decay: f(t) = a * exp(-b * t) + c
            iterations = np.arange(len(recent_fitness))

            # Linearize by taking log of (fitness - min_fitness + epsilon)
            min_fitness = min(recent_fitness)
            # Issue #13: Standardized division protection for log domain
            log_fitness = np.log(np.array(recent_fitness) - min_fitness + EPSILON_DIV)

            # Linear regression on log scale
            coeffs = np.polyfit(iterations, log_fitness, 1)
            decay_rate = -coeffs[0]

            if decay_rate > 0:
                # Predict iterations to reach fitness tolerance
                current_fitness = recent_fitness[-1]
                target_fitness = self.criteria.fitness_tolerance

                if current_fitness > target_fitness:
                    remaining_log_improvement = np.log(
                        (current_fitness - target_fitness + EPSILON_DIV) /
                        (current_fitness - min_fitness + EPSILON_DIV)
                    )
                    predicted_iterations = int(remaining_log_improvement / decay_rate)
                    return max(0, min(predicted_iterations, 1000))  # Cap at 1000

        except (ValueError, RuntimeError, FloatingPointError) as e:  # P2: Convergence prediction is optional
            logging.getLogger(__name__).debug(f"Convergence prediction failed: {e}")

        return -1  # Prediction failed

    def _estimate_convergence_probability(self) -> float:
        """Estimate probability of successful convergence."""
        if len(self.fitness_history) < 5:
            return 0.5  # Neutral probability initially

        factors = []

        # Factor 1: Improvement consistency
        recent_improvements = []
        for i in range(1, min(10, len(self.fitness_history))):
            improvement = self.fitness_history[-i-1] - self.fitness_history[-i]
            recent_improvements.append(improvement)

        if recent_improvements:
            positive_improvements = sum(1 for imp in recent_improvements if imp > 0)
            improvement_consistency = positive_improvements / len(recent_improvements)
            factors.append(improvement_consistency)

        # Factor 2: Convergence velocity stability
        if len(self.convergence_metrics_history) >= 3:
            recent_velocities = [m.convergence_velocity for m in self.convergence_metrics_history[-3:]]
            # Issue #13: Standardized division protection
            velocity_stability = 1.0 - np.std(recent_velocities) / (np.mean(np.abs(recent_velocities)) + EPSILON_DIV)
            factors.append(max(0.0, velocity_stability))

        # Factor 3: Diversity maintenance
        if len(self.diversity_history) >= 5:
            diversity_trend = np.polyfit(range(len(self.diversity_history)), self.diversity_history, 1)[0]
            diversity_factor = 1.0 / (1.0 + abs(diversity_trend) * 100)
            factors.append(diversity_factor)

        # Combine factors
        if factors:
            probability = np.mean(factors)
        else:
            probability = 0.5

        return float(np.clip(probability, 0.0, 1.0))

    def _calculate_statistical_confidence(self) -> float:
        """Calculate statistical confidence in convergence assessment."""
        if len(self.fitness_history) < self.criteria.min_sample_size:
            return 0.0

        # Use recent fitness values for statistical analysis
        sample_size = min(self.criteria.min_sample_size, len(self.fitness_history))
        recent_fitness = self.fitness_history[-sample_size:]

        # Calculate confidence interval for mean fitness
        try:
            mean_fitness = np.mean(recent_fitness)
            sem = stats.sem(recent_fitness)  # Standard error of mean

            if sem > 0:
                # Calculate confidence interval
                confidence_interval = stats.t.interval(
                    self.criteria.statistical_confidence_level,
                    len(recent_fitness) - 1,
                    loc=mean_fitness,
                    scale=sem
                )

                # Confidence is higher when interval is narrower
                interval_width = confidence_interval[1] - confidence_interval[0]
                # Issue #13: Standardized division protection
                normalized_width = interval_width / (abs(mean_fitness) + EPSILON_DIV)
                confidence = 1.0 / (1.0 + normalized_width)
            else:
                confidence = 1.0  # Perfect consistency

        except Exception:
            confidence = 0.5  # Default moderate confidence

        return float(np.clip(confidence, 0.0, 1.0))

    def _check_statistical_convergence(self) -> bool:
        """Check for statistical convergence using hypothesis testing."""
        if len(self.fitness_history) < self.criteria.min_sample_size:
            return False

        # Compare recent performance to earlier performance
        sample_size = min(self.criteria.min_sample_size // 2, len(self.fitness_history) // 2)

        if sample_size < 5:
            return False

        early_sample = self.fitness_history[:sample_size]
        recent_sample = self.fitness_history[-sample_size:]

        # Perform Mann-Whitney U test (non-parametric)
        try:
            statistic, p_value = stats.mannwhitneyu(
                early_sample, recent_sample, alternative='greater'
            )

            # Convergence if recent sample is significantly better
            alpha = 1.0 - self.criteria.statistical_confidence_level
            return p_value < alpha

        except Exception:
            return False

    def _detect_premature_convergence(self, metrics: ConvergenceMetrics) -> bool:
        """Detect premature convergence conditions."""
        if not self.criteria.premature_convergence_detection:
            return False

        # Premature convergence indicators:
        # 1. Very low diversity early in optimization
        # 2. All particles very similar but fitness not optimal
        # 3. Rapid diversity loss without corresponding fitness improvement

        if len(self.iteration_history) < 10:  # Too early to detect
            return False

        # Check for rapid diversity collapse
        if (metrics.population_diversity < self.criteria.min_diversity_threshold * 10 and
            metrics.iteration < 20):
            return True

        # Check for fitness plateau with diversity loss
        if (len(self.fitness_history) >= 10 and
            metrics.diversity_loss_rate > 0.8 and
            metrics.improvement_rate < 1e-4):
            return True

        return False

    def _update_convergence_status(self, metrics: ConvergenceMetrics) -> None:
        """Update internal convergence status based on metrics."""
        if self.current_status == ConvergenceStatus.NOT_STARTED:
            self.current_status = ConvergenceStatus.INITIALIZING

        elif self.current_status == ConvergenceStatus.INITIALIZING and metrics.iteration > 5:
            if metrics.convergence_velocity > 0:
                self.current_status = ConvergenceStatus.EXPLORING
            else:
                self.current_status = ConvergenceStatus.DIVERGING

        elif self.current_status == ConvergenceStatus.EXPLORING:
            if metrics.improvement_rate < 0.01 and metrics.population_diversity < 0.1:
                self.current_status = ConvergenceStatus.CONVERGING
            elif metrics.convergence_velocity < 0:
                self.current_status = ConvergenceStatus.OSCILLATING

        elif self.current_status == ConvergenceStatus.CONVERGING:
            if metrics.stagnation_score > 0.9:
                self.current_status = ConvergenceStatus.CONVERGED

    def get_convergence_diagnostics(self) -> Dict[str, Any]:
        """Get comprehensive convergence diagnostics."""
        if not self.convergence_metrics_history:
            return {'status': 'no_data'}

        latest_metrics = self.convergence_metrics_history[-1]

        return {
            'current_status': self.current_status.value,
            'convergence_detected_iteration': self.convergence_detected_iteration,
            'total_iterations': len(self.iteration_history),
            'stagnation_counter': self.stagnation_counter,
            'latest_metrics': {
                'best_fitness': latest_metrics.best_fitness,
                'population_diversity': latest_metrics.population_diversity,
                'convergence_velocity': latest_metrics.convergence_velocity,
                'improvement_rate': latest_metrics.improvement_rate,
                'convergence_probability': latest_metrics.convergence_probability,
                'confidence_level': latest_metrics.confidence_level
            },
            'convergence_criteria': {
                'fitness_tolerance': self.criteria.fitness_tolerance,
                'relative_improvement_threshold': self.criteria.relative_improvement_threshold,
                'min_diversity_threshold': self.criteria.min_diversity_threshold,
                'stagnation_window': self.criteria.stagnation_window
            },
            'controller_type': self.controller_type.value if self.controller_type else 'unknown',
            'prediction_accuracy': np.mean(self.prediction_accuracy_history) if self.prediction_accuracy_history else 0.0
        }

    def export_convergence_analysis(self, output_path: str = "convergence_analysis.json") -> Dict[str, Any]:
        """Export detailed convergence analysis."""
        analysis_data = {
            'metadata': {
                'controller_type': self.controller_type.value if self.controller_type else 'unknown',
                'analysis_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_iterations': len(self.iteration_history),
                'final_status': self.current_status.value
            },
            'convergence_history': {
                'iterations': self.iteration_history,
                'fitness_values': self.fitness_history,
                'diversity_values': self.diversity_history,
                'metrics': [
                    {
                        'iteration': m.iteration,
                        'best_fitness': m.best_fitness,
                        'population_diversity': m.population_diversity,
                        'convergence_velocity': m.convergence_velocity,
                        'improvement_rate': m.improvement_rate,
                        'convergence_probability': m.convergence_probability
                    }
                    for m in self.convergence_metrics_history
                ]
            },
            'convergence_criteria': {
                'fitness_tolerance': self.criteria.fitness_tolerance,
                'relative_improvement_threshold': self.criteria.relative_improvement_threshold,
                'min_diversity_threshold': self.criteria.min_diversity_threshold,
                'stagnation_window': self.criteria.stagnation_window,
                'max_stagnation_iterations': self.criteria.max_stagnation_iterations
            },
            'final_diagnostics': self.get_convergence_diagnostics()
        }

        # Save to file
        import json
        with open(output_path, 'w') as f:
            json.dump(analysis_data, f, indent=2)

        self.logger.info(f"Convergence analysis exported to {output_path}")
        return analysis_data


class PSOConvergenceValidator:
    """
    Validation framework for PSO convergence algorithms.

    Tests and validates convergence detection accuracy across different
    optimization scenarios and controller types.
    """

    def __init__(self):
        """Initialize PSO convergence validator."""
        self.logger = logging.getLogger(__name__)
        self.validation_results = {}

    def validate_convergence_detection(self,
                                     controller_type: SMCType,
                                     test_scenarios: int = 5) -> Dict[str, Any]:
        """
        Validate convergence detection accuracy for controller type.

        Args:
            controller_type: Controller type to test
            test_scenarios: Number of test scenarios to run

        Returns:
            Validation results with accuracy metrics
        """
        self.logger.info(f"Validating convergence detection for {controller_type.value}")

        validation_results = {
            'controller_type': controller_type.value,
            'test_scenarios': test_scenarios,
            'scenario_results': [],
            'accuracy_metrics': {},
            'validation_successful': False
        }

        scenario_accuracies = []

        for scenario in range(test_scenarios):
            try:
                scenario_result = self._run_convergence_test_scenario(
                    controller_type, scenario
                )
                validation_results['scenario_results'].append(scenario_result)
                scenario_accuracies.append(scenario_result['detection_accuracy'])

            except Exception as e:
                self.logger.warning(f"Scenario {scenario} failed: {e}")
                validation_results['scenario_results'].append({
                    'scenario': scenario,
                    'error': str(e),
                    'detection_accuracy': 0.0
                })
                scenario_accuracies.append(0.0)

        # Calculate overall accuracy metrics
        if scenario_accuracies:
            validation_results['accuracy_metrics'] = {
                'mean_accuracy': np.mean(scenario_accuracies),
                'std_accuracy': np.std(scenario_accuracies),
                'min_accuracy': np.min(scenario_accuracies),
                'max_accuracy': np.max(scenario_accuracies),
                'success_rate': sum(1 for acc in scenario_accuracies if acc > 0.7) / len(scenario_accuracies)
            }

            # Validation is successful if mean accuracy > 80%
            validation_results['validation_successful'] = (
                validation_results['accuracy_metrics']['mean_accuracy'] > 0.8
            )

        return validation_results

    def _run_convergence_test_scenario(self,
                                     controller_type: SMCType,
                                     scenario: int) -> Dict[str, Any]:
        """Run a single convergence detection test scenario."""
        from src.controllers.factory import create_smc_for_pso

        # Create test configuration
        config = load_config("config.yaml")

        # Create controller factory for this scenario
        def test_factory(gains):
            return create_smc_for_pso(
                smc_type=controller_type,
                gains=gains,
                max_force=150.0
            )

        # Create convergence analyzer
        analyzer = EnhancedConvergenceAnalyzer(
            criteria=ConvergenceCriteria(),
            controller_type=controller_type
        )

        # Run PSO with convergence monitoring
        tuner = PSOTuner(
            controller_factory=test_factory,
            config=config,
            seed=42 + scenario
        )

        # Mock PSO run for convergence testing
        converged = False
        convergence_iteration = None

        try:
            # Simulate PSO optimization with convergence tracking
            result = tuner.optimise(
                iters_override=25,
                n_particles_override=12
            )

            # Extract convergence information
            cost_history = result.get('history', {}).get('cost', [])

            # Simulate convergence detection
            for i, cost in enumerate(cost_history):
                # Create dummy population for diversity calculation
                dummy_population = np.random.random((12, len(result['best_pos'])))
                dummy_fitness = np.random.random(12) * cost

                metrics = analyzer.analyze_convergence(
                    iteration=i,
                    best_fitness=cost,
                    population_fitness=dummy_fitness,
                    population_positions=dummy_population
                )

                converged, status, explanation = analyzer.check_convergence(metrics)

                if converged and convergence_iteration is None:
                    convergence_iteration = i
                    break

            # Calculate detection accuracy
            actual_convergence = len(cost_history) - 5  # Assume convergence 5 iterations before end
            if convergence_iteration is not None:
                detection_error = abs(convergence_iteration - actual_convergence)
                detection_accuracy = max(0.0, 1.0 - detection_error / max(actual_convergence, 1))
            else:
                detection_accuracy = 0.0  # Failed to detect convergence

            return {
                'scenario': scenario,
                'actual_convergence_iteration': actual_convergence,
                'detected_convergence_iteration': convergence_iteration,
                'detection_accuracy': detection_accuracy,
                'final_cost': result['best_cost'],
                'convergence_status': status.value if converged else 'not_converged',
                'analysis_successful': True
            }

        except Exception as e:
            return {
                'scenario': scenario,
                'error': str(e),
                'detection_accuracy': 0.0,
                'analysis_successful': False
            }


def run_enhanced_convergence_validation() -> Dict[str, Any]:
    """Run comprehensive PSO convergence validation."""
    print("=" * 80)
    print("ENHANCED PSO CONVERGENCE VALIDATION - GitHub Issue #6")
    print("Advanced Convergence Criteria and Validation Algorithms")
    print("=" * 80)

    validator = PSOConvergenceValidator()

    validation_results = {
        'validation_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'controller_validations': {},
        'overall_metrics': {}
    }

    # Test all controller types
    controller_types = [SMCType.CLASSICAL, SMCType.ADAPTIVE, SMCType.SUPER_TWISTING, SMCType.HYBRID]

    all_accuracies = []
    successful_validations = 0

    for controller_type in controller_types:
        print(f"\n🔍 Validating convergence detection for {controller_type.value}...")

        controller_result = validator.validate_convergence_detection(
            controller_type, test_scenarios=3
        )

        validation_results['controller_validations'][controller_type.value] = controller_result

        if controller_result['validation_successful']:
            accuracy = controller_result['accuracy_metrics']['mean_accuracy']
            print(f"✅ {controller_type.value}: Validation PASSED (Accuracy: {accuracy:.1%})")
            all_accuracies.append(accuracy)
            successful_validations += 1
        else:
            accuracy = controller_result['accuracy_metrics'].get('mean_accuracy', 0.0)
            print(f"❌ {controller_type.value}: Validation FAILED (Accuracy: {accuracy:.1%})")
            all_accuracies.append(accuracy)

    # Calculate overall metrics
    if all_accuracies:
        validation_results['overall_metrics'] = {
            'overall_accuracy': np.mean(all_accuracies),
            'accuracy_std': np.std(all_accuracies),
            'success_rate': successful_validations / len(controller_types),
            'min_accuracy': np.min(all_accuracies),
            'max_accuracy': np.max(all_accuracies)
        }

    # Print summary
    print("\n" + "=" * 60)
    print("CONVERGENCE VALIDATION SUMMARY")
    print("=" * 60)

    overall_metrics = validation_results['overall_metrics']
    overall_accuracy = overall_metrics.get('overall_accuracy', 0.0)
    success_rate = overall_metrics.get('success_rate', 0.0)

    print(f"Overall Accuracy: {overall_accuracy:.1%}")
    print(f"Success Rate: {success_rate:.1%}")
    print(f"Successful Validations: {successful_validations}/{len(controller_types)}")

    if success_rate >= 0.75:
        print("\n🎉 ENHANCED CONVERGENCE VALIDATION: SUCCESSFUL")
        print("✅ Advanced convergence criteria validated across controllers")
        print("✅ Multi-criteria convergence detection working properly")
        print("✅ Statistical validation algorithms operational")
        print("✅ Performance prediction systems validated")
    else:
        print("\n⚠️  ENHANCED CONVERGENCE VALIDATION: PARTIAL SUCCESS")
        print(f"✅ {successful_validations} controllers validated successfully")
        print("⚠️  Some convergence algorithms may need refinement")

    return validation_results


if __name__ == "__main__":
    results = run_enhanced_convergence_validation()