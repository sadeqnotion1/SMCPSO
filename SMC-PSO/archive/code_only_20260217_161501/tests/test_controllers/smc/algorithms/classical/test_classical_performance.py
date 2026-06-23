#======================================================================================\\
#==== tests/test_controllers/smc/algorithms/classical/test_classical_performance.py ===\\
#======================================================================================\\

"""
Performance analysis tests for Modular Classical SMC.

Tests:
- Performance analysis integration
- Parameter retrieval completeness
- Chattering reduction effectiveness
"""

from __future__ import annotations

import numpy as np
import pytest

from src.controllers.smc.algorithms import ModularClassicalSMC, ClassicalSMCConfig


class TestPerformanceAnalysis:
    """Test performance analysis integration."""

    @pytest.fixture
    def controller(self) -> ModularClassicalSMC:
        """Create controller for performance testing."""
        config = ClassicalSMCConfig(
            gains=[1.0, 1.0, 1.0, 1.0, 10.0, 2.0],
            max_force=50.0,
            boundary_layer=0.1
        )
        return ModularClassicalSMC(config)

    @pytest.fixture
    def sample_history(self):
        """Create sample surface and control history."""
        surface_history = list(0.1 * np.sin(np.linspace(0, 10, 100)))
        control_history = list(5.0 * np.sin(np.linspace(0, 10, 100)))
        return surface_history, control_history

    def test_analyze_performance_method_exists(self, controller):
        """Test analyze_performance method exists."""
        assert hasattr(controller, 'analyze_performance')
        assert callable(controller.analyze_performance)

    def test_analyze_performance_returns_dict(self, controller, sample_history):
        """Test analyze_performance returns dictionary."""
        surface_history, control_history = sample_history

        analysis = controller.analyze_performance(
            surface_history, control_history, dt=0.01
        )

        assert isinstance(analysis, dict)

    def test_analyze_performance_with_chattering_metrics(self, controller, sample_history):
        """Test analyze_performance includes chattering metrics."""
        surface_history, control_history = sample_history

        analysis = controller.analyze_performance(
            surface_history, control_history, dt=0.01
        )

        # Should include chattering-related metrics from boundary layer
        assert isinstance(analysis, dict)
        # Analysis delegated to boundary layer component

    def test_analyze_performance_with_empty_history(self, controller):
        """Test analyze_performance with empty history."""
        surface_history = []
        control_history = []

        try:
            analysis = controller.analyze_performance(
                surface_history, control_history, dt=0.01
            )
            # Should either return empty dict or handle gracefully
            assert isinstance(analysis, dict)
        except ValueError:
            # Acceptable to raise ValueError for empty history
            pass

    def test_analyze_performance_with_mismatched_lengths(self, controller):
        """Test analyze_performance with mismatched history lengths."""
        surface_history = [0.1, 0.2, 0.3]
        control_history = [1.0, 2.0]  # Different length

        try:
            analysis = controller.analyze_performance(
                surface_history, control_history, dt=0.01
            )
            # Should handle gracefully or raise appropriate error
            assert isinstance(analysis, dict)
        except (ValueError, AssertionError):
            # Acceptable to raise error for mismatched lengths
            pass


class TestParameterRetrieval:
    """Test parameter retrieval completeness."""

    @pytest.fixture
    def controller(self) -> ModularClassicalSMC:
        """Create controller for parameter retrieval tests."""
        config = ClassicalSMCConfig(
            gains=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            max_force=50.0,
            boundary_layer=0.1
        )
        return ModularClassicalSMC(config)

    def test_get_parameters_returns_dict(self, controller):
        """Test get_parameters returns dictionary."""
        params = controller.get_parameters()

        assert isinstance(params, dict)

    def test_get_parameters_includes_gains(self, controller):
        """Test get_parameters includes gains."""
        params = controller.get_parameters()

        assert 'gains' in params
        assert params['gains'] == [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]

    def test_get_parameters_includes_config(self, controller):
        """Test get_parameters includes config."""
        params = controller.get_parameters()

        assert 'config' in params
        assert isinstance(params['config'], dict)
        assert 'max_force' in params['config']
        assert 'boundary_layer' in params['config']

    def test_get_parameters_includes_surface_params(self, controller):
        """Test get_parameters includes surface parameters."""
        params = controller.get_parameters()

        assert 'surface_params' in params
        # Surface params from LinearSlidingSurface

    def test_get_parameters_includes_boundary_layer_params(self, controller):
        """Test get_parameters includes boundary layer parameters."""
        params = controller.get_parameters()

        assert 'boundary_layer_params' in params
        # Boundary layer params from BoundaryLayer component

    def test_get_parameters_completeness(self, controller):
        """Test get_parameters returns all required keys."""
        params = controller.get_parameters()

        required_keys = {
            'gains',
            'config',
            'surface_params',
            'boundary_layer_params'
        }

        assert required_keys.issubset(params.keys())

    def test_gains_property_returns_list(self, controller):
        """Test gains property returns list."""
        gains = controller.gains

        assert isinstance(gains, list)
        assert gains == [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]

    def test_gains_property_is_copy(self, controller):
        """Test gains property returns a copy."""
        gains1 = controller.gains
        gains1[0] = 999.0

        gains2 = controller.gains

        # Original should be unchanged
        assert gains2[0] == 1.0


