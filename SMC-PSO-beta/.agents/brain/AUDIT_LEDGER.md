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
| M6-S1a-1 | 2026-06-30 | optimization/simulation | A | P1 | simulate_system_batch used logging.* but batch.py did not import logging (latent NameError in controller-init / history handlers) | FIXED | src/simulation/orchestrators/batch.py @ ca1e553d4d3bc83935b53794aea8be1d70e35cb4 |
| M6-S1b-1 | 2026-06-30 | optimization | A | P3 | non-ASCII math glyphs (sigma, <=, +/-, x, Delta) retained in docstrings/log strings | FLAGGED | src/optimization/algorithms/pso_optimizer.py |
| M6-S1b-2 | 2026-06-30 | optimization | B | P2 | legacy import src.utils.seed did not exist; create_rng rewired to utils.testing.reproducibility | FIXED | src/optimization/algorithms/pso_optimizer.py @ ba126625131d8ff00b1558362ec05c5d92640a70 |
| M6-S2-1 | 2026-06-30 | optimization/integration | A | P3 | EnhancedPSOFactory duplicates simulator/scenario fitness logic instead of reusing simulate_system_batch | FLAGGED | src/optimization/integration/pso_factory_bridge.py |
| M6-S2-2 | 2026-06-30 | optimization/integration | A | P3 | monkeypatches tuner._fitness = enhanced_fitness (brittle coupling to PSOTuner internals) | FLAGGED | src/optimization/integration/pso_factory_bridge.py |
| M6-S2-3 | 2026-06-30 | optimization/integration | B | P3 | bridge _get_default_gains fallbacks differ from factory registry defaults | FLAGGED | src/optimization/integration/pso_factory_bridge.py |
| M7-S1-1 | 2026-06-30 | interfaces/core | A | P3 | StreamingProtocol defined in protocols.py but not exported by core/__init__.py | FLAGGED | src/interfaces/core/__init__.py |
| M7-S1-2 | 2026-06-30 | interfaces/core | A | P3 | redundant import Tuple in protocols.py (L19) separate from L16 | FLAGGED | src/interfaces/core/protocols.py |
| M7-S2-1 | 2026-06-30 | interfaces/data_exchange | A | P1 | DataPacket.unpack() sliced header at data[:12] instead of data[:16] leading to struct unpack errors | FIXED | src/interfaces/data_exchange/data_types.py @ a6c2b8ba30fcca7e83e5a53cc5f388b177294069 |
| M7-S2-2 | 2026-06-30 | interfaces/data_exchange | A | P2 | __all__ exported nonexistent PerformanceSerializer and SerializationMetrics causing ImportError on star-imports | FIXED | src/interfaces/data_exchange/__init__.py @ a6c2b8ba30fcca7e83e5a53cc5f388b177294069 |
| M7-S2-3 | 2026-06-30 | interfaces/data_exchange | A | P1 | streaming.py async loop processes wait synchronously via condition lock instead of awaiting, causing event-loop hangs on stop() | FLAGGED | src/interfaces/data_exchange/streaming.py |
| M7-S2-4 | 2026-06-30 | interfaces/data_exchange | B | P3 | duplicate MessageType and Priority enums vs core package definitions | FLAGGED | src/interfaces/data_exchange/data_types.py |
| M7-S2-5 | 2026-06-30 | interfaces/data_exchange | A | P3 | DataPacket.unpack payload guard off-by-4 (12 -> 16 + payload_length); completes M7-S2-1 | FIXED | src/interfaces/data_exchange/data_types.py @ a6c2b8ba30fcca7e83e5a53cc5f388b177294069 |

## Summary counters (update on each session)
- Open P0: 0
- Open P1: 1 (M7-S2-3 streaming async-hang, deferred to dedicated remediation slice)
- Open P2: 16 (plant.A7, M2.v6, F-PLANT-2, F-PLANT-3, UTILS-DEDUP-1, UTILS-DEDUP-2, S2-A3, UTILS-DEDUP-3, S3-A4, UTILS-DEDUP-4, S4-A2, UTILS-DEDUP-5, S5-A3, MON-LAT-1, MON-LENSA-1, INFRA-LOG-1)
- Modules accepted to trunk: M1 (config), M2 (plant), M3 Slice 1 (utils types+validation), M3 Slice 2 (utils control.primitives), M3 Slice 3 (utils testing.reproducibility), M3 Slice 4 (utils numerical_stability), M3 Slice 5 (utils analysis), M3 Slice 6 (utils monitoring + infrastructure/threading), M3 Slice 7 (utils infrastructure: logging + memory)

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

