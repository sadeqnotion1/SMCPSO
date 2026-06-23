#!/usr/bin/env python3
"""
# example-metadata:
# runnable: true
#==============================================================================
# D:/Projects/main/scripts/docs/analyze_sphinx_warnings_v2.py
#==============================================================================
# Comprehensive Sphinx Warning Analyzer - Phase 1
#
# Parses Sphinx build logs and categorizes all warnings with detailed
# analysis, severity ranking, and fix complexity estimates.
#
# Usage:
#     python scripts/docs/analyze_sphinx_warnings_v2.py --log docs/sphinx_build.log
#     python scripts/docs/analyze_sphinx_warnings_v2.py --build-and-analyze
#==============================================================================
"""

import re
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Tuple
from collections import defaultdict
from datetime import datetime


# Warning pattern definitions with severity and fix complexity
WARNING_PATTERNS = {
    "orphaned_docs": {
        "pattern": r"WARNING: document isn't included in any toctree",
        "severity": "HIGH",
        "fix_complexity": "MEDIUM",
        "description": "Document exists but not referenced in any toctree",
        "auto_fixable": True
    },
    "malformed_toctree": {
        "pattern": r"WARNING: toctree contains reference to nonexisting document",
        "severity": "CRITICAL",
        "fix_complexity": "MEDIUM",
        "description": "Toctree directive has content parsed as document references",
        "auto_fixable": True
    },
    "pygments_lexer": {
        "pattern": r"WARNING: Pygments lexer name .* is not known",
        "severity": "LOW",
        "fix_complexity": "LOW",
        "description": "Invalid or unknown Pygments syntax highlighter name",
        "auto_fixable": True
    },
    "lexing_error": {
        "pattern": r"WARNING: Lexing literal_block .* as .* resulted in an error",
        "severity": "LOW",
        "fix_complexity": "LOW",
        "description": "Code block content incompatible with specified lexer",
        "auto_fixable": True
    },
    "unknown_document": {
        "pattern": r"WARNING: unknown document:",
        "severity": "MEDIUM",
        "fix_complexity": "LOW",
        "description": "Cross-reference to non-existent document",
        "auto_fixable": False
    },
    "header_hierarchy": {
        "pattern": r"WARNING: Non-consecutive header level increase",
        "severity": "MEDIUM",
        "fix_complexity": "LOW",
        "description": "Heading levels skip (e.g., H1 to H3)",
        "auto_fixable": True
    },
    "directive_parse": {
        "pattern": r"WARNING:.*Has content, but none permitted.*\[myst.directive_parse\]",
        "severity": "MEDIUM",
        "fix_complexity": "MEDIUM",
        "description": "MyST directive has content in options area",
        "auto_fixable": False
    },
    "include_file": {
        "pattern": r"WARNING: Include file .* not found or reading it failed",
        "severity": "HIGH",
        "fix_complexity": "HIGH",
        "description": "literalinclude or include directive pointing to missing file",
        "auto_fixable": False
    },
    "cross_reference": {
        "pattern": r"WARNING: Failed to create a cross reference",
        "severity": "LOW",
        "fix_complexity": "LOW",
        "description": "Reference to equation, figure, or section failed",
        "auto_fixable": False
    },
    "multiple_toctree": {
        "pattern": r"document is referenced in multiple toctrees",
        "severity": "LOW",
        "fix_complexity": "MEDIUM",
        "description": "Same document included in multiple toctree directives",
        "auto_fixable": False
    }
}


def build_sphinx_docs(docs_dir: Path = Path("docs")) -> Tuple[str, int]:
    """
    Run Sphinx build and capture output.

    Args:
        docs_dir: Path to documentation directory

    Returns:
        Tuple of (build_log_content, warning_count)
    """
    print(f"Building Sphinx documentation in {docs_dir}...")

    try:
        result = subprocess.run(
            ["sphinx-build", "-M", "html", ".", "_build", "-W", "--keep-going"],
            cwd=docs_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes max
        )

        build_output = result.stdout + result.stderr
        warning_count = build_output.count("WARNING:")

        print(f"Build completed with {warning_count} warnings")

        return build_output, warning_count

    except subprocess.TimeoutExpired:
        print("ERROR: Sphinx build timed out after 5 minutes")
        return "", -1
    except Exception as e:
        print(f"ERROR: Sphinx build failed: {e}")
        return "", -1


