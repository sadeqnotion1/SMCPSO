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
| M4 Controllers base + sim core | `src/controllers/base.py`, `src/simulation/` | [DONE] — Slices 1-6 all on main (framework complete) @ 0cc017d3 |
| M5 Controller implementations | classical / sta / adaptive / hybrid + factory | [TODO] |
| M6 Optimization | `src/optimization/` | [TODO] |
| M7 Interfaces / HIL | `src/interfaces/` (was missing from old plan) | [TODO] |
| M8 Analysis | `src/analysis/` (was missing) | [TODO] |
| M9 Entry points | `simulate.py`, `streamlit_app.py` | [TODO] |
| M10 Benchmarks (+ integration/assets) | `src/benchmarks/` (was missing) | [TODO] |
| M11 Verification suite & gates | `tests/`, coverage gates, CI | [TODO] |
| -- plant simplified/low-rank | scaffold files present in beta (src/plant/models/simplified/, src/plant/models/lowrank/); validation + parity-testing deferred follow-up after M2 (D9) | [TODO] (scaffolded, not yet validated) |

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
- **M4 Slice 5 (results + orchestrators; engines DROPPED / Trap F) — DONE @ d62e12d7.** Ported results (containers, exporters, processors, validators) and orchestrators (base, sequential, batch, parallel, real_time). 26 tests green, banner-only structural + RK4 behavioral parity OK, no `src/core/` imports.
- **M4 Slice 6 (strategies + package wiring / Trap D) — DONE @ 0cc017d3.** Ported strategies (monte_carlo) and wired package re-exports (get_step_fn, step, run_simulation, simulate, rk45_step, _guard_* aliases). 19 tests green, banner-only structural + Monte Carlo behavioral parity OK, no `src/core/` imports. M4 Complete.

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
- Slice 5 results + orchestrators (+Trap F) — DONE `d62e12d739c86dadf861e7540cacc80ce3416009`
- Slice 6 strategies + package wiring (+Trap D) — DONE `0cc017d3acfa453553645e9d9f7992d295e355bb`

## Next milestone
- Proceed to M5 per MIGRATION_PLAN.md.






