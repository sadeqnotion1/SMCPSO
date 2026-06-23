"""
Unit tests for simulation interfaces (src/simulation/core/interfaces.py).

Tests cover:
- ABC instantiation prevention
- Abstract method enforcement
- Concrete implementation validation
- Property requirements
"""

import numpy as np
import pytest
from abc import ABC

from src.simulation.core.interfaces import (
    SimulationEngine,
    Integrator,
    Orchestrator,
    SimulationStrategy,
    SafetyGuard,
    ResultContainer,
    DataLogger,
    PerformanceMonitor
)


# ======================================================================================
# ABC Instantiation Tests
# ======================================================================================

class TestAbstractBaseClasses:
    """Test that ABCs cannot be instantiated directly."""

    def test_simulation_engine_cannot_instantiate(self):
        """Should raise TypeError when instantiating SimulationEngine."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            SimulationEngine()

    def test_integrator_cannot_instantiate(self):
        """Should raise TypeError when instantiating Integrator."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            Integrator()

    def test_orchestrator_cannot_instantiate(self):
        """Should raise TypeError when instantiating Orchestrator."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            Orchestrator()

    def test_simulation_strategy_cannot_instantiate(self):
        """Should raise TypeError when instantiating SimulationStrategy."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            SimulationStrategy()

    def test_safety_guard_cannot_instantiate(self):
        """Should raise TypeError when instantiating SafetyGuard."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            SafetyGuard()

    def test_result_container_cannot_instantiate(self):
        """Should raise TypeError when instantiating ResultContainer."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            ResultContainer()

    def test_data_logger_cannot_instantiate(self):
        """Should raise TypeError when instantiating DataLogger."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            DataLogger()

    def test_performance_monitor_cannot_instantiate(self):
        """Should raise TypeError when instantiating PerformanceMonitor."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            PerformanceMonitor()


# ======================================================================================
# SimulationEngine Tests
# ======================================================================================

class TestSimulationEngine:
    """Test SimulationEngine interface."""

    def test_concrete_implementation_works(self):
        """Should allow concrete implementation."""
        class ConcreteEngine(SimulationEngine):
            def step(self, state, control, dt, **kwargs):
                return state + control * dt

        engine = ConcreteEngine()
        state = np.array([1.0, 2.0])
        control = np.array([0.5, 0.5])
        result = engine.step(state, control, 0.1)

        assert isinstance(result, np.ndarray)
        assert result.shape == state.shape

    def test_missing_step_method_fails(self):
        """Should fail if step() not implemented."""
        class IncompleteEngine(SimulationEngine):
            pass

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteEngine()


# ======================================================================================
# Integrator Tests
# ======================================================================================

class TestIntegrator:
    """Test Integrator interface."""

    def test_concrete_implementation_works(self):
        """Should allow concrete implementation."""
        class ConcreteIntegrator(Integrator):
            def integrate(self, dynamics_fn, state, control, dt, **kwargs):
                dx_dt = dynamics_fn(state, control, 0.0)
                return state + dx_dt * dt

            @property
            def order(self):
                return 1

            @property
            def adaptive(self):
                return False

        integrator = ConcreteIntegrator()
        dynamics = lambda x, u, t: np.array([1.0, 2.0])
        result = integrator.integrate(dynamics, np.zeros(2), np.zeros(2), 0.1)

        assert isinstance(result, np.ndarray)
        assert integrator.order == 1
        assert integrator.adaptive == False

    def test_missing_integrate_method_fails(self):
        """Should fail if integrate() not implemented."""
        class IncompleteIntegrator(Integrator):
            @property
            def order(self):
                return 1

            @property
            def adaptive(self):
                return False

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteIntegrator()

    def test_missing_order_property_fails(self):
        """Should fail if order property not implemented."""
        class IncompleteIntegrator(Integrator):
            def integrate(self, dynamics_fn, state, control, dt, **kwargs):
                return state

            @property
            def adaptive(self):
                return False

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteIntegrator()


# ======================================================================================
# Orchestrator Tests
# ======================================================================================

class TestOrchestrator:
    """Test Orchestrator interface."""

    def test_concrete_implementation_works(self):
        """Should allow concrete implementation."""
        class MockResultContainer(ResultContainer):
            def __init__(self):
                self.states = []
            def add_trajectory(self, states, times, **metadata):
                self.states.append(states)
            def get_states(self):
                return np.array(self.states) if self.states else np.array([])
            def get_times(self):
                return np.array([])
            def export(self, format_type, filepath):
                pass

        class ConcreteOrchestrator(Orchestrator):
            def execute(self, initial_state, control_inputs, dt, horizon, **kwargs):
                return MockResultContainer()

        orchestrator = ConcreteOrchestrator()
        result = orchestrator.execute(np.zeros(6), np.zeros(10), 0.01, 100)

        assert isinstance(result, ResultContainer)


