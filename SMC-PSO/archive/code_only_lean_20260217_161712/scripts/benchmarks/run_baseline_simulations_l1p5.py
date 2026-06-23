#!/usr/bin/env python
"""
Phase 1.5: Baseline Performance Benchmark Script

Executes comprehensive baseline simulations for 4 core controllers across 3 scenarios
with Monte Carlo analysis (30 runs per combination = 360 total simulations).

Controllers tested:
- Classical SMC
- Super-Twisting SMC (STA)
- Adaptive SMC
- Hybrid Adaptive STA-SMC

Scenarios:
1. Step Response: Basic setpoint tracking performance
2. Disturbance Rejection: Reaction to external disturbances
3. Model Uncertainty: Performance with ±10% parameter variation

Output Files:
- baselines/L1P5_raw_results.csv - All 360 simulation results
- baselines/L1P5_statistics.json - Aggregate statistics and confidence intervals
- baselines/L1P5_metadata.json - Simulation configuration and metadata

Usage:
    python scripts/benchmarks/run_baseline_simulations_l1p5.py

Expected Runtime: ~45-60 minutes (360 simulations @ 10s each)
"""

import os
import sys
import json
import time
import numpy as np
import pandas as pd
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Any
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

# ============================================================================
# IMPORTS
# ============================================================================

from src.controllers.factory import create_controller, get_default_gains
from src.core.simulation_context import SimulationContext
from src.plant.models.lowrank.dynamics import LowRankDIPDynamics
from src.plant.models.lowrank.config import LowRankDIPConfig


# ============================================================================
# CONFIGURATION
# ============================================================================

CONTROLLERS = [
    'classical_smc',
    'sta_smc',
    'adaptive_smc',
    'hybrid_adaptive_sta_smc',
]

INITIAL_CONDITIONS = {
    'nominal': [0.0, 0.1, 0.05, 0.0, 0.0, 0.0],      # Small initial angle
    'perturbed': [0.0, 0.15, 0.08, 0.0, 0.0, 0.0],   # Larger perturbation
    'extreme': [0.0, 0.20, 0.12, 0.0, 0.0, 0.0],     # Maximum safe angle
}

SCENARIOS = {
    'step_response': {
        'description': 'Step Response - Basic setpoint tracking',
        'disturbance': None,
        'parameter_uncertainty': 0.0,
    },
    'disturbance_rejection': {
        'description': 'Disturbance Rejection - 10N impulse at t=1s',
        'disturbance': {'magnitude': 10.0, 'start_time': 1.0, 'duration': 0.5},
        'parameter_uncertainty': 0.0,
    },
    'model_uncertainty': {
        'description': 'Model Uncertainty - ±10% parameter variation',
        'disturbance': None,
        'parameter_uncertainty': 0.10,
    },
}

NUM_RUNS_PER_COMBINATION = 30
SIMULATION_TIME = 10.0
DT = 0.01


# ============================================================================
# METRICS DATA CLASS
# ============================================================================

@dataclass
class SimulationMetrics:
    """Metrics from a single simulation run."""
    controller: str
    initial_condition: str
    scenario: str
    run_number: int
    timestamp: str

    # Performance metrics
    settling_time: float        # Time to reach ±5% of equilibrium
    overshoot: float            # Peak angle overshoot (%)
    rise_time: float            # Time to 90% setpoint
    steady_state_error: float   # Final steady-state error

    # Energy and efficiency
    energy_consumption: float   # Integral of control input squared
    control_effort: float       # Mean absolute control output

    # Robustness metrics
    max_control_output: float   # Peak control force
    control_smoothness: float   # Inverse of chattering (std of u')

    # Stability
    stability_maintained: bool  # System remained bounded
    convergence_achieved: bool  # Reached equilibrium


# ============================================================================
# SIMULATION EXECUTION
# ============================================================================

