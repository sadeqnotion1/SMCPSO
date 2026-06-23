# `.agents/` — Project Brain (SMC-PSO-beta)

This folder is the **single source of truth** an AI session reads before doing any
work on `SMC-PSO-beta`. It exists so any new chat / new model can pick up the
migration with **zero context loss**. It is the **only** AI folder — the former `ai/`
(its `AGENTS.md`, `CLAUDE.md`, and `planning/`) has been merged in here.

> **Golden rule:** the AI operates strictly from these files and never improvises
> project state. If a brain file is missing or stale, the AI fixes the brain first.
>
> **One entry file:** `AGENTS.md` is the single, merged AI/terminal brief (former
> `ai/AGENTS.md` + `ai/CLAUDE.md`). There is no separate `CLAUDE.md`.

## File map

```text
.agents/
├── AGENTS.md            # Entry point: read FIRST. Merged AI/terminal brief + boot sequence
├── README.md            # This file
├── CHANGELOG.md         # Brain changelog (what changed in the brain itself)
├── brain/
│   ├── README.md        # What each brain file is for
│   ├── STATE.md         # Where the migration is right now (living document)
│   ├── NEXT.md          # The ONE next task + exactly what to hand the AI
│   ├── ROADMAP.md       # Migration milestones M0..M8 (dependency-first)
│   ├── PLAYBOOK.md      # Roles, session loop, git policy, output contract
│   ├── DECISIONS.md     # Append-only decision log (D1..D5)
│   ├── SESSION_LOG.md   # Append-only session history (what happened + stop point)
│   └── PROMPTS.md       # The two copy-paste prompts (START + WRAP-UP)
├── graph/
│   ├── graph.json       # Repo knowledge graph (canonical src/ layout; query, don't dump)
│   ├── render_graph.py  # graph.json -> self-contained offline graph.html
│   └── README.md        # Graph schema + how to query without dumping
├── skills/
│   ├── index.md         # Skill registry: name + when to use + path
│   └── _template/
│       └── SKILL.md     # Copy this to author a new skill
└── prompts/
    ├── start.md         # #START kickoff prompt
    └── wrap-up.md       # #WRAP_UP prompt (close a session with zero context loss)
```

## How a session works (short version)

1. AI reads `AGENTS.md` -> `brain/STATE.md` -> `brain/NEXT.md` -> current ROADMAP
   milestone -> `brain/PLAYBOOK.md` -> skims `brain/DECISIONS.md`.
2. AI queries `graph/graph.json` only for the nodes/edges it needs.
3. AI discovers `skills/` and loads a matching skill, or declares "none found".
4. AI reports a four-part status (a/b/c/d) and waits, unless PLAYBOOK says proceed.
5. On wrap-up, AI updates STATE / NEXT / SESSION_LOG / DECISIONS / ROADMAP and the graph.

## Maintenance contract

- Keep files **small and current**. STATE/NEXT are living docs; prune aggressively.
- `DECISIONS.md` and `SESSION_LOG.md` are append-only. Never rewrite history.
- Regenerate `graph.html` with `python .agents/graph/render_graph.py` after editing the graph.
- Edits to the brain are **minimal, additive, anchored**. Back up before destructive change.

_Version: brain v2.2 · SMC-PSO-beta · ai/ merged in._
