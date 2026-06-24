# AUDIT CARD -- src/utils/ (M3 slice 1: types + validation)

> Covers the M3 FIRST SLICE only: `src/utils/control/types/` and
> `src/utils/control/validation/`. The wider utils module (analysis,
> infrastructure, monitoring, numerical_stability, testing, visualization,
> control.primitives) is deferred to later M3 slices, so the module stays [WIP].
> ASCII markers only. Severities: [P0] wrong/unsafe, [P1] bug, [P2] slop, [P3] nit.

- **Module:** `src/utils/control/{types,validation}/`
- **Source ref:** `SMC-PSO/src/utils/control/{types,validation}/`
- **Branch:** `main` (no migration branch -- Delivery Standard 5.5)
- **Date / session:** 2026-06-24 / Session 4
- **Status:** [WIP]  (slice 1 ACCEPTED; module not complete)

## Lens A -- AI-slop / code quality
| # | File:line | Finding | Sev | Fix / status |
|---|-----------|---------|-----|--------------|
| A1 | src/utils/__init__.py | Source top-level __init__ re-exports 7 not-yet-ported subpackages (analysis, infrastructure, monitoring, numerical_stability, testing, visualization) plus saturate / set_global_seed / Visualizer. A verbatim port would raise ImportError on first import. | P1 | RESOLVED -- shipped a slice-scoped __init__ that exposes ONLY control.types + control.validation. Widen in later slices as each domain lands. |
| A2 | control/types/control_outputs.py (References) | Citation gives "vol. 4, no. 7 ... 2005". The paper is real but the issue number is wrong: JOT vol. 4, no. 5 (July 2005), pp. 75-94. | P2 | FIXED -- corrected no. 7 -> no. 5 and added the verified JOT issue URL. Authenticity confirmed via JOT, Springer, ACM. (W1-style citation fix.) |
| A3 | control/types/control_outputs.py (docstrings) | Docstring/annotation drift: ClassicalSMCOutput doc says Tuple[(), ...] vs annotation Tuple[Any, ...]; STAOutput doc Tuple[float, float] vs ann Tuple[float, ...]; HybridSTAOutput doc Tuple[float, float, float] vs ann Tuple[float, ...]. | P3 | FLAG-ONLY -- ported faithfully (cosmetic). Fix in a docs pass. |
| A4 | all ported files | Source used non-ASCII (smart quotes, en/em dashes, non-breaking hyphens, >= glyph) violating D8 ASCII-only. | P3 | FIXED -- normalized to ASCII during port. |

## Lens B -- scientific / mathematical correctness
| # | What it should match | Finding | Sev | Fix / status |
|---|----------------------|---------|-----|--------------|
| B1 | require_positive / require_finite input typing | isinstance(value, (int, float)) accepts bool (bool subclasses int), so require_positive(True, ...) returns 1.0. Control gains should not be booleans. | P3 | FLAG-ONLY -- faithful port. Consider explicit bool rejection in a hardening pass. |
| B2 | validation semantics | Verified correct: require_positive (strict vs allow_zero, rejects None/NaN/inf), require_finite (rejects None/NaN/inf), require_in_range (inclusive vs exclusive bounds), require_probability ([0,1] inclusive). Units/bounds reasoning sound. | OK | PASS -- exercised by tests. |

## Lens C -- tests + numeric parity
- [x] Real tests with real assertions added: tests/test_utils/test_control_validation.py (14 tests), tests/test_utils/test_control_types.py (4 tests).
- [x] All 18 tests pass (sandbox-verified, 18 passed / 0 failed).
- [x] Property/invariant tests: require_positive returns input-as-float across a sample; inclusive/exclusive boundary behavior for require_in_range; probability unit-interval boundaries.
- [ ] Coverage tool not run in sandbox (no pytest-cov); happy + boundary + error paths are exhaustively hit by the suite. Run `pytest --cov` in the real env to record the number.
- Parity: N/A -- pure validation/types, no numerical trajectory to compare. M2.v5 golden parity is unrelated and still open.

## Dedupe vs core/ (FLAG-ONLY, no refactor this pass)
| # | New util | Overlaps | Sev | Action |
|---|----------|----------|-----|--------|
| UTILS-DEDUP-1 | control.validation.require_positive / require_finite | src/plant/configurations/validation.py :: PhysicsParameterValidator.validate_numerical_parameter and inline isinstance/isfinite/positivity checks | P2 | Flag-only. Generic primitives vs class-based domain validators. Do NOT consolidate this pass. |
| UTILS-DEDUP-2 | control.validation.require_in_range | src/plant/configurations/validation.py validate_numerical_parameter(min,max); src/config/schemas.py pydantic range validators | P2 | Flag-only. Revisit consolidation in a dedicated pass. |
| -- | (note) | src/core/, src/optimizer/, src/deprecated/ are deprecated shims -- not compared, not ported. | -- | -- |

## Gate decision
- [x] [P0] = 0 open
- [x] [P1] = 0 open (A1 resolved)
- [x] Parity pass (N/A -- documented)
- [x] Coverage gate: paths fully exercised (numeric % to be recorded in real env)
- [x] No emojis / no `python3` / no stray magic numbers
- **Decision:** ACCEPT slice 1 (types + validation) to main. Module `utils` remains [WIP] -- remaining slices: control.primitives, analysis, infrastructure, monitoring, numerical_stability, testing, visualization (logging/metrics/viz deferred per NEXT.md).
- **Notes / deliberate divergences (-> DECISIONS.md):**
  - Slice-scoped src/utils/__init__.py instead of the source's full re-export (A1) -- necessary because dependent subpackages are not ported yet.
  - Citation issue-number corrected (A2).
  - ASCII normalization applied (A4).

## Watch-items carried in (unchanged)
- M2.v5 [P2/OPEN]: golden source-parity for plant never run.
- F-PLANT-2, F-PLANT-3 [P2/OPEN]: revisit at M4.
- plant.A7 [P2/OPEN]: simplified-model inertia fudge (deferred per D9).
