# Audit Card — M5 Slice 2: Super-Twisting SMC

- **Source:** `SMC-PSO/src/controllers/smc/sta_smc.py` (class `SuperTwistingSMC`, 27 829 B)
- **Target:** `SMC-PSO-beta/src/controllers/sta_smc.py` (NEW) + widened `src/controllers/__init__.py`
- **Date:** 2026-06-29 · **Gate:** parity OK (structural + 400-case behavioral, du=dz=0.0) · 18/18 unit tests

## Lens A — AI-slop / structural hygiene
| Check | Finding | Action |
|---|---|---|
| Duplicate implementations | Source ships the monolith (`smc/sta_smc.py`, imported by `factory/base.py:191`, source `__init__.py:52`) AND a modular twin (`smc/algorithms/super_twisting/*`) whose `controller.py` re-exports `SuperTwistingSMC` for back-compat but only the `SuperTwistingSMCConfig` is consumed by the factory. | **Port monolith; drop modular twin.** (DECISIONS #1) |
| Dead code | `_sta_smc_control_numba` (module-level njit fn) is never called — `compute_control` uses `_sta_smc_core`. | **Retained** this slice for minimal-diff/byte-parity; flagged for a future cleanup slice. (DECISIONS #6) |
| Optional numba | `import numba` guarded by try/except with a `_DummyNumba` fallback supplying a no-op `njit`. | Kept as-is; offline gate exercises the pure-Python fallback. |
| Citation tokens (Trap E) | Many CJK-bracket pseudo-citations (Levant 2003, Moreno-Osorio 2008, Seeber 2017, numeric IDs). | Stripped via `\u3010[^\u3011]*\u3011`; 0 remain (asserted). Docstring-only. |
| Banner / EOL | CRLF + trailing `\\\` mojibake. | Normalized to LF + regenerated 86-col beta banner. |
| Trap B (`src.core`) | None. | Asserted absent. |
| Trap A (state order) | `_compute_sliding_surface` unpacks `_, th1, th2, _, th1dot, th2dot` = canonical GROUPED. | **No adapter** — `test_grouped_state_convention_trap_a`. |

## Lens B — control-theoretic correctness
| Property | Verification |
|---|---|
| Sliding surface `s = k1*(th1dot+lam1*th1) + k2*(th2dot+lam2*th2)` | Exact-formula test + parity reference. |
| True super-twisting law `u = u_eq - K1*|s|^(1/2)*sgn(s) + z - d*s` | Behavioral parity vs independent oracle, 400 cases, du=0. |
| Integrator update `z+ = z - K2*sgn(s)*dt + Kaw*(u_sat-u_raw)*dt` | Parity on z (dz=0) + dedicated integrator + anti-windup tests. |
| Moreno-Osorio gain conditions `K1>K2>0` | `validate_gains` (vectorized) enforces `K1>K2>0` + surface positivity (tested). Constructor enforces strict positivity of all six. Config ships `K1=8 > K2=4`. |
| Gain arity | Accepts `[K1,K2]` (defaults surface to 5,3,2,1) or `[K1,K2,k1,k2,lam1,lam2]`; `n_gains=6` (tested). |
| dt / boundary layer | `dt>0`, `boundary_layer>0`, `max_force>0`, `switch_method in {linear,tanh}` validated. |
| Equivalent control | 0 without dynamics model; finite + bounded with a model exposing `_compute_physics_matrices` (Tikhonov-regularized, controllability-guarded). |
| Saturation | u and z both clamped to +/- max_force (numba core). |

## Dependencies (all resolve in beta, no new porting)
`from ..utils.control.primitives import saturate` · `from ..utils import STAOutput, require_positive`. Beta `utils` (M3 s1-7) provides them.

## Carried / deferred
- Standalone class (not `ControllerInterface` ABC) — reconcile in S5 (factory). (DECISIONS #3)
- Dead `_sta_smc_control_numba` cleanup — future hygiene slice. (DECISIONS #6)
- Adaptive (S3), hybrid (S4), factory + `__init__` finalization (S5).
