"""
Fault scenario management and simulation runner.

Provides tools to compose multiple faults into scenarios and run
robustness simulations with baseline comparison.
"""

import numpy as np
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
import time

from .fault_injector import (
    FaultInjector,
    SensorFaultInjector,
    ActuatorFaultInjector,
    ParametricFaultInjector,
    EnvironmentalFaultInjector
)


@dataclass
class SimulationResult:
    """Results from a fault injection simulation."""

    # Scenario metadata
    scenario_name: str
    controller_name: str
    timestamp: float

    # Performance metrics
    settling_time: float  # Time to reach ±2% of target
    overshoot: float  # Peak deviation from target (%)
    energy: float  # Integral of control effort squared
    stability: bool  # Converged vs diverged

    # Degradation metrics (compared to baseline)
    settling_time_degradation_pct: Optional[float] = None
    overshoot_degradation_pct: Optional[float] = None
    energy_degradation_pct: Optional[float] = None
    stability_maintained: Optional[bool] = None

    # Raw trajectories
    time_array: np.ndarray = field(default_factory=lambda: np.array([]))
    state_trajectory: np.ndarray = field(default_factory=lambda: np.array([]))
    control_trajectory: np.ndarray = field(default_factory=lambda: np.array([]))

    # Fault details
    faults_applied: List[str] = field(default_factory=list)

    def compute_degradation(self, baseline: 'SimulationResult') -> None:
        """
        Compute degradation metrics compared to baseline.

        Args:
            baseline: Baseline (no faults) simulation result
        """
        if baseline.settling_time > 0:
            self.settling_time_degradation_pct = (
                (self.settling_time - baseline.settling_time) / baseline.settling_time * 100.0
            )
        else:
            self.settling_time_degradation_pct = 0.0

        if baseline.overshoot > 0:
            self.overshoot_degradation_pct = (
                (self.overshoot - baseline.overshoot) / baseline.overshoot * 100.0
            )
        else:
            self.overshoot_degradation_pct = 0.0

        if baseline.energy > 0:
            self.energy_degradation_pct = (
                (self.energy - baseline.energy) / baseline.energy * 100.0
            )
        else:
            self.energy_degradation_pct = 0.0

        self.stability_maintained = (self.stability == baseline.stability)

    def get_degradation_score(self, weights: Tuple[float, float, float] = (0.4, 0.4, 0.2)) -> float:
        """
        Compute weighted degradation score.

        Args:
            weights: (w_settling, w_overshoot, w_energy)

        Returns:
            Degradation score (0=no degradation, 100=100% worse)
        """
        if self.settling_time_degradation_pct is None:
            return 0.0

        w1, w2, w3 = weights
        score = (
            w1 * max(0, self.settling_time_degradation_pct) +
            w2 * max(0, self.overshoot_degradation_pct) +
            w3 * max(0, self.energy_degradation_pct)
        ) / sum(weights)

        return score

    def get_robustness_index(self) -> float:
        """
        Compute robustness index (inverse of degradation).

        Returns:
            RI in [0, 1], where 1=perfect robustness, 0=complete failure
        """
        degradation = self.get_degradation_score()
        return 1.0 / (1.0 + degradation / 100.0)


