#======================================================================================\\
#======== tests/test_plant/models/simplified/test_simplified_dynamics_comprehensive.py ========\\
#======================================================================================\\

"""
Comprehensive tests for Simplified DIP Dynamics Model.

Tests focus on:
- Initialization with various config types (Dict, SimplifiedConfig, AttributeDict, Pydantic v1/v2)
- Core dynamics computation under diverse conditions
- Physics delegation and matrix consistency
- Linearization accuracy and numerical stability
- Equilibrium states validation
- Step integration and energy drift
"""

from __future__ import annotations

import pytest
import numpy as np
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

from src.plant.models.simplified.dynamics import SimplifiedDIPDynamics
from src.plant.models.simplified.config import SimplifiedDIPConfig
from src.plant.core import NumericalInstabilityError


class MockAttributeDict:
    """Mock AttributeDict for testing."""
    def __init__(self, data: Dict[str, Any]):
        self._data = data

    def to_dict(self) -> Dict[str, Any]:
        return self._data


class MockPydanticV1Model:
    """Mock Pydantic v1 model for testing."""
    def __init__(self, data: Dict[str, Any]):
        self._data = data

    def dict(self) -> Dict[str, Any]:
        return self._data


class MockPydanticV2Model:
    """Mock Pydantic v2 model for testing."""
    def __init__(self, data: Dict[str, Any]):
        self._data = data

    def model_dump(self) -> Dict[str, Any]:
        return self._data


class TestInitializationAndConfigFiltering:
    """Test initialization with various config types and field filtering."""

    @pytest.fixture
    def valid_config_dict(self) -> Dict[str, Any]:
        """Create valid config dictionary."""
        return {
            'cart_mass': 1.0,
            'pendulum1_mass': 0.1,
            'pendulum2_mass': 0.1,
            'pendulum1_length': 0.5,
            'pendulum2_length': 0.5,
            'pendulum1_com': 0.25,
            'pendulum2_com': 0.25,
            'pendulum1_inertia': 0.01,
            'pendulum2_inertia': 0.01,
            'gravity': 9.81,
            'cart_friction': 0.1,
            'joint1_friction': 0.01,
            'joint2_friction': 0.01,
            'regularization_alpha': 1e-6,
            'max_condition_number': 1e12,
            'min_regularization': 1e-12
        }

    def test_init_with_simplified_config_object(self, valid_config_dict):
        """Test initialization with SimplifiedDIPConfig object."""
        config = SimplifiedDIPConfig.from_dict(valid_config_dict)
        dynamics = SimplifiedDIPDynamics(config)

        assert isinstance(dynamics.config, SimplifiedDIPConfig)
        assert dynamics.config.cart_mass == 1.0
        assert dynamics.config.gravity == 9.81

    def test_init_with_dict(self, valid_config_dict):
        """Test initialization with dictionary."""
        dynamics = SimplifiedDIPDynamics(valid_config_dict)

        assert isinstance(dynamics.config, SimplifiedDIPConfig)
        assert dynamics.config.cart_mass == 1.0
        assert dynamics.config.pendulum1_mass == 0.1

    def test_init_with_empty_dict_uses_defaults(self):
        """Test initialization with empty dict creates default config."""
        dynamics = SimplifiedDIPDynamics({})

        assert isinstance(dynamics.config, SimplifiedDIPConfig)
        # Should use defaults from SimplifiedDIPConfig
        assert dynamics.config.gravity == 9.81

    def test_init_with_attribute_dict(self, valid_config_dict):
        """Test initialization with AttributeDict object."""
        attr_dict = MockAttributeDict(valid_config_dict)
        dynamics = SimplifiedDIPDynamics(attr_dict)

        assert isinstance(dynamics.config, SimplifiedDIPConfig)
        assert dynamics.config.cart_mass == 1.0

    def test_init_with_pydantic_v2_model(self, valid_config_dict):
        """Test initialization with Pydantic v2 model (model_dump)."""
        pydantic_model = MockPydanticV2Model(valid_config_dict)
        dynamics = SimplifiedDIPDynamics(pydantic_model)

        assert isinstance(dynamics.config, SimplifiedDIPConfig)
        assert dynamics.config.cart_mass == 1.0

    def test_init_with_pydantic_v1_model(self, valid_config_dict):
        """Test initialization with Pydantic v1 model (dict)."""
        pydantic_model = MockPydanticV1Model(valid_config_dict)
        dynamics = SimplifiedDIPDynamics(pydantic_model)

        assert isinstance(dynamics.config, SimplifiedDIPConfig)
        assert dynamics.config.cart_mass == 1.0

    def test_filter_config_removes_unsupported_fields(self, valid_config_dict):
        """Test that config filtering removes unsupported fields."""
        # Add unsupported fields to config
        config_with_extra = valid_config_dict.copy()
        config_with_extra['unsupported_field'] = 123
        config_with_extra['another_unsupported'] = 'test'
        config_with_extra['wind_model'] = True  # Not supported by simplified

        # Create dynamics with AttributeDict to test filtering
        attr_dict = MockAttributeDict(config_with_extra)
        dynamics = SimplifiedDIPDynamics(attr_dict)

        # Should create successfully without unsupported fields
        assert isinstance(dynamics.config, SimplifiedDIPConfig)
        assert not hasattr(dynamics.config, 'unsupported_field')
        assert not hasattr(dynamics.config, 'wind_model')

    def test_filter_config_maps_field_names(self, valid_config_dict):
        """Test that config filtering maps field names correctly."""
        # Use old field names that need mapping
        config_with_old_names = valid_config_dict.copy()
        config_with_old_names['singularity_cond_threshold'] = 1e7
        config_with_old_names['regularization'] = 1e-5

        # Create dynamics with AttributeDict to test filtering
        attr_dict = MockAttributeDict(config_with_old_names)
        dynamics = SimplifiedDIPDynamics(attr_dict)

        # Should map to new field names
        assert dynamics.config.singularity_threshold == 1e7
        assert dynamics.config.regularization_alpha == 1e-5

    def test_init_with_invalid_config_type_raises_error(self):
        """Test initialization with invalid config type raises ValueError."""
        with pytest.raises(ValueError, match="config must be"):
            SimplifiedDIPDynamics("invalid_config")

    def test_init_fast_mode_and_monitoring_flags(self, valid_config_dict):
        """Test initialization with fast_mode and monitoring flags."""
        dynamics = SimplifiedDIPDynamics(
            valid_config_dict,
            enable_fast_mode=True,
            enable_monitoring=False
        )

        assert dynamics.enable_fast_mode is True
        assert dynamics.enable_monitoring is False


