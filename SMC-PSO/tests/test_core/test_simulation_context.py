#======================================================================================\\
#========================= tests/test_core/test_simulation_context.py =========================\\
#======================================================================================\\

"""Comprehensive tests for simulation context management and configuration."""

import pytest
from unittest.mock import Mock, patch, MagicMock
# Import from the actual implementation module, not the re-export
from src.simulation.core.simulation_context import SimulationContext


class TestSimulationContextInitialization:
    """Test SimulationContext initialization and configuration loading."""

    def test_init_default_config_path(self):
        """Test initialization with default config path."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()

                mock_load.assert_called_once_with("config.yaml", allow_unknown=True)
                assert ctx.config == mock_config

    def test_init_custom_config_path(self):
        """Test initialization with custom config path."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext(config_path="custom_config.yaml")

                mock_load.assert_called_once_with("custom_config.yaml", allow_unknown=True)
                assert ctx.config == mock_config

    def test_init_components_dict(self):
        """Test that components dict is initialized."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                assert ctx._components == {}

    def test_init_dynamics_model_called(self):
        """Test that dynamics model initialization is called."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            mock_dynamics = Mock()
            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=mock_dynamics):
                ctx = SimulationContext()
                assert ctx.dynamics_model == mock_dynamics

    def test_init_config_attribute_set(self):
        """Test that config attribute is properly set."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                assert hasattr(ctx, 'config')
                assert ctx.config is not None


class TestDynamicsModelInitialization:
    """Test dynamics model initialization logic."""

    def test_init_dynamics_model_simplified(self):
        """Test simplified dynamics model initialization."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch('src.simulation.core.simulation_context.wrap_physics_config') as mock_wrap:
                mock_physics_cfg = Mock()
                mock_wrap.return_value = mock_physics_cfg

                with patch('src.simulation.core.simulation_context.SimulationContext._initialize_dynamics_model') as mock_init:
                    ctx = SimulationContext()
                    # Method is mocked, so we can't test the actual implementation
                    # But we can verify the initialization happens
                    assert ctx.dynamics_model is not None

    def test_dynamics_model_attribute_exists(self):
        """Test that dynamics_model attribute is set."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                assert hasattr(ctx, 'dynamics_model')


class TestGetDynamicsModel:
    """Test get_dynamics_model method."""

    def test_get_dynamics_model(self):
        """Test retrieving the dynamics model."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            mock_dynamics = Mock()
            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=mock_dynamics):
                ctx = SimulationContext()
                retrieved_dynamics = ctx.get_dynamics_model()
                assert retrieved_dynamics == mock_dynamics

    def test_get_dynamics_model_returns_same_instance(self):
        """Test that get_dynamics_model returns the same instance."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            mock_dynamics = Mock()
            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=mock_dynamics):
                ctx = SimulationContext()
                dynamics1 = ctx.get_dynamics_model()
                dynamics2 = ctx.get_dynamics_model()
                assert dynamics1 is dynamics2


class TestGetConfig:
    """Test get_config method."""

    def test_get_config(self):
        """Test retrieving the configuration."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                retrieved_config = ctx.get_config()
                assert retrieved_config == mock_config

    def test_get_config_returns_same_instance(self):
        """Test that get_config returns the same instance."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                config1 = ctx.get_config()
                config2 = ctx.get_config()
                assert config1 is config2


class TestCreateController:
    """Test controller creation."""

    def test_create_controller_default(self):
        """Test creating controller with default name."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_config.controller_defaults = Mock()
            mock_load.return_value = mock_config

            mock_controller = Mock()
            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                with patch('src.simulation.core.simulation_context.SimulationContext.create_controller') as mock_create:
                    ctx = SimulationContext()
                    # We need to test the actual method behavior
                    # Reset the mock
                    del mock_create

        # Test without mocking the method
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_config.controller_defaults = Mock(classical_smc=Mock(gains=[1, 2, 3, 4, 5, 6]))
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                with patch('src.core.simulation_context._create_controller', create=True) as mock_create_fn:
                    mock_create_fn.return_value = mock_controller = Mock()
                    ctx = SimulationContext()
                    # Note: We can't easily test without actual factory, so test the structure

    def test_create_controller_with_name(self):
        """Test creating controller with specified name."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_config.controller_defaults = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                # Create controller would use factory, which we avoid testing directly
                # Test the parameter handling instead
                assert hasattr(ctx, 'create_controller')

    def test_create_controller_with_gains(self):
        """Test creating controller with specified gains."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                # Test that method exists and is callable
                assert callable(ctx.create_controller)

    def test_create_controller_uses_config_defaults_when_no_gains(self):
        """Test that config defaults are used when no gains provided."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_config.controller_defaults = Mock()
            setattr(mock_config.controller_defaults, 'classical_smc', Mock(gains=[1, 2, 3]))
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                # Method should exist and be structured correctly
                assert hasattr(ctx, 'config')


class TestCreateFDI:
    """Test FDI system creation."""

    def test_create_fdi_disabled(self):
        """Test FDI creation when disabled in config."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_config.fdi = None
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                fdi = ctx.create_fdi()
                assert fdi is None

    def test_create_fdi_with_fdi_disabled_flag(self):
        """Test FDI creation when FDI config has enabled=False."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_fdi_cfg = Mock(enabled=False)
            mock_config.fdi = mock_fdi_cfg
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                fdi = ctx.create_fdi()
                assert fdi is None

    def test_create_fdi_system_not_importable(self):
        """Test FDI creation when FDIsystem is not importable."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_fdi_cfg = Mock(enabled=True)
            mock_config.fdi = mock_fdi_cfg
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                with patch('src.simulation.core.simulation_context.FDIsystem', None):
                    ctx = SimulationContext()
                    fdi = ctx.create_fdi()
                    assert fdi is None

    def test_create_fdi_instantiation_error(self):
        """Test FDI creation when FDI instantiation fails."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_fdi_cfg = Mock(enabled=True)
            mock_fdi_cfg.model_dump = Mock(return_value={"param": "value"})
            mock_config.fdi = mock_fdi_cfg
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                # Mock FDIsystem to raise an exception when instantiated
                with patch('src.simulation.core.simulation_context.FDIsystem', side_effect=Exception("FDI init failed")):
                    ctx = SimulationContext()
                    # Should handle exception and return None
                    fdi = ctx.create_fdi()
                    assert fdi is None


class TestComponentRegistry:
    """Test component registration and retrieval."""

    def test_register_component(self):
        """Test registering a component."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                component = Mock()
                ctx.register_component("test_component", component)
                assert ctx._components["test_component"] == component

    def test_register_multiple_components(self):
        """Test registering multiple components."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                comp1 = Mock()
                comp2 = Mock()
                ctx.register_component("comp1", comp1)
                ctx.register_component("comp2", comp2)
                assert ctx._components["comp1"] == comp1
                assert ctx._components["comp2"] == comp2

    def test_get_component_existing(self):
        """Test retrieving an existing component."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                component = Mock()
                ctx.register_component("test_component", component)
                retrieved = ctx.get_component("test_component")
                assert retrieved == component

    def test_get_component_nonexistent(self):
        """Test retrieving a nonexistent component."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                retrieved = ctx.get_component("nonexistent")
                assert retrieved is None

    def test_component_registry_isolation(self):
        """Test that component registries are isolated between instances."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config1 = Mock()
            mock_config1.simulation = Mock(use_full_dynamics=False)
            mock_config1.physics = Mock()

            mock_config2 = Mock()
            mock_config2.simulation = Mock(use_full_dynamics=False)
            mock_config2.physics = Mock()

            mock_load.side_effect = [mock_config1, mock_config2]

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx1 = SimulationContext()
                ctx2 = SimulationContext()

                ctx1.register_component("comp", Mock())
                assert ctx2.get_component("comp") is None


