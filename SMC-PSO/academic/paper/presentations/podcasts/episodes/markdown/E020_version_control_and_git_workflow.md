# E020: Version Control and Git Workflow

**Part:** Part 4 Professional
**Duration:** 30-35 minutes
**Hosts:** Dr. Sarah Chen (Control Systems) & Alex Rivera (Software Engineering)

---

## Opening Hook: Git as a Time Machine

**Sarah:** Last episode we talked about workspace organization - the structure that keeps 985 files navigable over months of development. But structure without persistence is worthless.

**Alex:** You can organize your workspace perfectly. Give every directory a logical purpose, enforce cleanup policies, document every convention. But when the session ends at token limit - when the AI assistant runs out of context and everything stops - what survives?

**Sarah:** **Git commits.** With 10 out of 10 reliability.

**Alex:** Think of Git as a **time machine** for your project. Every commit is a snapshot—a save point you can travel back to. Made a mistake? Travel back to yesterday. Need to see what the code looked like in October? Travel back to October.

**Sarah:** Most research projects use Git as a backup system—clone, edit, commit when you remember, maybe push once a week. This project uses Git as the **persistence layer** for the entire recovery infrastructure.

**Alex:** Without proper Git workflow, the 30-second recovery we described in Episode 19 is impossible. Today we explain how Git enables that recovery—and why treating Git as mere version control is leaving 90% of its value on the table.

---

## What You'll Discover

- The commit message format that doubles as a task completion log
- Why every commit includes a task ID that triggers automated state tracking
- The main branch deployment strategy - no feature branches, continuous integration
- Pre-commit hooks that enforce documentation quality and workspace hygiene before any commit reaches the repository
- The three-tier persistence model: in-memory state (0 out of 10 reliability), checkpoint files (9 out of 10), Git commits (10 out of 10)
- How Git log analysis enables multi-account recovery by reconstructing project state from commit history
- Protected file workflows - why some files must never be moved or deleted
- The git mv command for history-preserving migrations
- Why heredoc syntax in commit messages prevents escaping issues
- The automated tracking system that updates project state based on commit messages - zero manual intervention required
- How pre-commit hooks catch workspace organization violations before they reach the repository
- The Co-Authored-By convention for AI collaboration attribution

---

## Commit Messages as Task Logs

**Sarah:** Let us start with commit messages. Most developers treat them as brief notes - "fix bug" or "update docs." This project treats them as structured task completion logs.

**Alex:** The format has three parts. First: the action line. This follows a modified conventional commits pattern - type, optional scope, colon, brief description. For example: "feat(MT-6): Complete boundary layer optimization."

**Sarah:** The type tells you what kind of work this is. feat for new features, fix for bug repairs, docs for documentation, refactor for code restructuring, test for test additions.

**Alex:** The scope - the part in parentheses - contains the task identifier. MT-6 means "medium-term task number 6" from the research roadmap. LT-7 means "long-term task 7." QW-3 means "quick win task 3." This identifier is critical because the pre-commit hook parses it automatically.

**Sarah:** What does the hook do with it?

**Alex:** It triggers the project state manager. When you commit with a task ID in the message, the hook extracts that ID, checks it against the roadmap tracker, and updates the project state file to mark that task as complete. Zero manual intervention. You never have to edit a tracking document by hand.

**Sarah:** Second part of the message?

**Alex:** Details. A bulleted list of what the commit actually changed. Not "added tests" - be specific. "Added 47 tests covering chattering detection edge cases. Fixed boundary condition bug in saturation control. Updated documentation with examples." The next person reading this commit - which might be you in three months - needs to understand the scope without reading the diff.

**Sarah:** Third part?

**Alex:** Footer. Two lines. First: "[AI] Generated with Claude Code" with a link. This attributes the work to AI-assisted development. Second: "Co-Authored-By: Claude <noreply@anthropic.com>". This is a GitHub-recognized convention that marks the commit as collaborative work between human and AI.

**Sarah:** Why does attribution matter in a research context?

