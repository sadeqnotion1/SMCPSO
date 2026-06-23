#!/usr/bin/env python3
#======================================================================================\\
#=============== scripts/benchmarks/validate_mt7_robust_pso.py ========================\\
#======================================================================================\\

"""
MT-7 Validation Script: Robust PSO vs Standard PSO Overfitting Test

Validates that robust multi-scenario PSO addresses the MT-7 overfitting issue where
standard PSO gains trained on small perturbations (±0.05 rad) show 50.4x chattering
degradation on realistic perturbations (±0.3 rad).

Target: Reduce degradation from 50.4x to <5x

Test Protocol:
- 500 simulations per configuration (10,000 total simulations)
- Test controllers: classical_smc, sta_smc (most chattering-sensitive)
- Metrics: Chattering index, success rate, settling time
- Conditions: Nominal (±0.05 rad) vs Realistic (±0.3 rad)

Expected Results:
- Standard PSO: ~50x degradation nominal→realistic
- Robust PSO: <5x degradation nominal→realistic
- Success rate: >90% on realistic conditions (vs ~10% for standard)

Usage:
    python scripts/benchmarks/validate_mt7_robust_pso.py --controller classical_smc
    python scripts/benchmarks/validate_mt7_robust_pso.py --controller sta_smc --n-runs 1000
    python scripts/benchmarks/validate_mt7_robust_pso.py --quick-test  # 50 runs only
"""

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import matplotlib.pyplot as plt

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import load_config
from src.controllers.factory import create_controller
from src.simulation.engines.vector_sim import simulate_system_batch
from src.utils.analysis.chattering_metrics import (
    compute_chattering_index,
    compute_control_rate_std
)


logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# Data Structures
# ------------------------------------------------------------------------------

@dataclass
class SimulationResult:
    """Single simulation result."""
    chattering_index: float
    control_rate_std: float
    settling_time: float
    max_angle_error: float
    success: bool  # Angles < 0.5 rad at end
    final_state: np.ndarray


@dataclass
class ConditionResults:
    """Results for one condition (nominal or realistic)."""
    condition_name: str
    n_runs: int
    mean_chattering: float
    std_chattering: float
    median_chattering: float
    p95_chattering: float
    success_rate: float
    mean_settling_time: float
    results: List[SimulationResult]


@dataclass
class ValidationReport:
    """Complete validation report."""
    controller: str
    standard_pso_nominal: ConditionResults
    standard_pso_realistic: ConditionResults
    robust_pso_nominal: ConditionResults
    robust_pso_realistic: ConditionResults
    standard_degradation: float  # realistic/nominal ratio
    robust_degradation: float
    improvement_factor: float  # standard_deg / robust_deg
    target_met: bool  # robust_deg < 5.0
    timestamp: str
    n_runs_per_condition: int
    total_simulations: int


# ------------------------------------------------------------------------------
# Simulation Functions
# ------------------------------------------------------------------------------

def generate_initial_conditions(
    n_samples: int,
    angle_range: float,
    seed: int
) -> List[np.ndarray]:
    """Generate diverse initial conditions.

    Parameters
    ----------
    n_samples : int
        Number of ICs to generate
    angle_range : float
        Maximum angle perturbation (rad)
    seed : int
        Random seed

    Returns
    -------
    ics : List[np.ndarray]
        Initial condition arrays [x, θ1, θ2, ẋ, θ̇1, θ̇2]
    """
    rng = np.random.default_rng(seed)
    ics = []

    for _ in range(n_samples):
        ic = np.array([
            0.0,  # Cart at origin
            rng.uniform(-angle_range, angle_range),  # θ1
            rng.uniform(-angle_range, angle_range),  # θ2
            0.0,  # At rest (no velocities)
            0.0,
            0.0
        ])
        ics.append(ic)

    return ics


