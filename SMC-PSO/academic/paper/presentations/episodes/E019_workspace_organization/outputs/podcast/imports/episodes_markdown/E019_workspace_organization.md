# E019: Workspace Organization

**Part:** Part 4 Professional
**Duration:** 25-30 minutes
**Hosts:** Dr. Sarah Chen (Control Systems) & Alex Rivera (Software Engineering)

---

## Opening Hook

**Sarah:** Alex, I want to talk about something that never makes it into research papers but determines whether a project survives six months or six years.

**Alex:** Workspace organization. The unsexy foundation everything else sits on.

**Sarah:** Exactly. We have 985 documentation files, 358 source files, multiple agent systems running concurrently, and a recovery infrastructure that lets us pick up where we left off after a token limit crash. None of that works without deliberate organization.

**Alex:** Most research projects start with a flat directory -- everything in one folder, no conventions, no automation. By month three, nobody can find anything.

**Sarah:** So today we walk through how this project is organized, why the decisions were made, and what the systems look like that keep it all coherent over time.

---

## What You'll Discover

- The directory structure philosophy: why visible root items are capped at 19 and hidden directories at 9
- The 6-agent orchestration system: how parallel AI agents coordinate without stepping on each other
- Model Context Protocol servers: 12 specialized tools that auto-trigger based on task keywords
- The multi-account recovery workflow: resuming work across different sessions and accounts
- Checkpoint systems that survive token limits and crashes
- The cleanup policy that prevents workspace drift
- Why architectural invariants are treated as sacred rules that must never be violated

---

## Directory Structure: The 19-Item Rule (The Limit of Human Short-Term Memory)

**Sarah:** Let's start with the physical layout. The project root has a hard limit: no more than 19 visible directory entries.

**Alex:** That sounds arbitrary. Why 19?

**Sarah:** Because of **cognitive load**—the limit of human short-term memory. Back in 1956, psychologist George Miller published a famous paper: "The Magical Number Seven, Plus or Minus Two."

**Alex:** Seven items, plus or minus two. So humans can hold 5 to 9 items in short-term memory at once.

**Sarah:** Exactly. When you open a project directory and see **40 folders**, your brain immediately feels overwhelmed. You can't process that many items at a glance. You have to scroll, re-read, forget what you've seen.

**Alex:** At 19 or fewer items, you can **mentally categorize everything in a few seconds**. Source code here. Documentation there. Configuration files over there. Your brain can handle it.

**Sarah:** It's not arbitrary—it's respecting the biological limits of human cognition.

**Alex:** Walk me through the actual structure.

**Sarah:** Core source directories: src/, tests/, scripts/. Data directories: academic/, benchmarks/, optimization results/, data/. Configuration: config dot yaml at the root. Entry points: simulate dot py, streamlit app dot py. Documentation: docs/, README, CHANGELOG, CLAUDE dot md.

**Alex:** And the hidden directories?

**Sarah:** Nine total, capped at nine. The primary one is dot ai underscore workspace -- that is the canonical location for all AI operation configs, development tools, guides, planning documents, and state tracking. There is also dot cache for ephemeral project data like pytest caches and hypothesis databases.

**Sarah:** The naming convention matters. dot ai underscore workspace uses underscores because dots and hyphens in directory names cause issues with some Windows tooling and shell globbing patterns.

**Alex:** What about the academic directory? That is visible and it is large.

**Sarah:** The academic directory follows a three-category structure that was reorganized in December 2025. Paper -- 203 megabytes -- holds research papers, thesis source, sphinx documentation, and experiment data. Logs -- 13 megabytes -- holds runtime and development logs. Dev -- 46 megabytes -- holds quality audits and coverage reports.

**Alex:** Why not hide academic behind a dot prefix?

**Sarah:** Because it contains the primary research deliverables. The thesis, the paper, the experiment results -- those are the project outputs. They should be visible and findable without knowing hidden directory conventions.

---

## The 6-Agent Orchestration System: The Conductor

