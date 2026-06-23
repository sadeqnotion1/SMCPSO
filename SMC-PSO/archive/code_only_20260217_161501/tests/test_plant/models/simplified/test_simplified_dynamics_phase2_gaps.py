#======================================================================================\
#=== tests/test_plant/models/simplified/test_simplified_dynamics_phase2_gaps.py ===\
#======================================================================================\

"""
Phase 2 Coverage Tests for Simplified DIP Dynamics.

Target: Push coverage from 76.26% to 90%+ by targeting specific uncovered lines.

Coverage Gaps Targeted:
1. Initialization edge cases (lines 54-103) - Invalid types, empty configs
2. Fast mode vs standard mode (lines 160-225) - Monitoring, error paths
3. Error handling paths (lines 296-335) - Invalid states, NaN/Inf handling
4. Monitoring & validation (lines 358-424) - Energy checks, diagnostics
5. Physics matrices and linearization (lines 246-276, 383-424)

Total: 15-20 new tests targeting ~66 uncovered statements (13.74% gap).
"""

import pytest
import numpy as np
import warnings
from unittest.mock import Mock, patch, MagicMock

from src.plant.models.simplified.dynamics import SimplifiedDIPDynamics
from src.plant.models.simplified.config import SimplifiedDIPConfig
from src.plant.core import NumericalInstabilityError


class TestInitializationEdgeCasesPhase2:
    """Phase 2: Test initialization with various config types and edge cases."""

    def test_init_with_empty_dict_returns_defaults(self):
        """Test initialization with empty dict returns default config."""
        # Empty dict should trigger default config creation (line 58)
        dynamics = SimplifiedDIPDynamics({})

        assert dynamics.config is not None
        assert dynamics.config.cart_mass == 1.0  # Default value
        assert dynamics.config.pendulum1_mass == 0.1  # Default value
        assert dynamics.config.gravity == 9.81  # Default value

    def test_init_with_simplified_config_object(self):
        """Test initialization with SimplifiedDIPConfig object."""
        config = SimplifiedDIPConfig.create_default()

        # Should accept SimplifiedDIPConfig directly (line 59-60)
        dynamics = SimplifiedDIPDynamics(config)

        assert dynamics.config.cart_mass == 1.0  # Default value
        assert dynamics.config is config

    def test_init_with_attribute_dict_non_empty(self):
        """Test initialization with AttributeDictionary containing valid data."""
        # Mock AttributeDictionary with to_dict method
        # Use valid values that satisfy physical constraints
        mock_config = Mock()
        mock_config.to_dict.return_value = {
            'cart_mass': 3.0,
            'pendulum1_mass': 0.5,
            'pendulum2_mass': 0.3,
            'pendulum1_length': 1.0,
            'pendulum2_length': 0.5,
            'pendulum1_com': 0.5,
            'pendulum2_com': 0.25,
            'pendulum1_inertia': 0.15,  # Must be >= m*L_com^2 = 0.5*0.5^2 = 0.125
            'pendulum2_inertia': 0.02,  # Must be >= m*L_com^2 = 0.3*0.25^2 = 0.01875
            'gravity': 9.81
        }
        # Remove pydantic methods to simulate AttributeDictionary
        del mock_config.model_dump
        del mock_config.dict

        # Should use to_dict path and filter config (lines 61-67)
        dynamics = SimplifiedDIPDynamics(mock_config)

        assert dynamics.config is not None
        assert dynamics.config.cart_mass == 3.0
        assert dynamics.config.pendulum1_mass == 0.5

    def test_filter_config_removes_unsupported_fields(self):
        """Test config filtering removes unsupported fields."""
        # Create dict with mixed supported and unsupported fields
        full_config = {
            'cart_mass': 2.0,
            'pendulum1_mass': 0.2,
            'pendulum2_mass': 0.15,
            'pendulum1_length': 0.8,
            'pendulum2_length': 0.6,
            'pendulum1_com': 0.4,
            'pendulum2_com': 0.3,
            'pendulum1_inertia': 0.08,
            'pendulum2_inertia': 0.04,
            'gravity': 9.81,
            'unsupported_field': 'should_be_removed',
            'another_bad_field': 42
        }

        mock_config = Mock()
        mock_config.to_dict.return_value = full_config
        del mock_config.model_dump
        del mock_config.dict

        # Should filter out unsupported fields (line 105-139)
        dynamics = SimplifiedDIPDynamics(mock_config)

        # Config should be valid with only supported fields
        assert dynamics.config is not None
        assert dynamics.config.cart_mass == 2.0
        assert dynamics.config.gravity == 9.81

    def test_filter_config_maps_field_names(self):
        """Test config filtering maps field names correctly."""
        # Test singularity_cond_threshold -> singularity_threshold mapping
        config_dict = {
            'cart_mass': 1.5,
            'pendulum1_mass': 0.3,
            'pendulum2_mass': 0.2,
            'pendulum1_length': 0.7,
            'pendulum2_length': 0.5,
            'pendulum1_com': 0.35,
            'pendulum2_com': 0.25,
            'pendulum1_inertia': 0.06,
            'pendulum2_inertia': 0.03,
            'singularity_cond_threshold': 1e4,  # Old name
            'regularization': 1e-5  # Old name
        }

        mock_config = Mock()
        mock_config.to_dict.return_value = config_dict
        del mock_config.model_dump
        del mock_config.dict

        # Should map field names (lines 111-138)
        dynamics = SimplifiedDIPDynamics(mock_config)

        assert dynamics.config is not None
        assert dynamics.config.cart_mass == 1.5


