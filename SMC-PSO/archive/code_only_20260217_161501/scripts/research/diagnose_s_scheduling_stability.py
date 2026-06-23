#!/usr/bin/env python3
"""
Diagnostic script to investigate why HybridWithSScheduling fails in PSO optimization.

Tests baseline controller stability with various fixed s-threshold combinations
to determine if the problem is:
1. Controller/scheduler implementation bug
2. PSO search space being wrong
3. Dynamics model issues
4. ROBUST_GAINS being inappropriate

Author: Research Phase 4.1
Date: 2025-11-09
"""

import sys
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.plant.models.simplified.config import SimplifiedDIPConfig
from src.plant.models.simplified.dynamics import SimplifiedDIPDynamics
from src.controllers.smc.hybrid_adaptive_sta_smc import HybridAdaptiveSTASMC
from src.controllers.scheduling.sliding_surface_scheduler import SlidingSurfaceAdaptiveScheduler
from src.controllers.hybrid_scheduling import HybridWithSScheduling
from src.core.simulation_runner import SimulationRunner


# ROBUST_GAINS from MT-8 Enhancement #3 (same as PSO script)
ROBUST_GAINS = np.array([10.149, 12.839, 6.815, 2.75])  # [c1, lambda1, c2, lambda2]


def safe_print(msg):
    """Windows-safe printing (no Unicode emojis)."""
    try:
        print(msg)
    except UnicodeEncodeError:
        # Strip non-ASCII characters
        print(msg.encode('ascii', 'ignore').decode('ascii'))


def run_single_test(s_aggressive, s_conservative, test_name="Test"):
    """
    Run a single simulation with fixed s-thresholds.

    Returns:
        tuple: (success: bool, final_time: float, max_state_norm: float)
    """
    safe_print(f"\n{'='*80}")
    safe_print(f"{test_name}: s_aggressive={s_aggressive:.2f}, s_conservative={s_conservative:.2f}")
    safe_print(f"{'='*80}")

    # Create dynamics
    dip_config = SimplifiedDIPConfig.create_default()
    dynamics = SimplifiedDIPDynamics(dip_config)

    # Create scheduler
    scheduler = SlidingSurfaceAdaptiveScheduler(
        s_aggressive=s_aggressive,
        s_conservative=s_conservative,
        aggressive_scale=0.8,
        conservative_scale=1.2
    )

    # Create controller
    controller = HybridWithSScheduling(
        scheduler=scheduler,
        gains=ROBUST_GAINS
    )

    # Initial conditions: small perturbation from upright
    x0 = np.array([
        0.0,     # cart position
        0.05,    # theta1 (5 deg ~= 0.087 rad, using 0.05)
        0.03,    # theta2 (3 deg ~= 0.052 rad, using 0.03)
        0.0,     # cart velocity
        0.0,     # theta1_dot
        0.0      # theta2_dot
    ])

    # Simulation parameters
    dt = 0.01
    T = 10.0

    # Run simulation
    runner = SimulationRunner(controller, dynamics, dt=dt)

    try:
        result = runner.run(
            x0=x0,
            T=T,
            show_progress=False,
            return_full_history=True
        )

        # Analyze results
        states = np.array(result.history['state'])
        times = np.array(result.history['time'])

        # Check if simulation completed
        if len(times) < int(T / dt):
            safe_print(f"[FAIL] Simulation diverged at t={times[-1]:.3f}s (expected {T:.1f}s)")
            max_norm = np.max(np.linalg.norm(states, axis=1))
            safe_print(f"       Max state norm: {max_norm:.2e}")

            # Show state at divergence
            final_state = states[-1]
            safe_print(f"       Final state: x={final_state[0]:.3f}, th1={final_state[1]:.3f}, th2={final_state[2]:.3f}")

            return False, times[-1], max_norm
        else:
            safe_print(f"[OK] Simulation completed successfully!")

            # Show final state
            final_state = states[-1]
            max_norm = np.max(np.linalg.norm(states, axis=1))
            safe_print(f"     Final state: x={final_state[0]:.3f}, th1={final_state[1]:.3f}, th2={final_state[2]:.3f}")
            safe_print(f"     Max state norm: {max_norm:.2f}")

            # Show settling time
            position_errors = np.abs(states[:, 0])
            angle1_errors = np.abs(states[:, 1])
            angle2_errors = np.abs(states[:, 2])

            settling_threshold = 0.01
            settled_idx = None
            for i in range(len(times)):
                if (position_errors[i] < settling_threshold and
                    angle1_errors[i] < settling_threshold and
                    angle2_errors[i] < settling_threshold):
                    if settled_idx is None:
                        settled_idx = i
                else:
                    settled_idx = None

            if settled_idx is not None:
                safe_print(f"     Settling time: {times[settled_idx]:.3f}s")

            return True, times[-1], max_norm

    except Exception as e:
        safe_print(f"[ERROR] Exception occurred: {e}")
        return False, 0.0, float('inf')


