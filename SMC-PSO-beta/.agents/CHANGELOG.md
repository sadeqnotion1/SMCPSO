# Brain Changelog

Track changes to the **brain itself** here (not project features). Newest on top.

## v2.4 -- 2026-06-23 (skills registry populated)
- `skills/index.md`: added a curated **Recommended external skills** section matched from
  https://skills.sh, grouped by source GitHub repo (RigorPilot-Skills, obra/superpowers,
  mattpocock/skills) with relevance, links, and a map to the audit milestones/lenses.
- Added an "Excluded / unsure" list documenting surveyed-but-rejected skills + reasons.
- Added "Top picks" shortlist (verification-before-completion, minimal-run-and-audit,
  ai-research-reproduction + paper-context-resolver, TDD).

## v2.3 -- 2026-06-23 (audit-driven migration plan)
- Added `brain/MIGRATION_PLAN.md`: port + AUDIT model. Two lenses on every module --
  (A) AI-slop/code defects, (B) scientific/mathematical correctness -- proven by (C) numeric
  parity + tests. Acceptance gate: P0 = 0, P1 = 0, parity pass, coverage met, Audit Card filed.
- Added `brain/templates/AUDIT_CARD.md` (per-module) and `brain/AUDIT_LEDGER.md` (findings log).
- ROADMAP/STATE rebuilt around 11 gated milestones; added the modules the old plan missed
  (interfaces/HIL, analysis, benchmarks; integration/assets decision). Plant: full model first (D9).
- Reference math sourced from repo `references/` (proofs + bib) but audited for authenticity (D10/W1).
- Converted all brain status markers to ASCII; removed Unicode emojis. Added decisions D6-D10.

## v2.2 -- 2026-06-23 (merged ai/ into .agents/)
- Merged `ai/AGENTS.md` + `ai/CLAUDE.md` into a single `.agents/AGENTS.md`. Stripped
  injected/auto-push directives. Folded `migration_plan.md` into ROADMAP + STATE.
- Reconciled graph to canonical `src/` layout. Re-pointed NEXT to plant. APPLY removes old `ai/`.

## v2.1 -- 2026-06-23 (starter pack instantiated for SMC-PSO-beta)
- Instantiated the `.agents/` starter pack; filled AGENTS/STATE/NEXT/ROADMAP; seeded the graph.
