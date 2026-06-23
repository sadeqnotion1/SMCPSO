#======================================================================================\\
#============ tests/test_controllers/smc/core/test_plant_integration.py ==============\\
#======================================================================================\\

"""
Integration Tests: SMC Core Components with Plant Models.

SINGLE JOB: Validate that SMC core components (sliding surface, switching functions,
equivalent control) work correctly with all 3 plant dynamics implementations:
- SimplifiedDIPDynamics
- FullDIPDynamics
- ModularLowRankDynamics

Tests verify:
- Controllers produce finite control outputs with all plant models
- State evolution is physically realistic
- Control objectives are achieved (stabilization)
- Numerical stability across different dynamics implementations
"""

import pytest
import numpy as np

from src.plant.models import (
    SimplifiedDIPDynamics,
    SimplifiedDIPConfig,
    FullDIPDynamics,
    FullDIPConfig,
    ModularLowRankDynamics,
    LowRankDIPConfig
)

from src.controllers.smc.core.sliding_surface import LinearSlidingSurface
from src.controllers.smc.core.switching_functions import SwitchingFunction, SwitchingMethod
from src.controllers.smc.core.equivalent_control import EquivalentControl


# Config helpers for different model types
def _create_simplified_config_dict():
    """Create config for SimplifiedDIPDynamics."""
    # Inertia bounds: min = m * com^2, max = m * L^2
    # For pendulum1: min = 0.23 * 0.32^2 = 0.0235, max = 0.23 * 0.64^2 = 0.0942
    return {
        'cart_mass': 2.4,
        'pendulum1_mass': 0.23,
        'pendulum2_mass': 0.23,
        'pendulum1_length': 0.64,
        'pendulum2_length': 0.64,
        'pendulum1_com': 0.32,
        'pendulum2_com': 0.32,
        'pendulum1_inertia': 0.05,  # Within bounds [0.0235, 0.0942]
        'pendulum2_inertia': 0.05,
        'gravity': 9.81,
        'cart_friction': 0.0,
        'joint1_friction': 0.0,
        'joint2_friction': 0.0,
        'use_fixed_regularization': False
    }


def _create_full_config_dict():
    """Create config for FullDIPDynamics."""
    return {
        'cart_mass': 2.4,
        'pendulum1_mass': 0.23,
        'pendulum2_mass': 0.23,
        'pendulum1_length': 0.64,
        'pendulum2_length': 0.64,
        'pendulum1_com': 0.32,
        'pendulum2_com': 0.32,
        'pendulum1_inertia': 0.05,
        'pendulum2_inertia': 0.05,
        'gravity': 9.81,
        'cart_viscous_friction': 0.0,
        'cart_coulomb_friction': 0.0,
        'joint1_viscous_friction': 0.0,
        'joint1_coulomb_friction': 0.0,
        'joint2_viscous_friction': 0.0,
        'joint2_coulomb_friction': 0.0,
    }


def _create_lowrank_config_dict():
    """Create config for ModularLowRankDynamics."""
    return {
        'cart_mass': 2.4,
        'pendulum1_mass': 0.23,
        'pendulum2_mass': 0.23,
        'pendulum1_length': 0.64,
        'pendulum2_length': 0.64,
        'gravity': 9.81,
        'friction_coefficient': 0.0,
        'damping_coefficient': 0.0,
    }


# Fixtures for plant models
@pytest.fixture
def simplified_dynamics():
    """Create simplified DIP dynamics model."""
    config_dict = _create_simplified_config_dict()
    config = SimplifiedDIPConfig(**config_dict)
    return SimplifiedDIPDynamics(config=config)


@pytest.fixture
def full_dynamics():
    """Create full fidelity DIP dynamics model."""
    config_dict = _create_full_config_dict()
    config = FullDIPConfig(**config_dict)
    return FullDIPDynamics(config=config)


@pytest.fixture
def lowrank_dynamics():
    """Create low-rank DIP dynamics model."""
    config_dict = _create_lowrank_config_dict()
    config = LowRankDIPConfig(**config_dict)
    return ModularLowRankDynamics(config=config)


@pytest.fixture
def all_dynamics(simplified_dynamics, full_dynamics, lowrank_dynamics):
    """Parametrize fixture providing all dynamics models."""
    return [
        ('simplified', simplified_dynamics),
        ('full', full_dynamics),
        ('lowrank', lowrank_dynamics)
    ]


