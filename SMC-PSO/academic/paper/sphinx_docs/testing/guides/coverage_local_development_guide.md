#==========================================================================================\\\
#============== docs/testing/coverage_local_development_guide.md =========================\\\
#==========================================================================================\\\

# Coverage Local Development Integration Guide
**Issue #9 - Local Development Workflow for Coverage Quality Gates** > **🎯 Mission**: Streamlined local development integration for coverage validation and quality gate enforcement

---

## 🚀 Quick Start for Developers ### 1-Minute Coverage Check

```bash
# Fast coverage validation (< 30 seconds)
python -m pytest tests/ --cov=src --cov-report=term-missing --tb=no -q # Quality gate status check
python scripts/coverage_validator.py --coverage-xml coverage.xml 2>/dev/null && echo "✅ Gates passed" || echo "❌ Gates failed"
``` ### Pre-Commit Coverage Validation

```bash
# Add to .git/hooks/pre-commit
python -m pytest tests/ --cov=src --cov-fail-under=85 --tb=no -q || exit 1
```

---

## 🛠️ Development Environment Setup ### Required Dependencies

```bash
# Install coverage dependencies
pip install pytest-cov coverage[toml] # Verify installation
python -m pytest --version
python -m coverage --version
``` ### IDE Integration #### VS Code Integration

**Add to `.vscode/settings.json`:**
```json
{ "python.testing.pytestArgs": [ "tests/", "--cov=src", "--cov-report=html:htmlcov", "--cov-report=xml:coverage.xml" ], "python.testing.cwd": "${workspaceFolder}", "files.watcherExclude": { "**/htmlcov/**": true, "**/.coverage": true, "**/coverage.xml": true }
}
``` #### PyCharm Integration

1. **Settings → Tools → Python Integrated Tools → Testing** - Default test runner: pytest - Additional arguments: `--cov=src --cov-report=html`
2. **Run/Debug Configurations** - Add pytest configuration with coverage enabled

---

## 📊 Local Coverage Workflows ### Daily Development Workflow #### 1. Feature Development Cycle

```bash
# Start development
git checkout -b feature/my-feature # Develop with continuous coverage feedback
python -m pytest tests/test_my_module.py --cov=src/my_module --cov-report=term-missing -v # Iterative improvement
while [[ $(python -m pytest tests/test_my_module.py --cov=src/my_module --cov-report=json -q && python -c "import json; print(json.load(open('coverage.json'))['totals']['percent_covered'])") < 95 ]]; do echo "Adding more tests..." # Add tests, repeat
done
``` #### 2. Pre-Merge Validation

```bash
# Full coverage validation before PR
python -m pytest tests/ --cov=src --cov-report=xml:coverage.xml
python scripts/coverage_validator.py --coverage-xml coverage.xml --verbose --fail-below-threshold # Generate PR-ready coverage report
python -m pytest tests/ --cov=src --cov-report=html:htmlcov --cov-report=json:coverage.json
``` ### Component-Specific Development #### Controller Development

```bash
# Controller development workflow
python -m pytest tests/test_controllers/ --cov=src/controllers --cov-report=html:controller_coverage/ # Safety-critical controller validation (requires 100%)
python -m pytest tests/test_controllers/smc/core/ --cov=src/controllers/smc/core --cov-fail-under=100
``` #### Optimization Development

```bash
# PSO optimization development
python -m pytest tests/test_optimization/ --cov=src/optimizer --cov-report=html:optimization_coverage/ # Mathematical property validation
python -m pytest tests/test_optimization/ -k "convergence or stability" --cov=src/optimizer -v
```

---

## 🔧 Local Quality Gate Validation ### Individual Gate Testing #### Infrastructure Health Check

```bash
# Test collection validation
python -m pytest --collect-only -q
echo "Exit code: $?" # Dependency validation
python -c "import pytest, coverage; print('✅ Dependencies OK')" 2>/dev/null || echo "❌ Missing dependencies"
``` #### Safety-Critical Coverage (100% Required)

```bash
# safety-critical validation
python -m pytest tests/test_controllers/smc/core/ tests/test_controllers/base/ \ --cov=src/controllers/smc/core --cov=src/controllers/base \ --cov-fail-under=100 \ --cov-report=html:safety_critical_coverage/ \ --cov-report=json:safety_coverage.json # Validate 100% achievement
python -c "
import json
with open('safety_coverage.json') as f: data = json.load(f) coverage = data['totals']['percent_covered'] print(f'Safety-critical coverage: {coverage}%') exit(0 if coverage == 100.0 else 1)
"
``` #### Critical Components (≥95% Required)

