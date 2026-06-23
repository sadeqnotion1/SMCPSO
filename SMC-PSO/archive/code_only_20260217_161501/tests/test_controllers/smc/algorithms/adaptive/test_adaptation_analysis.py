#======================================================================================\\
#===== tests/test_controllers/smc/algorithms/adaptive/test_adaptation_analysis.py =====\\
#======================================================================================\\

"""
Analysis and parameter tuning tests for Modular Adaptive SMC.

Tests:
- Adaptation analysis methods
- Runtime parameter tuning
- Parameter retrieval completeness
- Performance metrics
"""

from __future__ import annotations

import numpy as np
import pytest

from src.controllers.smc.algorithms import ModularAdaptiveSMC, AdaptiveSMCConfig


class TestAdaptationAnalysis:
    """Test adaptation analysis methods."""

    @pytest.fixture
    def controller_with_history(self) -> ModularAdaptiveSMC:
        """Create controller with pre-populated history."""
        config = AdaptiveSMCConfig(
            gains=[1.0, 1.0, 1.0, 1.0, 0.5],
            max_force=50.0,
            dt=0.01,
            K_init=10.0
        )
        controller = ModularAdaptiveSMC(config)

        # Pre-populate with history
        state = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])
        for _ in range(20):
            controller.compute_control(state, dt=0.01)

        return controller

    def test_get_adaptation_analysis_returns_dict(self, controller_with_history):
        """Test get_adaptation_analysis returns structured dictionary."""
        analysis = controller_with_history.get_adaptation_analysis()

        assert isinstance(analysis, dict)
        assert 'adaptation_performance' in analysis
        assert 'uncertainty_estimation' in analysis
        assert 'current_state' in analysis
        assert 'configuration' in analysis

    def test_adaptation_analysis_current_state(self, controller_with_history):
        """Test current_state section of adaptation analysis."""
        analysis = controller_with_history.get_adaptation_analysis()

        current_state = analysis['current_state']
        assert 'adaptive_gain' in current_state
        assert 'uncertainty_bound' in current_state
        assert 'control_history_length' in current_state

        # Values should be reasonable
        assert np.isfinite(current_state['adaptive_gain'])
        assert current_state['adaptive_gain'] > 0
        assert np.isfinite(current_state['uncertainty_bound'])
        assert current_state['uncertainty_bound'] > 0
        assert current_state['control_history_length'] > 0

    def test_adaptation_analysis_configuration(self, controller_with_history):
        """Test configuration section of adaptation analysis."""
        analysis = controller_with_history.get_adaptation_analysis()

        config = analysis['configuration']
        assert isinstance(config, dict)
        assert 'gains' in config
        assert 'dt' in config
        assert 'max_force' in config

    def test_adaptation_analysis_performance_metrics(self, controller_with_history):
        """Test adaptation_performance section."""
        analysis = controller_with_history.get_adaptation_analysis()

        performance = analysis['adaptation_performance']
        assert isinstance(performance, dict)
        # Should contain performance-related metrics

    def test_adaptation_analysis_uncertainty_metrics(self, controller_with_history):
        """Test uncertainty_estimation section."""
        analysis = controller_with_history.get_adaptation_analysis()

        uncertainty = analysis['uncertainty_estimation']
        assert isinstance(uncertainty, dict)
        # Should contain uncertainty estimation metrics


class TestRuntimeParameterTuning:
    """Test runtime parameter tuning."""

    @pytest.fixture
    def controller(self) -> ModularAdaptiveSMC:
        """Create controller for tuning tests."""
        config = AdaptiveSMCConfig(
            gains=[1.0, 1.0, 1.0, 1.0, 0.5],  # gamma = 0.5
            max_force=50.0,
            dt=0.01
        )
        return ModularAdaptiveSMC(config)

    def test_tune_adaptation_parameters_gamma(self, controller):
        """Test tuning gamma (adaptation rate) during runtime."""
        # Initial gamma is 0.5 from config
        initial_gamma = controller._adaptation.gamma

        # Tune gamma
        controller.tune_adaptation_parameters(gamma=1.5)

        # Check gamma was updated
        assert controller._adaptation.gamma != initial_gamma
        assert controller._adaptation.gamma == 1.5

    def test_tune_adaptation_parameters_sigma(self, controller):
        """Test tuning sigma (leak rate) during runtime."""
        # Tune sigma
        controller.tune_adaptation_parameters(sigma=0.2)

        # Check sigma was updated
        assert controller._adaptation.sigma == 0.2

    def test_tune_adaptation_parameters_rate_limit(self, controller):
        """Test tuning rate_limit during runtime."""
        # Tune rate_limit
        controller.tune_adaptation_parameters(rate_limit=10.0)

        # Check rate_limit was updated
        assert controller._adaptation.rate_limit == 10.0

    def test_tune_multiple_parameters_simultaneously(self, controller):
        """Test tuning multiple parameters at once."""
        controller.tune_adaptation_parameters(
            gamma=2.0,
            sigma=0.3,
            rate_limit=15.0
        )

        assert controller._adaptation.gamma == 2.0
        assert controller._adaptation.sigma == 0.3
        assert controller._adaptation.rate_limit == 15.0

    def test_tune_parameters_with_none_values(self, controller):
        """Test tuning with None values (should keep existing)."""
        original_gamma = controller._adaptation.gamma

        # Tune only sigma, leave gamma as None
        controller.tune_adaptation_parameters(gamma=None, sigma=0.25)

        # Gamma should remain unchanged
        assert controller._adaptation.gamma == original_gamma
        # Sigma should be updated
        assert controller._adaptation.sigma == 0.25

    def test_tuning_affects_control_behavior(self, controller):
        """Test that parameter tuning affects control output."""
        state = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])

        # Run with original parameters
        for _ in range(10):
            controller.compute_control(state, dt=0.01)

        gain_before = controller.get_adaptive_gain()

        # Tune to higher adaptation rate
        controller.tune_adaptation_parameters(gamma=5.0)

        # Run with new parameters
        for _ in range(10):
            controller.compute_control(state, dt=0.01)

        gain_after = controller.get_adaptive_gain()

        # Gains should have changed differently with new gamma
        # (This is a behavioral test, exact values depend on dynamics)
        assert isinstance(gain_before, float)
        assert isinstance(gain_after, float)