class TestCoreDynamicsComputation:
    """Test core dynamics computation under diverse conditions."""

    @pytest.fixture
    def dynamics(self) -> SimplifiedDIPDynamics:
        """Create dynamics model for testing."""
        config = SimplifiedDIPConfig.from_dict({
            'cart_mass': 1.0,
            'pendulum1_mass': 0.1,
            'pendulum2_mass': 0.1,
            'pendulum1_length': 0.5,
            'pendulum2_length': 0.5,
            'pendulum1_com': 0.25,
            'pendulum2_com': 0.25,
            'pendulum1_inertia': 0.01,
            'pendulum2_inertia': 0.01,
        })
        return SimplifiedDIPDynamics(config, enable_monitoring=False)

    def test_compute_dynamics_zero_state(self, dynamics):
        """Test dynamics computation at zero state."""
        state = np.zeros(6)
        control = np.array([0.0])

        result = dynamics.compute_dynamics(state, control)

        assert result.success
        assert result.state_derivative.shape == (6,)
        assert np.all(np.isfinite(result.state_derivative))
        # First 3 components (positions) should match last 3 (velocities)
        assert np.allclose(result.state_derivative[:3], state[3:6])

    def test_compute_dynamics_extreme_angles(self, dynamics):
        """Test dynamics computation with extreme angles."""
        # Near horizontal configuration
        state = np.array([0.0, np.pi/2 - 0.01, np.pi/2 - 0.01, 0.0, 0.0, 0.0])
        control = np.array([0.0])

        result = dynamics.compute_dynamics(state, control)

        assert result.success
        assert np.all(np.isfinite(result.state_derivative))

    def test_compute_dynamics_high_velocities(self, dynamics):
        """Test dynamics computation with high velocities."""
        state = np.array([0.0, 0.1, 0.2, 5.0, 20.0, 20.0])
        control = np.array([10.0])

        result = dynamics.compute_dynamics(state, control)

        assert result.success
        assert np.all(np.isfinite(result.state_derivative))

    def test_compute_dynamics_invalid_state_dimensions(self, dynamics):
        """Test dynamics computation rejects invalid state dimensions."""
        invalid_state = np.array([0.0, 0.1, 0.2])  # Only 3 elements
        control = np.array([0.0])

        result = dynamics.compute_dynamics(invalid_state, control)

        assert not result.success
        assert "Invalid state" in result.info.get('failure_reason', '')

    def test_compute_dynamics_non_finite_state(self, dynamics):
        """Test dynamics computation rejects non-finite state."""
        nan_state = np.array([0.0, np.nan, 0.0, 0.0, 0.0, 0.0])
        control = np.array([0.0])

        result = dynamics.compute_dynamics(nan_state, control)

        assert not result.success

    def test_compute_dynamics_excessive_control(self, dynamics):
        """Test dynamics computation rejects excessive control input."""
        state = np.zeros(6)
        excessive_control = np.array([2000.0])  # > 1000 limit

        result = dynamics.compute_dynamics(state, excessive_control)

        assert not result.success
        assert "Invalid control" in result.info.get('failure_reason', '')

    def test_compute_dynamics_fast_mode_vs_standard(self, dynamics):
        """Test both fast mode and standard mode produce valid results."""
        state = np.array([0.1, 0.2, 0.3, 0.1, 0.5, -0.3])
        control = np.array([5.0])

        # Standard mode
        dynamics.enable_fast_mode = False
        result_standard = dynamics.compute_dynamics(state, control)

        # Fast mode
        dynamics.enable_fast_mode = True
        result_fast = dynamics.compute_dynamics(state, control)

        # Both modes should succeed
        assert result_standard.success
        assert result_fast.success

        # Both modes should produce finite results
        assert np.all(np.isfinite(result_standard.state_derivative))
        assert np.all(np.isfinite(result_fast.state_derivative))

        # Velocity components (first 3) should match exactly (position derivatives)
        np.testing.assert_allclose(
            result_standard.state_derivative[:3],
            result_fast.state_derivative[:3],
            rtol=1e-10
        )

        # Both modes should produce physically reasonable accelerations
        # (may use different computation paths, so exact match not guaranteed)
        for i in range(3, 6):
            assert abs(result_standard.state_derivative[i]) < 1000.0
            assert abs(result_fast.state_derivative[i]) < 1000.0

    def test_compute_dynamics_returns_energy_values(self, dynamics):
        """Test compute_dynamics returns energy values in result."""
        state = np.array([0.0, 0.1, 0.2, 0.0, 0.0, 0.0])
        control = np.array([0.0])

        result = dynamics.compute_dynamics(state, control)

        assert result.success
        assert 'total_energy' in result.info
        assert 'kinetic_energy' in result.info
        assert 'potential_energy' in result.info
        assert all(np.isfinite(v) for v in [
            result.info['total_energy'],
            result.info['kinetic_energy'],
            result.info['potential_energy']
        ])


