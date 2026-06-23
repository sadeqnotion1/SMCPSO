"""
Memory leak detection script using tracemalloc.

This script runs 1000 simulation cycles for each controller type and tracks
memory allocations to identify potential leaks.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import tracemalloc
import gc
import json
from datetime import datetime
import numpy as np

from src.controllers.factory import create_controller
from src.config import load_config
from src.plant.models.lowrank.dynamics import LowRankDIPDynamics
from src.plant.models.lowrank.config import LowRankDIPConfig
from src.simulation.engines.simulation_runner import run_simulation


def detect_leaks(controller_type: str, num_cycles: int = 1000, dt: float = 0.01, sim_time: float = 0.5):
    """
    Detect memory leaks for a specific controller type.

    Parameters
    ----------
    controller_type : str
        Controller type (classical_smc, sta_smc, adaptive_smc, hybrid_adaptive_sta_smc)
    num_cycles : int
        Number of simulation cycles to run
    dt : float
        Timestep for simulation
    sim_time : float
        Duration of each simulation

    Returns
    -------
    dict
        Memory leak detection results
    """
    print(f"\n[INFO] Starting leak detection for {controller_type}...")
    print(f"[INFO] Cycles: {num_cycles}, dt: {dt}, sim_time: {sim_time}")

    # Load configuration
    config = load_config("config.yaml")

    # Extract gains for controller
    if controller_type == "classical_smc":
        gains = config.controller_defaults.classical_smc.gains
    elif controller_type == "sta_smc":
        gains = config.controller_defaults.sta_smc.gains
    elif controller_type == "adaptive_smc":
        gains = config.controller_defaults.adaptive_smc.gains
    elif controller_type == "hybrid_adaptive_sta_smc":
        gains = config.controller_defaults.hybrid_adaptive_sta_smc.gains
    else:
        raise ValueError(f"Unknown controller type: {controller_type}")

    # Create dynamics model
    dip_config = LowRankDIPConfig()
    dynamics = LowRankDIPDynamics(dip_config)

    # Initial state
    initial_state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])

    # Start memory tracking
    tracemalloc.start()

    # Baseline snapshot
    gc.collect()
    snapshot_start = tracemalloc.take_snapshot()
    start_current, start_peak = tracemalloc.get_traced_memory()

    # Memory snapshots at intervals
    snapshots = {
        0: {'current': start_current / 1024 / 1024, 'peak': start_peak / 1024 / 1024}
    }

    # Run simulation cycles
    for i in range(num_cycles):
        # Create controller
        controller = create_controller(controller_type, config=config, gains=gains)

        # Run simulation
        try:
            t_arr, x_arr, u_arr = run_simulation(
                controller=controller,
                dynamics_model=dynamics,
                sim_time=sim_time,
                dt=dt,
                initial_state=initial_state,
                u_max=20.0
            )
        except Exception as e:
            print(f"[ERROR] Simulation failed at cycle {i}: {e}")
            continue

        # Delete controller
        del controller

        # Force garbage collection every 100 cycles
        if (i + 1) % 100 == 0:
            gc.collect()

        # Take snapshots at intervals
        if (i + 1) in [100, 500, 1000]:
            current, peak = tracemalloc.get_traced_memory()
            snapshots[i + 1] = {
                'current': current / 1024 / 1024,
                'peak': peak / 1024 / 1024
            }
            print(f"[INFO] Cycle {i + 1}/{num_cycles}: Current={current / 1024 / 1024:.2f} MB, Peak={peak / 1024 / 1024:.2f} MB")

    # Final snapshot
    gc.collect()
    snapshot_end = tracemalloc.take_snapshot()
    end_current, end_peak = tracemalloc.get_traced_memory()

    # Analyze memory diff
    top_stats = snapshot_end.compare_to(snapshot_start, 'lineno')

    # Extract top 10 allocations
    top_allocations = []
    for stat in top_stats[:10]:
        top_allocations.append({
            'file': str(stat.traceback),
            'size_diff_mb': stat.size_diff / 1024 / 1024,
            'count_diff': stat.count_diff
        })

    # Stop memory tracking
    tracemalloc.stop()

    # Calculate growth rate
    total_growth_mb = (end_current - start_current) / 1024 / 1024
    growth_per_cycle_kb = (total_growth_mb * 1024) / num_cycles

    # Compile results
    results = {
        'controller_type': controller_type,
        'num_cycles': num_cycles,
        'dt': dt,
        'sim_time': sim_time,
        'timestamp': datetime.now().isoformat(),
        'memory_snapshots': snapshots,
        'start_memory_mb': start_current / 1024 / 1024,
        'end_memory_mb': end_current / 1024 / 1024,
        'peak_memory_mb': end_peak / 1024 / 1024,
        'total_growth_mb': total_growth_mb,
        'growth_per_cycle_kb': growth_per_cycle_kb,
        'top_allocations': top_allocations,
        'verdict': 'LEAK DETECTED' if growth_per_cycle_kb > 5.0 else 'OK'
    }

    print(f"\n[RESULTS] {controller_type}:")
    print(f"  Start memory: {start_current / 1024 / 1024:.2f} MB")
    print(f"  End memory: {end_current / 1024 / 1024:.2f} MB")
    print(f"  Total growth: {total_growth_mb:.2f} MB")
    print(f"  Growth per cycle: {growth_per_cycle_kb:.2f} KB")
    print(f"  Verdict: {results['verdict']}")

    return results


def main():
    """Run leak detection for all controllers."""
    print("[INFO] CA-02 Phase 2: Memory Leak Detection")
    print("[INFO] =" * 40)

    controller_types = [
        'classical_smc',
        'sta_smc',
        'adaptive_smc',
        'hybrid_adaptive_sta_smc'
    ]

    all_results = {}

    for ctrl_type in controller_types:
        try:
            results = detect_leaks(ctrl_type, num_cycles=1000, dt=0.01, sim_time=0.5)
            all_results[ctrl_type] = results
        except Exception as e:
            print(f"[ERROR] Failed to detect leaks for {ctrl_type}: {e}")
            all_results[ctrl_type] = {'error': str(e)}

    # Save results to JSON
    output_dir = Path(__file__).parent
    output_file = output_dir / "leak_detection_results.json"

    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n[INFO] Results saved to: {output_file}")

    # Summary
    print("\n[SUMMARY] Leak Detection Results:")
    print("=" * 80)
    for ctrl_type, results in all_results.items():
        if 'error' in results:
            print(f"{ctrl_type:30s} ERROR: {results['error']}")
        else:
            verdict = results['verdict']
            growth = results['growth_per_cycle_kb']
            print(f"{ctrl_type:30s} {verdict:15s} {growth:10.2f} KB/cycle")
    print("=" * 80)


if __name__ == "__main__":
    main()
