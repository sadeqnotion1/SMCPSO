"""M4 Slice 3 - integrator factory."""
import numpy as np
import pytest

from src.simulation.integrators.factory import (
    IntegratorFactory, create_integrator, get_available_integrators,
)
from src.simulation.integrators.base import BaseIntegrator
from src.simulation.integrators.fixed_step.runge_kutta import RungeKutta4
from src.simulation.integrators.fixed_step.euler import ForwardEuler
from src.simulation.integrators.adaptive.runge_kutta import DormandPrince45


def test_create_known_types():
    assert isinstance(create_integrator("rk4"), RungeKutta4)
    assert isinstance(create_integrator("euler"), ForwardEuler)
    assert isinstance(create_integrator("dp45"), DormandPrince45)
    assert isinstance(create_integrator("dormand_prince"), DormandPrince45)


def test_name_normalization():
    assert isinstance(create_integrator("Runge-Kutta 4"), RungeKutta4)


def test_default_dt_stored():
    integ = create_integrator("rk4", dt=0.02)
    assert integ.default_dt == 0.02


def test_unknown_type_raises():
    with pytest.raises(ValueError):
        create_integrator("does_not_exist")


def test_list_and_convenience():
    avail = get_available_integrators()
    for key in ("euler", "rk4", "dp45", "zoh"):
        assert key in avail


def test_create_default_is_rk4():
    assert isinstance(IntegratorFactory.create_default_integrator(), RungeKutta4)


def test_register_custom_integrator():
    class MyInteg(BaseIntegrator):
        @property
        def order(self):
            return 1
        @property
        def adaptive(self):
            return False
        def integrate(self, dynamics_fn, state, control, dt, **kwargs):
            return state
    IntegratorFactory.register_integrator("myinteg", MyInteg)
    assert isinstance(create_integrator("myinteg"), MyInteg)


def test_register_rejects_non_subclass():
    with pytest.raises(ValueError):
        IntegratorFactory.register_integrator("bad", dict)