## M3 / utils slice 7 -- 2026-06-25
- [P2] INFRA-LOG-1  Default file log dir `academic/logs` absent in beta; auto-created via mkdir; consider `logs/` or LOG_DIR. Status: OPEN.
- [P3] INFRA-LOG-DEPR-1  `datetime.utcfromtimestamp` deprecated (py3.12+) in JSON/Metric formatters. Status: OPEN.
- [P3] INFRA-LOG-LENSA-1  Broad/bare except in compression, async writer, flush (intentional logging resilience). Status: OPEN.
- [P3] INFRA-LOG-LENSA-2  Dead var `time_tuple` in doRollover; no-op `pass` branch in `_rotate_size`. Status: OPEN.
- [P3] INFRA-MEM-1  get_block returns array but return_block needs index; caller tracks mapping. Status: OPEN.
- [P3] INFRA-PROV-1  memory docstrings reference source-repo "Issue #17 (CRIT-008)". Status: OPEN.

---

## 2026-06-28 — M4 boundary closeout

### Finding #2 — physics_matrices (RESOLVED)
- Corrected energy-consistent / passivity-compliant Christoffel-Coriolis math wired
  into `physics_matrices.py`; `physics.py` (full-fidelity) delegates to the corrected
  base matrices.
- Evidence: `pytest tests/test_plant/test_full_dynamics_invariants.py` — all invariant
  tests pass (energy drift, SPD inertia, skew-symmetry of (Mdot - 2C)).
- Effect: re-opened M2 acceptance is now closed.

### Trap A — state-vector ordering mismatch (PINNED; controller wiring deferred)
- **Severity: P0** if left unmanaged — silent wrong dynamics, no exception, tests stay green.
- Plant (corrected physics, now live) uses GROUPED `[x, theta1, theta2, x_dot, theta1_dot, theta2_dot]`.
- Legacy controllers documented INTERLEAVED `[x, x_dot, theta1, theta1_dot, theta2, theta2_dot]`.
- Action taken: declared GROUPED canonical (`.agents/brain/STATE_VECTOR_CONVENTION.md`),
  shipped boundary adapters (`src/plant/state_convention.py`) + guard test
  (`tests/test_plant/test_state_vector_convention.py`).
- **Open item (M5):** controllers must call `interleaved_to_grouped()` at the plant
  boundary; add an integration test asserting it. `test_full_dynamics_invariants.py`
  does NOT catch this.

### M4 status
- Slice 1 (`src/controllers/base.py`) ported, cleaned (AI-slop removed), flattened. Done.
- Slices 2–6 (simulation core, integrators, safety, engines/orchestrators, results): TODO.

---

### M4 Slice 2 — simulation/core (accepted 2026-06-28)
- Scope: src/simulation/core/{interfaces,simulation_context,state_space,time_domain}.py + core/__init__ + minimal simulation/__init__.
- Lens A: no hallucinated citation tokens in core/ (Trap E was confined to control_primitives, handled in Slice 1). Banners normalized to Slice 1 style.
- Lens B findings:
  - P1 #S2-1 compute_energy(): docstring said "total energy" but returns KINETIC only; also silently assumes GROUPED ordering (Trap A). FIX: docstring corrected; grouped assumption pinned by test. Math unchanged (parity preserved).
  - P2 #S2-2 AdaptiveTimeStep: error exponent hard-coded to 1/4 regardless of integrator order. Deferred to Slice 3 (integrators) where it is actually consumed.
  - P2 #S2-3 interfaces.PerformanceMonitor duplicates a name the source simulation/__init__ imports from .safety. No real collision (different module path; not exported by core/__init__). Revisit in Slice 4.