class TestFastModeVsStandardMode:
    """Phase 2: Test fast mode optimizations and standard mode comparison."""

    def test_standard_mode_uses_physics_computer(self):
        """Test standard mode (fast_mode=False) uses physics computer."""
        config = SimplifiedDIPConfig.create_default()
        dynamics = SimplifiedDIPDynamics(config, enable_fast_mode=False)

        state = np.array([0.0, 0.1, -0.1, 0.0, 0.0, 0.0])
        control = np.array([1.0])

        # Spy on standard dynamics method
        with patch.object(dynamics, '_compute_standard_dynamics', wraps=dynamics._compute_standard_dynamics) as mock_std:
            result = dynamics.compute_dynamics(state, control)

            # Standard mode should call _compute_standard_dynamics (line 182)
            mock_std.assert_called_once()
            assert result.success

    def test_fast_mode_initialization_optimizations(self):
        """Test fast mode enables physics optimizations during init."""
        config = SimplifiedDIPConfig.create_default()

        # Mock physics computer to verify optimization calls
        with patch('src.plant.models.simplified.dynamics.SimplifiedPhysicsComputer') as MockPhysics:
            mock_physics = MockPhysics.return_value
            mock_physics.set_simplified_inertia = Mock()
            mock_physics.enable_matrix_caching = Mock()

            # Create with fast mode (lines 101-103)
            dynamics = SimplifiedDIPDynamics(config, enable_fast_mode=True)

            # Verify optimizations were enabled
            mock_physics.set_simplified_inertia.assert_called_once_with(True)
            mock_physics.enable_matrix_caching.assert_called_once_with(True)

    def test_fast_mode_numba_parameters(self):
        """Test fast mode passes all parameters to Numba function."""
        # Create config with custom values (frozen dataclass)
        config = SimplifiedDIPConfig.from_dict({
            'cart_mass': 2.0,
            'pendulum1_mass': 0.3,
            'pendulum2_mass': 0.2,
            'pendulum1_length': 0.7,
            'pendulum2_length': 0.5,
            'pendulum1_com': 0.35,
            'pendulum2_com': 0.25,
            'pendulum1_inertia': 0.06,
            'pendulum2_inertia': 0.03,
            'regularization_alpha': 1e-5
        })

        dynamics = SimplifiedDIPDynamics(config, enable_fast_mode=True)

        state = np.array([0.0, 0.1, -0.1, 0.0, 0.0, 0.0])
        control = np.array([2.5])

        # Patch Numba function to verify parameters
        with patch('src.plant.models.simplified.dynamics.compute_simplified_dynamics_numba') as mock_numba:
            mock_numba.return_value = np.zeros(6)

            dynamics.compute_dynamics(state, control)

            # Verify all config parameters passed (lines 335-353)
            mock_numba.assert_called_once()
            call_args = mock_numba.call_args[0]
            assert call_args[1] == 2.5  # Control input
            assert call_args[2] == 2.0  # Cart mass


