#!/usr/bin/env python3
"""Test baseline HybridAdaptiveSTASMC WITHOUT s-scheduling."""

import sys
import numpy as np
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.plant.models.simplified.config import SimplifiedDIPConfig
from src.plant.models.simplified.dynamics import SimplifiedDIPDynamics
from src.controllers.smc.hybrid_adaptive_sta_smc import HybridAdaptiveSTASMC
from src.config import load_config

ROBUST_GAINS = [10.149, 12.839, 6.815, 2.75]
DT = 0.01
SIM_DURATION = 10.0

def main():
    print("="*70)
    print("BASELINE TEST: HybridAdaptiveSTASMC (NO scheduling)")
    print(f"Gains: {ROBUST_GAINS}, Duration: {SIM_DURATION}s")
    print("="*70)

    np.random.seed(42)
    config = load_config()
    dip_config = SimplifiedDIPConfig.create_default()
    dynamics = SimplifiedDIPDynamics(dip_config)

    controller = HybridAdaptiveSTASMC(
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

    ic = np.array([0.0, 0.05, 0.03, 0.0, 0.0, 0.0])

    t = 0.0
    state = ic.copy()
    u_last = 0.0

    while t < SIM_DURATION:
        # Compute control (HybridAdaptiveSTASMC expects 3 args)
        output = controller.compute_control(state, state_vars=None, history=None)
        u = float(output.u)
        u = np.clip(u, -20.0, 20.0)

        # Dynamics
        result = dynamics.compute_dynamics(state, np.array([u]))

        if not result.success or len(result.state_derivative) == 0:
            print(f"\n[FAIL] Diverged at t={t:.3f}s")
            print(f"Final state: {state}")
            return

        state = state + result.state_derivative * DT
        t += DT

    print(f"\n[OK] SUCCESS! Completed {SIM_DURATION}s")
    print(f"Final state: x={state[0]:.3f}, th1={state[1]:.3f}, th2={state[2]:.3f}")

if __name__ == "__main__":
    main()
