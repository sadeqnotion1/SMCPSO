# NEXT -- the handoff card

> Exactly one task, run with the audit loop in `brain/MIGRATION_PLAN.md`
> (port -> audit A+B -> prove C -> gate -> accept). ASCII markers only.
> Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

## -> The one next task (M3): port + AUDIT `src/utils/` -- SECOND SLICE: control.primitives (saturation, seeding)
M3 Slice 1 (types + validation) is [DONE] and accepted on main.
Scope for the second slice:
- SECOND SLICE = `src/utils/control/primitives/` (such as saturation, seed-setting, etc.) ONLY.
- Logging, metrics, visualization, analysis, infrastructure, monitoring, numerical_stability, testing are LATER slices of M3 -- do NOT port them yet.

## Decisions locked this session (2026-06-24)
- Scope cut: types + validation first; defer logging/metrics/viz to later M3 slices.
- Dedupe policy: FLAG-ONLY. Where a util overlaps `src/plant/core/` (or any core/), log each
  duplicate as a [P2] watch-item in the Audit Card -- do NOT consolidate/refactor this pass.
- `src/core/`, `src/optimizer/`, `src/deprecated/` are deprecated compat shims (see ROADMAP):
  do NOT port them; treat them as non-canonical when comparing.

## Source locations (confirmed in repo)
- Untouched source repo: `E:\University\SMC-PSO`     -> `src/utils/` (types + validation modules)
- Target repo:           `E:\University\SMC-PSO-beta` -> `src/utils/`
- Existing beta stubs (if any) under `SMC-PSO-beta/src/utils/`: anchor edits, do not blind-overwrite.

## Start the next chat with this
> "Read .agents/AGENTS.md + brain. M3 Slice 1 (types + validation) is DONE. Begin M3 Second Slice -- `control.primitives` (saturation, seed-setting). Dedupe vs core/ = FLAG-ONLY. Port faithfully from SMC-PSO/src/utils/control/primitives/, minimal/additive/anchored. Show the file-level plan BEFORE writing code; file the Audit Card update; gate P0=0/P1=0."

## Definition of done for M3 second slice (the gate)
- control.primitives modules ported to beta `src/utils/control/primitives/`.
- Lens A: no fake/placeholder code, no hallucinated APIs, no dead code; findings logged.
- Lens B: saturation functions, seed validation, etc. match mathematical correctness (e.g. saturation bounds correctly clamped).
- Lens C: unit tests for saturation and seeding logic; coverage on control primitives paths.
- Dedup overlaps with core/ logged as [P2] (flag-only). Audit Card updated, ledger updated, P0 = 0 / P1 = 0.

## Watch-items carried in (do NOT lose)
- M2.v5 [P2/OPEN]: golden source-parity (SMC-PSO/ trajectories vs beta) was NEVER run -- M2 was
  accepted on the invariant gate only. Run `scripts/parity_check.py --emit-golden` / `--compare`
  on your machine OR record a formal deferral in DECISIONS.md.
- F-PLANT-2, F-PLANT-3 [P2/OPEN]: revisit at M4 (DIPParams compat defaults; DIPDynamics alias).
- plant.A7 [P2/OPEN]: simplified-model inertia fudge (deferred per D9; plant simplified/low-rank).

## After M3
M3 remaining slices (logging / metrics / viz) -> M4 controllers base + `src/simulation/`.
