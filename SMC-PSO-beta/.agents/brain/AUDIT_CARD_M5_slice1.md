# Audit Card — M5 Slice 1: Classical SMC

- **Source:** `SMC-PSO/src/controllers/smc/classic_smc.py` (class `ClassicalSMC`, 26 990 B)
- **Target:** `SMC-PSO-beta/src/controllers/classical_smc.py` (NEW) + `src/controllers/__init__.py` (NEW)
- **Date:** 2026-06-29 · **Gate:** parity OK (structural + 400-case behavioral, maxdiff 0.0) · 14/14 unit tests

## Lens A — AI-slop / structural hygiene
| Check | Finding | Action |
|---|---|---|
| Duplicate implementations | Source ships BOTH the monolith (`smc/classic_smc.py`, used by every factory/runtime path) AND a modular twin (`smc/algorithms/classical/*`, `smc/core/*`) that only contributes `ClassicalSMCConfig`. | **Port monolith; drop modular twin.** (DECISIONS #1) |
| Citation tokens (Trap E) | Monolith docstrings contained CJK-bracket pseudo-citations (`smc_edardar_2015`, `smc_sahamijoo_2016`, `Rhif2012`, numeric IDs, †line refs, etc.). | Stripped via `\u3010[^\u3011]*\u3011`. 0 remain (asserted in tests + parity). Docstring-only; no functional impact. |
| Banner / EOL | Source banner had CRLF + trailing `\\\` mojibake. | Normalized to LF + regenerated 86-col beta banner with the new path. |
| Dead `src.core` imports (Trap B) | None present. | Asserted absent. |
| Interleaved/grouped adapter (Trap A) | `_compute_sliding_surface` unpacks `_, th1, th2, _, dth1, dth2` = canonical GROUPED order already. The `base.py` "interleaved" note referred to the old `base/` package, not this controller. | **No adapter** — confirmed by `test_grouped_state_convention_trap_a`. |

## Lens B — control-theoretic correctness
| Property | Verification |
|---|---|
| Sliding surface `s = lam1*th1 + lam2*th2 + k1*dth1 + k2*dth2` | Exact formula test + parity reference. |
| Reaching law `u = u_eq - K*sat(s/eps) - kd*s`, saturated to `+/-max_force` | Behavioral parity vs independent oracle (dyn=None), 400 cases, diff 0.0. |
| Gain positivity (`k1,k2,lam1,lam2,K > 0`, `kd >= 0`) | Constructor + `validate_gains` (exactly 6 gains) tested. |
| Boundary-layer / switching | `boundary_layer > 0`; `switch_method in {tanh, linear}`; `hysteresis_ratio in [0,1]`; slope >= 0 — all validated. |
| Equivalent control | Returns 0 when no dynamics model; finite + bounded with a model exposing `_compute_physics_matrices` (Tikhonov-regularized, controllability-guarded). |
| Chattering mitigation | tanh vs linear switching both finite & distinct; hysteresis dead-band freezes the robust term for `|s| < ratio*eps0` (tested). |

## Dependencies (all resolve in beta, no new porting)
`from ..utils.control.primitives import saturate` · `from ..utils import ClassicalSMCOutput, require_positive`. Beta `utils` (M3 s1-7) provides byte-equivalent signatures (`saturate(sigma, epsilon, method, slope=3.0)`, `require_positive(value, name, *, allow_zero=False)`).

## Carried / deferred
- Standalone class does **not** yet implement beta `base.py` `ControllerInterface` ABC (different `compute_control` contract). Reconciled in **S5** (factory). See DECISIONS #3.
- STA / adaptive / hybrid / factory ports: M5 S2-S5.
