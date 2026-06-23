#!/usr/bin/env python3
"""
# example-metadata:
# runnable: true
#==============================================================================
# D:/Projects/main/scripts/docs/detect_ai_patterns.py
#==============================================================================
# AI-ish Language Pattern Detection for Documentation Quality Audit
#
# Scans all markdown files in docs/ directory for AI-sounding language patterns
# and generates structured JSON report with severity rankings.
#==============================================================================
"""

import re
import json
import argparse
from pathlib import Path
from typing import Dict
from collections import defaultdict
from datetime import datetime

# Pattern database categorized by AI-ish language type
AI_PATTERNS = {
    "greeting": [
        r"\bLet's\b",
        r"\bLet us\b",
        r"\bWe will\b",
        r"\bWe'll\b",
        r"\bWelcome\b",
        r"\bYou'll love\b",
        r"\bexciting journey\b",
        r"\bIn this section we will\b",
        r"\bNow let's\b",
        r"\bYou will learn\b",
        r"\bToday we'll\b",
    ],
    "enthusiasm": [
        r"\bpowerful\b",
        r"\bcomprehensive\b",
        r"\bseamless\b",
        r"\bcutting-edge\b",
        r"\bstate-of-the-art\b",
        r"\bbest-in-class\b",
        r"\bindustry-leading\b",
        r"\brevolutionary\b",
        r"\badvanced capabilities\b",
        r"\bsuperior performance\b",
        r"\bamazing\b",
        r"\bincredible\b",
        r"\bexciting\b",
        r"\bexcellent\b(?! agreement)",  # Exclude technical usage
    ],
    "hedge_words": [
        r"\bleverage\b",
        r"\butilize\b",
        r"\bdelve into\b",
        r"\bfacilitate\b",
        r"\benable\b(?! flag| option| the| this| logging| monitoring| feature| caching)",  # Exclude technical contexts
        # Removed "solutions" - causes false positives in mathematical/technical contexts
        # (e.g., "N solutions", "non-dominated solutions", "boundary solutions")
        r"\bcapabilities\b(?! of| include| are| :)",  # Exclude technical lists
        r"\bemploy\b",
        r"\bexploit\b(?! vulnerability)",  # Exclude security contexts
    ],
    "transitions": [
        r"\bAs we can see\b",
        r"\bIt's worth noting that\b",
        r"\bIt is worth noting that\b",
        r"\bAdditionally, it should be mentioned\b",
        r"\bFurthermore, we observe that\b",
        r"\bInterestingly,\b",
        r"\bNotably,\b",
        r"\bImportantly,\b",
    ],
    "repetitive": [
        r"\bIn this (section|chapter|guide)\b",
        r"\bThis (section|chapter|guide) (will|covers)\b",
        r"\bLet's (explore|examine|look at)\b",
        r"\bWe (will|can) (see|observe|note)\b",
    ],
}


