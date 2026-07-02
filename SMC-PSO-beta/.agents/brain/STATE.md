# STATE -- where we are right now

> Single source of truth. If this disagrees with the real code, the **code wins** -- tell me
> and I fix the brain. ASCII markers only. Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

**Status (one-liner):** Migrating `dip-smc-pso` from `SMC-PSO/` into the clean `SMC-PSO-beta/`
scaffold, **dependency-first AND audit-driven**: every module is ported, audited for AI-slop
+ scientific correctness, and proven by parity/tests BEFORE it is accepted (see
`brain/MIGRATION_PLAN.md`). Config phase is done; `.agents/` brain installed; `ai/` merged in.

## Migration phases (gated -- a phase is DONE only after its Audit Card passes)

| Milestone | Scope | Status |
|-----------|-------|--------|
| M1 Environment & config | requirements / setup / config.yaml / `src/config/` | [DONE] (re-audit pins owed) |
| M2 Plant dynamics (FULL model first) | `src/plant/models/` FULL model only + parity harness (simplified/low-rank scaffolds present but out of M2 scope -> see D9 row) | [DONE] physical consistency verified, W1 refs resolved, parity documented — Finding #2 resolved 2026-06-28 |
| M3 Utils & primitives | `src/utils/` | [WIP] (Slices 1-7 accepted) |
| M4 Controllers base + sim core | `src/controllers/base.py`, `src/simulation/` | [DONE] — Slices 1-6 all on main (framework complete) @ 8f640738 |
| M5 Controller implementations | classical / sta / adaptive / hybrid + factory | [DONE] — S1-S5 complete on main @ 788f1e93 |
| M6 Optimization | `src/optimization/` | [DONE] — S1a-S1b-S2 complete on main @ 1e321e1a |
| M7 Interfaces / HIL | src/interfaces/ (was missing from old plan) | [DONE] - all 6 submodules + top-level package __init__ (banner + lazy sub-module importer) on main. M7-S2-3 async-hang CLOSED @ bb513058. M7-S7 package __init__ @ 336d2cf56a0f3e7a7978a076a3d89bb5ee66f0a8. |
| M8 | Analysis | **[WIP]** | S1 core [DONE @ aed89ba], S2 fault_detection [DONE @ 74ef536], S3a validation-foundation [DONE @ b8d449d9fe4774f2df272582297e95c25de62d29], S3b validation-heavy [DONE @ 25194860071fb6a473cdad8e192c7a274b17419e], S4 performance [DONE @ bf11cac706580ecc263ef8b9c0bc587f0b607234], S5 visualization [NEXT], S6 reports+lazy __init__ |
| M9 Entry points | `simulate.py`, `streamlit_app.py` | [TODO] |
| M10 Benchmarks (+ integration/assets) | `src/benchmarks/` (was missing) | [TODO] |
| M11 Verification suite & gates | `tests/`, coverage gates, CI | [TODO] |
| -- plant simplified/low-rank | scaffold files present in beta (src/plant/models/simplified/, src/plant/models/lowrank/); validation + parity-testing deferred follow-up after M2 (D9) | [TODO] (scaffolded, not yet validated) |

## M8 - Analysis module (plan + locked decisions)

**Scope:** port `SMC-PSO/src/analysis/` -> `SMC-PSO-beta/src/analysis/` (6 subpackages, 29 files).
`src/utils/analysis/` is a SEPARATE module - already handled in M3; do not touch it here.
`src/analysis/validation/statistics.py` (CI/bootstrap/ANOVA/etc.) is NOT a duplicate of
`src/utils/analysis/statistics.py` (welch/monte-carlo) - keep both.

**Dependency order (drives slice order):** `core` -> {`fault_detection`, `validation`, `performance`}
-> `visualization` -> top-level `__init__`.

