"""
Memory stress testing script with extended duration.

This script runs 10,000 simulation steps (100 seconds) with SAME controller
to detect unbounded history list growth and generate memory usage plots.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import psutil
import os
import gc
import json
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

from src.controllers.factory import create_controller
from src.config import load_config
from src.plant.models.lowrank.dynamics import LowRankDIPDynamics
from src.plant.models.lowrank.config import LowRankDIPConfig


def stress_test(controller_type: str, num_steps: int = 10000, dt: float = 0.01):
    """
    Stress test memory usage over extended simulation.

    Parameters
    ----------
    controller_type : str
        Controller type
    num_steps : int
        Number of simulation steps
    dt : float
        Timestep

    Returns
    -------
    dict
        Stress test results
    """
    print(f"\n[INFO] Starting stress test for {controller_type}...")
    print(f"[INFO] Steps: {num_steps}, dt: {dt}, duration: {num_steps * dt:.1f}s")

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

    # Create controller ONCE
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

    # Get process for memory monitoring
    process = psutil.Process(os.getpid())

    # Memory samples (collect every 100 steps to avoid overhead)
    memory_samples = []
    step_samples = []

    # Baseline memory
    gc.collect()
    mem_info = process.memory_info()
    baseline_mb = mem_info.rss / 1024 / 1024
    print(f"[INFO] Baseline memory: {baseline_mb:.2f} MB")

    # Run simulation steps
    for i in range(num_steps):
        # Compute control
        try:
            if hasattr(controller, 'compute_control'):
                result = controller.compute_control(state, state_vars, history)
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

        # Sample memory every 100 steps
        if (i + 1) % 100 == 0:
            mem_info = process.memory_info()
            memory_mb = mem_info.rss / 1024 / 1024
            memory_samples.append(memory_mb)
            step_samples.append(i + 1)

            if (i + 1) % 1000 == 0:
                print(f"[INFO] Step {i + 1}/{num_steps}: Memory={memory_mb:.2f} MB ({memory_mb - baseline_mb:+.2f} MB)")

    # Final memory
    gc.collect()
    mem_info = process.memory_info()
    final_mb = mem_info.rss / 1024 / 1024

    # Calculate memory growth
    total_growth_mb = final_mb - baseline_mb
    growth_per_step_kb = (total_growth_mb * 1024) / num_steps

    # Inspect controller internals for history sizes
    history_sizes = {}
    if hasattr(controller, 'control_history'):
        history_sizes['control_history'] = len(controller.control_history)
    if hasattr(controller, 'switching_history'):
        history_sizes['switching_history'] = len(controller.switching_history)
    if hasattr(controller, '_control_history'):
        history_sizes['_control_history'] = len(controller._control_history)

    # Deep inspection of nested components
    if hasattr(controller, 'switching_logic'):
        if hasattr(controller.switching_logic, 'switch_history'):
            history_sizes['switching_logic.switch_history'] = len(controller.switching_logic.switch_history)
        if hasattr(controller.switching_logic, 'performance_history'):
            # performance_history is dict of deques
            total_perf_entries = sum(len(dq) for dq in controller.switching_logic.performance_history.values())
            history_sizes['switching_logic.performance_history'] = total_perf_entries
        if hasattr(controller.switching_logic, 'threshold_adaptation_history'):
            history_sizes['switching_logic.threshold_adaptation_history'] = len(controller.switching_logic.threshold_adaptation_history)

    # Generate plot
    output_dir = Path(__file__).parent
    plot_file = output_dir / f"memory_stress_{controller_type}.png"

    plt.figure(figsize=(10, 6))
    plt.plot(step_samples, memory_samples, linewidth=2)
    plt.xlabel("Simulation Step", fontsize=12)
    plt.ylabel("Memory Usage (MB)", fontsize=12)
    plt.title(f"Memory Stress Test: {controller_type}\n{num_steps} steps, {num_steps * dt:.1f}s duration", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(plot_file, dpi=150)
    plt.close()

    print(f"[INFO] Memory plot saved to: {plot_file}")

    # Compile results
    results = {
        'controller_type': controller_type,
        'num_steps': num_steps,
        'dt': dt,
        'duration_seconds': num_steps * dt,
        'timestamp': datetime.now().isoformat(),
        'baseline_memory_mb': baseline_mb,
        'final_memory_mb': final_mb,
        'total_growth_mb': total_growth_mb,
        'growth_per_step_kb': growth_per_step_kb,
        'peak_memory_mb': max(memory_samples) if memory_samples else final_mb,
        'memory_samples': memory_samples,
        'step_samples': step_samples,
        'history_sizes': history_sizes,
        'verdict': 'LEAK DETECTED' if growth_per_step_kb > 1.0 else 'OK'
    }

    print(f"\n[RESULTS] {controller_type}:")
    print(f"  Baseline memory: {baseline_mb:.2f} MB")
    print(f"  Final memory: {final_mb:.2f} MB")
    print(f"  Total growth: {total_growth_mb:.2f} MB")
    print(f"  Growth per step: {growth_per_step_kb:.2f} KB")
    print(f"  History sizes: {history_sizes}")
    print(f"  Verdict: {results['verdict']}")

    # Cleanup
    if hasattr(controller, 'cleanup'):
        controller.cleanup()

    return results


def main():
    """Run stress tests for all controllers."""
    print("[INFO] CA-02 Phase 3: Memory Stress Testing")
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
            results = stress_test(ctrl_type, num_steps=10000, dt=0.01)
            all_results[ctrl_type] = results
        except Exception as e:
            print(f"[ERROR] Failed stress test for {ctrl_type}: {e}")
            import traceback
            traceback.print_exc()
            all_results[ctrl_type] = {'error': str(e)}

    # Save results to JSON
    output_dir = Path(__file__).parent
    output_file = output_dir / "stress_test_results.json"

    # Convert memory_samples and step_samples to lists (not numpy arrays) for JSON
    for ctrl_type, results in all_results.items():
        if 'memory_samples' in results:
            results['memory_samples'] = [float(x) for x in results['memory_samples']]
        if 'step_samples' in results:
            results['step_samples'] = [int(x) for x in results['step_samples']]

    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n[INFO] Results saved to: {output_file}")

    # Summary
    print("\n[SUMMARY] Stress Test Results (10,000 steps):")
    print("=" * 80)
    for ctrl_type, results in all_results.items():
        if 'error' in results:
            print(f"{ctrl_type:30s} ERROR: {results['error']}")
        else:
            verdict = results['verdict']
            growth = results['growth_per_step_kb']
            total = results['total_growth_mb']
            history_sizes = results.get('history_sizes', {})
            history_str = ', '.join([f"{k}={v}" for k, v in history_sizes.items()])
            print(f"{ctrl_type:30s} {verdict:15s} {growth:10.2f} KB/step ({total:6.2f} MB total) [{history_str}]")
    print("=" * 80)


if __name__ == "__main__":
    main()
