#======================================================================================\\\
#================ src/optimization/validation/pso_bounds_validator.py =================\\\
#======================================================================================\\\

"""
PSO Bounds Validation and Optimization Module.

This module provides comprehensive validation and optimization of PSO parameter bounds
for control system optimization. It ensures bounds are appropriate for each controller
type and provides intelligent bounds adjustment based on system characteristics.

Features:
- Controller-specific bounds validation
- Automatic bounds adjustment for stability
- Theoretical bounds derivation from system parameters
- Bounds optimization for convergence
- Statistical validation of bounds effectiveness

References:
- Franklin, G.F., et al. "Feedback Control of Dynamic Systems"
- Utkin, V. "Sliding Modes in Control and Optimization"
"""

from __future__ import annotations

import logging
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from src.config import ConfigSchema
from src.utils.numerical_stability import EPSILON_DIV


@dataclass
class BoundsValidationResult:
    """Result of bounds validation analysis."""
    is_valid: bool
    warnings: List[str]
    recommendations: List[str]
    adjusted_bounds: Optional[Dict[str, Tuple[List[float], List[float]]]]
    stability_analysis: Dict[str, Any]
    convergence_estimate: float


class PSOBoundsValidator:
    """
    Advanced PSO bounds validator for control system optimization.

    This class provides comprehensive validation and optimization of PSO parameter
    bounds to ensure effective controller tuning.
    """

    def __init__(self, config: ConfigSchema):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Controller-specific parameter interpretations
        self.controller_params = {
            'classical_smc': {
                'param_names': ['k1', 'k2', 'lambda1', 'lambda2', 'K', 'kd'],
                'param_roles': ['position_gain', 'velocity_gain', 'surface_slope1',
                              'surface_slope2', 'switching_gain', 'derivative_gain'],
                'stability_constraints': self._classical_smc_constraints,
                'recommended_ranges': {
                    'k1': (1.0, 100.0),      # Position gain
                    'k2': (1.0, 100.0),      # Velocity gain
                    'lambda1': (0.1, 50.0),  # Surface slope for θ1
                    'lambda2': (0.1, 50.0),  # Surface slope for θ2
                    'K': (1.0, 200.0),       # Switching gain
                    'kd': (0.1, 20.0)        # Derivative gain
                }
            },
            'sta_smc': {
                'param_names': ['k1', 'k2', 'lambda1', 'lambda2', 'alpha', 'beta'],
                'param_roles': ['position_gain', 'velocity_gain', 'surface_slope1',
                              'surface_slope2', 'sta_gain1', 'sta_gain2'],
                'stability_constraints': self._sta_smc_constraints,
                'recommended_ranges': {
                    'k1': (1.0, 80.0),
                    'k2': (1.0, 80.0),
                    'lambda1': (0.5, 30.0),
                    'lambda2': (0.5, 30.0),
                    'alpha': (0.1, 10.0),    # STA gain 1
                    'beta': (0.1, 10.0)      # STA gain 2
                }
            },
            'adaptive_smc': {
                'param_names': ['k1', 'k2', 'lambda1', 'lambda2', 'gamma'],
                'param_roles': ['position_gain', 'velocity_gain', 'surface_slope1',
                              'surface_slope2', 'adaptation_rate'],
                'stability_constraints': self._adaptive_smc_constraints,
                'recommended_ranges': {
                    'k1': (1.0, 60.0),
                    'k2': (1.0, 60.0),
                    'lambda1': (0.5, 25.0),
                    'lambda2': (0.5, 25.0),
                    'gamma': (0.1, 10.0)     # Adaptation rate
                }
            },
            'hybrid_adaptive_sta_smc': {
                'param_names': ['k1', 'k2', 'gamma1', 'gamma2'],
                'param_roles': ['hybrid_gain1', 'hybrid_gain2', 'adapt_rate1', 'adapt_rate2'],
                'stability_constraints': self._hybrid_constraints,
                'recommended_ranges': {
                    'k1': (1.0, 50.0),
                    'k2': (1.0, 50.0),
                    'gamma1': (0.1, 5.0),
                    'gamma2': (0.1, 5.0)
                }
            }
        }

    def validate_bounds(self, controller_type: str,
                       bounds_min: List[float],
                       bounds_max: List[float]) -> BoundsValidationResult:
        """
        Comprehensive validation of PSO bounds for a specific controller.

        Parameters
        ----------
        controller_type : str
            Type of controller ('classical_smc', 'sta_smc', etc.)
        bounds_min : List[float]
            Lower bounds for optimization
        bounds_max : List[float]
            Upper bounds for optimization

        Returns
        -------
        BoundsValidationResult
            Comprehensive validation results with recommendations
        """
        warnings_list = []
        recommendations = []
        is_valid = True

        # Basic validation
        if len(bounds_min) != len(bounds_max):
            warnings_list.append("Bounds min/max lengths don't match")
            is_valid = False

        if not all(b_min < b_max for b_min, b_max in zip(bounds_min, bounds_max)):
            warnings_list.append("Some lower bounds are not less than upper bounds")
            is_valid = False

        # Controller-specific validation
        if controller_type not in self.controller_params:
            warnings_list.append(f"Unknown controller type: {controller_type}")
            is_valid = False
        else:
            ctrl_info = self.controller_params[controller_type]
            expected_count = len(ctrl_info['param_names'])

            if len(bounds_min) != expected_count:
                warnings_list.append(
                    f"Expected {expected_count} parameters for {controller_type}, "
                    f"got {len(bounds_min)}"
                )
                is_valid = False

            # Check against recommended ranges
            for i, (param_name, (rec_min, rec_max)) in enumerate(ctrl_info['recommended_ranges'].items()):
                if i < len(bounds_min):
                    if bounds_min[i] < rec_min * 0.1:  # Allow 10x smaller
                        warnings_list.append(
                            f"Lower bound for {param_name} ({bounds_min[i]:.3f}) "
                            f"is very small (recommended min: {rec_min:.3f})"
                        )
                    if bounds_max[i] > rec_max * 10:  # Allow 10x larger
                        warnings_list.append(
                            f"Upper bound for {param_name} ({bounds_max[i]:.3f}) "
                            f"is very large (recommended max: {rec_max:.3f})"
                        )

        # Stability analysis
        stability_analysis = self._analyze_stability_constraints(
            controller_type, bounds_min, bounds_max
        )

        if not stability_analysis['satisfies_constraints']:
            warnings_list.append("Bounds may lead to unstable controllers")
            is_valid = False

        # Convergence analysis
        convergence_estimate = self._estimate_convergence_difficulty(
            bounds_min, bounds_max
        )

        if convergence_estimate > 0.8:
            warnings_list.append("Bounds are very wide; convergence may be slow")
            recommendations.append("Consider narrowing bounds based on preliminary tuning")

        # Generate adjusted bounds if needed
        adjusted_bounds = None
        if not is_valid or warnings_list:
            adjusted_bounds = self._generate_improved_bounds(controller_type)

        return BoundsValidationResult(
            is_valid=is_valid,
            warnings=warnings_list,
            recommendations=recommendations,
            adjusted_bounds=adjusted_bounds,
            stability_analysis=stability_analysis,
            convergence_estimate=convergence_estimate
        )

    def _classical_smc_constraints(self, bounds_min: List[float],
                                  bounds_max: List[float]) -> Dict[str, Any]:
        """Stability constraints for classical SMC."""
        constraints = {
            'satisfies_constraints': True,
            'constraint_violations': [],
            'recommendations': []
        }

        # k1, k2 > 0 (basic positivity)
        if bounds_min[0] <= 0 or bounds_min[1] <= 0:
            constraints['satisfies_constraints'] = False
            constraints['constraint_violations'].append("Position/velocity gains must be positive")

        # λ1, λ2 > 0 (sliding surface slopes must be positive)
        if bounds_min[2] <= 0 or bounds_min[3] <= 0:
            constraints['satisfies_constraints'] = False
            constraints['constraint_violations'].append("Surface slopes must be positive")

        # K > 0 (switching gain must be positive)
        if bounds_min[4] <= 0:
            constraints['satisfies_constraints'] = False
            constraints['constraint_violations'].append("Switching gain must be positive")

        # kd >= 0 (derivative gain can be zero)
        if bounds_min[5] < 0:
            constraints['satisfies_constraints'] = False
            constraints['constraint_violations'].append("Derivative gain must be non-negative")

        # Hurwitz condition approximation: λ values should be reasonable
        max_lambda = max(bounds_max[2], bounds_max[3])
        if max_lambda > 100:
            constraints['recommendations'].append(
                "Very large surface slopes may cause chattering"
            )

        return constraints

    def _sta_smc_constraints(self, bounds_min: List[float],
                            bounds_max: List[float]) -> Dict[str, Any]:
        """Stability constraints for super-twisting SMC."""
        constraints = {
            'satisfies_constraints': True,
            'constraint_violations': [],
            'recommendations': []
        }

        # Basic positivity for all gains
        if any(b <= 0 for b in bounds_min[:4]):
            constraints['satisfies_constraints'] = False
            constraints['constraint_violations'].append("All primary gains must be positive")

        # STA stability condition: α, β > 0
        if bounds_min[4] <= 0 or bounds_min[5] <= 0:
            constraints['satisfies_constraints'] = False
            constraints['constraint_violations'].append("STA gains (α, β) must be positive")

        # STA convergence condition approximation: α² > β
        min_alpha_sq = bounds_min[4] ** 2
        max_beta = bounds_max[5]
        if min_alpha_sq <= max_beta:
            constraints['recommendations'].append(
                "Consider ensuring α² > β for better STA convergence"
            )

        return constraints

    def _adaptive_smc_constraints(self, bounds_min: List[float],
                                 bounds_max: List[float]) -> Dict[str, Any]:
        """Stability constraints for adaptive SMC."""
        constraints = {
            'satisfies_constraints': True,
            'constraint_violations': [],
            'recommendations': []
        }

        # Basic positivity
        if any(b <= 0 for b in bounds_min):
            constraints['satisfies_constraints'] = False
            constraints['constraint_violations'].append("All gains must be positive")

        # Adaptation rate should be reasonable
        if bounds_max[4] > 50:  # gamma
            constraints['recommendations'].append(
                "Very high adaptation rates may cause instability"
            )

        if bounds_min[4] < 0.01:
            constraints['recommendations'].append(
                "Very low adaptation rates may prevent convergence"
            )

        return constraints

    def _hybrid_constraints(self, bounds_min: List[float],
                           bounds_max: List[float]) -> Dict[str, Any]:
        """Stability constraints for hybrid adaptive-STA SMC."""
        constraints = {
            'satisfies_constraints': True,
            'constraint_violations': [],
            'recommendations': []
        }

        # All gains must be positive
        if any(b <= 0 for b in bounds_min):
            constraints['satisfies_constraints'] = False
            constraints['constraint_violations'].append("All gains must be positive")

        # Adaptation rates should be balanced
        gamma_ratio = bounds_max[3] / bounds_max[2] if bounds_max[2] > 0 else float('inf')
        if gamma_ratio > 10 or gamma_ratio < 0.1:
            constraints['recommendations'].append(
                "Consider balancing adaptation rates (γ1 and γ2)"
            )

        return constraints

    def _analyze_stability_constraints(self, controller_type: str,
                                     bounds_min: List[float],
                                     bounds_max: List[float]) -> Dict[str, Any]:
        """Analyze stability constraints for given bounds."""
        if controller_type not in self.controller_params:
            return {'satisfies_constraints': False, 'error': 'Unknown controller type'}

        ctrl_info = self.controller_params[controller_type]
        return ctrl_info['stability_constraints'](bounds_min, bounds_max)

    def _estimate_convergence_difficulty(self, bounds_min: List[float],
                                       bounds_max: List[float]) -> float:
        """Estimate convergence difficulty based on bounds width."""
        ranges = [b_max - b_min for b_min, b_max in zip(bounds_min, bounds_max)]
        # Issue #13: Standardized division protection
        normalized_ranges = [r / (abs(b_min) + abs(b_max) + EPSILON_DIV)
                           for r, b_min, b_max in zip(ranges, bounds_min, bounds_max)]

        # Return mean normalized range as difficulty metric (0-1 scale)
        difficulty = np.mean(normalized_ranges)
        return min(difficulty, 1.0)

    def _generate_improved_bounds(self, controller_type: str) -> Dict[str, Tuple[List[float], List[float]]]:
        """Generate improved bounds based on theoretical analysis."""
        if controller_type not in self.controller_params:
            return {}

        ctrl_info = self.controller_params[controller_type]
        rec_ranges = ctrl_info['recommended_ranges']

        # Extract system parameters for bounds scaling
        try:
            physics = self.config.physics
            # Characteristic frequency based on pendulum lengths
            char_freq = np.sqrt(physics.gravity / max(physics.pendulum1_length,
                                                     physics.pendulum2_length))

            # Scale gains based on system characteristics
            max(physics.pendulum1_inertia, physics.pendulum2_inertia)
            mass_scale = physics.cart_mass + physics.pendulum1_mass + physics.pendulum2_mass

            scale_factor = np.sqrt(mass_scale * char_freq)
        except Exception:
            scale_factor = 1.0

        improved_bounds = {}

        for param_name, (rec_min, rec_max) in rec_ranges.items():
            if 'gain' in param_name or param_name in ['k1', 'k2', 'K']:
                # Scale force/acceleration gains
                scaled_min = rec_min * scale_factor * 0.5
                scaled_max = rec_max * scale_factor * 2.0
            elif 'lambda' in param_name:
                # Frequency-related parameters
                scaled_min = rec_min * char_freq * 0.5
                scaled_max = rec_max * char_freq * 2.0
            else:
                # Conservative scaling for other parameters
                scaled_min = rec_min * 0.8
                scaled_max = rec_max * 1.2

            improved_bounds[param_name] = (scaled_min, scaled_max)

        # Convert to lists for controller type
        param_names = ctrl_info['param_names']
        bounds_min = [improved_bounds[name][0] for name in param_names]
        bounds_max = [improved_bounds[name][1] for name in param_names]

        return {
            controller_type: (bounds_min, bounds_max)
        }

    def optimize_bounds_for_convergence(self, controller_type: str,
                                       initial_bounds: Tuple[List[float], List[float]],
                                       target_convergence_time: float = 50) -> Tuple[List[float], List[float]]:
        """
        Optimize bounds to achieve target convergence time.

        Parameters
        ----------
        controller_type : str
            Type of controller
        initial_bounds : Tuple[List[float], List[float]]
            Initial (min, max) bounds
        target_convergence_time : float
            Target PSO convergence time in iterations

        Returns
        -------
        Tuple[List[float], List[float]]
            Optimized (min, max) bounds
        """
        bounds_min, bounds_max = initial_bounds

        # Estimate search space volume
        volume = np.prod([b_max - b_min for b_min, b_max in zip(bounds_min, bounds_max)])

        # Adjust bounds based on convergence target
        if volume > target_convergence_time * 1000:  # Heuristic threshold
            # Reduce bounds by narrowing around recommended centers
            if controller_type in self.controller_params:
                rec_ranges = self.controller_params[controller_type]['recommended_ranges']
                param_names = self.controller_params[controller_type]['param_names']

                optimized_min = []
                optimized_max = []

                for i, param_name in enumerate(param_names):
                    if param_name in rec_ranges:
                        rec_min, rec_max = rec_ranges[param_name]
                        center = (rec_min + rec_max) / 2
                        half_range = (rec_max - rec_min) / 4  # Narrower range

                        optimized_min.append(max(bounds_min[i], center - half_range))
                        optimized_max.append(min(bounds_max[i], center + half_range))
                    else:
                        # Keep original bounds for unknown parameters
                        optimized_min.append(bounds_min[i])
                        optimized_max.append(bounds_max[i])

                return optimized_min, optimized_max

        return bounds_min, bounds_max

    def generate_bounds_report(self, controller_type: str) -> str:
        """Generate a comprehensive bounds analysis report."""
        if controller_type not in self.controller_params:
            return f"Unknown controller type: {controller_type}"

        ctrl_info = self.controller_params[controller_type]

        report = f"""
PSO Bounds Analysis Report for {controller_type.upper()}
{'=' * 60}

Parameter Information:
"""

        for i, (param_name, role) in enumerate(zip(ctrl_info['param_names'], ctrl_info['param_roles'])):
            rec_range = ctrl_info['recommended_ranges'].get(param_name, (0, 0))
            report += f"  {i+1}. {param_name} ({role})\n"
            report += f"     Recommended range: [{rec_range[0]:.1f}, {rec_range[1]:.1f}]\n"

        report += """
Stability Considerations:
  - All gains must be positive for stability
  - Switching gains should be large enough to overcome uncertainties
  - Surface slopes should ensure reasonable reaching time
  - Avoid excessively large gains to prevent chattering

Convergence Tips:
  - Start with narrow bounds around recommended values
  - Gradually widen if global optimum is not found
  - Consider multi-stage optimization with adaptive bounds
  - Monitor convergence rate and adjust accordingly

System-Specific Scaling:
  - Gains should scale with system inertia and characteristic frequencies
  - Consider actuator saturation limits in bounds selection
  - Account for measurement noise in derivative gains
"""

        return report