- Decisions:
  - Trap C: ported core/ SimulationContext; context/ twin NOT ported (deferred drop to Slice 4 alongside safety).
  - Trap D: shipped a MINIMAL simulation/__init__ (no subpackage re-exports / legacy aliases). Full re-export deferred until Slices 3-6 land.
  - Trap F mirror: kept core as a subpackage (matches source); graph node `runner` maps to src/simulation/.
  - simulation_context: wrap_physics_config import made LAZY so core imports before utils/factory exist. Call-time behavior identical.
- Gate: P0=0, P1=0 (S2-1 resolved). pytest 24/24 green. parity OK. import-without-unported-deps OK. No src/core imports.

---

### M4 Slice 3 — simulation/integrators (accepted 2026-06-29)
- Scope: src/simulation/integrators/{base,factory,compatibility}.py + fixed_step/{euler,runge_kutta} + discrete/zero_order_hold + adaptive/{runge_kutta,error_control} + 4 __init__ + docstring-only simulation/__init__.
- Headline: ZERO functional edits. Integrators depend only on core.interfaces (Slice 2) + numpy/scipy; ported byte-identical to source except #=== banner normalization (machine-verified banner-only diff, 12 files).
- Lens A: no hallucinated citation tokens in integrators/. NOTE: legacy engines/adaptive_integrator.py (NOT ported; Slice 5) DOES contain Trap-E citation tokens — flag for Slice 5; integrators/adaptive/runge_kutta.rk45_step is the clean replacement.
  - P3 #S3-3 factory.get_integrator_info(): getattr(cls,'ORDER') always None (property is lowercase instance 'order'); 'adaptive' derived from type-name substring (wrong for dp45/dormand_prince). Metadata helper only; kept for parity; deferred.
  - P3 #S3-4 ZeroOrderHold.order returns float('inf') though ABC types order->int. Semantically intended (exact for LTI). Kept; test asserts ==inf.
  - P3 IntegratorSafetyWrapper uses print() not logging; compatibility.py keeps a 2nd small registry (DRY). Kept; deferred.
- Lens B findings:
  - P1 #S3-1 (RESOLVES carried watch-item S2-2): adaptive error control IS order-aware. ErrorController.update_step_size uses (tol/err)**(1/order) accept, 1/(order+1) reject; DormandPrince45 passes order=5. Pinned by test_error_controller_is_order_aware.
  - P2 #S3-2 (new carried watch-item): core/time_domain.AdaptiveTimeStep (Slice 2) still hard-codes 1/4 and is NOT order-aware — but it is NOT used on the integrator path (superseded by ErrorController). Deprecate/route through ErrorController when engines wire adaptive stepping in Slice 5.
  - P2 #S3-3(B) error-norm convention differs new vs legacy (RMS+old-state-scale vs L2+max-scale). Propagated y5 is IDENTICAL for accepted steps (formula parity); only suggested_dt/accept-threshold differ. Pinned by test_dp45_state_parity_with_legacy_rk45_step. Documented; no action.
- Decisions: Trap D still deferred (rk45_step ships inside adaptive/runge_kutta where source defines it; package-level alias deferred). simulation/__init__ docstring updated only. engines/adaptive_integrator.py deliberately NOT ported (Slice 5).
- Gate: P0=0, P1=0 (S3-1 resolved). pytest 47/47 green. structural parity banner-only + numerical correctness OK. import-without-unported-deps OK. No src/core imports.

---