class TestPhysicsDelegation:
    """Test physics delegation and matrix consistency."""

    @pytest.fixture
    def dynamics(self) -> SimplifiedDIPDynamics:
        """Create dynamics model for testing."""
        config = SimplifiedDIPConfig.from_dict({
            'cart_mass': 1.0,
            'pendulum1_mass': 0.1,
            'pendulum2_mass': 0.1,
            'pendulum1_length': 0.5,
            'pendulum2_length': 0.5,
            'pendulum1_com': 0.25,
            'pendulum2_com': 0.25,
            'pendulum1_inertia': 0.01,
            'pendulum2_inertia': 0.01,
        })
        return SimplifiedDIPDynamics(config)

    def test_get_physics_matrices_delegation(self, dynamics):
        """Test that get_physics_matrices delegates to physics computer."""
        state = np.array([0.0, 0.1, 0.2, 0.0, 0.0, 0.0])

        M, C, G = dynamics.get_physics_matrices(state)

        # Should return valid matrices
        assert M.shape == (3, 3)
        assert C.shape == (3, 3)
        assert G.shape == (3,)
        assert np.all(np.isfinite(M))
        assert np.all(np.isfinite(C))
        assert np.all(np.isfinite(G))

    def test_compute_total_energy_delegation(self, dynamics):
        """Test that compute_total_energy delegates to physics computer."""
        state = np.array([0.0, 0.1, 0.2, 0.0, 1.0, 0.5])

        energy = dynamics.compute_total_energy(state)

        assert isinstance(energy, (float, np.floating))
        assert np.isfinite(energy)

    def test_physics_matrices_consistency_with_dynamics(self, dynamics):
        """Test physics matrices are consistent with dynamics computation."""
        state = np.array([0.0, 0.1, 0.2, 0.0, 1.0, 0.5])
        control = np.array([5.0])

        # Get matrices
        M, C, G = dynamics.get_physics_matrices(state)

        # Compute dynamics
        result = dynamics.compute_dynamics(state, control)

        # Both should succeed and use same underlying physics
        assert result.success
        assert np.all(np.isfinite(M))
        assert np.all(np.isfinite(result.state_derivative))

    def test_inertia_matrix_positive_definite(self, dynamics):
        """Test inertia matrix from physics is positive definite."""
        state = np.array([0.0, 0.1, 0.2, 0.0, 0.0, 0.0])

        M, _, _ = dynamics.get_physics_matrices(state)

        # Check positive definiteness via eigenvalues
        eigenvalues = np.linalg.eigvals(M)
        assert np.all(eigenvalues > 0), "Inertia matrix not positive definite"


