# AUDIT CARD -- src/utils/ (M3, multi-slice)

> Tracks the M3 utils port slice by slice. ASCII markers only.
> Severities: [P0] wrong/unsafe, [P1] bug, [P2] slop, [P3] nit.

- **Module:** `src/utils/`
- **Source ref:** `SMC-PSO/src/utils/`
- **Branch:** `main` (no migration branch -- Delivery Standard 5.5)
- **Status:** [WIP]  (slices 1-3 accepted; module not complete)
- **Slices done:** 1 = control types + validation; 2 = control.primitives (saturation); 3 = testing.reproducibility (seeding)
- **Slices remaining:** testing.dev_tools, testing.fault_injection, analysis, infrastructure, monitoring, numerical_stability, visualization, top-level helpers (config_compatibility, control_analysis, disturbances, model_uncertainty, seed, streamlit_theme)

---

## SLICE 1 -- control/types + control/validation  (2026-06-24, ACCEPTED)

### Lens A
| # | File:line | Finding | Sev | Fix |
|---|-----------|---------|-----|-----|
| A1 | src/utils/__init__.py | Verbatim top-level __init__ re-exports unported domains -> ImportError. | P1 | RESOLVED -- slice-scoped __init__. |
| A2 | control/types/control_outputs.py | Citation "vol. 4, no. 7" wrong; real JOT vol. 4, no. 5 (2005). | P2 | FIXED + verified URL. |
| A3 | control/types/control_outputs.py | Docstring/annotation drift on state tuples. | P3 | FLAG-ONLY. |
| A4 | all | Non-ASCII chars vs D8. | P3 | FIXED. |

### Lens B
- B1 [P3 FLAG]: validators accept bool as number. B2 [OK]: semantics correct.

### Lens C: 18 tests pass (14 validation + 4 types).
### Dedupe: UTILS-DEDUP-1, UTILS-DEDUP-2 [P2 FLAG-ONLY] (overlap with plant/config validators).
### Gate: P0=0, P1=0 -> ACCEPT.

---

## SLICE 2 -- control/primitives (saturation)  (2026-06-24, ACCEPTED)

### Lens A
| # | File | Finding | Sev | Fix |
|---|------|---------|-----|-----|
| S2-A1 | primitives/saturation.py | Banner path wrong (`control/saturation.py`). | P3 | FIXED. |
| S2-A2 | primitives/saturation.py | Non-ASCII (sigma glyph, nb-hyphens, arrows). | P3 | FIXED. |
| S2-A3 | primitives/saturation.py `saturate` | Docstring contradicts code+inline-comments about `slope` (formula says multiply, code divides; "lower=smoother" backwards). | P2 | FLAG-ONLY (verbatim port; tests assert real behavior). |
| S2-A4 | primitives/__init__.py | `from .saturation import *` + no __all__ leaks names; primitives `__all__=[]`. | P3 | FLAG-ONLY. |

### Lens B: saturate (tanh/linear), smooth_sign, dead_zone all verified correct.
### Lens C: 14 new tests; full suite 32 pass.
### Dedupe: UTILS-DEDUP-3 [P2 FLAG, low-confidence] (controllers may reimplement saturation).
### Gate: P0=0, P1=0 -> ACCEPT.

---

## SLICE 3 -- testing/reproducibility (seeding)  (2026-06-24, ACCEPTED)

Source: `SMC-PSO/src/utils/testing/reproducibility/{__init__,seed.py}`.
Scope: ONLY the `reproducibility` subpackage. `testing.dev_tools` and
`testing.fault_injection` are deferred to later slices. `set_global_seed` is now
re-exported at the `utils` top level (source backward-compat).

