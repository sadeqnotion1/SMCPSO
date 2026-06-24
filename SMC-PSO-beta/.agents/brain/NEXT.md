# NEXT -- the handoff card

> Exactly one task, run with the audit loop in `brain/MIGRATION_PLAN.md`
> (port -> audit A+B -> prove C -> gate -> accept). ASCII markers only.
> Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

## -> The one next task (M3): port + AUDIT `src/utils/` -- SIXTH SLICE: monitoring (diagnostics + performance telemetry)
M3 Slices 1, 2, 3, 4 and 5 (types + validation, control.primitives saturation, testing.reproducibility seeding, numerical_stability safe operations, analysis statistics) are [DONE] and accepted on main.
Scope for the sixth slice:
- SIXTH SLICE = `src/utils/monitoring/` ONLY.
- Logging, visualization, infrastructure, testing (except reproducibility) are LATER slices of M3 -- do NOT port them yet.

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
> "Read .agents/AGENTS.md + brain. M3 Slices 1-5 are DONE. Begin M3 Sixth Slice -- `monitoring` (diagnostics + performance telemetry). Dedupe vs core/ = FLAG-ONLY. Port faithfully from SMC-PSO/src/utils/monitoring/, minimal/additive/anchored. Show the file-level plan BEFORE writing code; file the Audit Card update; gate P0=0/P1=0."

## Definition of done for M3 sixth slice (the gate)
- monitoring modules ported to beta `src/utils/monitoring/`.
- Lens A: no fake/placeholder code, no hallucinated APIs, no dead code; findings logged.
- Lens B: monitoring and telemetry metrics are mathematically correct and match domain specifications.
- Lens C: unit tests for monitoring operations; coverage on telemetry code paths.
- Dedup overlaps with core/ logged as [P2] (flag-only). Audit Card updated, ledger updated, P0 = 0 / P1 = 0.

## Watch-items carried in (do NOT lose)
- M2.v5 [P2/OPEN]: golden source-parity (SMC-PSO/ trajectories vs beta) was NEVER run -- M2 was
  accepted on the invariant gate only. Run `scripts/parity_check.py --emit-golden` / `--compare`
  on your machine OR record a formal deferral in DECISIONS.md.
- F-PLANT-2, F-PLANT-3 [P2/OPEN]: revisit at M4 (DIPParams compat defaults; DIPDynamics alias).
- plant.A7 [P2/OPEN]: simplified-model inertia fudge (deferred per D9; plant simplified/low-rank).
- UTILS-DEDUP-4 [P2/OPEN]: top-level `src/utils/seed.py` vs `testing/reproducibility/seed.py` duplicate.
- UTILS-DEDUP-5 [P2/OPEN]: `EPSILON_EXP = 700.0` in numerical_stability duplicates clamp in control/primitives/saturation.py.
- S5-A3 [P2/OPEN]: return type uses builtin `any` instead of `typing.Any` in `analysis/statistics.py`.
- scipy dependency: Ensure SciPy is listed in requirements (added in reqs, confirm pinning in M1 re-audit).

## After M3
M3 remaining slices (logging / metrics / viz) -> M4 controllers base + `src/simulation/`.