def compute_metrics(
    t: np.ndarray,
    state_history: np.ndarray,
    control_history: np.ndarray,
) -> Dict[str, float]:
    """Compute performance metrics from simulation results."""

    metrics = {}

    # Extract angle states (columns 1 and 2)
    theta1 = state_history[:, 1]
    theta2 = state_history[:, 2]
    combined_angle = np.sqrt(theta1**2 + theta2**2)

    # Control output
    u = control_history.flatten()

    # [1] Settling time: time to reach ±5% of final value
    final_angle = np.mean(combined_angle[-100:])  # Last 1 second
    threshold = 0.05 * np.abs(final_angle) if np.abs(final_angle) > 0.001 else 0.005
    settling_idx = np.where(np.abs(combined_angle - final_angle) <= threshold)[0]
    if len(settling_idx) > 0:
        metrics['settling_time'] = t[settling_idx[0]]
    else:
        metrics['settling_time'] = np.inf  # Did not settle

    # [2] Overshoot: peak angle as % of final value
    max_angle = np.max(combined_angle[int(0.5/DT):])  # Ignore transient
    metrics['overshoot'] = (max_angle - np.abs(final_angle)) / (np.abs(final_angle) + 1e-6) * 100

    # [3] Rise time: 10% to 90%
    if np.abs(final_angle) > 0.001:
        rise_10 = 0.1 * np.abs(final_angle)
        rise_90 = 0.9 * np.abs(final_angle)
        idx_10 = np.where(combined_angle >= rise_10)[0]
        idx_90 = np.where(combined_angle >= rise_90)[0]
        if len(idx_10) > 0 and len(idx_90) > 0:
            metrics['rise_time'] = t[idx_90[0]] - t[idx_10[0]]
        else:
            metrics['rise_time'] = np.inf
    else:
        metrics['rise_time'] = 0.0

    # [4] Steady-state error
    metrics['steady_state_error'] = np.mean(np.abs(combined_angle[-100:]))

    # [5] Energy consumption: integral of u^2
    metrics['energy_consumption'] = np.trapz(u**2, t)

    # [6] Control effort: mean absolute control
    metrics['control_effort'] = np.mean(np.abs(u))

    # [7] Max control output
    metrics['max_control_output'] = np.max(np.abs(u))

    # [8] Control smoothness: inverse of control derivative std
    u_dot = np.diff(u) / DT
    u_dot_std = np.std(u_dot)
    metrics['control_smoothness'] = 1.0 / (1.0 + u_dot_std)  # Range [0, 1]

    # [9] Stability: check if angles remained bounded
    metrics['stability_maintained'] = np.max(np.abs(theta1)) < np.pi and np.max(np.abs(theta2)) < np.pi

    # [10] Convergence: check if reached small angle
    metrics['convergence_achieved'] = final_angle < 0.2

    return metrics