class TestErrorHandlingAndValidation:
    """Phase 2: Test error handling paths and validation logic."""

    def test_compute_dynamics_invalid_state_returns_failure(self):
        """Test compute_dynamics returns failure for invalid state."""
        config = SimplifiedDIPConfig.create_default()
        dynamics = SimplifiedDIPDynamics(config)

        # Invalid state (NaN values)
        invalid_state = np.array([np.nan, 0.0, 0.0, 0.0, 0.0, 0.0])
        control = np.array([0.0])

        # Should return failure result (lines 160-165)
        result = dynamics.compute_dynamics(invalid_state, control)

        assert result.success is False
        assert "Invalid state vector" in result.info.get('failure_reason', '')

    def test_compute_dynamics_invalid_control_returns_failure(self):
        """Test compute_dynamics returns failure for invalid control."""
        config = SimplifiedDIPConfig.create_default()
        dynamics = SimplifiedDIPDynamics(config)

        state = np.zeros(6)
        # Invalid control (too large)
        invalid_control = np.array([2000.0])

        # Should return failure result (lines 167-172)
        result = dynamics.compute_dynamics(state, invalid_control)

        assert result.success is False
        assert "Invalid control input" in result.info.get('failure_reason', '')

    def test_compute_dynamics_invalid_derivative_returns_failure(self):
        """Test compute_dynamics handles invalid derivative computation."""
        config = SimplifiedDIPConfig.create_default()
        dynamics = SimplifiedDIPDynamics(config, enable_fast_mode=False)

        state = np.zeros(6)
        control = np.array([0.0])

        # Mock physics to return invalid derivative
        with patch.object(dynamics.physics, 'compute_dynamics_rhs', return_value=np.array([np.nan] * 6)):
            result = dynamics.compute_dynamics(state, control)

            # Should catch invalid derivative (lines 185-191)
            assert result.success is False

    def test_compute_dynamics_numerical_instability_monitoring(self):
        """Test numerical instability triggers monitoring."""
        config = SimplifiedDIPConfig.create_default()
        dynamics = SimplifiedDIPDynamics(config, enable_monitoring=True)

        # Add stability monitor
        dynamics._stability_monitor = Mock()

        # Force numerical instability
        with patch.object(dynamics, '_compute_standard_dynamics', side_effect=NumericalInstabilityError("Test")):
            state = np.zeros(6)
            control = np.array([0.0])

            result = dynamics.compute_dynamics(state, control)

            # Should record instability (lines 207-218)
            assert result.success is False
            assert dynamics._stability_monitor.record_inversion.called

    def test_compute_dynamics_generic_exception_monitoring(self):
        """Test generic exceptions trigger monitoring."""
        config = SimplifiedDIPConfig.create_default()
        dynamics = SimplifiedDIPDynamics(config, enable_monitoring=True)

        # Add stability monitor
        dynamics._stability_monitor = Mock()

        # Force generic exception
        with patch.object(dynamics, '_compute_standard_dynamics', side_effect=RuntimeError("Generic error")):
            state = np.zeros(6)
            control = np.array([0.0])

            result = dynamics.compute_dynamics(state, control)

            # Should record failure (lines 220-231)
            assert result.success is False
            assert dynamics._stability_monitor.record_inversion.called

    def test_step_normalizes_scalar_control(self):
        """Test step() normalizes scalar control input."""
        config = SimplifiedDIPConfig.create_default()
        dynamics = SimplifiedDIPDynamics(config)

        state = np.zeros(6)
        # Scalar control (line 296-297)
        scalar_control = 1.5
        dt = 0.01

        result_state = dynamics.step(state, scalar_control, dt)

        assert result_state is not None
        assert result_state.shape == (6,)