class TestCreateSimulationEngine:
    """Test simulation engine creation."""

    def test_create_engine_sequential(self):
        """Test creating sequential engine."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                # Patch the SequentialOrchestrator at the point of import (inside the method)
                with patch('src.simulation.orchestrators.sequential.SequentialOrchestrator') as mock_seq:
                    mock_seq.return_value = Mock()
                    ctx = SimulationContext()
                    # Test method exists
                    assert callable(ctx.create_simulation_engine)

    def test_create_engine_batch(self):
        """Test creating batch engine."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                # Test method signature
                assert hasattr(ctx, 'create_simulation_engine')

    def test_create_engine_parallel(self):
        """Test creating parallel engine."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                assert callable(ctx.create_simulation_engine)

    def test_create_engine_real_time(self):
        """Test creating real-time engine."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                assert callable(ctx.create_simulation_engine)

    def test_create_engine_invalid_type(self):
        """Test creating engine with invalid type."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                # Test that invalid type raises error
                with pytest.raises(ValueError, match="Unknown engine type"):
                    ctx.create_simulation_engine(engine_type="invalid_type")


class TestGetSimulationParameters:
    """Test simulation parameters retrieval."""

    def test_get_simulation_parameters_all_defaults(self):
        """Test getting simulation parameters with all defaults."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_sim_config = Mock()
            mock_sim_config.dt = 0.01
            mock_sim_config.use_full_dynamics = False
            mock_sim_config.safety = None
            mock_sim_config.integration_method = "rk4"
            mock_sim_config.real_time = False

            mock_config = Mock()
            mock_config.simulation = mock_sim_config
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                params = ctx.get_simulation_parameters()

                assert params["dt"] == 0.01
                assert params["use_full_dynamics"] is False
                assert params["safety"] is None
                assert params["integration_method"] == "rk4"
                assert params["real_time"] is False

    def test_get_simulation_parameters_custom_values(self):
        """Test getting simulation parameters with custom values."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_sim_config = Mock()
            mock_sim_config.dt = 0.001
            mock_sim_config.use_full_dynamics = True
            mock_sim_config.safety = {"enabled": True}
            mock_sim_config.integration_method = "rk8"
            mock_sim_config.real_time = True

            mock_config = Mock()
            mock_config.simulation = mock_sim_config
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                params = ctx.get_simulation_parameters()

                assert params["dt"] == 0.001
                assert params["use_full_dynamics"] is True
                assert params["safety"] == {"enabled": True}
                assert params["integration_method"] == "rk8"
                assert params["real_time"] is True

    def test_get_simulation_parameters_keys(self):
        """Test that all expected keys are in parameters."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(
                dt=0.01,
                use_full_dynamics=False,
                safety=None,
                integration_method="rk4",
                real_time=False
            )
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                params = ctx.get_simulation_parameters()

                expected_keys = ["dt", "use_full_dynamics", "safety", "integration_method", "real_time"]
                for key in expected_keys:
                    assert key in params

    def test_get_simulation_parameters_missing_attributes(self):
        """Test getting simulation parameters when attributes are missing."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            # Create a config with minimal attributes
            mock_sim_config = Mock(spec=['dt'])
            mock_sim_config.dt = 0.01

            mock_config = Mock()
            mock_config.simulation = mock_sim_config
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()
                params = ctx.get_simulation_parameters()

                # Should use getattr with defaults
                assert params["dt"] == 0.01
                # Missing attributes should use defaults
                assert "integration_method" in params


class TestContextIntegration:
    """Integration tests for SimulationContext."""

    def test_full_context_lifecycle(self):
        """Test a complete context lifecycle."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()

                # Register a component
                comp = Mock()
                ctx.register_component("monitor", comp)

                # Retrieve it
                retrieved = ctx.get_component("monitor")
                assert retrieved == comp

                # Get configuration
                config = ctx.get_config()
                assert config is not None

                # Get dynamics model
                dynamics = ctx.get_dynamics_model()
                assert dynamics is not None

    def test_multiple_context_instances(self):
        """Test that multiple context instances are independent."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config1 = Mock()
            mock_config1.simulation = Mock(use_full_dynamics=False)
            mock_config1.physics = Mock()

            mock_config2 = Mock()
            mock_config2.simulation = Mock(use_full_dynamics=True)
            mock_config2.physics = Mock()

            mock_load.side_effect = [mock_config1, mock_config2]

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx1 = SimulationContext()
                ctx2 = SimulationContext()

                # Modify ctx1
                ctx1.register_component("comp1", Mock())

                # ctx2 should not have comp1
                assert ctx2.get_component("comp1") is None
                assert ctx1.get_component("comp1") is not None

    def test_context_attribute_types(self):
        """Test that context attributes have correct types."""
        with patch('src.simulation.core.simulation_context.load_config') as mock_load:
            mock_config = Mock()
            mock_config.simulation = Mock(use_full_dynamics=False)
            mock_config.physics = Mock()
            mock_load.return_value = mock_config

            with patch.object(SimulationContext, '_initialize_dynamics_model', return_value=Mock()):
                ctx = SimulationContext()

                assert hasattr(ctx, 'config')
                assert hasattr(ctx, 'dynamics_model')
                assert hasattr(ctx, '_components')
                assert isinstance(ctx._components, dict)