def parse_warning_line(line: str) -> Dict:
    """
    Parse a single warning line and extract metadata.

    Args:
        line: Warning line from Sphinx build log

    Returns:
        Dictionary with file, line_number, message, category
    """
    # Extract file path and line number
    file_match = re.search(r'D:\\Projects\\main\\docs\\([^:]+):(\d+):', line)
    if not file_match:
        # Try alternative format without line number
        file_match = re.search(r'D:\\Projects\\main\\docs\\([^:]+):', line)
        if file_match:
            filepath = file_match.group(1).replace('\\', '/')
            line_num = None
        else:
            filepath = "unknown"
            line_num = None
    else:
        filepath = file_match.group(1).replace('\\', '/')
        line_num = int(file_match.group(2))

    # Extract warning message
    msg_match = re.search(r'WARNING: (.+)', line)
    message = msg_match.group(1) if msg_match else line

    # Categorize warning
    category = "unknown"
    for cat_name, cat_info in WARNING_PATTERNS.items():
        if re.search(cat_info["pattern"], line):
            category = cat_name
            break

    return {
        "file": filepath,
        "line": line_num,
        "message": message,
        "category": category,
        "raw": line.strip()
    }


def analyze_warnings(log_content: str) -> Dict:
    """
    Comprehensive analysis of all warnings in build log.

    Args:
        log_content: Complete Sphinx build log

    Returns:
        Structured analysis dictionary
    """
    warnings = []

    # Extract all warning lines
    for line in log_content.split('\n'):
        if 'WARNING:' in line:
            warning_data = parse_warning_line(line)
            warnings.append(warning_data)

    # Aggregate by category
    by_category = defaultdict(list)
    for warning in warnings:
        by_category[warning["category"]].append(warning)

    # Aggregate by file
    by_file = defaultdict(list)
    for warning in warnings:
        by_file[warning["file"]].append(warning)

    # Aggregate by directory
    by_directory = defaultdict(list)
    for warning in warnings:
        directory = warning["file"].split('/')[0] if '/' in warning["file"] else "root"
        by_directory[directory].append(warning)

    # Calculate severity distribution
    severity_count = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
    for warning in warnings:
        cat = warning["category"]
        if cat in WARNING_PATTERNS:
            severity = WARNING_PATTERNS[cat]["severity"]
            severity_count[severity] += 1
        else:
            severity_count["UNKNOWN"] += 1

    # Calculate fix complexity distribution
    fix_complexity = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "UNKNOWN": 0}
    auto_fixable_count = 0
    for warning in warnings:
        cat = warning["category"]
        if cat in WARNING_PATTERNS:
            complexity = WARNING_PATTERNS[cat]["fix_complexity"]
            fix_complexity[complexity] += 1
            if WARNING_PATTERNS[cat]["auto_fixable"]:
                auto_fixable_count += 1
        else:
            fix_complexity["UNKNOWN"] += 1

    # Top offending files
    top_files = sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)[:20]

    # Top offending directories
    top_dirs = sorted(by_directory.items(), key=lambda x: len(x[1]), reverse=True)

    return {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_warnings": len(warnings),
            "total_files": len(by_file),
            "total_directories": len(by_directory),
            "auto_fixable_count": auto_fixable_count,
            "auto_fixable_percentage": round(auto_fixable_count / len(warnings) * 100, 1) if warnings else 0
        },
        "by_category": {
            cat: {
                "count": len(warns),
                "percentage": round(len(warns) / len(warnings) * 100, 1) if warnings else 0,
                "severity": WARNING_PATTERNS[cat]["severity"] if cat in WARNING_PATTERNS else "UNKNOWN",
                "fix_complexity": WARNING_PATTERNS[cat]["fix_complexity"] if cat in WARNING_PATTERNS else "UNKNOWN",
                "auto_fixable": WARNING_PATTERNS[cat]["auto_fixable"] if cat in WARNING_PATTERNS else False,
                "description": WARNING_PATTERNS[cat]["description"] if cat in WARNING_PATTERNS else "Unknown warning type",
                "examples": [w["message"] for w in warns[:3]]
            }
            for cat, warns in sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True)
        },
        "severity_distribution": severity_count,
        "fix_complexity_distribution": fix_complexity,
        "by_directory": {
            dir_name: {
                "count": len(warns),
                "percentage": round(len(warns) / len(warnings) * 100, 1) if warnings else 0
            }
            for dir_name, warns in top_dirs
        },
        "top_offending_files": [
            {
                "file": filepath,
                "warning_count": len(warns),
                "categories": list({w["category"] for w in warns})
            }
            for filepath, warns in top_files
        ],
        "all_warnings": warnings
    }


