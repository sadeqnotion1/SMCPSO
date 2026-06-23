#!/usr/bin/env python
"""
MA-01 Link Validator
Validates all internal links in docs/guides/
Outputs: guides_broken_links.csv, guides_navigation_issues.md
"""

import json
import csv
import re
from pathlib import Path
from collections import defaultdict

def extract_links(content):
    """Extract all markdown links from content"""
    # Match [text](path) format
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    links = re.findall(link_pattern, content)
    return links

def validate_links():
    """Validate all links in docs/guides/"""

    inventory_path = Path(".artifacts/qa_audits/MA-01_GUIDES_AUDIT_2025-11-10/guides_inventory.json")
    with open(inventory_path, 'r', encoding='utf-8') as f:
        inventory = json.load(f)

    issues = {
        "broken_links": [],
        "orphaned_files": [],
        "dead_ends": [],
        "index_issues": []
    }

    all_guide_files = set(f["path"] for f in inventory["files"])
    linked_files = set()

    print(f"\n[INFO] Validating links in {len(inventory['files'])} files...")

    # First pass: Check INDEX.md
    index_path = Path("docs/guides/INDEX.md")
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            index_content = f.read()

        index_links = extract_links(index_content)
        print(f"[INFO] INDEX.md contains {len(index_links)} links")

        for text, target in index_links:
            # Normalize path
            if target.startswith('http'):
                continue  # Skip external links for now

            # Remove anchors
            target_file = target.split('#')[0]

            if target_file:
                # Try to resolve relative path
                if not target_file.startswith('guides/'):
                    target_file = f"guides/{target_file}"

                linked_files.add(target_file)

                # Check if file exists
                full_path = Path("docs") / target_file
                if not full_path.exists():
                    issues["index_issues"].append({
                        "file": "INDEX.md",
                        "line": "N/A",
                        "link_text": text,
                        "target": target,
                        "issue": "Target file does not exist"
                    })

    # Second pass: Check all files for broken links and dead ends
    for file_info in inventory["files"]:
        file_path = Path("docs") / file_info["path"].replace('guides/', '', 1)

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            content = ''.join(lines)

        links = extract_links(content)

        # Track if file has navigation (related/next/see also links)
        has_navigation = any(re.search(r'(next|previous|see also|related)', text, re.IGNORECASE)
                            for text, _ in links)
        has_navigation = has_navigation or re.search(r'## (Next Steps|See Also|Related|Navigation)', content, re.IGNORECASE)

        if not has_navigation and len(links) < 2:
            issues["dead_ends"].append({
                "file": file_info["path"],
                "link_count": len(links),
                "issue": "No navigation links to related content"
            })

        # Check each link
        for text, target in links:
            # Skip external links
            if target.startswith('http'):
                continue

            # Skip anchors only
            if target.startswith('#'):
                continue

            # Remove anchors
            target_file = target.split('#')[0]

            if not target_file:
                continue

            # Resolve relative path
            if target_file.startswith('/'):
                target_path = Path("docs") / target_file.lstrip('/')
            elif target_file.startswith('../'):
                # Relative to current file
                target_path = file_path.parent / target_file
            else:
                # Relative to current file
                target_path = file_path.parent / target_file

            # Normalize
            try:
                target_path = target_path.resolve()
            except:
                pass

            # Check existence
            if not target_path.exists():
                # Find line number
                line_num = "N/A"
                for idx, line in enumerate(lines, 1):
                    if target in line:
                        line_num = idx
                        break

                issues["broken_links"].append({
                    "file": file_info["path"],
                    "line": line_num,
                    "link_text": text,
                    "target": target,
                    "resolved_path": str(target_path),
                    "issue": "Target file not found"
                })

    # Check for orphaned files (not linked from INDEX.md)
    for file_path in all_guide_files:
        # INDEX.md and README.md are entry points, not orphans
        filename = Path(file_path).name
        if filename in ["INDEX.md", "README.md"]:
            continue

        if file_path not in linked_files:
            issues["orphaned_files"].append({
                "file": file_path,
                "issue": "Not linked from INDEX.md or any README.md"
            })

    # Save broken links CSV
    csv_path = Path(".artifacts/qa_audits/MA-01_GUIDES_AUDIT_2025-11-10/guides_broken_links.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        if issues["broken_links"]:
            writer = csv.DictWriter(f, fieldnames=["file", "line", "link_text", "target", "resolved_path", "issue"])
            writer.writeheader()
            writer.writerows(issues["broken_links"])

    print(f"\n[OK] Broken links: {len(issues['broken_links'])}")
    print(f"[OK] Orphaned files: {len(issues['orphaned_files'])}")
    print(f"[OK] Dead ends: {len(issues['dead_ends'])}")
    print(f"[OK] INDEX.md issues: {len(issues['index_issues'])}")

    # Generate navigation issues report
    report_path = Path(".artifacts/qa_audits/MA-01_GUIDES_AUDIT_2025-11-10/guides_navigation_issues.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# docs/guides/ Navigation Issues\n\n")
        f.write(f"**Audit Date:** November 10, 2025\n\n")
        f.write("---\n\n")

        f.write(f"## Summary\n\n")
        f.write(f"- Broken links: {len(issues['broken_links'])}\n")
        f.write(f"- Orphaned files: {len(issues['orphaned_files'])}\n")
        f.write(f"- Dead ends: {len(issues['dead_ends'])}\n")
        f.write(f"- INDEX.md issues: {len(issues['index_issues'])}\n\n")

        if issues['broken_links']:
            f.write(f"## Broken Links ({len(issues['broken_links'])})\n\n")
            f.write("| File | Line | Link Text | Target | Issue |\n")
            f.write("|------|------|-----------|--------|-------|\n")
            for item in issues['broken_links'][:20]:  # Limit to first 20
                f.write(f"| {item['file']} | {item['line']} | {item['link_text'][:30]} | {item['target']} | {item['issue']} |\n")
            if len(issues['broken_links']) > 20:
                f.write(f"\n...and {len(issues['broken_links']) - 20} more\n")

        if issues['orphaned_files']:
            f.write(f"\n## Orphaned Files ({len(issues['orphaned_files'])})\n\n")
            f.write("| File | Issue |\n")
            f.write("|------|-------|\n")
            for item in issues['orphaned_files']:
                f.write(f"| {item['file']} | {item['issue']} |\n")

        if issues['dead_ends']:
            f.write(f"\n## Dead Ends ({len(issues['dead_ends'])})\n\n")
            f.write("| File | Links | Issue |\n")
            f.write("|------|-------|-------|\n")
            for item in issues['dead_ends'][:20]:
                f.write(f"| {item['file']} | {item['link_count']} | {item['issue']} |\n")

        if issues['index_issues']:
            f.write(f"\n## INDEX.md Issues ({len(issues['index_issues'])})\n\n")
            f.write("| Link Text | Target | Issue |\n")
            f.write("|-----------|--------|-------|\n")
            for item in issues['index_issues']:
                f.write(f"| {item['link_text'][:30]} | {item['target']} | {item['issue']} |\n")

    print(f"[OK] Saved to: {csv_path}")
    print(f"[OK] Saved to: {report_path}")

    return issues

if __name__ == "__main__":
    validate_links()
