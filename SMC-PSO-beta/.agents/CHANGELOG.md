# Brain Changelog

Track changes to the **brain itself** here (not project features). Newest on top.

## v2.3 -- 2026-06-23 (audit-driven migration plan)
- Added `brain/MIGRATION_PLAN.md`: port + AUDIT model. Two lenses on every module --
  (A) AI-slop/code defects, (B) scientific/mathematical correctness -- proven by (C) numeric
  parity + tests. Acceptance gate: P0 = 0, P1 = 0, parity pass, coverage met, Audit Card filed.
- Added `brain/templates/AUDIT_CARD.md` (per-module) and `brain/AUDIT_LEDGER.md` (findings log).
- ROADMAP/STATE rebuilt around 11 gated milestones; added the modules the old plan missed
  (interfaces/HIL, analysis, benchmarks; integration/assets decision).
- NEXT (M2 plant) now includes the Lens A/B/C audit + building the shared parity harness.
- Converted all brain status markers to ASCII ([DONE]/[WIP]/[TODO]); removed Unicode emojis
  that violated the project's own no-emoji rule. Added decisions D6, D7, D8.

## v2.2 -- 2026-06-23 (merged ai/ into .agents/)
- Merged `ai/AGENTS.md` + `ai/CLAUDE.md` into a single `.agents/AGENTS.md`. Stripped
  injected/auto-push directives. Folded `migration_plan.md` into ROADMAP + STATE.
- Reconciled graph to canonical `src/` layout. Re-pointed NEXT to plant. APPLY removes old `ai/`.

## v2.1 -- 2026-06-23 (starter pack instantiated for SMC-PSO-beta)
- Instantiated the `.agents/` starter pack; filled AGENTS/STATE/NEXT/ROADMAP; seeded the graph.