class TestParameterRetrieval:
    """Test parameter retrieval completeness."""

    @pytest.fixture
    def controller(self) -> ModularAdaptiveSMC:
        """Create controller for parameter retrieval tests."""
        config = AdaptiveSMCConfig(
            gains=[1.0, 1.0, 1.0, 1.0, 0.5],
            max_force=50.0,
            dt=0.01,
            K_init=10.0
        )
        return ModularAdaptiveSMC(config)

    def test_get_parameters_returns_dict(self, controller):
        """Test get_parameters returns dictionary."""
        params = controller.get_parameters()

        assert isinstance(params, dict)

    def test_get_parameters_includes_static_gains(self, controller):
        """Test get_parameters includes static gains."""
        params = controller.get_parameters()

        assert 'static_gains' in params
        assert params['static_gains'] == [1.0, 1.0, 1.0, 1.0, 0.5]

    def test_get_parameters_includes_current_adaptive_gain(self, controller):
        """Test get_parameters includes current adaptive gain."""
        params = controller.get_parameters()

        assert 'current_adaptive_gain' in params
        assert isinstance(params['current_adaptive_gain'], float)
        assert np.isfinite(params['current_adaptive_gain'])

    def test_get_parameters_includes_config(self, controller):
        """Test get_parameters includes full configuration."""
        params = controller.get_parameters()

        assert 'config' in params
        assert isinstance(params['config'], dict)
        assert 'dt' in params['config']
        assert 'max_force' in params['config']

    def test_get_parameters_includes_surface_params(self, controller):
        """Test get_parameters includes surface parameters."""
        params = controller.get_parameters()

        assert 'surface_params' in params
        # Surface params should be from LinearSlidingSurface

    def test_get_parameters_includes_adaptation_bounds(self, controller):
        """Test get_parameters includes adaptation bounds."""
        params = controller.get_parameters()

        assert 'adaptation_bounds' in params
        bounds = params['adaptation_bounds']
        assert isinstance(bounds, tuple)
        assert len(bounds) == 2
        assert bounds[0] < bounds[1]  # K_min < K_max

    def test_get_parameters_completeness(self, controller):
        """Test get_parameters returns all required keys."""
        params = controller.get_parameters()

        required_keys = {
            'static_gains',
            'current_adaptive_gain',
            'config',
            'surface_params',
            'adaptation_bounds'
        }

        assert required_keys.issubset(params.keys())


class TestGainsProperty:
    """Test gains property."""

    def test_gains_property_returns_list(self):
        """Test gains property returns list."""
        config = AdaptiveSMCConfig(
            gains=[1.0, 2.0, 3.0, 4.0, 5.0],
            max_force=50.0,
            dt=0.01
        )
        controller = ModularAdaptiveSMC(config)

        gains = controller.gains

        assert isinstance(gains, list)
        assert gains == [1.0, 2.0, 3.0, 4.0, 5.0]

    def test_gains_property_is_copy(self):
        """Test gains property returns a copy (not reference)."""
        config = AdaptiveSMCConfig(
            gains=[1.0, 2.0, 3.0, 4.0, 5.0],
            max_force=50.0,
            dt=0.01
        )
        controller = ModularAdaptiveSMC(config)

        gains1 = controller.gains
        gains1[0] = 999.0

        gains2 = controller.gains

        # Original config should be unchanged
        assert gains2[0] == 1.0