**Sarah:** Now let's talk about the multi-agent system. This project uses what is called the Ultimate Orchestrator pattern for parallel AI-assisted development.

**Alex:** Six agents working simultaneously. How does that actually work without chaos?

**Sarah:** Think of a symphony orchestra. You have 80 musicians—violins, cellos, trumpets, drums. If they all played independently, it would be noise. But there's a **conductor** standing in front, coordinating everyone.

**Alex:** The Ultimate Orchestrator is the conductor. It doesn't play an instrument itself—it directs the other agents, decides when each one starts, makes sure they harmonize.

**Sarah:** The hierarchy has a clear structure. At the top is the Ultimate Orchestrator—the coordinating agent that plans multi-domain tasks, determines which subordinate agents to launch, and aggregates their results into a coherent whole.

**Alex:** And the subordinates?

**Sarah:** Five specialized agents. The Integration Agent handles end-to-end system integration and cross-component validation. Think of it as the agent that checks whether the pieces fit together. The Control Systems Agent focuses on SMC algorithm implementation and stability analysis -- the mathematical core. The PSO Agent handles optimization algorithm tuning and convergence analysis. The Documentation Agent generates documentation and enforces quality standards. And the Code Beautification Agent applies style guidelines and refactors for clarity.

**Alex:** Six agents running in parallel sounds like a coordination nightmare. How do they avoid conflicts?

**Sarah:** Three mechanisms. First, task decomposition. The Orchestrator breaks a complex task into independent subtasks that do not overlap. If one agent is working on controller implementation, another is working on test generation -- they touch different files.

**Alex:** What if they do need to touch the same file?

**Sarah:** Second mechanism: checkpoint ordering. Each agent writes checkpoints -- serialized state snapshots -- at defined intervals. The Orchestrator reviews checkpoints to detect conflicts before they reach the filesystem. If two agents are both modifying the same module, the Orchestrator serializes their work rather than letting them race.

**Sarah:** Third mechanism: quality gates. Before any agent's output is merged into the main codebase, it passes through a validation pipeline. Test pass rate must be 100 percent. No new critical issues. No architectural invariant violations.

**Alex:** How often do conflicts actually occur in practice?

**Sarah:** Rarely. The task decomposition is designed to minimize overlap. The agents work on different domains -- one on the controller math, another on the optimization infrastructure, another on documentation. Conflicts arise mainly when a documentation agent references code that a control systems agent is simultaneously modifying. The checkpoint system catches those.

---

## Model Context Protocol: 12 Specialized Servers

**Sarah:** Beyond the agent orchestration, this project uses 12 Model Context Protocol servers -- MCP servers -- that provide specialized capabilities to the AI development workflow.

**Alex:** What is a Model Context Protocol server, in plain language?

**Sarah:** Think of it as a plugin system. Each MCP server exposes a set of tools that the AI assistant can call. Instead of the AI knowing how to do everything itself, it delegates specialized tasks to purpose-built servers.

**Alex:** Give me the lineup.

**Sarah:** The core servers handle foundational operations. Filesystem for file read and write. GitHub for issue and pull request management. Sequential-thinking for planning and debugging workflows. Puppeteer for browser automation and UI testing.

**Alex:** Those sound like general-purpose tools.

**Sarah:** They are. The specialized servers are where it gets interesting. Pytest-MCP for test debugging -- it can run individual tests, capture stack traces, and suggest fixes. Git-MCP for advanced Git operations beyond what the standard CLI provides. SQLite-MCP for querying the PSO optimization database. Pandas-MCP for data analysis on benchmark results. NumPy-MCP for numerical computation. Lighthouse-MCP for performance audits. And MCP-Analyzer for code quality assessment.

**Alex:** 12 servers. How does the AI know which ones to use?

**Sarah:** Auto-triggering based on task keywords. If you ask about data analysis, the system chains filesystem, SQLite-MCP, and Pandas-MCP automatically. If you ask about testing, it chains Pytest-MCP and Puppeteer. The user does not need to specify which servers to activate -- the orchestration layer handles it.

**Alex:** What is the typical chain length?

