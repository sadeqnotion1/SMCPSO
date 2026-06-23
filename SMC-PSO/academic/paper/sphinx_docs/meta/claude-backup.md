# Automated Git Backup System

## Overview

The Claude Code Automated Backup System provides **frequent, automatic restore points** during coding sessions by committing and pushing repository changes at regular intervals (every 1 minute by default). This ensures work is never lost and provides granular rollback .
## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────┐
│  Windows Task Scheduler (every 1 minute)            │
│  ├─ Triggers: .dev_tools/claude-backup.ps1          │
│  └─ Runs as: Current User (non-elevated)            │
└─────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  PowerShell Script Workflow                         │
│  1. Verify repository location (D:\Projects\main)   │
│  2. Assert remote: github.com/theSadeQ/dip-smc-pso  │
│  3. Stage all changes (git add -A)                  │
│  4. Check if changes exist → Exit if none           │
│  5. Commit with timestamped message                 │
│  6. Push to origin/main                             │
│  7. Log result to .dev_tools/backup/backup.log      │
└─────────────────────────────────────────────────────┘
```

### Commit Message Format

Every automatic backup commit follows this template:

```
Auto-backup: 2025-10-01T14:23:15

- Staged working directory changes
- Periodic checkpoint from CI agent
- Includes files modified during this session

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Timestamp**: ISO 8601 format (YYYY-MM-DDTHH:mm:ss)

## Usage

### Manual Checkpoint

To force an immediate backup at any time:

```powershell
# Navigate to repository root
cd D:\Projects\main

# Run manual checkpoint
powershell -NoProfile -ExecutionPolicy Bypass -File .\.dev_tools\claude-backup.ps1 -Checkpoint
```

## Scheduled Automatic Backups

The Task Scheduler job `ClaudeCode-AutoBackup` runs **every 1 minute** automatically.

### Register Scheduled Task

```batch
rem Delete existing task (if any)
schtasks /Delete /TN "ClaudeCode-AutoBackup" /F 2>nul

rem Create new task (every 1 minute)
schtasks /Create ^
 /TN "ClaudeCode-AutoBackup" ^
 /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Projects\main\.dev_tools\claude-backup.ps1" ^
 /SC MINUTE ^
 /MO 1 ^
 /RL LIMITED ^
 /F ^
 /RU "%USERNAME%"
```

#### Run Task Immediately

```batch
schtasks /Run /TN "ClaudeCode-AutoBackup"
```

#### Check Task Status

```batch
schtasks /Query /TN "ClaudeCode-AutoBackup" /V /FO LIST
```

#### Unregister Task

```batch
schtasks /Delete /TN "ClaudeCode-AutoBackup" /F
```

### Optional: Run at Logon

To also trigger a backup when you log in:

```batch
schtasks /Create ^
 /TN "ClaudeCode-AutoBackup-OnLogon" ^
 /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Projects\main\.dev_tools\claude-backup.ps1" ^
 /SC ONLOGON ^
 /RL LIMITED ^
 /F ^
 /RU "%USERNAME%"
```

## Authentication

### Git Credential Helper

The backup script requires Git authentication to push to GitHub. Configure credentials using one of these methods:

#### Option 1: Git Credential Manager (Recommended)

```bash
# Windows default - usually already configured
git config --global credential.helper manager-core
```

## Option 2: Personal Access Token (PAT)

```bash
# Generate PAT at: https://github.com/settings/tokens
# Scopes required: repo (all)

# Store PAT using Git credential helper
git config --global credential.helper store
git push  # Enter PAT when prompted
```

## Verify Authentication

```bash
# Test push without changes
git push origin main --dry-run
```

## Behavior & Limitations

### What Gets Backed Up

- **All staged and unstaged changes** in the working directory
- **Untracked files** (new files not yet added to Git)
- **Respects `.gitignore`**: Excluded files are never committed

### What Doesn't Get Backed Up

- Files explicitly listed in `.gitignore`
- Files in `.git/` directory
- Temporary build artifacts (if properly ignored)

### Exit Conditions

| Condition | Exit Code | Behavior |
|-----------|-----------|----------|
| No changes detected | 0 | Silent exit, no commit created |
| Backup successful | 0 | Commit created, pushed to main |
| Repository not found | 1 | Error logged, no changes |
| Remote URL mismatch | 2 | Attempt to fix, retry |
| Git status check failed | 3 | Error logged |
| Commit/push failed | 4 | Error logged with hints |
| Unhandled exception | 99 | Error logged |

### Conflict Resolution

If the Task Scheduler runs while a manual checkpoint is in progress:

- **PowerShell locks ensure mutual exclusion** (only one instance runs at a time)
- If changes are detected but no diff exists (race condition), script exits cleanly
- If push fails due to remote changes, error is logged with actionable hint

## Advanced Features

### Token-Aware Backup

If the environment variable `CLAUDE_TOKENS_LEFT` is set and **< 2000**, the script triggers an emergency backup before exiting. This ensures critical work is saved when approaching token limits.

```powershell
# Example: Set token threshold
$env:CLAUDE_TOKENS_LEFT = 1500
.\claude-backup.ps1  # Will force backup
```

## Log File Inspection

All backup operations are logged to `.dev_tools/backup/backup.log`:

```powershell
# View recent backups
Get-Content .\.dev_tools\backup\backup.log -Tail 20

# Search for errors
Select-String -Path .\.dev_tools\backup\backup.log -Pattern "ERROR"
```

**Log Entry Format:**
```
[2025-10-01T14:23:15] [Info] === Claude Code Auto-Backup Script ===
[2025-10-01T14:23:15] [Info] Repository root: D:\Projects\main
[2025-10-01T14:23:16] [Info] Remote URL verified: https://github.com/theSadeQ/dip-smc-pso.git
[2025-10-01T14:23:16] [Info] Changes detected. Proceeding with backup...
[2025-10-01T14:23:17] [Success] Backup completed successfully!
```

## Troubleshooting

### Common Issues

#### "Authentication failed"

```powershell
# Solution: Configure Git credential helper
git config --global credential.helper manager-core
git push  # Authenticate when prompted
```

## "index.lock exists"

```bash
# Solution: Remove stale lock file
rm .git/index.lock
```

## "Not a git repository"

```powershell
# Solution: Verify you're in the correct directory
cd D:\Projects\main
git rev-parse --show-toplevel  # Should output repository root
```

## "Remote URL mismatch"

```bash
# Solution: Script auto-corrects, but you can verify manually
git remote -v
# Should show: origin  https://github.com/theSadeQ/dip-smc-pso.git
```

## Validation Test

To smoke-test the backup system:

```powershell
# 1. Make a temporary change
cd D:\Projects\main
echo "# Test" >> test_backup.txt

# 2. Run manual checkpoint
powershell -NoProfile -ExecutionPolicy Bypass -File .\.dev_tools\claude-backup.ps1 -Checkpoint

# 3. Verify commit was created
git log -1 --oneline
# Should show: "Auto-backup: <timestamp>"

# 4. Verify remote is synchronized
git ls-remote origin main
# Should show latest commit hash

# 5. Clean up
git rm test_backup.txt
git commit -m "Clean up test file"
git push origin main
```

## Performance Impact

- **Disk I/O**: Minimal (~10ms for status check)
- **Network**: Only on push (2-5 seconds typical)
- **CPU**: Negligible (<1% on modern systems)
- **Frequency**: Every 1 minute (configurable via Task Scheduler)

**Recommendation**: The 1-minute interval provides granularity without noticeable system impact.

## Security Considerations

- **Credentials**: Stored securely via Git Credential Manager
- **Execution Policy**: Bypass used only for this specific script
- **Permissions**: Runs as current user (no elevation required)
- **Network**: All traffic over HTTPS to GitHub

## Integration with CLAUDE.md

This backup system complies with the **Automatic Repository Management** policy in `CLAUDE.md`:

> **MANDATORY**: After ANY changes to the repository content, Claude MUST automatically stage, commit, and push to main branch.

The scheduled task ensures this policy is enforced even outside Claude Code sessions.

## Customization

### Change Backup Frequency

```batch
rem Example: Every 5 minutes instead of 1 minute
schtasks /Create ^
 /TN "ClaudeCode-AutoBackup" ^
 /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Projects\main\.dev_tools\claude-backup.ps1" ^
 /SC MINUTE ^
 /MO 5 ^
 /RL LIMITED ^
 /F ^
 /RU "%USERNAME%"
```

### Modify Commit Message Template

Edit `.dev_tools/claude-backup.ps1` and update the `$commitMessage` variable:

```powershell
# Line ~220
$commitMessage = @"
Auto-backup: $timestamp

- Custom message here
- Your changes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
"@
```

## Future Enhancements

Potential improvements for future versions:

- **Branch awareness**: Auto-detect current branch instead of hardcoded `main`
- **Conflict resolution**: Auto-merge or stash on pull conflicts
- **Retention policy**: Auto-squash old backup commits
- **Multi-repository**: Support backup across multiple projects
- **Web dashboard**: Real-time backup status monitoring



**Last Updated**: 2025-10-01
**Author**: Claude Code Team
**License**: MIT