def run_simulation_batch(
    controller_factory,
    gains: np.ndarray,
    initial_conditions: List[np.ndarray],
    config,
    sim_duration: float = 10.0,
    dt: float = 0.01
) -> List[SimulationResult]:
    """Run batch simulation and compute metrics.

    Parameters
    ----------
    controller_factory : callable
        Factory to create controller from gains
    gains : np.ndarray
        Controller gains
    initial_conditions : List[np.ndarray]
        Initial conditions to test
    config : ConfigSchema
        System configuration
    sim_duration : float
        Simulation duration (s)
    dt : float
        Time step (s)

    Returns
    -------
    results : List[SimulationResult]
        Simulation results with metrics
    """
    results = []

    for ic in initial_conditions:
        # Run simulation with IC override
        # NOTE: Pass controller_factory directly (it will be called internally for each particle)
        t, x_traj, u_traj, sigma_traj = simulate_system_batch(
            controller_factory=controller_factory,
            particles=gains.reshape(1, -1),
            sim_time=sim_duration,
            dt=dt,
            initial_state=ic,
            u_max=150.0
        )

        # Extract single trajectory (batch size=1)
        x = x_traj[0]  # Shape: (n_steps, 6)
        u = u_traj[0]  # Shape: (n_steps,)

        # Diagnostic check for zero control signal
        if len(u) < 10:
            logger.warning(f"[WARNING] Short control trajectory: {len(u)} steps (expected ~{int(sim_duration/dt)})")
        if np.allclose(u, 0.0):
            logger.warning(f"[WARNING] Zero control signal for IC: {ic[:3]}")  # Only show positions

        # Compute chattering metrics
        chattering_idx = compute_chattering_index(u, dt)
        control_rate_std = compute_control_rate_std(u, dt)

        # Compute settling time (angles < 0.1 rad)
        angles = x[:, 1:3]  # θ1, θ2
        angle_magnitudes = np.abs(angles).max(axis=1)
        settled_indices = np.where(angle_magnitudes < 0.1)[0]
        settling_time = t[settled_indices[0]] if len(settled_indices) > 0 else sim_duration

        # Check success (final angles < 0.5 rad)
        final_angles = x[-1, 1:3]
        max_angle_error = np.abs(final_angles).max()
        success = max_angle_error < 0.5

        results.append(SimulationResult(
            chattering_index=chattering_idx,
            control_rate_std=control_rate_std,
            settling_time=settling_time,
            max_angle_error=max_angle_error,
            success=success,
            final_state=x[-1]
        ))

    return results


def aggregate_results(
    results: List[SimulationResult],
    condition_name: str
) -> ConditionResults:
    """Aggregate simulation results into summary statistics.

    Parameters
    ----------
    results : List[SimulationResult]
        Individual simulation results
    condition_name : str
        Name of condition (e.g., "Nominal ±0.05 rad")

    Returns
    -------
    summary : ConditionResults
        Aggregated statistics
    """
    chattering_values = np.array([r.chattering_index for r in results])
    success_count = sum(1 for r in results if r.success)
    settling_times = np.array([r.settling_time for r in results])

    return ConditionResults(
        condition_name=condition_name,
        n_runs=len(results),
        mean_chattering=float(np.mean(chattering_values)),
        std_chattering=float(np.std(chattering_values)),
        median_chattering=float(np.median(chattering_values)),
        p95_chattering=float(np.percentile(chattering_values, 95)),
        success_rate=success_count / len(results),
        mean_settling_time=float(np.mean(settling_times)),
        results=results
    )


# ------------------------------------------------------------------------------
# Validation Workflow
# ------------------------------------------------------------------------------