**Alex:** Transparency. When someone clones this repository and reads the commit history, they can immediately see which work was AI-assisted. That matters for reproducibility. It also matters ethically - AI collaboration should be visible, not hidden.

**Alex:** The entire message is wrapped in a heredoc. That is a shell scripting pattern for multi-line strings. You write "git commit -m" followed by "dollar sign open paren cat space less-than less-than single-quote EOF single-quote" then your multi-line message, then "EOF" on its own line, then close paren."

**Sarah:** Why heredoc instead of just multiple -m flags?

**Alex:** Escaping. If your commit message contains quotes, apostrophes, or special characters, heredoc handles them automatically. You never have to backslash-escape anything. The message is treated as literal text from the opening EOF to the closing EOF.

**Sarah:** Show me a real example.

**Alex:** Here is one from the research phase.

```bash
git commit -m "$(cat <<'EOF'
feat(MT-6): Complete boundary layer optimization for Hybrid Adaptive STA-SMC

- Implemented epsilon tuning algorithm with 0.001 to 0.1 search range
- Ran 100 Monte Carlo simulations per epsilon value (10 values tested)
- Found optimal epsilon: 0.007 (lowest chattering, stable control)
- Updated controller configuration with optimized boundary layer
- Documented results in academic/experiments/hybrid_adaptive_sta/MT-6_results.md

[AI] Generated with Claude Code (https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Sarah:** The pre-commit hook sees "MT-6" in that message, queries the roadmap tracker, and marks medium-term task 6 as complete?

**Alex:** Exactly. The hook runs a Python script - project_state_manager.py - that parses the commit message, extracts "MT-6", looks it up in the research roadmap, and updates the state JSON file. All automatic. All reliable.

**Sarah:** What about commits that span multiple tasks?

**Alex:** The hook handles that. If your commit message mentions multiple task IDs - say, "feat(MT-5, MT-6): Complete comprehensive benchmarks and boundary layer optimization" - the hook extracts both IDs and updates state for both tasks. The regex pattern matches any occurrence of the task ID format: two or three letters followed by a dash and a number.

**Sarah:** Are there conventions for commit message length?

**Alex:** The action line should be under 72 characters to display properly in Git tools. The details section has no limit - be as specific as needed. The footer is always two lines, fixed format. Most commits in this project have action lines around 50 to 60 characters and details sections of 5 to 10 lines.

**Sarah:** What if you need to reference a specific file or module in the commit message?

**Alex:** Use relative paths from project root. For example: "Updated src/controllers/classical_smc.py with gain bounds validation." This makes the commit message searchable. You can run "git log --all --grep='classical_smc.py'" to find all commits that touched that file, even if the mention is only in the message text rather than the actual diff.

**Sarah:** The commit history becomes a searchable knowledge base.

**Alex:** Exactly. Structured, parseable, machine-readable. But also human-readable when you need to understand what changed and why.

---

## Main Branch Deployment Strategy

**Sarah:** This project uses a main-branch-only workflow. No feature branches, no pull requests, no code review gates. Why?

**Alex:** Context. This is a solo research project, not a production system with a team of developers. The overhead of creating feature branches, opening pull requests, and reviewing your own code provides zero value when you are the only contributor and the goal is rapid iteration on algorithms.

**Sarah:** But feature branches provide isolation. You can experiment without breaking the main branch.

**Alex:** True for production. Not valuable for research. In a research setting, experiments are the main branch. The goal is to test hypotheses, evaluate controllers, run benchmarks, and document results. Every commit should represent a meaningful step forward, not a work-in-progress placeholder.

**Alex:** The trade-off is discipline. Without feature branches, you cannot push broken code to main and assume nobody will notice. Every commit must pass tests. Every commit must leave the system in a working state. The pre-commit hooks enforce this - they run validation checks before allowing the commit.

**Sarah:** What about rollback? If a commit introduces a regression, do you revert?

**Alex:** Git revert is available but rarely needed. The test suite is comprehensive - 4,563 tests with 100 percent pass rate. If a commit breaks something, the tests catch it before you push. And because every commit is **atomic**—one task, one logical change—reverting is straightforward if necessary.

**Sarah:** Think of atomic commits like **saving your game before a boss fight**. You're about to do something risky—implement a new feature, refactor a complex module. Before you start, you commit your current state. Save the game.

**Alex:** If the boss fight goes badly—the feature breaks, the refactor fails—you can reload from your save. One `git reset --hard HEAD`, and you're back to safety.

**Sarah:** Atomic means **complete**. You don't commit half-finished work. You don't mix two unrelated changes in one commit. One commit = one logical change = one save point you can trust.

**Sarah:** Repository verification. The automation scripts need to confirm they are pushing to the correct remote. How does that work?

**Alex:** The repository management guide specifies a mandatory check before every push: "git remote get-url origin" must return "https://github.com/theSadeQ/dip-smc-pso.git". If it returns anything else - a fork, a different repository, a local path - the automation stops.

**Sarah:** Why is this critical?

**Alex:** Because the AI assistant can be invoked in any directory. If you accidentally run the automation script in a different project, you do not want it pushing commits to the wrong repository. The URL check is a safety guard.

---

## Pre-Commit Hooks and Automation

**Sarah:** Pre-commit hooks are programs that run automatically before Git allows a commit to proceed. This project uses them heavily. What do they check?

**Alex:** Four primary checks. First: documentation quality. The hook runs a Python script called detect_ai_patterns.py that scans any modified markdown files for AI-generated writing patterns - things like "comprehensive," "delve into," "it is important to note." If it finds more than five such patterns in a single file, it warns you.

**Sarah:** It does not block the commit?

**Alex:** Correct. It is a warning, not a blocker. The goal is awareness, not gatekeeping. The script outputs something like "[WARNING] Found 7 AI-ish patterns in docs/guide.md - consider revision" but allows the commit to proceed.

**Sarah:** Second check?

**Alex:** Root item count. The hook runs a directory listing of the project root and counts visible items. If it exceeds 19 - the workspace hygiene limit from Episode 19 - it blocks the commit and tells you to clean up first.

**Sarah:** So you cannot accidentally commit a cluttered workspace state.

**Alex:** Exactly. The hook enforces the organizational policy automatically. You might forget to clean up manually. The hook never forgets.

**Alex:** Third check: task ID extraction. We covered this earlier - the hook parses the commit message for task identifiers like MT-6 or LT-7 and updates the project state manager. This is not a check that blocks anything. It is an automation that runs silently in the background.

**Sarah:** Fourth check?

**Alex:** Test execution. If the hook detects changes to source files in src/, it optionally runs a subset of tests - the fast unit tests - to verify nothing broke. This is disabled by default because it slows down commits, but you can enable it by setting an environment variable.

**Sarah:** The hooks are platform-specific. Windows versus Linux.

**Alex:** Dual implementation. The hook file in .git/hooks/pre-commit is a Bash script on Linux and macOS. On Windows, it is a PowerShell script. Both implementations provide the same checks, adapted to platform-specific commands. For example, the Bash version uses "wc -l" to count root items. The PowerShell version uses "Get-ChildItem | Measure-Object."

**Sarah:** Can you bypass the hooks in an emergency?

**Alex:** Yes. "git commit --no-verify" skips all hooks. This is documented in the repository management guide as an emergency-only procedure. You use it when the hooks are malfunctioning or when you need to commit a known-broken state temporarily for recovery purposes.

**Sarah:** Example scenario?

**Alex:** You are mid-refactoring. The code does not compile, tests are failing, but you are about to hit the token limit and need to save progress immediately. You commit with --no-verify to bypass the test check, push to remote, and resume in the next session from that checkpoint. Then you fix the breakage and commit again normally.

**Alex:** The hooks are not installed by default when you clone the repository. You activate them by running a script: ".ai_workspace/tools/automation/install_hooks.sh" on Linux, or "install_hooks.ps1" on Windows. This gives users control - if you want manual commits without automation, you can skip installation.

**Sarah:** What happens if the hook script itself has a bug?

**Alex:** The hook is wrapped in error handling. If the Python scripts fail - say, detect_ai_patterns.py crashes due to malformed markdown - the hook catches the error, logs it to ".ai_workspace/logs/pre-commit-errors.log", and allows the commit to proceed with a warning. The philosophy is: never block legitimate work due to infrastructure failures.

**Sarah:** So the hooks are fail-safe, not fail-hard.

**Alex:** Correct. The only hard blocker is the root item count check, and that one is simple enough - just counting files - that it rarely fails. Everything else is soft warnings or silent automation.

**Alex:** The hooks also respect a bypass file. If ".ai_workspace/state/hook_bypass" exists, all checks are skipped. This is useful during bulk operations like repository reorganization where you might be committing intermediate states that would normally trigger warnings.

**Sarah:** How do you create the bypass file?

**Alex:** "touch .ai_workspace/state/hook_bypass" on Linux, or "New-Item .ai_workspace/state/hook_bypass" on Windows. The file can be empty. Its presence is the signal. Delete it when you are done with the bulk operation, and the hooks resume normal operation.

**Sarah:** The hook installation script - what does it actually do?

**Alex:** It copies the appropriate hook file to ".git/hooks/pre-commit" and makes it executable. On Linux, that is "chmod +x .git/hooks/pre-commit". On Windows, the PowerShell script does not need execute permissions - it is invoked by Git automatically. The installation script also verifies that Python is available and that the required scripts - detect_ai_patterns.py, project_state_manager.py - exist and are executable.

---

## Git as Recovery Persistence Layer

**Sarah:** Let us talk about reliability. In Episode 19, we mentioned Git commits survive token limits with 10 out of 10 reliability. What does that mean?

**Alex:** Token limit is the maximum amount of text an AI session can process. When you reach it, the session terminates immediately. All in-memory state - variables, objects, execution context - is lost. Zero out of 10 reliability. Nothing survives.

**Sarah:** Checkpoint files?

**Alex:** Nine out of 10 reliability. Checkpoint files are written to disk periodically - every 5 to 10 minutes during agent execution. If the session terminates gracefully - say, you manually end it - the last checkpoint is complete and contains all progress. But if the session crashes mid-write - the token limit hits while the checkpoint file is being written - the file can be incomplete. Corrupted JSON, truncated data. Nine out of 10 means it usually works but occasionally fails.

**Sarah:** Git commits are different.

**Alex:** Git commits are atomic. When you run "git commit," Git either completes the entire commit transaction - updates the object database, updates the ref, updates the index - or it fails completely and rolls back. There is no partial state. Either the commit exists and is valid, or it does not exist. Once "git commit" returns successfully, that commit is permanent. It survives process crashes, system reboots, disk failures if you have backups. Ten out of 10 reliability.

**Sarah:** So the three-tier persistence model is: in-memory state, checkpoint files, Git commits, with increasing reliability?

**Alex:** Exactly. Think of it as a pyramid. The base is Git commits - slow to write, high overhead, but indestructible. The middle is checkpoint files - faster, moderate overhead, very reliable. The top is in-memory state - instant, zero overhead, completely ephemeral.

**Sarah:** Why not skip checkpoints and commit everything directly to Git?

**Alex:** Commit granularity. A checkpoint might be written every 10 minutes during a 2-hour task. That is 12 checkpoints. If you committed every checkpoint, you would pollute the Git history with 12 intermediate commits that provide no value to someone reading the history later. The checkpoint files are temporary persistence. Once the task completes, you write one atomic Git commit that captures the entire task, and the checkpoint files are no longer needed.

**Alex:** The checkpoint files also enable recovery within a session. If an agent crashes but the overall session continues, the orchestrator can read the last checkpoint and restart the agent from that point without involving Git at all. Git is the cross-session persistence. Checkpoints are the within-session persistence.

**Sarah:** How does Git log analysis work for recovery?

**Alex:** The recovery script runs a series of Git commands to reconstruct project state. First: "git pull origin main" to fetch all commits since the last session. Second: "git log --grep='MT-' --grep='LT-' --grep='QW-' --oneline" to find all commits that mention task identifiers. Third: parse the commit messages to extract task IDs and completion dates.

**Sarah:** So the commit history becomes a task completion audit trail.

**Alex:** Yes. If the project state file is lost or corrupted, you can regenerate it entirely from Git history. The recovery script reads through all commits, extracts task IDs, checks them against the roadmap, and rebuilds the state JSON file. The Git log is the source of truth.

**Alex:** This is why commit message structure matters. If commits just said "fixed stuff" or "updates," the recovery script could not parse them. The structured format - with task IDs in a predictable location - makes automated parsing possible.

**Sarah:** Let us compare the three tiers explicitly with an example scenario.

**Alex:** Scenario: you are running a 2-hour PSO optimization task. In-memory state includes the current particle positions, velocities, fitness values, iteration count. This state is updated thousands of times per second as the algorithm runs. Zero persistence - it lives only in RAM.

**Sarah:** Checkpoint files?

**Alex:** Every 10 minutes, the agent writes a checkpoint: current iteration, best solution found so far, computational time elapsed. These are JSON files, a few kilobytes each, written to ".ai_workspace/tools/checkpoints/". If the session crashes at minute 47, you have checkpoints from minutes 10, 20, 30, 40. You lost at most 7 minutes of work.

**Sarah:** And the Git commit?

**Alex:** At the end of the full 2-hour task, when PSO completes and you have validated the optimized controller gains, you write one commit: "feat(MT-8): Robust PSO optimization with 15 disturbance scenarios". That commit includes the final optimized gains file, updated configuration, and documentation of results. The 12 intermediate checkpoints are now redundant - you can delete them. But the commit is permanent.

**Alex:** If you need to resume PSO mid-execution, you use the checkpoint. If you need to resume the entire project after weeks or months, you use Git. Different persistence mechanisms for different time scales.

**Sarah:** What about uncommitted changes? Files you edited but did not commit before the session ended?

**Alex:** Git tracks them in the working directory. When you pull in the next session, Git reports "You have uncommitted changes in the following files..." and lists them. You can review with "git diff", decide whether to keep, discard, or commit. The working directory state survives as long as you do not force-reset or hard-clean.

**Sarah:** But that requires the same machine, same clone?

**Alex:** Correct. Uncommitted changes do not transfer across clones. That is why the policy is: commit frequently. Do not leave significant work uncommitted when you end a session. If you absolutely must end a session with uncommitted work - emergency situation - you can commit with --no-verify and a message explaining the state is intermediate.

---

## Multi-Account Recovery Integration

**Sarah:** In Episode 19, we mentioned the 30-second recovery workflow for resuming work across different Claude accounts or after long gaps. Walk through how Git enables that.

**Alex:** Five steps. Step one: pull latest commits from remote. This ensures you have every piece of work that was committed before the session ended, even if it was from a different account or weeks ago.

**Sarah:** You run "git pull origin main"?

**Alex:** Exactly. The recovery script runs it automatically. You do not even have to type it manually. The script is ".ai_workspace/tools/recovery/recover_project.sh" on Linux or ".bat" on Windows. Run it once, and it handles all five steps.

**Sarah:** Step two?

**Alex:** Load project state from ".ai_workspace/state/project_state.json". This file tracks current phase, roadmap progress, and active task list. It is updated automatically by the pre-commit hook whenever you commit with a task ID. The recovery script reads it to determine where you left off.

**Sarah:** Step three?

**Alex:** Analyze agent checkpoints. The script scans ".ai_workspace/tools/checkpoints/" for any checkpoint files that are newer than the last commit. If it finds one, that means a multi-agent task was interrupted before it could be committed. The script reports which agents were running and how much progress they made.

**Sarah:** So you can resume the interrupted agent work?

**Alex:** Yes. The checkpoint file contains the agent's state - task ID, agent ID, hours completed, deliverables produced so far. You can manually review that output and decide whether to restart the agent from scratch or resume from the checkpoint.

**Sarah:** Step four?

**Alex:** Review the roadmap tracker. The script runs "python .ai_workspace/tools/analysis/roadmap_tracker.py" which parses the 72-hour research roadmap and identifies remaining tasks. It cross-references completed tasks from the project state file and outputs a summary: "11 out of 11 tasks complete, Phase 5 finished."

**Sarah:** Step five?

**Alex:** Resume from last known good state. At this point, you have pulled all commits, loaded project state, analyzed checkpoints, and reviewed the roadmap. The recovery script outputs a summary: "You are currently in Phase 5 Maintenance. Last commit: feat(LT-7): Research paper submission-ready v2.1. No incomplete agent work detected. All 11 research tasks complete. You may proceed with maintenance tasks or new development."

**Alex:** That entire workflow - all five steps - takes 30 seconds. Most of that time is Git pull over the network. The state analysis is nearly instant.

**Sarah:** And this works even if you switch Claude accounts?

**Alex:** Yes. Because everything is persisted in Git commits and checkpoint files, the recovery does not depend on in-memory state from the previous session. A completely fresh session, different account, different machine - as long as you clone the repository and run the recovery script, you get full context within 30 seconds.

**Sarah:** The validation for this workflow?

**Alex:** Eleven tests covering the recovery sequence. All passing at 100 percent. The tests verify that recovery produces identical state to what existed before the interruption. You can see them in "tests/test_integration/test_recovery_workflow/" - they cover checkpoint file parsing, state reconstruction from Git log, roadmap task matching, and end-to-end recovery simulation.

**Sarah:** What if the remote repository is unavailable? Network down, GitHub outage?

**Alex:** The recovery script degrades gracefully. Step one - git pull - fails with a network error. The script catches it, logs a warning, and proceeds with steps two through four using only local state. You get a partial recovery: project state from the last session on this machine, checkpoint analysis, roadmap review. But you do not get commits from other machines or accounts until the network returns.

**Sarah:** So local recovery still works, just not cross-machine recovery?

**Alex:** Exactly. The 30-second recovery assumes network connectivity. Without it, you still get 60-second recovery using local state only. The design prioritizes degraded functionality over complete failure.

**Alex:** The recovery script also validates Git history integrity. It runs "git fsck" - the Git file system check command - to verify the repository is not corrupted. If fsck reports errors, the script alerts you and recommends running repair commands before trusting the recovered state.

**Sarah:** Has corruption ever occurred in practice?

**Alex:** Never in this project across hundreds of commits over months. Git is extremely robust. But the fsck check is defensive programming - verify the foundation before building on it.

---

## Protected Files and Migration Workflows

**Sarah:** Some files must never be moved or deleted. What are they, and why?

**Alex:** The primary one is external to the repository: "D:\Tools\Claude\Switch-ClaudeAccount.ps1". This is a PowerShell script for multi-account switching - it automates the process of changing between different Claude Code accounts. It lives outside the project directory because it applies to all projects, not just this one.

**Sarah:** Why does it need protection?

**Alex:** Because the AI assistant sometimes proposes cleanup tasks that would accidentally delete or move external tools. The workspace organization guide explicitly lists this file as protected with a comment: "NEVER DELETE - Multi-account switcher (EXTERNAL LOCATION)." That warning prevents accidental removal.

**Sarah:** What about migrations within the repository?

**Alex:** Use "git mv" instead of manual move followed by "git add". The difference is history preservation. When you run "git mv src/old_name.py src/new_name.py", Git records the move as a rename operation. The file's history - all commits that modified it - stays attached to the new filename. You can run "git log --follow src/new_name.py" and see commits from before the rename.

**Sarah:** What happens with manual move?

**Alex:** If you manually move the file using "mv" or Windows File Explorer, then "git add" the new location and "git rm" the old location, Git treats this as a delete and a create. The old file's history is now under the old name. The new file starts with zero history. You have broken the connection.

**Sarah:** Give me a real example from this project.

**Alex:** The December 2025 reorganization. The benchmarks directory was restructured - "benchmarks/raw/" for immutable original outputs, "benchmarks/processed/" for derived datasets, "src/benchmarks/" for analysis modules. Every file move in that reorganization used "git mv" to preserve history. You can verify this by running "git log --follow src/benchmarks/analysis.py" - it shows commits from when the file was at "benchmarks/analysis.py" before the move.

**Alex:** The migration workflow is: backup first, then migrate with git mv, then verify with git log --follow, then commit. If something goes wrong, you have a backup and you can restore. But git mv is so reliable that failures are rare.

**Sarah:** Does git mv work for directories?

**Alex:** Yes. "git mv old_directory/ new_directory/" moves the entire directory and preserves history for all files inside. The December reorganization moved entire directory trees - ".project/" became ".ai_workspace/" - using git mv at the directory level.

---

## Automated Tracking System

**Sarah:** We have mentioned the automated tracking several times. Let us make it explicit. What updates automatically, and how?

**Alex:** Zero manual updates. Every piece of project state tracking happens through Git hooks and commit message parsing. The developer writes a commit message with a task ID. The pre-commit hook extracts the ID. The hook runs project_state_manager.py with the task ID as an argument. The Python script updates the state JSON file to mark that task complete.

**Sarah:** So the workflow is: developer completes work, commits with task ID, hook auto-updates tracking?

**Alex:** Exactly. No separate step to edit a tracking document. No risk of forgetting to update status. The act of committing is the act of updating status.

**Sarah:** What if the commit message does not contain a task ID?

**Alex:** The hook still runs but does nothing. Commits without task IDs are valid - they just do not trigger state updates. This is common for maintenance commits, documentation fixes, or small refactorings that are not tied to a specific roadmap task.

**Alex:** The project state file contains four fields: current phase, completed tasks (a list of task IDs), active tasks (a list of IDs currently in progress), and last update timestamp. When the hook detects a task ID in a commit, it adds that ID to the completed tasks list, removes it from the active tasks list if present, and updates the timestamp.

**Sarah:** The roadmap tracker is separate?

**Alex:** Yes. The roadmap tracker parses the research roadmap document - a markdown file with 50 tasks across multiple phases - and generates a summary of progress. It does not update the roadmap itself. It reads the project state file to see which tasks are complete, cross-references that against the roadmap, and outputs a report.

**Alex:** You run it manually: "python .ai_workspace/tools/analysis/roadmap_tracker.py". The output shows: "Phase 5 Research: 11 out of 11 tasks complete. QW-1 through QW-5 finished. MT-5 through MT-8 finished. LT-4, LT-6, LT-7 finished." It is a read-only analysis tool.

**Sarah:** The reliability test you mentioned - 11 out of 11 tests at 100 percent. What do those tests verify?

**Alex:** The test suite in "tests/test_integration/test_automated_tracking/" covers six scenarios. First: commit with valid task ID updates state correctly. Second: commit without task ID leaves state unchanged. Third: commit with invalid task ID (does not exist in roadmap) triggers a warning but does not corrupt state. Fourth: commit with multiple task IDs updates all of them. Fifth: state file corruption is detected and reported. Sixth: recovery from corrupted state by regenerating from Git log.

**Alex:** The tests use a mock Git repository - a temporary directory with a fake commit history - to verify behavior without touching the real project repository. Each test runs the pre-commit hook script, checks the resulting state file, and asserts correctness.

---

## Key Takeaways

**Sarah:** Eight core lessons about Git workflow as research infrastructure.

**Alex:** First: Git is the persistence layer, not just version control. It is the mechanism that makes 30-second recovery possible. Without atomic commits that survive token limits, the entire recovery infrastructure would not work.

**Sarah:** Second: commit messages are task completion logs. Structured format with task IDs enables automated tracking. The act of committing is the act of updating project status.

**Alex:** Third: pre-commit hooks automate quality enforcement. Documentation patterns, workspace hygiene, task ID extraction - all happen automatically before the commit reaches the repository. No manual checks required.

**Sarah:** Fourth: 10 out of 10 reliability for Git commits versus 9 out of 10 for checkpoints versus 0 out of 10 for in-memory state. The three-tier persistence model provides redundancy at multiple time scales.

**Alex:** Fifth: main branch strategy fits research workflow. No feature branches, no pull requests, continuous integration. Every commit is a meaningful step forward. This does not work for production teams but it works perfectly for solo research.

**Sarah:** Sixth: git mv preserves history. Always use git mv for file and directory migrations. Manual move breaks the history connection. Verification with git log --follow confirms history is intact.

**Alex:** Seventh: protected files prevent accidental deletion. External tools like the account switcher script must be explicitly documented as protected. The AI assistant reads that documentation and avoids proposing harmful cleanup.

**Sarah:** Eighth: automated tracking eliminates manual updates. Zero editing of tracking documents by hand. Commit with task ID, hook updates state, roadmap tracker generates reports. The system maintains itself.

**Alex:** The workflow is invisible to users reading the research paper. But it is the foundation that allowed this project to survive months of development, token limits, account switches, and multi-month gaps without losing context.

---

## Pronunciation Guide

For listeners unfamiliar with technical terms used in this episode:

- **Heredoc**: short for "here document." A multi-line string input method in shell scripting. Pronounced "HERE-dock."
- **Pre-commit hook**: a script that runs before Git allows a commit. Say "pre" like the prefix, "commit" as usual, "hook" as in fishing hook.
- **Idempotent**: producing the same result no matter how many times you run it. Pronounced "eye-DEM-po-tent."
- **Atomic**: all-or-nothing operation that cannot be partially completed. Pronounced "uh-TOM-ick."
- **Token limit**: the maximum text an AI session can process. "Token" rhymes with "spoken."
- **Grep**: a search command. The name stands for "global regular expression print." Say it like it looks: "grep."
- **Rebase**: a Git command to reapply commits on a new base. Pronounced "re-BASE."
- **Cherry-pick**: a Git command to apply a specific commit from one branch to another. Two words: "cherry" then "pick."

---

## What's Next

**Sarah:** Next episode, we move into the appendix reference series - deeper dives into specific technical topics for listeners who want the full details beyond the main series coverage.

**Alex:** Episode 21 will be the first appendix reference. These episodes assume you have heard the main series. They are the "go deeper" content for topics that deserve more time than we could give them in the overview episodes.

**Sarah:** If you have made it this far in the series - 20 episodes, over 10 hours of content - you are ready for the appendix material. It is where we stop holding back on the mathematics, the edge cases, and the implementation minutiae.

**Alex:** Episode 21. For listeners who want to go further.

---

## Pause and Reflect

Think about the last time you lost work. A file not saved. A session crash. An accidental overwrite. How much time did you lose - minutes, hours, days? Now imagine a workflow where every meaningful piece of work is persisted automatically, survives any session termination, and can be recovered in 30 seconds. That is not science fiction. That is Git used as infrastructure rather than as a backup tool. The principles in this episode apply beyond research projects. They apply anywhere continuity matters more than convenience.

---

## Resources

- Repository: https://github.com/theSadeQ/dip-smc-pso.git
- Repository management guide: `.ai_workspace/config/repository_management.md`
- Session continuity guide: `.ai_workspace/guides/session_continuity.md`
- Recovery script: `.ai_workspace/tools/recovery/recover_project.sh`
- Pre-commit hook installation: `.ai_workspace/tools/automation/install_hooks.sh`
- Project state manager: `.ai_workspace/tools/recovery/project_state_manager.py`
- Roadmap tracker: `.ai_workspace/tools/analysis/roadmap_tracker.py`
- Multi-account recovery: `.ai_workspace/tools/multi_account/MULTI_ACCOUNT_RECOVERY_GUIDE.md`
- Workspace organization: `.ai_workspace/guides/workspace_organization.md`

---

*Educational podcast episode -- Git workflow as research infrastructure and persistence layer*
