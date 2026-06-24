# NEXT -- the handoff card

> Exactly one task, run with the audit loop in `brain/MIGRATION_PLAN.md`
> (port -> audit A+B -> prove C -> gate -> accept). ASCII markers only.
> Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

## -> The one next task (M3): port + AUDIT `src/utils/` -- FIRST SLICE: types + validation only
M2 (plant, full) is [DONE] and accepted on main. Start M3 on a fresh branch `migration/utils`.
Scope is deliberately narrow this pass (owner decision, 2026-06-24):
- FIRST SLICE = the **types** and **validation** primitives under `src/utils/` ONLY.
- Logging, metrics, and visualization are LATER slices of M3 -- do NOT port them yet.

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
> "Read .agents/AGENTS.md + brain. M2 Plant is DONE. Begin M3 -- Utils, FIRST SLICE = types +
> validation ONLY (skip logging/metrics/viz this pass). Dedupe vs core/ = FLAG-ONLY (log dupes
> as P2, do not refactor; core/ is a deprecated shim -- do not port). Port faithfully from
> SMC-PSO/src/utils/, minimal/additive/anchored, back up first. Show the file-level plan BEFORE
> writing code; file the Audit Card to brain/audits/utils.md; gate P0=0/P1=0."

## Definition of done for M3 first slice (the gate)
- types + validation modules ported to beta `src/utils/`; logging/metrics/viz untouched/deferred.
- Lens A: no fake/placeholder code, no hallucinated APIs, no dead code; findings logged.
- Lens B: validation predicates + any type/metric definitions match their scientific/physical
  meaning (units, bounds); cross-checked where a reference exists.
- Lens C: real + property unit tests for types/validation (bound checks, NaN guards); coverage
  on the validation paths.
- Dedup overlaps with core/ logged as [P2] (flag-only). Audit Card filed (brain/audits/utils.md),
  ledger updated, P0 = 0 / P1 = 0. Then mark the M3 slice in STATE.md / ROADMAP.md.

## Watch-items carried in (do NOT lose)
- M2.v5 [P2/OPEN]: golden source-parity (SMC-PSO/ trajectories vs beta) was NEVER run -- M2 was
  accepted on the invariant gate only. Run `scripts/parity_check.py --emit-golden` / `--compare`
  on your machine OR record a formal deferral in DECISIONS.md.
- F-PLANT-2, F-PLANT-3 [P2/OPEN]: revisit at M4 (DIPParams compat defaults; DIPDynamics alias).
- plant.A7 [P2/OPEN]: simplified-model inertia fudge (deferred per D9; plant simplified/low-rank).

## After M3
M3 remaining slices (logging / metrics / viz) -> M4 controllers base + `src/simulation/`.
