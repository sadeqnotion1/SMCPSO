"""M4 Slice 2 - core interfaces are abstract and importable without unported deps."""
import numpy as np
import pytest

from src.simulation.core.interfaces import (
    SimulationEngine, Integrator, Orchestrator, SimulationStrategy,
    SafetyGuard, ResultContainer,
)


@pytest.mark.parametrize("cls", [
    SimulationEngine, Integrator, Orchestrator, SimulationStrategy,
    SafetyGuard, ResultContainer,
])
def test_abstract_cannot_instantiate(cls):
    with pytest.raises(TypeError):
        cls()


def test_concrete_engine_subclass_works():
    class Euler(SimulationEngine):
        def step(self, state, control, dt, **kwargs):
            return state + dt * control

    e = Euler()
    out = e.step(np.zeros(2), np.ones(2), 0.5)
    assert np.allclose(out, [0.5, 0.5])


def test_core_package_imports_without_unported_modules():
    # The whole point of the lazy-import fix: importing the core package must
    # NOT pull in orchestrators / integrators / safety / factory / utils.
    import importlib
    mod = importlib.import_module("src.simulation.core")
    for name in ("SimulationEngine", "SimulationContext", "StateSpaceUtilities",
                 "TimeManager"):
        assert hasattr(mod, name)
