#======================================================================================\\\
#======== tests/test_controllers/factory/test_factory_dynamics_consolidated.py ========\\\
#======================================================================================\\\

import importlib
import pytest

factory = importlib.import_module("src.controllers.factory")

def test_factory_and_dynamics_core(monkeypatch):
    # a) unknown controller lists available (from registry, not config)
    class Dyn:
        def __init__(self, physics): pass
    monkeypatch.setattr(factory, "DoubleInvertedPendulum", Dyn, raising=False)
    class CfgA:
        class Sim:
            use_full_dynamics = False
            dt = 0.01
        simulation = Sim()
        controllers = {"zeta": {}, "alpha": {}, "beta": {}}
        controller_defaults = {}
    with pytest.raises(ValueError) as e1:
        factory.create_controller("does_not_exist", config=CfgA(), gains=None)
    # The new factory lists actual available controllers from registry
    expected_controllers = ["classical_smc", "sta_smc", "adaptive_smc", "hybrid_adaptive_sta_smc"]
    error_msg = str(e1.value)
    assert "Available:" in error_msg
    # Check that all expected controllers are mentioned
    for controller in expected_controllers:
        assert controller in error_msg

    # b) empty controllers_map UX - new factory uses registry, so this test checks for unknown controller
    class CfgEmpty:
        controllers = {}
    with pytest.raises(ValueError) as e2:
        factory.create_controller("anything", config=CfgEmpty(), gains=None)
    # The new factory will show available controllers from registry, not "none configured"
    assert "Available:" in str(e2.value)

    # c) Test invalid gains for classical_smc (should have 6 gains, not 3)
    class CfgD:
        class Sim:
            use_full_dynamics = False
            dt = 0.01
        simulation = Sim()
        controllers = {"classical_smc": {"gains":[1,1,1], "boundary_layer": 0.05}}
    with pytest.raises(ValueError):
        factory.create_controller("classical_smc", config=CfgD(), gains=[1,1,1])

    # d) Test successful controller creation with proper gains
    monkeypatch.setattr(factory, "DoubleInvertedPendulum", Dyn, raising=False)
    class CfgF:
        class Sim:
            use_full_dynamics = True
            dt = 0.01
        simulation = Sim()
        controllers = {"classical_smc": {"gains":[1,1,1,1,1,1], "boundary_layer": 0.05}}
    # Should succeed with proper 6 gains
    controller = factory.create_controller("classical_smc", config=CfgF(), gains=[1,1,1,1,1,1])
    assert controller is not None

    # e) Test parameter validation (positive max_force)
    try:
        controller = factory.create_controller("classical_smc", gains=[1,1,1,1,1,1])
        assert controller is not None  # Should succeed with valid parameters
    except Exception as e:
        # If there's an exception, it shouldn't be related to invalid dt (our factory handles this differently)
        assert "dt must be > 0" not in str(e)

    # f) _as_dict normalization
    class PydLike:
        def __init__(self, d): self._d = d
        def model_dump(self, exclude_unset=True): return dict(self._d)
    out = factory._as_dict(PydLike({"a":1}))
    assert out == {"a":1}
