#!/usr/bin/env python3
"""
Simple baseline test for |s|-based scheduling.

Tests if the HybridWithSScheduling controller can stabilize the system at all
with fixed s-thresholds before trying PSO optimization.

Author: Research Phase 4.1
Date: 2025-11-09
"""

import sys
import numpy as np
from pathlib import Path
from typing import List

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.plant.models.simplified.config import SimplifiedDIPConfig
from src.plant.models.simplified.dynamics import SimplifiedDIPDynamics
from src.controllers.smc.hybrid_adaptive_sta_smc import HybridAdaptiveSTASMC
from src.config import load_config


# ROBUST_GAINS from MT-8 Enhancement #3
ROBUST_GAINS = [10.149, 12.839, 6.815, 2.75]  # [c1, lambda1, c2, lambda2]

# Simulation parameters
DT = 0.01
SIM_DURATION = 10.0


# ============================================================================
# Scheduler and Controller Classes (copied from PSO script)
# ============================================================================

class SlidingSurfaceAdaptiveScheduler:
    """Adaptive gain scheduler based on sliding surface magnitude |s|."""

    def __init__(self, s_aggressive: float, s_conservative: float,
                 aggressive_scale: float = 1.5, conservative_scale: float = 0.5):
        self.s_aggressive = s_aggressive
        self.s_conservative = s_conservative
        self.aggressive_scale = aggressive_scale
        self.conservative_scale = conservative_scale
        self.current_mode = "nominal"
        self.mode_history = []

    def update(self, s: np.ndarray, gains: np.ndarray) -> np.ndarray:
        s_magnitude = np.linalg.norm(s)

        if s_magnitude > self.s_aggressive:
            mode = "aggressive"
            scale = self.aggressive_scale
        elif s_magnitude < self.s_conservative:
            mode = "conservative"
            scale = self.conservative_scale
        else:
            mode = "nominal"
            scale = 1.0

        self.current_mode = mode
        self.mode_history.append(mode)
        return np.array(gains) * scale


