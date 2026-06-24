# NEXT -- the handoff card

> Exactly one task, run with the audit loop in `brain/MIGRATION_PLAN.md`
> (port -> audit A+B -> prove C -> gate -> accept). ASCII markers only.
> Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

## -> The one next task (M3): port + AUDIT `src/utils/` -- THIRD SLICE: testing.reproducibility (seeding)
M3 Slices 1 and 2 (types + validation, control.primitives saturation) are [DONE] and accepted on main.
Scope for the third slice:
- THIRD SLICE = `src/utils/testing/reproducibility/` (specifically `seed.py` / `set_global_seed`) ONLY.
- Note: The source primitives/ directory did not contain seeding; it lives in testing/reproducibility/.
- Logging, metrics, visualization, analysis, infrastructure, monitoring, numerical_stability are LATER slices of M3 -- do NOT port them yet.

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
> "Read .agents/AGENTS.md + brain. M3 Slices 1 & 2 are DONE. Begin M3 Third Slice -- `testing.reproducibility` (specifically `seed.py` / `set_global_seed`). Dedupe vs core/ = FLAG-ONLY. Port faithfully from SMC-PSO/src/utils/testing/reproducibility/, minimal/additive/anchored. Show the file-level plan BEFORE writing code; file the Audit Card update; gate P0=0/P1=0."

## Definition of done for M3 third slice (the gate)
- testing.reproducibility modules ported to beta `src/utils/testing/reproducibility/`.
- Lens A: no fake/placeholder code, no hallucinated APIs, no dead code; findings logged.
- Lens B: seeding/reproducibility functions set state correctly across all libraries (NumPy, PyTorch, random, etc. as appropriate).
- Lens C: unit tests for seeding logic verifying reproducibility of random draws; coverage on testing paths.
- Dedup overlaps with core/ logged as [P2] (flag-only). Audit Card updated, ledger updated, P0 = 0 / P1 = 0.

## Watch-items carried in (do NOT lose)
- M2.v5 [P2/OPEN]: golden source-parity (SMC-PSO/ trajectories vs beta) was NEVER run -- M2 was
  accepted on the invariant gate only. Run `scripts/parity_check.py --emit-golden` / `--compare`
  on your machine OR record a formal deferral in DECISIONS.md.
- F-PLANT-2, F-PLANT-3 [P2/OPEN]: revisit at M4 (DIPParams compat defaults; DIPDynamics alias).
- plant.A7 [P2/OPEN]: simplified-model inertia fudge (deferred per D9; plant simplified/low-rank).

## After M3
M3 remaining slices (logging / metrics / viz) -> M4 controllers base + `src/simulation/`.
