<!-- AUTO-GENERATED from .project/ai/edu/ - DO NOT EDIT DIRECTLY -->
<!-- Source: .project/ai/edu/README.md -->
<!-- Generated: 2025-11-11 13:29:26 -->

# Educational Materials (.ai/edu)

**Purpose**: Educational resources and learning roadmaps for users at all skill levels, managed by Claude Code.

**Directory**: `.project/ai/edu/` (Educational materials, excluded from main docs build)

---

## Contents

### 1. Beginner Roadmap

**File**: `beginner-roadmap.md` (~4,000 lines when complete)

**Target Audience**: Complete beginners with ZERO coding and ZERO control theory background

**Learning Path**: 125-150 hours over 4-6 months

**Coverage**:
- **Phase 1** (Week 1-4): Foundations (Computing, Python, Physics, Math basics)
- **Phase 2** (Week 5-8): Core Concepts (Control theory, feedback, SMC introduction)
- **Phase 3** (Week 9-12): Hands-On Learning (Running simulations, interpreting results)
- **Phase 4** (Week 13-16): Advancing Skills (Deeper Python, reading code, understanding math)
- **Phase 5** (Week 17+): Mastery Path (Connecting to Tutorials 01-05, research workflows)

**Current Status**: Phases 1-2 complete (~2,000 lines)

**Next Steps**: Complete Phases 3-5 (estimated +1,500-2,000 lines)

---

## Why .ai/edu/?

**Separation of Concerns**:
- Main `docs/` focuses on project-specific documentation (tutorials, API, theory)
- `.project/ai/edu/` provides prerequisite learning for complete beginners
- Users who already have Python/physics knowledge can skip directly to `docs/guides/getting-started.md`

**Audience Segmentation**:
- `.project/ai/edu/beginner-roadmap.md` --> Users with NO programming/physics background (Path 0)
- `docs/guides/getting-started.md` --> Users with Python basics and some physics (Path 1)
- `docs/guides/tutorials/` --> Users ready for hands-on project work (Paths 2-4)

**Maintenance**:
- Educational content evolves separately from project documentation
- External resource links (YouTube, Khan Academy) managed independently
- Claude Code can update learning paths without affecting core docs

---

## Integration with Main Documentation

### Learning Path Progression

```
Path 0: Complete Beginner (NEW)
  └─> .project/ai/edu/beginner-roadmap.md (125-150 hours)
       ├─> Phase 1: Foundations (Python, physics, math)
       ├─> Phase 2: Core Concepts (Control theory, SMC)
       ├─> Phase 3-5: Hands-on --> Mastery
       └─> Connects to Path 1 (v)

Path 1: Quick Start (EXISTING)
  └─> docs/guides/getting-started.md --> Tutorial 01 (1-2 hours)

Path 2: Controller Expert (EXISTING)
  └─> Getting Started --> Tutorials 01-03 --> SMC Theory (4-6 hours)

Path 3: Custom Development (EXISTING)
  └─> Getting Started --> Tutorials 01-04 --> API Reference (8-12 hours)

Path 4: Research Publication (EXISTING)
  └─> Complete Paths 1-2 --> Tutorial 05 --> Theory Guides (12+ hours)
```

### Cross-References

**From beginner-roadmap.md to main docs**:
- Phase 5 links to `docs/guides/tutorials/tutorial-01-first-simulation.md`
- Physics sections reference `docs/guides/theory/dip-dynamics.md`
- SMC introduction prepares for `docs/guides/theory/smc-theory.md`
- Python skills needed for `docs/guides/api/` usage

**From main docs to beginner-roadmap.md**:
- `docs/guides/getting-started.md` --> Prerequisites section links to `.project/ai/edu/beginner-roadmap.md`
- `docs/guides/INDEX.md` --> "Path 0: Complete Beginner" references this directory
- `README.md` --> Learning paths section mentions Path 0 for absolute beginners

---

## Future Educational Content

**Planned Additions**:

1. **Intermediate Roadmap** (`.project/ai/edu/intermediate-roadmap.md`)
   - For users who completed Path 1-2 and want to go deeper
   - Advanced control theory (Lyapunov, stability proofs)
   - Advanced Python (decorators, generators, async)
   - Research methods (experimental design, statistical validation)

2. **Quick Reference Cards** (`.project/ai/edu/cheatsheets/`)
   - Python essentials for this project
   - Control theory formulas
   - Git commands
   - Command line reference
   - NumPy/Matplotlib quick reference

3. **Video Curriculum** (`.project/ai/edu/video-series.md`)
   - Curated YouTube playlists for each phase
   - Timestamp links to specific topics
   - Alternative explanations for difficult concepts

