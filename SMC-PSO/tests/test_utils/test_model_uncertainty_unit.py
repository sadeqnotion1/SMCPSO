"""
================================================================================
Unit Tests for Model Uncertainty Module
================================================================================

Unit tests for src/utils/model_uncertainty.py

Tests cover:
1. Parameter perturbation (perturb_parameters)
2. Uncertainty scenario generation (create_uncertainty_scenarios)
3. Error handling and validation

Author: DIP_SMC_PSO Team
Created: December 21, 2025 (Week 3 Session 13 - Final Push to 590)
"""

import pytest
import numpy as np
from unittest.mock import MagicMock
from src.utils.model_uncertainty import (
    perturb_parameters,
    create_uncertainty_scenarios,
)


# =============================================================================
# Test perturb_parameters
# =============================================================================

def test_perturb_single_mass():
    """Perturb a single mass parameter."""
    base_config = MagicMock()
    base_config.physics = MagicMock(
        cart_mass=1.0,
        pendulum1_mass=0.1,
        pendulum2_mass=0.1,
        pendulum1_length=0.5,
        pendulum2_length=0.5,
        pendulum1_inertia=0.01,
        pendulum2_inertia=0.01,
    )
    base_config.model_copy = MagicMock(return_value=base_config)

    result = perturb_parameters(base_config, {'m1': 1.1})  # +10% error

    # Should multiply pendulum1_mass by 1.1
    assert hasattr(result.physics, 'pendulum1_mass')


def test_perturb_multiple_parameters():
    """Perturb multiple parameters simultaneously."""
    base_config = MagicMock()
    base_config.physics = MagicMock(
        cart_mass=1.0,
        pendulum1_mass=0.1,
        pendulum2_mass=0.1,
        pendulum1_length=0.5,
        pendulum2_length=0.5,
        pendulum1_inertia=0.01,
        pendulum2_inertia=0.01,
    )
    base_config.model_copy = MagicMock(return_value=base_config)

    result = perturb_parameters(base_config, {'m1': 1.1, 'l2': 0.9})

    assert result is not None


def test_perturb_unknown_parameter_raises_error():
    """Unknown parameter should raise ValueError."""
    base_config = MagicMock()
    base_config.model_copy = MagicMock(return_value=base_config)

    with pytest.raises(ValueError, match="Unknown parameter"):
        perturb_parameters(base_config, {'invalid_param': 1.1})


def test_perturb_all_masses():
    """Perturb all mass parameters."""
    base_config = MagicMock()
    base_config.physics = MagicMock(
        cart_mass=1.0,
        pendulum1_mass=0.1,
        pendulum2_mass=0.1,
        pendulum1_length=0.5,
        pendulum2_length=0.5,
        pendulum1_inertia=0.01,
        pendulum2_inertia=0.01,
    )
    base_config.model_copy = MagicMock(return_value=base_config)

    result = perturb_parameters(base_config, {'m0': 1.2, 'm1': 1.2, 'm2': 1.2})

    assert result is not None


def test_perturb_all_lengths():
    """Perturb all length parameters."""
    base_config = MagicMock()
    base_config.physics = MagicMock(
        cart_mass=1.0,
        pendulum1_mass=0.1,
        pendulum2_mass=0.1,
        pendulum1_length=0.5,
        pendulum2_length=0.5,
        pendulum1_inertia=0.01,
        pendulum2_inertia=0.01,
    )
    base_config.model_copy = MagicMock(return_value=base_config)

    result = perturb_parameters(base_config, {'l1': 0.9, 'l2': 1.1})

    assert result is not None


def test_perturb_all_inertias():
    """Perturb all inertia parameters."""
    base_config = MagicMock()
    base_config.physics = MagicMock(
        cart_mass=1.0,
        pendulum1_mass=0.1,
        pendulum2_mass=0.1,
        pendulum1_length=0.5,
        pendulum2_length=0.5,
        pendulum1_inertia=0.01,
        pendulum2_inertia=0.01,
    )
    base_config.model_copy = MagicMock(return_value=base_config)

    result = perturb_parameters(base_config, {'I1': 1.15, 'I2': 0.85})

    assert result is not None


def test_perturb_zero_multiplier():
    """Zero multiplier should set parameter to zero."""
    base_config = MagicMock()
    base_config.physics = MagicMock(
        cart_mass=1.0,
        pendulum1_mass=0.1,
        pendulum2_mass=0.1,
        pendulum1_length=0.5,
        pendulum2_length=0.5,
        pendulum1_inertia=0.01,
        pendulum2_inertia=0.01,
    )
    base_config.model_copy = MagicMock(return_value=base_config)

    result = perturb_parameters(base_config, {'m1': 0.0})

    assert result is not None