def main():
    """Run diagnostic tests with various s-threshold combinations."""

    safe_print("\n" + "="*80)
    safe_print("DIAGNOSTIC: HybridWithSScheduling Stability Analysis")
    safe_print("="*80)
    safe_print(f"Controller gains: {ROBUST_GAINS}")
    safe_print(f"Dynamics: SimplifiedDIPDynamics (default config)")
    safe_print(f"Initial conditions: x=[0, 0.05, 0.03, 0, 0, 0] (small perturbation)")
    safe_print("="*80)

    # Test cases: various s-threshold combinations
    test_cases = [
        # (s_aggressive, s_conservative, description)
        (50.0, 2.5, "PSO Middle Point"),  # Middle of PSO search space
        (10.0, 1.0, "Conservative Both"),
        (20.0, 0.5, "Moderate Aggressive, Low Conservative"),
        (5.0, 0.1, "PSO Lower Bounds"),
        (100.0, 5.0, "PSO Upper Bounds"),
        (30.0, 3.0, "Balanced High"),
        (15.0, 1.5, "Balanced Medium"),
        (8.0, 0.3, "Balanced Low"),
    ]

    results = []

    for i, (s_agg, s_cons, desc) in enumerate(test_cases, 1):
        success, final_t, max_norm = run_single_test(
            s_agg, s_cons,
            f"Test {i}/{len(test_cases)}: {desc}"
        )
        results.append((desc, s_agg, s_cons, success, final_t, max_norm))

    # Summary
    safe_print("\n" + "="*80)
    safe_print("SUMMARY OF RESULTS")
    safe_print("="*80)

    successes = [r for r in results if r[3]]
    failures = [r for r in results if not r[3]]

    safe_print(f"\nSuccessful: {len(successes)}/{len(test_cases)}")
    safe_print(f"Failed:     {len(failures)}/{len(test_cases)}")

    if successes:
        safe_print("\n[OK] Successful configurations:")
        for desc, s_agg, s_cons, _, final_t, max_norm in successes:
            safe_print(f"  - {desc:30s} | s_agg={s_agg:6.2f}, s_cons={s_cons:5.2f} | max_norm={max_norm:7.2f}")

    if failures:
        safe_print("\n[FAIL] Failed configurations:")
        for desc, s_agg, s_cons, _, final_t, max_norm in failures:
            safe_print(f"  - {desc:30s} | s_agg={s_agg:6.2f}, s_cons={s_cons:5.2f} | diverged at t={final_t:.3f}s")

    # Diagnostic conclusions
    safe_print("\n" + "="*80)
    safe_print("DIAGNOSTIC CONCLUSIONS")
    safe_print("="*80)

    if len(successes) == 0:
        safe_print("\n[CRITICAL] NO configurations stabilized the system!")
        safe_print("This suggests:")
        safe_print("  1. ROBUST_GAINS may not be suitable for HybridWithSScheduling")
        safe_print("  2. SlidingSurfaceAdaptiveScheduler implementation may have bugs")
        safe_print("  3. SimplifiedDIPDynamics may have issues")
        safe_print("  4. HybridWithSScheduling controller logic may be incorrect")
        safe_print("\nRecommended next steps:")
        safe_print("  - Test baseline HybridAdaptiveSTASMC (without s-scheduling)")
        safe_print("  - Test classical_smc with same dynamics")
        safe_print("  - Review scheduler implementation")
    elif len(successes) < len(test_cases) // 2:
        safe_print("\n[WARNING] Only some configurations work!")
        safe_print("This suggests:")
        safe_print("  1. PSO search bounds may be too wide")
        safe_print("  2. Some s-threshold ranges are inherently unstable")
        safe_print("\nRecommended next steps:")
        safe_print("  - Narrow PSO search bounds to successful region")
        safe_print("  - Add constraints to PSO to avoid unstable regions")
    else:
        safe_print("\n[OK] Most configurations work!")
        safe_print("This suggests:")
        safe_print("  1. PSO search may be hitting edge cases")
        safe_print("  2. PSO may need more particles/iterations")
        safe_print("  3. Cost function may be guiding PSO to unstable regions")
        safe_print("\nRecommended next steps:")
        safe_print("  - Increase PSO particles (10 -> 20)")
        safe_print("  - Review cost function implementation")
        safe_print("  - Add stability checks to cost function")

    safe_print("="*80)


if __name__ == "__main__":
    main()