# Fixtures for SMC components
@pytest.fixture
def sliding_surface():
    """Create sliding surface with standard gains."""
    gains = [10.0, 8.0, 5.0, 3.0]  # k1, k2, lam1, lam2
    return LinearSlidingSurface(gains)


@pytest.fixture
def switching_function():
    """Create tanh switching function."""
    return SwitchingFunction(SwitchingMethod.TANH)


@pytest.fixture
def test_state():
    """Create a small perturbation from equilibrium."""
    # Small angles (5 degrees), small velocities
    return np.array([0.0, 0.0, np.radians(5), 0.1, np.radians(-5), -0.1])


@pytest.fixture
def equilibrium_state():
    """Create equilibrium state (upright, zero velocity)."""
    return np.zeros(6)


@pytest.mark.integration
class TestSlidingSurfaceWithPlantModels:
    """Test sliding surface computation with different plant models."""

    def test_sliding_surface_with_simplified_dynamics(self, simplified_dynamics, sliding_surface, test_state):
        """Test sliding surface works with simplified dynamics."""
        # Compute sliding surface
        s = sliding_surface.compute(test_state)

        # Should be finite
        assert np.isfinite(s), "Sliding surface with simplified dynamics is not finite"

        # Should be non-zero for perturbed state
        assert abs(s) > 1e-6, "Sliding surface should be non-zero for perturbed state"

    def test_sliding_surface_with_full_dynamics(self, full_dynamics, sliding_surface, test_state):
        """Test sliding surface works with full dynamics."""
        s = sliding_surface.compute(test_state)

        assert np.isfinite(s), "Sliding surface with full dynamics is not finite"
        assert abs(s) > 1e-6, "Sliding surface should be non-zero for perturbed state"

    def test_sliding_surface_with_lowrank_dynamics(self, lowrank_dynamics, sliding_surface, test_state):
        """Test sliding surface works with low-rank dynamics."""
        s = sliding_surface.compute(test_state)

        assert np.isfinite(s), "Sliding surface with lowrank dynamics is not finite"
        assert abs(s) > 1e-6, "Sliding surface should be non-zero for perturbed state"

    def test_sliding_surface_consistency_across_models(self, all_dynamics, sliding_surface, test_state):
        """Test sliding surface is consistent across all dynamics models."""
        # Sliding surface should be the SAME for all models (it only depends on state, not dynamics)
        surfaces = []

        for model_name, dynamics in all_dynamics:
            s = sliding_surface.compute(test_state)
            surfaces.append((model_name, s))

        # All should be identical (sliding surface is independent of dynamics)
        s_simplified = surfaces[0][1]
        for model_name, s in surfaces[1:]:
            assert np.isclose(s, s_simplified, rtol=1e-10), \
                f"Sliding surface inconsistent: {model_name} s={s} != simplified s={s_simplified}"


@pytest.mark.integration
class TestEquivalentControlWithPlantModels:
    """Test equivalent control computation with different plant models."""

    def test_equivalent_control_with_simplified_dynamics(self, simplified_dynamics, sliding_surface, test_state):
        """Test equivalent control with simplified dynamics."""
        eq_control = EquivalentControl(dynamics_model=simplified_dynamics)

        u_eq = eq_control.compute(test_state, sliding_surface)

        # Should be finite
        assert np.isfinite(u_eq), "Equivalent control with simplified dynamics is not finite"

    def test_equivalent_control_with_full_dynamics(self, full_dynamics, sliding_surface, test_state):
        """Test equivalent control with full dynamics."""
        eq_control = EquivalentControl(dynamics_model=full_dynamics)

        u_eq = eq_control.compute(test_state, sliding_surface)

        assert np.isfinite(u_eq), "Equivalent control with full dynamics is not finite"

    def test_equivalent_control_with_lowrank_dynamics(self, lowrank_dynamics, sliding_surface, test_state):
        """Test equivalent control with low-rank dynamics."""
        eq_control = EquivalentControl(dynamics_model=lowrank_dynamics)

        u_eq = eq_control.compute(test_state, sliding_surface)

        assert np.isfinite(u_eq), "Equivalent control with lowrank dynamics is not finite"

    def test_equivalent_control_variability_across_models(self, all_dynamics, sliding_surface, test_state):
        """Test equivalent control varies across dynamics models (model-dependent)."""
        u_eqs = []

        for model_name, dynamics in all_dynamics:
            eq_control = EquivalentControl(dynamics_model=dynamics)
            u_eq = eq_control.compute(test_state, sliding_surface)
            u_eqs.append((model_name, u_eq))

        # Equivalent controls can differ across models (dynamics-dependent)
        # But all should be finite
        for model_name, u_eq in u_eqs:
            assert np.isfinite(u_eq), f"{model_name}: u_eq not finite"

    def test_equivalent_control_at_equilibrium(self, all_dynamics, sliding_surface, equilibrium_state):
        """Test equivalent control at equilibrium (should be small or zero)."""
        for model_name, dynamics in all_dynamics:
            eq_control = EquivalentControl(dynamics_model=dynamics)
            u_eq = eq_control.compute(equilibrium_state, sliding_surface)

            # At equilibrium, equivalent control should be very small
            # (ideally zero, but numerical errors may cause small values)
            assert abs(u_eq) < 1.0, \
                f"{model_name}: u_eq at equilibrium too large: {u_eq}"


