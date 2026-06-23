# MCP Debugging & Code Quality

**Model Context Protocol (MCP) integration, code quality analysis, and debugging workflows**

This section documents the MCP server ecosystem integration, automated code quality analysis workflows, and comprehensive debugging procedures for the DIP SMC PSO Framework.

---

## Overview

The MCP debugging infrastructure provides:

- **[MCP Server Integration](#mcp-server-integration)** - Ruff, Vulture, Pandas, and Playwright MCP servers
- **[Code Quality Analysis](#code-quality-analysis)** - Automated ruff and vulture findings
- **[Debugging Workflows](#debugging-workflows)** - Complete multi-server debugging procedures
- **[Validation Workflows](#validation-workflows)** - Code quality and validation automation

**MCP Servers**: Ruff (linting), Vulture (dead code), Pandas (data analysis), Playwright (browser testing)

---

## MCP Server Integration

Core documentation for MCP server setup, configuration, and troubleshooting.

```{toctree}
:maxdepth: 2
:caption: MCP Integration

README
QUICK_REFERENCE
INSTALLATION_LOG
MISSING_SERVERS_RESEARCH
```

**Key Documents:**
- [MCP Debugging README](README.md) - Overview and getting started
- [Quick Reference](QUICK_REFERENCE.md) - Common MCP server commands and workflows
- [Installation Log](INSTALLATION_LOG.md) - MCP server installation history and troubleshooting
- [Missing Servers Research](MISSING_SERVERS_RESEARCH.md) - Investigation of unavailable MCP servers

### Available MCP Servers

| MCP Server | Purpose | Status | Usage |
|------------|---------|--------|-------|
| **Ruff** | Python linting and code quality | ✅ Active | Automated linting in workflows |
| **Vulture** | Dead code detection | ✅ Active | Find unused code and imports |
| **Pandas** | Data analysis and manipulation | ✅ Active | Statistical analysis, data processing |
| **Playwright** | Browser automation and testing | ✅ Active | Streamlit dashboard testing |

---

## Code Quality Analysis

Automated code quality analysis results from ruff (linting) and vulture (dead code detection).

### Analysis Results Index

```{toctree}
:maxdepth: 2
:caption: Analysis Results

analysis_results/README
```

### Ruff Linting Results

Comprehensive linting findings across multiple analysis sessions.

```{toctree}
:maxdepth: 1
:caption: Ruff Findings

analysis_results/RUFF_FINDINGS_20251006_175120
analysis_results/RUFF_FINDINGS_20251006_175404
analysis_results/RUFF_FINDINGS_20251006_183442
analysis_results/RUFF_FINDINGS_20251006_183953
analysis_results/RUFF_FINDINGS_20251006_191744
```

**Ruff Analysis Sessions:**
- Session 1 (17:51:20): Initial comprehensive lint
- Session 2 (17:54:04): Post-cleanup analysis
- Session 3 (18:34:42): Mid-fix validation
- Session 4 (18:39:53): Near-complete validation
- Session 5 (19:17:44): Final lint verification

### Vulture Dead Code Detection

Unused code and import detection across analysis sessions.

```{toctree}
:maxdepth: 1
:caption: Vulture Findings

analysis_results/VULTURE_FINDINGS_20251006_175120
analysis_results/VULTURE_FINDINGS_20251006_175404
analysis_results/VULTURE_FINDINGS_20251006_183442
analysis_results/VULTURE_FINDINGS_20251006_183953
analysis_results/VULTURE_FINDINGS_20251006_191744
```

**Vulture Analysis Sessions:**
- Session 1 (17:51:20): Baseline dead code analysis
- Session 2 (17:54:04): Post-initial-cleanup
- Session 3 (18:34:42): Mid-cleanup verification
- Session 4 (18:39:53): Near-complete dead code removal
- Session 5 (19:17:44): Final dead code verification

---

## Debugging Workflows

Comprehensive multi-server debugging and validation workflows.

```{toctree}
:maxdepth: 2
:caption: Debugging Workflows

workflows/CODE_QUALITY_ANALYSIS_PLAN
workflows/complete-debugging-workflow
workflows/VALIDATION_WORKFLOW
```

### Workflow Documentation

| Workflow | Purpose | MCP Servers Used |
|----------|---------|------------------|
| [Code Quality Analysis Plan](workflows/CODE_QUALITY_ANALYSIS_PLAN.md) | Systematic code quality improvement plan | Ruff, Vulture |
| [Complete Debugging Workflow](workflows/complete-debugging-workflow.md) | End-to-end multi-server debugging procedure | Ruff, Vulture, Pandas, Playwright |
| [Validation Workflow](workflows/VALIDATION_WORKFLOW.md) | Automated validation and quality gates | Ruff, Vulture, pytest |

---

## Analysis Results Summary

### Code Quality Improvements (2025-10-06)

**Ruff Findings Progression:**
```
Session 1 → Session 5
Initial Issues → 95%+ Resolution
```

**Key Improvements:**
1. Import organization and optimization
2. Type hint coverage enhancement (≥95% critical components)
3. Unused variable and import removal
4. PEP 8 compliance fixes
5. Code style consistency

**Vulture Findings Progression:**
```
Session 1 → Session 5
Baseline Dead Code → Minimal Remaining
```

**Key Improvements:**
1. Unused function removal (80%+ reduction)
2. Unused import elimination
3. Dead code path removal
4. Unused class and method cleanup
5. Import optimization

---

## MCP Integration Architecture

### Server Configuration

MCP servers are configured in `.claude/settings.local.json`:

```json
{
  "mcpServers": {
    "ruff": { "command": "uvx", "args": ["mcp-server-ruff"] },
    "vulture": { "command": "uv", "args": ["run", "mcp-server-vulture"] },
    "pandas": { "command": "uv", "args": ["run", "mcp-server-pandas"] },
    "playwright": { "command": "npx", "args": ["-y", "@executeautomation/playwright-mcp-server"] }
  }
}
```

### Workflow Integration

1. **Automated Code Quality**
   - Pre-commit hooks run ruff linting
   - CI/CD pipeline executes vulture dead code detection
   - Continuous quality monitoring

2. **Interactive Debugging**
   - Use MCP servers during development
   - Real-time linting feedback
   - Dead code detection on-demand

3. **Testing & Validation**
   - Pandas MCP for statistical analysis
   - Playwright MCP for dashboard testing
   - Integrated validation workflows

---

## Usage Examples

### Ruff Linting

```bash
# Run ruff via MCP
# (Executed automatically via MCP server integration)

# Manual ruff check
ruff check src/ tests/

# Ruff fix with auto-corrections
ruff check --fix src/
```

### Vulture Dead Code Detection

```bash
# Run vulture via MCP
# (Executed automatically via MCP server integration)

# Manual vulture check
vulture src/ tests/

# Vulture with minimum confidence threshold
vulture src/ --min-confidence 80
```

### Pandas Data Analysis

```python
# Example: Analyze PSO convergence data via Pandas MCP
import pandas as pd

# Load PSO optimization results
df = pd.read_csv('optimization_results/pso_convergence.csv')

# Statistical analysis
print(df.describe())
print(df['cost'].min(), df['cost'].mean(), df['cost'].std())
```

### Playwright Dashboard Testing

```python
# Example: Automated Streamlit dashboard testing
# (Via Playwright MCP server)
# See: .claude/commands/test-browser.sh
```

---

## Troubleshooting

### Common MCP Issues

| Issue | Solution | Reference |
|-------|----------|-----------|
| MCP server not found | Check installation log | [Installation Log](INSTALLATION_LOG.md) |
| Connection timeout | Verify server configuration | [README](README.md) |
| Missing dependencies | Install via uv/uvx/npx | [Quick Reference](QUICK_REFERENCE.md) |
| Server crash | Check logs, restart Claude Code | [MISSING_SERVERS_RESEARCH](MISSING_SERVERS_RESEARCH.md) |

### Quality Gate Failures

| Failure | Diagnosis | Fix |
|---------|-----------|-----|
| Ruff linting errors | Review ruff findings reports | Apply auto-fixes, manual corrections |
| Vulture false positives | Whitelist necessary code | Update vulture config |
| Coverage regression | Run pytest with coverage | Add missing tests |
| Type hint coverage <95% | Run mypy | Add type annotations |

---

## External Links

- **[Main Documentation Hub](../index.md)** - Complete project documentation
- **[Testing Documentation](../testing/index.md)** - Quality assurance and validation
- **[Code Quality Standards](../.claude/documentation_quality.md)** - Documentation quality standards
- **[Agent Orchestration](../.claude/agent_orchestration.md)** - Multi-agent workflow coordination

---

## Best Practices

### MCP Server Usage

1. **Always use MCP servers for code quality** - Automated, consistent analysis
2. **Review findings incrementally** - Address issues session-by-session
3. **Combine multiple servers** - Ruff + Vulture for comprehensive coverage
4. **Integrate with CI/CD** - Automated quality gates

### Code Quality Workflow

```
1. Write code
2. Run ruff via MCP (linting)
3. Run vulture via MCP (dead code detection)
4. Fix issues iteratively
5. Validate with pytest
6. Commit with clean quality report
```

### Debugging Strategy

1. **Start with complete-debugging-workflow** - Comprehensive multi-server analysis
2. **Use CODE_QUALITY_ANALYSIS_PLAN** - Systematic improvement strategy
3. **Follow VALIDATION_WORKFLOW** - Ensure quality gates pass
4. **Document findings** - Add to analysis_results/

---

**Last Updated**: 2025-10-10
**Active MCP Servers**: 4 (Ruff, Vulture, Pandas, Playwright)
**Analysis Sessions**: 5 major quality improvement sessions (2025-10-06)
**Documentation Status**: Complete (18 files, all accessible via toctree navigation)

---

**MCP Resources:**
- Getting Started: [README](README.md)
- Quick Commands: [Quick Reference](QUICK_REFERENCE.md)
- Complete Workflow: [Complete Debugging Workflow](workflows/complete-debugging-workflow.md)
---

**Navigation**: Return to [Master Navigation Hub](../NAVIGATION.md) | Browse all [Documentation Categories](../index.md)
