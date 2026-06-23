#!/bin/bash
# GitHub Issues Management Script for DIP_SMC_PSO Project
# Replacement for local problem-tracking system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Manage GitHub issues for DIP SMC PSO project"
    echo ""
    echo "Commands:"
    echo "  list [FILTER]             List issues with optional filter"
    echo "  show ID                   Show detailed issue information"
    echo "  close ID [REASON]         Close an issue with optional reason"
    echo "  reopen ID                 Reopen a closed issue"
    echo "  label ID LABELS           Add labels to an issue"
    echo "  comment ID TEXT           Add comment to an issue"
    echo "  search QUERY              Search issues by text"
    echo "  stats                     Show repository issue statistics"
    echo "  export [FORMAT]           Export issues to CSV/JSON"
    echo ""
    echo "List Filters:"
    echo "  --stability               Show stability issues only"
    echo "  --performance             Show performance issues only"
    echo "  --pso                     Show PSO optimization issues only"
    echo "  --critical                Show critical priority issues only"
    echo "  --open                    Show open issues only (default)"
    echo "  --closed                  Show closed issues only"
    echo "  --all                     Show all issues"
    echo ""
    echo "Examples:"
    echo "  $0 list --stability       # List stability issues"
    echo "  $0 list --critical        # List critical issues"
    echo "  $0 show 5                 # Show issue #5 details"
    echo "  $0 close 3 \"Fixed by commit abc123\""
    echo "  $0 search \"overshoot\"     # Search for overshoot issues"
    echo "  $0 stats                  # Show issue statistics"
}

# Function to list issues with filters
list_issues() {
    local filter=""
    local state="open"

    case $1 in
        --stability)
            filter="label:stability"
            ;;
        --performance)
            filter="label:performance"
            ;;
        --pso)
            filter="label:pso"
            ;;
        --critical)
            filter="label:critical"
            ;;
        --open)
            state="open"
            ;;
        --closed)
            state="closed"
            ;;
        --all)
            state="all"
            ;;
    esac

    echo -e "${BLUE}📋 Listing issues (state: $state)${NC}"
    if [ -n "$filter" ]; then
        echo -e "${YELLOW}Filter: $filter${NC}"
    fi
    echo ""

    if [ -n "$filter" ]; then
        gh issue list --state "$state" --search "$filter" --limit 50
    else
        gh issue list --state "$state" --limit 50
    fi
}

# Function to show issue details
show_issue() {
    local issue_id=$1

    if [ -z "$issue_id" ]; then
        echo -e "${RED}Error: Issue ID required${NC}"
        return 1
    fi

    echo -e "${BLUE}📄 Issue #$issue_id Details${NC}"
    echo ""
    gh issue view "$issue_id"
}

# Function to close issue
close_issue() {
    local issue_id=$1
    local reason=$2

    if [ -z "$issue_id" ]; then
        echo -e "${RED}Error: Issue ID required${NC}"
        return 1
    fi

    echo -e "${YELLOW}🔒 Closing issue #$issue_id${NC}"

    if [ -n "$reason" ]; then
        gh issue close "$issue_id" --reason completed --comment "Closed: $reason"
    else
        gh issue close "$issue_id" --reason completed
    fi

    echo -e "${GREEN}✅ Issue #$issue_id closed${NC}"
}

# Function to reopen issue
reopen_issue() {
    local issue_id=$1

    if [ -z "$issue_id" ]; then
        echo -e "${RED}Error: Issue ID required${NC}"
        return 1
    fi

    echo -e "${YELLOW}🔓 Reopening issue #$issue_id${NC}"
    gh issue reopen "$issue_id"
    echo -e "${GREEN}✅ Issue #$issue_id reopened${NC}"
}

# Function to add labels
add_labels() {
    local issue_id=$1
    local labels=$2

    if [ -z "$issue_id" ] || [ -z "$labels" ]; then
        echo -e "${RED}Error: Issue ID and labels required${NC}"
        return 1
    fi

    echo -e "${YELLOW}🏷️  Adding labels to issue #$issue_id${NC}"
    gh issue edit "$issue_id" --add-label "$labels"
    echo -e "${GREEN}✅ Labels added: $labels${NC}"
}