def scan_file(file_path: Path, single_file_mode: bool = False) -> Dict:
    """
    Scan single file for AI patterns.

    Args:
        file_path: Path to markdown file
        single_file_mode: If True, provides detailed output for single file scan

    Returns:
        Dictionary with scan results including patterns found, severity, and context
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        matches = defaultdict(list)

        # Track code blocks and example sections to exclude from pattern matching
        in_code_block = False
        exclude_lines = set()

        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Toggle code block state on triple backticks
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                exclude_lines.add(i)
            elif in_code_block:
                exclude_lines.add(i)
            # Exclude markdown tables (lines starting with |)
            elif stripped.startswith('|'):
                exclude_lines.add(i)
            # Exclude blockquotes (lines starting with >)
            elif stripped.startswith('>'):
                exclude_lines.add(i)
            # Exclude checklist items (lines with - [ ])
            elif '- [ ]' in line or '- [x]' in line or '- [X]' in line:
                exclude_lines.add(i)
            # Exclude quoted examples in bullet points (lines with - "...pattern...")
            elif stripped.startswith('- "') and '"' in stripped[3:]:
                exclude_lines.add(i)
            # Exclude examples showing bad patterns (lines with ❌, BAD:, DO NOT USE:)
            elif any(marker in line for marker in ['❌', 'BAD:', 'DO NOT USE:', 'AI-ish']):
                exclude_lines.add(i)
            # Exclude lines with mathematical notation (inline $...$ or display $$...$$)
            elif '$' in line and line.count('$') >= 2:
                exclude_lines.add(i)
            # Exclude lines starting with math directives (```{math})
            elif stripped.startswith('```{math}') or stripped == '```':
                exclude_lines.add(i)

        for category, patterns in AI_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_num = content[:match.start()].count('\n') + 1

                    # Skip if in excluded lines (code blocks, examples, checklists, etc.)
                    if line_num in exclude_lines:
                        continue

                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line_end = content.find('\n', match.end())
                    if line_end == -1:
                        line_end = len(content)
                    full_line = content[line_start:line_end]

                    matches[category].append({
                        "pattern": pattern,
                        "line": line_num,
                        "text": match.group(),
                        "context": content[max(0, match.start()-50):match.end()+50],
                        "full_line": full_line.strip()
                    })

        total_issues = sum(len(v) for v in matches.values())

        # Severity classification
        if total_issues > 15:
            severity = "CRITICAL"
        elif total_issues > 10:
            severity = "HIGH"
        elif total_issues > 5:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        # Fix path resolution: try relative first, fall back to absolute
        try:
            relative_path = file_path.relative_to(Path.cwd())
            file_str = str(relative_path)
        except ValueError:
            # File is outside cwd, use absolute path
            file_str = str(file_path.absolute())

        return {
            "file": file_str,
            "total_issues": total_issues,
            "severity": severity,
            "patterns": dict(matches),
            "file_size": len(content),
            "lines": content.count('\n') + 1,
        }
    except Exception as e:
        return {
            "file": str(file_path),
            "error": str(e),
            "total_issues": 0,
            "severity": "ERROR"
        }


def scan_all_docs(docs_dir: Path) -> Dict:
    """
    Scan all markdown files in docs directory.

    Args:
        docs_dir: Path to docs directory

    Returns:
        Comprehensive audit report with statistics and per-file results
    """
    results = []
    pattern_stats = defaultdict(int)
    total_lines_scanned = 0

    print(f"Scanning markdown files in {docs_dir}...")

    for md_file in docs_dir.rglob("*.md"):
        file_result = scan_file(md_file)
        results.append(file_result)
        total_lines_scanned += file_result.get("lines", 0)

        if "patterns" in file_result:
            for category, matches in file_result["patterns"].items():
                pattern_stats[category] += len(matches)

    # Sort by severity and total issues
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "ERROR": 4}
    results.sort(key=lambda x: (
        severity_order.get(x.get("severity", "ERROR"), 5),
        -x.get("total_issues", 0)
    ))

    return {
        "scan_date": datetime.now().isoformat(),
        "total_files_scanned": len(results),
        "total_lines_scanned": total_lines_scanned,
        "files_with_issues": len([r for r in results if r.get("total_issues", 0) > 0]),
        "total_issues": sum(r.get("total_issues", 0) for r in results),
        "pattern_frequency": dict(sorted(pattern_stats.items(), key=lambda x: -x[1])),
        "severity_breakdown": {
            "CRITICAL": len([r for r in results if r.get("severity") == "CRITICAL"]),
            "HIGH": len([r for r in results if r.get("severity") == "HIGH"]),
            "MEDIUM": len([r for r in results if r.get("severity") == "MEDIUM"]),
            "LOW": len([r for r in results if r.get("severity") == "LOW"]),
            "ERROR": len([r for r in results if r.get("severity") == "ERROR"]),
        },
        "files": results
    }


def print_single_file_report(result: Dict):
    """Print detailed report for single file scan with Unicode handling."""
    def safe_print(text):
        """Print with fallback for Windows cp1252 encoding."""
        try:
            print(text)
        except UnicodeEncodeError:
            # Fallback: encode to ASCII with replacement for Windows terminals
            print(text.encode('ascii', errors='replace').decode('ascii'))

    safe_print(f"\n{'='*80}")
    safe_print(f"File: {result['file']}")
    safe_print(f"{'='*80}")
    safe_print(f"Total Issues: {result['total_issues']}")
    safe_print(f"Severity: {result['severity']}")
    safe_print(f"File Size: {result.get('file_size', 'N/A')} bytes")
    safe_print(f"Lines: {result.get('lines', 'N/A')}\n")

    if result['total_issues'] > 0:
        for category, matches in result.get('patterns', {}).items():
            safe_print(f"\n{category.upper()} ({len(matches)} issues):")
            safe_print("-" * 80)
            for match in matches[:10]:  # Show first 10 per category
                safe_print(f"  Line {match['line']}: {match['text']}")
                # Truncate and sanitize full line for display
                full_line = match['full_line'][:100].replace('\u2192', '->').replace('\u2713', 'OK')
                safe_print(f"    Full line: {full_line}...")
            if len(matches) > 10:
                safe_print(f"  ... and {len(matches) - 10} more")
    else:
        safe_print("No AI-ish patterns detected!")


def main():
    parser = argparse.ArgumentParser(
        description="Detect AI-ish language patterns in documentation"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Scan a single file instead of full docs directory"
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path("D:/Projects/main/docs"),
        help="Documentation directory to scan (default: D:/Projects/main/docs)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("D:/Projects/main/.artifacts/docs_audit/ai_pattern_detection_report.json"),
        help="Output JSON report path"
    )

    args = parser.parse_args()

    if args.file:
        # Single file mode
        result = scan_file(args.file, single_file_mode=True)
        print_single_file_report(result)

        # Also save to JSON
        output_path = args.output.parent / f"single_file_{args.file.stem}_report.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(f"\nDetailed report saved to: {output_path}")

    else:
        # Full directory scan
        results = scan_all_docs(args.docs_dir)

        # Save to JSON
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(results, indent=2), encoding='utf-8')

        # Print summary
        print(f"\n{'='*80}")
        print("DOCUMENTATION QUALITY AUDIT SUMMARY")
        print(f"{'='*80}")
        print(f"Scan Date: {results['scan_date']}")
        print(f"Total Files Scanned: {results['total_files_scanned']}")
        print(f"Total Lines Scanned: {results['total_lines_scanned']:,}")
        print(f"Files with Issues: {results['files_with_issues']}")
        print(f"Total Issues Found: {results['total_issues']}")
        print("\nSeverity Breakdown:")
        for severity, count in results['severity_breakdown'].items():
            if count > 0:
                print(f"  {severity}: {count} files")
        print("\nPattern Frequency:")
        for category, count in results['pattern_frequency'].items():
            print(f"  {category}: {count} occurrences")
        print(f"\nReport saved to: {args.output}")

        # Show top 10 worst offenders
        print(f"\n{'='*80}")
        print("TOP 10 FILES REQUIRING IMMEDIATE ATTENTION")
        print(f"{'='*80}")
        for i, file_data in enumerate(results['files'][:10], 1):
            if file_data.get('total_issues', 0) > 0:
                print(f"{i}. {file_data['file']}")
                print(f"   Severity: {file_data['severity']} | Issues: {file_data['total_issues']}")


if __name__ == "__main__":
    main()
