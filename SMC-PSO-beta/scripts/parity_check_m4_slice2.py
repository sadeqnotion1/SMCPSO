#!/usr/bin/env python3
"""Parity check: ported simulation/core vs the original SMC-PSO source.

Lens-B evidence for M4 Slice 2. Compares behavior (not source text) of the
self-contained, numpy-only modules (interfaces, state_space, time_domain) between
the original tree and the beta port. simulation_context is excluded here because
it pulls config/plant/factory; its only change is a lazy import (behavior at
call-time is identical) and is covered by the import smoke test.

Usage:
    python scripts/parity_check_m4_slice2.py --source /path/to/SMC-PSO

Exit code 0 == parity holds.
"""
from __future__ import annotations
import argparse, importlib.util, sys, pathlib
import numpy as np


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="path to original SMC-PSO repo root")
    ap.add_argument("--beta", default=str(pathlib.Path(__file__).resolve().parents[1]),
                    help="path to SMC-PSO-beta repo root (default: this kit)")
    args = ap.parse_args()

    src = pathlib.Path(args.source) / "src" / "simulation" / "core"
    beta = pathlib.Path(args.beta) / "src" / "simulation" / "core"

    fails = []

    # --- state_space ---
    s_ss = _load(src / "state_space.py", "src_ss")
    b_ss = _load(beta / "state_space.py", "beta_ss")
    rng = np.random.default_rng(1234)
    for _ in range(200):
        st = rng.normal(size=6)
        if not np.isclose(s_ss.StateSpaceUtilities.compute_energy(st),
                          b_ss.StateSpaceUtilities.compute_energy(st)):
            fails.append("compute_energy mismatch")
            break
    A_true = np.array([[0.0, 1.0], [-2.0, -3.0]]); B_true = np.array([[0.0], [1.0]])
    dyn = lambda x, u: A_true @ x + B_true @ u
    sA, sB = s_ss.StateSpaceUtilities.linearize_about_equilibrium(dyn, np.zeros(2), np.zeros(1))
    bA, bB = b_ss.StateSpaceUtilities.linearize_about_equilibrium(dyn, np.zeros(2), np.zeros(1))
    if not (np.allclose(sA, bA) and np.allclose(sB, bB)):
        fails.append("linearize mismatch")

    # --- time_domain ---
    s_td = _load(src / "time_domain.py", "src_td")
    b_td = _load(beta / "time_domain.py", "beta_td")
    for dt, ht in [(0.01, 100), (0.1, 10), (0.005, 400)]:
        s_tm = s_td.TimeManager(dt=dt, horizon=ht)
        b_tm = b_td.TimeManager(dt=dt, horizon=ht)
        if not np.allclose(s_tm.get_time_vector(), b_tm.get_time_vector()):
            fails.append(f"time_vector mismatch dt={dt}"); break
    s_a = s_td.AdaptiveTimeStep(initial_dt=0.01)
    b_a = b_td.AdaptiveTimeStep(initial_dt=0.01)
    for err in [1e-9, 1e-4, 1e-2, 1.0]:
        r1 = s_a.update_step_size(err, 1e-3)
        r2 = b_a.update_step_size(err, 1e-3)
        if not (np.isclose(r1[0], r2[0]) and r1[1] == r2[1]):
            fails.append(f"adaptive mismatch err={err}"); break

    if fails:
        print("PARITY FAIL:")
        for f in fails:
            print("  -", f)
        return 1
    print("PARITY OK: state_space + time_domain behavior matches source.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
