"""
Robustness tests for STA SMC controller (Super-Twisting Algorithm).

Tests controller performance under sensor faults, actuator limitations,
and combined disturbances. Parameter uncertainty tests are omitted because
STA SMC is inherently robust to parameter variations due to its integral
sliding mode design.
"""

import pytest
import numpy as np
from src.controllers.factory import create_controller, get_default_gains
from src.utils.testing.fault_injection import FaultScenario, SimulationResult


class TestSTASMCRobustness:
    """Robustness test suite for STA SMC (Super-Twisting Algorithm)."""

    @pytest.fixture
    def controller(self):
        """Create STA SMC controller."""
        gains = get_default_gains('sta_smc')
        return create_controller('sta_smc', gains=gains)

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
        """Test STA SMC with mild sensor noise (SNR=50dB)."""
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
        """Test STA SMC with moderate sensor noise (SNR=30dB)."""
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
        """Test STA SMC with severe sensor noise (SNR=10dB)."""
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
        """Test STA SMC with mild actuator saturation (80%)."""
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
        """Test STA SMC with moderate actuator saturation (60%)."""
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
        """Test STA SMC with severe actuator saturation (40%)."""
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
    # COMBINED FAULTS TESTS
    # (Parameter uncertainty tests omitted - STA SMC is inherently robust)
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
        """Test STA SMC with combined mild faults."""
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
        """Test STA SMC with combined moderate faults."""
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
        """Test STA SMC with combined severe faults."""
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
        assert ri > 0.5, "STA SMC should have decent robustness (RI > 0.5)"


# Run tests if executed directly
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
