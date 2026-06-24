# AUDIT CARD -- src/utils/ (M3, multi-slice)

> Tracks the M3 utils port slice by slice. ASCII markers only.
> Severities: [P0] wrong/unsafe, [P1] bug, [P2] slop, [P3] nit.

- **Module:** `src/utils/`
- **Source ref:** `SMC-PSO/src/utils/`
- **Branch:** `main` (no migration branch -- Delivery Standard 5.5)
- **Status:** [WIP]  (slices 1-2 accepted; module not complete)
- **Slices done:** 1 = control types + validation; 2 = control.primitives (saturation)
- **Slices remaining:** control seeding/testing.reproducibility, analysis, infrastructure, monitoring, numerical_stability, testing, visualization

---

## SLICE 1 -- control/types + control/validation  (2026-06-24, ACCEPTED)

### Lens A -- AI-slop / code quality
| # | File:line | Finding | Sev | Fix / status |
|---|-----------|---------|-----|--------------|
| A1 | src/utils/__init__.py | Source top-level __init__ re-exports 7 not-yet-ported subpackages + saturate/set_global_seed/Visualizer; verbatim port would ImportError. | P1 | RESOLVED -- slice-scoped __init__ exposing only ported items; widen per slice. |
| A2 | control/types/control_outputs.py (References) | Citation "vol. 4, no. 7 ... 2005" wrong issue. Real: JOT vol. 4, no. 5 (July 2005), pp. 75-94. | P2 | FIXED -- no.7 -> no.5 + verified JOT URL. |
| A3 | control/types/control_outputs.py (docstrings) | Docstring/annotation drift (Tuple[(),...] / Tuple[float,float] / Tuple[float,float,float] vs Tuple[Any,...]/Tuple[float,...]). | P3 | FLAG-ONLY -- faithful port. |
| A4 | all ported files | Non-ASCII (smart quotes, dashes, >= glyph) vs D8. | P3 | FIXED -- ASCII normalized. |

### Lens B -- correctness
| # | What | Finding | Sev | Status |
|---|------|---------|-----|--------|
| B1 | require_positive / require_finite | isinstance(value,(int,float)) accepts bool (True->1.0). | P3 | FLAG-ONLY. |
| B2 | validator semantics | strict/allow_zero, None/NaN/inf rejection, inclusive/exclusive range, probability [0,1] all correct. | OK | PASS. |

### Lens C -- tests
- 18 tests (14 validation + 4 types), all pass.

### Dedupe (FLAG-ONLY)
- UTILS-DEDUP-1 [P2]: control.validation.require_positive/require_finite overlaps plant/configurations/validation.py PhysicsParameterValidator. Do NOT consolidate.
- UTILS-DEDUP-2 [P2]: control.validation.require_in_range overlaps plant validate_numerical_parameter(min,max) + config/schemas.py pydantic validators. Flag-only.

### Gate: P0=0, P1=0 -> ACCEPT slice 1.

---

## SLICE 2 -- control/primitives (saturation)  (2026-06-24, ACCEPTED)

Source: `SMC-PSO/src/utils/control/primitives/{__init__,saturation}.py`.
Scope note: the source `primitives/` dir contains ONLY `saturation.py` (saturate,
smooth_sign, dead_zone). "Seeding" (set_global_seed) is NOT here -- it lives in
`testing/reproducibility/seed.py` and belongs to the later `testing` slice. NEXT.md's
"saturation, seeding" wording is corrected by this slice (see APPLY step 5).

### Lens A -- AI-slop / code quality
| # | File:line | Finding | Sev | Fix / status |
|---|-----------|---------|-----|--------------|
| S2-A1 | primitives/saturation.py (banner) | Banner path read `src/utils/control/saturation.py`; actual is `.../primitives/saturation.py`. | P3 | FIXED -- banner path corrected. |
| S2-A2 | primitives/saturation.py | Non-ASCII in docstrings/comments (sigma glyph, non-breaking hyphens, `->` arrows). | P3 | FIXED -- ASCII normalized (behavior unchanged). |
| S2-A3 | primitives/saturation.py `saturate` docstring | DOUBLE doc/code mismatch about `slope`: (1) docstring formula says `tanh((slope*sigma)/epsilon)` but code computes `tanh(sigma/(epsilon*slope))` (divides, not multiplies); (2) docstring says "Lower values (2-5) provide smoother transitions" and "steep slopes (10+) behaved like discontinuous", but mathematically a LARGER slope shrinks the argument => gentler/smoother, and SMALLER slope => steeper/more sign-like. The inline comments are CORRECT; the docstring is misleading. | P2 | FLAG-ONLY -- ported verbatim (ASCII only), behavior unchanged. Recommend author reconcile docstring wording/formula. Tests assert the ACTUAL behavior (higher slope = gentler). |
| S2-A4 | primitives/__init__.py | `from .saturation import *` with no `__all__` in saturation leaks np/warnings/Literal/Union into the primitives namespace; and primitives `__all__ = []` means `from primitives import *` exports nothing. Direct imports still work. | P3 | FLAG-ONLY -- faithful port. |

### Lens B -- scientific / mathematical correctness
| # | What it should match | Finding | Sev | Status |
|---|----------------------|---------|-----|--------|
| S2-B1 | tanh boundary-layer switching | `tanh(clip(sigma/(epsilon*slope), -700, 700))`: bounded in (-1,1), odd, overflow-guarded, saturates to +/-1 for large \|sigma\|. Correct continuous sign approximation. | OK | PASS (tests). |
| S2-B2 | linear method | `clip(sigma/epsilon, -1, 1)` + RuntimeWarning. Correct piecewise-linear saturation. | OK | PASS. |
| S2-B3 | dead_zone | `0` for \|x\|<=threshold else `x - threshold*sign(x)` (unity-slope dead zone); rejects threshold<=0; scalar->float, array->array. Correct. | OK | PASS. |
| S2-B4 | smooth_sign | Delegates to saturate(method=tanh); sign(0)=0. Correct. | OK | PASS. |

### Lens C -- tests + numeric parity
- [x] 14 new tests in tests/test_utils/test_control_primitives.py (epsilon guard, unknown-method guard, zero, tanh bounded+odd, slope-monotonicity reflecting REAL behavior, linear clip+warn, array shape preservation, overflow guard, smooth_sign==saturate, dead-zone guards/shift/scalar/array, convenience re-export identity).
- [x] Full suite (slice 1 + slice 2) = 32 tests, all pass (sandbox-verified with numpy).
- Parity: N/A -- deterministic primitives, no stored golden trajectory. (M2.v5 golden parity unrelated, still open.)

### Dedupe (FLAG-ONLY)
- UTILS-DEDUP-3 [P2, low-confidence]: switching/saturation logic may be reimplemented inside individual controllers; couldn't grep (tool disabled). Watch-item: controllers should import `utils.control.primitives.saturate` rather than rolling their own. Do NOT consolidate this pass.

### Gate: P0=0, P1=0 -> ACCEPT slice 2. Module `utils` remains [WIP].
- Deliberate divergences (-> DECISIONS.md): slice-scoped __init__ widened to add primitives + `saturate` backward-compat re-export; banner path corrected (S2-A1); ASCII normalization (S2-A2).

---

## Watch-items carried in (unchanged)
- M2.v5 [P2/OPEN]: golden source-parity for plant never run.
- F-PLANT-2, F-PLANT-3 [P2/OPEN]: revisit at M4.
- plant.A7 [P2/OPEN]: simplified-model inertia fudge (deferred per D9).