**Sarah:** Three to five servers for a complete workflow. Sequential-thinking for planning, then the relevant domain servers for execution, then the quality servers for validation. A data analysis workflow might look like: sequential-thinking plans the analysis, filesystem locates the data files, SQLite-MCP queries the PSO results database, Pandas-MCP performs the statistical computations, and MCP-Analyzer checks the output quality.

**Sarah:** The configuration lives in dot mcp dot json at the project root. All 12 servers are defined there with their connection parameters and capability descriptions.

**Alex:** How does the auto-trigger actually work under the hood?

**Sarah:** The orchestration layer maintains a keyword-to-server mapping. When a task description contains words like "benchmark," "performance," or "timing," the system activates the relevant analysis servers. When it contains "test," "debug," or "failure," the testing servers come online. It is not a simple keyword match -- it uses semantic analysis to determine which server combination best fits the task.

**Alex:** And the servers communicate with each other?

**Sarah:** They share a common data format. The output of one server becomes the input to the next in the chain. Pandas-MCP can consume the output of SQLite-MCP directly. MCP-Analyzer can evaluate the code produced by the filesystem server. The chain is composable -- you can add or remove servers without breaking the workflow.

**Alex:** What happens when a server fails mid-chain?

**Sarah:** The orchestration layer catches the error, logs it, and either retries with a different server or falls back to a degraded workflow. For example, if Pandas-MCP is unavailable, the analysis can still proceed using NumPy-MCP with reduced functionality. The system is designed for graceful degradation, not all-or-nothing execution.

---

## Multi-Account Recovery: Surviving Session Boundaries

**Sarah:** Here is a problem unique to AI-assisted development: the AI assistant has a token limit. When it runs out, the session ends. All in-memory state is lost.

**Alex:** That sounds catastrophic for complex multi-hour tasks.

**Sarah:** It would be, without the recovery infrastructure. This project implements a multi-account recovery workflow that allows work to resume from any session, any account, within 30 seconds.

**Alex:** How?

**Sarah:** Git is the persistence layer. Every meaningful piece of work is committed with a structured message format. The commit message includes a task identifier -- like MT-6 or LT-7 -- and a brief description. A pre-commit hook automatically updates the project state tracker based on the task ID in the commit message.

**Alex:** So the git history is not just version control. It is a task completion log.

**Sarah:** Exactly. When a new session starts -- whether due to token limit, account switch, or hours-long gap -- the recovery script pulls the latest commits, reads the project state from dot ai underscore workspace slash state, analyzes agent checkpoints for any incomplete work, and reconstructs exactly where the previous session left off.

**Alex:** Walk me through the recovery sequence.

**Sarah:** Step one: pull latest commits from remote. This ensures you have every piece of work that was committed before the session ended. Step two: load project state from the state directory. This file tracks current phase, roadmap progress, and active task list. Step three: analyze agent checkpoints. If a multi-agent task was interrupted mid-execution, the checkpoint files show which agents completed and which were still running. Step four: review the roadmap tracker, which parses the 72-hour research roadmap and identifies remaining tasks. Step five: resume from the last known good state.

**Alex:** The key tools in this system?

**Sarah:** Three primary scripts. Project State Manager tracks phase and roadmap progress -- it is the single source of truth for "where are we." Roadmap Tracker parses the full 72-hour research roadmap, which contains 50 tasks across multiple phases. Agent Checkpoint handles recovery of interrupted multi-agent work specifically.

**Alex:** And the validation?

**Sarah:** 11 tests covering the recovery workflow, all passing at 100 percent. The test suite verifies that recovery produces identical state to what existed before the interruption.

---

## Checkpoint System: Surviving Token Limits

**Sarah:** The checkpoint system deserves its own discussion because it is the mechanism that makes long-running tasks survivable.

**Alex:** What does a checkpoint actually contain?

**Sarah:** A serialized snapshot of the agent's state at a point in time. It includes: the task identifier, the agent identifier, hours completed, deliverables produced so far, and the current phase of execution. It is written to disk every 5 to 10 minutes during agent execution.