class FaultScenario:
    """Composer for multi-fault scenarios."""

    def __init__(self, name: str, seed: Optional[int] = None):
        """
        Initialize fault scenario.

        Args:
            name: Scenario name
            seed: Random seed for reproducibility
        """
        self.name = name
        self.seed = seed
        self._sensor_faults: List[SensorFaultInjector] = []
        self._actuator_faults: List[ActuatorFaultInjector] = []
        self._parametric_faults: List[ParametricFaultInjector] = []
        self._environmental_faults: List[EnvironmentalFaultInjector] = []

    def add_sensor_fault(self, fault: SensorFaultInjector) -> 'FaultScenario':
        """Add sensor fault to scenario (builder pattern)."""
        self._sensor_faults.append(fault)
        return self

    def add_actuator_fault(self, fault: ActuatorFaultInjector) -> 'FaultScenario':
        """Add actuator fault to scenario."""
        self._actuator_faults.append(fault)
        return self

    def add_parametric_fault(self, fault: ParametricFaultInjector) -> 'FaultScenario':
        """Add parametric fault to scenario."""
        self._parametric_faults.append(fault)
        return self

    def add_environmental_fault(self, fault: EnvironmentalFaultInjector) -> 'FaultScenario':
        """Add environmental fault to scenario."""
        self._environmental_faults.append(fault)
        return self

    def get_all_faults(self) -> List[FaultInjector]:
        """Get list of all faults in scenario."""
        return (
            self._sensor_faults +
            self._actuator_faults +
            self._parametric_faults +
            self._environmental_faults
        )

    def get_fault_names(self) -> List[str]:
        """Get names of all enabled faults."""
        return [f.name for f in self.get_all_faults() if f.enabled]

    def run_simulation(
        self,
        controller: Any,
        plant: Any,
        initial_state: np.ndarray,
        duration: float = 10.0,
        dt: float = 0.01,
        target_state: Optional[np.ndarray] = None
    ) -> SimulationResult:
        """
        Run simulation with fault injection.

        Args:
            controller: Controller object with compute_control() method
            plant: Plant dynamics with step() method
            initial_state: Initial system state
            duration: Simulation duration (seconds)
            dt: Timestep (seconds)
            target_state: Target equilibrium state (default: zeros)

        Returns:
            SimulationResult with metrics and trajectories
        """
        # Setup
        if target_state is None:
            target_state = np.zeros_like(initial_state)

        num_steps = int(duration / dt)
        state = initial_state.copy()
        last_control = np.zeros(1)  # Scalar control for DIP

        # Storage
        time_array = np.zeros(num_steps)
        state_trajectory = np.zeros((num_steps, len(state)))
        control_trajectory = np.zeros(num_steps)

        # Apply parametric faults to controller/plant at initialization
        if self._parametric_faults:
            # This is a simplified approach - real implementation would modify
            # controller gains or plant parameters before simulation loop
            pass

        # Initialize controller state and history
        controller_state = None
        history = {}

        # Simulation loop
        for step in range(num_steps):
            current_time = step * dt
            time_array[step] = current_time

            # 1. Sensor faults: corrupt state measurement
            state_measured = state.copy()
            for sensor_fault in self._sensor_faults:
                if sensor_fault.enabled:
                    state_measured = sensor_fault.inject(state_measured)

            # 2. Compute control
            control_output = controller.compute_control(
                state_measured,
                controller_state,
                history
            )

            # Extract control value from controller output
            # Controllers return a NamedTuple with (u, state, history)
            control_commanded = control_output.u

            # Update controller state and history for next iteration
            controller_state = control_output.state
            history = control_output.history

            # Handle array/scalar control output
            if isinstance(control_commanded, np.ndarray):
                control_commanded = control_commanded.item() if control_commanded.size == 1 else control_commanded[0]

            # 3. Actuator faults: corrupt control command
            control_actual = control_commanded
            for actuator_fault in self._actuator_faults:
                if actuator_fault.enabled:
                    control_actual = actuator_fault.inject(
                        np.array([control_actual]),
                        dt=dt
                    )
                    if isinstance(control_actual, np.ndarray):
                        control_actual = control_actual.item()

            # 4. Environmental faults: add disturbances
            for env_fault in self._environmental_faults:
                if env_fault.enabled:
                    control_with_disturbance = env_fault.inject(
                        np.array([control_actual]),
                        time=current_time
                    )
                    if isinstance(control_with_disturbance, np.ndarray):
                        control_actual = control_with_disturbance.item()

            # 5. Step plant dynamics
            state = plant.step(state, control_actual, dt)

            # Store results
            state_trajectory[step] = state
            control_trajectory[step] = control_actual
            last_control = np.array([control_actual])

        # Compute performance metrics
        settling_time = self._compute_settling_time(
            time_array, state_trajectory, target_state
        )
        overshoot = self._compute_overshoot(state_trajectory, target_state)
        energy = self._compute_energy(control_trajectory, dt)
        stability = self._check_stability(state_trajectory)

        # Create result
        result = SimulationResult(
            scenario_name=self.name,
            controller_name=controller.__class__.__name__,
            timestamp=time.time(),
            settling_time=settling_time,
            overshoot=overshoot,
            energy=energy,
            stability=stability,
            time_array=time_array,
            state_trajectory=state_trajectory,
            control_trajectory=control_trajectory,
            faults_applied=self.get_fault_names()
        )

        return result

    def _compute_settling_time(
        self,
        time_array: np.ndarray,
        state_trajectory: np.ndarray,
        target_state: np.ndarray,
        threshold: float = 0.02
    ) -> float:
        """
        Compute settling time (time to reach ±2% of target).

        Args:
            time_array: Time samples
            state_trajectory: State trajectory
            target_state: Target state
            threshold: Settling threshold (default 2%)

        Returns:
            Settling time in seconds (inf if never settles)
        """
        # Focus on angle states (first 2 states: theta1, theta2)
        angle_errors = np.abs(state_trajectory[:, :2] - target_state[:2])
        max_angle_error = np.max(angle_errors, axis=1)

        # Find first time when error stays below threshold
        tolerance = threshold * np.pi  # 2% of pi radians
        settled_mask = max_angle_error < tolerance

        # Find first index where settled
        settled_indices = np.where(settled_mask)[0]
        if len(settled_indices) == 0:
            return np.inf  # Never settled

        # Check if it stays settled (no more violations after first settled point)
        first_settled_idx = settled_indices[0]
        if np.all(settled_mask[first_settled_idx:]):
            return time_array[first_settled_idx]
        else:
            return np.inf  # Settled but then left region

    def _compute_overshoot(
        self,
        state_trajectory: np.ndarray,
        target_state: np.ndarray
    ) -> float:
        """
        Compute maximum overshoot (%).

        Args:
            state_trajectory: State trajectory
            target_state: Target state

        Returns:
            Overshoot percentage
        """
        # Focus on angle states
        angle_errors = np.abs(state_trajectory[:, :2] - target_state[:2])
        max_error = np.max(angle_errors)
        overshoot_pct = (max_error / np.pi) * 100.0  # As % of pi radians
        return overshoot_pct

    def _compute_energy(
        self,
        control_trajectory: np.ndarray,
        dt: float
    ) -> float:
        """
        Compute control energy (integral of u^2).

        Args:
            control_trajectory: Control trajectory
            dt: Timestep

        Returns:
            Total energy
        """
        energy = np.sum(control_trajectory ** 2) * dt
        return energy

    def _check_stability(
        self,
        state_trajectory: np.ndarray,
        threshold: float = 1e3
    ) -> bool:
        """
        Check if system remained stable (no divergence).

        Args:
            state_trajectory: State trajectory
            threshold: Divergence threshold

        Returns:
            True if stable, False if diverged
        """
        max_state = np.max(np.abs(state_trajectory))
        return max_state < threshold

    def reset_all_faults(self):
        """Reset all stateful faults (lag filters, dropout memory, etc.)."""
        for fault in self.get_all_faults():
            if hasattr(fault, 'reset_state'):
                fault.reset_state()