### M4 Slice 4 — simulation/safety (+ Trap C closure) (accepted 2026-06-29)
- Scope: src/simulation/safety/{__init__,guards,constraints,monitors,recovery}.py + docstring-only simulation/__init__. DROPPED the src/simulation/context/ twin (NOT ported).
- Headline: ZERO functional edits. safety depends only on core.interfaces (Slice 2) + numpy; ported byte-identical to source except #=== banner normalization (machine-verified banner-only diff, 5/5 files).
- Trap C RESOLVED: core/simulation_context.py (Slice 2) is a strict SUPERSET of context/simulation_context.py (adds register_component/get_component/create_simulation_engine/get_simulation_parameters + newer dynamics loader). context/safety_guards.py (_guard_*, RuntimeError) superseded by safety/guards.py (guard_*, SafetyViolationError <: RuntimeError) with identical frozen substrings. Source __init__ already imports SimulationContext from .core, not .context. => context/ dropped, nothing unique lost.
- Watch-item S2-3 RESOLVED (false alarm): safety.PerformanceMonitor is a re-export of core.interfaces.PerformanceMonitor (via monitors.py), not a duplicate class; concrete impl is SimulationPerformanceMonitor. Pinned by test_safety_import (is-identity).
- Lens A: no citation tokens in safety/. P3 #S4-1 error messages carry literal placeholders <i>/<val>/<max>/<t> — these are INTENTIONAL frozen test-matching substrings (do not modify); preserved verbatim, flagged so future cleanup doesn't break acceptance tests. P3 #S4-4 apply_safety_guards approximates time as step_idx*0.01 (hard dt); kept for parity, revisit when engines wire real t (Slice 5).
- Lens B: P3 #S4-2 guards define 'energy' as ||state||^2 (not physical kinetic+potential); self-consistent, matches source; route through plant energy fn post-M4. P3 #S4-3 EnergyGuard.check uses sum(state**2) (no axis) vs legacy guard_energy sum(.,axis=-1); identical for single state, differ only batched; kept.
- Decisions: Trap D still deferred — package-level simulation/__init__ re-exports (safety + _guard_* aliases) wait for Slice 6 (orchestrators/results/strategies absent). simulation/__init__ docstring updated only; still side-effect free.
- Gate: P0=0, P1=0. pytest 22/22 green (5 files). structural parity banner-only + behavioral correctness OK. import-without-unported-deps OK. No src/core imports. context/ twin absent.

---

## M4 Slice 5 — simulation/results + simulation/orchestrators (engines DROPPED, Trap F)

- **Date:** applied with Slice 5 kit. **Verdict:** PORT AS-IS (banner-normalize only).
- **Files (11):** `results/{__init__,containers,exporters,processors,validators}.py` (6 exports); `orchestrators/{__init__,base,sequential,batch,parallel,real_time}.py` (5 exports). Plus docstring-only `simulation/__init__.py`.
- **Diff vs source:** banner-only (3-line `#=` banner, CRLF->LF + trailing backslash strip) = 9 bytes/file.
- **Gate:** 26/26 tests (14 results + 12 orchestrators); STRUCTURAL parity OK (banner-only) + BEHAVIORAL OK (RK4 vs closed-form); P0=0, P1=0; no `src/core/` imports.
- **Findings:**
  - **S5-1 (supersedes S3-2):** `core/time_domain.AdaptiveTimeStep.update_step_size` hard-coded `(1/4)` exponent left UNTOUCHED — dead on canonical path (adaptive stepping uses order-aware `ErrorController` in `integrators/adaptive`). Resolved by analysis; editing shipped Slice-2 code would add parity risk for zero benefit.
  - **S5-2:** legacy `orchestrators/sequential.py` helpers `get_step_fn`/`step`/`_load_full_step`/`_load_lowrank_step` reference pre-migration `src.config.schemas` + `...plant.models.dip_full`/`dip_lowrank`; lazy + dead on canonical path; preserved byte-identical; remap deferred to Slice 6/M6.
  - **S5-3 (Trap F closure):** `engines/` (adaptive_integrator, simulation_runner, vector_sim) DROPPED — duplicate of integrators+orchestrators, reachable only via `src/core/*` shims (Trap B), still imported removed `context/` (Trap C), carried lone Trap-E citation token. Analogous to Slice 4 Trap-C drop.
  - **S5-4:** `simulation/__init__.py` docstring-only update (Slice 5 regrouping + Trap F note); package stays import side-effect free; package-level re-exports + `_guard_*` aliases (Trap D) deferred to Slice 6.
- **Carry-forward:** Slice 6 = `strategies/` (MonteCarloStrategy) + Trap-D re-exports + remap S5-2 plant paths. Before retiring `engines/` (M6/M9), grep repo for importers of `src.simulation.engines` / `src.core.vector_sim` / `src.core.simulation_runner`.

---

## M4 Slice 6 — simulation/strategies + package wiring (Trap D close) — M4 COMPLETE

