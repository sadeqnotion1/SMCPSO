# PROMPTS — the two copy-paste prompts that run the whole cycle

> These also live as standalone files in `.agents/prompts/start.md` and
> `.agents/prompts/wrap-up.md`. Keep them in sync.

---

## #START

```text
You are the session lead for SMC-PSO-beta. Read .agents/AGENTS.md, then the boot
sequence it lists (STATE -> NEXT -> current ROADMAP milestone -> PLAYBOOK -> skim
DECISIONS). Query .agents/graph/graph.json only for what the task needs — never dump it.

Then post a four-part status and STOP:
  a) Where we are (from STATE).
  b) The one task (from NEXT) + your file-level plan.
  c) Decisions/inputs you need from me.
  d) Definition of done.

If the task is unambiguous and DoD is clear, you may proceed after posting (a)-(d).
Keep edits minimal, additive, anchored. Back up before destructive changes.
```

---

## #WRAP_UP

```text
Wrap up this session for SMC-PSO-beta with zero context loss. Do all of:
  1. Update .agents/brain/STATE.md (statuses, risks).
  2. Rewrite .agents/brain/NEXT.md to the single next task.
  3. Append a .agents/brain/SESSION_LOG.md entry with today's date, what changed,
     the verified result, and the exact stop point.
  4. Append any new .agents/brain/DECISIONS.md entries (append-only).
  5. Advance .agents/brain/ROADMAP.md if a milestone changed.
  6. Update .agents/graph/graph.json and note to regenerate graph.html if structure changed.
Show me the diffs. Don't start new work.
```
