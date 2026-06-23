# E010: Documentation System and Navigation

**Part:** Part 2 Infrastructure & Tooling
**Duration:** 15-20 minutes
**Source:** DIP-SMC-PSO Documentation System

---

## Opening Hook

**Sarah:** How do you document 105,000 lines of code? Where do you even start?

**Alex:** You start by assuming that future you will forget everything current you knows. Documentation is not for users. It is for the person reading your code six months from now who has no memory of why you made these decisions.

**Sarah:** And if that person is you?

**Alex:** Then you are grateful that past you was thorough. Today we talk about the documentation system -- how we organized 706 documentation files, built automated API reference, and created navigation that works for five different audience types.

---

## The Documentation Problem

**Sarah:** 105,000 lines of production code across 358 files. How many documentation files does that require?

**Alex:** 706 files in the Sphinx documentation system alone. That does not count README files, docstrings, code comments, or the AI workspace guides. Just the structured documentation.

**Sarah:** How do you prevent that from becoming a mess?

**Alex:** Three principles. First: colocate documentation with code. Every controller in `src/controllers/` has a corresponding page in `sphinx_docs/controllers/`. Second: automate what you can. API reference is generated from docstrings -- we never write it manually. Third: multiple navigation strategies for different mental models.

---

## Sphinx Documentation System

**Sarah:** Walk me through the Sphinx setup. What is Sphinx and why use it?

**Alex:** Think of Sphinx as a Librarian for your scattered notes. You have code comments here, theory explanations there, tutorial examples somewhere else. Sphinx gathers everything, organizes it into chapters, creates a table of contents, builds an index, adds cross-references between related topics, and binds it into a searchable book. It is the standard in the Python ecosystem -- NumPy, SciPy, Django, Flask all use it. The alternative is chaos -- dozens of disconnected markdown files that nobody can navigate.

**Sarah:** Where does it live in the project?

**Alex:** `academic/paper/sphinx_docs/` directory. The configuration is in `conf.py` -- 19 kilobytes of settings for themes, extensions, autodoc behavior, and build options. The source files are organized into subdirectories: `api/`, `controllers/`, `benchmarks/`, `architecture/`, `development/`, `deployment/`, `examples/`.

**Sarah:** How does the build process work?

**Alex:** You run a single command. Sphinx reads the configuration file, parses all markdown and reStructuredText files, generates API reference from Python docstrings using autodoc, builds cross-reference links, and outputs searchable HTML. Think of it like compiling code -- source files go in, website comes out.

**Sarah:** What if the build fails?

**Alex:** Sphinx reports exactly what went wrong. Common failures: broken cross-references between pages, missing docstrings for public functions, invalid markup syntax. You fix the error, rebuild, and verify. We run this in strict mode -- warnings become errors -- to catch problems early. No broken documentation makes it to production.

---

## Directory Structure: Organizing 706 Files

**Sarah:** How are those 706 files organized?

**Alex:** Eight main categories. `api/` has auto-generated API reference -- every public class, function, and module documented from docstrings. `controllers/` has theory and implementation details for each of the seven controllers. `benchmarks/` has performance results and analysis. `architecture/` explains design decisions and patterns. `development/` has contributor guides and coding standards. `deployment/` covers installation and production setup. `examples/` has runnable tutorials. `for_reviewers/` has materials for academic paper reviewers.

**Sarah:** Give me the file count breakdown.

**Alex:** I do not have exact per-category counts, but the largest sections are `api/` with auto-generated reference for 358 source files, and `benchmarks/` with results from 11 research tasks. The `controllers/` section has at least 7 subdirectories -- one per controller type.

---

## API Reference: Automated Documentation

**Sarah:** Explain how API reference generation works.

**Alex:** Here is the key insight: documentation should live next to the code it documents. You write a docstring directly inside the Python function. Sphinx reads that docstring and auto-generates formatted reference pages. Change the function signature? The docs update automatically. No manual copy-pasting. No synchronization problems.

**Sarah:** Why is that important?

**Alex:** Documentation that lives in a separate file always goes stale. You change the code, forget to update the docs, now they lie. Docstrings prevent that. The documentation IS the code. Sphinx just formats it nicely. We use a standard format called NumPy Style -- it forces you to document exactly what goes in and what comes out. Think of it as a contract for every function.

**Sarah:** What happens if you forget to document a public function?

**Alex:** The build fails. We enable strict checking -- missing docstrings trigger warnings, and warnings block commits. It sounds harsh, but it prevents the slow decay into undocumented code. You cannot merge a function without explaining what it does. This is accountability built into the development process.

