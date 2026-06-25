# Utils Migration Audit Card (M3)

Scope: porting `src/utils/` from the source repo (`SMC-PSO/`) into the beta repo
(`SMC-PSO-beta/`), slice by slice. Each slice = one cohesive subpackage, ported
faithfully (ASCII-normalized, drop-in), audited (Lens A/B/C), and tested.

Severity legend: [P0] wrong/unsafe, [P1] bug, [P2] AI-slop / doc-vs-code / hygiene,
[P3] nit. "FLAG" = ported verbatim and recorded; "FIXED" = corrected in the port.

Modules accepted: control.types, control.validation, control.primitives,
testing.reproducibility, numerical_stability, analysis.
Combined test count: 92 (18 + 14 + 12 + 31 + 17).

---

## Slice 1 - control.types + control.validation (ACCEPT)

- Ported `control/types/control_outputs.py` (ClassicalSMCOutput, AdaptiveSMCOutput,
  STAOutput, HybridSTAOutput - NamedTuples) and `control/validation/`
  (parameter_validators.py: require_positive/require_finite/require_probability;
  range_validators.py: require_in_range).
- 18 tests. Lens B math OK. Gate: P0=0, P1=0 -> ACCEPT.

## Slice 2 - control.primitives / saturation (ACCEPT)

- Ported `control/primitives/saturation.py`: saturate, smooth_sign, dead_zone.
- S2-A3 [P2 FLAG]: docstring says `tanh((slope*sigma)/epsilon)` but code computes
  `tanh(sigma/(epsilon*slope))`. Ported verbatim; tests assert real behavior.
- S2-A4 [P3 FLAG]: hardcoded overflow constant 700 in saturation.
- 14 tests. Gate -> ACCEPT.

## Slice 3 - testing.reproducibility / seeding (ACCEPT)

- Ported `testing/reproducibility/seed.py` (set_global_seed, SeedManager,
  create_rng) + package `__init__` (set_seed alias; dummy with_seed /
  random_seed_context shims).
- S3-A3 [P2 FIXED]: removed hallucinated citation artifacts from docstrings.
- S3-A4 [P2 FLAG]: dummy with_seed / random_seed_context shims kept verbatim.
- UTILS-DEDUP-4 [FLAG]: top-level `src/utils/seed.py` vs
  `testing/reproducibility/seed.py` - reconcile when top-level helpers land.
- 12 tests. Gate -> ACCEPT.

## Slice 4 - numerical_stability / safe operations (ACCEPT)

- Ported `numerical_stability/safe_operations.py` (safe_divide, safe_reciprocal,
  safe_sqrt, safe_log, safe_exp, safe_power, safe_norm, safe_normalize +
  EPSILON_DIV/SQRT/LOG/EXP + is_safe_denominator, clip_to_safe_range) and
  package `__init__`.
- S4-A1 [P3 FIXED]: ASCII-normalized non-ASCII glyphs + trailing-backslash banner.
- S4-A2 [P2 FLAG]: safe_sqrt docstring example outputs are wrong (`-0.001 -> 1e-7`;
  real result is `sqrt(1e-15) ~= 3.16e-8`). Ported verbatim; test asserts truth.
- S4-A3 [P2 FIXED]: `__init__` used absolute `from src.utils...` import that breaks
  under the beta import root; converted to relative `.safe_operations`.
- S4-A4 [P3 FLAG]: dead code in safe_divide (np.zeros_like + masked assign
  overwritten by later np.where).
- S4-A5 [P3 FLAG]: EPSILON_GENERAL defined but unused / unexported.
- UTILS-DEDUP-5 [P2 FLAG]: EPSILON_EXP=700.0 duplicates slice-2 saturation's
  hardcoded 700 (S2-A4).
- 31 tests. Gate -> ACCEPT.

## Slice 5 - analysis / statistics (ACCEPT)

Ported `analysis/statistics.py` + package `__init__` exposing 7 functions:
confidence_interval, bootstrap_confidence_interval, welch_t_test, one_way_anova,
monte_carlo_analysis, performance_comparison_summary, sample_size_calculation.

### Capability / dependency note (IMPORTANT)
- `analysis.statistics` imports `from scipy.stats import t, f` (and `norm` inside
  sample_size_calculation). **This is the first SciPy runtime dependency in the
  beta utils port.** SciPy must be installed in the project environment, and
  `scipy` should be added to beta's requirements if not already present.
- The offline audit sandbox has no SciPy, so verification ran the real ship code
  against a minimal but accurate `scipy.stats` shim (regularized incomplete beta
  for t/F CDFs; Acklam inverse-normal for norm.ppf). The shim is NOT shipped.
  Assertions use textbook values (e.g. t_crit(0.975, df=9)=2.26216; sample size
  63 for d=0.5/power=0.8/alpha=0.05) so they validate the ship wiring directly.