- **Date:** applied with Slice 6 kit. **Verdict:** PORT AS-IS (banner-normalize only). 0 functional edits.
- **Files (3):** `strategies/{__init__,monte_carlo}.py` (NEW; exports MonteCarloStrategy);   `simulation/__init__.py` (REPLACED docstring-only with the fully-wired original surface   + legacy aliases + factory fns).
- **Diff vs source:** banner + line-ending only (`chg_lines=3`/file). Norm sha256(12):   strategies/__init__ `8f6fee91fbd3`, strategies/monte_carlo `c7ea679557a1`,   simulation/__init__ `8ad30c37a4d6`.
- **Gate:** 19/19 tests (12 strategies + 7 package-surface) + regression green; STRUCTURAL   parity OK (banner-only) + BEHAVIORAL OK (MonteCarlo stats vs numpy ref); P0=0, P1=0;   no `src.core` imports.
- **Findings:**
  - **S6-1 (Trap D close):** package-level re-exports + legacy aliases (get_step_fn, step,     run_simulation, simulate=simulate_batch, rk45_step, _guard_no_nan/_energy/_bounds) +     factory fns (create_simulation_engine, run_monte_carlo_analysis) wired by shipping the     original `__init__` banner-normalized. Every name verified to resolve in beta. NB: this     makes `import src.simulation` EAGER (requires scipy) — intended final-wiring behavior.     No current caller depends on the package-level surface (grep of `from src.simulation     import` across both repos = EMPTY); reproduced for forward-compat.
  - **S6-2:** `MonteCarloStrategy._run_parallel_simulations` is a documented sequential     placeholder (not real multiprocessing) — matches source; preserved, not "fixed".
  - **S5-2 (now UNBLOCKED, deferred):** beta has since grown `src/config/` (schemas.py) and     `src/plant/` (models/), so the legacy `sequential.py` plant-path remap is now feasible.     NOT done here (edits a shipped byte-clean file + needs the real plant/config symbol     names, which were not pulled). Tracked as a focused follow-up slice with its own audit.
- **Milestone:** M4 (simulation framework) COMPLETE — Slices 1-6 all on `main`.
- **Carry-forward:** (1) S5-2 remap slice (pull src/plant/models + src/config/schemas symbols).   (2) Before retiring legacy engines/src.core (M6/M9): grep importers of `src.simulation.engines`   / `src.core.vector_sim` / `src.core.simulation_runner`.

---

## M5 · Slice 1 — Classical SMC port

- **When:** 2026-06-29
- **Source → Target:** `src/controllers/smc/classic_smc.py` (monolith, `ClassicalSMC`) → `src/controllers/classical_smc.py` (flat, NEW) + `src/controllers/__init__.py` (NEW)
- **Transforms (only):** EOL/banner normalize; Trap-E citation-token strip (0 remain); relocation dot reduction `from ...utils|...plant` → `from ..utils|..plant` (depth-3 → depth-2). No numeric/algorithmic edits.
- **Dropped (AI-slop):** modular twin `smc/algorithms/classical/*` + `smc/core/*` (monolith is the canonical, factory-referenced implementation).
- **Traps:** A = no-op (already grouped, verified); B = no `src.core`; E = tokens stripped. 
- **Gate:** `parity_check_m5_slice1.py` → STRUCTURAL OK (byte-identical to transformed source) + BEHAVIORAL OK (400 cases, max|repo-ref| = 0.0); 14/14 unit tests.
- **Findings for review:** (1) monolith-vs-modular drop; (2) standalone class not yet `ControllerInterface` ABC — reconcile in S5; (3) relocation import-dot edits are required & documented.
- **Commit:** `3daa54f0a2caedffc21a418520336209c15d7f1d` (record parent = `8f6407386bf9f14f177fb797c5520a02cf896be0`).

### Provenance correction (golden rule: code wins)
Earlier ledger/STATE entries recorded a pre-commit SHA (chicken-and-egg). Verified-on-`main` SHAs:
- M4 S5 = `a1834d5ac87583b4e8cac6fbd2a9eb4108c41eed` (ledger previously said `d62e12d7…`).
- M4 S6 = `8f6407386bf9f14f177fb797c5520a02cf896be0` (ledger/STATE previously said `0cc017d3…`).
Going forward, record the **parent** SHA at kit-build time and the **actual** push SHA in the CLI report.