class TestPhysicsMatricesAndLinearization:
    """Phase 2: Test physics matrices and linearization edge cases."""

    def test_get_physics_matrices_delegates_to_physics(self):
        """Test get_physics_matrices delegates to physics computer."""
        config = SimplifiedDIPConfig.create_default()
        dynamics = SimplifiedDIPDynamics(config)

        state = np.array([0.0, 0.1, -0.1, 0.0, 0.0, 0.0])

        # Mock physics computer
        with patch.object(dynamics.physics, 'get_physics_matrices', return_value=(
            np.eye(3), np.zeros((3, 3)), np.ones(3)
        )) as mock_get:
            M, C, G = dynamics.get_physics_matrices(state)

            # Should delegate call (line 246)
            mock_get.assert_called_once_with(state)
            assert M.shape == (3, 3)
            assert C.shape == (3, 3)
            assert G.shape == (3,)

    def test_compute_total_energy_delegates_to_physics(self):
        """Test compute_total_energy delegates to physics computer."""
        config = SimplifiedDIPConfig.create_default()
        dynamics = SimplifiedDIPDynamics(config)

        state = np.array([0.1, 0.2, 0.05, 0.1, -0.03, -0.05])

        # Mock physics computer (line 248-250)
        with patch.object(dynamics.physics, 'compute_total_energy', return_value=10.5) as mock_energy:
            energy = dynamics.compute_total_energy(state)

            mock_energy.assert_called_once_with(state)
            assert energy == 10.5

    def test_compute_linearization_interface(self):
        """Test compute_linearization interface."""
        config = SimplifiedDIPConfig.create_default()
        dynamics = SimplifiedDIPDynamics(config)

        eq_state = np.zeros(6)
        eq_input = np.array([0.0])

        # Should call _compute_linearization_matrices (line 267)
        A, B = dynamics.compute_linearization(eq_state, eq_input)

        assert A.shape == (6, 6)
        assert B.shape == (6, 1)

    def test_get_equilibrium_states_returns_all_configs(self):
        """Test get_equilibrium_states returns all standard equilibria."""
        config = SimplifiedDIPConfig.create_default()
        dynamics = SimplifiedDIPDynamics(config)

        # Get equilibria (lines 269-276)
        equilibria = dynamics.get_equilibrium_states()

        assert 'upright' in equilibria
        assert 'downward' in equilibria
        assert 'mixed_1' in equilibria
        assert 'mixed_2' in equilibria

        # Verify values
        np.testing.assert_array_equal(equilibria['upright'], np.zeros(6))
        np.testing.assert_array_equal(equilibria['downward'], np.array([0.0, np.pi, np.pi, 0.0, 0.0, 0.0]))
        np.testing.assert_array_equal(equilibria['mixed_1'], np.array([0.0, 0.0, np.pi, 0.0, 0.0, 0.0]))
        np.testing.assert_array_equal(equilibria['mixed_2'], np.array([0.0, np.pi, 0.0, 0.0, 0.0, 0.0]))

    def test_linearization_at_unstable_equilibrium_raises(self):
        """Test linearization raises ValueError for unstable equilibrium."""
        config = SimplifiedDIPConfig.create_default()
        dynamics = SimplifiedDIPDynamics(config)

        # Use state that makes compute_dynamics fail
        with patch.object(dynamics, 'compute_dynamics') as mock_compute:
            # Mock failure result
            mock_result = Mock()
            mock_result.success = False
            mock_compute.return_value = mock_result

            unstable_state = np.array([10.0, 2.0, -2.0, 1.0, 1.0, 1.0])
            control = np.array([0.0])

            # Should raise ValueError (lines 392-394)
            with pytest.raises(ValueError, match="Cannot linearize"):
                dynamics.compute_linearization(unstable_state, control)

    def test_linearization_a_matrix_finite_difference(self):
        """Test linearization A matrix computation uses finite differences."""
        config = SimplifiedDIPConfig.create_default()
        dynamics = SimplifiedDIPDynamics(config)

        eq_state = np.array([0.0, 0.05, -0.05, 0.0, 0.0, 0.0])
        eq_input = np.array([0.0])

        # Linearization should use finite differences (lines 389-410)
        A, B = dynamics.compute_linearization(eq_state, eq_input)

        # A should be computed for all state dimensions
        assert A.shape == (6, 6)
        assert np.all(np.isfinite(A))

    def test_linearization_b_matrix_finite_difference(self):
        """Test linearization B matrix computation uses finite differences."""
        config = SimplifiedDIPConfig.create_default()
        dynamics = SimplifiedDIPDynamics(config)

        eq_state = np.zeros(6)
        eq_input = np.array([0.0])

        # Linearization should compute B matrix (lines 411-423)
        A, B = dynamics.compute_linearization(eq_state, eq_input)

        # B should show control influence
        assert B.shape == (6, 1)
        assert np.all(np.isfinite(B))