**Alex:** So if the session crashes at minute 47 of a 2-hour task, the checkpoint from minute 45 captures almost all the progress?

**Sarah:** Correct. The recovery script finds that checkpoint, reads the state, and the next session can resume from minute 45 rather than starting from scratch.

**Alex:** How are checkpoints triggered?

**Sarah:** Four mandatory checkpoint calls in the workflow. First: when the user approves the plan -- this captures the task definition and scope. Second: when each agent launches -- this records which agent is starting and what its role is. Third: every 5 to 10 minutes during execution -- this is the progress heartbeat. Fourth: when an agent completes or fails -- this captures the final outcome or the failure reason with a recovery recommendation.

**Sarah:** The checkpoint files live in dot ai underscore workspace slash tools slash checkpoints. They are small -- typically under 10 kilobytes each -- but their presence is the difference between losing two hours of work and losing nothing.

**Alex:** What survives token limits and what does not?

**Sarah:** Git commits survive with 10 out of 10 reliability. Project state survives at 9 out of 10. Agent checkpoints at 9 out of 10. Data files at 8 out of 10. What does not survive: background bash processes and in-memory agent state. But the checkpoint system is specifically designed to capture the in-memory state before it can be lost.

---

## Cleanup Policy: Preventing Workspace Drift

**Sarah:** Organization is not a one-time setup. It degrades over time unless there are explicit policies to maintain it.

**Alex:** What kind of drift happens?

**Sarah:** Intermediate files accumulate at the root level. Build artifacts pile up. Test output files proliferate. Old versions of scripts sit alongside new ones. Within a few weeks of active development, a clean workspace becomes cluttered.

**Alex:** So you enforce cleanup?

**Sarah:** Mandatory cleanup after multi-file creation, after PDF or LaTeX compilation, and before every commit. The target is no more than 5 active files at any folder root -- final deliverables only. Old versions get archived. Intermediate files get removed. Build artifacts go into the cache directory.

**Sarah:** The workspace health check is a simple sequence of commands: count visible root items (target 19 or fewer), count hidden directories (target 9 or fewer), check cache size (target under 50 megabytes), check academic directory size (target under 150 megabytes including the 98-megabyte thesis).

**Alex:** And these targets are enforced automatically?

**Sarah:** The pre-commit hook checks root item count. If it exceeds the limit, the commit is flagged. The cleanup is a human action -- the AI assistant is instructed to perform cleanup before committing -- but the enforcement is automated.

**Alex:** What does the cleanup workflow look like in practice?

**Sarah:** When a task involves creating multiple files -- say, generating benchmark reports or running a LaTeX compilation -- the workflow is: create the files, archive any old versions of those files, add a README if the directory is new, then commit. The intermediate outputs -- compiler logs, temporary data files, draft versions -- are removed before the commit reaches the repository.

**Alex:** Does this slow down development?

**Sarah:** Not if it is built into the workflow. The cleanup trigger is "after multi-file creation" -- it happens at natural pause points, not mid-task. And the rules are simple enough that the AI assistant can execute them without human intervention. The target of 5 active files per folder root means most cleanup is just "move the old version to archive, keep the new one."

**Alex:** What about the deprecated directory aliases?

**Sarah:** During the December 2025 reorganization, several directories were migrated. dot project moved to dot ai underscore workspace. dot ai moved to dot ai underscore workspace or academic archive. dot artifacts moved to academic. dot logs moved to academic logs. All migrations used git mv to preserve history. But the old paths are explicitly marked as deprecated in the conventions -- any code referencing them triggers a warning.

---

## Architectural Invariants: The Rules That Cannot Be Broken

**Sarah:** The final piece of workspace organization is architectural invariants -- rules established through structural analysis that must never be violated regardless of what task is being performed.

**Alex:** Give me examples.

**Sarah:** Compatibility layers must be preserved. The optimizer directory redirects to the optimization directory for backward compatibility. If you refactor and remove that redirect, existing code that imports from the old path breaks silently. Re-export chains must remain intact -- simulation context is intentionally available from three different import paths for flexibility.