---

## M5 · Slice 2 — Super-Twisting SMC port

- **When:** 2026-06-29
- **Source → Target:** `src/controllers/smc/sta_smc.py` (monolith, `SuperTwistingSMC`) → `src/controllers/sta_smc.py` (flat, NEW); `src/controllers/__init__.py` widened to export `SuperTwistingSMC`.
- **Transforms (only):** EOL/banner normalize; Trap-E citation-token strip (0 remain); relocation `from ...utils` → `from ..utils` (3x). No numeric/algorithmic edits.
- **Dropped (AI-slop):** modular twin `smc/algorithms/super_twisting/*` (monolith is factory-canonical; only its Config is used — deferred to S5).
- **Retained + flagged:** dead `_sta_smc_control_numba` (never called); `numba` kept behind `_DummyNumba` try/except fallback.
- **Traps:** A = no-op (already grouped, verified); B = no `src.core`; E = tokens stripped.
- **Gate:** `parity_check_m5_slice2.py` → STRUCTURAL OK (byte-identical to transformed source) + BEHAVIORAL OK (400 cases, max|du|=max|dz|=0.0, incl. saturation + anti-windup); 18/18 unit tests.
- **Lens B:** true STA law `u=-K1|s|^½ sgn(s)+z-d s`, `z+=z-K2 sgn(s)dt+Kaw(u_sat-u_raw)dt`; Moreno-Osorio `K1>K2>0` enforced in `validate_gains`; config K1=8>K2=4.
- **Findings for review:** (1) monolith-vs-modular drop; (2) standalone class not yet ControllerInterface ABC (S5); (3) dead numba fn retained for later cleanup.
- **Commit:** `0291875150821d3f98fcde64ffec2110c92131e3` (record parent `3daa54f0a2caedffc21a418520336209c15d7f1d`).

---

## M5 · Slice 3 — Adaptive SMC port

- **When:** 2026-06-30
- **Source → Target:** `src/controllers/smc/adaptive_smc.py` (monolith, `AdaptiveSMC`, sha `d8a2db6c…`) → `src/controllers/adaptive_smc.py` (flat, NEW, sha `0e82cf55a249`); `src/controllers/__init__.py` widened to export `AdaptiveSMC`.
- **Transforms (only):** EOL/banner normalize; Trap-E citation-token strip (0 remain); relocation `from ...utils` → `from ..utils` (5x). No numeric/algorithmic edits.
- **Dropped (AI-slop):** modular twin `smc/algorithms/adaptive/*` (monolith is factory-canonical; only its Config is used — deferred to S5).
- **Traps:** A = no-op (already grouped, verified); B = no `src.core`; E = tokens stripped. No numba in this module.
- **Gate:** `parity_check_m5_slice3.py` → STRUCTURAL OK (byte-identical to transformed source) + BEHAVIORAL OK (400 cases, max|du|=max|dK|=max|dt_sld|=0.0); 22/22 unit tests.
- **Lens B:** law `u=-K*sat(s/eps)-alpha*s`; dead-zone-gated leaky rate-limited adaptation `dK=gamma|s|-leak(K-K0)` (0 inside dead-zone), `K^+=clip(K+dK dt,K_min,K_max)`; `K_min<=K_init<=K_max` enforced.
- **Findings for review:** (1) monolith-vs-modular drop; (2) standalone class not yet ControllerInterface ABC (S5); (3) state_vars=(K,last_u,time_in_sliding) carries adaptive gain.
- **Commit:** `00eb5696b8d515994ac2cadd858876b4a15d746c` (record parent `0291875150821d3f98fcde64ffec2110c92131e3`).


---

## M5 · Slice 4 — Hybrid Adaptive STA-SMC port

