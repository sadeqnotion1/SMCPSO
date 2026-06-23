# Skills registry -- SMC-PSO-beta

Two kinds of skills are tracked here:

1. **Local skills** -- operating procedures authored in this repo under `.agents/skills/`.
   Author new ones by copying `_template/SKILL.md` to `skills/<name>/SKILL.md` and listing them below.
2. **Recommended external skills** -- vetted, off-the-shelf agent skills (from https://skills.sh)
   that fit this project. Adopt by vendoring the skill folder from its source GitHub repo, or by
   pointing your agent/CLI at it. ASCII markers only (project rule).

---

## 1) Local skills (authored/vendored here)

| Skill | When to use | Path |
|-------|-------------|------|
| `_template` | Copy to start a new skill | `skills/_template/SKILL.md` |
| `ai-research-reproduction` | Ground PSO-tuned gains against cited paper benchmark metrics | `skills/ai-research-reproduction/SKILL.md` |
| `paper-context-resolver` | Resolves reference papers to keep agent context grounded | `skills/paper-context-resolver/SKILL.md` |
| `minimal-run-and-audit` | Runs project minimally and audits outputs (port-and-audit loop) | `skills/minimal-run-and-audit/SKILL.md` |
| `safe-debug` | Structured side-effect-free debugging for JIT/solvers | `skills/safe-debug/SKILL.md` |
| `explore-run` | Maps Numba batch-sim and Optuna execution paths | `skills/explore-run/SKILL.md` |
| `repo-intake-and-plan` | Emits structured work plans for src/ modules | `skills/repo-intake-and-plan/SKILL.md` |
| `test-driven-development` | Write failing tests first for Hypothesis/pytest expansion | `skills/test-driven-development/SKILL.md` |
| `systematic-debugging` | Structured fault isolation for SMC gain/PSO failures | `skills/systematic-debugging/SKILL.md` |
| `verification-before-completion` | Verified outcomes vs criteria before completing (quality gate) | `skills/verification-before-completion/SKILL.md` |
| `writing-plans` | Create checkable migration plans per module | `skills/writing-plans/SKILL.md` |
| `dispatching-parallel-agents` | Spawns multiple parallel agents to audit modules simultaneously | `skills/dispatching-parallel-agents/SKILL.md` |
| `finishing-a-development-branch` | Branch closure and validation workflow | `skills/finishing-a-development-branch/SKILL.md` |
| `tdd` | Red-green-refactor testing workflow | `skills/tdd/SKILL.md` |
| `improve-codebase-architecture` | Structure improvement and module layout suggestions | `skills/improve-codebase-architecture/SKILL.md` |
| `diagnosing-bugs` | Structured bug-triage for config validation and solver errors | `skills/diagnosing-bugs/SKILL.md` |

---

## 2) Recommended external skills (matched from skills.sh)

> Source catalog: https://skills.sh (~283 skills surveyed). Matched 2026-06-23 against this
> repo's needs: running + auditing numerical simulations, reproducing academic results,
> pytest-based testing, debugging Numba/SciPy numerics, and a structured module-by-module
> migration. Grouped by source GitHub repo; ranked within each group. Verify each skill's
> license + contents before vendoring.

### lllllllama/RigorPilot-Skills -- https://github.com/lllllllama/RigorPilot-Skills

| Skill | Relevance | Why it fits | Maps to | Link |
|-------|-----------|-------------|---------|------|
| `ai-research-reproduction` | High | DIP-SMC is grounded in papers; ensures PSO-tuned gains match cited control-theory benchmarks | Lens B (science), M5/M6 | [link](https://github.com/lllllllama/RigorPilot-Skills/tree/main/skills/ai-research-reproduction) |
| `paper-context-resolver` | High | Resolves the SMC/PSO source papers in `references/` to keep agent context grounded | Section 6b (references audit) | [link](https://github.com/lllllllama/RigorPilot-Skills/tree/main/skills/paper-context-resolver) |
| `minimal-run-and-audit` | High | Runs a project minimally, then audits outputs -- the core migration audit pattern | Lens C + gate | [link](https://github.com/lllllllama/RigorPilot-Skills/tree/main/skills/minimal-run-and-audit) |
| `safe-debug` | High | Debugs without mutating state; vital for Numba-JIT / SciPy solver side-effect bugs | Numerics audit | [link](https://github.com/lllllllama/RigorPilot-Skills/tree/main/skills/safe-debug) |
| `explore-run` | Med | Maps Numba batch-sim and Optuna trial execution paths during audits | M2/M6 | [link](https://github.com/lllllllama/RigorPilot-Skills/tree/main/skills/explore-run) |
| `repo-intake-and-plan` | Med | Reads repo structure, emits a structured work plan per module under `src/` | Per-module workflow | [link](https://github.com/lllllllama/RigorPilot-Skills/tree/main/skills/repo-intake-and-plan) |

### obra/superpowers -- https://github.com/obra/superpowers

| Skill | Relevance | Why it fits | Maps to | Link |
|-------|-----------|-------------|---------|------|
| `test-driven-development` | High | Write failing tests first -- serves pytest + pytest-benchmark + Hypothesis expansion | Lens C, M11 | [link](https://github.com/obra/superpowers/tree/main/skills/test-driven-development) |
| `systematic-debugging` | High | Structured fault isolation -- SMC gain instability vs PSO convergence failure | Lens B debugging | [link](https://github.com/obra/superpowers/tree/main/skills/systematic-debugging) |
| `verification-before-completion` | High | Forces verifying outputs vs acceptance criteria before closing -- our gate | Acceptance gate | [link](https://github.com/obra/superpowers/tree/main/skills/verification-before-completion) |
| `writing-plans` | Med | Structured, checkable plans -- the per-module migration checklist | ROADMAP/NEXT | [link](https://github.com/obra/superpowers/tree/main/skills/writing-plans) |
| `dispatching-parallel-agents` | Med | Parallel subagents -- audit independent modules at once (controllers + plant) | Throughput | [link](https://github.com/obra/superpowers/tree/main/skills/dispatching-parallel-agents) |
| `finishing-a-development-branch` | Med | Safe branch-close checklist -- git discipline per `migration/<module>` branch | Per-module workflow | [link](https://github.com/obra/superpowers/tree/main/skills/finishing-a-development-branch) |

### mattpocock/skills -- https://github.com/mattpocock/skills

| Skill | Relevance | Why it fits | Maps to | Link |
|-------|-----------|-------------|---------|------|
| `tdd` | High | Red-green-refactor workflow -- complements benchmark/Hypothesis tests for optimizer/controllers | Lens C | [link](https://github.com/mattpocock/skills/tree/main/skills/engineering/tdd) |
| `improve-codebase-architecture` | Med | Proposes structural improvements -- rationalize the `src/` layout during migration | M3/M4 | [link](https://github.com/mattpocock/skills/tree/main/skills/engineering/improve-codebase-architecture) |
| `diagnosing-bugs` | Med | Bug-triage protocol -- Pydantic config validation / Optuna trial errors | Lens A/B | [link](https://github.com/mattpocock/skills/tree/main/skills/engineering/diagnosing-bugs) |

### Top picks if you only adopt a few
1. `verification-before-completion` (obra) -- it IS our acceptance gate.
2. `minimal-run-and-audit` (RigorPilot) -- it IS our port-and-audit loop.
3. `ai-research-reproduction` + `paper-context-resolver` (RigorPilot) -- the scientific/Lens-B core.
4. `test-driven-development` / `tdd` (obra / mattpocock) -- Lens C coverage gates.

---

## Excluded / unsure (surveyed but not adopted)

- **Front-end / React** -- `frontend-design`, `vercel-react-best-practices`, `web-design-guidelines`,
  `vercel-composition-patterns` (vercel-labs): no React UI here (Streamlit needs no React skill).
- **Cloud infra** -- `microsoft-foundry`, `azure-ai`, `azure-kubernetes`, `azure-compute`
  (microsoft/azure-skills): no cloud-deployment surface.
- **`agent-browser`** (vercel-labs/agent-browser): browser automation; irrelevant to numerics.
- **`brainstorming`** (obra/superpowers): too generic for control-systems migration.
- **`ai-research-explore`** (RigorPilot): overlaps with `ai-research-reproduction`; dropped to stay focused.
- **`run-train`** (RigorPilot): named for ML training loops; PSO is optimization, not ML training -- ambiguous fit.
- **`pptx` / `docx` / `xlsx`** (anthropics/skills): document generation; no fit with Sphinx / scientific Python.
- **`github-actions-docs`** (xixu-me/skills): useful later, but no CI workflow exists yet (revisit at M11).
- **Off-domain** -- `just-scrape` (scrapegraphai), `remotion-*` (remotion-dev), `agentspace-*`, `lark-*`,
  `runcomfy-*`, `shadcn`, `firebase-*`: media / productivity / web frameworks / image-gen.
- **`sentry-cli`** (sentry): error-monitoring SaaS; not integrated.
- **`supabase`** (supabase): Postgres/backend; no database layer in this repo.

_Matched from https://skills.sh on 2026-06-23. Re-run the Prompt Crafter/Perplexity match if the
catalog or this repo's needs change. Confirm licensing before vendoring any external skill._
