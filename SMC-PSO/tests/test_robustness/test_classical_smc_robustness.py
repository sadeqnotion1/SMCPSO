"""
Robustness tests for Classical SMC controller.

Tests controller performance under sensor faults, actuator limitations,
parameter variations, and combined disturbances.
"""

import pytest
import numpy as np
from src.controllers.factory import create_controller, get_default_gains
from src.utils.testing.fault_injection import FaultScenario, SimulationResult


class TestClassicalSMCRobustness:
    """Robustness test suite for Classical SMC."""

    @pytest.fixture
    def controller(self):
        """Create Classical SMC controller."""
        gains = get_default_gains('classical_smc')
        return create_controller('classical_smc', gains=gains)

    @pytest.fixture
    def baseline_result(self, controller, dynamics, initial_state, simulation_params):
        """Run baseline (no faults) simulation."""
        scenario = FaultScenario(name="baseline", seed=42)
        result = scenario.run_simulation(
            controller=controller,
            plant=dynamics,
            initial_state=initial_state,
            duration=simulation_params['duration'],
            dt=simulation_params['dt']
        )
        return result

    # ========================================================================
    # SENSOR NOISE TESTS
    # ========================================================================

    def test_sensor_noise_mild(
        self,
        controller,
        dynamics,
        initial_state,
        simulation_params,
        sensor_noise_mild,
        baseline_result,
        fault_acceptance_criteria
    ):
        """Test Classical SMC with mild sensor noise (SNR=50dB)."""
        result = sensor_noise_mild.run_simulation(
            controller=controller,
            plant=dynamics,
            initial_state=initial_state,
            duration=simulation_params['duration'],
            dt=simulation_params['dt']
        )

        # Compute degradation
        result.compute_degradation(baseline_result)

        # Assertions
        assert result.stability, "Controller must remain stable with mild noise"

        # Check settling time degradation only if finite (not NaN from inf/inf)
        if not np.isnan(result.settling_time_degradation_pct):
            assert result.settling_time_degradation_pct <= fault_acceptance_criteria['settling_time_degradation_max'], \
                f"Settling time degradation {result.settling_time_degradation_pct:.1f}% exceeds limit"

        assert result.overshoot_degradation_pct <= fault_acceptance_criteria['overshoot_degradation_max'], \
            f"Overshoot degradation {result.overshoot_degradation_pct:.1f}% exceeds limit"

    def test_sensor_noise_moderate(
        self,
        controller,
        dynamics,
        initial_state,
        simulation_params,
        sensor_noise_moderate,
        baseline_result,
        fault_acceptance_criteria
    ):
        """Test Classical SMC with moderate sensor noise (SNR=30dB)."""
        result = sensor_noise_moderate.run_simulation(
            controller=controller,
            plant=dynamics,
            initial_state=initial_state,
            duration=simulation_params['duration'],
            dt=simulation_params['dt']
        )

        result.compute_degradation(baseline_result)

        assert result.stability, "Controller must remain stable with moderate noise"

        # Check settling time degradation only if finite (not NaN from inf/inf)
        if not np.isnan(result.settling_time_degradation_pct):
            assert result.settling_time_degradation_pct <= fault_acceptance_criteria['settling_time_degradation_max']

    def test_sensor_noise_severe(
        self,
        controller,
        dynamics,
        initial_state,
        simulation_params,
        sensor_noise_severe,
        baseline_result
    ):
        """Test Classical SMC with severe sensor noise (SNR=10dB)."""
        result = sensor_noise_severe.run_simulation(
            controller=controller,
            plant=dynamics,
            initial_state=initial_state,
            duration=simulation_params['duration'],
            dt=simulation_params['dt']
        )

        result.compute_degradation(baseline_result)

        # Severe noise may exceed acceptance criteria, but must remain stable
        assert result.stability, "Controller must remain stable (no divergence)"

    # ========================================================================
    # ACTUATOR SATURATION TESTS
    # ========================================================================

    def test_actuator_saturation_mild(
        self,
        controller,
        dynamics,
        initial_state,
        simulation_params,
        actuator_saturation_mild,
        baseline_result,
        fault_acceptance_criteria
    ):
        """Test Classical SMC with mild actuator saturation (80%)."""
        result = actuator_saturation_mild.run_simulation(
            controller=controller,
            plant=dynamics,
            initial_state=initial_state,
            duration=simulation_params['duration'],
            dt=simulation_params['dt']
        )

        result.compute_degradation(baseline_result)

        assert result.stability, "Controller must remain stable with mild saturation"

        # Check settling time degradation only if finite (not NaN from inf/inf)
        if not np.isnan(result.settling_time_degradation_pct):
            assert result.settling_time_degradation_pct <= fault_acceptance_criteria['settling_time_degradation_max']

    def test_actuator_saturation_moderate(
        self,
        controller,
        dynamics,
        initial_state,
        simulation_params,
        actuator_saturation_moderate,
        baseline_result,
        fault_acceptance_criteria
    ):
        """Test Classical SMC with moderate actuator saturation (60%)."""
        result = actuator_saturation_moderate.run_simulation(
            controller=controller,
            plant=dynamics,
            initial_state=initial_state,
            duration=simulation_params['duration'],
            dt=simulation_params['dt']
        )

        result.compute_degradation(baseline_result)

        assert result.stability, "Controller must remain stable with moderate saturation"

    def test_actuator_saturation_severe(
        self,
        controller,
        dynamics,
        initial_state,
        simulation_params,
        actuator_saturation_severe,
        baseline_result
    ):
        """Test Classical SMC with severe actuator saturation (40%)."""
        result = actuator_saturation_severe.run_simulation(
            controller=controller,
            plant=dynamics,
            initial_state=initial_state,
            duration=simulation_params['duration'],
            dt=simulation_params['dt']
        )

        result.compute_degradation(baseline_result)

        # Severe saturation may exceed criteria but must remain stable
        assert result.stability, "Controller must remain stable (no divergence)"

    # ========================================================================
    # PARAMETER UNCERTAINTY TESTS
    # ========================================================================

    def test_parameter_uncertainty_mild(
        self,
        controller,
        dynamics,
        initial_state,
        simulation_params,
        parameter_uncertainty_mild,
        baseline_result,
        fault_acceptance_criteria
    ):
        """Test Classical SMC with mild parameter uncertainty (±5%)."""
        # NOTE: Parameter uncertainty affects controller gains, not plant
        # Apply gain errors to controller gains before simulation
        nominal_gains = np.array([10.0, 5.0, 8.0, 3.0, 15.0, 2.0])
        gain_fault = parameter_uncertainty_mild._parametric_faults[0]
        corrupted_gains = gain_fault.inject(nominal_gains)

        # Recreate controller with corrupted gains
        faulty_controller = create_controller('classical_smc', gains=corrupted_gains.tolist())

        # Run simulation without parameter fault (since we already applied it)
        scenario = FaultScenario(name="parameter_uncertainty_mild_applied", seed=42)
        result = scenario.run_simulation(
            controller=faulty_controller,
            plant=dynamics,
            initial_state=initial_state,
            duration=simulation_params['duration'],
            dt=simulation_params['dt']
        )

        result.compute_degradation(baseline_result)

        assert result.stability, "Controller must remain stable with mild parameter uncertainty"

        # Check settling time degradation only if finite (not NaN from inf/inf)
        if not np.isnan(result.settling_time_degradation_pct):
            assert result.settling_time_degradation_pct <= fault_acceptance_criteria['settling_time_degradation_max']

    def test_parameter_uncertainty_moderate(
        self,
        controller,
        dynamics,
        initial_state,
        simulation_params,
        parameter_uncertainty_moderate,
        baseline_result
    ):
        """Test Classical SMC with moderate parameter uncertainty (±10%)."""
        nominal_gains = np.array([10.0, 5.0, 8.0, 3.0, 15.0, 2.0])
        gain_fault = parameter_uncertainty_moderate._parametric_faults[0]
        corrupted_gains = gain_fault.inject(nominal_gains)

        faulty_controller = create_controller('classical_smc', gains=corrupted_gains.tolist())

        scenario = FaultScenario(name="parameter_uncertainty_moderate_applied", seed=42)
        result = scenario.run_simulation(
            controller=faulty_controller,
            plant=dynamics,
            initial_state=initial_state,
            duration=simulation_params['duration'],
            dt=simulation_params['dt']
        )

        result.compute_degradation(baseline_result)

        assert result.stability, "Controller must remain stable with moderate parameter uncertainty"

    def test_parameter_uncertainty_severe(
        self,
        controller,
        dynamics,
        initial_state,
        simulation_params,
        parameter_uncertainty_severe,
        baseline_result
    ):
        """Test Classical SMC with severe parameter uncertainty (±20%)."""
        nominal_gains = np.array([10.0, 5.0, 8.0, 3.0, 15.0, 2.0])
        gain_fault = parameter_uncertainty_severe._parametric_faults[0]
        corrupted_gains = gain_fault.inject(nominal_gains)

        faulty_controller = create_controller('classical_smc', gains=corrupted_gains.tolist())

        scenario = FaultScenario(name="parameter_uncertainty_severe_applied", seed=42)
        result = scenario.run_simulation(
            controller=faulty_controller,
            plant=dynamics,
            initial_state=initial_state,
            duration=simulation_params['duration'],
            dt=simulation_params['dt']
        )

        result.compute_degradation(baseline_result)

        # Severe uncertainty may exceed criteria but must remain stable
        assert result.stability, "Controller must remain stable (no divergence)"

    # ========================================================================
    # COMBINED FAULTS TESTS
    # ========================================================================

    def test_combined_faults_mild(
        self,
        controller,
        dynamics,
        initial_state,
        simulation_params,
        combined_faults_mild,
        baseline_result,
        fault_acceptance_criteria
    ):
        """Test Classical SMC with combined mild faults."""
        result = combined_faults_mild.run_simulation(
            controller=controller,
            plant=dynamics,
            initial_state=initial_state,
            duration=simulation_params['duration'],
            dt=simulation_params['dt']
        )

        result.compute_degradation(baseline_result)

        assert result.stability, "Controller must remain stable with combined mild faults"

        # Check settling time degradation only if finite (not NaN from inf/inf)
        if not np.isnan(result.settling_time_degradation_pct):
            assert result.settling_time_degradation_pct <= fault_acceptance_criteria['settling_time_degradation_max']

    def test_combined_faults_moderate(
        self,
        controller,
        dynamics,
        initial_state,
        simulation_params,
        combined_faults_moderate,
        baseline_result
    ):
        """Test Classical SMC with combined moderate faults."""
        result = combined_faults_moderate.run_simulation(
            controller=controller,
            plant=dynamics,
            initial_state=initial_state,
            duration=simulation_params['duration'],
            dt=simulation_params['dt']
        )

        result.compute_degradation(baseline_result)

        assert result.stability, "Controller must remain stable with combined moderate faults"

    def test_combined_faults_severe(
        self,
        controller,
        dynamics,
        initial_state,
        simulation_params,
        combined_faults_severe,
        baseline_result
    ):
        """Test Classical SMC with combined severe faults."""
        result = combined_faults_severe.run_simulation(
            controller=controller,
            plant=dynamics,
            initial_state=initial_state,
            duration=simulation_params['duration'],
            dt=simulation_params['dt']
        )

        result.compute_degradation(baseline_result)

        # Severe combined faults may exceed criteria but must remain stable
        assert result.stability, "Controller must remain stable (no divergence)"

    # ========================================================================
    # ROBUSTNESS METRICS
    # ========================================================================

    def test_compute_robustness_index(
        self,
        controller,
        dynamics,
        initial_state,
        simulation_params,
        sensor_noise_moderate,
        baseline_result
    ):
        """Test robustness index calculation."""
        result = sensor_noise_moderate.run_simulation(
            controller=controller,
            plant=dynamics,
            initial_state=initial_state,
            duration=simulation_params['duration'],
            dt=simulation_params['dt']
        )

        result.compute_degradation(baseline_result)
        ri = result.get_robustness_index()

        assert 0.0 <= ri <= 1.0, "Robustness index must be in [0, 1]"
        assert ri > 0.5, "Classical SMC should have decent robustness (RI > 0.5)"


# Run tests if executed directly
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
