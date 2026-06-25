# AUDIT LEDGER -- append-only findings log

> Every problem found during migration lands here: AI-slop AND scientific defects.
> Append at the bottom; never rewrite. Close items by setting Status = FIXED (with the
> commit/branch) or WONTFIX (with justification -> also record in DECISIONS.md).
>
> Severities: [P0] scientifically wrong / unsafe  |  [P1] functional bug  |
>             [P2] slop / maintainability         |  [P3] nit
> Status: OPEN | IN_PROGRESS | FIXED | WONTFIX

| ID | Date | Module | Lens (A/B/C) | Sev | Finding (one line) | Status | Fix ref |
|----|------|--------|--------------|-----|--------------------|--------|---------|
| W1 | 2026-06-23 | references/ | B | P1? | Verify `references/proofs/` + `controllers.bib`/`config.bib` are genuine (real theorems/citations), not AI-fabricated, BEFORE using them as the Lens B oracle | FIXED | M2 / config.bib VERIFIED + web-check (2026-06-24) |

| F-PLANT-1 | 2026-06-24 | plant (full) | B | P1 | Parity harness + invariant test hardcoded rejected inertias I1=0.0081/I2=0.0034; replaced with grounded uniform-thin-rod config values I1=0.00265/I2=0.00115 ((1/12) m L^2) | FIXED | scripts/parity_check.py + tests/test_plant/test_full_dynamics_invariants.py (2026-06-24); gate + 603 tests pass |
| U1 | 2026-06-24 | utils | A | P1 | utils __init__ slice-scoped (was import-breaking as it re-exported not-yet-ported packages) | FIXED | src/utils/__init__.py (2026-06-24) |
| U2 | 2026-06-24 | utils | A | P2 | control_outputs citation issue-number 7 -> 5 + JOT URL | FIXED | src/utils/control/types/control_outputs.py (2026-06-24) |
| U3 | 2026-06-24 | utils | A | P3 | control_outputs docstring/annotation drift (flag-only) | OPEN | |
| U4 | 2026-06-24 | utils | B | P3 | require_positive / require_finite accepts bool as number (flag-only) | OPEN | |
| UTILS-DEDUP-1 | 2026-06-24 | utils | A | P2 | require_positive / require_finite overlap with plant/config validators (flag-only) | OPEN | |
| UTILS-DEDUP-2 | 2026-06-24 | utils | A | P2 | require_in_range overlap with plant/config validators (flag-only) | OPEN | |
| S2-A1 | 2026-06-24 | utils | A | P3 | saturation banner path corrected | FIXED | src/utils/control/primitives/saturation.py (2026-06-24) |
| S2-A2 | 2026-06-24 | utils | A | P3 | ASCII normalization in saturation.py | FIXED | src/utils/control/primitives/saturation.py (2026-06-24) |
| S2-A3 | 2026-06-24 | utils | A | P2 | saturate docstring contradicts code/inline comments about slope | OPEN | |
| S2-A4 | 2026-06-24 | utils | A | P3 | primitives __all__=[] / star-import leak (flag-only) | OPEN | |
| UTILS-DEDUP-3 | 2026-06-24 | utils | A | P2 | possible saturation reimplementation inside controllers (flag-only) | OPEN | |
| S3-A1 | 2026-06-24 | utils | A | P3 | seed.py / reproducibility __init__ banner paths corrected | FIXED | src/utils/testing/reproducibility/seed.py (2026-06-24) |
| S3-A2 | 2026-06-24 | utils | A | P3 | ASCII normalization in seed.py | FIXED | src/utils/testing/reproducibility/seed.py (2026-06-24) |
| S3-A3 | 2026-06-24 | utils | A | P2 | removed hallucinated citation artifacts from seed.py docstrings | FIXED | src/utils/testing/reproducibility/seed.py (2026-06-24) |
| S3-A4 | 2026-06-24 | utils | A | P2 | dummy shims with_seed/random_seed_context logic issues | OPEN | |
| S3-A5 | 2026-06-24 | utils | A | P3 | stale docstring import path corrected in seed.py | FIXED | src/utils/testing/reproducibility/seed.py (2026-06-24) |
| S3-B4 | 2026-06-24 | utils | B | P3 | set_global_seed uses NumPy legacy global RNG (flag-only) | OPEN | |
| UTILS-DEDUP-4 | 2026-06-24 | utils | A | P2 | top-level src/utils/seed.py vs testing/reproducibility/seed.py possible duplicate (flag-only) | OPEN | |
| S4-A1 | 2026-06-24 | utils | A | P3 | ASCII normalization + banner rebuild in safe_operations.py | FIXED | src/utils/numerical_stability/safe_operations.py (2026-06-24) |
| S4-A2 | 2026-06-24 | utils | A | P2 | safe_sqrt docstring example outputs are wrong (flag-only) | OPEN | |
| S4-A3 | 2026-06-24 | utils | A | P2 | import breaking absolute import path in numerical_stability/__init__.py | FIXED | src/utils/numerical_stability/__init__.py (2026-06-24) |
| S4-A4 | 2026-06-24 | utils | A | P3 | dead/redundant code in safe_divide (flag-only) | OPEN | |
| S4-A5 | 2026-06-24 | utils | A | P3 | EPSILON_GENERAL defined but never used and not exported (flag-only) | OPEN | |
| UTILS-DEDUP-5 | 2026-06-24 | utils | A | P2 | EPSILON_EXP duplicates hardcoded saturation overflow clamp (flag-only) | OPEN | |
| S5-A1 | 2026-06-24 | utils | A | P3 | ASCII-normalized statistics/__init__ banners in analysis | FIXED | src/utils/analysis/statistics.py (2026-06-24) |
| S5-A2 | 2026-06-24 | utils | A | P3 | ASCII hyphens replaced non-breaking hyphens in statistics.py docstrings | FIXED | src/utils/analysis/statistics.py (2026-06-24) |
| S5-A3 | 2026-06-24 | utils | A | P2 | return type uses builtin any instead of typing.Any (flag-only) | OPEN | |
| S5-A4 | 2026-06-24 | utils | A | P3 | builtin callable used as type annotation instead of typing.Callable (flag-only) | OPEN | |
| W-REFS-INFO | 2026-06-24 | references | D | INFO | W-REFS harvest workstream opened; REFERENCES_LEDGER.md created | FIXED | REFERENCES_LEDGER.md (2026-06-24) |
| W-REFS-DONE | 2026-06-24 | references | D | INFO | W-REFS: REFERENCES_LEDGER.md created and back-filled (M1/M2/M3 s1-5); Lens D added to audit loop; 0 dangling proof keys | FIXED | REFERENCES_LEDGER.md (2026-06-24) |
| MON-DEP-1 | 2026-06-25 | utils | A | P1 | unconditional `import psutil` in realtime/memory_monitor.py | FIXED | src/utils/monitoring/realtime/__init__.py + requirements.txt (2026-06-25) |
| MON-LAT-1 | 2026-06-25 | utils | B | P2 | `LatencyMonitor.end()` Miss threshold uses `dt*margin` while `missed_rate()` uses `dt` | OPEN | |
| MON-LENSA-1 | 2026-06-25 | utils | A | P2 | bare `except:` in visualization.py matplotlib style setup | OPEN | |
| MON-LENSA-2 | 2026-06-25 | utils | A | P3 | broad `except Exception as e` in coverage_monitoring.py, metrics_collector_control.py | OPEN | |
| MON-STA-2 | 2026-06-25 | utils | B | P3 | `numpy.bool_` leakage in stability.py monitor result dicts | OPEN | |
| MON-UNICODE-1 | 2026-06-25 | utils | A | P3 | non-ASCII math glyphs in stability.py/diagnostics.py docstrings | OPEN | |
| MON-EMOJI-1 | 2026-06-25 | utils | A | P3 | unicode emojis in coverage_monitoring.py alert strings | OPEN | |
| MON-PROV-1 | 2026-06-25 | utils | C | P3 | hardcoded `theSadeQ/dip-smc-pso` and "Issue #9" in coverage_monitoring.py | OPEN | |

