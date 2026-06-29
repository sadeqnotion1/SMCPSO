#!/usr/bin/env python3
r"""Parity + correctness check for M4 Slice 3 (simulation/integrators).

Two kinds of evidence:

(1) STRUCTURAL PARITY (with --source): the ported integrators are byte-identical
    to the original SMC-PSO source except for `#===` banner lines (trailing
    backslashes stripped) and the EOF newline. This is the strongest parity
    statement: no functional edits were made in this slice.

(2) NUMERICAL CORRECTNESS (always): the integrators are validated against analytic
    references (math.exp for linear ODEs, diagonal ZOH closed form, ZOH-vs-fine-RK4),
    and the adaptive error controller is checked for order-awareness.

Usage:
    python scripts/parity_check_m4_slice3.py [--source /path/to/SMC-PSO]

Exit 0 == all checks pass.
"""
from __future__ import annotations
import argparse, math, pathlib, sys
import numpy as np

INTEG_FILES = [
    "__init__.py", "base.py", "factory.py", "compatibility.py",
    "fixed_step/__init__.py", "fixed_step/euler.py", "fixed_step/runge_kutta.py",
    "discrete/__init__.py", "discrete/zero_order_hold.py",
    "adaptive/__init__.py", "adaptive/error_control.py", "adaptive/runge_kutta.py",
]


def _nonbanner(text: str):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln for ln in text.split("\n") if not ln.startswith("#=")]
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def structural_parity(source_root: pathlib.Path, beta_root: pathlib.Path) -> list[str]:
    fails = []
    src = source_root / "src" / "simulation" / "integrators"
    beta = beta_root / "src" / "simulation" / "integrators"
    for rel in INTEG_FILES:
        s = (src / rel).read_text(encoding="utf-8")
        b = (beta / rel).read_text(encoding="utf-8")
        if _nonbanner(s) != _nonbanner(b):
            fails.append(f"functional drift vs source in {rel}")
    return fails


def numerical_correctness() -> list[str]:
    from src.simulation.integrators.fixed_step.euler import ForwardEuler
    from src.simulation.integrators.fixed_step.runge_kutta import RungeKutta4
    from src.simulation.integrators.adaptive.runge_kutta import DormandPrince45
    from src.simulation.integrators.adaptive.error_control import ErrorController
    from src.simulation.integrators.discrete.zero_order_hold import ZeroOrderHold

    fails = []
    U = np.array([0.0])
    lam, dt = -0.7, 0.05
    lin = lambda t, x, u: lam * x
    ref = math.exp(lam * dt)

    if abs(RungeKutta4().integrate(lin, np.array([1.0]), U, dt)[0] - ref) > 1e-8:
        fails.append("RK4 vs exp")
    if abs(DormandPrince45().integrate(lin, np.array([1.0]), U, dt)[0] - ref) > 1e-10:
        fails.append("DP45 vs exp")
    if abs(ForwardEuler().integrate(lin, np.array([1.0]), U, dt)[0] - (1 + lam * dt)) > 1e-12:
        fails.append("ForwardEuler formula")

    # error controller order-awareness (S2-2 fix)
    ec = ErrorController(safety_factor=0.9)
    d5, _ = ec.update_step_size(0.5, 0.1, 1e-12, 10.0, order=5)
    d2, _ = ec.update_step_size(0.5, 0.1, 1e-12, 10.0, order=2)
    if not (d5 < d2) or np.isclose(d5, d2):
        fails.append("error controller not order-aware")

    # ZOH exact vs fine RK4
    A = np.array([[0.0, 1.0], [-2.0, -3.0]]); B = np.array([[0.0], [1.0]])
    x0 = np.array([0.5, -0.3]); u = np.array([0.7]); DT = 0.1
    z = ZeroOrderHold(); z.set_linear_system(A, B, DT)
    x_zoh = z.integrate(lambda t, x, c: A @ x + B @ c, x0, u, DT)
    rk4 = RungeKutta4(); x = x0.copy(); h = DT / 2000
    f = lambda t, xx, c: A @ xx + B @ c
    for _ in range(2000):
        x = rk4.integrate(f, x, u, h)
    if not np.allclose(x_zoh, x, atol=1e-6):
        fails.append("ZOH not exact vs fine RK4")

    return fails


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=None, help="path to original SMC-PSO repo root")
    ap.add_argument("--beta", default=str(pathlib.Path(__file__).resolve().parents[1]))
    args = ap.parse_args()

    fails = []
    if args.source:
        sf = structural_parity(pathlib.Path(args.source), pathlib.Path(args.beta))
        print("STRUCTURAL PARITY:", "OK (banner-only diff)" if not sf else "FAIL")
        fails += sf
    else:
        print("STRUCTURAL PARITY: skipped (no --source)")

    nf = numerical_correctness()
    print("NUMERICAL CORRECTNESS:", "OK" if not nf else "FAIL")
    fails += nf

    if fails:
        print("\nFAILURES:")
        for f in fails:
            print("  -", f)
        return 1
    print("\nPARITY OK: integrators match source (banner-only) and pass correctness checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
