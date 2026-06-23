#!/usr/bin/env python
"""
MA-01 Batch Metrics Runner
Runs calculate_file_metrics on all 62 guides files
Outputs: guides_metrics.json, guides_ranked.csv
"""

import json
import csv
from pathlib import Path
import sys

# Import the single file analyzer
sys.path.insert(0, str(Path(__file__).parent))
from calculate_file_metrics import analyze_file

def batch_analyze():
    """Analyze all files in docs/guides/"""

    # Load inventory
    inventory_path = Path(".artifacts/qa_audits/MA-01_GUIDES_AUDIT_2025-11-10/guides_inventory.json")
    with open(inventory_path, 'r', encoding='utf-8') as f:
        inventory = json.load(f)

    all_metrics = {
        "audit_metadata": inventory["audit_metadata"],
        "overall_scores": {
            "completeness": 0,
            "accuracy": 0,
            "readability": 0,
            "overall": 0
        },
        "per_subcategory_scores": {},
        "per_file_metrics": [],
        "file_rankings": {
            "top_5": [],
            "bottom_5": [],
            "all_files_ranked": []
        }
    }

    # Initialize subcategory tracking
    subcategories = ["api", "features", "how-to", "interactive", "theory", "tutorials", "workflows", "root"]
    for subcat in subcategories:
        all_metrics["per_subcategory_scores"][subcat] = {
            "completeness": 0,
            "accuracy": 0,
            "readability": 0,
            "overall": 0,
            "file_count": 0
        }

    print(f"\n[INFO] Analyzing {len(inventory['files'])} files...")

    # Analyze each file
    for idx, file_info in enumerate(inventory['files'], 1):
        file_path = Path("docs") / file_info['path'].replace('guides/', '', 1)

        print(f"[{idx}/{len(inventory['files'])}] {file_info['path']}...", end=" ")

        try:
            metrics = analyze_file(file_path)

            # Add file metadata
            metrics["metadata"] = {
                "path": file_info['path'],
                "subcategory": file_info['subcategory'],
                "type": file_info['type'],
                "lines": file_info['lines'],
                "words": file_info['words']
            }

            # Ensure all values are JSON-serializable (convert any non-standard types)
            metrics = json.loads(json.dumps(metrics, default=str))

            all_metrics["per_file_metrics"].append(metrics)

            # Update subcategory totals
            subcat = file_info['subcategory']
            all_metrics["per_subcategory_scores"][subcat]["completeness"] += metrics["completeness"]["score"]
            all_metrics["per_subcategory_scores"][subcat]["accuracy"] += metrics["accuracy"]["score"]
            all_metrics["per_subcategory_scores"][subcat]["readability"] += metrics["readability"]["score"]
            all_metrics["per_subcategory_scores"][subcat]["overall"] += metrics["overall"]
            all_metrics["per_subcategory_scores"][subcat]["file_count"] += 1

            # Update overall totals
            all_metrics["overall_scores"]["completeness"] += metrics["completeness"]["score"]
            all_metrics["overall_scores"]["accuracy"] += metrics["accuracy"]["score"]
            all_metrics["overall_scores"]["readability"] += metrics["readability"]["score"]
            all_metrics["overall_scores"]["overall"] += metrics["overall"]

            print(f"{metrics['overall']}/100")

        except Exception as e:
            print(f"[ERROR] {str(e)}")

    # Calculate averages
    total_files = len(inventory['files'])
    if total_files > 0:
        all_metrics["overall_scores"]["completeness"] = round(all_metrics["overall_scores"]["completeness"] / total_files, 1)
        all_metrics["overall_scores"]["accuracy"] = round(all_metrics["overall_scores"]["accuracy"] / total_files, 1)
        all_metrics["overall_scores"]["readability"] = round(all_metrics["overall_scores"]["readability"] / total_files, 1)
        all_metrics["overall_scores"]["overall"] = round(all_metrics["overall_scores"]["overall"] / total_files, 1)

    # Calculate subcategory averages
    for subcat in subcategories:
        count = all_metrics["per_subcategory_scores"][subcat]["file_count"]
        if count > 0:
            all_metrics["per_subcategory_scores"][subcat]["completeness"] = round(
                all_metrics["per_subcategory_scores"][subcat]["completeness"] / count, 1)
            all_metrics["per_subcategory_scores"][subcat]["accuracy"] = round(
                all_metrics["per_subcategory_scores"][subcat]["accuracy"] / count, 1)
            all_metrics["per_subcategory_scores"][subcat]["readability"] = round(
                all_metrics["per_subcategory_scores"][subcat]["readability"] / count, 1)
            all_metrics["per_subcategory_scores"][subcat]["overall"] = round(
                all_metrics["per_subcategory_scores"][subcat]["overall"] / count, 1)

    # Rank files
    ranked = sorted(all_metrics["per_file_metrics"], key=lambda x: x["overall"], reverse=True)
    all_metrics["file_rankings"]["all_files_ranked"] = [
        {
            "rank": idx + 1,
            "path": m["metadata"]["path"],
            "overall": m["overall"],
            "completeness": m["completeness"]["score"],
            "accuracy": m["accuracy"]["score"],
            "readability": m["readability"]["score"]
        }
        for idx, m in enumerate(ranked)
    ]

    all_metrics["file_rankings"]["top_5"] = all_metrics["file_rankings"]["all_files_ranked"][:5]
    all_metrics["file_rankings"]["bottom_5"] = all_metrics["file_rankings"]["all_files_ranked"][-5:]

    # Save JSON
    metrics_path = Path(".artifacts/qa_audits/MA-01_GUIDES_AUDIT_2025-11-10/guides_metrics.json")
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(all_metrics, f, indent=2)

    print(f"\n[OK] Metrics saved to: {metrics_path}")

    # Save CSV ranking
    csv_path = Path(".artifacts/qa_audits/MA-01_GUIDES_AUDIT_2025-11-10/guides_ranked.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["rank", "path", "overall", "completeness", "accuracy", "readability"])
        writer.writeheader()
        writer.writerows(all_metrics["file_rankings"]["all_files_ranked"])

    print(f"[OK] Rankings saved to: {csv_path}")

    # Print summary
    print(f"\n=== OVERALL SCORES ===")
    print(f"Completeness: {all_metrics['overall_scores']['completeness']}/100")
    print(f"Accuracy:     {all_metrics['overall_scores']['accuracy']}/100")
    print(f"Readability:  {all_metrics['overall_scores']['readability']}/100")
    print(f"OVERALL:      {all_metrics['overall_scores']['overall']}/100")

    print(f"\n=== TOP 5 FILES ===")
    for item in all_metrics["file_rankings"]["top_5"]:
        print(f"{item['rank']}. {item['path']}: {item['overall']}/100")

    print(f"\n=== BOTTOM 5 FILES ===")
    for item in all_metrics["file_rankings"]["bottom_5"]:
        print(f"{item['rank']}. {item['path']}: {item['overall']}/100")

    return all_metrics

if __name__ == "__main__":
    batch_analyze()
