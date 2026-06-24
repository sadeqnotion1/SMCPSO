# Utils Migration Audit Card

Scope: porting `src/utils/` from the source repo into beta, one slice at a time.
Each slice ports a faithful copy of the real source, ASCII-normalized and with
beta import conventions, plus tests and findings. Findings use severities
[P0] wrong/unsafe, [P1] bug, [P2] slop, [P3] nit.

Status: M3 WIP. Slices accepted: 1 (types+validation), 2 (control.primitives /
saturation), 3 (testing.reproducibility / seeding), 4 (numerical_stability /
safe operations).

---

## Slice 1 - control types + validation  [ACCEPTED]

Files: `control/types.py` (4 NamedTuples), `control/validation/parameter_validators.py`,
`control/validation/range_validators.py`, package `__init__`s.

Findings: U1..U4 (see AUDIT_LEDGER). All [P2/P3], 0x P0/P1. Drop-in, faithful.

---

## Slice 2 - control.primitives / saturation  [ACCEPTED]

Files: `control/primitives/saturation.py` (`saturate`, `smooth_sign`, `dead_zone`),
package `__init__`s.

- S2-A1 [P3] banner non-ASCII / artifacts -> normalized.
- S2-A2 [P3] unused import -> left verbatim, flagged.
- S2-A3 [P2] docstring formula `tanh((slope*sigma)/epsilon)` disagrees with code
  `tanh(sigma/(epsilon*slope))`; "lower slope = smoother" is backwards. Ported
  verbatim; tests assert the REAL behavior.
- S2-A4 [P3] magic 700 overflow clamp in tanh path (duplicated as EPSILON_EXP in
  slice 4 - see UTILS-DEDUP note).

14 tests. 0x P0/P1.

---

## Slice 3 - testing.reproducibility / seeding  [ACCEPTED]

Files: `testing/reproducibility/seed.py` (`set_global_seed`, `SeedManager`,
`create_rng`), `testing/reproducibility/__init__.py` (+`set_seed` alias, dummy
`with_seed`, dummy `random_seed_context`), `testing/__init__.py`, package `__init__`s.

- S3-A1..A2 [P3] banner / import path normalization.
- S3-A3 [P2 FIXED] docstrings contained hallucinated web-citation artifacts
  (e.g. fancy-bracket reference codes) with no real bibliography -> markers removed,
  prose kept.
- S3-A4 [P2 FLAG] dummy shims `with_seed` (no-op, ignores seed) and
  `random_seed_context` (dead restore: `old_seed=None`, never restores) -> ported
  verbatim, flagged for follow-up when the real impls are ported.
- S3-A5 / S3-B4 see ledger.
- UTILS-DEDUP-4 [P2 FLAG] top-level `src/utils/seed.py` duplicates
  `testing/reproducibility/seed.py` - reconcile when top-level helpers are ported.

12 tests. 0x P0/P1.

---

## Slice 4 - numerical_stability / safe operations  [ACCEPTED]

Files (NEW unless noted):
- `src/utils/numerical_stability/safe_operations.py` (faithful port)
- `src/utils/numerical_stability/__init__.py` (faithful API surface)
- `src/utils/__init__.py` (UPDATED: + `numerical_stability`, v0.4.0-m3slice4)
- `tests/test_utils/test_numerical_stability.py` (31 tests)

API: `safe_divide, safe_reciprocal, safe_sqrt, safe_log, safe_exp, safe_power,
safe_norm, safe_normalize`; constants `EPSILON_DIV (1e-12), EPSILON_SQRT (1e-15),
EPSILON_LOG (1e-15), EPSILON_EXP (700.0)`; utils `is_safe_denominator,
clip_to_safe_range`.

