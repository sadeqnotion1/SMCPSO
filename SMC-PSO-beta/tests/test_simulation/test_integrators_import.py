"""M4 Slice 3 - the integrators package imports cleanly with no unported deps."""
import sys
import importlib


def test_package_exports():
    mod = importlib.import_module("src.simulation.integrators")
    for name in ("BaseIntegrator", "AdaptiveRungeKutta", "DormandPrince45",
                 "ForwardEuler", "BackwardEuler", "RungeKutta4", "RungeKutta2",
                 "ZeroOrderHold", "IntegratorFactory", "create_integrator",
                 "get_available_integrators"):
        assert hasattr(mod, name), name


def test_no_unported_subpackages_pulled_in():
    # Importing integrators must NOT drag in slices 4-6 (safety/results/strategies)
    # or engines/orchestrators. Only core (+numpy/scipy) is a legitimate dep.
    import sys
    import types
    import importlib
    import os
    
    # Save original modules
    saved_modules = {}
    for m in list(sys.modules.keys()):
        if m.startswith("src.simulation"):
            saved_modules[m] = sys.modules[m]
            
    # Find original path before we delete the module
    real_sim_module = sys.modules.get("src.simulation")
    if real_sim_module and hasattr(real_sim_module, "__path__"):
        sim_path = list(real_sim_module.__path__)
    else:
        sim_path = [os.path.join(os.path.dirname(importlib.import_module("src").__file__), "simulation")]
        
    # Unload src.simulation submodules to force fresh import
    for m in list(sys.modules.keys()):
        if m.startswith("src.simulation"):
            del sys.modules[m]
            
    # Mock parent module as a package with __path__ to bypass its eager __init__.py
    mock_sim = types.ModuleType("src.simulation")
    mock_sim.__path__ = sim_path
    sys.modules["src.simulation"] = mock_sim
    
    try:
        importlib.import_module("src.simulation.integrators")
        for forbidden in ("src.simulation.orchestrators", "src.simulation.safety",
                          "src.simulation.results", "src.simulation.strategies",
                          "src.simulation.engines"):
            assert forbidden not in sys.modules, f"unexpectedly imported {forbidden}"
    finally:
        # Restore original modules
        for m in list(sys.modules.keys()):
            if m.startswith("src.simulation"):
                del sys.modules[m]
        for m, mod in saved_modules.items():
            sys.modules[m] = mod