**Alex:** What about the model variants?

**Sarah:** Eight dynamics files exist in the plant module, each representing a different accuracy-performance tradeoff. A developer might look at that and think "this is redundant, let me consolidate." But each variant serves a specific use case. The simplified model runs fast for Monte Carlo. The full nonlinear model provides accuracy for validation. The low-rank approximation balances speed and fidelity. Consolidating them would destroy that flexibility.

**Sarah:** And there is one that catches people off-guard: the test automation file in the HIL interfaces directory is production code, not a test file. Its filename contains "test" but it is part of the hardware-in-the-loop framework. Moving it to the tests directory would break the HIL system.

**Alex:** How are these invariants documented?

**Sarah:** Section 25 of CLAUDE dot md -- the project conventions file -- lists every architectural invariant with a rationale. Any AI assistant or developer working on this project reads that section before making structural changes.

**Alex:** What are the quality gates for invariant compliance?

**Sarah:** Zero critical issues -- mandatory. Zero malformed directory or file names -- mandatory. Test pass rate 100 percent -- mandatory. Root items 19 or fewer -- required. High-priority issues 3 or fewer -- required.

---

## Key Takeaways

**Sarah:** Workspace organization is infrastructure, not decoration. The decisions made here -- directory caps, agent coordination, checkpoint systems, cleanup policies, architectural invariants -- are what allow a complex research project to remain navigable and maintainable over months of development.

**Alex:** The 30-second recovery workflow is the headline achievement. Token limits, account switches, multi-month gaps -- none of them destroy progress because every meaningful state change is persisted through git commits and checkpoint files.

**Sarah:** And the 6-agent orchestration with 12 MCP servers means the AI development workflow scales without human bottlenecks. Complex tasks decompose into parallel streams, each handled by a specialist, coordinated by an orchestrator, validated by quality gates.

**Alex:** The organization is not the glamorous part of the project. But without it, everything glamorous -- the controllers, the paper, the benchmarks -- would not exist in their current form.

---

## Pronunciation Guide

- **MCP**: Model Context Protocol. Say each letter: "M-C-P."
- **Orchestrator**: the coordinating agent. Pronounced "or-ches-TRAY-tor."
- **Checkpoint**: a saved snapshot of progress. Two words: "check" then "point."
- **Token limit**: the maximum amount of text an AI session can process. "Token" rhymes with "spoken."
- **Weakref**: weak reference. A programming pattern. Two words: "weak" then "ref."
- **Serialized**: converted to a storable format. Pronounced "SEER-ee-ah-lized."
- **Idempotent**: producing the same result regardless of how many times it runs. Pronounced "eye-DEM-po-tent."

---

## What's Next

**Sarah:** Next episode, Episode 20, we talk about version control and the Git workflow that underlies all of this organization.

**Alex:** Git is not just a backup system here. It is the persistence layer for the recovery infrastructure, the task completion log, and the coordination mechanism between agents.

**Sarah:** We will walk through commit conventions, branch strategy, and how the pre-commit hooks automate state tracking.

**Alex:** Episode 20. The plumbing that holds everything together.

---

## Pause and Reflect

Consider the last research project you worked on. How long did it take to find a specific file? How long to understand where you left off after a break? If those answers are measured in hours rather than seconds, the organization infrastructure we described today is the difference. It is not about tidiness for its own sake. It is about preserving the ability to do complex work over extended time periods without losing context.

---

## Resources

- Repository: https://github.com/theSadeQ/dip-smc-pso.git
- Workspace conventions: CLAUDE.md sections 14, 22, 25
- Agent orchestration guide: `.ai_workspace/config/agent_orchestration.md`
- MCP server configuration: `.mcp.json`
- Recovery workflow: `.ai_workspace/tools/recovery/recover_project.sh`
- Checkpoint system: `.ai_workspace/tools/checkpoints/`

---

*Educational podcast episode -- workspace organization and AI development infrastructure*
