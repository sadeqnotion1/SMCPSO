# Brain Changelog

Track changes to the **brain itself** here (not project features). Newest on top.

## v2.2 — 2026-06-23 (merged ai/ into .agents/)
- Merged `ai/AGENTS.md` + `ai/CLAUDE.md` into a single `.agents/AGENTS.md` (one file for
  the AI terminal). Stripped injected/auto-push directives; flagged source-only sections.
- Folded `ai/planning/migration_plan.md` into `brain/ROADMAP.md` (M1..M8) + `brain/STATE.md`.
- Reconciled the knowledge graph to the canonical `src/` layout (`src/simulation/`,
  `src/optimization/`); `src/core/` + `src/optimizer/` noted as deprecated shims.
- Re-pointed `brain/NEXT.md` to Migration Phase 2 (`src/plant/`), dependency-first.
- Added decisions D3 (merge), D4 (dependency-first order), D5 (canonical layout).
- APPLY now removes the old `ai/` folder so `.agents/` is the only AI folder.

## v2.1 — 2026-06-23 (starter pack instantiated for SMC-PSO-beta)
- Instantiated the `.agents/` starter pack for SMC-PSO-beta.
- Filled AGENTS.md, brain/STATE/NEXT/ROADMAP from the source `SMC-PSO` architecture.
- Seeded `graph/graph.json`; authored PLAYBOOK, PROMPTS, start/wrap-up prompts.