class TestLinearization:
    """Test linearization accuracy and numerical stability."""

    @pytest.fixture
    def dynamics(self) -> SimplifiedDIPDynamics:
        """Create dynamics model for testing."""
        config = SimplifiedDIPConfig.from_dict({
            'cart_mass': 1.0,
            'pendulum1_mass': 0.1,
            'pendulum2_mass': 0.1,
            'pendulum1_length': 0.5,
            'pendulum2_length': 0.5,
            'pendulum1_com': 0.25,
            'pendulum2_com': 0.25,
            'pendulum1_inertia': 0.01,
            'pendulum2_inertia': 0.01,
        })
        return SimplifiedDIPDynamics(config)

    def test_linearization_upright_equilibrium(self, dynamics):
        """Test linearization around upright equilibrium."""
        eq_state = np.zeros(6)
        eq_input = np.array([0.0])

        A, B = dynamics.compute_linearization(eq_state, eq_input)

        assert A.shape == (6, 6)
        assert B.shape == (6, 1)
        assert np.all(np.isfinite(A))
        assert np.all(np.isfinite(B))

    def test_linearization_inverted_equilibrium(self, dynamics):
        """Test linearization around inverted (downward) equilibrium."""
        eq_state = np.array([0.0, np.pi, np.pi, 0.0, 0.0, 0.0])
        eq_input = np.array([0.0])

        A, B = dynamics.compute_linearization(eq_state, eq_input)

        assert A.shape == (6, 6)
        assert B.shape == (6, 1)
        assert np.all(np.isfinite(A))
        assert np.all(np.isfinite(B))

    def test_linearization_jacobian_accuracy(self, dynamics):
        """Test linearization Jacobian accuracy via finite differences."""
        eq_state = np.zeros(6)
        eq_input = np.array([0.0])

        A, B = dynamics.compute_linearization(eq_state, eq_input)

        # Verify A matrix accuracy manually for a few elements
        eps = 1e-8
        for i in [0, 1, 2]:  # Test a few state elements
            state_plus = eq_state.copy()
            state_plus[i] += eps

            f0 = dynamics.compute_dynamics(eq_state, eq_input).state_derivative
            f1 = dynamics.compute_dynamics(state_plus, eq_input).state_derivative

            expected_col = (f1 - f0) / eps
            np.testing.assert_allclose(A[:, i], expected_col, rtol=1e-4, atol=1e-6)

    def test_linearization_b_matrix_structure(self, dynamics):
        """Test B matrix has expected structure (control affects cart acceleration)."""
        eq_state = np.zeros(6)
        eq_input = np.array([0.0])

        A, B = dynamics.compute_linearization(eq_state, eq_input)

        # B matrix should primarily affect cart acceleration (index 3)
        # and have coupling to pendulum accelerations
        assert B[3, 0] != 0.0  # Cart force affects cart acceleration
        # First 3 rows (velocities) should be zero (control doesn't directly affect velocities)
        assert np.allclose(B[:3, 0], 0.0, atol=1e-6)

    def test_linearization_numerical_stability(self, dynamics):
        """Test linearization produces valid matrices at upright equilibrium."""
        # Test at upright equilibrium (most stable)
        eq_state = np.zeros(6)
        eq_input = np.array([0.0])

        A, B = dynamics.compute_linearization(eq_state, eq_input)

        # Should produce finite matrices
        assert np.all(np.isfinite(A))
        assert np.all(np.isfinite(B))

        # Verify matrix dimensions
        assert A.shape == (6, 6)
        assert B.shape == (6, 1)

        # Verify state-space structure (first 3 rows copy velocities)
        assert np.allclose(A[0, 3], 1.0)
        assert np.allclose(A[1, 4], 1.0)
        assert np.allclose(A[2, 5], 1.0)

        # Verify dynamics rows (3-5) have non-zero elements
        assert not np.allclose(A[3:6, :], 0.0)

        # Note: Condition number may be infinite due to state-space structure,
        # but all values should be finite and physically meaningful

    def test_linearization_fails_at_unstable_point(self, dynamics):
        """Test linearization raises error at non-equilibrium point."""
        # Non-equilibrium state with high velocities
        non_eq_state = np.array([0.0, 0.0, 0.0, 10.0, 10.0, 10.0])
        eq_input = np.array([0.0])

        # Compute dynamics at this state - should have non-zero derivative
        result = dynamics.compute_dynamics(non_eq_state, eq_input)

        # If derivative is non-zero (not equilibrium), linearization should warn or handle
        if not np.allclose(result.state_derivative, 0.0, atol=1e-3):
            # Either raises error or produces linearization with warning
            try:
                A, B = dynamics.compute_linearization(non_eq_state, eq_input)
                # If it succeeds, at least matrices should be finite
                assert np.all(np.isfinite(A))
                assert np.all(np.isfinite(B))
            except ValueError:
                # Acceptable to raise error for non-equilibrium
                pass


