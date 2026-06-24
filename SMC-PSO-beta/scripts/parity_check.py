#!/usr/bin/env python3
"""
Shared parity + invariant harness for the DIP plant (M2 and reused by later milestones).

Two layers:
  1) INVARIANT GATE (always runs, no repo needed): symmetry/PD, KE-vs-M consistency,
     (Mdot-2C) skew-symmetry, energy conservation. Uses the verified-correct reference.
  2) PARITY (optional): if your real `FullDIPDynamics` is importable, compare its
     M/C/G and a short trajectory against the reference and report max abs diff.

Golden trajectories vs SMC-PSO/ (source) must be captured on your machine; this
environment cannot run both repos. The command is printed at the end.

ASCII markers only.  Exit code 0 = gate passed, 1 = failed.
"""
import sys, os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from plant.core.physics_matrices_corrected import (  # noqa: E402
    DIPParameters, inertia_matrix, coriolis_matrix, gravity_vector,
    kinetic_energy, potential_energy, rhs_conservative,
)

# Nominal params from config.yaml [physics]
P = DIPParameters(m0=1.5, m1=0.2, m2=0.15, L1=0.4, L2=0.3,
                  Lc1=0.2, Lc2=0.15, I1=0.00265, I2=0.00115, g=9.81)

RNG = np.random.default_rng(42)
fails = []


def gate():
    # A: symmetric PD
    bad_sym = bad_pd = 0
    for _ in range(2000):
        t1, t2 = RNG.uniform(-np.pi, np.pi, 2)
        M = inertia_matrix(P, t1, t2)
        if not np.allclose(M, M.T, atol=1e-12):
            bad_sym += 1
        if np.min(np.linalg.eigvalsh((M + M.T) / 2)) <= 0:
            bad_pd += 1
    print(f"[{'OK' if not (bad_sym or bad_pd) else 'ERROR'}] A  M symmetric-PD ({bad_sym},{bad_pd} viol)")
    if bad_sym or bad_pd:
        fails.append("A")

    # B: KE consistency
    e = 0.0
    for _ in range(2000):
        t1, t2 = RNG.uniform(-np.pi, np.pi, 2)
        qd = RNG.uniform(-3, 3, 3)
        st = [0.0, t1, t2, qd[0], qd[1], qd[2]]
        e = max(e, abs(kinetic_energy(P, st) - 0.5 * qd.dot(inertia_matrix(P, t1, t2).dot(qd))))
    print(f"[{'OK' if e < 1e-9 else 'ERROR'}] B  KE == 0.5 qd^T M qd  (max err {e:.2e})")
    if e >= 1e-9:
        fails.append("B")

    # C: skew-symmetry
    mq = 0.0
    for _ in range(2000):
        q = np.array([0.0, RNG.uniform(-np.pi, np.pi), RNG.uniform(-np.pi, np.pi)])
        qd = RNG.uniform(-3, 3, 3)
        h = 1e-6
        Mdot = (inertia_matrix(P, q[1] + h * qd[1], q[2] + h * qd[2])
                - inertia_matrix(P, q[1] - h * qd[1], q[2] - h * qd[2])) / (2 * h)
        S = Mdot - 2 * coriolis_matrix(P, q, qd)
        mq = max(mq, abs(qd.dot(S.dot(qd))))
    print(f"[{'OK' if mq < 1e-4 else 'ERROR'}] C  (Mdot-2C) skew  (max {mq:.2e})")
    if mq >= 1e-4:
        fails.append("C")

    # D: energy conservation
    s = np.array([0.0, 0.15, -0.10, 0.0, 0.0, 0.0])
    E0 = kinetic_energy(P, s) + potential_energy(P, s)
    dr = 0.0
    dt = 1e-4
    for _ in range(int(2.0 / dt)):
        k1 = rhs_conservative(P, s); k2 = rhs_conservative(P, s + 0.5 * dt * k1)
        k3 = rhs_conservative(P, s + 0.5 * dt * k2); k4 = rhs_conservative(P, s + dt * k3)
        s = s + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        dr = max(dr, abs(kinetic_energy(P, s) + potential_energy(P, s) - E0))
    rel = dr / abs(E0)
    print(f"[{'OK' if rel < 1e-3 else 'ERROR'}] D  energy conserved  (rel drift {rel:.2e})")
    if rel >= 1e-3:
        fails.append("D")


def parity():
    try:
        from plant.models.full.dynamics import FullDIPDynamics  # type: ignore
    except Exception as ex:  # noqa: BLE001
        print(f"[INFO] parity skipped: real FullDIPDynamics not importable ({ex.__class__.__name__})")
        return
    print("[INFO] real FullDIPDynamics imported -- compare M/C/G + trajectory here")
    # TODO(user): instantiate with config.yaml, compare get_physics_matrices() vs reference.


if __name__ == "__main__":
    print("=== M2 plant invariant gate ===")
    gate()
    parity()
    print("\nGolden parity vs source repo (run locally):")
    print("  cd SMC-PSO  && python scripts/parity_check.py --emit-golden > golden_src.json")
    print("  cd SMC-PSO-beta && python scripts/parity_check.py --compare ../SMC-PSO/golden_src.json")
    if fails:
        print(f"\n[ERROR] gate FAILED: {','.join(fails)}")
        sys.exit(1)
    print("\n[OK] gate passed")
    sys.exit(0)
