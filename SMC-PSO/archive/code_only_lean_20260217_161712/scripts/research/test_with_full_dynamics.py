#!/usr/bin/env python3
"""Test MT-8 ROBUST_GAINS with FULL dynamics (as they were optimized)."""

import sys
import numpy as np
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import load_config
from src.core.dynamics import DIPDynamics
from src.controllers.factory import create_controller

ROBUST_GAINS = [10.149, 12.839, 6.815, 2.75]
DT = 0.01
SIM_DURATION = 10.0

def main():
    print("="*70)
    print("TEST: MT-8 ROBUST_GAINS with FULL DIPDynamics")
    print(f"(Same config as MT-8 optimization)")
    print("="*70)

    np.random.seed(42)
    config = load_config()

    # Use FULL dynamics (like MT-8)
    dynamics = DIPDynamics(config.physics)

    # Create controller
    controller = create_controller(
        'hybrid_adaptive_sta_smc',
        config=config,
        gains=ROBUST_GAINS
    )

    # IC like MT-8 (0.1 rad for both angles)
    ic = np.array([0, 0.1, 0.1, 0, 0, 0])

    print(f"\nSimulating: IC={ic}, Duration={SIM_DURATION}s")
    print(f"Dynamics: FULL DIPDynamics (config.physics)")
    print(f"Controller: hybrid_adaptive_sta_smc, gains={ROBUST_GAINS}")

    t = 0.0
    state = ic.copy()
    n_steps = int(SIM_DURATION / DT)
    step = 0

    state_history = [state.copy()]

    while step < n_steps:
        # Compute control
        u = controller.compute_control(state, state_vars=None, history=None)
        u_val = float(u.u) if hasattr(u, 'u') else float(u)
        u_val = np.clip(u_val, -150.0, 150.0)

        # Dynamics step
        xdot = dynamics.compute_dynamics(state, u_val)

        # Check for divergence
        if np.any(np.abs(xdot) > 1000):
            print(f"\n[FAIL] Diverged at t={t:.3f}s (xdot exploded)")
            print(f"  Final state: {state}")
            print(f"  xdot: {xdot}")
            return False

        state = state + xdot * DT

        # Check state bounds
        if np.any(np.abs(state) > 100):
            print(f"\n[FAIL] Diverged at t={t:.3f}s (state too large)")
            print(f"  Final state: {state}")
            return False

        state_history.append(state.copy())
        t += DT
        step += 1

    print(f"\n[OK] SUCCESS! Completed {SIM_DURATION}s")
    final_state = state_history[-1]
    print(f"Final state: x={final_state[0]:.3f}, th1={final_state[1]:.3f}, th2={final_state[2]:.3f}")
    print(f"  (Angles: {np.rad2deg(final_state[1]):.1f}°, {np.rad2deg(final_state[2]):.1f}°)")
    return True


if __name__ == "__main__":
    success = main()
    print("\n" + "="*70)
    if success:
        print("CONCLUSION: MT-8 gains WORK with FULL dynamics!")
        print("Problem was using SimplifiedDIPDynamics instead of DIPDynamics")
    else:
        print("CONCLUSION: MT-8 gains FAIL even with FULL dynamics")
        print("Deeper issue with controller implementation")
    print("="*70)
