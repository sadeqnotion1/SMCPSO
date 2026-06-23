# APPLY — install the `.agents/` brain into SMC-PSO-beta

This kit is **purely additive**: it only creates a new `.agents/` folder inside
`SMC-PSO-beta/`. It touches **no existing code**. Repo:
https://github.com/sadeqnotion1/smcpso

## What's in this ZIP
```text
APPLY.md            <- this file (do not copy into the repo)
.agents/            <- drop this whole folder into SMC-PSO-beta/
```

## Steps (literal)

1. **Back up first.** Run from your repo root (the `smcpso/` folder):
   - macOS/Linux:
     ```bash
     zip -r "../smcpso-backup-$(date +%Y%m%d-%H%M%S).zip" . -x "*.git/*" -x "*__pycache__/*" -x "*node_modules/*"
     ```
   - Windows PowerShell:
     ```powershell
     Compress-Archive -Path * -DestinationPath "..\smcpso-backup-$(Get-Date -Format yyyyMMdd-HHmmss).zip"
     ```

2. **Copy the folder.** Put the `.agents/` folder from this ZIP into `SMC-PSO-beta/`
   so you end up with `SMC-PSO-beta/.agents/`.
   - macOS/Linux: `cp -r .agents /path/to/smcpso/SMC-PSO-beta/`
   - Windows: drag the `.agents` folder into `SMC-PSO-beta\`.

3. **(Optional) Generate the visual graph:**
   ```bash
   cd /path/to/smcpso/SMC-PSO-beta
   python .agents/graph/render_graph.py
   # writes .agents/graph/graph.html — open it in any browser (offline, no deps)
   ```

4. **(Optional) Verify with the createproject installer**, if you have it locally:
   ```bash
   python init_agents.py --target /path/to/smcpso/SMC-PSO-beta --check
   ```

## Run / verify
- Open `SMC-PSO-beta/.agents/AGENTS.md` — it describes the DIP-SMC-PSO project and the boot sequence.
- `python .agents/graph/render_graph.py` prints `Wrote .../graph.html (17 nodes, 20 edges)` and creates `graph.html`.
- Nothing else in the repo changes.

## Quality gate (keep only if ALL pass — else delete the folder / restore backup)
- [ ] `SMC-PSO-beta/.agents/` exists with `AGENTS.md`, `brain/`, `graph/`, `skills/`, `prompts/`.
- [ ] No existing files were modified or deleted (additive only).
- [ ] `render_graph.py` runs with no errors and writes `graph.html`.
- [ ] `AGENTS.md` / `brain/STATE.md` / `brain/NEXT.md` describe the real project (not placeholders).
- [ ] Backup ZIP from step 1 exists.

## If something's wrong
The kit is additive — just delete `SMC-PSO-beta/.agents/` to fully revert (restore the
backup ZIP if you also want to undo anything else).

## Notes
- This is the **AI-brain** portion of the `createproject` starter pack only. The pack's
  `run.bat` / `run.sh` launchers and `launcher/ui_theme.py` are separate and not included here.
- The `skills/` index ships empty by design; author new skills from `skills/_template/SKILL.md`.
- Several files in the upstream `createproject` template carried obfuscated
  injected-instruction markers; those were ignored and these brain files were written clean.