### Lens A - surface / hygiene
| # | File:loc | Finding | Sev | Action |
|---|----------|---------|-----|--------|
| S4-A1 | safe_operations.py banner + docstrings | non-ASCII glyphs (approx, epsilon, sqrt, inf, x, dot, arrows) and a trailing-backslash banner artifact | P3 | FIXED - ASCII-normalized; banner rebuilt |
| S4-A2 | safe_operations.py safe_sqrt docstring | example outputs are wrong: claims `safe_sqrt(-0.001) -> 1e-07`, but with default `min_value=1e-15` the result is `sqrt(1e-15) ~= 3.16e-8` (1e-7 would require min_value=1e-14) | P2 | FLAG - docstring kept verbatim; test asserts the true value |
| S4-A3 | numerical_stability/__init__.py | source used absolute `from src.utils.numerical_stability.safe_operations import ...`, which breaks under beta import root (`src/`, top package `utils`); docstring example used same stale `src.` prefix | P2 | FIXED - converted to relative `from .safe_operations import ...`; docstring example -> `from utils.numerical_stability import ...` |
| S4-A4 | safe_operations.py safe_divide | dead/redundant code: `result = np.zeros_like(...)` then `result[zero_mask] = fallback` is fully overwritten by the later `result = np.where(zero_mask, fallback, result_temp)` (only the warn side-effect matters) | P3 | FLAG - ported verbatim |
| S4-A5 | safe_operations.py | `EPSILON_GENERAL = 1e-10` defined but never used and not exported in `__all__` | P3 | FLAG - ported verbatim |

### Lens B - math / correctness
| # | Op | Verified behavior | Result |
|---|----|-------------------|--------|
| S4-B1 | safe_divide | normal a/b; near-zero -> a/(epsilon)*sign(b); exact 0 -> fallback; sign preserved for negative near-zero | OK |
| S4-B2 | safe_sqrt / safe_log | clip to [min_value, inf): sqrt(max(x,1e-15)), ln(max(x,1e-15)); safe_log(0)=ln(1e-15)~=-34.539 | OK |
| S4-B3 | safe_exp | exp(min(x,700)); safe_exp(1000)=exp(700) | OK |
| S4-B4 | safe_power | |b|^e with small-base floor + exp clip; sign applied ONLY for odd integer exponents; even/fractional -> principal positive value | OK (documented) |
| S4-B5 | safe_norm / safe_normalize | norm floored at min_norm; normalize divides by safe_norm; zero-vector -> zeros (or fallback) | OK |
| S4-B6 | is_safe_denominator / clip_to_safe_range | `|x| >= epsilon`; clip to [-1e10, 1e10] | OK |

No P0/P1 in math: every safe operation matches its stated contract. Note S4-B4 -
for negative base with even/fractional exponent the function returns the positive
principal value by design (not a complex result); documented, not a bug.

### Dedup watch
- UTILS-DEDUP-5 [P2 FLAG, low-confidence] `EPSILON_EXP = 700.0` here duplicates the
  hard-coded `700` overflow clamp in slice-2 `control/primitives/saturation.py`
  (S2-A4). When more numerical helpers land, consider centralizing the overflow
  constant. No action this slice.

### Lens C - tests
31 tests in `test_numerical_stability.py` covering: constants; safe_divide (normal,
near-zero, sign, exact-zero fallback, array broadcast, epsilon<=0 raises);
safe_reciprocal; safe_sqrt (normal, negative-clip true value, negative min_value
raises); safe_log (normal, zero-clip, non-positive min_value raises); safe_exp
(normal, overflow clip); safe_power (normal, negative odd, negative even, small-base
floor); safe_norm (euclidean, floor, axis); safe_normalize (unit, zero vector, axis);
is_safe_denominator (scalar/array); clip_to_safe_range (scalar/array); package
namespace wiring.

### Gate
- P0 = 0, P1 = 0
- Imports resolve under beta convention (relative import fix applied)
- No emojis, no `python3`, ASCII-only
- Coverage: all 14 public symbols exercised
=> ACCEPT

Combined utils suite after slice 4: 18 (s1) + 14 (s2) + 12 (s3) + 31 (s4) = 75 tests.
