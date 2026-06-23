#!/usr/bin/env python3
"""Simple baseline test - copied directly from PSO script structure."""

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

ROBUST_GAINS = [10.149, 12.839, 6.815, 2.75]
DT = 0.01
SIM_DURATION = 10.0
IC_RANGE = 0.05


class SlidingSurfaceAdaptiveScheduler:
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
    def __init__(self, scheduler: SlidingSurfaceAdaptiveScheduler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scheduler = scheduler
        self.s_history = []

    def compute_control(self, state: np.ndarray, last_control: float = 0.0,
                       history: List[np.ndarray] = None) -> float:
        x, theta1, theta2, xdot, theta1dot, theta2dot = state
        s1 = self.c1 * theta1 + theta1dot
        s2 = self.c2 * theta2 + theta2dot
        s = np.array([s1, s2])
        self.s_history.append(np.linalg.norm(s))

        base_gains = [self.c1, self.lambda1, self.c2, self.lambda2]
        scheduled_gains = self.scheduler.update(s, base_gains)

        original_gains = (self.c1, self.lambda1, self.c2, self.lambda2)
        self.c1, self.lambda1, self.c2, self.lambda2 = scheduled_gains

        output = super().compute_control(state, state_vars=None, history=None)

        self.c1, self.lambda1, self.c2, self.lambda2 = original_gains

        return float(output.u)


def run_test(s_aggressive, s_conservative):
    """Run simulation - copied from PSO script."""
    print(f"\n[TEST] s_agg={s_aggressive:.1f}, s_cons={s_conservative:.1f}")

    config = load_config()
    dip_config = SimplifiedDIPConfig.create_default()
    dynamics = SimplifiedDIPDynamics(dip_config)

    scheduler = SlidingSurfaceAdaptiveScheduler(
        s_aggressive=s_aggressive,
        s_conservative=s_conservative,
        aggressive_scale=0.8,
        conservative_scale=1.2
    )

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

    ic = np.array([
        0.0,
        np.random.uniform(-IC_RANGE, IC_RANGE),
        np.random.uniform(-IC_RANGE, IC_RANGE),
        0.0,
        0.0,
        0.0
    ])

    # Simulation loop (copied from PSO script lines 251-286)
    t = 0.0
    state = ic.copy()
    u_last = 0.0

    while t < SIM_DURATION:
        u = controller.compute_control(state, u_last, None)
        u = np.clip(u, -20.0, 20.0)

        # Dynamics (expects control as array, returns DynamicsResult)
        result = dynamics.compute_dynamics(state, np.array([u]))

        if not result.success or len(result.state_derivative) == 0:
            print(f"  [FAIL] Diverged at t={t:.3f}s (dynamics failed)")
            return False

        state = state + result.state_derivative * DT

        u_last = u
        t += DT

    print(f"  [OK] Success! Final: x={state[0]:.3f}, th1={state[1]:.3f}, th2={state[2]:.3f}")
    return True


def main():
    print("="*70)
    print("BASELINE TEST: HybridWithSScheduling")
    print(f"Gains: {ROBUST_GAINS}, Duration: {SIM_DURATION}s, dt={DT}s")
    print("="*70)

    np.random.seed(42)  # Reproducible

    tests = [
        (50.0, 2.5, "PSO middle"),
        (10.0, 1.0, "Conservative"),
        (20.0, 0.5, "Moderate"),
        (5.0, 0.1, "Lower bounds"),
        (100.0, 5.0, "Upper bounds"),
    ]

    results = []
    for s_agg, s_cons, desc in tests:
        success = run_test(s_agg, s_cons)
        results.append((desc, success))

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    successes = sum(1 for _, s in results if s)
    print(f"Success rate: {successes}/{len(results)}")

    if successes == 0:
        print("\n[CRITICAL] NO configurations work!")
        print("Problem: Controller or ROBUST_GAINS")
    elif successes < len(results) // 2:
        print("\n[WARNING] Only some work - PSO bounds may be wrong")
    else:
        print("\n[OK] Most work - PSO tuning needed")


if __name__ == "__main__":
    main()