class HybridWithSScheduling(HybridAdaptiveSTASMC):
    """Hybrid controller with |s|-based adaptive gain scheduling."""

    def __init__(self, scheduler: SlidingSurfaceAdaptiveScheduler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scheduler = scheduler
        self.s_history = []

    def compute_control(self, state: np.ndarray, last_control: float = 0.0,
                       history: List[np.ndarray] = None) -> float:
        x, theta1, theta2, xdot, theta1dot, theta2dot = state

        # Sliding surface
        s1 = self.c1 * theta1 + theta1dot
        s2 = self.c2 * theta2 + theta2dot
        s = np.array([s1, s2])
        self.s_history.append(np.linalg.norm(s))

        # Get scheduled gains
        base_gains = [self.c1, self.lambda1, self.c2, self.lambda2]
        scheduled_gains = self.scheduler.update(s, base_gains)

        # Temporarily override gains
        original_gains = (self.c1, self.lambda1, self.c2, self.lambda2)
        self.c1, self.lambda1, self.c2, self.lambda2 = scheduled_gains

        # Compute control
        output = super().compute_control(state, state_vars=None, history=None)

        # Restore original gains
        self.c1, self.lambda1, self.c2, self.lambda2 = original_gains

        return float(output.u)


# ============================================================================
# Simulation Function
# ============================================================================

def run_test(s_aggressive, s_conservative, aggressive_scale=0.8, conservative_scale=1.2):
    """Run single test with given s-thresholds."""
    print(f"\n[TEST] s_aggressive={s_aggressive:.2f}, s_conservative={s_conservative:.2f}")
    print(f"       aggressive_scale={aggressive_scale}, conservative_scale={conservative_scale}")

    # Create dynamics
    dip_config = SimplifiedDIPConfig.create_default()
    dynamics = SimplifiedDIPDynamics(dip_config)

    # Create scheduler
    scheduler = SlidingSurfaceAdaptiveScheduler(
        s_aggressive=s_aggressive,
        s_conservative=s_conservative,
        aggressive_scale=aggressive_scale,
        conservative_scale=conservative_scale
    )

    # Create controller
    controller = HybridWithSScheduling(
        scheduler=scheduler,
        gains=ROBUST_GAINS,
        dt=DT,
        max_force=20.0,
        k1_init=15.0,
        k2_init=8.0,
        gamma1=1.0,
        gamma2=1.0,
        dead_zone=0.01,
        dynamics_model=dynamics
    )

    # Initial conditions
    ic = np.array([
        0.0,   # cart_pos
        0.05,  # theta1
        0.03,  # theta2
        0.0,   # cart_vel
        0.0,   # theta1dot
        0.0    # theta2dot
    ])

    # Simulation loop
    state = ic.copy()
    states = [state.copy()]
    times = [0.0]

    t = 0.0
    step = 0
    max_steps = int(SIM_DURATION / DT)

    while step < max_steps:
        # Compute control
        u = controller.compute_control(state)

        # Clip control
        u = np.clip(u, -20.0, 20.0)

        # Dynamics step
        state_dot = dynamics.compute_dynamics(state, u)
        state_dot = np.array(state_dot)  # Convert to array if needed
        state = state + state_dot * DT

        # Check for divergence
        if np.any(np.abs(state) > 100.0):
            print(f"[FAIL] Diverged at t={t:.3f}s, step={step}")
            print(f"       Final state: {state}")
            return False, t

        states.append(state.copy())
        times.append(t)

        t += DT
        step += 1

    print(f"[OK] Completed {SIM_DURATION}s simulation")
    final_state = states[-1]
    print(f"     Final state: x={final_state[0]:.3f}, th1={final_state[1]:.3f}, th2={final_state[2]:.3f}")
    return True, SIM_DURATION


# ============================================================================
# Main
# ============================================================================

def main():
    print("="*80)
    print("BASELINE TEST: HybridWithSScheduling")
    print("="*80)
    print(f"ROBUST_GAINS: {ROBUST_GAINS}")
    print(f"Duration: {SIM_DURATION}s, dt={DT}s")
    print("="*80)

    # Test cases
    tests = [
        (50.0, 2.5, "PSO middle point"),
        (10.0, 1.0, "Conservative both"),
        (20.0, 0.5, "Moderate aggressive, low conservative"),
        (5.0, 0.1, "PSO lower bounds"),
        (100.0, 5.0, "PSO upper bounds"),
    ]

    results = []
    for s_agg, s_cons, desc in tests:
        success, final_t = run_test(s_agg, s_cons)
        results.append((desc, s_agg, s_cons, success, final_t))

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    successes = [r for r in results if r[3]]
    failures = [r for r in results if not r[3]]

    print(f"\nSuccessful: {len(successes)}/{len(results)}")
    print(f"Failed: {len(failures)}/{len(results)}")

    if successes:
        print("\n[OK] Successful configurations:")
        for desc, s_agg, s_cons, _, _ in successes:
            print(f"  - {desc}: s_agg={s_agg}, s_cons={s_cons}")

    if failures:
        print("\n[FAIL] Failed configurations:")
        for desc, s_agg, s_cons, _, final_t in failures:
            print(f"  - {desc}: s_agg={s_agg}, s_cons={s_cons} (diverged at t={final_t:.3f}s)")

    # Conclusion
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    if len(successes) == 0:
        print("[CRITICAL] NO configurations work!")
        print("Problem is likely with:")
        print("  1. Controller implementation (HybridWithSScheduling)")
        print("  2. ROBUST_GAINS being inappropriate")
        print("  3. Dynamics model issues")
    elif len(successes) < len(results) // 2:
        print("[WARNING] Only some configurations work")
        print("PSO search bounds may be too wide")
    else:
        print("[OK] Most configurations work")
        print("PSO may need tuning (more particles, better cost function)")


if __name__ == "__main__":
    main()