---

## Learning Paths: Five Audience Types

**Sarah:** You mentioned five learning paths. Who are they for?

**Alex:** Path 0: Complete beginners with zero programming or control theory background. About a semester's worth of prerequisite material on Python, physics, calculus, linear algebra, and control fundamentals. This lives in the education directory as the beginner roadmap.

**Sarah:** That is a long path.

**Alex:** It is. But if you are a mechanical engineering student who has never coded, you need that foundation before you can understand sliding mode control. Path 0 gets you to the starting line. Think of it as the prerequisites course before the main class.

**Sarah:** What about Path 1?

**Alex:** Path 1 is quick start for users with prerequisites. Get a simulation running in 1 to 2 hours. `docs/guides/getting-started.md` -- install Python, clone the repo, create virtual environment, run `python simulate.py`, see the pendulum stabilize. Then Tutorial 01 walks through configuration and visualization.

**Sarah:** And Paths 2 through 4?

**Alex:** Path 2 is advanced usage -- custom controllers, PSO tuning, batch simulations. Path 3 is research workflows -- running benchmarks, analyzing results, writing papers. Path 4 is production deployment -- thread safety, memory management, HIL integration. Each path builds on the previous.

**Sarah:** How do users know which path to follow?

**Alex:** README.md has a decision tree. "Have you programmed in Python before? No -> Path 0. Yes -> Do you know control theory? No -> Path 0 theory section. Yes -> Do you want to run a quick demo? Yes -> Path 1. Do you want to write custom controllers? Yes -> Path 2." And so on.

---

## Cross-References and Linkage

**Sarah:** With 706 files, how do you prevent broken links?

**Alex:** Sphinx cross-reference syntax. You write `:ref:\`section-label\`` to link to a section, `:doc:\`path/to/file\`` to link to a document, `:class:\`ClassName\`` to link to API reference. Sphinx validates all references during build and emits warnings for broken links.

**Sarah:** What if you reorganize the docs?

**Alex:** Update the references. Sphinx catches broken links, you fix them, rebuild passes. This is why automated validation is critical -- you cannot manually verify 706 files for link integrity.

**Sarah:** Do you have a policy for internal vs external links?

**Alex:** Internal links use Sphinx references. External links use plain markdown: `[NumPy Documentation](https://numpy.org/doc/)`. We have a separate link checker script that validates external URLs once per week to catch dead links.

---

## Docstring Standards: NumPy Style

**Sarah:** You mentioned NumPy style docstrings. Why does this matter?

**Alex:** Future-proofing. Six months from now, you will not remember why you designed a function this way. A docstring is a contract. It forces you to document exactly what goes in, what comes out, and what can go wrong. We use NumPy Style -- a standard format that forces you to answer four questions: What does this function do? What inputs does it need? What does it return? What errors can it raise?

**Sarah:** Why not just comment the code?

**Alex:** Comments explain HOW the code works. Docstrings explain WHAT the function promises. And here is the magic: Sphinx reads docstrings and auto-generates API reference. Write documentation once in the code, it appears in three places -- your IDE autocomplete, the function help text when you type question mark in Python, and the published HTML docs. Zero duplication.

**Sarah:** What happens if someone writes a bad docstring?

**Alex:** The build catches it. Missing parameter descriptions? Warning. Return type not documented? Warning. Example code does not run? Error. We enforce this with automated checks. A function without a proper docstring cannot be merged. It sounds strict, but it prevents six months of confusion later when someone asks "What is this parameter supposed to be?" and the original author has graduated and moved to another country.

**Sarah:** So it is accountability.

**Alex:** Exactly. A docstring is a promise to your future self and your collaborators. This function does X. It needs Y. It returns Z. If you cannot write that clearly, you probably do not understand what you are building yet. Good documentation makes you write better code.

---

## Documentation Build Workflow

**Sarah:** When do you rebuild the documentation?

**Alex:** Three scenarios. First: during development when you add new features. You write the code, write the docstring, run `sphinx-build`, verify the API reference looks correct. Second: before committing. Pre-commit hook runs `sphinx-build -W` and fails the commit if there are documentation errors. Third: in CI/CD. GitHub Actions builds the docs and deploys them to GitHub Pages on every merge to main.

**Sarah:** What if the build is slow?

**Alex:** Incremental builds. Sphinx caches parsed content and only rebuilds changed files. First build might take 30 seconds for 706 files. Subsequent builds with one file changed take 2 to 3 seconds.

**Sarah:** Does the documentation get deployed automatically?

