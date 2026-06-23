#!/usr/bin/env python
"""
MA-01 Gap Analyzer
Finds missing topics, incomplete files, outdated content
Outputs: guides_gap_analysis.md
"""

import json
import re
from pathlib import Path

def analyze_gaps():
    """Analyze gaps in docs/guides/"""

    inventory_path = Path(".artifacts/qa_audits/MA-01_GUIDES_AUDIT_2025-11-10/guides_inventory.json")
    with open(inventory_path, 'r', encoding='utf-8') as f:
        inventory = json.load(f)

    gaps = {
        "missing_topics": [],
        "incomplete_files": [],
        "outdated_content": [],
        "controller_coverage": {}
    }

    print(f"\n[INFO] Analyzing gaps in {len(inventory['files'])} files...")

    # Check for incomplete files (TODO, FIXME, TBD markers)
    for file_info in inventory["files"]:
        file_path = Path("docs") / file_info["path"].replace('guides/', '', 1)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for TODO markers
        todos = re.findall(r'\b(TODO|FIXME|TBD|XXX)\b.*', content, re.IGNORECASE)
        if todos:
            gaps["incomplete_files"].append({
                "file": file_info["path"],
                "markers": len(todos),
                "examples": todos[:3],  # First 3
                "lines": file_info["lines"],
                "issue": f"{len(todos)} TODO/FIXME/TBD markers found"
            })

        # Check for very short files (likely stubs)
        if file_info["lines"] < 50 and file_info["filename"] not in ["README.md", "index.md"]:
            gaps["incomplete_files"].append({
                "file": file_info["path"],
                "markers": 0,
                "examples": [],
                "lines": file_info["lines"],
                "issue": f"Only {file_info['lines']} lines (likely incomplete)"
            })

        # Check for outdated version references
        old_versions = re.findall(r'v?[01]\.\d+|version [01]\.\d+', content, re.IGNORECASE)
        if old_versions:
            gaps["outdated_content"].append({
                "file": file_info["path"],
                "issue": f"{len(old_versions)} old version references",
                "examples": old_versions[:3]
            })

    # Check for missing controller documentation
    controllers = {
        "classical_smc": False,
        "sta_smc": False,
        "adaptive_smc": False,
        "hybrid_adaptive_sta_smc": False,
        "swing_up_smc": False,
        "mpc_controller": False,
        "factory": False
    }

    for file_info in inventory["files"]:
        file_path = Path("docs") / file_info["path"].replace('guides/', '', 1)
        filename = file_info["filename"].lower()
        path_str = str(file_path).lower()

        # Check if file mentions controllers
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()

        for controller in controllers:
            if controller in content or controller.replace('_', '-') in content:
                controllers[controller] = True

    gaps["controller_coverage"] = controllers

    # Check for missing tutorials (1-5 should all exist)
    tutorials_found = {i: False for i in range(1, 6)}
    for file_info in inventory["files"]:
        match = re.search(r'tutorial-0?(\d)', file_info["filename"].lower())
        if match:
            num = int(match.group(1))
            if num in tutorials_found:
                tutorials_found[num] = True

    for num, found in tutorials_found.items():
        if not found:
            gaps["missing_topics"].append({
                "topic": f"tutorial-0{num}",
                "expected_location": f"docs/guides/tutorials/tutorial-0{num}-*.md",
                "reason": "Expected based on tutorial sequence"
            })

    # Save gap analysis report
    report_path = Path(".artifacts/qa_audits/MA-01_GUIDES_AUDIT_2025-11-10/guides_gap_analysis.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# docs/guides/ Gap Analysis\n\n")
        f.write(f"**Audit Date:** November 10, 2025\n\n")
        f.write("---\n\n")

        f.write("## Summary\n\n")
        f.write(f"- Incomplete files: {len(gaps['incomplete_files'])}\n")
        f.write(f"- Outdated content: {len(gaps['outdated_content'])}\n")
        f.write(f"- Missing topics: {len(gaps['missing_topics'])}\n\n")

        f.write("## Controller Documentation Coverage\n\n")
        f.write("| Controller | Documented | Status |\n")
        f.write("|------------|------------|--------|\n")
        for controller, documented in gaps["controller_coverage"].items():
            status = "[OK] YES" if documented else "[ERROR] NO"
            f.write(f"| {controller} | {documented} | {status} |\n")

        missing_controllers = [c for c, d in gaps["controller_coverage"].items() if not d]
        if missing_controllers:
            f.write(f"\n[WARNING] Missing controller docs: {', '.join(missing_controllers)}\n")
        else:
            f.write(f"\n[OK] All 7 controllers have documentation\n")

        f.write("\n## Incomplete Files\n\n")
        if gaps['incomplete_files']:
            f.write("| File | Lines | Issue | Examples |\n")
            f.write("|------|-------|-------|----------|\n")
            for item in gaps['incomplete_files']:
                examples_str = "; ".join(item['examples'][:2]) if item['examples'] else "N/A"
                f.write(f"| {item['file']} | {item['lines']} | {item['issue']} | {examples_str[:50]} |\n")
        else:
            f.write("None found\n")

        f.write("\n## Outdated Content\n\n")
        if gaps['outdated_content']:
            f.write("| File | Issue | Examples |\n")
            f.write("|------|-------|----------|\n")
            for item in gaps['outdated_content']:
                examples_str = ", ".join(item['examples'][:3])
                f.write(f"| {item['file']} | {item['issue']} | {examples_str} |\n")
        else:
            f.write("None found\n")

        f.write("\n## Missing Topics\n\n")
        if gaps['missing_topics']:
            f.write("| Topic | Expected Location | Reason |\n")
            f.write("|-------|-------------------|--------|\n")
            for item in gaps['missing_topics']:
                f.write(f"| {item['topic']} | {item['expected_location']} | {item['reason']} |\n")
        else:
            f.write("None found\n")

    print(f"\n[OK] Incomplete files: {len(gaps['incomplete_files'])}")
    print(f"[OK] Outdated content: {len(gaps['outdated_content'])}")
    print(f"[OK] Missing topics: {len(gaps['missing_topics'])}")
    print(f"[OK] Controller coverage: {sum(gaps['controller_coverage'].values())}/7")
    print(f"[OK] Saved to: {report_path}")

    return gaps

if __name__ == "__main__":
    analyze_gaps()
