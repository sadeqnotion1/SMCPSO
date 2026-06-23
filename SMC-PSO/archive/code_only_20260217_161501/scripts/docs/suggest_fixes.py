#!/usr/bin/env python3
"""
# example-metadata:
# runnable: true
#==============================================================================
# D:/Projects/main/scripts/docs/suggest_fixes.py
#==============================================================================
# Generate automated fix suggestions for AI-ish patterns in documentation
#==============================================================================
"""

import json
import re
import argparse
from pathlib import Path
from typing import Dict, List
from collections import defaultdict


# Comprehensive replacement mapping
REPLACEMENTS = {
    # Greeting patterns
    r"\bLet's\s+": "REMOVE_OR_REPHRASE",
    r"\bLet\s+us\s+": "REMOVE_OR_REPHRASE",
    r"\bWe\s+will\s+": "This document covers",
    r"\bWe'll\s+": "This guide demonstrates",
    r"\bWelcome!\s*": "REMOVE",
    r"\bYou'll\s+love\s+": "REMOVE",
    r"\bIn\s+this\s+section\s+we\s+will\s+": "This section covers",
    r"\bNow\s+let's\s+": "REMOVE_OR_REPHRASE",

    # Enthusiasm patterns
    r"\bpowerful\s+": "CHECK_IF_NECESSARY",
    r"\bcomprehensive\s+": "CHECK_IF_NECESSARY",
    r"\bseamless\s+": "REMOVE",
    r"\bcutting-edge\s+": "CITE_OR_REMOVE",
    r"\bstate-of-the-art\s+": "CITE_OR_REMOVE",
    r"\bbest-in-class\s+": "REMOVE",
    r"\bindustry-leading\s+": "REMOVE",
    r"\brevolutionary\s+": "novel ",
    r"\badvanced\s+capabilities\b": "specific capabilities",
    r"\bsuperior\s+performance\b": "improved performance",
    r"\bamazing\s+": "REMOVE",
    r"\bincredible\s+": "REMOVE",
    r"\bexciting\s+": "REMOVE",

    # Hedge words
    r"\bleverage\s+": "use ",
    r"\bleverage\s+the\s+": "use the ",
    r"\butilize\s+": "use ",
    r"\bdelve\s+into\s+": "examine ",
    r"\bfacilitate\s+": "enable ",
    r"\bemploy\s+": "use ",

    # Transitions
    r"\bAs\s+we\s+can\s+see,\s*": "REMOVE",
    r"\bAs\s+we\s+can\s+see\s+": "REMOVE",
    r"\bIt's\s+worth\s+noting\s+that\s+": "REMOVE",
    r"\bIt\s+is\s+worth\s+noting\s+that\s+": "REMOVE",
    r"\bAdditionally,\s+it\s+should\s+be\s+mentioned\s+that\s+": "Additionally, ",
    r"\bFurthermore,\s+we\s+observe\s+that\s+": "Furthermore, ",
}