def validate_pso_configuration(config: ConfigSchema) -> BoundsValidationResult:
    """
    Validate complete PSO configuration for all controllers.

    Parameters
    ----------
    config : ConfigSchema
        Complete system configuration

    Returns
    -------
    BoundsValidationResult
        Aggregated validation results for all controllers
    """
    validator = PSOBoundsValidator(config)

    all_warnings = []
    all_recommendations = []
    all_valid = True
    all_adjusted_bounds = {}

    # Check each controller type in PSO bounds
    pso_bounds = config.pso.bounds

    # Default bounds
    default_validation = validator.validate_bounds(
        'classical_smc',  # Use as reference
        pso_bounds.min,
        pso_bounds.max
    )

    if not default_validation.is_valid:
        all_valid = False
        all_warnings.extend([f"Default bounds: {w}" for w in default_validation.warnings])

    # Controller-specific bounds
    controller_types = ['classical_smc', 'sta_smc', 'adaptive_smc', 'hybrid_adaptive_sta_smc']

    for ctrl_type in controller_types:
        if hasattr(pso_bounds, ctrl_type):
            ctrl_bounds = getattr(pso_bounds, ctrl_type)
            if ctrl_bounds is not None:
                validation = validator.validate_bounds(
                    ctrl_type,
                    ctrl_bounds.min,
                    ctrl_bounds.max
                )

                if not validation.is_valid:
                    all_valid = False
                    all_warnings.extend([f"{ctrl_type}: {w}" for w in validation.warnings])

                all_recommendations.extend([f"{ctrl_type}: {r}" for r in validation.recommendations])

                if validation.adjusted_bounds:
                    all_adjusted_bounds.update(validation.adjusted_bounds)

    return BoundsValidationResult(
        is_valid=all_valid,
        warnings=all_warnings,
        recommendations=all_recommendations,
        adjusted_bounds=all_adjusted_bounds if all_adjusted_bounds else None,
        stability_analysis={'overall_valid': all_valid},
        convergence_estimate=0.5  # Average estimate
    )