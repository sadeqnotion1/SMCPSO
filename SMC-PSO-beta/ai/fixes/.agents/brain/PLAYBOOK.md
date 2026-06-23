# PLAYBOOK — rules of engagement

> Repo: https://github.com/sadeqnotion1/smcpso (`SMC-PSO-beta/`)

## Roles
- **Maintainer (human, SadeQ):** product decisions, runs code locally, pastes
  logs/screenshots, final say.
- **AI (session lead):** disciplined senior engineer for the ONE task in `NEXT.md`.
  Minimal, additive, anchored edits. Backs up before destructive changes.
  No "while I'm here" scope creep.

## Session loop
1. Read `AGENTS.md` -> `STATE.md` -> `NEXT.md` -> current milestone in `ROADMAP.md`
   -> this file -> skim `DECISIONS.md`.
2. Query `graph/graph.json` only for what the task needs.
3. Report the **four-part status** and then either wait or proceed per below:
   a. **Where we are** (1-2 lines from STATE).
   b. **The one task** (from NEXT) + your file-level plan.
   c. **Decisions/inputs needed** (blockers).
   d. **Definition of done** (how we'll verify).
4. Do the task. Prefer new files over large rewrites; keep diffs small and anchored.
5. Wrap up (checklist below).

## Proceed-vs-wait rule
- If the task is unambiguous and DoD is clear, proceed after posting the four-part status.
- If a real decision in NEXT (c) blocks correctness, ask the minimum questions, then go.

## Migration discipline (this repo)
- Source of truth is `SMC-PSO/`. Port faithfully; don't redesign during a port.
- Keep numeric behavior identical unless a decision says otherwise (log it in DECISIONS).
- Don't carry over dead/garbage files from source (e.g. the mojibake `.bat`).
- Back up before deleting/overwriting; changes are minimal and additive.

## Feature-intake questions (when the maintainer says "build/port X")
1. **Goal** — what should work, in one sentence?
2. **Source** — which source file(s)/module(s) are we porting from?
3. **Data impact** — config keys, new fields, schema changes?
4. **Interface shape** — public functions/classes + signatures.
5. **Edge cases** — empty config, NaN guard, large batch sims.
6. **Acceptance** — the concrete check that proves it's done.
7. **Scope cut** — smallest version we can land first.
Ask only what you can't infer, then go.

## Wrap-up checklist (every session)
- [ ] Update `STATE.md` (statuses, risks).
- [ ] Rewrite `NEXT.md` to the next single task.
- [ ] Append a `SESSION_LOG.md` entry with the exact stop point.
- [ ] Append any new `DECISIONS.md` entries (append-only).
- [ ] Advance `ROADMAP.md` if a milestone changed.
- [ ] Update `graph/graph.json` and regenerate `graph.html` if structure changed.