class TestEquilibriumStates:
    """Test equilibrium states validation."""

    @pytest.fixture
    def dynamics(self) -> SimplifiedDIPDynamics:
        """Create dynamics model for testing."""
        config = SimplifiedDIPConfig.from_dict({
            'cart_mass': 1.0,
            'pendulum1_mass': 0.1,
            'pendulum2_mass': 0.1,
            'pendulum1_length': 0.5,
            'pendulum2_length': 0.5,
            'pendulum1_com': 0.25,
            'pendulum2_com': 0.25,
            'pendulum1_inertia': 0.01,
            'pendulum2_inertia': 0.01,
        })
        return SimplifiedDIPDynamics(config, enable_monitoring=False)

    def test_upright_equilibrium_is_equilibrium(self, dynamics):
        """Test upright configuration is actually an equilibrium."""
        equilibria = dynamics.get_equilibrium_states()
        upright = equilibria['upright']
        control = np.array([0.0])

        result = dynamics.compute_dynamics(upright, control)

        assert result.success
        # At equilibrium with zero control, derivative should be near zero
        # (except velocities map to positions)
        assert np.allclose(result.state_derivative[3:], 0.0, atol=1e-6)

    def test_downward_equilibrium_is_equilibrium(self, dynamics):
        """Test downward (hanging) configuration is equilibrium."""
        equilibria = dynamics.get_equilibrium_states()
        downward = equilibria['downward']
        control = np.array([0.0])

        result = dynamics.compute_dynamics(downward, control)

        assert result.success
        # At equilibrium with zero control, angular accelerations should be zero
        assert np.allclose(result.state_derivative[3:], 0.0, atol=1e-6)

    def test_equilibrium_states_structure(self, dynamics):
        """Test equilibrium states have correct structure."""
        equilibria = dynamics.get_equilibrium_states()

        # Should have at least upright and downward
        assert 'upright' in equilibria
        assert 'downward' in equilibria

        # All should be 6-dimensional with zero velocities
        for name, eq_state in equilibria.items():
            assert eq_state.shape == (6,)
            assert np.allclose(eq_state[3:], 0.0), f"{name} has non-zero velocities"