**Slice plan (each = its own backup-first, gated, focused-commit kit, mirroring M7 cadence):**
- **S1 core/** - interfaces, data_structures, metrics, __init__. No cross-module deps. **DONE @ `aed89bad467017c1673695d7046bdd4fee86bcb4`.**
- **S2 fault_detection/** - fdi, fdi_system, residual_generators, threshold_adapters. core + scipy. Clean.
- **S3 validation/** - 9 files. core + scipy. Guard the lazy `benchmarks` import in statistical_benchmarks.py.
- **S4 performance/** - BLOCKED by cross-module coupling. See DECISIONS below.
- **S5 visualization/** - matplotlib-heavy. Guard the matplotlib import (lazy) so import-time is clean.
- **S6 reports/ (empty) + top-level src/analysis/__init__.py as a LAZY PEP-562 loader** (NOT the original eager __init__, which hard-fails today). Closes M8.

**LOCKED DECISIONS (SadeQ, 2026-07-01) - do NOT defer to a later 'fix kit':**
1. **performance/ deps -> Decouple & guard.** In S4: drop the `benchmarks.metrics.*` re-exports from
   `performance/__init__.py` (keep only `ControlAnalyzer`); make the MPC import
   (`src.controllers.mpc.mpc_controller`, excluded in M5) and the `src.plant.core.numerical_stability`
   (deprecated twin) imports lazy + guarded. Port performance now; log residual coupling as findings.
   Keeps M8 self-contained (no pulling M10 benchmarks forward).
2. **robustness.py placeholders -> FIX IN-SLICE (S4).** Implement REAL perturbation / re-simulation in
   the robustness methods that currently `return nominal` (lines ~479-689, multiple
   `# TODO: Implement actual perturbed simulation`). Do it as part of S4; do not ship a hollow port.
   Note: core/RobustnessMetrics honest-NaN behavior is fine and stays; this decision is about
   `performance/robustness.py` which silently returns nominal data (scientifically misleading).

**Namespace note:** submodule slices (S1-S5) ship WITHOUT a top-level `src/analysis/__init__.py`;
`src.analysis` is a namespace package until S6 (same pattern proven in M7).

## Audit posture (why this plan changed)
- Repo was largely AI-generated -> every ported file is **"guilty until verified."**
- Two lenses on every module: (A) AI-slop/code defects, (B) scientific/math correctness.
- Gate: P0 = 0, P1 = 0, parity passes, coverage met, Audit Card filed. Findings -> `AUDIT_LEDGER.md`.
- Lens B oracle = `references/proofs/` + `references/controllers.bib` + `references/config.bib`,
  but those references are themselves audited for authenticity (ledger W1).

## Open decisions / questions waiting on you
- Confirm package import root (`src/` flat vs `src/<pkg>/`).
- (RESOLVED D9) Plant fidelity: full model first, simplified/low-rank deferred.
- (RESOLVED D10) Reference equations: use repo `references/` (proofs + bib), validate authenticity.

## Known risks / watch-items
- [RESOLVED] W1 (ledger): `references/proofs/` + `.bib` verified genuine.
- Source has duplicated logic: `src/core/` vs `src/simulation/`, `src/optimizer/` vs
  `src/optimization/`, and a nested `src/plant/core/` -- canonical wins; shims dropped.
  Do NOT port the deprecated dirs.
- Source has a stray mojibake file (`DProjects...compile.bat`) -- do NOT carry it over.
- `numpy<2.0` must stay pinned for Numba; verify in M1 re-audit.
- Numba batch path must keep numeric parity with the pure-Python path.
- [OPEN — M5] Trap A: state-ordering; canonical=GROUPED, adapters shipped.

---

## Session update — 2026-06-28 (M4 boundary)
- **Finding #2 (physics_matrices): RESOLVED.** Corrected math wired into
  `physics_matrices.py`; `physics.py` delegates to it. Verified by
  `tests/test_plant/test_full_dynamics_invariants.py` (all invariants pass).
  M2 acceptance re-closed.
- **M4 Slice 1 (`src/controllers/base.py`): DONE.** Flattened from the source
  `controllers/base/` package; AI-slop citation tokens removed.
- **Trap A (state ordering): PINNED.** Canonical = GROUPED
  `[x, theta1, theta2, x_dot, theta1_dot, theta2_dot]`
  (see `.agents/brain/STATE_VECTOR_CONVENTION.md`). Adapters + guard test shipped.
  Controller-side conversion is deferred to **M5** and is the top open risk.
- **M4 Slice 2 (`src/simulation/core/`): DONE.** Ported interfaces, simulation_context,
  state_space, time_domain + minimal `simulation/__init__`. Trap C: dropped the `context/`
  twin (deferred to Slice 4). Trap D: minimal package __init__, legacy aliases deferred.
  `wrap_physics_config` import made lazy so `import src.simulation.core` works before
  utils/factory land. 24/24 tests green; parity vs source OK; no `src/core` imports.
- **M4 Slice 3 (`src/simulation/integrators/`): DONE.** Ported fixed-step (Euler family,
  RK2/RK4/RK 3/8), adaptive (Dormand-Prince 4(5) + error control), discrete (zero-order hold),
  factory and compatibility wrappers. ZERO functional edits — byte-identical to source modulo
  banner normalization (machine-verified). 47/47 tests green; structural + numerical parity OK;
  no src/core imports.
- **M4 Slice 4 (`src/simulation/safety/`): DONE.** Ported guards, constraints, monitors,
  recovery. ZERO functional edits — byte-identical to source modulo banner normalization
  (machine-verified). 25/25 tests green; structural + behavioral parity OK; no src/core imports.
- **Trap C RESOLVED:** the `context/` twin was DROPPED (not ported). core.SimulationContext
  (Slice 2) is a strict superset of context/simulation_context; safety/guards supersedes
  context/safety_guards (identical frozen substrings). Nothing unique lost.
- **Watch-item S2-3 RESOLVED (false alarm):** safety.PerformanceMonitor IS
  core.interfaces.PerformanceMonitor (re-export, not a duplicate); concrete impl is
  SimulationPerformanceMonitor.
- **NOTE (frozen substrings):** safety guard messages keep literal `<i>/<val>/<max>/<t>`
  placeholders ON PURPOSE (acceptance-test matching) — do not "fix" them.
- **M4 Slice 5 (results + orchestrators; engines DROPPED / Trap F) — DONE @ a1834d5a.** Ported results (containers, exporters, processors, validators) and orchestrators (base, sequential, batch, parallel, real_time). 26 tests green, banner-only structural + RK4 behavioral parity OK, no `src/core/` imports.
- **M4 Slice 6 (strategies + package wiring / Trap D) — DONE @ 8f640738.** Ported strategies (monte_carlo) and wired package re-exports (get_step_fn, step, run_simulation, simulate, rk45_step, _guard_* aliases). 19 tests green, banner-only structural + Monte Carlo behavioral parity OK, no `src/core/` imports. M4 Complete.

## M4 Traps status — ALL CLOSED
- Trap A (state ordering `[x, theta1, theta2, x_dot, theta1_dot, theta2_dot]`): respected.
- Trap B (`src/core/*` shims): NOT ported.
- Trap C (`context/` twin): DROPPED (Slice 4).
- Trap D (package-level re-exports): CLOSED (Slice 6 — wired __init__).
- Trap E (citation tokens): none in ported files.
- Trap F (`engines/` duplicate): DROPPED (Slice 5).

## Open follow-ups (post-M4)
- **S5-2 remap (now unblocked):** beta grew `src/config/` + `src/plant/`; remap the dead lazy plant/config paths in `orchestrators/sequential.py` (own slice + audit). sequential.py is currently byte-identical to source.
- Before retiring legacy `engines/` + `src/core/*` (M6/M9): grep repo for importers of `src.simulation.engines` / `src.core.vector_sim` / `src.core.simulation_runner`.

## Slice ledger
- Slice 2 core — DONE `2e7f5a0ca93487871e00117c89ac6b2e7650820c`
- Slice 3 integrators — DONE `ed82b3c82659891ea2c7279154827db41285d38d`
- Slice 4 safety (+Trap C) — DONE `239df497011b20221b4ff238569f53f7552272ff`
- Slice 5 results + orchestrators (+Trap F) — DONE `a1834d5ac87583b4e8cac6fbd2a9eb4108c41eed`
- Slice 6 strategies + package wiring (+Trap D) — DONE `8f6407386bf9f14f177fb797c5520a02cf896be0`

## M5 Slice ledger
- S1 classical_smc.py ...... [DONE]   @ 3daa54f0a2caedffc21a418520336209c15d7f1d
- S2 sta_smc.py ............ [DONE]   @ 0291875150821d3f98fcde64ffec2110c92131e3
- S3 adaptive_smc.py ....... [DONE]   @ 00eb5696b8d515994ac2cadd858876b4a15d746c  (parent 02918751)
- S4 hybrid_adaptive_sta ... [DONE]   @ bee626406fd5e800f7ad4c308912fff42a62c2ee
- S5 factory.py + __init__ . [DONE]   @ 788f1e9359047cc877086bdde0fd840c998d47a3

Note: `src/controllers/__init__.py` now exports `ClassicalSMC` + `SuperTwistingSMC` + `AdaptiveSMC` + `HybridAdaptiveSTASMC` (still slice-scoped; widen as S5 lands).

## M6 Optimization Ledger
- S1a simulate_system_batch .. [DONE]   @ 4e5ad7f8306749cadb9a91c05b7a164774efa253
- S1a-fix import logging .... [DONE]   @ ca1e553d4d3bc83935b53794aea8be1d70e35cb4
- S1b PSOTuner port .......... [DONE]   @ ba126625131d8ff00b1558362ec05c5d92640a70
- S2 integration bridge ...... [DONE]   @ 1e321e1aca248a76a05c25512c61b4e9ad8ce35f

## Session update - 2026-07-01 (M7 close)
- **M7-S7 (`src/interfaces/__init__.py`): DONE @ 336d2cf56a0f3e7a7978a076a3d89bb5ee66f0a8.** Ported the top-level package banner + PEP 562 lazy sub-module importer from SMC-PSO/ source.
- **P1 fix:** source hardcoded `import_module(..., package='interfaces')`, which breaks under the beta `src` layout; changed to `package=__name__`. Sandbox proof: ported resolves 84/84 advertised symbols under `src.interfaces`; the original resolved 0/84.
- Lens B: all 84 `__all__`/`_LAZY_IMPORTS` names verified against the 6 ported submodules; no dangling refs and no imports of the deprecated network twins (dropped in the port).
- Added `tests/test_interfaces/test_interfaces_package_init.py` (framework-info consistency + all advertised names resolve + unknown-attr raises).
- **M7 is now COMPLETE.** Open P0 = 0, Open P1 = 0.

## Next milestone
- Proceed to **M8-S5 (visualization/)** (guard matplotlib imports lazily, resolve M8-SCHED-6).

## M7 Interfaces / HIL Ledger
- S1 interfaces core ........ [DONE]   @ 6c8264efa21b60d0eee807c3f4f3a6a2471efb13
- S2 data exchange .......... [DONE]   @ a6c2b8ba30fcca7e83e5a53cc5f388b177294069
- S3 hardware drivers ....... [DONE]   @ f76adc137b768cb835927e35a3d7016ceacf45e4
- S4 monitoring ............. [DONE]   @ 6f77cfab529eeaca8067a02cb376366bcc08bf5f
- S5 network interfaces ..... [DONE]   @ bc0c8829a42d4440d4e824191e124ebe3a1cca4d
- S6 HIL simulation & wiring  [DONE]   @ 29bab7ab53c689bf9cba9ff412d104c92fcf4a6d
- S7 interfaces/__init__.py ... [DONE]   @ 336d2cf56a0f3e7a7978a076a3d89bb5ee66f0a8  (banner + lazy sub-module importer; P1 package=__name__ fix)

## M8 Analysis Ledger
- S1 core/ .................. [DONE]   @ aed89bad467017c1673695d7046bdd4fee86bcb4  (foundation; interfaces, data_structures, metrics)
- S2 fault_detection/ ....... [DONE]   @ 74ef5361717983a2305fa04903774d0f9b5e2068  (fdi, fdi_system, residual_generators, threshold_adapters; fail-loud param-est; stripped fdi citation slop)
- S3a validation foundation . [DONE]   @ b8d449d9fe4774f2df272582297e95c25de62d29  (__init__, statistical_benchmarks, core, metrics, statistics; stripped unicode-dash)
- S3b validation heavy ...... [DONE]   @ 25194860071fb6a473cdad8e192c7a274b17419e  (benchmarking, cross_validation, monte_carlo, statistical_tests; honest-degraded p-values; slop normalized)
- S4 performance/ ........... [DONE]   @ bf11cac706580ecc263ef8b9c0bc587f0b607234  (ControlAnalyzer, control_analysis, control_metrics, robustness, stability_analysis; real re-sims; MPC lazy-guarded)
- S5 visualization/ ......... [PENDING]
- S6 reports/ & __init__ .... [PENDING]

### Session update - 2026-07-01
- M8 opened. Recon audit of the full `src/analysis/` pack complete (29 files, 6 subpackages).
- Locked S4 decisions with SadeQ: (1) decouple & guard performance deps; (2) fix robustness.py
  perturbation in-slice. Recorded above so they survive to S4.
- **M8-S1 (core/) DONE @ aed89bad467017c1673695d7046bdd4fee86bcb4** (brain 9b40276): interfaces + data_structures + metrics
  ported (banner slop stripped, CRLF->LF, no functional edits), +7 regression tests. Full suite 971 green.
- **Next: M8-S2 (fault_detection/).**

- M8-S2 applied: ported src/analysis/fault_detection/ (5 files) + tests/test_analysis/test_fault_detection.py (12 tests).
  Faithful port except: fdi.py stripped 6 fabricated citation anchors + normalized U+2011 hyphen (M8-S2-1);
  ParameterEstimationGenerator._estimate_parameters now raises NotImplementedError instead of fabricating via
  np.random (M8-S2-2, locked decision: fail-loud). No top-level src/analysis/__init__.py yet (namespace pattern).
  Note (flag only, resolve at S6): fdi_system.py ships a duplicate "legacy" FDIsystem + DynamicsProtocol with
  DIFFERENT defaults (threshold 0.5, no hysteresis) vs fdi.py's calibrated 0.150 + hysteresis (M8-S2-3).
- **M8-S2 DONE @ 74ef5361717983a2305fa04903774d0f9b5e2068** (brain d42164a).
- **Next: M8-S3 (validation/).**

- M8-S3a: ported analysis/validation foundation (`__init__`, `statistical_benchmarks`, `core`, `metrics`, `statistics`) — banner-strip + LF + Unicode-dash->ASCII only. Added `tests/test_analysis/test_validation_foundation.py` (13 tests). M8-SCHED-5 found VOID (docstring-only import). Findings M8-S3a-1 (P2 latent ImportError in advanced wrappers) and M8-S3a-2 (P3 dash slop, fixed). Open P0=0, P1=0.
- **M8-S3a DONE @ b8d449d9fe4774f2df272582297e95c25de62d29** (brain 9c494e0).
- **Next: M8-S3b (validation_heavy).**

- M8-S3b: Ported src/analysis/validation heavy modules: benchmarking.py, cross_validation.py, monte_carlo.py, statistical_tests.py. Decision honest_degrade applied to statistical_tests.py ONLY: nulled 3 fabricated hardcoded p-values (Anderson-Darling ~L246, ADF ~L488, KPSS ~L513) -> p_value=None + method='simplified'; real statistics/critical values preserved. Power analysis turned out to use real scipy (t.cdf/t.ppf/norm.ppf) -> no fabricated value to null; faithful port + P3 doc flag only. ASCII-slop normalized: U+00B1 (monte_carlo comment) -> +/-, U+2260 (2 statistical_tests labels) -> !=. __init__.py NOT modified (these 4 modules are import-by-path; source does not export them). Added tests/test_analysis/test_validation_heavy.py (12 tests incl. honest-degrade pins + over-degrade guards). M8-S3 fully complete.
- **M8-S3b DONE @ 25194860071fb6a473cdad8e192c7a274b17419e** (brain 310b82f).
- **Next: M8-S4 (performance/).**

- M8-S4: Ported src/analysis/performance/ (5 modules). Dropped benchmarks re-exports (M8-SCHED-1); control_analysis MPC imports lazy-guarded (M8-SCHED-2); stability_analysis plant.core imports regularizer-guarded (M8-SCHED-3); robustness.py placeholder re-simulations replaced with real linear state-space re-simulation using scipy.signal.lsim (M8-SCHED-4). Added tests/test_analysis/test_performance.py (17 tests). Full test suite 1025 passed.
- **M8-S4 DONE @ bf11cac706580ecc263ef8b9c0bc587f0b607234** (brain 7a7099c).
- **Next: M8-S5 (visualization/).**