class TestMonitoringAndDiagnostics:
    """Phase 2: Test monitoring and diagnostic features."""

    def test_successful_computation_records_conditioning(self):
        """Test successful computation records matrix conditioning."""
        config = SimplifiedDIPConfig.create_default()
        dynamics = SimplifiedDIPDynamics(config, enable_monitoring=True)

        # Add stability monitor
        mock_monitor = Mock()
        dynamics._stability_monitor = mock_monitor

        # Mock physics conditioning
        with patch.object(dynamics.physics, 'get_matrix_conditioning', return_value=100.0):
            state = np.zeros(6)
            control = np.array([0.0])

            result = dynamics.compute_dynamics(state, control)

            # Should record conditioning (lines 426-434)
            assert result.success
            mock_monitor.record_inversion.assert_called_once()
            call_kwargs = mock_monitor.record_inversion.call_args[1]
            assert call_kwargs['condition_number'] == 100.0
            assert call_kwargs['failed'] is False

    def test_instability_records_infinite_conditioning(self):
        """Test numerical instability records with infinite conditioning."""
        config = SimplifiedDIPConfig.create_default()
        dynamics = SimplifiedDIPDynamics(config, enable_monitoring=True)

        # Add stability monitor
        mock_monitor = Mock()
        dynamics._stability_monitor = mock_monitor

        # Mock conditioning failure
        with patch.object(dynamics.physics, 'get_matrix_conditioning', side_effect=Exception("Singular")):
            with patch.object(dynamics, '_compute_standard_dynamics', side_effect=NumericalInstabilityError("Test")):
                state = np.zeros(6)
                control = np.array([0.0])

                result = dynamics.compute_dynamics(state, control)

                # Should record with inf conditioning (lines 436-448)
                assert result.success is False
                mock_monitor.record_inversion.assert_called_once()
                call_kwargs = mock_monitor.record_inversion.call_args[1]
                assert call_kwargs['condition_number'] == np.inf
                assert call_kwargs['failed'] is True

    def test_computation_failure_records_infinite_conditioning(self):
        """Test generic failure records with infinite conditioning."""
        config = SimplifiedDIPConfig.create_default()
        dynamics = SimplifiedDIPDynamics(config, enable_monitoring=True)

        # Add stability monitor
        mock_monitor = Mock()
        dynamics._stability_monitor = mock_monitor

        # Force generic exception
        with patch.object(dynamics, '_compute_standard_dynamics', side_effect=RuntimeError("Generic")):
            state = np.zeros(6)
            control = np.array([0.0])

            result = dynamics.compute_dynamics(state, control)

            # Should record with inf conditioning (lines 450-457)
            assert result.success is False
            mock_monitor.record_inversion.assert_called_once()
            call_kwargs = mock_monitor.record_inversion.call_args[1]
            assert call_kwargs['condition_number'] == np.inf
            assert call_kwargs['failed'] is True

    def test_compute_dynamics_includes_energy_analysis(self):
        """Test successful computation includes energy analysis."""
        config = SimplifiedDIPConfig.create_default()
        dynamics = SimplifiedDIPDynamics(config, enable_monitoring=False)

        state = np.array([0.0, 0.1, -0.1, 0.0, 0.0, 0.0])
        control = np.array([0.0])

        # Mock physics energy methods
        with patch.object(dynamics.physics, 'compute_total_energy', return_value=5.0):
            with patch.object(dynamics.physics, 'compute_kinetic_energy', return_value=2.0):
                with patch.object(dynamics.physics, 'compute_potential_energy', return_value=3.0):
                    result = dynamics.compute_dynamics(state, control)

                    # Should include energy in result (lines 197-205)
                    assert result.success
                    assert result.info['total_energy'] == 5.0
                    assert result.info['kinetic_energy'] == 2.0
                    assert result.info['potential_energy'] == 3.0


class TestLegacyCompatibility:
    """Phase 2: Test legacy compatibility methods."""

    def test_rhs_core_with_scalar_control(self):
        """Test _rhs_core legacy method with scalar control."""
        config = SimplifiedDIPConfig.create_default()
        dynamics = SimplifiedDIPDynamics(config)

        state = np.array([0.0, 0.1, -0.1, 0.0, 0.0, 0.0])
        scalar_u = 1.5

        # Call legacy method (lines 459-481)
        derivative = dynamics._rhs_core(state, scalar_u)

        assert derivative.shape == (6,)
        assert np.all(np.isfinite(derivative))

    def test_rhs_core_with_array_control(self):
        """Test _rhs_core legacy method with array control."""
        config = SimplifiedDIPConfig.create_default()
        dynamics = SimplifiedDIPDynamics(config)

        state = np.array([0.0, 0.1, -0.1, 0.0, 0.0, 0.0])
        array_u = np.array([2.0])

        # Call legacy method (line 474)
        derivative = dynamics._rhs_core(state, array_u)

        assert derivative.shape == (6,)
        assert np.all(np.isfinite(derivative))


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