4. **Exercise Solutions** (`.project/ai/edu/exercises/`)
   - Detailed solutions to practice problems
   - Worked examples with explanations
   - Additional challenge problems

5. **FAQ for Beginners** (`.project/ai/edu/faq-beginners.md`)
   - Common misconceptions
   - "I'm stuck at X, what should I do?"
   - Hardware requirements clarification
   - Time commitment reality checks

---

## Maintenance Guidelines

**For Claude Code**:

1. **When updating beginner-roadmap.md**:
   - Keep external links updated (check for broken YouTube links)
   - Update time estimates based on user feedback
   - Add new interactive code examples as Python evolves
   - Maintain consistency with main `docs/` tutorials

2. **When adding new educational content**:
   - Follow the same structure: Learning objectives --> Steps --> Self-assessment
   - Include time estimates for each section
   - Provide multiple learning modalities (video, text, interactive)
   - Link to relevant main docs sections

3. **Quality standards**:
   - All code examples must be runnable and tested
   - External resource links should be to reputable sources (Khan Academy, MIT OCW, official docs)
   - Avoid "fluff" - every section should teach concrete skills
   - Self-assessments should be meaningful (not trivial)

**For Users**:

- If a link is broken, open an issue on GitHub
- If a concept is unclear, suggest improvements in Discussions
- If you find a better external resource, recommend it
- If time estimates are way off, provide feedback

---

## Document Status

| File | Status | Lines | Completion | Last Updated |
|------|--------|-------|------------|--------------|
| `beginner-roadmap.md` | Partial | ~2,000 / ~4,000 | 50% | 2025-10-16 |
| `README.md` (this file) | Complete | ~200 | 100% | 2025-10-16 |
| `intermediate-roadmap.md` | Planned | 0 | 0% | N/A |
| `cheatsheets/` | Planned | 0 | 0% | N/A |
| `video-series.md` | Planned | 0 | 0% | N/A |

---

## How to Use This Directory

**If you're a complete beginner**:
1. Start with `beginner-roadmap.md`
2. Follow the phases in order
3. Take the self-assessments seriously
4. Don't skip sections unless you're SURE you know the material
5. Expect 4-6 months of part-time study

**If you have some background**:
1. Review Phase 1 self-assessments to identify gaps
2. Skip sections you already know
3. Focus on control theory (Phase 2) if coming from software background
4. Focus on Python (Phase 1.2) if coming from engineering background
5. Jump to `docs/guides/getting-started.md` once assessments pass

**If you're an educator**:
1. Use these materials as supplementary resources
2. Adapt time estimates for classroom settings (usually faster with instructor)
3. Consider the interactive code examples for demonstrations
4. Link to this roadmap for students needing prerequisites

---

## Contributing

**To improve educational materials**:

1. **Suggest better external resources**:
   - Open issue: "Better resource for [topic]"
   - Provide link, brief description, why it's better

2. **Report broken links**:
   - Open issue: "Broken link in beginner-roadmap.md line [X]"
   - Include section name

3. **Improve explanations**:
   - Fork repository
   - Edit `.project/ai/edu/beginner-roadmap.md`
   - Submit pull request with clear description of improvement

4. **Add interactive examples**:
   - All code must run without errors
   - Include comments explaining what code does
   - Add expected output description

5. **Update time estimates**:
   - If you completed a phase, report actual time taken
   - Help us calibrate estimates for future learners

---

## Philosophy

**Progressive Disclosure**:
- Start simple, add complexity gradually
- Don't overwhelm beginners with advanced concepts
- Build intuition before introducing mathematics

**Just-In-Time Learning**:
- Learn concepts right before you need them
- Avoid "you'll need this later" syndrome
- Immediate application reinforces learning

**Multiple Modalities**:
- Visual (diagrams, plots)
- Hands-on (code examples, experiments)
- Reading (detailed explanations)
- Auditory (linked video resources)

**Feedback Loops**:
- Self-assessments after every major section
- Immediate feedback on understanding
- Clear remediation paths if stuck

**Realistic Expectations**:
- Honest time estimates (not optimistic)
- Acknowledgment of difficulty
- Celebration of progress

---

## Contact

**For questions about educational materials**:
- Open issue on GitHub: [Issues](https://github.com/theSadeQ/dip-smc-pso/issues)
- Tag with `documentation` and `education`
- Claude Code monitoring for educational content improvements

**For general project questions**:
- See `docs/guides/getting-started.md` for Getting Started support
- See `CLAUDE.md` for project conventions
- See `README.md` for project overview

---

**Last Updated**: 2025-10-16
**Maintained By**: Claude Code AI Assistant
**Repository**: https://github.com/theSadeQ/dip-smc-pso
