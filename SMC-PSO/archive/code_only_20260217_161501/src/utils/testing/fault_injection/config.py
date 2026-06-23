"""
Configuration loader for fault scenarios.

Supports YAML-based scenario definition with validation.
"""

import yaml
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path

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
from .fault_scenario import FaultScenario


@dataclass
class FaultScenarioConfig:
    """Configuration for a fault scenario."""
    name: str
    description: str = ""
    seed: Optional[int] = None
    sensor_faults: List[Dict[str, Any]] = None
    actuator_faults: List[Dict[str, Any]] = None
    parameter_variations: List[Dict[str, Any]] = None
    disturbances: List[Dict[str, Any]] = None


def load_fault_scenario(config_path: str) -> FaultScenario:
    """
    Load fault scenario from YAML configuration.

    Args:
        config_path: Path to YAML config file

    Returns:
        Configured FaultScenario

    Example YAML:
        scenario:
          name: "stress_test"
          seed: 42
          sensor_faults:
            - type: "gaussian_noise"
              snr_db: 30
              enabled: true
          actuator_faults:
            - type: "saturation"
              limit_pct: 80
              enabled: true
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)

    # Extract scenario section
    scenario_dict = config_dict.get('scenario', config_dict)

    # Create scenario
    scenario = FaultScenario(
        name=scenario_dict.get('name', 'unnamed'),
        seed=scenario_dict.get('seed', None)
    )

    # Add sensor faults
    for fault_cfg in scenario_dict.get('sensor_faults', []):
        if not fault_cfg.get('enabled', True):
            continue

        fault_type = fault_cfg.get('type')
        if fault_type == 'gaussian_noise':
            fault = GaussianNoiseFault(
                snr_db=fault_cfg.get('snr_db', 30.0),
                target=fault_cfg.get('target', 'all_states'),
                seed=scenario.seed
            )
        elif fault_type == 'bias':
            fault = BiasFault(
                bias_magnitude=fault_cfg.get('bias_magnitude', 0.05),
                target=fault_cfg.get('target', 'all_states'),
                seed=scenario.seed
            )
        elif fault_type == 'dropout':
            fault = DropoutFault(
                dropout_rate=fault_cfg.get('dropout_rate', 0.05),
                target=fault_cfg.get('target', 'all_states'),
                seed=scenario.seed
            )
        elif fault_type == 'quantization':
            fault = QuantizationFault(
                bit_depth=fault_cfg.get('bit_depth', 12),
                signal_range=fault_cfg.get('signal_range', 2.0),
                target=fault_cfg.get('target', 'all_states'),
                seed=scenario.seed
            )
        else:
            continue

        scenario.add_sensor_fault(fault)

    # Add actuator faults
    for fault_cfg in scenario_dict.get('actuator_faults', []):
        if not fault_cfg.get('enabled', True):
            continue

        fault_type = fault_cfg.get('type')
        if fault_type == 'saturation':
            fault = SaturationFault(
                limit_pct=fault_cfg.get('limit_pct', 80.0),
                nominal_range=fault_cfg.get('nominal_range', 10.0),
                seed=scenario.seed
            )
        elif fault_type == 'dead_zone':
            fault = DeadZoneFault(
                dead_zone_width=fault_cfg.get('dead_zone_width', 0.1),
                center=fault_cfg.get('center', 0.0),
                seed=scenario.seed
            )
        elif fault_type == 'lag':
            fault = LagFault(
                time_constant=fault_cfg.get('time_constant', 0.02),
                dt=fault_cfg.get('dt', 0.01),
                seed=scenario.seed
            )
        elif fault_type == 'jitter':
            fault = JitterFault(
                jitter_amplitude=fault_cfg.get('jitter_amplitude', 0.05),
                jitter_frequency=fault_cfg.get('jitter_frequency', 50.0),
                seed=scenario.seed
            )
        else:
            continue

        scenario.add_actuator_fault(fault)

    # Add parameter variations
    for fault_cfg in scenario_dict.get('parameter_variations', []):
        if not fault_cfg.get('enabled', True):
            continue

        fault_type = fault_cfg.get('type')
        if fault_type == 'gain_error':
            fault = GainErrorFault(
                tolerance_pct=fault_cfg.get('tolerance_pct', 10.0),
                distribution=fault_cfg.get('distribution', 'uniform'),
                seed=scenario.seed
            )
        elif fault_type == 'system_uncertainty':
            param_variations = {
                k: v for k, v in fault_cfg.items()
                if k not in ['type', 'enabled'] and isinstance(v, (int, float))
            }
            fault = SystemUncertaintyFault(
                param_variations=param_variations,
                seed=scenario.seed
            )
        elif fault_type == 'drift':
            fault = DriftFault(
                drift_rate=fault_cfg.get('drift_rate', 0.01),
                drift_pattern=fault_cfg.get('drift_pattern', 'linear'),
                seed=scenario.seed
            )
        else:
            continue

        scenario.add_parametric_fault(fault)

    # Add environmental disturbances
    for fault_cfg in scenario_dict.get('disturbances', []):
        if not fault_cfg.get('enabled', True):
            continue

        fault = DisturbanceFault(
            disturbance_type=fault_cfg.get('type', 'step'),
            magnitude=fault_cfg.get('magnitude', 0.5),
            frequency=fault_cfg.get('frequency', 2.0),
            start_time=fault_cfg.get('start_time', 1.0),
            end_time=fault_cfg.get('end_time', 5.0),
            seed=scenario.seed
        )
        scenario.add_environmental_fault(fault)

    return scenario