### Lens A -- AI-slop / code quality
| # | File:line | Finding | Sev | Fix / status |
|---|-----------|---------|-----|--------------|
| S3-A1 | seed.py + reproducibility/__init__.py banners | Banner paths missing the `testing/` segment (read `src/utils/reproducibility/...`). | P3 | FIXED -- corrected to `src/utils/testing/reproducibility/...`. |
| S3-A2 | seed.py | Non-ASCII: smart quotes, non-breaking hyphens (pseudo-random, 32-bit, built-in). | P3 | FIXED -- ASCII normalized. |
| S3-A3 | seed.py docstrings (3 sites) | HALLUCINATED CITATION ARTIFACTS of the form `<CJK-bracket>675644021986605 + dagger + L385-L388<CJK-bracket>` -- they reference no bibliography in the file and are LLM web-citation cruft (a clear AI-slop tell). | P2 | FIXED -- removed the bogus markers (kept the surrounding prose). No real source was discarded; there was no References section. |
| S3-A4 | reproducibility/__init__.py | Two "dummy" backward-compat shims: `with_seed(seed)` is a no-op decorator that IGNORES `seed` entirely (never seeds before the wrapped call), and `random_seed_context(seed)` has DEAD restore code (`old_seed = None` then `if old_seed is not None` is never true) -- it seeds on enter but never restores prior state on exit. | P2 | FLAG-ONLY -- ported verbatim (faithful). Recommend implementing properly or removing if unused. Tests document the actual (no-restore) behavior. |
| S3-A5 | seed.py `set_global_seed` docstring example | Stale import path `from src.utils.seed import set_global_seed`. | P3 | FIXED -- corrected to `from utils.testing.reproducibility import set_global_seed`. |

### Lens B -- scientific / mathematical correctness
| # | What | Finding | Sev | Status |
|---|------|---------|-----|--------|
| S3-B1 | set_global_seed | Seeds Python `random` + NumPy legacy global RNG; `None` is a no-op; int coercion guarded by try/except. Reproducible. | OK | PASS (tests). |
| S3-B2 | SeedManager.spawn | Deterministic 32-bit seeds derived from master Generator; records `history`; range [0, 2**32-2]. | OK | PASS. |
| S3-B3 | create_rng | Deterministic `default_rng(int(seed))`; `None` -> fresh generator; invalid seed -> fallback generator. | OK | PASS. |
| S3-B4 | set_global_seed | Uses NumPy LEGACY global `np.random.seed` (RandomState), not the modern Generator API. Acceptable for backward-compat; modern code should prefer `create_rng`/`SeedManager`. | P3 | FLAG-ONLY (nit). |

### Lens C -- tests + parity
- [x] 12 new tests in tests/test_utils/test_reproducibility.py: global-seed reproducibility, None=no-op stream semantics, SeedManager determinism/history/range, None master seed, create_rng determinism/None/invalid-fallback, set_seed alias identity, with_seed identity-decorator, random_seed_context seeds-within-block, package + top-level export alignment.
- [x] Full suite (slices 1+2+3) = 44 tests, all pass (sandbox-verified, numpy 2.4.6).
- Parity: N/A (deterministic seeding utilities; M2.v5 golden parity unrelated, still open).

### Dedupe (FLAG-ONLY)
- UTILS-DEDUP-4 [P2, low-confidence]: the source also has a TOP-LEVEL `src/utils/seed.py` (not ported in this slice) alongside `testing/reproducibility/seed.py`. Possible duplicate seeding logic + the wrong banner paths suggest a prior file move. Watch-item: reconcile the two seed modules when the top-level utils helpers are ported. Do NOT consolidate this pass.

### Gate: P0=0, P1=0 -> ACCEPT slice 3. Module `utils` remains [WIP].
- Deliberate divergences (-> DECISIONS.md): slice-scoped `testing/__init__` (only reproducibility); widened utils `__init__` (+testing, +set_global_seed re-export, v0.3.0-m3slice3); removed hallucinated citation markers (S3-A3); corrected banner + docstring import paths (S3-A1/A5).

---

## Watch-items carried in (unchanged)
- M2.v5 [P2/OPEN]: golden source-parity for plant never run.
- F-PLANT-2, F-PLANT-3 [P2/OPEN]: revisit at M4.
- plant.A7 [P2/OPEN]: simplified-model inertia fudge (deferred per D9).
