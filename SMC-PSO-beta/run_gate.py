#=====================================================================================
#=================================== run_gate.py =====================================
#=====================================================================================

"""M5 Slice 5 offline gate - controller factory.

Run from the repo root in the real beta environment:

    python run_gate.py

Validates the clean beta-native ``src/controllers/factory.py`` and the widened
``src/controllers/__init__.py``:

  STRUCTURAL : 86-col LF banner, no src.core / twin / fallback imports, public
               surface importable, SMCType has 4 members, registry has the 4
               canonical types, __init__ re-exports the factory surface.
  UNIT       : alias canonicalisation, default-gain counts, PSO bound lengths,
               validate_smc_gains true/false, STA K1>K2 hard error,
               create_controller for all 4 types, PSO wrapper shape/finite/clip.
  PARITY     : factory.create_controller(...) vs directly constructed monolith
               with identical kwargs -> max|du| over N random states == 0.

Exit code 0 = all green, 1 = any failure.
"""

from __future__ import annotations

import os
import sys
import traceback

import numpy as np

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

FACTORY_PATH = os.path.join(REPO_ROOT, "src", "controllers", "factory.py")
INIT_PATH = os.path.join(REPO_ROOT, "src", "controllers", "__init__.py")

_failures = []
_passes = 0


def check(name, cond, detail=""):
    global _passes
    if cond:
        _passes += 1
        print(f"PASS  {name}")
    else:
        _failures.append(name)
        print(f"FAIL  {name}  {detail}")


def section(title):
    print(f"\n----- {title} -----")


#--- STRUCTURAL --------------------------------------------------------------------
section("STRUCTURAL")

with open(FACTORY_PATH, "rb") as fh:
    raw = fh.read()
check("factory.py uses LF only", b"\r\n" not in raw, "found CRLF")
check("factory.py ends with newline", raw.endswith(b"\n"))
text = raw.decode("utf-8")
lines = text.split("\n")
check("factory banner line1 width 86", len(lines[0]) == 86, repr(lines[0]))
check("factory banner path line", lines[1] == "#" + "=" * 28 + " src/controllers/factory.py " + "=" * 29, repr(lines[1]))
check("factory banner line3 width 86", len(lines[2]) == 86)
# Inspect ACTUAL import statements (not docstring prose) via AST so the
# "Dropped from scope" documentation does not trip the forbidden-import gate.
import ast as _ast
_imported = set()
for _node in _ast.walk(_ast.parse(text)):
    if isinstance(_node, _ast.Import):
        for _a in _node.names:
            _imported.add(_a.name)
    elif isinstance(_node, _ast.ImportFrom):
        _imported.add(("." * (_node.level or 0)) + (_node.module or ""))
_forbidden = {"core", "plant", "legacy_factory", "fallback_configs", "conditional_hybrid", "mpc"}
_bad = []
for _m in _imported:
    _parts = set(_m.replace("src.", "").lstrip(".").split("."))
    if (_parts & _forbidden) or ("threading" in _m):
        _bad.append(_m)
check("no forbidden imports (core/plant/legacy/mpc/threading)", not _bad, f"bad={sorted(set(_bad))} all={sorted(_imported)}")

with open(INIT_PATH, "rb") as fh:
    raw_init = fh.read()
check("__init__.py uses LF only", b"\r\n" not in raw_init)
check("__init__ banner width 86", len(raw_init.decode("utf-8").split("\n")[0]) == 86)

try:
    import src.controllers as C
    from src.controllers.factory import (
        SMCType, SMCConfig, SMCFactory, create_controller, create_smc_for_pso,
        create_pso_controller_factory, get_gain_bounds_for_pso, validate_smc_gains,
        validate_controller_gains, get_expected_gain_count, canonicalize_controller_type,
        list_available_controllers, get_default_gains, PSOControllerWrapper,
        CONTROLLER_REGISTRY, ValidationResult,
    )
    from src.controllers import (
        ClassicalSMC, SuperTwistingSMC, AdaptiveSMC, HybridAdaptiveSTASMC,
    )
    imported = True
except Exception as exc:  # pragma: no cover
    imported = False
    traceback.print_exc()
check("factory + monoliths import", imported)
if not imported:
    print("\nABORTING: import failed")
    sys.exit(1)

for name in ["SMCType", "SMCConfig", "SMCFactory", "create_controller",
             "create_smc_for_pso", "get_gain_bounds_for_pso", "validate_smc_gains",
             "get_expected_gain_count", "PSOControllerWrapper"]:
    check(f"__init__ re-exports {name}", hasattr(C, name))

check("SMCType has 4 members",
      {m.value for m in SMCType} == {"classical_smc", "adaptive_smc", "sta_smc", "hybrid_adaptive_sta_smc"})
check("registry has 4 types",
      sorted(CONTROLLER_REGISTRY) == sorted(["classical_smc", "sta_smc", "adaptive_smc", "hybrid_adaptive_sta_smc"]))
check("no conditional/mpc aliases",
      all(v in CONTROLLER_REGISTRY for v in C.CONTROLLER_ALIASES.values())
      and not any("conditional" in k for k in C.CONTROLLER_ALIASES))


#--- UNIT --------------------------------------------------------------------------
section("UNIT")