# Function to add comment
add_comment() {
    local issue_id=$1
    local comment=$2

    if [ -z "$issue_id" ] || [ -z "$comment" ]; then
        echo -e "${RED}Error: Issue ID and comment text required${NC}"
        return 1
    fi

    echo -e "${YELLOW}💬 Adding comment to issue #$issue_id${NC}"
    gh issue comment "$issue_id" --body "$comment"
    echo -e "${GREEN}✅ Comment added${NC}"
}

# Function to search issues
search_issues() {
    local query=$1

    if [ -z "$query" ]; then
        echo -e "${RED}Error: Search query required${NC}"
        return 1
    fi

    echo -e "${BLUE}🔍 Searching issues for: \"$query\"${NC}"
    echo ""
    gh issue list --search "$query" --limit 30
}

# Function to show statistics
show_stats() {
    echo -e "${PURPLE}📊 Issue Statistics${NC}"
    echo ""

    local total_open=$(gh issue list --state open --limit 1000 | wc -l)
    local total_closed=$(gh issue list --state closed --limit 1000 | wc -l)
    local total=$((total_open + total_closed))

    echo -e "📈 ${BLUE}Total Issues:${NC} $total"
    echo -e "🟢 ${GREEN}Open Issues:${NC} $total_open"
    echo -e "🔴 ${RED}Closed Issues:${NC} $total_closed"
    echo ""

    echo -e "${YELLOW}By Category:${NC}"
    echo -e "🔴 Stability: $(gh issue list --search "label:stability" --state all --limit 1000 | wc -l)"
    echo -e "🟡 Performance: $(gh issue list --search "label:performance" --state all --limit 1000 | wc -l)"
    echo -e "🔵 PSO: $(gh issue list --search "label:pso" --state all --limit 1000 | wc -l)"
    echo -e "🐛 Implementation: $(gh issue list --search "label:implementation" --state all --limit 1000 | wc -l)"
    echo -e "✨ Features: $(gh issue list --search "label:feature-request" --state all --limit 1000 | wc -l)"
    echo ""

    echo -e "${YELLOW}By Priority:${NC}"
    echo -e "🚨 Critical: $(gh issue list --search "label:critical" --state all --limit 1000 | wc -l)"
    echo -e "⚠️  High: $(gh issue list --search "label:high" --state all --limit 1000 | wc -l)"
    echo -e "🟡 Medium: $(gh issue list --search "label:medium" --state all --limit 1000 | wc -l)"
    echo -e "🟢 Low: $(gh issue list --search "label:low" --state all --limit 1000 | wc -l)"
}

# Function to export issues
export_issues() {
    local format=${1:-csv}
    local filename="issues_export_$(date +%Y%m%d_%H%M%S).$format"

    echo -e "${BLUE}📤 Exporting issues to $filename${NC}"

    if [ "$format" = "json" ]; then
        gh api repos/:owner/:repo/issues --paginate > "$filename"
    else
        # CSV export
        echo "number,title,state,labels,created_at,updated_at,assignee,url" > "$filename"
        gh issue list --state all --limit 1000 --json number,title,state,labels,createdAt,updatedAt,assignees,url \
            --jq '.[] | [.number, .title, .state, (.labels | map(.name) | join(";")), .createdAt, .updatedAt, (.assignees | map(.login) | join(";")), .url] | @csv' \
            >> "$filename"
    fi

    echo -e "${GREEN}✅ Export completed: $filename${NC}"
}

# Main command processing
COMMAND=$1
shift

case $COMMAND in
    list)
        list_issues "$@"
        ;;
    show)
        show_issue "$@"
        ;;
    close)
        close_issue "$@"
        ;;
    reopen)
        reopen_issue "$@"
        ;;
    label)
        add_labels "$@"
        ;;
    comment)
        add_comment "$@"
        ;;
    search)
        search_issues "$@"
        ;;
    stats)
        show_stats
        ;;
    export)
        export_issues "$@"
        ;;
    -h|--help|help)
        usage
        ;;
    *)
        if [ -z "$COMMAND" ]; then
            echo -e "${RED}Error: Command required${NC}"
        else
            echo -e "${RED}Error: Unknown command '$COMMAND'${NC}"
        fi
        echo ""
        usage
        exit 1
        ;;
esac