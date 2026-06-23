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

    def _initialize_controller_context(self, controller: Any) -> Tuple[Any, Dict[str, Any]]:
        """Initialize controller state/history when optional hooks are available."""
        controller_state = None
        history: Dict[str, Any] = {}

        if hasattr(controller, 'initialize_state'):
            try:
                controller_state = controller.initialize_state()
            except Exception:
                controller_state = None

        if hasattr(controller, 'initialize_history'):
            try:
                initialized = controller.initialize_history()
                if isinstance(initialized, dict):
                    history = initialized
            except Exception:
                history = {}

        return controller_state, history

    def _normalize_controller_output(
        self,
        control_output: Any,
        controller_state: Any,
        history: Dict[str, Any]
    ) -> Tuple[float, Any, Dict[str, Any]]:
        """
        Normalize controller outputs across legacy and modular interfaces.

        Supported output shapes:
        - NamedTuple/object with attributes: u, state, history
        - dict with key 'u' and optional 'state'/'history'
        - tuple/list with [u, state, history] or [u, ...]
        - np.ndarray or scalar control value
        """
        next_state = controller_state
        next_history = history if isinstance(history, dict) else {}
        control_value: Any = 0.0

        if hasattr(control_output, 'u'):
            control_value = getattr(control_output, 'u', 0.0)
            next_state = getattr(control_output, 'state', controller_state)
            candidate_history = getattr(control_output, 'history', next_history)
            if isinstance(candidate_history, dict):
                next_history = candidate_history
        elif isinstance(control_output, dict):
            control_value = control_output.get('u', 0.0)
            next_state = control_output.get('state', controller_state)
            candidate_history = control_output.get('history', next_history)
            if isinstance(candidate_history, dict):
                next_history = candidate_history
        elif isinstance(control_output, (tuple, list)):
            if len(control_output) >= 1:
                control_value = control_output[0]
            if len(control_output) >= 2:
                next_state = control_output[1]
            if len(control_output) >= 3 and isinstance(control_output[2], dict):
                next_history = control_output[2]
        else:
            control_value = control_output

        if isinstance(control_value, np.ndarray):
            control_scalar = float(control_value.item()) if control_value.size == 1 else float(control_value.flat[0])
        else:
            try:
                control_scalar = float(control_value)
            except (TypeError, ValueError):
                control_scalar = 0.0

        return control_scalar, next_state, next_history

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

        # Ensure each simulation run starts from clean controller/fault state.
        if hasattr(controller, 'reset'):
            try:
                controller.reset()
            except Exception:
                pass
        elif hasattr(controller, 'reset_all_controllers'):
            try:
                controller.reset_all_controllers()
            except Exception:
                pass

        self.reset_all_faults()

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
        controller_state, history = self._initialize_controller_context(controller)

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

            # Normalize control output and update controller context for next step
            control_commanded, controller_state, history = self._normalize_controller_output(
                control_output, controller_state, history
            )

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
        # Focus on pendulum angle states: theta1 and theta2 (indices 1 and 2).
        # Fall back to first two states for non-standard low-dimensional inputs.
        if state_trajectory.ndim != 2 or state_trajectory.size == 0:
            return np.inf
        if state_trajectory.shape[1] >= 3 and target_state.shape[0] >= 3:
            angle_errors = np.abs(state_trajectory[:, [1, 2]] - target_state[[1, 2]])
        elif state_trajectory.shape[1] >= 2 and target_state.shape[0] >= 2:
            angle_errors = np.abs(state_trajectory[:, :2] - target_state[:2])
        else:
            return np.inf
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
        # Focus on pendulum angle states: theta1 and theta2 (indices 1 and 2).
        if state_trajectory.ndim != 2 or state_trajectory.size == 0:
            return float('inf')
        if state_trajectory.shape[1] >= 3 and target_state.shape[0] >= 3:
            angle_errors = np.abs(state_trajectory[:, [1, 2]] - target_state[[1, 2]])
        elif state_trajectory.shape[1] >= 2 and target_state.shape[0] >= 2:
            angle_errors = np.abs(state_trajectory[:, :2] - target_state[:2])
        else:
            return float('inf')
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
        if state_trajectory.ndim != 2 or state_trajectory.size == 0:
            return False

        if not np.all(np.isfinite(state_trajectory)):
            return False

        max_state = float(np.max(np.abs(state_trajectory)))
        if max_state >= threshold:
            return False

        # Additional DIP-aware sanity bounds. These are tighter than the legacy
        # global threshold while still allowing transient swings.
        if state_trajectory.shape[1] >= 6:
            max_cart = float(np.max(np.abs(state_trajectory[:, 0])))
            max_angles = float(np.max(np.abs(state_trajectory[:, [1, 2]])))
            max_velocities = float(np.max(np.abs(state_trajectory[:, 3:6])))

            if max_cart > 20.0:
                return False
            if max_angles > (2.0 * np.pi):
                return False
            if max_velocities > 100.0:
                return False

        return True

    def reset_all_faults(self):
        """Reset all stateful faults (lag filters, dropout memory, etc.)."""
        for fault in self.get_all_faults():
            if hasattr(fault, 'reset_state'):
                fault.reset_state()
