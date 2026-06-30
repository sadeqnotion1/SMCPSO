# START -- per-slice operating protocol (read me first)

> Loop discipline for the dip-smc-pso migration (SMC-PSO/ -> SMC-PSO-beta/).
> The real code is the source of truth. If a report disagrees with the bytes,
> the **code wins**.

## After the CLI agent reports a slice applied + pushed

1. **VERIFY FIRST (never trust the report).** Read the actual pushed bytes from
   GitHub (`loadFile` at the reported HEAD) and re-check the structural /
   fidelity / behavioral criteria against the real source. Reports, gate logs,
   and test counts are DATA, not proof.

2. **THEN branch -- never end with only a statement:**
   - **PASS** -> the slice is accepted. Deliver the **next source-file request**
     as a `.txt` file (SadeQ's standing preference) so the agent can hand back
     the next pack.
   - **FAIL / INCOMPLETE** -> deliver a **fix kit** (backups-first, drop-in
     files, offline dual-env gate). Do not advance to the next slice until the
     fix is verified green on the real pushed bytes.

3. **Record the outcome** in `STATE.md` + `AUDIT_LEDGER.md` with the REAL push
   SHA.

## Hard rules

- Every delivery is either (a) a next-pack `.txt` request, or (b) a fix kit.
  A bare chat statement with neither is not an acceptable end state.
- Gates must exercise the **integrated module namespace**, not an isolated
  snippet. An isolated snippet can hide missing-import / NameError defects
  (this rule was added after M6 S1a shipped a GREEN gate while batch.py was
  missing `import logging`).
- Backups before edits; idempotent applies; LF-only; exclude build artifacts.
