#!/usr/bin/env python
"""
MA-01 Inventory Collector
Collects comprehensive inventory of docs/guides/ category
Outputs: guides_inventory.json
"""

import json
import os
from pathlib import Path
from datetime import datetime

def collect_inventory():
    """Collect complete inventory of docs/guides/"""
    guides_dir = Path("docs/guides")

    inventory = {
        "audit_metadata": {
            "category": "docs/guides/",
            "audit_date": datetime.now().isoformat(),
            "auditor": "Claude Code MA-01",
        },
        "files": [],
        "summary": {
            "total_files": 0,
            "total_lines": 0,
            "total_words": 0,
            "by_subcategory": {},
            "by_type": {}
        }
    }

    # Subcategories
    subcategories = ["api", "features", "how-to", "interactive", "theory", "tutorials", "workflows", "root"]

    for subcat in subcategories:
        inventory["summary"]["by_subcategory"][subcat] = {
            "files": 0,
            "lines": 0,
            "words": 0
        }

    # Collect all .md files
    for md_file in sorted(guides_dir.rglob("*.md")):
        rel_path = md_file.relative_to(Path("docs"))

        # Count lines and words
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.count('\n') + 1
            words = len(content.split())

        # Determine subcategory
        parts = md_file.relative_to(guides_dir).parts
        if len(parts) == 1:
            subcat = "root"
        else:
            subcat = parts[0]

        # Categorize file type
        filename = md_file.stem.lower()
        if 'tutorial' in filename:
            file_type = "tutorial"
        elif 'workflow' in filename:
            file_type = "workflow"
        elif filename in ['readme', 'index']:
            file_type = "index"
        elif 'api' in str(md_file.parent):
            file_type = "api_reference"
        elif 'theory' in str(md_file.parent):
            file_type = "theory"
        elif 'how-to' in str(md_file.parent):
            file_type = "how_to_guide"
        elif 'interactive' in str(md_file.parent):
            file_type = "interactive_demo"
        else:
            file_type = "general"

        file_info = {
            "path": str(rel_path),
            "filename": md_file.name,
            "subcategory": subcat,
            "type": file_type,
            "lines": lines,
            "words": words,
            "size_bytes": md_file.stat().st_size,
            "last_modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
        }

        inventory["files"].append(file_info)

        # Update summary
        inventory["summary"]["total_files"] += 1
        inventory["summary"]["total_lines"] += lines
        inventory["summary"]["total_words"] += words
        inventory["summary"]["by_subcategory"][subcat]["files"] += 1
        inventory["summary"]["by_subcategory"][subcat]["lines"] += lines
        inventory["summary"]["by_subcategory"][subcat]["words"] += words

        # Track by type
        if file_type not in inventory["summary"]["by_type"]:
            inventory["summary"]["by_type"][file_type] = {"count": 0, "lines": 0}
        inventory["summary"]["by_type"][file_type]["count"] += 1
        inventory["summary"]["by_type"][file_type]["lines"] += lines

    # Save to JSON
    output_path = Path(".artifacts/qa_audits/MA-01_GUIDES_AUDIT_2025-11-10/guides_inventory.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2)

    print(f"[OK] Inventory collected: {inventory['summary']['total_files']} files")
    print(f"[OK] Total lines: {inventory['summary']['total_lines']:,}")
    print(f"[OK] Total words: {inventory['summary']['total_words']:,}")
    print(f"[OK] Saved to: {output_path}")

    return inventory

if __name__ == "__main__":
    collect_inventory()