def validate_mt7_robust_pso(
    controller_name: str,
    standard_pso_gains: np.ndarray,
    robust_pso_gains: np.ndarray,
    config,
    n_runs: int = 500,
    seed: int = 42
) -> ValidationReport:
    """Run complete MT-7 validation comparing standard vs robust PSO.

    Parameters
    ----------
    controller_name : str
        Controller type ("classical_smc" or "sta_smc")
    standard_pso_gains : np.ndarray
        Gains from standard PSO (trained on ±0.05 rad)
    robust_pso_gains : np.ndarray
        Gains from robust PSO (trained on diverse scenarios)
    config : ConfigSchema
        System configuration
    n_runs : int
        Number of runs per condition (default 500)
    seed : int
        Random seed for reproducibility

    Returns
    -------
    report : ValidationReport
        Complete validation results
    """
    logger.info(f"[INFO] Starting MT-7 validation for {controller_name}")
    logger.info(f"[INFO] Runs per condition: {n_runs} (Total: {n_runs * 4} simulations)")

    # Create dynamics model (required by simulate_system_batch)
    from src.plant.models.simplified.dynamics import SimplifiedDIPDynamics
    from src.plant.models.simplified.config import SimplifiedDIPConfig

    dip_config = SimplifiedDIPConfig.create_default()
    dynamics = SimplifiedDIPDynamics(dip_config)

    # Controller factory with dynamics_model attribute
    def controller_factory(gains):
        controller = create_controller(controller_name, config=config, gains=gains)
        controller.dynamics_model = dynamics  # Required by simulate_system_batch
        return controller

    # Generate initial conditions
    logger.info("[INFO] Generating initial conditions...")
    nominal_ics = generate_initial_conditions(n_runs, angle_range=0.05, seed=seed)
    realistic_ics = generate_initial_conditions(n_runs, angle_range=0.3, seed=seed + 1000)

    # Test 1: Standard PSO on Nominal (±0.05 rad)
    logger.info("[INFO] Test 1/4: Standard PSO on Nominal conditions (±0.05 rad)")
    start_time = time.time()
    std_nominal_results = run_simulation_batch(
        controller_factory, standard_pso_gains, nominal_ics, config
    )
    logger.info(f"[INFO] Completed in {time.time() - start_time:.1f}s")

    # Test 2: Standard PSO on Realistic (±0.3 rad)
    logger.info("[INFO] Test 2/4: Standard PSO on Realistic conditions (±0.3 rad)")
    start_time = time.time()
    std_realistic_results = run_simulation_batch(
        controller_factory, standard_pso_gains, realistic_ics, config
    )
    logger.info(f"[INFO] Completed in {time.time() - start_time:.1f}s")

    # Test 3: Robust PSO on Nominal (±0.05 rad)
    logger.info("[INFO] Test 3/4: Robust PSO on Nominal conditions (±0.05 rad)")
    start_time = time.time()
    robust_nominal_results = run_simulation_batch(
        controller_factory, robust_pso_gains, nominal_ics, config
    )
    logger.info(f"[INFO] Completed in {time.time() - start_time:.1f}s")

    # Test 4: Robust PSO on Realistic (±0.3 rad)
    logger.info("[INFO] Test 4/4: Robust PSO on Realistic conditions (±0.3 rad)")
    start_time = time.time()
    robust_realistic_results = run_simulation_batch(
        controller_factory, robust_pso_gains, realistic_ics, config
    )
    logger.info(f"[INFO] Completed in {time.time() - start_time:.1f}s")

    # Aggregate results
    logger.info("[INFO] Aggregating results...")
    std_nominal = aggregate_results(std_nominal_results, "Standard PSO - Nominal (±0.05 rad)")
    std_realistic = aggregate_results(std_realistic_results, "Standard PSO - Realistic (±0.3 rad)")
    robust_nominal = aggregate_results(robust_nominal_results, "Robust PSO - Nominal (±0.05 rad)")
    robust_realistic = aggregate_results(robust_realistic_results, "Robust PSO - Realistic (±0.3 rad)")

    # Compute degradation ratios with zero-division guards
    if std_nominal.mean_chattering < 1e-9:
        logger.warning("[WARNING] Standard PSO nominal chattering near zero - using penalty value")
        standard_degradation = float('inf')
    else:
        standard_degradation = std_realistic.mean_chattering / std_nominal.mean_chattering

    if robust_nominal.mean_chattering < 1e-9:
        logger.warning("[WARNING] Robust PSO nominal chattering near zero - using penalty value")
        robust_degradation = float('inf')
    else:
        robust_degradation = robust_realistic.mean_chattering / robust_nominal.mean_chattering

    # Compute improvement factor with guards
    if robust_degradation < 1e-9:
        improvement_factor = float('inf')
    elif standard_degradation == float('inf'):
        improvement_factor = float('inf')
    else:
        improvement_factor = standard_degradation / robust_degradation

    target_met = robust_degradation < 5.0

    # Create report
    report = ValidationReport(
        controller=controller_name,
        standard_pso_nominal=std_nominal,
        standard_pso_realistic=std_realistic,
        robust_pso_nominal=robust_nominal,
        robust_pso_realistic=robust_realistic,
        standard_degradation=standard_degradation,
        robust_degradation=robust_degradation,
        improvement_factor=improvement_factor,
        target_met=target_met,
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        n_runs_per_condition=n_runs,
        total_simulations=n_runs * 4
    )

    logger.info("[INFO] Validation complete!")
    return report


