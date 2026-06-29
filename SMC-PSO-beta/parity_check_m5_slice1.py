#!/usr/bin/env python3
#======================================================================================
#============================== parity_check_m5_slice1.py =============================
#======================================================================================
"""M5 Slice 1 parity gate: classical SMC port.

Usage:  python parity_check_m5_slice1.py [REPO_ROOT=.]

STRUCTURAL: re-derive the expected beta file from the bundled normalized source
(parity_src/source_classic_smc.py) by applying ONLY the documented transforms
(EOL/banner normalize, Trap-E citation-token strip, ...->.. relocation, beta
banner) and assert it is byte-identical to the repo's classical_smc.py. This
proves no hidden functional drift was introduced by the port.

BEHAVIORAL: instantiate the repo ClassicalSMC (no dynamics model -> pure
switching law) and compare its output against an independent reference
implementation of the documented control law across a random battery.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = sys.argv[1] if len(sys.argv) > 1 else "."
W = 86


def norm_eol(t):
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    out = []
    for ln in t.split("\n"):
        if ln.lstrip().startswith("#="):
            ln = ln.rstrip("\\ \t")
        out.append(ln)
    return "\n".join(out)


def strip_tokens(t):
    return re.sub(r"\u3010[^\u3011]*\u3011", "", t)


def strip_banner(t):
    lines = t.split("\n")
    i = 0
    while i < len(lines) and lines[i].lstrip().startswith("#="):
        i += 1
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    j = len(lines)
    while j > i and (lines[j-1].strip() == "" or lines[j-1].lstrip().startswith("#=")):
        j -= 1
    return "\n".join(lines[i:j])


def banner(p):
    l1 = "#" + "=" * (W - 1)
    title = " " + p + " "
    pad = (W - 1) - len(title)
    left = pad // 2
    l2 = "#" + "=" * left + title + "=" * (pad - left)
    return l1 + "\n" + l2 + "\n" + l1 + "\n"


def reloc(t):
    return t.replace("from ...utils", "from ..utils").replace("from ...plant", "from ..plant")


def expected_beta():
    raw = open(os.path.join(HERE, "parity_src", "source_classic_smc.py"), encoding="utf-8").read()
    body = reloc(strip_tokens(strip_banner(norm_eol(raw))))
    return banner("src/controllers/classical_smc.py") + body + "\n"


def structural():
    repo_file = os.path.join(REPO, "src", "controllers", "classical_smc.py")
    got = norm_eol(open(repo_file, encoding="utf-8").read())
    if not got.endswith("\n"):
        got += "\n"
    exp = expected_beta()
    if got != exp:
        gl, el = got.split("\n"), exp.split("\n")
        for n, (a, b) in enumerate(zip(gl, el), 1):
            if a != b:
                print(f"  STRUCT DIFF line {n}:\n    repo: {a!r}\n    exp : {b!r}")
                break
        if len(gl) != len(el):
            print(f"  STRUCT length differs: repo={len(gl)} exp={len(el)}")
        return False
    for bad, why in (("\u3010", "Trap E token"), ("src.core", "Trap B import"),
                     ("from ...utils", "unrelocated import"), ("from ...plant", "unrelocated import")):
        if bad in got:
            print(f"  STRUCT FAIL: found {why} ({bad!r})")
            return False
    return True


def behavioral():
    sys.path.insert(0, REPO)
    import numpy as np
    from src.controllers.classical_smc import ClassicalSMC

    def ref_u(state, gains, max_force, eps, method, slope=3.0):
        k1, k2, lam1, lam2, K, kd = [float(g) for g in gains]
        _, th1, th2, _, dth1, dth2 = state
        sigma = lam1 * th1 + lam2 * th2 + k1 * dth1 + k2 * dth2
        s = sigma / eps
        if method == "tanh":
            sat = np.tanh(np.clip(s / slope, -700, 700))
        else:
            sat = np.clip(s, -1.0, 1.0)
        u = -K * sat - kd * sigma  # u_eq = 0 (no dynamics model)
        return float(np.clip(u, -max_force, max_force))

    rng = np.random.default_rng(12345)
    maxdiff = 0.0
    n = 0
    for _ in range(400):
        gains = [float(rng.uniform(0.5, 10)) for _ in range(5)] + [float(rng.uniform(0.0, 5))]
        max_force = float(rng.uniform(5, 200))
        eps = float(rng.uniform(0.05, 1.0))
        method = "tanh" if rng.random() < 0.5 else "linear"
        c = ClassicalSMC(gains, max_force=max_force, boundary_layer=eps, switch_method=method)
        state = rng.uniform(-2, 2, size=6)
        got = c.compute_control(state, (), {}).u
        exp = ref_u(state, gains, max_force, eps, method)
        maxdiff = max(maxdiff, abs(got - exp))
        n += 1
    print(f"  behavioral: {n} cases, max|repo-ref| = {maxdiff:.2e}")
    return maxdiff < 1e-9


def main():
    s = structural()
    print("STRUCTURAL PARITY:", "OK (banner + Trap-E + relocation normalized)" if s else "FAIL")
    b = behavioral()
    print("BEHAVIORAL CORRECTNESS:", "OK" if b else "FAIL")
    if s and b:
        print("PARITY OK")
        return 0
    print("PARITY FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