```bash
# Critical component validation
CRITICAL_COMPONENTS=( "tests/test_controllers/factory/" "tests/test_optimization/" "tests/test_core/"
) for component in "${CRITICAL_COMPONENTS[@]}"; do echo "Validating: $component" python -m pytest "$component" --cov="${component/tests\/test_/src/}" --cov-fail-under=95 -q
done
``` ### Local Gate Status Dashboard

```bash
#!/bin/bash
# local_coverage_status.sh
echo "🔵 Local Coverage Quality Gate Status"
echo "=====================================" # Infrastructure
python -m pytest --collect-only -q > /dev/null 2>&1
echo "📊 Infrastructure Health: $([ $? -eq 0 ] && echo '✅ PASS' || echo '❌ FAIL')" # Overall Coverage
OVERALL_COV=$(python -m pytest tests/ --cov=src --cov-report=json:temp_cov.json -q 2>/dev/null && python -c "import json; print(f\"{json.load(open('temp_cov.json'))['totals']['percent_covered']:.1f}\")" 2>/dev/null || echo "0.0")
echo "📈 Overall Coverage: $OVERALL_COV% $([ $(echo "$OVERALL_COV >= 85" | bc -l) -eq 1 ] && echo '✅ PASS' || echo '❌ FAIL')" # Safety-Critical
python -m pytest tests/test_controllers/smc/core/ --cov=src/controllers/smc/core --cov-fail-under=100 -q > /dev/null 2>&1
echo "🔴 Safety-Critical: $([ $? -eq 0 ] && echo '✅ PASS (100%)' || echo '❌ FAIL (<100%)')" # Critical Components
python -m pytest tests/test_controllers/factory/ tests/test_optimization/ tests/test_core/ --cov=src/controllers/factory --cov=src/optimizer --cov=src/core --cov-fail-under=95 -q > /dev/null 2>&1
echo "🟠 Critical Components: $([ $? -eq 0 ] && echo '✅ PASS (≥95%)' || echo '❌ FAIL (<95%)')" # Cleanup
rm -f temp_cov.json
```

---

## ⚡ Performance-Optimized Local Testing ### Fast Coverage Collection

```bash
# Minimal coverage for rapid feedback (< 10 seconds)
python -m pytest tests/test_specific_module.py --cov=src/specific_module --cov-report=term -x # Parallel execution (if tests are thread-safe)
python -m pytest tests/ --cov=src -n auto --cov-report=term-missing # Skip slow tests during development
python -m pytest tests/ --cov=src -m "not slow" --cov-report=term-missing
``` ### Incremental Coverage Analysis

```bash
# Track coverage changes against git baseline
coverage run -m pytest tests/
coverage report --skip-covered --show-missing # Compare coverage with main branch
git checkout main
coverage run -m pytest tests/ && coverage report --format=json > main_coverage.json
git checkout feature/my-feature
coverage run -m pytest tests/ && coverage report --format=json > feature_coverage.json # Calculate coverage diff
python -c "
import json
with open('main_coverage.json') as f: main = json.load(f)
with open('feature_coverage.json') as f: feature = json.load(f)
diff = feature['totals']['percent_covered'] - main['totals']['percent_covered']
print(f'Coverage change: {diff:+.2f}%')
"
```

---

## 🐛 Local Development Debugging ### Coverage Collection Issues #### Missing Coverage Data

```bash
# Debug coverage collection
export COVERAGE_DEBUG=trace
python -m pytest tests/test_specific.py --cov=src/specific --cov-report=term -v # Validate source file detection
python -c "
import coverage
cov = coverage.Coverage()
cov.start()
cov.stop()
print('Detected source files:', list(cov.get_data().measured_files()))
"
``` #### Unexpected Low Coverage

```bash
# Identify uncovered lines with context
python -m pytest tests/ --cov=src --cov-report=annotate:annotate_coverage/ # View annotate files with line-by-line coverage
ls annotate_coverage/
cat annotate_coverage/src_controllers_classic_smc_py.txt
``` ### Quality Gate Failures #### Infrastructure Failures

```bash
# Test discovery debugging
python -m pytest --collect-only -v 2>&1 | grep -E "(ERROR|FAILED|ImportError)" # Import path validation
python -c "
import sys
sys.path.insert(0, 'src')
try: import controllers.factory print('✅ Import successful')
except Exception as e: print(f'❌ Import failed: {e}')
"
``` #### Coverage Threshold Failures

