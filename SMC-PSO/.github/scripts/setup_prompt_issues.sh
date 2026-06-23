#!/bin/bash
#==========================================================================================\\\
#========================== setup_prompt_issues.sh ====================================\\\
#==========================================================================================\\\
#
# Setup script to create GitHub issues from the prompt folder documentation.
# This script will create 9 comprehensive issues based on the documented test failures
# and analysis reports found in the prompt/ directory.
#
# Usage:
#   bash .github/scripts/setup_prompt_issues.sh          # Create all issues
#   bash .github/scripts/setup_prompt_issues.sh --dry-run # Preview what would be created
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  DIP SMC PSO - GitHub Issues Setup      ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Check if we're in the right directory
if [[ ! -f "$REPO_ROOT/prompt/pytest_analysis_report.md" ]]; then
    echo -e "${RED}Error: Cannot find prompt/pytest_analysis_report.md${NC}"
    echo -e "${RED}Please run this script from the repository root${NC}"
    exit 1
fi

# Check if GitHub CLI is installed and authenticated
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
    echo -e "${YELLOW}Install it with: winget install GitHub.cli${NC}"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI is not authenticated${NC}"
    echo -e "${YELLOW}Please run: gh auth login${NC}"
    exit 1
fi

echo -e "${GREEN}✓ GitHub CLI is installed and authenticated${NC}"

# Check if create_issue script exists
if [[ ! -f "$REPO_ROOT/.github/scripts/create_issue.sh" ]]; then
    echo -e "${RED}Error: create_issue.sh script not found${NC}"
    echo -e "${RED}Expected: $REPO_ROOT/.github/scripts/create_issue.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Issue creation script found${NC}"

# Parse command line arguments
DRY_RUN=""
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN="--dry-run"
    echo -e "${YELLOW}DRY RUN MODE - No issues will be created${NC}"
fi

echo ""
echo -e "${BLUE}Analyzing prompt folder documentation...${NC}"

# Check what's in the prompt folder
echo -e "${YELLOW}Found documentation files:${NC}"
ls -la "$REPO_ROOT/prompt/" | grep -E "\.(md|txt)$" | while read -r line; do
    echo "  $line"
done

echo ""
echo -e "${BLUE}Creating GitHub issues from documented problems...${NC}"

# Run the Python script to create issues
cd "$REPO_ROOT"
python .github/scripts/create_prompt_issues.py $DRY_RUN

if [[ -z "$DRY_RUN" ]]; then
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}  Issues Created Successfully!            ${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo ""
    echo -e "${BLUE}1. View all created issues:${NC}"
    echo "   gh issue list --search 'state:open'"
    echo ""
    echo -e "${BLUE}2. View critical issues:${NC}"
    echo "   gh issue list --search 'label:critical state:open'"
    echo ""
    echo -e "${BLUE}3. Access the Issue Dashboard:${NC}"
    echo "   cat .github/ISSUE_DASHBOARD.md"
    echo ""
    echo -e "${BLUE}4. Use the Navigation Guide:${NC}"
    echo "   cat .github/ISSUE_NAVIGATION_GUIDE.md"
    echo ""
    echo -e "${BLUE}5. Web interface links:${NC}"
    echo "   - All Issues: https://github.com/theSadeQ/dip-smc-pso/issues"
    echo "   - Critical Issues: https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Acritical"
    echo "   - High Priority: https://github.com/theSadeQ/dip-smc-pso/issues?q=is%3Aissue+is%3Aopen+label%3Ahigh"
    echo ""
    echo -e "${YELLOW}Issue Summary:${NC}"
    echo "  - 3 CRITICAL issues (stability, safety, configuration)"
    echo "  - 3 HIGH priority issues (PSO, factory, adaptive SMC)"
    echo "  - 3 MEDIUM priority issues (testing, performance, UI)"
    echo ""
    echo -e "${RED}IMPORTANT: Critical issues require response within 4 hours!${NC}"

else
    echo ""
    echo -e "${YELLOW}============================================${NC}"
    echo -e "${YELLOW}  Dry Run Complete                        ${NC}"
    echo -e "${YELLOW}============================================${NC}"
    echo ""
    echo -e "${BLUE}To actually create the issues, run:${NC}"
    echo "   bash .github/scripts/setup_prompt_issues.sh"
    echo ""
fi

echo -e "${GREEN}Setup complete!${NC}"