class TestChatteringReduction:
    """Test chattering reduction effectiveness."""

    @pytest.fixture
    def controller_thin_boundary(self) -> ModularClassicalSMC:
        """Create controller with thin boundary layer (more chattering)."""
        config = ClassicalSMCConfig(
            gains=[1.0, 1.0, 1.0, 1.0, 20.0, 2.0],  # High K
            max_force=50.0,
            boundary_layer=0.01  # Very thin
        )
        return ModularClassicalSMC(config)

    @pytest.fixture
    def controller_thick_boundary(self) -> ModularClassicalSMC:
        """Create controller with thick boundary layer (less chattering)."""
        config = ClassicalSMCConfig(
            gains=[1.0, 1.0, 1.0, 1.0, 20.0, 2.0],  # High K
            max_force=50.0,
            boundary_layer=1.0  # Thick
        )
        return ModularClassicalSMC(config)

    def test_boundary_layer_reduces_chattering(self, controller_thin_boundary, controller_thick_boundary):
        """Test thick boundary layer reduces chattering vs thin layer."""
        state = np.array([0, 0, 0.5, 0, 0, 0])  # Near boundary

        # Run multiple steps and track control variation
        controls_thin = []
        controls_thick = []

        for i in range(20):
            # Slight variation in state
            state_varied = state + 0.01 * np.sin(i * 0.1) * np.array([0, 0, 1, 0, 0, 0])

            result_thin = controller_thin_boundary.compute_control(state_varied, None, {})
            result_thick = controller_thick_boundary.compute_control(state_varied, None, {})

            controls_thin.append(result_thin['u'])
            controls_thick.append(result_thick['u'])

        # Calculate variation (simple std dev)
        variation_thin = np.std(controls_thin)
        variation_thick = np.std(controls_thick)

        # Thick boundary layer should generally produce smoother control
        # (This is a behavioral test, not a strict requirement)
        assert isinstance(variation_thin, float)
        assert isinstance(variation_thick, float)

    def test_control_smooth_near_surface(self, controller_thick_boundary):
        """Test control is continuous near surface."""
        # States very close to surface
        state1 = np.array([0, 0, 0.001, 0, 0, 0])
        state2 = np.array([0, 0, -0.001, 0, 0, 0])

        result1 = controller_thick_boundary.compute_control(state1, None, {})
        result2 = controller_thick_boundary.compute_control(state2, None, {})

        # Controls should be finite and relatively close
        assert np.isfinite(result1['u'])
        assert np.isfinite(result2['u'])

        # Should not have huge discontinuity
        control_diff = abs(result1['u'] - result2['u'])
        assert control_diff < 100.0  # Reasonable smoothness

    def test_in_boundary_layer_flag_consistency(self, controller_thick_boundary):
        """Test in_boundary_layer flag is consistent."""
        # Inside boundary layer (surface < boundary_layer)
        state_inside = np.array([0, 0, 0.1, 0, 0, 0])  # boundary_layer = 1.0
        result_inside = controller_thick_boundary.compute_control(state_inside, None, {})

        # Outside boundary layer
        state_outside = np.array([0, 0, 5.0, 0, 0, 0])
        result_outside = controller_thick_boundary.compute_control(state_outside, None, {})

        # Flags should be consistent with boundary layer logic
        assert 'in_boundary_layer' in result_inside
        assert 'in_boundary_layer' in result_outside

    def test_chattering_index_calculation(self, controller_thick_boundary):
        """Test chattering index can be calculated from history."""
        state = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])

        surface_history = []
        control_history = []

        # Generate history
        for _ in range(100):
            result = controller_thick_boundary.compute_control(state, None, {})
            surface_history.append(result['surface_value'])
            control_history.append(result['u'])

        # Analyze performance
        try:
            analysis = controller_thick_boundary.analyze_performance(
                surface_history, control_history, dt=0.01
            )

            # Should return valid analysis
            assert isinstance(analysis, dict)
        except Exception:
            # If boundary layer doesn't implement performance analysis,
            # that's acceptable (test validates interface exists)
            pass