## Summary counters (update on each session)
- Open P0: 0
- Open P1: 0 (W1 verified genuine 2026-06-24; F-PLANT-1 fixed 2026-06-24)
- Open P2: 15 (plant.A7, M2.v6, F-PLANT-2, F-PLANT-3, UTILS-DEDUP-1, UTILS-DEDUP-2, S2-A3, UTILS-DEDUP-3, S3-A4, UTILS-DEDUP-4, S4-A2, UTILS-DEDUP-5, S5-A3, MON-LAT-1, MON-LENSA-1)
- Modules accepted to trunk: M1 (config), M2 (plant), M3 Slice 1 (utils types+validation), M3 Slice 2 (utils control.primitives), M3 Slice 3 (utils testing.reproducibility), M3 Slice 4 (utils numerical_stability), M3 Slice 5 (utils analysis), M3 Slice 6 (utils monitoring + infrastructure/threading)

## M2 / plant -- 2026-06-23
- [P0] plant.B1  Inertia matrix M(q) incorrect (M12,M22,M23 spurious terms). Proof: KE-vs-M residual 2.95e-1. Status: FIXED (migration/plant).
- [P0] plant.B2  Coriolis matrix fails (Mdot-2C) skew-symmetry (4.80e-1). Status: FIXED (migration/plant).
- [P0] plant.B3  Energy not conserved, zero input/friction (rel drift 8.7e2). Status: FIXED (migration/plant).
- [P1] plant.B4  Gravity vector sign inconsistent with potential-energy convention. Status: FIXED (migration/plant).
- [P1] plant.A1  Duplicate `_rhs_core` in models/full/dynamics.py (529, 565). Status: FIXED (migration/plant).
- [P1] plant.A2  State-order docstring contradiction in `_rhs_core`. Status: FIXED (migration/plant).
- [P1] plant.A8  Plant port couples to src.utils.config_compatibility. Status: FIXED (migration/plant).
- [P1] plant.A9  core/dynamics.py + models/dynamics.py shims resolve to deprecated src/core. Status: FIXED (migration/plant).
- [P2] plant.A3  Fabricated gyroscopic term gyro_coupling=0.01. Status: FIXED (migration/plant).
- [P2] plant.A4  Aerodynamics "full fidelity" is a magic-number approximation. Status: FIXED (migration/plant).
- [P2] plant.A5  Base-excitation magic numbers (freq 1.0, amp 0.1). Status: FIXED (migration/plant).
- [P2] plant.A6  Friction baked into core Coriolis matrix. Status: FIXED (migration/plant).
- [P2] plant.A7  Simplified inertia fudge factors 0.5/0.8 (deferred per D9). Status: OPEN.
- [P2] plant.A10 54 build artifacts (*.pyc/*.nbc/*.nbi) + 8 __pycache__ shipped in port. Status: FIXED (migration/plant).
- [INFO] plant.FIX  Verified-correct reference passes gate (skew 5e-16, energy 4e-15). See physics_matrices_corrected.py.

## W1 / references authenticity -- 2026-06-23
- [OK]  W1.ok1  Moreno&Osorio 2008 (doi:10.1109/CDC.2008.4739356) VERIFIED authentic.
- [OK]  W1.ok2  Slotine&Li 1991 Applied Nonlinear Control VERIFIED authentic.
- [OK]  W1.ok3  Sandve 2013 (doi:10.1371/journal.pcbi.1003285) VERIFIED authentic.
- [P1]  W1-1  config.bib Prasad2014 (IJECE double inverted pendulum, doi:10.11591/ijece.v4i2.5694) UNVERIFIABLE / likely fabricated. Status: FIXED (removed and replaced by genuine double-inverted-pendulum sources: Bogdanov2004, Graichen2007, Zhong2001).
- [P1]  W1-2  Dangling key: proofs cite Prasad2012 but config.bib defines Prasad2014; discussed_sources misstates it. Status: FIXED (all dangling citation keys replaced with verified keys).
- [P1]  W1-3  Wrong-system provenance: all genuine Prasad refs are SINGLE-IP, cited as DIP parameter source. Status: FIXED (all occurrences of Prasad removed from schemas, configs, proofs, and documentation).
- [P1]  W1-4  inertia_validation_proof.md misapplies Parallel-Axis Theorem (claims I_com >= m*d^2). Config inertia inflated 0.00265->0.0081, 0.00115->0.0034. Status: FIXED (re-written to reflect physical center-of-mass bounds and citable thin-rod values).
- [P1]  W1-5  validation.py::validate_inertia_consistency uses min_inertia=m*com^2 (pivot bound) on COM inertia field. Status: FIXED (validate_inertia_consistency checks physical center-of-mass bounds).
- [P2]  W1-6  Citation metadata drift (2012 AMS page numbers/venue). Status: FIXED (metadata-drift citations removed).

## M2 verification (independent review of migration/plant) -- 2026-06-23
- [OK]  M2.v1  core/physics_matrices.py M/C/G corrected; C re-derived by hand = Christoffel(M). VERIFIED.
- [OK]  M2.v2  full/physics.py M/C corrected; gyro term removed; friction/aero/disturbance separated. VERIFIED.
- [OK]  M2.v3  full/dynamics.py duplicate _rhs_core removed. VERIFIED.
- [WARNING] M2.v4  STATE.md on branch still shows M2 [WIP]; CLI's [DONE] claim NOT reflected in repo. Status: CLOSED (reverted to [WIP] pending parity and refs).
- [WARNING] M2.v5  Source-parity (golden trajectories vs SMC-PSO/) NOT run; invariant gate only. Status: OPEN.
- [P2]  M2.v6  Remaining slop untouched: aero magic 0.1/0.5 (A4), base-excitation magic 1.0/0.1 (A5), simplified fudge 0.5/0.8 (A7, deferred D9). Status: OPEN.

## M2 verification follow-up & corrections -- 2026-06-24
- [P2] F-PLANT-2  DIPParams compat class hardcodes default physics divergent from config.yaml. Status: OPEN (revisit at M4).
- [P2] F-PLANT-3  core/dynamics.py aliases DIPDynamics = SimplifiedDIPDynamics. Status: OPEN (revisit at M4).
- [OK] W1.ok4     All discussed-source citations web-verified GENUINE. Status: FIXED (references/config.bib updated).

## M3 / utils slice 1 -- 2026-06-24
- [P1] U1  utils __init__ slice-scoped (was import-breaking). Status: FIXED (src/utils/__init__.py).
- [P2] U2  control_outputs citation issue-number 7 -> 5 + JOT URL. Status: FIXED (src/utils/control/types/control_outputs.py).
- [P3] U3  control_outputs docstring/annotation drift (flag-only). Status: OPEN.
- [P3] U4  require_positive / require_finite accepts bool as number (flag-only). Status: OPEN.
- [P2] UTILS-DEDUP-1  require_positive / require_finite overlap with plant/config validators (flag-only). Status: OPEN.
- [P2] UTILS-DEDUP-2  require_in_range overlap with plant/config validators (flag-only). Status: OPEN.

## M3 / utils slice 2 -- 2026-06-24
- [P3] S2-A1  saturation banner path corrected. Status: FIXED (src/utils/control/primitives/saturation.py).
- [P3] S2-A2  ASCII normalization in saturation.py. Status: FIXED (src/utils/control/primitives/saturation.py).
- [P2] S2-A3  saturate docstring contradicts code + inline comments about slope. Status: OPEN.
- [P3] S2-A4  primitives __all__=[] / star-import leak. Status: OPEN.
- [P2] UTILS-DEDUP-3  possible saturation reimplementation inside controllers. Status: OPEN.

## M3 / utils slice 3 -- 2026-06-24
- [P3] S3-A1  seed.py / reproducibility __init__ banner paths corrected. Status: FIXED (src/utils/testing/reproducibility/seed.py).
- [P3] S3-A2  ASCII normalization in seed.py. Status: FIXED (src/utils/testing/reproducibility/seed.py).
- [P2] S3-A3  removed hallucinated citation artifacts from seed.py docstrings. Status: FIXED (src/utils/testing/reproducibility/seed.py).
- [P2] S3-A4  dummy shims -- with_seed ignores its seed; random_seed_context never restores prior state (dead code). Status: OPEN.
- [P3] S3-A5  stale docstring import path corrected. Status: FIXED (src/utils/testing/reproducibility/seed.py).
- [P3] S3-B4  set_global_seed uses NumPy legacy global RNG. Status: OPEN.
- [P2] UTILS-DEDUP-4  top-level src/utils/seed.py vs testing/reproducibility/seed.py possible duplicate. Status: OPEN.

## M3 / utils slice 4 -- 2026-06-24
- [P3] S4-A1  ASCII normalization + banner rebuild in safe_operations.py. Status: FIXED (src/utils/numerical_stability/safe_operations.py).
- [P2] S4-A2  safe_sqrt docstring example outputs are wrong (expects 1e-7 but default min_value=1e-15 gets sqrt(1e-15)~=3.16e-8). Status: OPEN.
- [P2] S4-A3  import breaking absolute import path in numerical_stability/__init__.py. Status: FIXED (src/utils/numerical_stability/__init__.py).
- [P3] S4-A4  dead/redundant code in safe_divide. Status: OPEN.
- [P3] S4-A5  EPSILON_GENERAL defined but never used and not exported. Status: OPEN.
- [P2] UTILS-DEDUP-5  EPSILON_EXP (700.0) duplicates hardcoded saturation overflow clamp in slice 2. Status: OPEN.

## M3 / utils slice 5 -- 2026-06-24
- [P3] S5-A1  ASCII-normalized statistics/__init__ banners in analysis. Status: FIXED (src/utils/analysis/statistics.py).
- [P3] S5-A2  ASCII hyphens replaced non-breaking hyphens in statistics.py docstrings. Status: FIXED (src/utils/analysis/statistics.py).
- [P2] S5-A3  return type uses builtin any instead of typing.Any. Status: OPEN.
- [P3] S5-A4  builtin callable used as type annotation instead of typing.Callable. Status: OPEN.

## M3 / utils slice 6 -- 2026-06-25
- [P1] MON-DEP-1  unconditional import of psutil in realtime/memory_monitor.py causing ModuleNotFoundError if psutil is absent. Status: FIXED (applied requirements additions).
- [P2] MON-LAT-1  LatencyMonitor.end Miss threshold uses dt*margin while missed_rate uses dt, causing dual, inconsistent definitions of deadline-miss. Status: OPEN.
- [P2] MON-LENSA-1  bare except in visualization.py matplotlib style setup swallows KeyboardInterrupt and other errors. Status: OPEN.
- [P3] MON-LENSA-2  broad except Exception as e in coverage_monitoring.py and metrics_collector_control.py. Status: OPEN.
- [P3] MON-STA-2  numpy.bool_ leakage in stability.py monitor result dicts instead of Python bool. Status: OPEN.
- [P3] MON-UNICODE-1  non-ASCII math glyphs (sigma, kappa, angle-bracket) in stability.py/diagnostics.py docstrings. Status: OPEN.
- [P3] MON-EMOJI-1  unicode emojis in coverage_monitoring.py alert strings violate no-emojis rule. Status: OPEN.
- [P3] MON-PROV-1  hardcoded dip-smc-pso repository identity and Issue #9 in coverage_monitoring.py. Status: OPEN.

