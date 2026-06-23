"""M2 Lens-B/C invariant tests for the DIP full plant model.

These run against the production FullDIPDynamics to prove physical consistency.
ASCII only. Run: python -m pytest tests/test_plant/test_full_dynamics_invariants.py -q
"""
import os, sys
import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from plant.models.full.config import FullDIPConfig
from plant.models.full.dynamics import FullDIPDynamics

config = FullDIPConfig(
    cart_mass=1.5,
    pendulum1_mass=0.2,
    pendulum2_mass=0.15,
    pendulum1_length=0.4,
    pendulum2_length=0.3,
    pendulum1_com=0.2,
    pendulum2_com=0.15,
    pendulum1_inertia=0.0081,
    pendulum2_inertia=0.0034,
    gravity=9.81,
    cart_viscous_friction=0.0,
    cart_coulomb_friction=0.0,
    joint1_viscous_friction=0.0,
    joint1_coulomb_friction=0.0,
    joint2_viscous_friction=0.0,
    joint2_coulomb_friction=0.0,
    include_aerodynamic_forces=False,
    wind_model_enabled=False,
    base_excitation_enabled=False,
    use_adaptive_integration=False,
    use_iterative_refinement=False,
    regularization_alpha=0.0,
    min_regularization=0.0
)

dyn = FullDIPDynamics(config, enable_monitoring=False, enable_validation=False)
RNG = np.random.default_rng(123)


@pytest.mark.parametrize("_", range(200))
def test_inertia_symmetric_pd(_):
    t1, t2 = RNG.uniform(-np.pi, np.pi, 2)
    state = np.array([0.0, t1, t2, 0.0, 0.0, 0.0])
    M, _, _ = dyn.get_physics_matrices(state)
    assert np.allclose(M, M.T, atol=1e-12)
    assert np.min(np.linalg.eigvalsh((M + M.T) / 2)) > 0


@pytest.mark.parametrize("_", range(200))
def test_kinetic_energy_matches_inertia(_):
    t1, t2 = RNG.uniform(-np.pi, np.pi, 2)
    qd = RNG.uniform(-3, 3, 3)
    st = np.array([0.0, t1, t2, qd[0], qd[1], qd[2]])
    M, _, _ = dyn.get_physics_matrices(st)
    ke_analysis = dyn.compute_energy_analysis(st)['kinetic_energy']
    assert ke_analysis == pytest.approx(0.5 * qd.dot(M.dot(qd)), abs=1e-10)


@pytest.mark.parametrize("_", range(200))
def test_coriolis_skew_symmetry(_):
    q = np.array([0.0, RNG.uniform(-np.pi, np.pi), RNG.uniform(-np.pi, np.pi)])
    qd = RNG.uniform(-3, 3, 3)
    h = 1e-6

    st_p = np.array([q[0], q[1] + h * qd[1], q[2] + h * qd[2], 0.0, 0.0, 0.0])
    st_m = np.array([q[0], q[1] - h * qd[1], q[2] - h * qd[2], 0.0, 0.0, 0.0])

    Mp, _, _ = dyn.get_physics_matrices(st_p)
    Mm, _, _ = dyn.get_physics_matrices(st_m)
    Mdot = (Mp - Mm) / (2 * h)

    st = np.array([q[0], q[1], q[2], qd[0], qd[1], qd[2]])
    _, C, _ = dyn.get_physics_matrices(st)

    S = Mdot - 2 * C
    assert abs(qd.dot(S.dot(qd))) < 1e-4


def test_energy_conserved_zero_input_frictionless():
    s = np.array([0.0, 0.15, -0.10, 0.0, 0.0, 0.0])

    def get_total_energy(st):
        e = dyn.compute_energy_analysis(st)
        return e['kinetic_energy'] + e['potential_energy']

    E0 = get_total_energy(s)
    dt, dr = 1e-4, 0.0
    u = np.array([0.0])
    for _ in range(int(2.0 / dt)):
        k1 = dyn.compute_dynamics(s, u).state_derivative
        k2 = dyn.compute_dynamics(s + 0.5 * dt * k1, u).state_derivative
        k3 = dyn.compute_dynamics(s + 0.5 * dt * k2, u).state_derivative
        k4 = dyn.compute_dynamics(s + dt * k3, u).state_derivative
        s = s + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        dr = max(dr, abs(get_total_energy(s) - E0))
    assert dr / abs(E0) < 1e-3


def test_upright_and_down_equilibria():
    # zero velocity + zero gravity-free angle => zero generalized accel at theta=0
    s0 = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    u = np.array([0.0])
    assert np.allclose(dyn.compute_dynamics(s0, u).state_derivative[3:], 0.0, atol=1e-12)


def test_physics_matrices_direct_coverage():
    from plant.core.physics_matrices import DIPPhysicsMatrices, SimplifiedDIPPhysicsMatrices
    pm = DIPPhysicsMatrices(config)
    spm = SimplifiedDIPPhysicsMatrices(config)
    
    state = np.array([0.1, 0.2, -0.3, 0.4, 0.5, -0.6])
    
    # DIPPhysicsMatrices
    M1 = pm.compute_inertia_matrix(state)
    C1 = pm.compute_coriolis_matrix(state)
    G1 = pm.compute_gravity_vector(state)
    
    M2, C2, G2 = pm.compute_all_matrices(state)
    assert np.allclose(M1, M2)
    assert np.allclose(C1, C2)
    assert np.allclose(G1, G2)
    
    # SimplifiedDIPPhysicsMatrices
    M_simp = spm.compute_inertia_matrix(state)
    assert M_simp.shape == (3, 3)