- **When:** 2026-06-30
- **Source → Target:** `src/controllers/smc/hybrid_adaptive_sta_smc.py` (monolith, `HybridAdaptiveSTASMC`, sha `85d67e32…`) → `src/controllers/hybrid_adaptive_sta_smc.py` (flat, NEW, sha `b5d0e46a5cfa`); `src/controllers/__init__.py` widened to export `HybridAdaptiveSTASMC`.
- **Transforms (only):** EOL/banner normalize; Trap-E citation-token strip (0 remain); relocation `from ...utils` → `from ..utils` (1x). No numeric/algorithmic edits.
- **Dropped (AI-slop):** modular twin `smc/algorithms/hybrid/*` (monolith is factory-canonical; Config deferred to S5).
- **Traps:** A = no-op (already grouped, verified); B = no `src.core`; E = tokens stripped. No numba in this module.
- **Gate:** `run_gate.py` → STRUCTURAL OK (byte-identical to transformed source) + BEHAVIORAL OK (400 cases, max|du|=max|dk1|=max|dk2|=max|du_int|=max|ds|=0.0); 25/25 unit tests.
- **Lens B:** law `u = -k1*sqrt(|s|)*sat(s) + u_int - k_d*s + u_cart + u_eq`, `u_int += -k2*sat(s)*dt`; dead-zone-gated leaky/taper/time-tapered adaptation; emergency reset on divergence.
- **Findings for review:** (1) monolith-vs-modular drop; (2) standalone class not yet ControllerInterface ABC (S5); (3) broken `__del__` (intended local inside `cleanup()`) preserved verbatim to maintain byte-parity; (4) dead `use_equivalent` kwarg preserved.
- **Commit:** `bee626406fd5e800f7ad4c308912fff42a62c2ee` (record parent `a461e9d72c2039cf5fc9bd679bf5a603f3469e35`).


---

## M5 · Slice 5 — Controller Factory and Wiring port

- **When:** 2026-06-30
- **Source → Target:** `src/controllers/factory/` (multiple files) → `src/controllers/factory.py` (flat, NEW, sha `909ed188be7a…`); `src/controllers/__init__.py` widened to export the factory surface.
- **Transforms (only):** Consolidated base.py, registry.py, fallback_configs.py, types.py, validation.py and legacy_factory.py into a clean, flat beta-native `factory.py` adapter. Normalized line endings to LF, 86-col banners. No unported dependencies (core/plant) imported (Trap B).
- **Dropped (AI-slop):** modular-twin coupling in registry, legacy_factory build code for unported controllers (conditional_hybrid, MPC, swing_up, etc.), fallback configs, thread-locks.
- **ABC Reconcile:** Monolith constructors and interfaces kept as-is, with signature mismatch documented in package `__init__.py`. Interface unification deferred to future cleanup.
- **Gate:** `run_gate.py` (newly shipped) → STRUCTURAL OK (clean imports, LF-only, banners) + UNIT OK (49 checks pass) + BEHAVIORAL PARITY OK (4/4 controllers, 50 random states each vs direct construction, max|du| = 0.0). 74/74 gate tests green.
- **Commit:** `788f1e9359047cc877086bdde0fd840c998d47a3` (record parent `0f3348320421f8a81dd6e62ce46e4d1cfcca6139`).


---

## M6 · Slice 1a — Restore simulate_system_batch

- **When:** 2026-06-30
- **Source → Target:** `src/simulation/engines/vector_sim.py::simulate_system_batch` (legacy engine dropped in M4 S5) → `src/simulation/orchestrators/batch.py` (appended, NEW); `src/simulation/__init__.py` widened to export `simulate_system_batch`.
- **Transforms (only):** Restored the closed-loop batched simulation routine. EOL/banner normalized to LF, 86-col banners. No `[CIT-*]` tokens, no `src.core` imports, no numba decorators.
- **Gate:** `run_gate.py` (from kit) → STRUCTURAL OK (compile, single definition, LF, no banned tokens) + FIDELITY OK (matches reviewed snippet) + BEHAVIORAL OK (shapes, saturations, early-stopping, convergence tolerances, particle broadcast, determinism). 22/22 gate checks green.
- **Commit:** `4e5ad7f8306749cadb9a91c05b7a164774efa253` (record parent `8677a356d5d401ab8cb42df044dc0821f4f7d364`).

---

## M6 · Slice 1b — PSOTuner port