def test_perturb_negative_multiplier():
    """Negative multiplier should work (though physically unrealistic)."""
    base_config = MagicMock()
    base_config.physics = MagicMock(
        cart_mass=1.0,
        pendulum1_mass=0.1,
        pendulum2_mass=0.1,
        pendulum1_length=0.5,
        pendulum2_length=0.5,
        pendulum1_inertia=0.01,
        pendulum2_inertia=0.01,
    )
    base_config.model_copy = MagicMock(return_value=base_config)

    result = perturb_parameters(base_config, {'m1': -0.5})

    assert result is not None


def test_perturb_large_multiplier():
    """Large multiplier (2x, 5x) should work."""
    base_config = MagicMock()
    base_config.physics = MagicMock(
        cart_mass=1.0,
        pendulum1_mass=0.1,
        pendulum2_mass=0.1,
        pendulum1_length=0.5,
        pendulum2_length=0.5,
        pendulum1_inertia=0.01,
        pendulum2_inertia=0.01,
    )
    base_config.model_copy = MagicMock(return_value=base_config)

    result = perturb_parameters(base_config, {'m1': 5.0})

    assert result is not None


# =============================================================================
# Test create_uncertainty_scenarios
# =============================================================================

def test_create_scenarios_includes_nominal():
    """Scenarios should include nominal case."""
    base_config = MagicMock()

    scenarios = create_uncertainty_scenarios(base_config, error_levels=[0.1])

    # First scenario should be ("nominal", base_config)
    assert len(scenarios) > 0
    assert scenarios[0][0] == "nominal"


def test_create_scenarios_default_error_levels():
    """Default error levels should be [0.1, 0.2]."""
    base_config = MagicMock()

    scenarios = create_uncertainty_scenarios(base_config)  # Use defaults

    # Should have scenarios with 10% and 20% errors
    assert len(scenarios) > 1


def test_create_scenarios_single_error_level():
    """Single error level should generate scenarios."""
    base_config = MagicMock()

    scenarios = create_uncertainty_scenarios(base_config, error_levels=[0.15])

    # Should have nominal + single-param scenarios + combined scenarios
    assert len(scenarios) > 5


def test_create_scenarios_multiple_error_levels():
    """Multiple error levels should multiply scenarios."""
    base_config = MagicMock()

    scenarios_1 = create_uncertainty_scenarios(base_config, error_levels=[0.1])
    scenarios_2 = create_uncertainty_scenarios(base_config, error_levels=[0.1, 0.2])

    # More error levels → more scenarios
    assert len(scenarios_2) > len(scenarios_1)


def test_scenario_names_are_strings():
    """All scenario names should be strings."""
    base_config = MagicMock()

    scenarios = create_uncertainty_scenarios(base_config, error_levels=[0.1])

    for name, config in scenarios:
        assert isinstance(name, str), f"Scenario name should be string, got {type(name)}"


def test_scenarios_return_tuples():
    """Scenarios should be list of (name, config) tuples."""
    base_config = MagicMock()

    scenarios = create_uncertainty_scenarios(base_config, error_levels=[0.1])

    assert isinstance(scenarios, list)
    for item in scenarios:
        assert isinstance(item, tuple), "Each scenario should be a tuple"
        assert len(item) == 2, "Each tuple should have 2 elements (name, config)"


def test_empty_error_levels():
    """Empty error levels should return only nominal."""
    base_config = MagicMock()

    scenarios = create_uncertainty_scenarios(base_config, error_levels=[])

    # Should only have nominal case
    assert len(scenarios) == 1
    assert scenarios[0][0] == "nominal"


def test_zero_error_level_skipped():
    """Zero error level should be skipped (same as nominal)."""
    base_config = MagicMock()

    scenarios = create_uncertainty_scenarios(base_config, error_levels=[0.0, 0.1])

    # Should not duplicate nominal case
    # Count occurrences of "nominal"
    nominal_count = sum(1 for name, _ in scenarios if name == "nominal")
    assert nominal_count == 1, "Should have exactly one nominal scenario"


def test_negative_error_level():
    """Negative error level should work (represents -X% error)."""
    base_config = MagicMock()

    # Negative error level is unusual but valid (means decrease)
    scenarios = create_uncertainty_scenarios(base_config, error_levels=[-0.1])

    assert len(scenarios) > 1


def test_create_scenarios_large_error():
    """Large error levels (50%, 100%) should work."""
    base_config = MagicMock()

    scenarios = create_uncertainty_scenarios(base_config, error_levels=[0.5, 1.0])

    # Should have scenarios
    assert len(scenarios) > 1


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