# ======================================================================================
# SimulationStrategy Tests
# ======================================================================================

class TestSimulationStrategy:
    """Test SimulationStrategy interface."""

    def test_concrete_implementation_works(self):
        """Should allow concrete implementation."""
        class ConcreteStrategy(SimulationStrategy):
            def analyze(self, simulation_fn, parameters, **kwargs):
                return {"result": "analyzed"}

        strategy = ConcreteStrategy()
        result = strategy.analyze(lambda x: x, {})

        assert isinstance(result, dict)
        assert "result" in result


# ======================================================================================
# SafetyGuard Tests
# ======================================================================================

class TestSafetyGuard:
    """Test SafetyGuard interface."""

    def test_concrete_implementation_works(self):
        """Should allow concrete implementation."""
        class ConcreteGuard(SafetyGuard):
            def __init__(self):
                self.last_violation = None

            def check(self, state, step_idx, **kwargs):
                is_safe = np.all(np.abs(state) < 10.0)
                if not is_safe:
                    self.last_violation = "State exceeded bounds"
                return is_safe

            def get_violation_message(self):
                return self.last_violation or "No violation"

        guard = ConcreteGuard()
        assert guard.check(np.array([1.0, 2.0]), 0) == True
        assert guard.check(np.array([100.0, 2.0]), 1) == False
        assert "exceeded bounds" in guard.get_violation_message()


# ======================================================================================
# ResultContainer Tests
# ======================================================================================

class TestResultContainer:
    """Test ResultContainer interface."""

    def test_concrete_implementation_works(self):
        """Should allow concrete implementation."""
        class ConcreteContainer(ResultContainer):
            def __init__(self):
                self.states_list = []
                self.times_list = []

            def add_trajectory(self, states, times, **metadata):
                self.states_list.append(states)
                self.times_list.append(times)

            def get_states(self):
                return np.array(self.states_list) if self.states_list else np.array([])

            def get_times(self):
                return np.array(self.times_list) if self.times_list else np.array([])

            def export(self, format_type, filepath):
                pass

        container = ConcreteContainer()
        container.add_trajectory(np.zeros((10, 6)), np.linspace(0, 1, 10))

        states = container.get_states()
        assert isinstance(states, np.ndarray)


# ======================================================================================
# DataLogger Tests
# ======================================================================================

class TestDataLogger:
    """Test DataLogger interface."""

    def test_concrete_implementation_works(self):
        """Should allow concrete implementation."""
        class ConcreteLogger(DataLogger):
            def __init__(self):
                self.logs = []

            def log_step(self, step_data):
                self.logs.append(step_data)

            def finalize(self):
                pass

        logger = ConcreteLogger()
        logger.log_step({"time": 0.0, "state": [1, 2, 3]})
        logger.finalize()

        assert len(logger.logs) == 1


# ======================================================================================
# PerformanceMonitor Tests
# ======================================================================================

class TestPerformanceMonitor:
    """Test PerformanceMonitor interface."""

    def test_concrete_implementation_works(self):
        """Should allow concrete implementation."""
        class ConcreteMonitor(PerformanceMonitor):
            def __init__(self):
                self.timings = {}

            def start_timing(self, operation):
                import time
                self.timings[operation] = {"start": time.time()}

            def end_timing(self, operation):
                import time
                if operation in self.timings:
                    elapsed = time.time() - self.timings[operation]["start"]
                    self.timings[operation]["elapsed"] = elapsed
                    return elapsed
                return 0.0

            def get_statistics(self):
                return {op: data.get("elapsed", 0.0) for op, data in self.timings.items()}

        monitor = ConcreteMonitor()
        monitor.start_timing("test_op")
        elapsed = monitor.end_timing("test_op")
        stats = monitor.get_statistics()

        assert elapsed >= 0.0
        assert "test_op" in stats


# ======================================================================================
# Interface Inheritance Tests
# ======================================================================================

class TestInterfaceInheritance:
    """Test that all interfaces are ABC subclasses."""

    def test_all_interfaces_inherit_from_abc(self):
        """All interfaces should inherit from ABC."""
        interfaces = [
            SimulationEngine,
            Integrator,
            Orchestrator,
            SimulationStrategy,
            SafetyGuard,
            ResultContainer,
            DataLogger,
            PerformanceMonitor
        ]

        for interface in interfaces:
            assert issubclass(interface, ABC), f"{interface.__name__} should inherit from ABC"
