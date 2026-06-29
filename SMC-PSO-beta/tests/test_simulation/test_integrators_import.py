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
    importlib.import_module("src.simulation.integrators")
    for forbidden in ("src.simulation.orchestrators", "src.simulation.safety",
                      "src.simulation.results", "src.simulation.strategies",
                      "src.simulation.engines"):
        assert forbidden not in sys.modules, f"unexpectedly imported {forbidden}"
