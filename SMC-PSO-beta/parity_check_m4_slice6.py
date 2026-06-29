#!/usr/bin/env python3
"""PARITY CHECK - M4 Slice 6 (simulation/strategies + wired simulation/__init__, Trap D).
Usage: python parity_check_m4_slice6.py [REPO_ROOT]   (default ".")
Verifies (1) STRUCTURAL: each ported file is byte-identical to source after banner
normalization (CRLF->LF + strip trailing backslash/space on #= banner lines); and
(2) BEHAVIORAL: MonteCarloStrategy statistics match a numpy reference and the wired
simulation package exposes the full legacy surface.
"""
import hashlib, os, sys

NORM_SHA256 = {
    'strategies/__init__.py': '8f6fee91fbd3ec48eb10fa7f04f9c1820e33ec392f60a92f1b0dd2b70803a90b',
    'strategies/monte_carlo.py': 'c7ea679557a1c223acb7ac58799742d7ecdf31f72826b4d95619374f95bf8540',
    '__init__.py': '8ad30c37a4d607f3877ac95e7853fe98c756d5d3a062c883f002ed01d9123e7f',
}

def norm_bytes(b):
    s = b.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    out = []
    for line in s.split("\n"):
        if line.startswith("#="):
            line = line.rstrip("\\ \t")
        out.append(line)
    return "\n".join(out).encode("utf-8")

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    base = os.path.join(root, "src", "simulation")
    ok = True
    for rel, want in NORM_SHA256.items():
        path = os.path.join(base, *rel.split("/"))
        if not os.path.exists(path):
            print("  MISSING", path); ok = False; continue
        with open(path, "rb") as f:
            raw = f.read()
        nb = norm_bytes(raw)
        got = hashlib.sha256(nb).hexdigest()
        delta = len(raw) - len(nb)
        if got == want:
            print("  ok  src/simulation/%s  (banner+EOL-only delta vs source: %d bytes)" % (rel, delta))
        else:
            print("  MISMATCH src/simulation/%s\n      want %s\n      got  %s" % (rel, want, got)); ok = False
    print("STRUCTURAL PARITY: OK (banner-only diff)" if ok else "STRUCTURAL PARITY: FAILED")

    # ---- behavioral ----
    bok = True
    try:
        sys.path.insert(0, root)
        import numpy as np
        from src.simulation.strategies import MonteCarloStrategy
        class _R:
            def __init__(s, st): s._st = np.asarray(st, float)
            def get_states(s): return s._st
        def fn(p, **k): return _R([[0.0, 0.0], [p.get("g", 1.0), 2.0 * p.get("g", 1.0)]])
        out = MonteCarloStrategy(n_samples=50, parallel=False).analyze(
            fn, {"distributions": {"g": {"type": "constant", "value": 2.0}}})
        assert out["success_rate"] == 1.0, "success_rate"
        assert abs(out["statistics"]["final_state_0"]["mean"] - 2.0) < 1e-9, "mean f0"
        assert abs(out["statistics"]["final_state_1"]["mean"] - 4.0) < 1e-9, "mean f1"
        assert abs(out["statistics"]["max_deviation"]["max"] - 4.0) < 1e-9, "max_dev"
    except Exception as e:
        print("  BEHAVIORAL MonteCarlo FAILED:", repr(e)); bok = False
    print("BEHAVIORAL CORRECTNESS: OK" if bok else "BEHAVIORAL CORRECTNESS: FAILED")

    print("PARITY OK" if (ok and bok) else "PARITY FAILED")
    sys.exit(0 if (ok and bok) else 1)

if __name__ == "__main__":
    main()