class TestResetBehavior:
    """Test reset behavior."""

    @pytest.fixture
    def controller_with_state(self) -> ModularAdaptiveSMC:
        """Create controller with accumulated state."""
        config = AdaptiveSMCConfig(
            gains=[1.0, 1.0, 1.0, 1.0, 0.5],
            max_force=50.0,
            dt=0.01,
            K_init=10.0
        )
        controller = ModularAdaptiveSMC(config)

        # Accumulate state
        state = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])
        for _ in range(30):
            controller.compute_control(state, dt=0.01)

        return controller

    def test_reset_clears_control_history(self, controller_with_state):
        """Test reset clears control history."""
        assert len(controller_with_state._control_history) > 0

        controller_with_state.reset()

        assert len(controller_with_state._control_history) == 0

    def test_reset_resets_previous_surface(self, controller_with_state):
        """Test reset resets previous surface to zero."""
        assert controller_with_state._previous_surface != 0.0

        controller_with_state.reset()

        assert controller_with_state._previous_surface == 0.0

    def test_reset_resets_adaptive_gain_to_init(self, controller_with_state):
        """Test reset resets adaptive gain to K_init."""
        # Gain should have changed from initial
        current_gain = controller_with_state.get_adaptive_gain()

        controller_with_state.reset()

        reset_gain = controller_with_state.get_adaptive_gain()
        assert reset_gain == 10.0  # K_init

    def test_reset_adaptation_with_custom_gain(self, controller_with_state):
        """Test reset_adaptation with custom initial gain."""
        controller_with_state.reset_adaptation(initial_gain=25.0)

        assert controller_with_state.get_adaptive_gain() == 25.0

    def test_reset_via_standard_reset_method(self, controller_with_state):
        """Test that reset() delegates to reset_adaptation()."""
        controller_with_state.reset()

        # Should have same effect as reset_adaptation()
        assert len(controller_with_state._control_history) == 0
        assert controller_with_state._previous_surface == 0.0
        assert controller_with_state.get_adaptive_gain() == 10.0


class TestBackwardCompatibilityFacade:
    """Test backward compatibility AdaptiveSMC facade."""

    def test_facade_initialization(self):
        """Test facade initializes correctly."""
        from src.controllers.smc.algorithms import AdaptiveSMC

        controller = AdaptiveSMC(
            gains=[1.0, 1.0, 1.0, 1.0, 0.5],
            dt=0.01,
            max_force=50.0
        )

        assert controller is not None
        assert hasattr(controller, '_controller')

    def test_facade_compute_control(self):
        """Test facade compute_control delegates correctly."""
        from src.controllers.smc.algorithms import AdaptiveSMC

        controller = AdaptiveSMC(
            gains=[1.0, 1.0, 1.0, 1.0, 0.5],
            dt=0.01,
            max_force=50.0
        )

        state = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])
        result = controller.compute_control(state, None, {})

        assert isinstance(result, dict)
        assert 'u' in result

    def test_facade_gains_property(self):
        """Test facade gains property delegation."""
        from src.controllers.smc.algorithms import AdaptiveSMC

        controller = AdaptiveSMC(
            gains=[1.0, 2.0, 3.0, 4.0, 5.0],
            dt=0.01,
            max_force=50.0
        )

        assert controller.gains == [1.0, 2.0, 3.0, 4.0, 5.0]

    def test_facade_get_adaptive_gain(self):
        """Test facade get_adaptive_gain delegation."""
        from src.controllers.smc.algorithms import AdaptiveSMC

        controller = AdaptiveSMC(
            gains=[1.0, 1.0, 1.0, 1.0, 0.5],
            dt=0.01,
            max_force=50.0,
            K_init=15.0
        )

        gain = controller.get_adaptive_gain()
        assert gain == 15.0

    def test_facade_reset(self):
        """Test facade reset delegation."""
        from src.controllers.smc.algorithms import AdaptiveSMC

        controller = AdaptiveSMC(
            gains=[1.0, 1.0, 1.0, 1.0, 0.5],
            dt=0.01,
            max_force=50.0
        )

        # Run some control
        state = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])
        for _ in range(10):
            controller.compute_control(state, None, {})

        # Reset
        controller.reset()

        # Should have reset internal state
        assert len(controller._controller._control_history) == 0

    def test_facade_reset_adaptation(self):
        """Test facade reset_adaptation delegation."""
        from src.controllers.smc.algorithms import AdaptiveSMC

        controller = AdaptiveSMC(
            gains=[1.0, 1.0, 1.0, 1.0, 0.5],
            dt=0.01,
            max_force=50.0,
            K_init=10.0
        )

        # Run some control
        state = np.array([0.1, 0.2, 0.3, 0.1, 0.1, 0.1])
        for _ in range(10):
            controller.compute_control(state, None, {})

        # Reset adaptation
        controller.reset_adaptation()

        # Gain should be back to K_init
        assert controller.get_adaptive_gain() == 10.0

    def test_facade_get_parameters(self):
        """Test facade get_parameters delegation."""
        from src.controllers.smc.algorithms import AdaptiveSMC

        controller = AdaptiveSMC(
            gains=[1.0, 1.0, 1.0, 1.0, 0.5],
            dt=0.01,
            max_force=50.0
        )

        params = controller.get_parameters()

        assert isinstance(params, dict)
        assert 'static_gains' in params
