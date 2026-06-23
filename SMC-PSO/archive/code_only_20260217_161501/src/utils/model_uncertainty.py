"""
Model Parameter Uncertainty Module
==================================

Perturbs physical parameters (mass, length, inertia) to simulate model mismatch.

This module enables robustness testing by creating systematic parameter variations
that represent real-world model uncertainty (e.g., measurement errors, manufacturing
tolerances, unmodeled dynamics).

Usage:
    from src.utils.model_uncertainty import perturb_parameters, create_uncertainty_scenarios

    # Single perturbation
    perturbed_config = perturb_parameters(base_config, {'m1': 1.1, 'l1': 0.9})

    # Batch scenarios
    scenarios = create_uncertainty_scenarios(base_config, error_levels=[0.1, 0.2])

Author: Claude Code (LT-6 Model Uncertainty Analysis)
Date: October 18, 2025
"""

import copy
from typing import Dict, List, Tuple


def perturb_parameters(
    base_config,
    perturbations: Dict[str, float]
):
    """
    Perturb model parameters by multiplicative factors.

    This creates a new configuration where physical parameters are scaled
    to simulate model uncertainty. For example, a +10% error in mass1
    represents the controller being designed for 1.0kg but the real system
    having 1.1kg.

    Args:
        base_config: Base configuration (ConfigSchema from load_config)
        perturbations: {param_name: multiplier}
                      e.g., {'m1': 1.1} = +10% error in mass1
                           {'l1': 0.9} = -10% error in length1

    Returns:
        New config with perturbed parameters (copy, doesn't modify original)

    Example:
        # +10% error in mass1, -5% error in length2
        config = perturb_parameters(base, {'m1': 1.1, 'l2': 0.95})

    Supported Parameters:
        - Masses: m0, m1, m2 (cart, pendulum1, pendulum2)
        - Lengths: l1, l2 (pendulum1, pendulum2)
        - Inertias: I1, I2 (pendulum1, pendulum2)
    """
    # Create a deep copy using model_copy
    config = base_config.model_copy(deep=True)

    # Mapping from short names to config field names
    param_mapping = {
        'm0': 'cart_mass',
        'm1': 'pendulum1_mass',
        'm2': 'pendulum2_mass',
        'l1': 'pendulum1_length',
        'l2': 'pendulum2_length',
        'I1': 'pendulum1_inertia',
        'I2': 'pendulum2_inertia',
    }

    for param, multiplier in perturbations.items():
        if param not in param_mapping:
            raise ValueError(f"Unknown parameter: {param}. Supported: {list(param_mapping.keys())}")

        field = param_mapping[param]
        original_value = getattr(config.physics, field)
        setattr(config.physics, field, original_value * multiplier)

    return config


def create_uncertainty_scenarios(
    base_config,
    error_levels: List[float] = [0.1, 0.2]  # ±10%, ±20%
):
    """
    Create systematic uncertainty scenarios for robustness testing.

    Generates a comprehensive set of parameter perturbations that cover:
    - Nominal case (no error)
    - Single parameter variations (+/- each parameter independently)
    - Combined worst-case (all masses +error or all masses -error)

    This systematic approach ensures we test robustness across all
    physical parameters and identify which errors are most critical.

    Args:
        base_config: Base configuration (ConfigSchema from load_config)
        error_levels: List of fractional errors (e.g., [0.1, 0.2] = ±10%, ±20%)

    Returns:
        List of (scenario_name, perturbed_config) tuples

    Example:
        scenarios = create_uncertainty_scenarios(config, error_levels=[0.1, 0.2])
        # Returns ~29 scenarios:
        #   1 nominal +
        #   14 single-param scenarios × 2 error levels +
        #   2 combined worst-case × 2 error levels

    Scenario Types:
        1. "nominal" - No error (baseline)
        2. "m1+10%" - Mass1 with +10% error
        3. "m1-10%" - Mass1 with -10% error
        4. "all_masses+20%" - All masses with +20% error (worst-case overestimate)
        5. "all_masses-20%" - All masses with -20% error (worst-case underestimate)
        ... and so on for all parameters
    """
    scenarios = [("nominal", base_config)]

    params = {
        'masses': ['m0', 'm1', 'm2'],
        'lengths': ['l1', 'l2'],
        'inertias': ['I1', 'I2']
    }

    for error in error_levels:
        # Single parameter variations
        # (Test each parameter independently to identify critical sensitivities)
        for param_type, param_list in params.items():
            for param in param_list:
                # +error (overestimate)
                scenarios.append((
                    f"{param}+{int(error*100)}%",
                    perturb_parameters(base_config, {param: 1 + error})
                ))
                # -error (underestimate)
                scenarios.append((
                    f"{param}-{int(error*100)}%",
                    perturb_parameters(base_config, {param: 1 - error})
                ))

        # Combined worst-case scenarios
        # (Test correlated errors - e.g., all masses measured with same biased scale)

        # All masses +error
        scenarios.append((
            f"all_masses+{int(error*100)}%",
            perturb_parameters(base_config, {p: 1+error for p in params['masses']})
        ))
        # All masses -error
        scenarios.append((
            f"all_masses-{int(error*100)}%",
            perturb_parameters(base_config, {p: 1-error for p in params['masses']})
        ))

    return scenarios


def get_perturbation_summary(scenarios) -> Dict[str, int]:
    """
    Get summary statistics about generated scenarios.

    Args:
        scenarios: List of (scenario_name, config) tuples

    Returns:
        Dict with counts: {
            'total': int,
            'nominal': int,
            'single_param': int,
            'combined': int
        }
    """
    total = len(scenarios)
    nominal = sum(1 for name, _ in scenarios if name == 'nominal')
    combined = sum(1 for name, _ in scenarios if 'all_' in name)
    single_param = total - nominal - combined

    return {
        'total': total,
        'nominal': nominal,
        'single_param': single_param,
        'combined': combined
    }
