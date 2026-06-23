"""
History list leak detection script using tracemalloc.

This script runs 1000 simulation steps with the SAME controller instance
to detect unbounded history list growth (identified in Phase 1).
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


def detect_history_leaks(controller_type: str, num_steps: int = 1000, dt: float = 0.01):
    """
    Detect history list leaks by running continuous simulation with SAME controller.

    Parameters
    ----------
    controller_type : str
        Controller type
    num_steps : int
        Number of simulation steps (NOT cycles)
    dt : float
        Timestep

    Returns
    -------
    dict
        History leak detection results
    """
    print(f"\n[INFO] Starting history leak detection for {controller_type}...")
    print(f"[INFO] Steps: {num_steps}, dt: {dt}")

    # Load configuration
    config = load_config("config.yaml")

    # Extract gains
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

    # Create controller ONCE (not recreated each step)
    controller = create_controller(controller_type, config=config, gains=gains)

    # Initialize controller state
    if hasattr(controller, 'initialize_state'):
        state_vars = controller.initialize_state()
    else:
        state_vars = None

    if hasattr(controller, 'initialize_history'):
        history = controller.initialize_history()
    else:
        history = None

    # Initial state
    state = np.array([0.0, 0.1, 0.1, 0.0, 0.0, 0.0])

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

    # Run simulation steps (SAME controller)
    for i in range(num_steps):
        # Compute control
        try:
            if hasattr(controller, 'compute_control'):
                result = controller.compute_control(state, state_vars, history)
                # Extract control, state_vars, history from result
                if isinstance(result, tuple):
                    if len(result) == 3:
                        u, state_vars, history = result
                    else:
                        u = result[0]
                else:
                    u = result
            else:
                u = controller(i * dt, state)
        except Exception as e:
            print(f"[ERROR] Control computation failed at step {i}: {e}")
            break

        # Saturate control
        u = np.clip(u, -20.0, 20.0)

        # Step dynamics
        try:
            state_next = dynamics.step(state, u, dt)
            state = np.asarray(state_next, dtype=float).reshape(-1)
        except Exception as e:
            print(f"[ERROR] Dynamics step failed at step {i}: {e}")
            break

        # Take snapshots at intervals
        if (i + 1) in [100, 500, 1000]:
            gc.collect()
            current, peak = tracemalloc.get_traced_memory()
            snapshots[i + 1] = {
                'current': current / 1024 / 1024,
                'peak': peak / 1024 / 1024
            }
            print(f"[INFO] Step {i + 1}/{num_steps}: Current={current / 1024 / 1024:.2f} MB, Peak={peak / 1024 / 1024:.2f} MB")

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
    growth_per_step_kb = (total_growth_mb * 1024) / num_steps

    # Inspect controller internals for history sizes
    history_sizes = {}
    if hasattr(controller, 'control_history'):
        history_sizes['control_history'] = len(controller.control_history)
    if hasattr(controller, 'switching_history'):
        history_sizes['switching_history'] = len(controller.switching_history)
    if hasattr(controller, '_control_history'):
        history_sizes['_control_history'] = len(controller._control_history)
    if hasattr(controller, '_adaptation_history'):
        history_sizes['_adaptation_history'] = len(controller._adaptation_history)

    # Compile results
    results = {
        'controller_type': controller_type,
        'num_steps': num_steps,
        'dt': dt,
        'timestamp': datetime.now().isoformat(),
        'memory_snapshots': snapshots,
        'start_memory_mb': start_current / 1024 / 1024,
        'end_memory_mb': end_current / 1024 / 1024,
        'peak_memory_mb': end_peak / 1024 / 1024,
        'total_growth_mb': total_growth_mb,
        'growth_per_step_kb': growth_per_step_kb,
        'history_sizes': history_sizes,
        'top_allocations': top_allocations,
        'verdict': 'LEAK DETECTED' if growth_per_step_kb > 5.0 else 'OK'
    }

    print(f"\n[RESULTS] {controller_type}:")
    print(f"  Start memory: {start_current / 1024 / 1024:.2f} MB")
    print(f"  End memory: {end_current / 1024 / 1024:.2f} MB")
    print(f"  Total growth: {total_growth_mb:.2f} MB")
    print(f"  Growth per step: {growth_per_step_kb:.2f} KB")
    print(f"  History sizes: {history_sizes}")
    print(f"  Verdict: {results['verdict']}")

    # Cleanup
    if hasattr(controller, 'cleanup'):
        controller.cleanup()

    return results


def main():
    """Run history leak detection for all controllers."""
    print("[INFO] CA-02 Phase 2: History List Leak Detection")
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
            results = detect_history_leaks(ctrl_type, num_steps=1000, dt=0.01)
            all_results[ctrl_type] = results
        except Exception as e:
            print(f"[ERROR] Failed to detect history leaks for {ctrl_type}: {e}")
            import traceback
            traceback.print_exc()
            all_results[ctrl_type] = {'error': str(e)}

    # Save results to JSON
    output_dir = Path(__file__).parent
    output_file = output_dir / "history_leak_detection_results.json"

    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n[INFO] Results saved to: {output_file}")

    # Summary
    print("\n[SUMMARY] History Leak Detection Results:")
    print("=" * 80)
    for ctrl_type, results in all_results.items():
        if 'error' in results:
            print(f"{ctrl_type:30s} ERROR: {results['error']}")
        else:
            verdict = results['verdict']
            growth = results['growth_per_step_kb']
            history_sizes = results.get('history_sizes', {})
            history_str = ', '.join([f"{k}={v}" for k, v in history_sizes.items()])
            print(f"{ctrl_type:30s} {verdict:15s} {growth:10.2f} KB/step [{history_str}]")
    print("=" * 80)


if __name__ == "__main__":
    main()