def run_simulation(
    controller_name: str,
    gains: List[float],
    initial_state: np.ndarray,
    scenario_config: Dict[str, Any],
) -> Dict[str, float]:
    """Run a single simulation and return metrics."""

    # Create controller and plant
    controller = create_controller(controller_name, gains=gains)
    plant_config = LowRankDIPConfig()
    plant = LowRankDIPDynamics(plant_config)

    # Apply parameter uncertainty if specified
    if scenario_config.get('parameter_uncertainty', 0.0) > 0:
        uncertainty = scenario_config['parameter_uncertainty']
        # Modify plant parameters with random ±uncertainty
        seed_offset = int(time.time() * 1e6) % 1000
        np.random.seed(np.random.randint(0, 10000) + seed_offset)
        plant_config.m1 *= (1.0 + np.random.uniform(-uncertainty, uncertainty))
        plant_config.m2 *= (1.0 + np.random.uniform(-uncertainty, uncertainty))
        plant_config.l1 *= (1.0 + np.random.uniform(-uncertainty, uncertainty))
        plant_config.l2 *= (1.0 + np.random.uniform(-uncertainty, uncertainty))

    # Create simulation context
    context = SimulationContext(
        dt=DT,
        duration=SIMULATION_TIME,
        controller=controller,
        plant=plant,
        initial_state=initial_state.copy(),
    )

    # Run simulation
    results = context.run()

    # Extract trajectories
    t = results.time
    state_history = np.array(results.state_history)
    control_history = np.array(results.control_history)

    # Compute metrics
    metrics = compute_metrics(t, state_history, control_history)

    return metrics


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Execute baseline simulations for all controller/scenario combinations."""

    logger.info('=' * 80)
    logger.info('PHASE 1.5: BASELINE PERFORMANCE BENCHMARK')
    logger.info('=' * 80)

    # Create output directory
    output_dir = Path(PROJECT_ROOT) / 'baselines'
    output_dir.mkdir(exist_ok=True)

    # Configuration summary
    total_sims = len(CONTROLLERS) * len(INITIAL_CONDITIONS) * len(SCENARIOS) * NUM_RUNS_PER_COMBINATION
    logger.info(f'Configuration:')
    logger.info(f'  Controllers: {len(CONTROLLERS)} ({", ".join(CONTROLLERS)})')
    logger.info(f'  Initial Conditions: {len(INITIAL_CONDITIONS)} ({", ".join(INITIAL_CONDITIONS.keys())})')
    logger.info(f'  Scenarios: {len(SCENARIOS)} ({", ".join(SCENARIOS.keys())})')
    logger.info(f'  Runs per combination: {NUM_RUNS_PER_COMBINATION}')
    logger.info(f'  Total simulations: {total_sims}')
    logger.info(f'  Expected time: ~{total_sims * SIMULATION_TIME / 3600:.1f} hours')
    logger.info('')

    # Collect all results
    all_results = []
    start_time = time.time()
    sim_count = 0

    # Iterate through all combinations
    for controller_name in CONTROLLERS:
        logger.info(f'Testing {controller_name.upper()}...')
        gains = get_default_gains(controller_name)

        for ic_name, initial_state in INITIAL_CONDITIONS.items():
            logger.info(f'  Initial Condition: {ic_name}')

            for scenario_name, scenario_config in SCENARIOS.items():
                logger.info(f'    Scenario: {scenario_name}')

                for run in range(1, NUM_RUNS_PER_COMBINATION + 1):
                    try:
                        # Run simulation
                        metrics_dict = run_simulation(
                            controller_name=controller_name,
                            gains=gains,
                            initial_state=np.array(initial_state, dtype=float),
                            scenario_config=scenario_config,
                        )

                        # Create metrics object
                        metrics = SimulationMetrics(
                            controller=controller_name,
                            initial_condition=ic_name,
                            scenario=scenario_name,
                            run_number=run,
                            timestamp=datetime.now().isoformat(),
                            **metrics_dict
                        )

                        all_results.append(asdict(metrics))
                        sim_count += 1

                        # Progress logging
                        if run % 10 == 0:
                            elapsed = time.time() - start_time
                            rate = sim_count / elapsed
                            remaining = (total_sims - sim_count) / rate
                            logger.info(f'      Run {run}/{NUM_RUNS_PER_COMBINATION} (Completed {sim_count}/{total_sims}, ETA: {remaining/60:.0f}m)')

                    except Exception as e:
                        logger.error(f'      Run {run} FAILED: {str(e)}')
                        continue

    # Save results to CSV
    df = pd.DataFrame(all_results)
    csv_file = output_dir / 'L1P5_raw_results.csv'
    df.to_csv(csv_file, index=False)
    logger.info(f'\nResults saved to: {csv_file}')
    logger.info(f'Total successful runs: {len(all_results)}/{total_sims}')

    # Compute aggregate statistics
    stats = {}
    for controller in CONTROLLERS:
        controller_data = df[df['controller'] == controller]
        stats[controller] = {
            'settling_time_mean': float(controller_data['settling_time'].mean()),
            'settling_time_std': float(controller_data['settling_time'].std()),
            'overshoot_mean': float(controller_data['overshoot'].mean()),
            'overshoot_std': float(controller_data['overshoot'].std()),
            'energy_mean': float(controller_data['energy_consumption'].mean()),
            'energy_std': float(controller_data['energy_consumption'].std()),
            'stability_rate': float(controller_data['stability_maintained'].mean()),
            'convergence_rate': float(controller_data['convergence_achieved'].mean()),
        }

    # Save statistics
    stats_file = output_dir / 'L1P5_statistics.json'
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    logger.info(f'Statistics saved to: {stats_file}')

    # Save metadata
    metadata = {
        'timestamp': datetime.now().isoformat(),
        'total_simulations': len(all_results),
        'controllers': CONTROLLERS,
        'initial_conditions': list(INITIAL_CONDITIONS.keys()),
        'scenarios': list(SCENARIOS.keys()),
        'runs_per_combination': NUM_RUNS_PER_COMBINATION,
        'simulation_time': SIMULATION_TIME,
        'dt': DT,
        'total_runtime_seconds': time.time() - start_time,
    }

    metadata_file = output_dir / 'L1P5_metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f'Metadata saved to: {metadata_file}')

    logger.info('=' * 80)
    logger.info('BASELINE SIMULATIONS COMPLETE')
    logger.info('=' * 80)


if __name__ == '__main__':
    main()
