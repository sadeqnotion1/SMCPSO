#!/bin/bash
#==========================================================================================\
#================================ scripts/docs/validate_week1.sh ==========================\
#==========================================================================================\

# Week 1 Documentation Infrastructure Validation Script
# Runs comprehensive checks on documentation generator, templates, and generated docs

# Note: We don't use set -e so we can collect all validation results

# Color codes for output (if terminal supports it)
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    GREEN=''
    RED=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Project root detection
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

echo "=========================================="
echo "Week 1 Validation - Quick Start"
echo "=========================================="
echo ""

# Counter for pass/fail
TOTAL_CHECKS=0
PASSED_CHECKS=0

# Function to print result
check_result() {
    local name="$1"
    local result="$2"
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if [ "$result" = "pass" ]; then
        echo -e "${GREEN}✓${NC} $name"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${RED}✗${NC} $name"
    fi
}

# 1. File Structure Verification
echo -e "${BLUE}[1/6]${NC} Checking file structure..."
if [ -f "scripts/docs/generate_code_docs.py" ] && [ -f "scripts/docs/validate_code_docs.py" ]; then
    check_result "Core scripts exist" "pass"
else
    check_result "Core scripts exist" "fail"
fi

if [ -d "scripts/docs/templates" ] && [ -f "scripts/docs/templates/module_template.md" ]; then
    check_result "Template directory exists" "pass"
else
    check_result "Template directory exists" "fail"
fi

TEMPLATE_COUNT=$(find scripts/docs/templates -name "*.md" -type f | wc -l)
if [ "$TEMPLATE_COUNT" -ge 3 ]; then
    check_result "Required templates present (found $TEMPLATE_COUNT)" "pass"
else
    check_result "Required templates present (found $TEMPLATE_COUNT)" "fail"
fi

# 2. Generated Documentation Count
echo ""
echo -e "${BLUE}[2/6]${NC} Checking documentation count..."
DOC_COUNT=$(find docs/reference -name "*.md" -type f 2>/dev/null | wc -l)
echo "Documentation files: $DOC_COUNT (expected: ~337)"
if [ "$DOC_COUNT" -ge 330 ]; then
    check_result "Documentation files generated" "pass"
else
    check_result "Documentation files generated" "fail"
fi

MODULE_DIRS=$(find docs/reference -maxdepth 1 -type d 2>/dev/null | wc -l)
if [ "$MODULE_DIRS" -ge 15 ]; then
    check_result "Module directories created (found $MODULE_DIRS)" "pass"
else
    check_result "Module directories created (found $MODULE_DIRS)" "fail"
fi

# 3. Running Validation Script
echo ""
echo -e "${BLUE}[3/6]${NC} Running validation script..."
if python scripts/docs/validate_code_docs.py --check-all > /tmp/validation_output.txt 2>&1; then
    check_result "Validation script execution" "pass"

    # Check individual validation results
    if grep -q "\[PASS\].*Literalinclude Paths" /tmp/validation_output.txt; then
        check_result "Literalinclude paths valid" "pass"
    else
        check_result "Literalinclude paths valid" "fail"
    fi

    if grep -q "\[PASS\].*Coverage" /tmp/validation_output.txt; then
        check_result "Documentation coverage 100%" "pass"
    else
        check_result "Documentation coverage 100%" "fail"
    fi

    if grep -q "\[PASS\].*Toctree" /tmp/validation_output.txt; then
        check_result "Toctree references valid" "pass"
    else
        check_result "Toctree references valid" "fail"
    fi

    if grep -q "\[PASS\].*Syntax" /tmp/validation_output.txt; then
        check_result "No syntax errors" "pass"
    else
        check_result "No syntax errors" "fail"
    fi
else
    check_result "Validation script execution" "fail"
fi

# 4. Testing Generator (Dry-Run)
echo ""
echo -e "${BLUE}[4/6]${NC} Testing generator (dry-run)..."
python scripts/docs/generate_code_docs.py --module controllers --dry-run > /tmp/generator_test.txt 2>&1
GENERATOR_EXIT=$?
if [ $GENERATOR_EXIT -eq 0 ]; then
    check_result "Generator dry-run successful" "pass"

    if grep -q "Found [0-9]* Python files to document" /tmp/generator_test.txt; then
        check_result "Generator file discovery working" "pass"
    else
        check_result "Generator file discovery working" "fail"
    fi
else
    check_result "Generator dry-run successful" "fail"
    echo "Generator exit code: $GENERATOR_EXIT"
fi

# 5. Git Status Check
echo ""
echo -e "${BLUE}[5/6]${NC} Checking git status..."
if git log --oneline -1 | grep -q "Week 1"; then
    check_result "Week 1 commit exists" "pass"
else
    check_result "Week 1 commit exists" "fail"
fi

# Check if branch is up to date
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if git status | grep -q "Your branch is up to date with"; then
    check_result "Branch synced with remote" "pass"
else
    echo -e "${YELLOW}⚠${NC} Branch may not be synced with remote"
fi

# 6. Quality Checks
echo ""
echo -e "${BLUE}[6/6]${NC} Running quality checks..."

# Check Python file count
PYTHON_FILES=$(find src -name "*.py" -type f | wc -l)
if [ "$PYTHON_FILES" -eq 316 ]; then
    check_result "Python file count matches (316)" "pass"
else
    echo -e "${YELLOW}⚠${NC} Python file count: $PYTHON_FILES (expected 316)"
fi

# Check for __pycache__ pollution
PYCACHE_COUNT=$(find . -name "__pycache__" -type d 2>/dev/null | wc -l)
if [ "$PYCACHE_COUNT" -eq 0 ]; then
    check_result "No __pycache__ pollution" "pass"
else
    echo -e "${YELLOW}⚠${NC} Found $PYCACHE_COUNT __pycache__ directories (cleanup recommended)"
fi

# Summary
echo ""
echo "=========================================="
echo "Week 1 Validation Complete!"
echo "=========================================="
echo ""
echo -e "${GREEN}Passed: $PASSED_CHECKS${NC} / $TOTAL_CHECKS checks"
echo ""

if [ "$PASSED_CHECKS" -eq "$TOTAL_CHECKS" ]; then
    echo -e "${GREEN}✓ Week 1 infrastructure is solid!${NC}"
    echo "Ready to proceed to Week 2 (Controllers detailed documentation)"
    exit 0
elif [ "$PASSED_CHECKS" -ge $((TOTAL_CHECKS * 3 / 4)) ]; then
    echo -e "${YELLOW}⚠ Most checks passed, but some issues found${NC}"
    echo "Review failures above before proceeding to Week 2"
    exit 1
else
    echo -e "${RED}✗ Significant issues detected${NC}"
    echo "Fix issues before proceeding to Week 2"
    exit 1
fi