**Alex:** Yes. CI workflow builds HTML, creates a tarball, and pushes to the `gh-pages` branch. GitHub Pages serves it at `https://thesadeq.github.io/dip-smc-pso/`. Users always see the latest docs matching the main branch.

---

## Code Examples and Runnable Tutorials

**Sarah:** You mentioned examples. How are those organized?

**Alex:** `examples/` subdirectory with numbered tutorials. `tutorial_01_quick_start.py` -- run a simulation with default settings. `tutorial_02_custom_gains.py` -- modify controller gains and compare. `tutorial_03_pso_tuning.py` -- optimize gains with PSO. `tutorial_04_batch_simulation.py` -- run Monte Carlo validation. `tutorial_05_hil_setup.py` -- configure hardware-in-the-loop.

**Sarah:** Are these runnable scripts or markdown?

**Alex:** Runnable Python scripts with extensive comments. You can copy-paste the code and run it. Each tutorial also has a corresponding markdown file in `sphinx_docs/examples/` that explains the concepts, shows the code, and displays expected output.

**Sarah:** How do you ensure the examples stay up to date?

**Alex:** CI runs all tutorial scripts as integration tests. If a tutorial fails, the build fails. This prevents broken examples from being merged. We also have a validation script that checks if code blocks in markdown match the actual tutorial script files.

---

## Search and Indexing

**Sarah:** With 706 files, how do users find what they need?

**Alex:** Sphinx search. The built HTML includes a JavaScript search index with every heading, function name, class name, and significant term. You type "sliding surface" in the search box, you get links to theory pages, API reference for the sliding surface module, and tutorial examples.

**Sarah:** How granular is the indexing?

**Alex:** Section-level. Every heading is indexed. So if you search for "boundary layer chattering", you get direct links to the section in the Classical SMC theory page where boundary layers are explained, the API reference for the boundary layer parameter, and the benchmark results showing chattering reduction.

**Sarah:** Does it index code snippets?

**Alex:** No. Only headings, API signatures, and manually marked index entries. If you want a code example to appear in search, you add an explicit index entry: `.. index:: PSO; cost function`.

---

## Maintenance and Freshness

**Sarah:** How do you keep 706 files from going stale?

**Alex:** Three mechanisms. First: automated API reference never goes stale because it is generated from code. Change a function signature, the docs update automatically. Second: link validation. Weekly cron job checks all internal and external links, files an issue if any are broken. Third: deprecation warnings. If we mark a function as deprecated, the docstring says so, and Sphinx generates a warning box in the rendered page.

**Sarah:** What about conceptual docs that explain design decisions?

**Alex:** Those require manual review. We have a policy: any pull request that changes architecture must update the corresponding `architecture/` documentation page. The PR template has a checklist: "Updated architecture docs? Yes/No". Reviewer verifies before approving.

**Sarah:** How do you handle documentation debt?

**Alex:** Quarterly audits. We use a script that lists files in `src/` without corresponding documentation in `sphinx_docs/`. That list goes on a backlog. If a module is undocumented but is not used by anyone, we either document it or mark it as deprecated. Undocumented and used modules get priority.

---

## Beginner Roadmap: Path 0

**Sarah:** Tell me more about Path 0. You said about a semester's worth of material.

**Alex:** Five phases spread over 4 to 6 months. Phase 1: Computing basics -- command line, text editors, Git, Python fundamentals. Phase 2: Math foundations -- calculus, linear algebra, differential equations. Phase 3: Physics -- Newtonian mechanics, Lagrangian dynamics, pendulum systems. Phase 4: Control theory -- feedback, PID control, state-space methods. Phase 5: Sliding mode control -- fundamentals, Lyapunov stability, chattering mitigation.

**Sarah:** That is a full semester course.

**Alex:** It is. And that is deliberate. We do not want someone to reach Tutorial 01, hit a line of code that says eigenvalue decomposition, and have no idea what that means. Path 0 ensures you have the prerequisites. Think of it as the foundation before building the house.

**Sarah:** Where does Path 0 live?

**Alex:** In the education directory as the beginner roadmap. It is separate from the Sphinx docs because it is not project-specific -- it is general education. We link to external resources: Python courses on Codecademy, linear algebra on Khan Academy, control theory on MIT OpenCourseWare. We curate the best free resources, not reinvent them.

**Sarah:** How do you test if someone has completed Path 0?

**Alex:** We do not. It is self-paced. But Tutorial 01 assumes you know Python syntax, can read NumPy array operations, and understand what a differential equation is. If you do not, you go back to Path 0. The roadmap has checkpoints -- "Can you write a function? Can you multiply matrices? Can you explain Newton's second law?" -- to help learners self-assess.

