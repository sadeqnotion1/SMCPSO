# Audit Card — M5 Slice 3: Adaptive SMC

- **Source:** `SMC-PSO/src/controllers/smc/adaptive_smc.py` (class `AdaptiveSMC`, sha `d8a2db6c…`)
- **Target:** `SMC-PSO-beta/src/controllers/adaptive_smc.py` (NEW, sha `0e82cf55a249`) + widened `src/controllers/__init__.py`
- **Date:** 2026-06-30 · **Gate:** parity OK (structural + 400-case behavioral, du=dK=dt_sld=0.0) · 22/22 unit tests

## Lens A — AI-slop / structural hygiene
| Check | Finding | Action |
|---|---|---|
| Duplicate implementations | Source ships the monolith (`smc/adaptive_smc.py`, imported by `factory/base.py:192` and source `__init__.py:51`) AND a modular twin (`smc/algorithms/adaptive/*`) whose `controller.py` re-exports `AdaptiveSMC` for back-compat (`ModularAdaptiveSMC`); the factory registry only consumes the twin's `AdaptiveSMCConfig`. | **Port monolith; drop modular twin.** (DECISIONS #1) |
| numba | None in this module (pure numpy). | n/a — simpler than classical/STA. |
| Citation tokens (Trap E) | 2 multi-line CJK-bracket pseudo-citations in the class docstring (Plestan 2010, Roy 2020). | Stripped via `\u3010[^\u3011]*\u3011`; 0 remain (asserted). Docstring-only. |
| Banner / EOL | CRLF + trailing `\\\` mojibake on banner lines. | Normalized to LF + regenerated 86-col beta banner. |
| Repeated inline imports | `require_positive` re-imported via try/except in 4 places; `saturate` once inside `compute_control`. | Preserved verbatim (behavior-preserving); only the `...utils` dot-depth relocated. |
| Trap B (`src.core`) | None. | Asserted absent. |
| Trap A (state order) | `compute_control` unpacks `x, theta1, theta2, x_dot, theta1_dot, theta2_dot = state` = canonical GROUPED. | **No adapter** — `test_grouped_state_convention_trap_a`. |

## Lens B — control-theoretic correctness
| Property | Verification |
|---|---|
| Sliding surface `s = k1*(th1dot+lam1*th1) + k2*(th2dot+lam2*th2)` | Exact-formula test (via `out.sigma`) + parity reference. |
| Control law `u = -K*sat(s/eps) - alpha*s` (clamped) | Behavioral parity vs independent oracle, 400 cases, du=0; reference test for tanh + linear switching. |
| Dead-zone gating: `dK=0` for `|s|<=dead_zone`, else `dK=gamma*|s| - leak*(K-K0)` | Frozen-inside + active-outside tests + parity on K (dK=0). |
| Rate limiting `dK = clip(dK, +/- adapt_rate_limit)` | Dedicated clamp test + parity. |
| Gain envelope `K^+ = clip(K + dK*dt, K_min, K_max)` | K-max clamp test + parity (dK=0 over 400 cases). |
| Constructor validation | `dt, max_force, K_min, K_max, boundary_layer > 0`; `leak_rate, adapt_rate_limit, dead_zone >= 0`; `K_min <= K_init <= K_max`. All tested. |
| Gain arity | `validate_gains` (STATIC) requires >=5 gains, all of `k1,k2,lam1,lam2,gamma > 0`; extras tolerated (stored, ignored). |
| time-in-sliding counter | `+dt` while `|s|<=boundary_layer`, resets to 0 otherwise (tested + parity). |
| Output contract | `AdaptiveSMCOutput(u, (new_K, u, time_in_sliding), history, sigma)`; history keys `K, sigma, u_sw, dK, time_in_sliding`. |

## Dependencies (all resolve in beta, no new porting)
`from ..utils import AdaptiveSMCOutput, require_positive` · `from ..utils.control.primitives import saturate`. Beta `utils` (M3 s1-7) provides them.

## Carried / deferred
- Standalone class (not `ControllerInterface` ABC) — reconcile in S5 (factory). (DECISIONS #3)
- Modular `AdaptiveSMCConfig` wiring — S5 (factory).
- Hybrid (S4); factory + `__init__` finalization (S5).
