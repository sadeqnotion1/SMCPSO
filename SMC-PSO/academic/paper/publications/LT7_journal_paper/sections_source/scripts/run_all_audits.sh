#!/bin/bash
# Run all 12 section audits using Gemini CLI
# Usage: ./run_all_audits.sh

set -e  # Exit on error

echo "[INFO] LT-7 Research Paper - Automated Section Audits"
echo "[INFO] Starting audit process for 12 sections..."
echo ""

# Check prerequisites
if ! command -v gemini &> /dev/null; then
    echo "[ERROR] Gemini CLI not found. Install with: pip install google-generativeai-cli"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "[ERROR] jq not found. Install with: sudo apt install jq (Linux) or brew install jq (Mac)"
    exit 1
fi

if [ -z "$GOOGLE_API_KEY" ]; then
    echo "[WARNING] GOOGLE_API_KEY not set. You may encounter authentication errors."
    echo "[INFO] Set with: export GOOGLE_API_KEY='your-api-key'"
fi

# Create audits directory
mkdir -p audits

# Track statistics
total_sections=12
completed=0
failed=0
start_time=$(date +%s)

# Process each section
for i in {0..11}; do
    # Calculate section number with zero padding
    section_num=$(printf "%02d" $((i + 1)))

    # Get section metadata from JSON
    section_name=$(jq -r ".sections[$i].section_name" audit_config.json)
    md_file=$(jq -r ".sections[$i].markdown_file" audit_config.json)
    prompt=$(jq -r ".sections[$i].audit_prompt" audit_config.json)

    # Output files
    output_file="audits/Section_${section_num}_AUDIT_REPORT.md"
    temp_input="temp_audit_input_${section_num}.txt"

    echo "[INFO] =========================================="
    echo "[INFO] Section $section_num: $section_name"
    echo "[INFO] Source: $md_file"
    echo "[INFO] Output: $output_file"
    echo ""

    # Check if source file exists
    if [ ! -f "$md_file" ]; then
        echo "[ERROR] Source file not found: $md_file"
        ((failed++))
        continue
    fi

    # Create combined input file
    echo "[INFO] Creating audit input..."
    {
        cat "$md_file"
        echo ""
        echo ""
        echo "=== AUDIT INSTRUCTIONS ==="
        echo ""
        echo "$prompt"
    } > "$temp_input"

    # Run Gemini audit
    echo "[INFO] Running Gemini audit (this may take 30-60 seconds)..."
    if gemini < "$temp_input" > "$output_file" 2>&1; then
        # Check if output file was created and is not empty
        if [ -s "$output_file" ]; then
            file_size=$(wc -c < "$output_file")
            echo "[OK] Audit completed successfully ($file_size bytes)"
            ((completed++))
        else
            echo "[ERROR] Audit produced empty output"
            ((failed++))
        fi
    else
        echo "[ERROR] Gemini audit failed"
        ((failed++))
    fi

    # Cleanup temp file
    rm -f "$temp_input"

    echo ""
done

# Calculate elapsed time
end_time=$(date +%s)
elapsed=$((end_time - start_time))
minutes=$((elapsed / 60))
seconds=$((elapsed % 60))

# Print summary
echo "[INFO] =========================================="
echo "[INFO] AUDIT SUMMARY"
echo "[INFO] =========================================="
echo "[INFO] Total sections: $total_sections"
echo "[OK] Completed: $completed"
echo "[ERROR] Failed: $failed"
echo "[INFO] Elapsed time: ${minutes}m ${seconds}s"
echo ""

if [ $completed -eq $total_sections ]; then
    echo "[OK] All audits completed successfully!"
    echo "[INFO] Reports saved to audits/ directory"
    echo ""
    echo "[INFO] Next steps:"
    echo "  1. Review audit reports in audits/ directory"
    echo "  2. Focus on CRITICAL sections first (05, 08, 09)"
    echo "  3. Extract overall scores: grep 'Overall:' audits/*.md"
    echo "  4. Collect critical issues: grep -A 10 'CRITICAL' audits/*.md"
    echo "  5. Create AUDIT_SUMMARY.md after reviewing all reports"
else
    echo "[WARNING] Some audits failed. Check error messages above."
    echo "[INFO] Successfully audited $completed out of $total_sections sections."
fi

echo ""
echo "[INFO] Audit process complete."