---

## Version-Specific Documentation

**Sarah:** Do you maintain docs for multiple versions?

**Alex:** Not yet. We are at version 0.x -- pre-1.0 release. Documentation tracks the main branch only. Once we hit 1.0, we will use Sphinx versioning extension to maintain docs for major releases. Users could switch between "latest", "stable", "v1.0", "v2.0" in the web UI.

**Sarah:** What about deprecated features?

**Alex:** Docstring includes a deprecation notice:

```python
def old_function(x):
    """Legacy function for backward compatibility.

    .. deprecated:: 0.8.0
       Use :func:`new_function` instead. This function will be
       removed in version 1.0.
    """
```

Sphinx renders this with a prominent warning box in the HTML.

---

## User-Contributed Documentation

**Sarah:** Can external contributors add documentation?

**Alex:** Yes. Pull requests welcome for typos, clarifications, new examples. The contribution guide is in `sphinx_docs/development/contributing.md`. Guidelines: follow NumPy docstring style, run `sphinx-build -W` locally to verify no errors, add yourself to the contributors list.

**Sarah:** How do you review documentation PRs?

**Alex:** Same process as code PRs. Check for technical accuracy, verify examples run correctly, ensure links work, confirm the new content fits the existing structure. If the PR adds a new concept, we check that it links to related pages and is reachable from the main navigation.

---

## Key Takeaways

**Sarah:** Let us recap the documentation system.

**Alex:** 706 files in Sphinx documentation system. Organized into eight main categories: API reference, controllers, benchmarks, architecture, development, deployment, examples, reviewer materials.

**Sarah:** API reference is auto-generated from NumPy-style docstrings using Sphinx autodoc. Change the code, the docs update automatically.

**Alex:** Five learning paths for different audiences: Path 0 for complete beginners (about a semester's worth of prerequisites), Path 1 for quick start (1-2 hours), Paths 2-4 for advanced usage, research, and production.

**Sarah:** Sphinx validates cross-references during build. Broken links cause build warnings. CI runs docs build on every commit to prevent merging broken documentation.

**Alex:** Runnable tutorials in `examples/` directory. CI executes them as integration tests to ensure examples stay up to date with code changes.

**Sarah:** Three freshness mechanisms: automated API generation, weekly link validation, PR checklist requiring architecture docs updates.

**Alex:** Path 0 beginner roadmap lives in the education directory with about a semester's worth of prerequisite material on Python, math, physics, and control theory.

**Sarah:** Quarterly audits identify undocumented modules. Prioritize based on usage. Document or deprecate.

---

## Pronunciation Guide

For listeners unfamiliar with technical terms used in this episode:

- **Sphinx**: A documentation generator. Pronounced "SFINKS" (like the mythical creature).
- **reStructuredText**: A markup language. Often abbreviated as "reST." Pronounced "rest" or "R-S-T."
- **autodoc**: Sphinx extension for automatic API documentation. Pronounced "auto-dock."
- **NumPy**: Numerical Python library. Pronounced "NUM-pie."
- **Docstring**: Documentation string inside Python code. Pronounced "dock-string."
- **Markdown**: A lightweight markup language. Pronounced "MARK-down."
- **YAML**: A configuration file format. Pronounced "YAM-ul" (rhymes with "camel").

---

## What's Next

**Sarah:** Next episode, Episode 11, we cover configuration and deployment. How `config.yaml` validates parameters, how Pydantic ensures type safety, and what it takes to deploy this system in different environments.

**Alex:** Configuration as code. Validation as a design principle.

**Sarah:** Episode 11. Coming soon.

---

## Pause and Reflect

Documentation is not a chore. It is a design tool. When you write a docstring explaining what a function does, you often realize the function is too complex. When you write a tutorial showing how to use your system, you discover that your API is confusing. Good documentation makes you write better code. If you cannot explain it clearly, you probably should not build it. The 706 files in this project are not just for users. They are a mirror showing us where the design is clean and where it is still messy. And that mirror is invaluable.

---

## Resources

- **Repository:** https://github.com/theSadeQ/dip-smc-pso.git
- **Sphinx Documentation:** `academic/paper/sphinx_docs/`
- **Documentation Build System:** `.ai_workspace/guides/documentation_build_system.md`
- **Beginner Roadmap (Path 0):** `.ai_workspace/education/beginner-roadmap.md`
- **Getting Started (Path 1):** `sphinx_docs/guides/getting-started.md`

---

*Educational podcast episode -- documenting 105,000 lines of research software*