TYPES = {
    "classical_smc": (ClassicalSMC, 6),
    "sta_smc": (SuperTwistingSMC, 6),
    "adaptive_smc": (AdaptiveSMC, 5),
    "hybrid_adaptive_sta_smc": (HybridAdaptiveSTASMC, 4),
}
for alias, canon in [("classic_smc", "classical_smc"), ("super_twisting", "sta_smc"),
                     ("sta", "sta_smc"), ("adaptive", "adaptive_smc"),
                     ("hybrid", "hybrid_adaptive_sta_smc")]:
    check(f"alias {alias}->{canon}", canonicalize_controller_type(alias) == canon)

for t, (cls, n) in TYPES.items():
    check(f"gain_count {t}={n}", get_expected_gain_count(t) == n)
    lo, hi = get_gain_bounds_for_pso(t)
    check(f"bounds len {t}", len(lo) == n and len(hi) == n and all(l < h for l, h in zip(lo, hi)))
    check(f"default gains len {t}", len(get_default_gains(t)) == n)

check("validate good classical", validate_smc_gains("classical_smc", [20, 15, 12, 8, 35, 5]) is True)
check("validate wrong count", validate_smc_gains("classical_smc", [1, 2, 3]) is False)
check("validate negative", validate_smc_gains("adaptive_smc", [25, 18, 15, 10, -1]) is False)

vr_bad = validate_controller_gains([5, 10, 20, 12, 8, 6], "sta_smc", check_bounds=False, check_stability=False)
check("STA K1<=K2 invalid", (not vr_bad.valid) and any("K1 > K2" in e for e in vr_bad.errors))
check("STA K1>K2 valid", validate_controller_gains([25, 15, 20, 12, 8, 6], "sta_smc", check_bounds=False, check_stability=False).valid)
try:
    create_controller("sta_smc", gains=[5, 10, 20, 12, 8, 6])
    check("create STA bad raises", False)
except ValueError:
    check("create STA bad raises", True)

ctrls = {}
for t, (cls, n) in TYPES.items():
    c = create_controller(t, gains=get_default_gains(t))
    ctrls[t] = c
    check(f"create {t} -> {cls.__name__}", isinstance(c, cls))


def call(controller, state):
    sv = controller.initialize_state() if hasattr(controller, "initialize_state") else ()
    hist = controller.initialize_history() if hasattr(controller, "initialize_history") else {}
    result = controller.compute_control(state, sv, hist)
    u = getattr(result, "u", None)
    if u is None:
        u = result[0] if isinstance(result, (tuple, list)) else result
    return float(np.asarray(u, dtype=float).flatten()[0])


rng = np.random.default_rng(12345)
states = [rng.uniform(-0.5, 0.5, 6) for _ in range(50)]
for t, c in ctrls.items():
    us = [call(c, s) for s in states]
    check(f"{t} compute finite", all(np.isfinite(us)))

for t, (cls, n) in TYPES.items():
    w = create_smc_for_pso(t, get_default_gains(t))
    check(f"{t} wrapper type", isinstance(w, PSOControllerWrapper))
    out = w.compute_control(states[0])
    check(f"{t} wrapper shape/finite", isinstance(out, np.ndarray) and out.shape == (1,) and np.isfinite(out[0]))
    check(f"{t} wrapper saturates", abs(out[0]) <= w.max_force + 1e-9)
    mask = w.validate_gains(np.array([get_default_gains(t), [-1] + list(get_default_gains(t))[1:]]))
    check(f"{t} validate_gains mask", bool(mask[0]) and not bool(mask[1]))

pf = create_pso_controller_factory(SMCType.ADAPTIVE)
check("pso factory metadata", pf.n_gains == 5 and pf.controller_type == "adaptive_smc")
check("pso factory builds wrapper", isinstance(pf(get_default_gains("adaptive_smc")), PSOControllerWrapper))


#--- BEHAVIORAL PARITY -------------------------------------------------------------
section("BEHAVIORAL PARITY (factory vs direct construction)")

direct_builders = {
    "classical_smc": lambda g: ClassicalSMC(gains=g, max_force=150.0, boundary_layer=0.02,
                                            dynamics_model=None, regularization=1e-10, switch_method="tanh"),
    "sta_smc": lambda g: SuperTwistingSMC(gains=g, dt=0.001, max_force=150.0, damping_gain=0.0,
                                          boundary_layer=0.01, dynamics_model=None, switch_method="linear"),
    "adaptive_smc": lambda g: AdaptiveSMC(gains=g, dt=0.001, max_force=150.0, leak_rate=0.01,
                                          adapt_rate_limit=10.0, K_min=0.1, K_max=100.0, smooth_switch=True,
                                          boundary_layer=0.01, dead_zone=0.05, K_init=10.0, alpha=0.5),
    "hybrid_adaptive_sta_smc": lambda g: HybridAdaptiveSTASMC(gains=g, dt=0.001, max_force=150.0,
                                          k1_init=4.0, k2_init=0.4, gamma1=0.1, gamma2=0.05,
                                          dead_zone=0.05, sat_soft_width=0.35, dynamics_model=None),
}
for t in TYPES:
    g = get_default_gains(t)
    cf = create_controller(t, gains=g)
    cd = direct_builders[t](g)
    md = max(abs(call(cf, s) - call(cd, s)) for s in states)
    check(f"PARITY {t} max|du|={md:.3e}", md == 0.0, f"max|du|={md}")


#--- SUMMARY -----------------------------------------------------------------------
print(f"\n===== GATE SUMMARY: {_passes} passed, {len(_failures)} failed =====")
if _failures:
    for f in _failures:
        print("  FAILED:", f)
    sys.exit(1)
print("ALL GREEN")
sys.exit(0)
