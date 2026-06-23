#!/bin/bash
# GitHub Issues Creation Script for DIP_SMC_PSO Project
# Replacement for local problem-tracking system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Create GitHub issues for DIP SMC PSO project problems"
    echo ""
    echo "Options:"
    echo "  -t, --type TYPE           Issue type: stability|performance|convergence|bounds|implementation|feature"
    echo "  -p, --priority PRIORITY   Priority: critical|high|medium|low"
    echo "  -T, --title TITLE         Issue title"
    echo "  -d, --description DESC    Issue description"
    echo "  -c, --controller CTRL     Controller type: classical_smc|sta_smc|adaptive_smc|hybrid_sta_smc|swing_up_smc|mpc"
    echo "  -g, --gains GAINS         Control gains (comma-separated)"
    echo "  -r, --reproduction CMD    Reproduction command"
    echo "  -l, --labels LABELS       Additional labels (comma-separated)"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  # Create stability issue"
    echo "  $0 -t stability -p critical -T \"Lyapunov violation in classical SMC\" -c classical_smc"
    echo ""
    echo "  # Create PSO convergence issue"
    echo "  $0 -t convergence -p high -T \"PSO stagnation after 20 iterations\" -d \"PSO fails to converge\""
    echo ""
    echo "  # Create performance issue"
    echo "  $0 -t performance -p medium -T \"Excessive overshoot in STA-SMC\" -c sta_smc -g \"10,5,8,3,15,2\""
}

# Default values
TYPE=""
PRIORITY="medium"
TITLE=""
DESCRIPTION=""
CONTROLLER=""
GAINS=""
REPRODUCTION=""
LABELS=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TYPE="$2"
            shift 2
            ;;
        -p|--priority)
            PRIORITY="$2"
            shift 2
            ;;
        -T|--title)
            TITLE="$2"
            shift 2
            ;;
        -d|--description)
            DESCRIPTION="$2"
            shift 2
            ;;
        -c|--controller)
            CONTROLLER="$2"
            shift 2
            ;;
        -g|--gains)
            GAINS="$2"
            shift 2
            ;;
        -r|--reproduction)
            REPRODUCTION="$2"
            shift 2
            ;;
        -l|--labels)
            LABELS="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            usage
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$TYPE" ] || [ -z "$TITLE" ]; then
    echo -e "${RED}Error: Type and title are required${NC}"
    usage
    exit 1
fi

# Validate type
case $TYPE in
    stability|performance|convergence|bounds|implementation|feature)
        ;;
    *)
        echo -e "${RED}Error: Invalid type '$TYPE'${NC}"
        echo "Valid types: stability, performance, convergence, bounds, implementation, feature"
        exit 1
        ;;
esac

# Validate priority
case $PRIORITY in
    critical|high|medium|low)
        ;;
    *)
        echo -e "${RED}Error: Invalid priority '$PRIORITY'${NC}"
        echo "Valid priorities: critical, high, medium, low"
        exit 1
        ;;
esac

# Build title prefix and labels based on type
case $TYPE in
    stability)
        TITLE_PREFIX="[STABILITY]"
        BASE_LABELS="stability,control-systems,$PRIORITY"
        ICON="🔴"
        ;;
    performance)
        TITLE_PREFIX="[PERFORMANCE]"
        BASE_LABELS="performance,control-systems,$PRIORITY"
        ICON="🟡"
        ;;
    convergence)
        TITLE_PREFIX="[PSO-CONVERGENCE]"
        BASE_LABELS="convergence,optimization,pso,$PRIORITY"
        ICON="🔵"
        ;;
    bounds)
        TITLE_PREFIX="[PSO-BOUNDS]"
        BASE_LABELS="parameter-bounds,optimization,pso,$PRIORITY"
        ICON="🟠"
        ;;
    implementation)
        TITLE_PREFIX="[BUG]"
        BASE_LABELS="bug,implementation,$PRIORITY"
        ICON="🐛"
        ;;
    feature)
        TITLE_PREFIX="[FEATURE]"
        BASE_LABELS="enhancement,feature-request,$PRIORITY"
        ICON="✨"
        ;;
esac

# Combine labels
if [ -n "$LABELS" ]; then
    ALL_LABELS="$BASE_LABELS,$LABELS"
else
    ALL_LABELS="$BASE_LABELS"
fi

# Build issue body
BODY="$ICON **Issue Type**: $TYPE\n\n"

if [ -n "$DESCRIPTION" ]; then
    BODY+="## Description\n$DESCRIPTION\n\n"
fi

if [ -n "$CONTROLLER" ]; then
    BODY+="## Controller Information\n"
    BODY+="- **Controller Type**: $CONTROLLER\n"
    if [ -n "$GAINS" ]; then
        BODY+="- **Control Gains**: [$GAINS]\n"
    fi
    BODY+="\n"
fi

if [ -n "$REPRODUCTION" ]; then
    BODY+="## Reproduction\n"
    BODY+="\`\`\`bash\n$REPRODUCTION\n\`\`\`\n\n"
fi

BODY+="## System Information\n"
BODY+="- **Platform**: $(uname -s)\n"
BODY+="- **Python**: $(python --version 2>&1 | cut -d' ' -f2)\n"
BODY+="- **Timestamp**: $(date -u +"%Y-%m-%dT%H:%M:%SZ")\n\n"

BODY+="---\n"
BODY+="🤖 Created with GitHub Issues CLI workflow"

# Create the issue
echo -e "${BLUE}Creating GitHub issue...${NC}"
echo -e "Title: ${GREEN}$TITLE_PREFIX $TITLE${NC}"
echo -e "Labels: ${YELLOW}$ALL_LABELS${NC}"
echo ""

ISSUE_URL=$(gh issue create \
    --title "$TITLE_PREFIX $TITLE" \
    --body "$BODY" \
    --label "$ALL_LABELS")

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Issue created successfully!${NC}"
    echo -e "URL: ${BLUE}$ISSUE_URL${NC}"
else
    echo -e "${RED}❌ Failed to create issue${NC}"
    exit 1
fi