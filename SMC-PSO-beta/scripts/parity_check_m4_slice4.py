r"""M4 Slice 4 parity check: simulation/safety.

Two checks:
  1. STRUCTURAL PARITY: ported safety/*.py is byte-identical to the source modulo
     #=== banner normalization (trailing backslashes stripped, CRLF->LF, trailing
     blank lines). Run with --source pointing at the original SMC-PSO checkout.
  2. BEHAVIORAL CORRECTNESS: guard frozen substrings, recovery semantics, and the
     S2-3 reconciliation (safety.PerformanceMonitor IS core.interfaces.PerformanceMonitor).

Usage:
  PYTHONPATH=<beta_src_root> python scripts/parity_check_m4_slice4.py [--source <SMC-PSO root>]
"""
import argparse, os, sys

FILES = ["__init__.py", "guards.py", "constraints.py", "monitors.py", "recovery.py"]


def _nonbanner(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [l for l in text.split("\n") if not l.startswith("#=")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def structural(source_root):
    here = os.path.dirname(os.path.abspath(__file__))
    beta = os.path.normpath(os.path.join(here, "..", "src", "simulation", "safety"))
    src = os.path.join(source_root, "src", "simulation", "safety")
    ok = True
    for f in FILES:
        a = _nonbanner(open(os.path.join(src, f), encoding="utf-8").read())
        b = _nonbanner(open(os.path.join(beta, f), encoding="utf-8").read())
        same = a == b
        ok = ok and same
        print(f"  {f:18s} non-banner identical: {same}")
    print("STRUCTURAL PARITY: OK (banner-only diff)" if ok else "STRUCTURAL PARITY: FAIL")
    return ok


def behavioral():
    import numpy as np
    from src.simulation.safety.guards import guard_no_nan, guard_energy, guard_bounds, SafetyViolationError
    from src.simulation.safety.recovery import EmergencyStop, StateLimiter
    from src.simulation.safety import PerformanceMonitor as SafetyPM
    from src.simulation.core.interfaces import PerformanceMonitor as CorePM
    ok = True

    def expect(label, fn, frozen):
        nonlocal ok
        try:
            fn()
            print(f"  {label}: FAIL (no raise)"); ok = False
        except SafetyViolationError as e:
            hit = frozen in str(e)
            ok = ok and hit
            print(f"  {label}: {'OK' if hit else 'FAIL'} (frozen substring)")

    expect("guard_no_nan", lambda: guard_no_nan(np.array([np.nan]), 1), "NaN detected in state at step <i>")
    expect("guard_energy", lambda: guard_energy(np.array([9.0]), {"max": 1.0}), "Energy check failed: total_energy=<val> exceeds <max>")
    expect("guard_bounds", lambda: guard_bounds(np.array([9.0]), (0.0, 1.0), 0.5), "State bounds violated at t=<t>")

    st, ctrl, good = EmergencyStop().recover(np.array([1.0]), 5.0, {})
    cond = good and ctrl == 0.0
    ok = ok and cond
    print(f"  EmergencyStop zeros control: {'OK' if cond else 'FAIL'}")

    st, ctrl, good = StateLimiter(np.array([0.0]), np.array([1.0])).recover(np.array([5.0]), 4.0, {})
    cond = good and float(st[0]) == 1.0 and ctrl == 2.0
    ok = ok and cond
    print(f"  StateLimiter clips + halves control: {'OK' if cond else 'FAIL'}")

    cond = SafetyPM is CorePM
    ok = ok and cond
    print(f"  S2-3 PerformanceMonitor reconciliation: {'OK' if cond else 'FAIL'}")

    print("BEHAVIORAL CORRECTNESS: OK" if ok else "BEHAVIORAL CORRECTNESS: FAIL")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=None, help="path to original SMC-PSO root")
    args = ap.parse_args()
    s = structural(args.source) if args.source else True
    if not args.source:
        print("STRUCTURAL PARITY: SKIPPED (no --source)")
    b = behavioral()
    print("PARITY OK" if (s and b) else "PARITY FAIL")
    sys.exit(0 if (s and b) else 1)


if __name__ == "__main__":
    main()
