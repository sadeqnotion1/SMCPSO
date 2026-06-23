#!/bin/bash
# Generate minimal audit prompt for manual copy/paste into Gemini CLI
# Usage: ./generate_audit_prompt.sh [section_number]
# Example: ./generate_audit_prompt.sh 1  (for Section 01)
#          ./generate_audit_prompt.sh 5  (for Section 05)

if [ -z "$1" ]; then
    echo "Usage: $0 <section_number>"
    echo "Example: $0 1  (for Section 01: Introduction)"
    echo ""
    echo "Available sections:"
    echo "  1  - Introduction"
    echo "  2  - List of Figures"
    echo "  3  - System Model"
    echo "  4  - Controller Design"
    echo "  5  - Lyapunov Stability [PRIORITY]"
    echo "  6  - PSO Methodology"
    echo "  7  - Experimental Setup"
    echo "  8  - Performance Results [PRIORITY]"
    echo "  9  - Robustness Analysis [PRIORITY]"
    echo "  10 - Discussion"
    echo "  11 - Conclusion"
    echo "  12 - Acknowledgments"
    exit 1
fi

# Calculate section index (0-based) and section number (01-12)
section_idx=$((10#$1 - 1))
section_num=$(printf "%02d" $1)

# Get section metadata
section_name=$(jq -r ".sections[$section_idx].section_name" audit_config.json)
md_file=$(jq -r ".sections[$section_idx].markdown_file" audit_config.json)
prompt=$(jq -r ".sections[$section_idx].audit_prompt" audit_config.json)

# Check if file exists
if [ ! -f "$md_file" ]; then
    echo "ERROR: File not found: $md_file"
    exit 1
fi

# Print header
echo "========================================================================"
echo "AUDIT PROMPT FOR GEMINI CLI"
echo "Section $section_num: $section_name"
echo "========================================================================"
echo ""
echo "INSTRUCTIONS:"
echo "1. Copy EVERYTHING below this line"
echo "2. Paste into Gemini CLI"
echo "3. Wait for response"
echo "4. Save response to: audits/Section_${section_num}_AUDIT_REPORT.md"
echo ""
echo "========================================================================"
echo "START COPYING FROM HERE"
echo "========================================================================"
echo ""

# Output markdown content
cat "$md_file"

# Add separator
echo ""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "AUDIT INSTRUCTIONS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Output audit prompt
echo "$prompt"

echo ""
echo "========================================================================"
echo "END OF PROMPT"
echo "========================================================================"
echo ""
echo "Next: Paste the above content into Gemini CLI and save the response."