# ------------------------------------------------------------------------------
# Reporting & Visualization
# ------------------------------------------------------------------------------

def print_validation_report(report: ValidationReport):
    """Print human-readable validation report.

    Parameters
    ----------
    report : ValidationReport
        Validation results
    """
    print("\n" + "=" * 80)
    print(f"MT-7 VALIDATION REPORT: {report.controller}")
    print("=" * 80)
    print(f"Timestamp: {report.timestamp}")
    print(f"Total Simulations: {report.total_simulations} ({report.n_runs_per_condition} per condition)")
    print()

    # Standard PSO Results
    print("STANDARD PSO (trained on ±0.05 rad)")
    print("-" * 80)
    print(f"Nominal (±0.05 rad):")
    print(f"  Chattering: {report.standard_pso_nominal.mean_chattering:.4f} ± {report.standard_pso_nominal.std_chattering:.4f}")
    print(f"  Success Rate: {report.standard_pso_nominal.success_rate * 100:.1f}%")
    print(f"Realistic (±0.3 rad):")
    print(f"  Chattering: {report.standard_pso_realistic.mean_chattering:.4f} ± {report.standard_pso_realistic.std_chattering:.4f}")
    print(f"  Success Rate: {report.standard_pso_realistic.success_rate * 100:.1f}%")
    print(f"DEGRADATION: {report.standard_degradation:.2f}x")
    print()

    # Robust PSO Results
    print("ROBUST PSO (trained on diverse scenarios)")
    print("-" * 80)
    print(f"Nominal (±0.05 rad):")
    print(f"  Chattering: {report.robust_pso_nominal.mean_chattering:.4f} ± {report.robust_pso_nominal.std_chattering:.4f}")
    print(f"  Success Rate: {report.robust_pso_nominal.success_rate * 100:.1f}%")
    print(f"Realistic (±0.3 rad):")
    print(f"  Chattering: {report.robust_pso_realistic.mean_chattering:.4f} ± {report.robust_pso_realistic.std_chattering:.4f}")
    print(f"  Success Rate: {report.robust_pso_realistic.success_rate * 100:.1f}%")
    print(f"DEGRADATION: {report.robust_degradation:.2f}x")
    print()

    # Summary
    print("SUMMARY")
    print("-" * 80)
    print(f"Improvement Factor: {report.improvement_factor:.2f}x")
    print(f"  (Standard degradation / Robust degradation)")
    print(f"Target (<5x degradation): {'[OK] PASS' if report.target_met else '[ERROR] FAIL'}")
    print(f"MT-7 Issue Resolved: {'YES' if report.target_met else 'NO'}")
    print("=" * 80 + "\n")


