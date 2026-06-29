# Audit Card — M4 Slice 3: simulation/integrators

**Milestone:** M4 · **Slice:** 3 of 6 · **Verdict:** PASS (gate green)

## Scope ported
`src/simulation/integrators/` (full subpackage):
`base.py` (BaseIntegrator + IntegrationResult), `factory.py`, `compatibility.py`,
`fixed_step/{euler,runge_kutta}.py`, `discrete/zero_order_hold.py`,
`adaptive/{runge_kutta,error_control}.py`, and the four `__init__.py` files.
Source: `SMC-PSO/src/simulation/integrators/`. Deps: `..core.interfaces` (Slice 2) + numpy + scipy.

## Headline: zero functional edits
The integrators depend only on the already-ported `core.interfaces` plus numpy/scipy,
so **no source changes were required**. The only transform is cosmetic banner
normalization (strip trailing `\\\` on `#===` lines; CRLF->LF). Proven: all
non-banner / non-EOF bytes are identical to source across all 12 files (36 banner
lines normalized). See `scripts/parity_check_m4_slice3.py --source`.

## Lens A — AI-slop / code defects
- Banners normalized to Slice 1/2 style.
- No hallucinated citation tokens in the integrators/ files. NOTE: the *legacy*
  `engines/adaptive_integrator.py` (NOT ported here — engines = Slice 5) DOES contain
  AI-slop citation tokens `【313837333132264†L58-L82】` (Trap E). Flag for Slice 5: the
  ported `integrators/adaptive/runge_kutta.py::rk45_step` is the clean replacement.
- S3-3 (P3): `factory.get_integrator_info()` reads `getattr(cls, 'ORDER')` (always None;
  order is a lowercase instance property) and derives `adaptive` from a substring of the
  type name (wrong for `dp45`/`dormand_prince`). Metadata helper only, not on the critical
  path. Left as-is to preserve parity; deferred.
- S3-4 (P3): `ZeroOrderHold.order` returns `float('inf')` though the ABC types `order -> int`.
  Semantically intended (exact for LTI). Kept; documented; test asserts `== inf`.
- P3: `IntegratorSafetyWrapper` uses `print()` instead of logging. Kept (parity); deferred.
- P3 (DRY): `compatibility.create_compatible_dynamics` / `create_safe_integrator` keep a
  second small integrator registry separate from `factory._integrator_registry`. Kept; deferred.

## Lens B — scientific / correctness
| ID | Sev | Finding | Resolution |
|----|-----|---------|------------|
| S3-1 | P1->resolved | **Carried watch-item S2-2.** Adaptive step control must scale the error exponent with method order. | `ErrorController.update_step_size(order=...)` correctly uses `(tol/err)**(1/order)` (accept) and `1/(order+1)` (reject); `DormandPrince45` passes `order=5`. The integrator adaptive path is order-correct. Pinned by `test_error_controller_is_order_aware`. The standalone `core/time_domain.AdaptiveTimeStep` (1/4 hard-code) is **superseded** by `ErrorController` and is NOT used by integrators — see S3-2. |
| S3-2 | P2 | `core/time_domain.AdaptiveTimeStep` (Slice 2) still hard-codes the 1/4 exponent and is not order-aware. | Not used on the integrator path. Recommend deprecating it (or routing it through `ErrorController`) when engines/orchestrators wire adaptive stepping in **Slice 5**. Logged as the new carried watch-item. |
| S3-3 | P2 | Error-norm convention differs between the new `DormandPrince45` (RMS norm via `_compute_error_norm`, scale on the OLD state) and the legacy `rk45_step`/`_original_rk45_step` (L2 `np.linalg.norm`, scale on `max(|y|,|y5|)`). | The propagated 5th-order state `y5` is **identical** for an accepted step (formula parity), only `suggested_dt`/accept-threshold differ. Pinned by `test_dp45_state_parity_with_legacy_rk45_step`. Documented as expected refactor; no action. |

Numerics verified correct: RK4/DP45 vs `exp` (1e-8 / 1e-10), Forward/Backward Euler
formulas, RK2<RK4 accuracy, RK 3/8 order 4, ZOH diagonal closed form + ZOH-exact vs
fine RK4 (1e-6), Dormand-Prince Butcher tableau matches the legacy explicit stages.

## Trap decisions
- **Trap D (legacy aliases in `simulation/__init__`):** still deferred. `rk45_step` ships
  *inside* `integrators/adaptive/runge_kutta.py` (where source defines it) — that is correct
  and self-contained. The package-level `simulation/__init__` re-exports stay deferred until
  Slices 4-6 land. `simulation/__init__.py` docstring updated to note integrators now exist.
- **Trap E (AI-slop citations):** none in integrators/; flagged for Slice 5 engines/.
- **Scope:** `engines/adaptive_integrator.py` deliberately NOT ported (Slice 5).

## Gate evidence
- Structural parity: banner-only diff vs source (no functional drift) across 12 files.
- Import smoke: `import src.simulation.integrators` OK with only `src.config` (stub) + core +
  numpy/scipy; no orchestrators/safety/results/strategies/engines pulled into `sys.modules`.
- Unit tests: see gate run (fixed_step, adaptive, discrete, factory, compatibility, import).
- Numerical correctness: `parity_check_m4_slice3.py` -> PARITY OK.

## Gate checklist
- [x] P0 = 0, P1 = 0 (S3-1 resolved)
- [x] Structural parity vs source (banner-only)
- [x] Numerical correctness vs analytic references
- [x] Order-awareness of adaptive control asserted by a test
- [x] No imports from deprecated `src/core/`
- [x] Findings logged to `AUDIT_LEDGER.md`
