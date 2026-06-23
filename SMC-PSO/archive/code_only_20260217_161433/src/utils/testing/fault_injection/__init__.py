"""
Fault Injection Framework for Robustness Testing

This package provides chaos testing capabilities for validating controller
robustness under sensor faults, actuator limitations, parameter variations,
and environmental disturbances.

Main Components:
- FaultInjector: Base class for all fault injectors
- FaultModels: Concrete implementations of specific faults
- FaultScenario: Composer for multi-fault scenarios
- Config: YAML-based configuration loader

Usage:
    from src.utils.testing.fault_injection import (
        GaussianNoiseFault,
        SaturationFault,
        FaultScenario
    )

    scenario = FaultScenario(name="stress_test")
    scenario.add_sensor_fault(GaussianNoiseFault(snr_db=30))
    scenario.add_actuator_fault(SaturationFault(limit_pct=80))

    results = scenario.run_simulation(controller, plant, initial_state)
"""

from .fault_injector import (
    FaultInjector,
    SensorFaultInjector,
    ActuatorFaultInjector,
    ParametricFaultInjector,
    EnvironmentalFaultInjector
)

from .fault_models import (
    GaussianNoiseFault,
    BiasFault,
    DropoutFault,
    QuantizationFault,
    SaturationFault,
    DeadZoneFault,
    LagFault,
    JitterFault,
    GainErrorFault,
    SystemUncertaintyFault,
    DriftFault,
    DisturbanceFault
)

from .fault_scenario import (
    FaultScenario,
    SimulationResult
)

from .config import (
    load_fault_scenario,
    FaultScenarioConfig
)

__all__ = [
    # Base classes
    'FaultInjector',
    'SensorFaultInjector',
    'ActuatorFaultInjector',
    'ParametricFaultInjector',
    'EnvironmentalFaultInjector',

    # Sensor faults
    'GaussianNoiseFault',
    'BiasFault',
    'DropoutFault',
    'QuantizationFault',

    # Actuator faults
    'SaturationFault',
    'DeadZoneFault',
    'LagFault',
    'JitterFault',

    # Parameter variations
    'GainErrorFault',
    'SystemUncertaintyFault',
    'DriftFault',

    # Environmental
    'DisturbanceFault',

    # Scenario management
    'FaultScenario',
    'SimulationResult',

    # Configuration
    'load_fault_scenario',
    'FaultScenarioConfig'
]

__version__ = '1.0.0'