def suggest_file_fixes(file_path: Path) -> List[Dict]:
    """
    Generate line-by-line fix suggestions for a file.

    Args:
        file_path: Path to markdown file

    Returns:
        List of fix suggestion dictionaries
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        suggestions = []

        for line_num, line in enumerate(lines, 1):
            for pattern, replacement in REPLACEMENTS.items():
                matches = list(re.finditer(pattern, line, re.IGNORECASE))
                if matches:
                    for match in matches:
                        # Generate suggested replacement
                        if replacement == "REMOVE":
                            suggested = re.sub(pattern, "", line, flags=re.IGNORECASE)
                        elif replacement == "REMOVE_OR_REPHRASE":
                            suggested = "MANUAL_REVIEW_REQUIRED"
                        elif replacement == "CHECK_IF_NECESSARY":
                            suggested = "REVIEW: Keep if technical term, otherwise remove"
                        elif replacement == "CITE_OR_REMOVE":
                            suggested = "CITE_REFERENCE or remove"
                        else:
                            suggested = re.sub(pattern, replacement, line, flags=re.IGNORECASE, count=1)

                        severity = "HIGH" if replacement in ["REMOVE", "REMOVE_OR_REPHRASE"] else "MEDIUM"

                        suggestions.append({
                            "line": line_num,
                            "column": match.start(),
                            "original": line.strip(),
                            "pattern": pattern,
                            "matched_text": match.group(),
                            "action": replacement,
                            "suggested": suggested.strip(),
                            "severity": severity
                        })

        return suggestions

    except Exception as e:
        return [{"error": str(e), "file": str(file_path)}]


def generate_diff_format(file_path: Path, suggestions: List[Dict]) -> str:
    """
    Generate unified diff-style output for suggestions.

    Args:
        file_path: Path to file
        suggestions: List of fix suggestions

    Returns:
        Unified diff-style string
    """
    diff_lines = [f"--- {file_path}", f"+++ {file_path} (suggested)", ""]

    # Group by line number
    by_line = defaultdict(list)
    for suggestion in suggestions:
        by_line[suggestion['line']].append(suggestion)

    for line_num in sorted(by_line.keys()):
        line_suggestions = by_line[line_num]
        diff_lines.append(f"@@ Line {line_num} @@")
        diff_lines.append(f"- {line_suggestions[0]['original']}")
        diff_lines.append(f"+ {line_suggestions[0]['suggested']}")
        diff_lines.append(f"  # Action: {line_suggestions[0]['action']}")
        diff_lines.append("")

    return "\n".join(diff_lines)


def process_critical_files(json_report_path: Path, output_dir: Path):
    """
    Process all CRITICAL severity files and generate fix suggestions.

    Args:
        json_report_path: Path to AI pattern detection JSON report
        output_dir: Directory to save fix suggestions
    """
    json_data = json.loads(json_report_path.read_text(encoding='utf-8'))

    critical_files = [f for f in json_data['files'] if f.get('severity') == 'CRITICAL']

    output_dir.mkdir(parents=True, exist_ok=True)

    all_suggestions = {}
    total_fixes = 0

    print(f"Processing {len(critical_files)} CRITICAL files...")

    for i, file_data in enumerate(critical_files, 1):
        file_path = Path(file_data['file'])
        if not file_path.exists():
            print(f"  [{i}/{len(critical_files)}] SKIP: {file_path} (not found)")
            continue

        suggestions = suggest_file_fixes(file_path)
        if suggestions and 'error' not in suggestions[0]:
            all_suggestions[str(file_path)] = suggestions
            total_fixes += len(suggestions)

            # Generate diff file
            diff_output = generate_diff_format(file_path, suggestions)
            diff_file = output_dir / f"{file_path.stem}_fixes.diff"
            diff_file.write_text(diff_output, encoding='utf-8')

            print(f"  [{i}/{len(critical_files)}] {file_path.name}: {len(suggestions)} fixes -> {diff_file.name}")

    # Save comprehensive JSON
    json_output = output_dir / "all_fix_suggestions.json"
    json_output.write_text(json.dumps(all_suggestions, indent=2), encoding='utf-8')

    print("\nSummary:")
    print(f"  Files processed: {len(all_suggestions)}")
    print(f"  Total fixes suggested: {total_fixes}")
    print(f"  JSON output: {json_output}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate automated fix suggestions for AI-ish patterns"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Generate suggestions for single file"
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("D:/Projects/main/.artifacts/docs_audit/ai_pattern_detection_report.json"),
        help="Path to AI pattern detection JSON report"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("D:/Projects/main/.artifacts/docs_audit/fix_suggestions"),
        help="Directory to save fix suggestions"
    )

    args = parser.parse_args()

    if args.file:
        # Single file mode
        suggestions = suggest_file_fixes(args.file)
        if suggestions:
            print(f"\nFix suggestions for {args.file}:")
            print("=" * 80)
            for suggestion in suggestions[:20]:  # Show first 20
                print(f"Line {suggestion['line']}: {suggestion['matched_text']}")
                print(f"  Action: {suggestion['action']}")
                print(f"  Original: {suggestion['original'][:80]}...")
                print(f"  Suggested: {suggestion['suggested'][:80]}...")
                print()

            if len(suggestions) > 20:
                print(f"... and {len(suggestions) - 20} more suggestions")
    else:
        # Process all critical files
        process_critical_files(args.report, args.output_dir)


if __name__ == "__main__":
    main()
