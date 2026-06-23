#!/usr/bin/env python3
"""
# example-metadata:
# runnable: true
#==============================================================================
# D:/Projects/main/scripts/docs/generate_audit_report.py
#==============================================================================
# Convert JSON audit results to human-readable markdown report
#==============================================================================
"""

import json
import argparse
from pathlib import Path
from typing import Dict
from datetime import datetime


def format_severity_badge(severity: str) -> str:
    """Generate markdown badge for severity level."""
    badges = {
        "CRITICAL": "![CRITICAL](https://img.shields.io/badge/CRITICAL-red)",
        "HIGH": "![HIGH](https://img.shields.io/badge/HIGH-orange)",
        "MEDIUM": "![MEDIUM](https://img.shields.io/badge/MEDIUM-yellow)",
        "LOW": "![LOW](https://img.shields.io/badge/LOW-green)",
        "ERROR": "![ERROR](https://img.shields.io/badge/ERROR-grey)",
    }
    return badges.get(severity, severity)


def generate_markdown_report(json_data: Dict) -> str:
    """
    Generate human-readable markdown audit report from JSON data.

    Args:
        json_data: Parsed JSON audit report

    Returns:
        Markdown formatted report string
    """
    md = []

    # Header
    md.append("# Documentation Quality Audit: AI-ish Language Detection\n\n")
    md.append(f"**Scan Date:** {json_data.get('scan_date', 'N/A')}\n\n")

    # Executive Summary
    md.append("## Executive Summary\n\n")
    md.append(f"- **Total Files Scanned:** {json_data['total_files_scanned']}\n")
    md.append(f"- **Total Lines Scanned:** {json_data['total_lines_scanned']:,}\n")
    md.append(f"- **Files with Issues:** {json_data['files_with_issues']} ")
    md.append(f"({json_data['files_with_issues']/json_data['total_files_scanned']*100:.1f}%)\n")
    md.append(f"- **Total Issues Found:** {json_data['total_issues']}\n")
    md.append("- **Average Issues per File:** ")
    avg_issues = json_data['total_issues'] / json_data['total_files_scanned']
    md.append(f"{avg_issues:.2f}\n\n")

    # Severity Breakdown
    md.append("## Severity Breakdown\n\n")
    md.append("| Severity | File Count | Percentage |\n")
    md.append("|----------|------------|------------|\n")
    total_files = json_data['total_files_scanned']
    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "ERROR"]:
        count = json_data['severity_breakdown'].get(severity, 0)
        if count > 0:
            pct = (count / total_files) * 100
            md.append(f"| {format_severity_badge(severity)} | {count} | {pct:.1f}% |\n")
    md.append("\n")

    # Pattern Frequency Statistics
    md.append("## Pattern Frequency Statistics\n\n")
    md.append("| Category | Occurrences | Priority |\n")
    md.append("|----------|-------------|----------|\n")
    for category, count in json_data['pattern_frequency'].items():
        priority = "HIGH" if count > 50 else "MEDIUM" if count > 20 else "LOW"
        md.append(f"| {category.title()} | {count} | {priority} |\n")
    md.append("\n")

    # Critical Priority Files
    critical_files = [f for f in json_data['files'] if f.get('severity') == 'CRITICAL']
    if critical_files:
        md.append("## Critical Priority Files (Severity: CRITICAL)\n\n")
        md.append(f"**{len(critical_files)} files require immediate attention**\n\n")
        for i, file_data in enumerate(critical_files[:30], 1):
            md.append(f"### {i}. `{file_data['file']}`\n\n")
            md.append(f"- **Total Issues:** {file_data['total_issues']}\n")
            md.append(f"- **File Size:** {file_data.get('file_size', 'N/A')} bytes\n")
            md.append(f"- **Lines:** {file_data.get('lines', 'N/A')}\n\n")

            md.append("**Issue Breakdown:**\n\n")
            for category, matches in file_data.get('patterns', {}).items():
                md.append(f"- **{category.title()}:** {len(matches)} issues\n")

            # Show sample issues
            md.append("\n**Sample Issues:**\n\n")
            all_matches = []
            for category, matches in file_data.get('patterns', {}).items():
                for match in matches[:3]:  # First 3 from each category
                    all_matches.append((category, match))

            for category, match in all_matches[:5]:  # Show max 5 samples
                md.append(f"- Line {match['line']} ({category}): `{match['text']}`\n")
                md.append(f"  ```\n  {match['full_line'][:100]}...\n  ```\n")

            md.append("\n---\n\n")

    # High Priority Files
    high_files = [f for f in json_data['files'] if f.get('severity') == 'HIGH']
    if high_files:
        md.append("## High Priority Files (Severity: HIGH)\n\n")
        md.append(f"**{len(high_files)} files need revision**\n\n")
        md.append("| File | Issues | Categories Affected |\n")
        md.append("|------|--------|---------------------|\n")
        for file_data in high_files[:50]:  # Top 50
            categories = ", ".join(file_data.get('patterns', {}).keys())
            md.append(f"| `{file_data['file']}` | {file_data['total_issues']} | {categories} |\n")
        if len(high_files) > 50:
            md.append(f"\n*...and {len(high_files) - 50} more HIGH severity files*\n")
        md.append("\n")

    # Medium Priority Files Summary
    medium_files = [f for f in json_data['files'] if f.get('severity') == 'MEDIUM']
    if medium_files:
        md.append("## Medium Priority Files (Severity: MEDIUM)\n\n")
        md.append(f"**{len(medium_files)} files have moderate issues**\n\n")
        md.append("<details>\n<summary>Click to expand medium priority file list</summary>\n\n")
        md.append("| File | Issues |\n")
        md.append("|------|--------|\n")
        for file_data in medium_files:
            md.append(f"| `{file_data['file']}` | {file_data['total_issues']} |\n")
        md.append("\n</details>\n\n")

    # Recommendations
    md.append("## Recommendations\n\n")
    md.append("### Immediate Actions (Next 24 Hours)\n\n")
    md.append(f"1. **Address {len(critical_files)} CRITICAL files** - These have 15+ AI-ish patterns\n")
    md.append("2. **Create replacement guidelines** - Document professional alternatives\n")
    md.append("3. **Establish review process** - Prevent future AI-ish language\n\n")

    md.append("### Short-term Actions (Next Week)\n\n")
    md.append(f"1. **Revise {len(high_files)} HIGH priority files** - 10-15 patterns each\n")
    md.append("2. **Implement automated checks** - Pre-commit hooks for pattern detection\n")
    md.append("3. **Train documentation contributors** - Share style guidelines\n\n")

    md.append("### Long-term Actions (Next Month)\n\n")
    md.append(f"1. **Address remaining {len(medium_files)} MEDIUM files**\n")
    md.append("2. **Establish documentation standards** - Formal style guide\n")
    md.append("3. **Periodic audits** - Monthly quality checks\n\n")

    # Pattern-Specific Guidance
    md.append("## Pattern-Specific Replacement Guidance\n\n")

    guidance = {
        "greeting": {
            "description": "Conversational welcomes and exploratory language",
            "examples": [
                ("Let's explore the PSO optimizer", "The PSO optimizer minimizes..."),
                ("Welcome to the guide!", "This guide covers..."),
                ("We will examine the controller", "The controller implements..."),
            ]
        },
        "enthusiasm": {
            "description": "Marketing buzzwords and hype language",
            "examples": [
                ("powerful framework", "framework"),
                ("seamless integration", "integration"),
                ("cutting-edge algorithms", "algorithms (see references)"),
            ]
        },
        "hedge_words": {
            "description": "Unnecessarily complex terminology",
            "examples": [
                ("leverage the optimizer", "use the optimizer"),
                ("utilize the controller", "use the controller"),
                ("delve into the details", "examine the implementation"),
            ]
        },
        "transitions": {
            "description": "Redundant transitional phrases",
            "examples": [
                ("As we can see, the results show...", "The results show..."),
                ("It's worth noting that the system...", "The system..."),
                ("Furthermore, we observe that...", "Additionally, ... OR remove entirely"),
            ]
        }
    }

    for category, info in guidance.items():
        count = json_data['pattern_frequency'].get(category, 0)
        if count > 0:
            md.append(f"### {category.title()} ({count} occurrences)\n\n")
            md.append(f"**Issue:** {info['description']}\n\n")
            md.append("**Examples:**\n\n")
            md.append("| AI-ish | Professional |\n")
            md.append("|--------|-------------|\n")
            for ai_phrase, professional in info['examples']:
                md.append(f"| {ai_phrase} | {professional} |\n")
            md.append("\n")

    # Footer
    md.append("---\n\n")
    md.append("**Generated by:** `scripts/docs/generate_audit_report.py`\n")
    md.append(f"**Report Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    return "".join(md)


def main():
    parser = argparse.ArgumentParser(
        description="Generate human-readable markdown audit report from JSON"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("D:/Projects/main/.artifacts/docs_audit/ai_pattern_detection_report.json"),
        help="Path to JSON audit report (default: ai_pattern_detection_report.json)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("D:/Projects/main/.artifacts/docs_audit/AI_PATTERN_AUDIT_REPORT.md"),
        help="Output markdown report path (default: AI_PATTERN_AUDIT_REPORT.md)"
    )

    args = parser.parse_args()
    json_path = args.input
    output_path = args.output

    if not json_path.exists():
        print(f"Error: JSON report not found at {json_path}")
        print("Run detect_ai_patterns.py first to generate the report.")
        return

    json_data = json.loads(json_path.read_text(encoding='utf-8'))

    md_report = generate_markdown_report(json_data)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md_report, encoding='utf-8')

    print("Markdown report generated successfully!")
    print(f"Output: {output_path}")
    print("\nReport Summary:")
    print(f"  - Total files: {json_data['total_files_scanned']}")
    print(f"  - Files with issues: {json_data['files_with_issues']}")
    print(f"  - Total issues: {json_data['total_issues']}")
    print(f"  - CRITICAL files: {json_data['severity_breakdown'].get('CRITICAL', 0)}")
    print(f"  - HIGH files: {json_data['severity_breakdown'].get('HIGH', 0)}")


if __name__ == "__main__":
    main()