### Lens A - findings
| # | File:loc | Finding | Sev | Action |
|---|----------|---------|-----|--------|
| S5-A1 | statistics.py / __init__.py banners | Trailing-backslash artifacts in source banner comments | P3 | FIXED (clean ASCII banner) |
| S5-A2 | statistics.py docstrings | Non-breaking hyphen glyphs (U+2011) throughout ("Student-t", "half-width", etc.) | P3 | FIXED (ASCII hyphens) |
| S5-A3 | monte_carlo_analysis / performance_comparison_summary return type | `Dict[str, any]` uses builtin `any` instead of `typing.Any` | P2 | FLAG (ported verbatim; harmless at runtime, annotation only) |
| S5-A4 | bootstrap / monte_carlo / sample_size params | `callable` builtin used as type annotation instead of `typing.Callable` | P3 | FLAG (ported verbatim; runtime-harmless) |

### Lens B - math / correctness (all OK)
- S5-B1 confidence_interval: half_width = t_crit * s(ddof=1) / sqrt(n); n<2 -> NaN; n=0 -> mean NaN. Correct.
- S5-B2 welch_t_test: standard Welch t-stat + Welch-Satterthwaite df; two-sided p = 2*(1 - t.cdf(|t|, df)); effect_size documented as Cohen's d approximation. Correct.
- S5-B3 one_way_anova: SSB/SSW, df_between=k-1, df_within=N-k, F=MSB/MSW, p=1-F.cdf, eta^2=SSB/(SSB+SSW). Correct.
- S5-B4 bootstrap: percentile method over n_bootstrap resamples (np.random.choice). Nondeterministic by design; tests seed np.random.
- S5-B5 monte_carlo_analysis: aggregates scalar performance; raises RuntimeError if all trials fail; reuses confidence_interval. Correct.
- S5-B6 sample_size_calculation: normal-approx two-sample t-test n=2*((z_a+z_b)/d)^2; anova = ceil(1.2 * t_test_n). Documented approximations. Correct.

### Lens C - tests / coverage
- 17 tests: t-CI (value + small-sample NaN), bootstrap bracketing, Welch (no-reject / reject / too-few-raises), ANOVA (reject / <2 groups raise / <2 obs raise / df+eta), Monte Carlo (deterministic + all-fail-raises), comparison summary (3-controller anova + pairwise=3 / 2-controller no-anova), sample size (t_test=63 / anova=76 / unknown-type raises), namespace export check.

### Gate
P0=0, P1=0, no emojis, no `python3`, ASCII-only ship code. Open-P2 carried.
-> ACCEPT.

---

## Slice 6 - monitoring + infrastructure/threading (ACCEPT)

Ported `src/utils/monitoring/**` (16 modules) + `src/utils/infrastructure/threading/**` (AtomicCounter dependency) + `src/utils/infrastructure/__init__.py`.

### Capability / dependency note (IMPORTANT)
- Core monitoring introduces a dependency on `psutil`. The applier (`APPLY.ps1`) automatically ensures that `psutil>=5.9` is listed in `requirements.txt`.
- Verification requires `psutil` installed in the python environment.

### Lens A - findings
| # | File:loc | Finding | Sev | Action |
|---|----------|---------|-----|--------|
| MON-DEP-1 | memory_monitor.py / realtime/__init__.py | Unconditional `import psutil` in realtime modules causes import failure if `psutil` is absent | P1 | FIXED (added to requirements) |
| MON-LENSA-1 | visualization.py:66 | Bare `except:` in matplotlib style configuration swallows KeyboardInterrupt and system exits | P2 | FLAG (ported verbatim) |
| MON-LENSA-2 | coverage_monitoring.py, metrics_collector_control.py | Broad `except Exception as e` in coverage recording and callback loops | P3 | FLAG (ported verbatim) |
| MON-UNICODE-1 | stability.py, diagnostics.py | non-ASCII math glyphs (sigma, kappa, angle-bracket) in docstrings | P3 | FLAG (preserved verbatim) |
| MON-EMOJI-1 | coverage_monitoring.py | Unicode emojis in alert strings violate the no-emoji rule | P3 | FLAG (preserved verbatim) |

### Lens B - math / correctness
- MON-LAT-1 (P2): `LatencyMonitor.end()` flags a missed deadline at `latency > dt*margin`, whereas `missed_rate()` and `enforce()` check `sample > dt`. Characterization test documented this current mismatch (`test_end_vs_missed_rate_threshold_mismatch`).
- MON-STA-2 (P3): Stability monitors leak `numpy.bool_` instead of standard Python `bool` in result dictionaries. Characterization test covers this.

### Lens C - tests / coverage
- 26 tests covering atomic primitives, data models, diagnostics, latency, memory monitoring, package import, and stability monitoring.
- All 26 tests passed in the local repository environment.

### Gate
P0=0, P1=0 (MON-DEP-1 mitigated with package requirement). Open P2 carried.
-> ACCEPT.

---

## Open items / watch-list
- M3 remains WIP. Remaining utils domains: visualization, testing.dev_tools, testing.fault_injection, and top-level helpers (config_compatibility, control_analysis, disturbances, model_uncertainty, seed, streamlit_theme). Widen `utils/__init__.py` as each lands.
- UTILS-DEDUP-4 (seed.py duplication) and UTILS-DEDUP-5 (overflow constant 700) remain FLAG-only pending later slices.
- Carry MON-LAT-1 (threshold mismatch), MON-LENSA-1 (bare except) as open items.

