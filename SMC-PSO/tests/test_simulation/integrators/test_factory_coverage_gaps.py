#======================================================================================\\
#======== tests/test_simulation/integrators/test_factory_coverage_gaps.py ============\\
#======================================================================================\\

"""
Coverage gap tests for Integrator Factory.
Target: Fill gaps from 94.34% to 95%+ coverage.
Focus: Exception handling in create_integrator (lines 87-89).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.simulation.integrators.factory import IntegratorFactory, create_integrator
from src.simulation.integrators.base import BaseIntegrator


class TestCreateIntegratorExceptionHandling:
    """Test exception handling in create_integrator method (lines 87-89)."""

    def test_integrator_constructor_type_error(self):
        """Test that TypeError in constructor is logged and re-raised."""
        # Create a mock integrator that requires specific arg types
        class TypeErrorIntegrator(BaseIntegrator):
            def __init__(self, required_int: int):
                self.value = required_int

            def step(self, state, control, dt):
                return state

        factory = IntegratorFactory()
        factory.register_integrator('type_error_test', TypeErrorIntegrator)

        try:
            # Mock logging.getLogger to verify error logging
            with patch('logging.getLogger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                # Attempt to create with wrong type - should raise TypeError
                with pytest.raises(TypeError):
                    factory.create_integrator('type_error_test', dt=0.01, required_int="not_an_int")

                # Verify logger.error was called (line 88)
                assert mock_logger.error.called
                error_call_args = str(mock_logger.error.call_args)
                assert 'type_error_test' in error_call_args.lower()

        finally:
            if 'type_error_test' in factory._integrator_registry:
                del factory._integrator_registry['type_error_test']

    def test_integrator_constructor_value_error(self):
        """Test that ValueError in constructor is logged and re-raised."""
        class ValueErrorIntegrator(BaseIntegrator):
            def __init__(self, param: int):
                if param < 0:
                    raise ValueError("Parameter must be non-negative")
                self.param = param

            def step(self, state, control, dt):
                return state

            @property
            def adaptive(self):
                return False

            @property
            def order(self):
                return 1

            def integrate(self, state, control, dt):
                return state

        factory = IntegratorFactory()
        factory.register_integrator('value_error_test', ValueErrorIntegrator)

        try:
            with patch('logging.getLogger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                # Should raise ValueError for negative param
                with pytest.raises(ValueError, match="must be non-negative"):
                    factory.create_integrator('value_error_test', dt=0.01, param=-5)

                # Verify error logging
                assert mock_logger.error.called

        finally:
            if 'value_error_test' in factory._integrator_registry:
                del factory._integrator_registry['value_error_test']

    def test_integrator_constructor_runtime_error(self):
        """Test that RuntimeError in constructor is logged and re-raised."""
        class RuntimeErrorIntegrator(BaseIntegrator):
            def __init__(self):
                raise RuntimeError("Constructor failed unexpectedly")

            def step(self, state, control, dt):
                return state

            @property
            def adaptive(self):
                return False

            @property
            def order(self):
                return 1

            def integrate(self, state, control, dt):
                return state

        factory = IntegratorFactory()
        factory.register_integrator('runtime_error_test', RuntimeErrorIntegrator)

        try:
            with patch('logging.getLogger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                with pytest.raises(RuntimeError, match="failed unexpectedly"):
                    factory.create_integrator('runtime_error_test', dt=0.01)

                # Verify error logging (line 88)
                assert mock_logger.error.called
                error_call_args = str(mock_logger.error.call_args)
                assert 'runtime_error_test' in error_call_args

        finally:
            if 'runtime_error_test' in factory._integrator_registry:
                del factory._integrator_registry['runtime_error_test']

    def test_integrator_constructor_missing_required_arg(self):
        """Test that missing required argument is logged and re-raised."""
        class RequiredArgIntegrator(BaseIntegrator):
            def __init__(self, required_param):
                self.param = required_param

            def step(self, state, control, dt):
                return state

        factory = IntegratorFactory()
        factory.register_integrator('required_arg_test', RequiredArgIntegrator)

        try:
            with patch('logging.getLogger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                # Should raise TypeError for missing required argument
                with pytest.raises(TypeError):
                    factory.create_integrator('required_arg_test', dt=0.01)

                # Verify error logging
                assert mock_logger.error.called

        finally:
            if 'required_arg_test' in factory._integrator_registry:
                del factory._integrator_registry['required_arg_test']

    def test_integrator_constructor_attribute_error(self):
        """Test that AttributeError in constructor is logged and re-raised."""
        class AttributeErrorIntegrator(BaseIntegrator):
            def __init__(self):
                # Try to access non-existent attribute
                self.value = self.nonexistent_attribute

            def step(self, state, control, dt):
                return state

            @property
            def adaptive(self):
                return False

            @property
            def order(self):
                return 1

            def integrate(self, state, control, dt):
                return state

        factory = IntegratorFactory()
        factory.register_integrator('attr_error_test', AttributeErrorIntegrator)

        try:
            with patch('logging.getLogger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                with pytest.raises(AttributeError):
                    factory.create_integrator('attr_error_test', dt=0.01)

                # Verify error logging
                assert mock_logger.error.called

        finally:
            if 'attr_error_test' in factory._integrator_registry:
                del factory._integrator_registry['attr_error_test']

    def test_integrator_constructor_key_error(self):
        """Test that KeyError in constructor is logged and re-raised."""
        class KeyErrorIntegrator(BaseIntegrator):
            def __init__(self, config: dict):
                # Try to access missing key
                self.value = config['missing_key']

            def step(self, state, control, dt):
                return state

            @property
            def adaptive(self):
                return False

            @property
            def order(self):
                return 1

            def integrate(self, state, control, dt):
                return state

        factory = IntegratorFactory()
        factory.register_integrator('key_error_test', KeyErrorIntegrator)

        try:
            with patch('logging.getLogger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                with pytest.raises(KeyError):
                    factory.create_integrator('key_error_test', dt=0.01, config={})

                # Verify error logging
                assert mock_logger.error.called

        finally:
            if 'key_error_test' in factory._integrator_registry:
                del factory._integrator_registry['key_error_test']
