#!/usr/bin/env python3
#======================================================================================
#============================== parity_check_m5_slice2.py =============================
#======================================================================================
"""M5 Slice 2 parity gate: super-twisting SMC port.

Usage:  python parity_check_m5_slice2.py [REPO_ROOT=.]

STRUCTURAL: re-derive the expected beta file from the bundled normalized source
(parity_src/source_sta_smc.py) by applying ONLY the documented transforms
(EOL/banner normalize, Trap-E citation-token strip, ...utils -> ..utils
relocation) and assert byte-identity with the repo's sta_smc.py.

BEHAVIORAL: instantiate the repo SuperTwistingSMC (no dynamics model -> pure
switching law) and compare u AND the updated integrator state z against an
independent reference implementation of the super-twisting law across a random
battery (incl. saturation + anti-windup).
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
    raw = open(os.path.join(HERE, "parity_src", "source_sta_smc.py"), encoding="utf-8").read()
    body = reloc(strip_tokens(strip_banner(norm_eol(raw))))
    return banner("src/controllers/sta_smc.py") + body + "\n"


def structural():
    repo_file = os.path.join(REPO, "src", "controllers", "sta_smc.py")
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
                     ("from ...utils", "unrelocated import")):
        if bad in got:
            print(f"  STRUCT FAIL: found {why} ({bad!r})")
            return False
    return True


def behavioral():
    sys.path.insert(0, REPO)
    import numpy as np
    from src.controllers.sta_smc import SuperTwistingSMC
    from src.utils import saturate

    def ref(state, z, gains, dt, max_force, damping, eps, method, Kaw):
        K1, K2, k1, k2, lam1, lam2 = [float(g) for g in gains]
        _, th1, th2, _, th1dot, th2dot = state
        sigma = k1 * (th1dot + lam1 * th1) + k2 * (th2dot + lam2 * th2)
        sgn = saturate(sigma, eps, method=method)
        u_cont = -K1 * np.sqrt(abs(sigma)) * sgn
        u_raw = u_cont + z - damping * sigma  # u_eq = 0
        u_sat = float(np.clip(u_raw, -max_force, max_force))
        new_z = z - K2 * sgn * dt + Kaw * (u_sat - u_raw) * dt
        new_z = float(np.clip(new_z, -max_force, max_force))
        return u_sat, new_z

    rng = np.random.default_rng(2025)
    md_u = md_z = 0.0
    n = 0
    for _ in range(400):
        gains = [float(rng.uniform(0.5, 12)) for _ in range(6)]
        dt = float(rng.uniform(1e-3, 5e-2))
        max_force = float(rng.uniform(1.0, 200.0))
        damping = float(rng.uniform(0.0, 3.0))
        eps = float(rng.uniform(0.05, 1.0))
        Kaw = float(rng.uniform(0.0, 3.0))
        method = "tanh" if rng.random() < 0.5 else "linear"
        z = float(rng.uniform(-50, 50))
        c = SuperTwistingSMC(gains, dt=dt, max_force=max_force, damping_gain=damping,
                             boundary_layer=eps, switch_method=method, anti_windup_gain=Kaw)
        state = rng.uniform(-2, 2, size=6)
        out = c.compute_control(state, (z, 0.0), {})
        eu, ez = ref(state, z, gains, dt, max_force, damping, eps, method, Kaw)
        md_u = max(md_u, abs(out.u - eu))
        md_z = max(md_z, abs(out.state[0] - ez))
        n += 1
    print(f"  behavioral: {n} cases, max|du| = {md_u:.2e}, max|dz| = {md_z:.2e}")
    return md_u < 1e-9 and md_z < 1e-9


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