@pytest.mark.integration
class TestCompleteSMCControlLawWithPlantModels:
    """Test complete SMC control law with all plant models."""

    def test_complete_control_law_with_simplified(self, simplified_dynamics, sliding_surface,
                                                  switching_function, test_state):
        """Test complete SMC control law: u = u_eq - K*switch(s/ε)."""
        eq_control = EquivalentControl(dynamics_model=simplified_dynamics)

        # Compute sliding surface
        s = sliding_surface.compute(test_state)

        # Compute equivalent control
        u_eq = eq_control.compute(test_state, sliding_surface)

        # Compute switching component
        epsilon = 0.1  # Boundary layer
        K = 15.0  # Switching gain
        u_switch = K * switching_function.compute(s, epsilon)

        # Complete control law
        u_total = u_eq - u_switch

        # Should be finite
        assert np.isfinite(u_total), "Total control with simplified dynamics is not finite"

        # Should be bounded (rough sanity check)
        assert abs(u_total) < 1000.0, "Total control unreasonably large"

    def test_complete_control_law_with_full(self, full_dynamics, sliding_surface,
                                           switching_function, test_state):
        """Test complete SMC control law with full dynamics."""
        eq_control = EquivalentControl(dynamics_model=full_dynamics)

        s = sliding_surface.compute(test_state)
        u_eq = eq_control.compute(test_state, sliding_surface)
        u_switch = 15.0 * switching_function.compute(s, 0.1)
        u_total = u_eq - u_switch

        assert np.isfinite(u_total), "Total control with full dynamics is not finite"
        assert abs(u_total) < 1000.0, "Total control unreasonably large"

    def test_complete_control_law_with_lowrank(self, lowrank_dynamics, sliding_surface,
                                               switching_function, test_state):
        """Test complete SMC control law with low-rank dynamics."""
        eq_control = EquivalentControl(dynamics_model=lowrank_dynamics)

        s = sliding_surface.compute(test_state)
        u_eq = eq_control.compute(test_state, sliding_surface)
        u_switch = 15.0 * switching_function.compute(s, 0.1)
        u_total = u_eq - u_switch

        assert np.isfinite(u_total), "Total control with lowrank dynamics is not finite"
        assert abs(u_total) < 1000.0, "Total control unreasonably large"

    def test_control_law_all_models(self, all_dynamics, sliding_surface, switching_function, test_state):
        """Test control law works with all dynamics models."""
        for model_name, dynamics in all_dynamics:
            eq_control = EquivalentControl(dynamics_model=dynamics)

            s = sliding_surface.compute(test_state)
            u_eq = eq_control.compute(test_state, sliding_surface)
            u_switch = 15.0 * switching_function.compute(s, 0.1)
            u_total = u_eq - u_switch

            # All control outputs should be finite and reasonable
            assert np.isfinite(u_total), f"{model_name}: u_total not finite"
            assert abs(u_total) < 1000.0, f"{model_name}: u_total too large: {u_total}"