```bash
# Detailed gap analysis
python scripts/coverage_validator.py --coverage-xml coverage.xml --verbose | grep -A 5 "FAIL" # Component-specific analysis
python -m pytest tests/test_controllers/ --cov=src/controllers --cov-report=missing | grep "TOTAL"
```

---

## 📈 Coverage Improvement Workflows ### Systematic Coverage Enhancement #### 1. Gap Identification

```bash
# Generate missing coverage report
python -m pytest tests/ --cov=src --cov-report=missing > missing_coverage.txt # Extract uncovered lines
grep -E "src/.*py.*[0-9]" missing_coverage.txt | head -10
``` #### 2. Test Development Prioritization

```bash
# Priority matrix for test development
python -c "
import json
with open('coverage.json') as f: data = json.load(f) files = [(filename, file_data['summary']['percent_covered']) for filename, file_data in data['files'].items()]
files.sort(key=lambda x: x[1]) print('Lowest coverage files (priority for testing):')
for filename, coverage in files[:10]: print(f'{coverage:5.1f}% - {filename}')
"
``` #### 3. Mathematical Property Testing

```bash
# Add theoretical validation tests
python -m pytest tests/test_analysis/test_stability.py -v --cov=src/controllers --cov-report=term-missing # Property-based testing integration
python -m pytest tests/ -k "hypothesis" --cov=src --cov-report=term-missing
``` ### Coverage Quality Enhancement #### Branch Coverage Analysis

```bash
# branch coverage
python -m pytest tests/ --cov=src --cov-branch --cov-report=html:branch_coverage/ # Identify uncovered branches
python -m pytest tests/ --cov=src --cov-branch --cov-report=missing | grep -E "->|branch"
``` #### Edge Case Coverage

```bash
# Focus on error handling paths
python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing -k "error or exception or invalid" # Boundary condition testing
python -m pytest tests/ --cov=src --cov-report=html -k "boundary or limit or edge"
```

---

## 🔄 Continuous Coverage Monitoring ### Git Hook Integration #### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
echo "🔍 Pre-commit coverage validation..." # Quick coverage check
python -m pytest tests/ --cov=src --cov-fail-under=85 --tb=no -q
COVERAGE_STATUS=$? if [ $COVERAGE_STATUS -ne 0 ]; then echo "❌ Coverage below 85% threshold. Commit blocked." echo "📊 Run: python -m pytest tests/ --cov=src --cov-report=term-missing" exit 1
fi echo "✅ Coverage validation passed."
exit 0
``` #### Post-Merge Coverage Tracking

```bash
#!/bin/bash
# .git/hooks/post-merge
echo "📈 Post-merge coverage analysis..." # Generate coverage baseline
python -m pytest tests/ --cov=src --cov-report=json:baseline_coverage.json -q # Archive coverage history
mkdir -p .coverage_history
cp baseline_coverage.json ".coverage_history/coverage_$(date +%Y%m%d_%H%M%S).json"
``` ### Coverage Trend Analysis

```bash
# Weekly coverage trend
python -c "
import json, glob, os
from datetime import datetime files = sorted(glob.glob('.coverage_history/coverage_*.json'))
for file in files[-7:]: # Last 7 coverage snapshots with open(file) as f: data = json.load(f) timestamp = os.path.basename(file).split('_')[1:3] coverage = data['totals']['percent_covered'] print(f'{timestamp[0]}_{timestamp[1]}: {coverage:.1f}%')
"
```

---

## 🎯 Success Metrics & KPIs ### Local Development Metrics | **Metric** | **Target** | **Frequency** |

|------------|------------|---------------|
| Daily Coverage Check | >85% | Each commit |
| Feature Branch Coverage | +0% (no regression) | Before PR |
| Safety-Critical Coverage | 100% | Before merge |
| Coverage Collection Time | <30s | Each run |
| Quality Gate Pass Rate | >95% | Weekly | ### Development Efficiency Indicators
```bash
# Time-to-coverage metrics
time python -m pytest tests/ --cov=src --cov-report=term-missing # Coverage development velocity
git log --oneline --since="1 week ago" | grep -i "test\|coverage" | wc -l
```

---

**🎯 Issue #9 Local Development Integration**: This guide provides streamlined local development workflows for coverage quality gate enforcement, enabling efficient development cycles while maintaining the sophisticated 85%/95%/100% coverage framework. **🔗 Repository**: https://github.com/theSadeQ/dip-smc-pso.git
**📋 Documentation Version**: 1.0.0 - Issue #9 Local Development Integration
**🤖 Generated with**: [Claude Code](https://claude.ai/code) - Documentation Expert Agent