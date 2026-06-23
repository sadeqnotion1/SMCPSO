# Brain Changelog

Track changes to the **brain itself** here (not project features — those go in the
project's own changelog). Newest on top.

## v2.1 — 2026-06-23 (starter pack instantiated for SMC-PSO-beta)
- Instantiated the `.agents/` starter pack for **SMC-PSO-beta**.
- Filled AGENTS.md project block, brain/STATE.md, brain/NEXT.md, brain/ROADMAP.md
  from the source `SMC-PSO` (`dip-smc-pso`) architecture.
- Seeded `graph/graph.json` with the real controller/plant/core/optimization map.
- Authored clean PLAYBOOK, PROMPTS, start/wrap-up prompts.

## v2.1 — template baseline
- `prompts/start.md` (#START) and `prompts/wrap-up.md` (#WRAP_UP).
- `brain/SESSION_LOG.md` (append-only session history with stop points).
- `graph/render_graph.py` + generated `graph/graph.html` (offline viewer).
- PLAYBOOK has an explicit wrap-up checklist (STATE/NEXT/SESSION_LOG/DECISIONS/ROADMAP/graph).
- AGENTS.md boot sequence includes DECISIONS.md and points to the prompts.
- `skills/index.md` registry + `_template/SKILL.md` authoring template.