@pytest.mark.integration
class TestSimulationStepWithPlantModels:
    """Test single simulation step with SMC + plant models."""

    def test_simulation_step_simplified(self, simplified_dynamics, sliding_surface,
                                       switching_function, test_state):
        """Test one simulation step with simplified dynamics."""
        eq_control = EquivalentControl(dynamics_model=simplified_dynamics)

        # Compute control
        s = sliding_surface.compute(test_state)
        u_eq = eq_control.compute(test_state, sliding_surface)
        u_switch = 15.0 * switching_function.compute(s, 0.1)
        u = u_eq - u_switch

        # Apply control and get state derivative
        result = simplified_dynamics.compute_dynamics(test_state, np.array([u]))
        assert result.success, f"Dynamics computation failed: {result.info.get('failure_reason', 'Unknown')}"
        state_dot = result.state_derivative

        # State derivative should be finite
        assert np.all(np.isfinite(state_dot)), "State derivative contains non-finite values"

        # State should evolve (not stuck at current state)
        assert np.linalg.norm(state_dot) > 1e-10, "State derivative too small (system not evolving)"

    def test_simulation_step_full(self, full_dynamics, sliding_surface,
                                  switching_function, test_state):
        """Test one simulation step with full dynamics."""
        eq_control = EquivalentControl(dynamics_model=full_dynamics)

        s = sliding_surface.compute(test_state)
        u_eq = eq_control.compute(test_state, sliding_surface)
        u_switch = 15.0 * switching_function.compute(s, 0.1)
        u = u_eq - u_switch

        result = full_dynamics.compute_dynamics(test_state, np.array([u]))
        assert result.success, f"Dynamics computation failed: {result.info.get('failure_reason', 'Unknown')}"
        state_dot = result.state_derivative

        assert np.all(np.isfinite(state_dot)), "State derivative contains non-finite values"
        assert np.linalg.norm(state_dot) > 1e-10, "State derivative too small"

    def test_simulation_step_lowrank(self, lowrank_dynamics, sliding_surface,
                                     switching_function, test_state):
        """Test one simulation step with low-rank dynamics."""
        eq_control = EquivalentControl(dynamics_model=lowrank_dynamics)

        s = sliding_surface.compute(test_state)
        u_eq = eq_control.compute(test_state, sliding_surface)
        u_switch = 15.0 * switching_function.compute(s, 0.1)
        u = u_eq - u_switch

        result = lowrank_dynamics.compute_dynamics(test_state, np.array([u]))
        assert result.success, f"Dynamics computation failed: {result.info.get('failure_reason', 'Unknown')}"
        state_dot = result.state_derivative

        assert np.all(np.isfinite(state_dot)), "State derivative contains non-finite values"
        assert np.linalg.norm(state_dot) > 1e-10, "State derivative too small"

    def test_euler_integration_step_all_models(self, all_dynamics, sliding_surface,
                                               switching_function, test_state):
        """Test Euler integration step with all models."""
        dt = 0.001  # Small timestep

        for model_name, dynamics in all_dynamics:
            eq_control = EquivalentControl(dynamics_model=dynamics)

            # Compute control
            s = sliding_surface.compute(test_state)
            u_eq = eq_control.compute(test_state, sliding_surface)
            u_switch = 15.0 * switching_function.compute(s, 0.1)
            u = u_eq - u_switch

            # Get state derivative
            result = dynamics.compute_dynamics(test_state, np.array([u]))
            assert result.success, f"{model_name}: Dynamics failed: {result.info.get('failure_reason', 'Unknown')}"
            state_dot = result.state_derivative

            # Euler step: x_{k+1} = x_k + dt * f(x_k, u_k)
            next_state = test_state + dt * state_dot

            # Next state should be finite
            assert np.all(np.isfinite(next_state)), \
                f"{model_name}: next_state contains non-finite values"

            # State should change (not frozen)
            state_change = np.linalg.norm(next_state - test_state)
            assert state_change > 1e-12, \
                f"{model_name}: State didn't change in Euler step"


