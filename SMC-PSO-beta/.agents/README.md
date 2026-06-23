# `.agents/` -- Project Brain (SMC-PSO-beta)

This folder is the **single source of truth** an AI session reads before doing any work on
`SMC-PSO-beta`. It exists so any new chat / new model can pick up the migration with **zero
context loss**. It is the **only** AI folder -- the former `ai/` has been merged in here.

> **Golden rule:** the AI operates strictly from these files and never improvises project
> state. If a brain file is missing or stale, the AI fixes the brain first.
>
> **Migration is audit-driven:** see `brain/MIGRATION_PLAN.md`. Every module is ported AND
> audited for AI-slop + scientific correctness, then proven by parity/tests before acceptance.

## File map

```text
.agents/
|-- AGENTS.md              # Entry point: read FIRST. Merged AI/terminal brief + boot sequence
|-- README.md              # This file
|-- CHANGELOG.md           # Brain changelog (what changed in the brain itself)
|-- brain/
|   |-- README.md          # What each brain file is for
|   |-- STATE.md           # Where the migration is right now (gated milestones)
|   |-- NEXT.md            # The ONE next task + exactly what to hand the AI
|   |-- ROADMAP.md         # Milestones M0..M11 (dependency-first, audit-gated)
|   |-- MIGRATION_PLAN.md  # Audit-driven plan: lenses A/B/C, severities, gate, harness
|   |-- AUDIT_LEDGER.md    # Append-only findings log (P0..P3)
|   |-- PLAYBOOK.md        # Roles, session loop, git policy, output contract
|   |-- DECISIONS.md       # Append-only decision log (D1..D8)
|   |-- SESSION_LOG.md     # Append-only session history (what happened + stop point)
|   |-- PROMPTS.md         # The two copy-paste prompts (START + WRAP-UP)
|   `-- templates/
|       `-- AUDIT_CARD.md  # Copy per module -> brain/audits/<module>.md
|-- graph/
|   |-- graph.json         # Repo knowledge graph (canonical src/ layout; query, don't dump)
|   |-- render_graph.py    # graph.json -> self-contained offline graph.html
|   `-- README.md          # Graph schema + how to query without dumping
|-- skills/
|   |-- index.md           # Skill registry: name + when to use + path
|   `-- _template/
|       `-- SKILL.md        # Copy this to author a new skill
`-- prompts/
    |-- start.md           # #START kickoff prompt
    `-- wrap-up.md         # #WRAP_UP prompt (close a session with zero context loss)
```

## How a session works (short version)

1. AI reads `AGENTS.md` -> `brain/STATE.md` -> `brain/NEXT.md` -> current ROADMAP milestone
   -> `brain/MIGRATION_PLAN.md` (the audit loop + gate) -> `brain/PLAYBOOK.md` -> skims DECISIONS.
2. AI queries `graph/graph.json` only for the nodes/edges it needs.
3. AI runs the module loop: port -> audit (A slop, B science) -> prove (C parity + tests) -> gate.
4. Findings go to `brain/AUDIT_LEDGER.md`; per-module Audit Card from `templates/AUDIT_CARD.md`.
5. On wrap-up, AI updates STATE / NEXT / SESSION_LOG / DECISIONS / ROADMAP and the graph.

## Maintenance contract
- Keep files small and current. STATE/NEXT are living docs; prune aggressively.
- `DECISIONS.md`, `SESSION_LOG.md`, `AUDIT_LEDGER.md` are append-only. Never rewrite history.
- Regenerate `graph.html` with `python .agents/graph/render_graph.py` after editing the graph.
- A module is `[DONE]` only after its Audit Card passes the gate in `MIGRATION_PLAN.md`.
- ASCII status markers only (no Unicode emojis) -- project hard rule.

_Version: brain v2.3 - SMC-PSO-beta - audit-driven migration._