def generate_markdown_report(analysis: Dict, output_path: Path):
    """
    Generate human-readable markdown report.

    Args:
        analysis: Analysis results dictionary
        output_path: Where to save markdown report
    """
    md_lines = [
        "# Sphinx Documentation Warning Analysis - Phase 1 Baseline",
        f"**Generated**: {analysis['metadata']['timestamp']}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"**Total Warnings**: {analysis['metadata']['total_warnings']}",
        f"**Affected Files**: {analysis['metadata']['total_files']}",
        f"**Affected Directories**: {analysis['metadata']['total_directories']}",
        f"**Auto-Fixable**: {analysis['metadata']['auto_fixable_count']} ({analysis['metadata']['auto_fixable_percentage']}%)",
        "",
        "---",
        "",
        "## Severity Distribution",
        "",
        "| Severity | Count | Percentage |",
        "|----------|-------|------------|"
    ]

    total = analysis['metadata']['total_warnings']
    for severity, count in analysis['severity_distribution'].items():
        if count > 0:
            pct = round(count / total * 100, 1) if total > 0 else 0
            md_lines.append(f"| {severity} | {count} | {pct}% |")

    md_lines.extend([
        "",
        "---",
        "",
        "## Warning Categories (Sorted by Count)",
        ""
    ])

    for cat_name, cat_data in analysis['by_category'].items():
        md_lines.extend([
            f"### {cat_name.replace('_', ' ').title()}",
            "",
            f"**Count**: {cat_data['count']} ({cat_data['percentage']}%)",
            f"**Severity**: {cat_data['severity']}",
            f"**Fix Complexity**: {cat_data['fix_complexity']}",
            f"**Auto-Fixable**: {'Yes' if cat_data['auto_fixable'] else 'No'}",
            "",
            f"**Description**: {cat_data['description']}",
            "",
            "**Examples**:",
            ""
        ])

        for example in cat_data['examples']:
            md_lines.append(f"- `{example[:100]}...`" if len(example) > 100 else f"- `{example}`")

        md_lines.append("")

    md_lines.extend([
        "---",
        "",
        "## Top 20 Offending Files",
        "",
        "| Rank | File | Warnings | Categories |",
        "|------|------|----------|------------|"
    ])

    for i, file_data in enumerate(analysis['top_offending_files'], 1):
        categories = ', '.join(file_data['categories'][:3])
        if len(file_data['categories']) > 3:
            categories += f", +{len(file_data['categories']) - 3} more"
        md_lines.append(f"| {i} | {file_data['file']} | {file_data['warning_count']} | {categories} |")

    md_lines.extend([
        "",
        "---",
        "",
        "## Directory Distribution",
        "",
        "| Directory | Warnings | Percentage |",
        "|-----------|----------|------------|"
    ])

    for dir_name, dir_data in list(analysis['by_directory'].items())[:15]:
        md_lines.append(f"| {dir_name}/ | {dir_data['count']} | {dir_data['percentage']}% |")

    md_lines.extend([
        "",
        "---",
        "",
        "## Recommendations",
        "",
        "### Priority 1: Auto-Fixable (High Impact)",
        ""
    ])

    auto_fixable_cats = [
        (cat, data) for cat, data in analysis['by_category'].items()
        if data['auto_fixable'] and data['count'] > 10
    ]
    auto_fixable_cats.sort(key=lambda x: x[1]['count'], reverse=True)

    for cat_name, cat_data in auto_fixable_cats[:5]:
        md_lines.append(f"- **{cat_name.replace('_', ' ').title()}**: {cat_data['count']} warnings - Use automated script")

    md_lines.extend([
        "",
        "### Priority 2: Manual Review Required",
        ""
    ])

    manual_cats = [
        (cat, data) for cat, data in analysis['by_category'].items()
        if not data['auto_fixable'] and data['count'] > 5
    ]
    manual_cats.sort(key=lambda x: x[1]['count'], reverse=True)

    for cat_name, cat_data in manual_cats[:5]:
        md_lines.append(f"- **{cat_name.replace('_', ' ').title()}**: {cat_data['count']} warnings - Requires manual fix")

    md_lines.extend([
        "",
        "---",
        "",
        "**Report Generated By**: analyze_sphinx_warnings_v2.py",
        "**Phase**: 1 - Foundation & Automation Tooling",
        "**Next Steps**: Use fix scripts from Phase 1 to address auto-fixable categories"
    ])

    output_path.write_text('\n'.join(md_lines), encoding='utf-8')
    print(f"Markdown report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive Sphinx warning analyzer - Phase 1"
    )
    parser.add_argument(
        "--log",
        type=Path,
        help="Path to existing Sphinx build log file"
    )
    parser.add_argument(
        "--build-and-analyze",
        action="store_true",
        help="Build docs first, then analyze"
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path(".artifacts/sphinx_warnings_baseline_report.json"),
        help="Output JSON report path"
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path(".artifacts/sphinx_warnings_baseline_report.md"),
        help="Output Markdown report path"
    )

    args = parser.parse_args()

    # Get log content
    if args.build_and_analyze:
        log_content, warning_count = build_sphinx_docs()
        if warning_count < 0:
            print("ERROR: Build failed, cannot analyze")
            return 1
    elif args.log:
        if not args.log.exists():
            print(f"ERROR: Log file not found: {args.log}")
            return 1
        log_content = args.log.read_text(encoding='utf-8', errors='ignore')
    else:
        # Try to find recent log
        default_log = Path("docs/sphinx_build.log")
        if default_log.exists():
            print(f"Using default log: {default_log}")
            log_content = default_log.read_text(encoding='utf-8', errors='ignore')
        else:
            print("ERROR: No log file specified and no default found")
            print("Use --log PATH or --build-and-analyze")
            return 1

    # Analyze warnings
    print("\nAnalyzing warnings...")
    analysis = analyze_warnings(log_content)

    # Create output directory
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)

    # Save JSON report
    with open(args.output_json, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)
    print(f"JSON report saved to: {args.output_json}")

    # Generate markdown report
    generate_markdown_report(analysis, args.output_md)

    # Print summary
    print("\n" + "=" * 70)
    print("ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"Total Warnings:        {analysis['metadata']['total_warnings']}")
    print(f"Auto-Fixable:          {analysis['metadata']['auto_fixable_count']} ({analysis['metadata']['auto_fixable_percentage']}%)")
    print(f"Affected Files:        {analysis['metadata']['total_files']}")
    print(f"Affected Directories:  {analysis['metadata']['total_directories']}")
    print()
    print("Top 3 Categories:")
    for i, (cat, data) in enumerate(list(analysis['by_category'].items())[:3], 1):
        print(f"  {i}. {cat.replace('_', ' ').title()}: {data['count']} ({data['percentage']}%)")
    print()
    print("Reports saved:")
    print(f"  - JSON: {args.output_json}")
    print(f"  - Markdown: {args.output_md}")

    return 0


if __name__ == "__main__":
    exit(main())
