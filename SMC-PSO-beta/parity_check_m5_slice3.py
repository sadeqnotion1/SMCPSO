#!/usr/bin/env python3
#======================================================================================
#============================== parity_check_m5_slice3.py ============================
#======================================================================================
"""M5 Slice 3 parity gate: adaptive SMC port.

Usage:  python parity_check_m5_slice3.py [REPO_ROOT=.]

STRUCTURAL: re-derive the expected beta file from the bundled normalized source
(parity_src/source_adaptive_smc.py) by applying ONLY the documented transforms
(EOL/banner normalize, Trap-E citation-token strip, ...utils -> ..utils
relocation) and assert byte-identity with the repo's adaptive_smc.py.

BEHAVIORAL: instantiate the repo AdaptiveSMC and compare the control u, the
adapted gain K^+, AND the time-in-sliding counter against an independent
reference implementation of the full dead-zone-gated, leaky, rate-limited
adaptation law across a random battery (smooth + linear switching).
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
    raw = open(os.path.join(HERE, "parity_src", "source_adaptive_smc.py"), encoding="utf-8").read()
    body = reloc(strip_tokens(strip_banner(norm_eol(raw))))
    return banner("src/controllers/adaptive_smc.py") + body + "\n"


def structural():
    repo_file = os.path.join(REPO, "src", "controllers", "adaptive_smc.py")
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
    from src.controllers.adaptive_smc import AdaptiveSMC
    from src.utils import saturate

    def ref(state, K0, t0, gains, dt, max_force, leak, arl, Kmin, Kmax, smooth, bl, dz, K_init, alpha):
        k1, k2, lam1, lam2, gamma = [float(g) for g in gains[:5]]
        _, th1, th2, _, th1d, th2d = state
        sigma = k1 * (th1d + lam1 * th1) + k2 * (th2d + lam2 * th2)
        sw = saturate(sigma, bl, method="tanh" if smooth else "linear")
        u_sw = -K0 * sw
        u = float(np.clip(u_sw - alpha * sigma, -max_force, max_force))
        t = t0 + dt if abs(sigma) <= bl else 0.0
        if abs(sigma) <= dz:
            dK = 0.0
        else:
            dK = gamma * abs(sigma) - leak * (K0 - K_init)
        dK = float(np.clip(dK, -arl, arl))
        newK = float(np.clip(K0 + dK * dt, Kmin, Kmax))
        return u, newK, t

    rng = np.random.default_rng(2025)
    md_u = md_K = md_t = 0.0
    n = 0
    for _ in range(400):
        gains = [float(rng.uniform(0.5, 12)) for _ in range(5)]
        dt = float(rng.uniform(1e-3, 5e-2))
        max_force = float(rng.uniform(1.0, 200.0))
        leak = float(rng.uniform(0.0, 1.0))
        arl = float(rng.uniform(0.1, 50.0))
        Kmin = float(rng.uniform(0.05, 1.0))
        Kmax = Kmin + float(rng.uniform(5.0, 100.0))
        K_init = float(rng.uniform(Kmin, Kmax))
        K0 = float(rng.uniform(Kmin, Kmax))
        t0 = float(rng.uniform(0.0, 5.0))
        alpha = float(rng.uniform(0.0, 2.0))
        bl = float(rng.uniform(0.05, 1.0))
        dz = float(rng.uniform(0.0, 0.3))
        smooth = bool(rng.random() < 0.5)
        c = AdaptiveSMC(gains, dt=dt, max_force=max_force, leak_rate=leak,
                        adapt_rate_limit=arl, K_min=Kmin, K_max=Kmax,
                        smooth_switch=smooth, boundary_layer=bl, dead_zone=dz,
                        K_init=K_init, alpha=alpha)
        state = rng.uniform(-2, 2, size=6)
        out = c.compute_control(state, (K0, 0.0, t0), {})
        eu, eK, et = ref(state, K0, t0, gains, dt, max_force, leak, arl, Kmin, Kmax,
                         smooth, bl, dz, K_init, alpha)
        md_u = max(md_u, abs(out.u - eu))
        md_K = max(md_K, abs(out.state[0] - eK))
        md_t = max(md_t, abs(out.state[2] - et))
        n += 1
    print(f"  behavioral: {n} cases, max|du| = {md_u:.2e}, max|dK| = {md_K:.2e}, max|dt_sld| = {md_t:.2e}")
    return md_u < 1e-9 and md_K < 1e-9 and md_t < 1e-9


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