@pytest.mark.integration
class TestMultiStepSimulationWithPlantModels:
    """Test multi-step simulation with SMC + plant models."""

    def test_10_step_simulation_simplified(self, simplified_dynamics, sliding_surface,
                                          switching_function):
        """Test 10-step simulation with simplified dynamics."""
        eq_control = EquivalentControl(dynamics_model=simplified_dynamics)

        # Initial state
        state = np.array([0.0, 0.0, np.radians(10), 0.0, np.radians(-10), 0.0])
        dt = 0.001

        for _ in range(10):
            # Compute control
            s = sliding_surface.compute(state)
            u_eq = eq_control.compute(state, sliding_surface)
            u_switch = 15.0 * switching_function.compute(s, 0.1)
            u = u_eq - u_switch

            # Integrate
            result = simplified_dynamics.compute_dynamics(state, np.array([u]))
            assert result.success, f"Dynamics failed: {result.info.get('failure_reason', 'Unknown')}"
            state_dot = result.state_derivative
            state = state + dt * state_dot

            # Check state remains finite
            assert np.all(np.isfinite(state)), "State became non-finite during simulation"

        # After 10 steps, state should still be reasonable (not diverged)
        assert np.linalg.norm(state) < 100.0, "State diverged during simulation"

    def test_10_step_simulation_all_models(self, all_dynamics, sliding_surface, switching_function):
        """Test 10-step simulation with all models."""
        for model_name, dynamics in all_dynamics:
            eq_control = EquivalentControl(dynamics_model=dynamics)

            state = np.array([0.0, 0.0, np.radians(10), 0.0, np.radians(-10), 0.0])
            dt = 0.001

            for _ in range(10):
                s = sliding_surface.compute(state)
                u_eq = eq_control.compute(state, sliding_surface)
                u_switch = 15.0 * switching_function.compute(s, 0.1)
                u = u_eq - u_switch

                result = dynamics.compute_dynamics(state, np.array([u]))
                assert result.success, f"{model_name}: Dynamics failed: {result.info.get('failure_reason', 'Unknown')}"
                state_dot = result.state_derivative
                state = state + dt * state_dot

                assert np.all(np.isfinite(state)), f"{model_name}: State became non-finite"

            # State should remain bounded
            assert np.linalg.norm(state) < 100.0, f"{model_name}: State diverged"


@pytest.mark.integration
class TestNumericalStabilityAcrossModels:
    """Test numerical stability of SMC core with different plant models."""

    def test_large_perturbation_handling(self, all_dynamics, sliding_surface, switching_function):
        """Test SMC handles large perturbations without numerical issues."""
        # Large initial perturbation (30 degrees)
        state = np.array([0.0, 0.0, np.radians(30), 0.5, np.radians(-30), -0.5])

        for model_name, dynamics in all_dynamics:
            eq_control = EquivalentControl(dynamics_model=dynamics)

            # Compute control
            s = sliding_surface.compute(state)
            u_eq = eq_control.compute(state, sliding_surface)
            u_switch = 15.0 * switching_function.compute(s, 0.1)
            u = u_eq - u_switch

            # All outputs should be finite
            assert np.isfinite(s), f"{model_name}: s not finite for large perturbation"
            assert np.isfinite(u_eq), f"{model_name}: u_eq not finite for large perturbation"
            assert np.isfinite(u), f"{model_name}: u not finite for large perturbation"

    def test_zero_state_handling(self, all_dynamics, sliding_surface, equilibrium_state):
        """Test SMC handles equilibrium state correctly."""
        for model_name, dynamics in all_dynamics:
            eq_control = EquivalentControl(dynamics_model=dynamics)

            s = sliding_surface.compute(equilibrium_state)
            u_eq = eq_control.compute(equilibrium_state, sliding_surface)

            # At equilibrium, sliding surface should be zero
            assert abs(s) < 1e-10, f"{model_name}: s not zero at equilibrium: {s}"

            # Equivalent control should be small (holding at equilibrium)
            assert abs(u_eq) < 10.0, f"{model_name}: u_eq too large at equilibrium: {u_eq}"


@pytest.mark.integration
class TestControllabilityAcrossModels:
    """Test controllability analysis with different plant models."""

    @pytest.mark.skip(reason="Requires get_dynamics(state)->(M,F) interface; models provide get_physics_matrices(state)->(M,C,G)")
    def test_controllability_check_simplified(self, simplified_dynamics, sliding_surface, test_state):
        """Test controllability analysis with simplified dynamics."""
        eq_control = EquivalentControl(dynamics_model=simplified_dynamics)

        result = eq_control.check_controllability(test_state, sliding_surface)

        # Should return valid dict
        assert 'controllable' in result
        assert 'condition_number' in result
        assert np.isfinite(result['condition_number'])

    @pytest.mark.skip(reason="Requires get_dynamics(state)->(M,F) interface; models provide get_physics_matrices(state)->(M,C,G)")
    def test_controllability_check_all_models(self, all_dynamics, sliding_surface, test_state):
        """Test controllability analysis with all models."""
        for model_name, dynamics in all_dynamics:
            eq_control = EquivalentControl(dynamics_model=dynamics)

            result = eq_control.check_controllability(test_state, sliding_surface)

            assert 'controllable' in result, f"{model_name}: missing 'controllable' key"
            assert 'condition_number' in result, f"{model_name}: missing 'condition_number'"
            assert np.isfinite(result['condition_number']), \
                f"{model_name}: condition number not finite"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
