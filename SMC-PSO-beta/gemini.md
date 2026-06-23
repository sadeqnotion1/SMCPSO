# gemini.md -- Project Conventions & Gemini Agent Instructions

> Universal instructions for any Gemini-based AI agent working in this repository.
> Combines platform safety, repository architecture, and agent execution guidelines.

---

## 1) Critical Platform Rules

**NO EMOJIS (MANDATORY):**
- NEVER use Unicode emojis in code, scripts, output, or documentation.
- ALWAYS use ASCII text markers: `[OK]`, `[ERROR]`, `[WARNING]`, `[INFO]`, `[AI]`, `[DONE]`, `[FAIL]`, `[PAUSE]`
- Reason: The Windows terminal (cp1252 encoding) cannot display Unicode properly, causing execution crashes.
- Applies to: Python scripts, shell output, markdown docs, commit messages, and all agent-user interactions.

**WINDOWS PLATFORM (MANDATORY):**
- Platform: Windows (win32).
- ALWAYS use `python` NOT `python3` (`python3` does not exist on Windows, causing exit code 49).
- ALWAYS use `python -m pytest` NOT `python3 -m pytest`.
- Example: `python simulate.py --ctrl classical_smc --plot`

**PATH SAFETY (MANDATORY):**
- NEVER create directories with braces or spaces: `{dir}/`, `my folder/`.
- NEVER use Windows device names: `nul`, `con`, `prn`, `aux`, `com1`..`com9`, `lpt1`..`lpt9`.
- NEVER use Unicode characters in file/directory paths.

---

## 2) Auto-Commit Policy

**SUSPENDED MODE:**
- GitHub access is currently unavailable. Do NOT push or commit automatically unless explicitly requested.
- Standard flow in suspended mode:
  1. Make and verify all file changes.
  2. Stage changes: `git add <changed files>`
  3. STOP -- do not commit, do not push.
  4. Inform the user what is staged and provide the commit command to run manually.

**COMMIT MESSAGE FORMAT:**
```
<Action>: <Brief description>

- <Detailed change 1>
- <Detailed change 2>

[AI] Generated with AI assistance

Co-Authored-By: AI Agent <noreply@agent.ai>
```

---

## 3) Project Architecture & Directory Conventions

### Core Folder Structure
- `src/` -- Production code only (models, controllers, configuration, optimization).
- `scripts/` -- Development tools (executed, not imported by production code).
- `tests/` -- Pytest test suite (files named `test_*.py`).
- `academic/` -- Research logs, papers, and draft artifacts.

### Reference Database Synchronization
- Whenever a new reference is added or modified in the bibliography databases (`references/config.bib` or `references/controllers.bib`), the corresponding document PDF (or a descriptive placeholder text file if the document is under a strict paywall/copyright restriction) MUST be downloaded/placed in `references/discussed_sources/` and staged.

### Key Entry Points
- `simulate.py` -- Main CLI script for simulation runs and optimizations.
- `streamlit_app.py` -- Web UI dashboard for control comparisons.
- `config.yaml` -- Dynamic parameters definition file.

### Architectural Invariants (DO NOT "FIX")
- **Shim Folders**: `src/optimizer/` (re-exports from `src/optimization/`) and `src/core/` (re-exports from `src/simulation/`) are compatibility layers. Do NOT consolidate these.
- **Simulation Context**: Re-exported chains (`src/core/simulation_context.py` -> `src/simulation/context/simulation_context.py` -> `src/simulation/core/simulation_context.py`) are intentional paths.
- **Model Variants**: Multiple dynamics files in `src/plant/models/` represent simplified, full, and low-rank mathematical approximations.

---

## 4) Testing & Quality Standards

- **Enforced Coverage**: Overall >= 85% | Critical >= 95% | Safety-Critical = 100%.
- **File Matching**: Every production file in `src/` should have a matching `test_*.py` script in `tests/`.
- **Command References**:
  ```bash
  python -m pytest tests/ -v                             # Runs entire suite
  python -m pytest tests/ --cov=src --cov-report=html    # With coverage reports
  ```

---

## 5) Gemini Agent Guidelines

### Planning Mode Workflow
When planning major architectural changes or non-trivial modifications, Gemini agents must:
1. **Research**: Review codebase structure before edits.
2. **Create Plan**: Write or update `implementation_plan.md` in the App Data conversation folder with `RequestFeedback: true` in the metadata.
3. **Wait for Approval**: Stop execution and wait for the user to review.
4. **Track Execution**: Create a `task.md` list to check off completed items.
5. **Verify**: Run compilation checks and test suites, then compile a final `walkthrough.md`.

### Clickable File Links (MANDATORY)
- ALWAYS format links to local files and code folders using absolute file links (e.g. `[setup.py](file:///E:/University/SMC-PSO-beta/setup.py)`).
- On Windows systems, use forward slashes for the URI path format (e.g. `file:///E:/University/...`).
- NEVER wrap link text in backticks.
  - Correct: `[setup.py](file:///path)`
  - Incorrect: `[\`setup.py\`](file:///path)`

### Responses & Coding Style
- **Type Hints**: Include comprehensive type hints in all Python function signatures.
- **ASCII Headers**: Maintain package and module ASCII visual borders in Python files:
  ```python
  #======================================================================================\\\
  #============================ module_name.py ==========================================\\\
  #======================================================================================\\\
  ```
- **Controller Memory**: All controller instances must expose a `cleanup()` method and use Python's `weakref` module to avoid circular memory leaks with simulation engines.
