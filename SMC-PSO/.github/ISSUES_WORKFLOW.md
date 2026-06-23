# GitHub Issues Workflow - DIP SMC PSO Project

## Overview

This document describes the GitHub Issues workflow that replaces the local `problem-tracking/` directory system. The new workflow provides better collaboration, integration with development workflows, and centralized issue management.

## 🎯 Quick Start

### Create Issues

**Using GitHub Web Interface:**
1. Go to https://github.com/theSadeQ/dip-smc-pso/issues
2. Click "New issue"
3. Choose appropriate template:
   - 🔴 Control Systems - Stability Issue
   - 🟡 Control Systems - Performance Issue
   - 🔵 PSO Optimization - Convergence Issue
   - 🟠 PSO Optimization - Parameter Bounds Issue
   - 🐛 Implementation Bug
   - ✨ Feature Request / Enhancement

**Using Command Line:**
```bash
# Windows
.github\scripts\create_issue.bat -t stability -p critical -T "Lyapunov violation in classical SMC" -c classical_smc

# Linux/macOS/Git Bash
.github/scripts/create_issue.sh -t stability -p critical -T "Lyapunov violation in classical SMC" -c classical_smc
```

### Manage Issues

```bash
# List all open issues
.github/scripts/manage_issues.sh list

# List stability issues only
.github/scripts/manage_issues.sh list --stability

# Show issue details
.github/scripts/manage_issues.sh show 5

# Close an issue
.github/scripts/manage_issues.sh close 3 "Fixed by implementing new gain bounds"

# Search issues
.github/scripts/manage_issues.sh search "overshoot"

# Show statistics
.github/scripts/manage_issues.sh stats
```

## 📋 Issue Categories & Templates

### 🔴 Stability Issues (CRITICAL)
**Response Time**: < 4 hours

Use for:
- Lyapunov stability violations
- Reaching phase instability
- Sliding phase instability
- Excessive chattering
- Parameter adaptation divergence

**Labels**: `stability`, `control-systems`, `critical`

### 🟡 Performance Issues (HIGH)
**Response Time**: < 8 hours

Use for:
- Excessive overshoot (>20%)
- Extended settling time
- Non-zero static error
- Poor disturbance rejection
- High parameter sensitivity

**Labels**: `performance`, `control-systems`, `high`

### 🔵 PSO Convergence Issues (CRITICAL)
**Response Time**: < 4 hours

Use for:
- Premature convergence
- Non-convergence/stagnation
- Convergence to infeasible solutions
- Loss of swarm diversity

**Labels**: `convergence`, `optimization`, `pso`, `critical`

### 🟠 PSO Parameter Bounds Issues (HIGH)
**Response Time**: < 6 hours

Use for:
- Bounds violations
- Restrictive search space
- Boundary clustering
- Infeasible parameter combinations

**Labels**: `parameter-bounds`, `optimization`, `pso`, `high`

### 🐛 Implementation Bugs (MEDIUM)
**Response Time**: < 16 hours

Use for:
- Controller factory problems
- SMC variant implementation issues
- Numerical implementation errors
- Configuration problems

**Labels**: `bug`, `implementation`, `medium`

### ✨ Feature Requests (LOW)
**Response Time**: Next development cycle

Use for:
- New controller algorithms
- Optimization enhancements
- UI improvements
- Documentation requests

**Labels**: `enhancement`, `feature-request`, `low`

## 🏷️ Label System

### Priority Labels
- `critical` - System instability, safety violations (🚨)
- `high` - Performance degradation, spec violations (⚠️)
- `medium` - Minor issues, code quality (🟡)
- `low` - Enhancements, non-critical improvements (🟢)

### Category Labels
- `stability` - Critical stability issues
- `performance` - Performance problems
- `control-systems` - Controller-related issues
- `optimization` - Optimization algorithm issues
- `pso` - PSO-specific problems
- `convergence` - Convergence failures
- `parameter-bounds` - Parameter space issues
- `implementation` - Code/integration bugs
- `migrated` - Issues migrated from local tracking