def save_validation_report(report: ValidationReport, output_dir: Path):
    """Save validation report to JSON file.

    Parameters
    ----------
    report : ValidationReport
        Validation results
    output_dir : Path
        Output directory
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"mt7_validation_{report.controller}_{timestamp}.json"

    # Convert to dict (excluding full result lists for size)
    report_dict = {
        "controller": report.controller,
        "timestamp": report.timestamp,
        "n_runs_per_condition": report.n_runs_per_condition,
        "total_simulations": report.total_simulations,
        "standard_pso_nominal": {
            "condition_name": report.standard_pso_nominal.condition_name,
            "mean_chattering": report.standard_pso_nominal.mean_chattering,
            "std_chattering": report.standard_pso_nominal.std_chattering,
            "success_rate": report.standard_pso_nominal.success_rate,
        },
        "standard_pso_realistic": {
            "condition_name": report.standard_pso_realistic.condition_name,
            "mean_chattering": report.standard_pso_realistic.mean_chattering,
            "std_chattering": report.standard_pso_realistic.std_chattering,
            "success_rate": report.standard_pso_realistic.success_rate,
        },
        "robust_pso_nominal": {
            "condition_name": report.robust_pso_nominal.condition_name,
            "mean_chattering": report.robust_pso_nominal.mean_chattering,
            "std_chattering": report.robust_pso_nominal.std_chattering,
            "success_rate": report.robust_pso_nominal.success_rate,
        },
        "robust_pso_realistic": {
            "condition_name": report.robust_pso_realistic.condition_name,
            "mean_chattering": report.robust_pso_realistic.mean_chattering,
            "std_chattering": report.robust_pso_realistic.std_chattering,
            "success_rate": report.robust_pso_realistic.success_rate,
        },
        "standard_degradation": report.standard_degradation,
        "robust_degradation": report.robust_degradation,
        "improvement_factor": report.improvement_factor,
        "target_met": report.target_met,
    }

    with open(output_path, 'w') as f:
        json.dump(report_dict, f, indent=2)

    logger.info(f"[OK] Report saved: {output_path}")


# ------------------------------------------------------------------------------
# CLI Entry Point
# ------------------------------------------------------------------------------

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="MT-7 Validation: Robust PSO vs Standard PSO Overfitting Test"
    )
    parser.add_argument(
        "--controller",
        type=str,
        default="classical_smc",
        choices=["classical_smc", "sta_smc"],
        help="Controller type to test (default: classical_smc)"
    )
    parser.add_argument(
        "--n-runs",
        type=int,
        default=500,
        help="Number of runs per condition (default: 500, total 2000 sims)"
    )
    parser.add_argument(
        "--quick-test",
        action="store_true",
        help="Quick test mode: 50 runs per condition (200 sims total)"
    )
    parser.add_argument(
        "--standard-gains",
        type=str,
        default=None,
        help="Path to standard PSO gains JSON file (default: use config defaults)"
    )
    parser.add_argument(
        "--robust-gains",
        type=str,
        default=None,
        help="Path to robust PSO gains JSON file (REQUIRED if running validation)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=".artifacts/mt7_validation",
        help="Output directory for results (default: .artifacts/mt7_validation)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )

    args = parser.parse_args()

    # Override n_runs if quick test
    if args.quick_test:
        args.n_runs = 50
        logger.info("[INFO] Quick test mode: 50 runs per condition")

    # Load configuration
    config = load_config("config.yaml")

    # Load gains
    if args.standard_gains:
        with open(args.standard_gains, 'r') as f:
            standard_gains_data = json.load(f)
            standard_gains = np.array(standard_gains_data[args.controller])
    else:
        # Use config defaults
        controller_defaults = getattr(config, "controller_defaults", {})
        if hasattr(controller_defaults, args.controller):
            standard_gains = np.array(getattr(controller_defaults, args.controller).gains)
        else:
            logger.error(f"[ERROR] No default gains found for {args.controller}")
            sys.exit(1)

    if args.robust_gains:
        with open(args.robust_gains, 'r') as f:
            robust_gains_data = json.load(f)
            robust_gains = np.array(robust_gains_data[args.controller])
    else:
        logger.error("[ERROR] --robust-gains is required for validation")
        logger.info("[INFO] First run: python simulate.py --controller {args.controller} --run-pso --robust-pso --save gains_robust.json")
        sys.exit(1)

    # Run validation
    report = validate_mt7_robust_pso(
        controller_name=args.controller,
        standard_pso_gains=standard_gains,
        robust_pso_gains=robust_gains,
        config=config,
        n_runs=args.n_runs,
        seed=args.seed
    )

    # Print report
    print_validation_report(report)

    # Save report
    output_dir = Path(args.output_dir)
    save_validation_report(report, output_dir)

    # Exit code based on target
    sys.exit(0 if report.target_met else 1)


if __name__ == "__main__":
    main()
