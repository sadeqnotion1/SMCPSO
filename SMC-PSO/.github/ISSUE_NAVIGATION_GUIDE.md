# GitHub Issues Navigation Guide
## DIP SMC PSO Project Issue Management

> 🎯 **Quick Access**: [View All Issues](https://github.com/theSadeQ/dip-smc-pso/issues) | [Create New Issue](https://github.com/theSadeQ/dip-smc-pso/issues/new/choose)

---

## 📊 Issue Dashboard & Quick Navigation

### 🚨 Critical Issues (Immediate Attention Required)
```bash
# View all critical issues
gh issue list --search "label:critical state:open"

# Web link for critical issues
```
[**🔗 View Critical Issues**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Acritical)

**Expected Critical Issues:**
- **Fault Detection Infrastructure Failures** (Safety-critical systems)
- **Sliding Mode Control Mathematical Property Failures** (Stability violations)
- **Configuration Validation System Failures** (Safety parameter validation)

### ⚠️ High Priority Issues (4-8 Hour Response)
```bash
# View high priority issues
gh issue list --search "label:high state:open"
```
[**🔗 View High Priority Issues**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Ahigh)

**Expected High Priority Issues:**
- **PSO Integration System Failures** (Optimization broken)
- **Controller Factory Integration Failures** (Architecture issues)
- **Adaptive SMC Algorithm Core Failures** (Control algorithm problems)

### 🔧 Medium Priority Issues (16 Hour Response)
```bash
# View medium priority issues
gh issue list --search "label:medium state:open"
```
[**🔗 View Medium Priority Issues**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Amedium)

**Expected Medium Priority Issues:**
- **Test Infrastructure Configuration Problems** (Development workflow)
- **Performance Benchmark Test Failures** (Performance monitoring)
- **Application Layer Integration Failures** (UI/CLI issues)

---

## 🏷️ Search by Category

### 🎯 Stability & Safety Issues
```bash
# Command line search
gh issue list --search "label:stability OR label:safety state:open"

# Advanced stability search
gh issue list --search "label:stability label:critical state:open"
```
[**🔗 Stability Issues**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Astability) | [**🔗 Safety Issues**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Asafety)

**Key Stability Categories:**
- `fault-detection` - Fault detection system issues
- `lyapunov` - Lyapunov stability analysis problems
- `mathematical` - Core mathematical algorithm failures
- `sliding-mode` - Sliding mode control specific issues

### 🔄 Optimization & PSO Issues
```bash
# PSO and optimization issues
gh issue list --search "label:pso OR label:optimization OR label:convergence state:open"
```
[**🔗 PSO Issues**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Apso) | [**🔗 Convergence Issues**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Aconvergence)

**Key Optimization Categories:**
- `pso` - Particle Swarm Optimization specific
- `convergence` - Convergence and optimization failures
- `parameter-bounds` - Parameter bounds and constraints
- `optimization` - General optimization issues

### 🏗️ Implementation & Architecture Issues
```bash
# Implementation and architecture problems
gh issue list --search "label:implementation OR label:architecture OR label:factory state:open"
```
[**🔗 Implementation Issues**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Aimplementation) | [**🔗 Architecture Issues**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Aarchitecture)

**Key Implementation Categories:**
- `factory` - Controller factory pattern issues
- `integration` - Component integration problems
- `memory` - Memory management and leaks
- `testing` - Test infrastructure problems

### 📊 Performance & Benchmarks
```bash
# Performance and benchmark issues
gh issue list --search "label:performance OR label:benchmarks OR label:regression state:open"
```
[**🔗 Performance Issues**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Aperformance) | [**🔗 Benchmark Issues**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Abenchmarks)

**Key Performance Categories:**
- `benchmarks` - Performance benchmark failures
- `regression` - Performance regression detection
- `memory` - Memory usage optimization
- `slow-execution` - Execution time issues

---

## 🎛️ Search by Controller Type

### 🔍 Controller-Specific Issues
```bash
# Classical SMC issues
gh issue list --search "label:classical-smc state:open"

# Adaptive SMC issues
gh issue list --search "label:adaptive-smc state:open"

# All SMC variants
gh issue list --search "classical-smc OR adaptive-smc OR sta-smc OR hybrid-smc state:open"
```

**Controller-Specific Links:**
- [**🔗 Classical SMC**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Aclassical-smc)
- [**🔗 Adaptive SMC**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Aadaptive-smc)
- [**🔗 Super-Twisting SMC**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Asta-smc)
- [**🔗 Hybrid Adaptive STA-SMC**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Ahybrid-smc)

---

## 📁 Search by Source/Test File

### 🧪 Test-Related Issues
```bash
# Issues related to specific test files
gh issue list --search "test_controllers state:open"
gh issue list --search "test_benchmarks state:open"
gh issue list --search "test_analysis state:open"
```

**Test Category Links:**
- [**🔗 Controller Tests**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+test_controllers)
- [**🔗 Benchmark Tests**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+test_benchmarks)
- [**🔗 Analysis Tests**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+test_analysis)

### 📋 Source Documentation Issues
```bash
# Issues created from prompt folder documentation
gh issue list --search "MIGRATED OR prompt/ state:open"
```
[**🔗 Migrated/Documented Issues**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+MIGRATED+OR+prompt%2F)

---

## 🚀 Quick Actions & Workflows

### 📝 Create New Issues

**Using GitHub Web Interface:**
1. [**🔗 Create New Issue**](https://github.com/theSadeQ/dip-smc-pso/issues/new/choose)
2. Choose appropriate template:
   - 🔴 **Control Systems - Stability Issue**
   - 🟡 **Control Systems - Performance Issue**
   - 🔵 **PSO Optimization - Convergence Issue**
   - 🟠 **PSO Optimization - Parameter Bounds Issue**
   - 🐛 **Implementation Bug**
   - ✨ **Feature Request / Enhancement**

**Using Command Line:**
```bash
# Critical stability issue
.github/scripts/create_issue.sh -t stability -p critical -T "Issue title" -d "Description"

# Performance issue
.github/scripts/create_issue.sh -t performance -p high -T "Issue title" -d "Description"

# PSO convergence issue
.github/scripts/create_issue.sh -t convergence -p critical -T "Issue title" -d "Description"
```

### 🔍 Advanced Search Examples

**Complex Searches:**
```bash
# Open critical issues in controller tests
gh issue list --search "label:critical test_controllers state:open"

# High priority PSO issues assigned to specific user
gh issue list --search "label:high label:pso assignee:username state:open"

# Recent issues (last 7 days)
gh issue list --search "created:>$(date -d '7 days ago' '+%Y-%m-%d') state:open"

# Issues with no assignee (need attention)
gh issue list --search "no:assignee state:open"
```

**Search by Text Content:**
```bash
# Search in issue titles and descriptions
gh issue list --search "Lyapunov state:open"
gh issue list --search "boundary layer state:open"
gh issue list --search "fault detection state:open"
```

### 📊 Issue Analytics & Reporting

**Quick Statistics:**
```bash
# Count issues by priority
gh issue list --search "label:critical state:open" --json number | jq '. | length'
gh issue list --search "label:high state:open" --json number | jq '. | length'
gh issue list --search "label:medium state:open" --json number | jq '. | length'

# Issues by controller type
gh issue list --search "label:classical-smc state:open" --json number | jq '. | length'
gh issue list --search "label:adaptive-smc state:open" --json number | jq '. | length'
```

**Generate Reports:**
```bash
# Export all issues to CSV
gh issue list --state all --json number,title,state,labels,createdAt --jq '.[] | [.number, .title, .state, (.labels | map(.name) | join(";")), .createdAt] | @csv'

# Issues created this week
gh issue list --search "created:>$(date -d '7 days ago' '+%Y-%m-%d')" --json number,title,createdAt
```

---

## 🔧 Issue Management Commands

### ✅ Closing and Managing Issues

**Close Issues:**
```bash
# Close issue with resolution
gh issue close 123 --comment "Fixed by implementing new stability analysis in PR #456"

# Close multiple related issues
gh issue list --search "label:resolved" --json number --jq '.[].number' | xargs -I {} gh issue close {}
```

**Update Issues:**
```bash
# Add labels
gh issue edit 123 --add-label "needs-review,high-priority"

# Remove labels
gh issue edit 123 --remove-label "needs-investigation"

# Assign issues
gh issue edit 123 --assignee @username

# Update milestone
gh issue edit 123 --milestone "v1.0-stability-fixes"
```

### 🏷️ Bulk Operations

**Mass Label Updates:**
```bash
# Add "needs-review" to all critical issues
gh issue list --search "label:critical state:open" --json number --jq '.[].number' | xargs -I {} gh issue edit {} --add-label "needs-review"

# Assign all PSO issues to optimization team member
gh issue list --search "label:pso state:open" --json number --jq '.[].number' | xargs -I {} gh issue edit {} --assignee @pso-expert
```

---

## 📱 Mobile & Web Access

### 🌐 Quick Web Links

**Priority Dashboards:**
- [**🚨 Critical Issues**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Acritical)
- [**⚠️ High Priority**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Ahigh)
- [**📋 All Open Issues**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen)
- [**✅ Recently Closed**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aclosed+sort%3Aupdated-desc)

**Category Dashboards:**
- [**🎯 Stability Issues**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Astability)
- [**🔄 PSO Issues**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Apso)
- [**🏗️ Architecture Issues**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Aarchitecture)
- [**📊 Performance Issues**](https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Aperformance)

### 📱 GitHub Mobile App

**Quick Actions on Mobile:**
1. Install [GitHub Mobile App](https://github.com/mobile)
2. Navigate to **theSadeQ/dip-smc-pso** repository
3. Tap **Issues** tab
4. Use **Filters** to find specific issue types
5. **Subscribe** to critical issues for notifications

---

## 🔔 Notifications & Monitoring

### 📧 Email Notifications

**Setup Email Alerts:**
1. Go to [Notification Settings](https://github.com/settings/notifications)
2. Configure repository-specific notifications
3. Enable email for:
   - Issues assigned to you
   - Issues you're participating in
   - Critical/High priority label additions

**Watch Repository:**
- [**🔗 Watch Repository**](https://github.com/theSadeQ/dip-smc-pso/subscription) for issue notifications

### 🤖 Automated Monitoring

**GitHub Actions Integration:**
- Automated issue creation from test failures
- Daily health check reports
- Performance regression alerts
- Critical issue notifications

**Custom Notification Rules:**
```bash
# Create GitHub CLI alias for monitoring
echo "alias check-critical='gh issue list --search \"label:critical state:open\" && echo \"$(gh issue list --search \"label:critical state:open\" --json number | jq \". | length\") critical issues open\"'" >> ~/.bashrc
```

---

## 📚 Documentation & Training

### 📖 Related Documentation
- [**🔗 Issues Workflow Guide**](.github/ISSUES_WORKFLOW.md) - Complete workflow documentation
- [**🔗 Issue Templates**](.github/ISSUE_TEMPLATE/) - Standard issue templates
- [**🔗 Implementation Strategy**](.github/scripts/implementation_strategy.md) - Detailed implementation guide

### 🎓 Quick Training

**New Team Member Onboarding:**
1. **Read** this navigation guide
2. **Install** GitHub CLI: `winget install GitHub.cli`
3. **Authenticate**: `gh auth login`
4. **Test** issue creation: `.github/scripts/create_issue.sh -t implementation -p low -T "Test issue"`
5. **Practice** searching: `gh issue list --search "state:open"`

**Daily Workflow:**
```bash
# Morning check
check-critical  # Custom alias (see above)
gh issue list --search "assignee:@me state:open"

# Work on assigned issues
gh issue view 123  # Read issue details
gh issue edit 123 --add-label "in-progress"

# End of day update
gh issue comment 123 --body "Progress update: Fixed boundary layer computation, testing remaining..."
```

---

## 🚨 Emergency Procedures

### 🔥 Critical Issue Response

**When a CRITICAL issue is detected:**

1. **Immediate Assessment** (< 15 minutes):
   ```bash
   gh issue view [ISSUE_NUMBER]  # Read full details
   gh issue edit [ISSUE_NUMBER] --add-label "investigating"
   ```

2. **Team Notification** (< 30 minutes):
   ```bash
   gh issue comment [ISSUE_NUMBER] --body "@team Critical issue under investigation. ETA for initial assessment: [TIME]"
   ```

3. **Resolution Tracking** (ongoing):
   ```bash
   # Regular updates
   gh issue comment [ISSUE_NUMBER] --body "Status update: [PROGRESS]"

   # When resolved
   gh issue close [ISSUE_NUMBER] --comment "✅ RESOLVED: [SOLUTION SUMMARY]"
   ```

### 📞 Escalation Path

**Critical Stability Issues (4-hour SLA):**
1. Assign to senior control systems engineer
2. Notify project lead if not resolved in 2 hours
3. Consider rollback if in production

**High Priority Issues (8-hour SLA):**
1. Assign to appropriate specialist
2. Daily standup review if not resolved in 24 hours

---

🤖 **This navigation guide was generated by [Claude Code](https://claude.ai/code)**

📅 **Last Updated**: Check repository commit history for updates