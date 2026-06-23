# NEXT -- the handoff card

> Exactly one task, run with the audit loop in `brain/MIGRATION_PLAN.md`
> (port -> audit A+B -> prove C -> gate -> accept). ASCII markers only.
> Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

## -> The one next task (M3): Port, audit, and verify `src/utils/`
We need to migrate utility modules from `SMC-PSO/src/utils/` (including types, validation, logging, metrics, and visualization) to `SMC-PSO-beta/src/utils/`.

## Source locations (confirmed in repo)
- Untouched source repo: `E:\University\SMC-PSO`
- Target repo: `E:\University\SMC-PSO-beta`
- Module directory: `src/utils/`

## Start the next chat with this
> "Read .agents/AGENTS.md + brain (esp. MIGRATION_PLAN.md). Start milestone M3:
> (1) Review files in `E:\University\SMC-PSO\src\utils` and compare them with any existing structure in `E:\University\SMC-PSO-beta\src\utils`.
> (2) Migrate the utilities, deduplicate any overlap with `src/plant/core/`, verify definition correctness of all metrics, and write invariant unit tests for them."

## Definition of done for M3 (the gate)
- All utility files ported and verified against scientific definitions.
- Unit testing coverage check for metric computations is implemented.
- STATE.md / ROADMAP.md updated to [DONE] for M3 once completed.

## After M3
M4 controllers base + `src/simulation/`.

