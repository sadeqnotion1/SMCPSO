#!/bin/bash
#==========================================================================================\
#================================ scripts/docs/quick_validate.sh ==========================\
#==========================================================================================\

# Quick 30-Second Week 1 Health Check
# Runs minimal validation for fast feedback

set -e

# Project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 Week 1 Quick Health Check (30 seconds)"
echo ""

# 1. Scripts exist?
if [ -f "scripts/docs/generate_code_docs.py" ]; then
    echo "✓ Generator script exists"
else
    echo "✗ Generator script missing"
    exit 1
fi

# 2. Docs generated?
DOC_COUNT=$(find docs/reference -name "*.md" -type f 2>/dev/null | wc -l)
if [ "$DOC_COUNT" -ge 330 ]; then
    echo "✓ Documentation generated ($DOC_COUNT files)"
else
    echo "✗ Documentation incomplete ($DOC_COUNT files, expected ~337)"
    exit 1
fi

# 3. Validation passes?
if python scripts/docs/validate_code_docs.py --check-all > /dev/null 2>&1; then
    echo "✓ All validation checks pass"
else
    echo "✗ Validation checks failed"
    exit 1
fi

# 4. Git commit exists?
if git log --oneline -5 | grep -q "Week 1"; then
    echo "✓ Week 1 commit exists"
else
    echo "✗ Week 1 commit not found"
    exit 1
fi

echo ""
echo "✅ Week 1 infrastructure healthy!"
echo "Run './scripts/docs/validate_week1.sh' for detailed validation"