### Controller Labels
- `classical-smc` - Classical sliding mode control
- `sta-smc` - Super-twisting SMC
- `adaptive-smc` - Adaptive SMC
- `hybrid-sta-smc` - Hybrid adaptive STA-SMC
- `swing-up-smc` - Swing-up SMC
- `mpc` - Model predictive control

## 🔄 Workflow Integration

### With Simulation Commands
```bash
# Report issues found during simulation
python simulate.py --ctrl classical_smc --plot
# If issues found, create issue:
.github/scripts/create_issue.sh -t stability -T "Found instability in classical SMC" -r "python simulate.py --ctrl classical_smc --plot"
```

### With PSO Optimization
```bash
# Report PSO convergence issues
python simulate.py --ctrl adaptive_smc --run-pso --save gains.json
# If convergence fails:
.github/scripts/create_issue.sh -t convergence -T "PSO stagnation in adaptive SMC tuning" -r "python simulate.py --ctrl adaptive_smc --run-pso"
```

### With Testing
```bash
# Link test failures to issues
pytest tests/test_controllers/test_classical_smc.py
# Create issue referencing test:
.github/scripts/create_issue.sh -t implementation -T "Classical SMC test failure" -d "Test fails in test_classical_smc.py line 45"
```

## 📊 Migration from Local System

### What Was Migrated
✅ Problem taxonomies → Issue templates
✅ Category system → GitHub labels
✅ Priority levels → Priority labels
✅ CSV tracking → GitHub issues database
✅ Local workflows → CLI scripts

### What's Different
- **Centralized**: Issues visible to team/collaborators
- **Integrated**: Links with commits, PRs, and code
- **Searchable**: Full-text search across all issues
- **Notifications**: Automatic updates and mentions
- **History**: Complete audit trail and comments

### Migration Commands
```bash
# Export current GitHub issues
.github/scripts/manage_issues.sh export csv

# View migration statistics
.github/scripts/manage_issues.sh stats
```

## 🛠️ Advanced Usage

### Issue Automation
```bash
# Close issue with commit reference
git commit -m "Fix stability issue in classical SMC

Closes #15"

# Reference issues in commits
git commit -m "Improve PSO bounds validation

Related to #23"
```

### Bulk Operations
```bash
# Add labels to multiple issues
gh issue list --search "label:stability" --json number --jq '.[].number' | xargs -I {} gh issue edit {} --add-label "needs-review"

# Close all low priority completed issues
gh issue list --search "label:low state:open" --json number --jq '.[].number' | xargs -I {} gh issue close {}
```

### Integration with Development
```bash
# Create issue from failed test
pytest tests/ --tb=short | grep -A 5 "FAILED" | .github/scripts/create_issue.sh -t implementation -T "Test failure detected"

# Create performance issue from benchmark
pytest --benchmark-only | grep "slower" | .github/scripts/create_issue.sh -t performance -T "Performance regression detected"
```

## 📈 Benefits Over Local Tracking

1. **Team Collaboration**: Multiple people can work on issues
2. **Integration**: Automatic linking with PRs and commits
3. **Searchability**: Find issues across all history
4. **Notifications**: Stay updated on issue progress
5. **Analytics**: Built-in metrics and reporting
6. **Mobile Access**: Access issues from anywhere
7. **API Integration**: Automate with scripts and workflows
8. **Backup**: Cloud-hosted, version controlled

## 🔧 Troubleshooting

### Common Issues

**GitHub CLI not authenticated:**
```bash
gh auth login
```

**Permission denied on scripts:**
```bash
chmod +x .github/scripts/*.sh
```

**Labels not found:**
```bash
# Recreate labels
gh label create "stability" --description "Critical stability issues" --color "d73a4a"
```

**Template not loading:**
- Check `.github/ISSUE_TEMPLATE/` directory exists
- Verify YAML syntax in template files
- Clear browser cache and retry

### Getting Help
- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitHub Issues Guide](https://docs.github.com/en/issues)
- Project issues: https://github.com/theSadeQ/dip-smc-pso/issues

---

🤖 **This workflow was automatically generated and configured with [Claude Code](https://claude.ai/code)**