- **When:** 2026-06-30
- **Source → Target:** `SMC-PSO/src/optimization/algorithms/pso_optimizer.py` → `src/optimization/algorithms/pso_optimizer.py` (flat, NEW); `src/optimization/__init__.py` and `algorithms/__init__.py` created/widened to export `PSOTuner`.
- **Transforms (only):** EOL CRLF -> LF; banner regenerated as 86-col path-centered banner; removed 10 trailing ` # [CIT-068]` tokens; normalized 3 non-breaking spaces (U+00A0); rewrote imports to beta-native relative form.
- **Gate:** `run_gate.py` (from kit) → STRUCTURAL OK (LF, compiles, single class, exported, no CJK/CIT/nbsp/backslash slop) + FIDELITY OK (matches expected sha256) + BEHAVIORAL OK (constructs, normalises safely, cost aggregation, penalizes instability, run optimise). 34/34 gate checks green.
- **Commit:** `ba126625131d8ff00b1558362ec05c5d92640a70` (record parent `8097fbc23a97d4cb95c286437bada15906dedae1`).

---

## M6 · Slice 2 — PSO <-> Controller-Factory Integration Bridge

- **When:** 2026-06-30
- **Source → Target:** `SMC-PSO/src/optimization/integration/` → `src/optimization/integration/` (flat, NEW); `src/optimization/integration/__init__.py` re-exports all integration bridge symbols.
- **Transforms (only):** EOL CRLF -> LF; banner regenerated as 86-col path-centered banner; rewrote 5 absolute imports to relative depths.
- **Gate:** `run_gate.py` (from kit) → STRUCTURAL OK (LF, compiles, single banner, relative imports, no CIT/CJK/nbsp slop, exported) + FIDELITY OK (matches expected sha256) + BEHAVIORAL OK (members, config, construct, enhanced factory & fitness, optimize_controller). 42/42 gate checks green.
- **Commit:** `1e321e1aca248a76a05c25512c61b4e9ad8ce35f` (record parent `30d4448b0d5a5ba6000cde3f0c61d06b3975aaf6`).

---

## M7 · Slice 1 — Interfaces Core Submodule

- **When:** 2026-06-30
- **Source → Target:** `SMC-PSO/src/interfaces/core/` → `src/interfaces/core/` (NEW); contains `__init__.py`, `data_types.py`, and `protocols.py`.
- **Transforms (only):** LF EOL normalization, 86-col centered banner regeneration, trailing-newline normalization.
- **Gate:** `run_gate.py` (from kit) → STRUCTURAL OK (LF, compiles, centered banners, relative imports, no slop, exported __all__) + FIDELITY OK (matches expected sha256) + BEHAVIORAL OK (symbols resolve, instantiate dataclasses, ABC protocols abstract, method smoke). 53/53 gate checks green.
- **Commit:** `6c8264efa21b60d0eee807c3f4f3a6a2471efb13` (record parent `1e321e1aca248a76a05c25512c61b4e9ad8ce35f`).

---

## M7 · Slice 2 — Interfaces Data Exchange Submodule

- **When:** 2026-06-30
- **Source → Target:** `SMC-PSO/src/interfaces/data_exchange/` → `src/interfaces/data_exchange/` (NEW); contains 7 files (`__init__.py`, `data_types.py`, `factory.py`, `factory_resilient.py`, `schemas.py`, `serializers.py`, `streaming.py`).
- **Transforms (only):** LF EOL normalization, 86-col centered banner regeneration, trailing-newline normalization, bake in three fixes: `DataPacket.unpack()` (guard size/slice corrected to 16 bytes; payload guard corrected to 16 + payload_length) and `__init__.py` (removed phantom `PerformanceSerializer`/`SerializationMetrics` from `__all__`).
- **Gate:** `run_gate.py` (from kit) → STRUCTURAL OK (compile, centered banners, relative imports, clean __all__) + FIDELITY OK (matches expected sha256) + BEHAVIORAL OK (formats round-trip: JSON, Pickle, Custom binary, Compression wrap; schemas and custom validators; thread-safe StreamBuffer FIFO and backpressure; rejects truncated payload). 102/102 gate checks green.
- **Commit:** `a6c2b8ba30fcca7e83e5a53cc5f388b177294069` (record parent `6c8264efa21b60d0eee807c3f4f3a6a2471efb13`).