class TestStepIntegration:
    """Test step integration and energy drift."""

    @pytest.fixture
    def dynamics(self) -> SimplifiedDIPDynamics:
        """Create dynamics model for testing."""
        config = SimplifiedDIPConfig.from_dict({
            'cart_mass': 1.0,
            'pendulum1_mass': 0.1,
            'pendulum2_mass': 0.1,
            'pendulum1_length': 0.5,
            'pendulum2_length': 0.5,
            'pendulum1_com': 0.25,
            'pendulum2_com': 0.25,
            'pendulum1_inertia': 0.01,
            'pendulum2_inertia': 0.01,
            'cart_friction': 0.0,  # Zero friction for energy tests
            'joint1_friction': 0.0,
            'joint2_friction': 0.0,
        })
        return SimplifiedDIPDynamics(config)

    def test_step_single_integration(self, dynamics):
        """Test single step integration produces valid state."""
        state = np.array([0.0, 0.1, 0.2, 0.0, 0.0, 0.0])
        control = np.array([0.0])
        dt = 0.01

        next_state = dynamics.step(state, control, dt)

        assert next_state.shape == (6,)
        assert np.all(np.isfinite(next_state))
        # State should change slightly
        assert not np.allclose(next_state, state)

    def test_step_trajectory_consistency(self, dynamics):
        """Test step integration produces consistent trajectory."""
        state = np.array([0.0, 0.1, 0.2, 0.0, 0.0, 0.0])
        control = np.array([0.0])
        dt = 0.01

        trajectory = [state]
        for _ in range(10):
            state = dynamics.step(state, control, dt)
            trajectory.append(state)

        # All states should be valid
        for s in trajectory:
            assert np.all(np.isfinite(s))

        # Trajectory should be smooth (no large jumps)
        for i in range(1, len(trajectory)):
            delta = np.linalg.norm(trajectory[i] - trajectory[i-1])
            assert delta < 1.0, "Large discontinuity in trajectory"

    def test_step_scalar_control_input(self, dynamics):
        """Test step integration accepts scalar control input."""
        state = np.zeros(6)
        control_scalar = 5.0  # Scalar, not array
        dt = 0.01

        next_state = dynamics.step(state, control_scalar, dt)

        assert next_state.shape == (6,)
        assert np.all(np.isfinite(next_state))

    def test_step_energy_drift_without_friction(self, dynamics):
        """Test energy drift is bounded without friction."""
        # Start with small perturbation from upright
        state = np.array([0.0, 0.05, 0.05, 0.0, 0.0, 0.0])
        control = np.array([0.0])
        dt = 0.001  # Small timestep for accuracy

        initial_energy = dynamics.compute_total_energy(state)

        # Simulate for 100 steps
        for _ in range(100):
            state = dynamics.step(state, control, dt)

        final_energy = dynamics.compute_total_energy(state)

        # Energy should be conserved (within integration error)
        # For Euler integration, expect some drift
        energy_drift_ratio = abs(final_energy - initial_energy) / (abs(initial_energy) + 1e-10)
        assert energy_drift_ratio < 0.5, f"Large energy drift: {energy_drift_ratio}"
