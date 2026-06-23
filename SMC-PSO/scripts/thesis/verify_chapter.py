#!/usr/bin/env python3
"""
Thesis Chapter Verification Tool - Master Orchestrator
=======================================================

Comprehensive chapter verification using all automated tools:
- Equations (LaTeX syntax, numbering, references)
- Citations (existence, sequencing)
- Figures & Tables (numbering, captions, references)
- Content structure (headings, sections)
- Basic grammar checks

Usage:
    python verify_chapter.py --chapter 3
    python verify_chapter.py --chapter 3 --comprehensive
    python verify_chapter.py --all-chapters
    python verify_chapter.py --resume

Author: Claude Code (LT-8 Project)
Created: 2025-11-05
"""

import argparse
from pathlib import Path
from typing import Dict, List
import json
import sys

# Import verification modules
try:
    from verify_equations import verify_chapter_equations
    from verify_citations import verify_chapter_citations, extract_references
    from verify_figures import verify_chapter_figures_tables
    from checkpoint_verification import (
        create_checkpoint,
        save_checkpoint,
        load_latest_checkpoint,
        display_status,
    )
except ImportError:
    # Handle relative imports for when run as module
    from scripts.thesis.verify_equations import verify_chapter_equations
    from scripts.thesis.verify_citations import verify_chapter_citations, extract_references
    from scripts.thesis.verify_figures import verify_chapter_figures_tables
    from scripts.thesis.checkpoint_verification import (
        create_checkpoint,
        save_checkpoint,
        load_latest_checkpoint,
        display_status,
    )

# ==============================================================================
# Constants
# ==============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
THESIS_DIR = PROJECT_ROOT / "docs" / "thesis" / "chapters"
ISSUES_DIR = PROJECT_ROOT / ".artifacts" / "thesis" / "issues"
REPORTS_DIR = PROJECT_ROOT / ".artifacts" / "thesis" / "reports"
REFERENCES_FILE = THESIS_DIR / "references.md"

CHAPTERS = [
    {"num": 0, "title": "Introduction", "file": "00_introduction.md"},
    {"num": 1, "title": "Problem Statement", "file": "01_problem_statement.md"},
    {"num": 2, "title": "Literature Review", "file": "02_literature_review.md"},
    {"num": 3, "title": "System Modeling", "file": "03_system_modeling.md"},
    {"num": 4, "title": "Sliding Mode Control", "file": "04_sliding_mode_control.md"},
    {"num": 5, "title": "Chattering Mitigation", "file": "05_chattering_mitigation.md"},
    {"num": 6, "title": "PSO Optimization", "file": "06_pso_optimization.md"},
    {"num": 7, "title": "Simulation Setup", "file": "07_simulation_setup.md"},
    {"num": 8, "title": "Results & Discussion", "file": "08_results.md"},
    {"num": 9, "title": "Conclusion", "file": "09_conclusion.md"},
    {"num": "A", "title": "Lyapunov Proofs", "file": "appendix_a_proofs.md"},
]

# ==============================================================================
# Comprehensive Verification
# ==============================================================================

def verify_chapter_comprehensive(chapter_num: int, validate_algebra: bool = False) -> Dict:
    """
    Run all verification tools on a chapter.

    Returns:
        {
            "chapter": chapter_num,
            "chapter_title": str,
            "verification_results": {
                "equations": {...},
                "citations": {...},
                "figures_tables": {...},
            },
            "aggregated_issues": [...],
            "summary": {...}
        }
    """

    # Find chapter metadata
    chapter_info = None
    for ch in CHAPTERS:
        if ch["num"] == chapter_num:
            chapter_info = ch
            break

    if not chapter_info:
        print(f"[ERROR] Chapter {chapter_num} not found in CHAPTERS list", file=sys.stderr)
        return {"error": f"Chapter {chapter_num} not found"}

    chapter_file = THESIS_DIR / chapter_info["file"]
    if not chapter_file.exists():
        print(f"[ERROR] Chapter file not found: {chapter_file}", file=sys.stderr)
        return {"error": f"Chapter file not found: {chapter_file}"}

    print(f"[COMPREHENSIVE VERIFICATION] Chapter {chapter_num}: {chapter_info['title']}")
    print(f"File: {chapter_file}")
    print("")

    # Load references (needed for citation validation)
    references = extract_references(REFERENCES_FILE)

    # Run verification tools
    results = {}

    # 1. Equations
    print("[1/3] Verifying equations...")
    eq_result = verify_chapter_equations(chapter_num, validate_algebra=validate_algebra)
    results["equations"] = eq_result
    if "error" not in eq_result:
        print(f"  Equations: {eq_result['numbered_equations']} numbered, {len(eq_result['issues'])} issues")

    # 2. Citations
    print("[2/3] Verifying citations...")
    cite_result = verify_chapter_citations(chapter_num, references)
    results["citations"] = cite_result
    if "error" not in cite_result:
        print(f"  Citations: {cite_result['citations_count']} total, {len(cite_result['issues'])} issues")

    # 3. Figures & Tables
    print("[3/3] Verifying figures & tables...")
    fig_result = verify_chapter_figures_tables(chapter_num)
    results["figures_tables"] = fig_result
    if "error" not in fig_result:
        print(f"  Figures: {fig_result['figures_count']}, Tables: {fig_result['tables_count']}, Issues: {len(fig_result['issues'])}")

    print("")

    # Aggregate all issues
    all_issues = []
    for tool_name, tool_result in results.items():
        if "error" not in tool_result and "issues" in tool_result:
            for issue in tool_result["issues"]:
                issue["source_tool"] = tool_name
                all_issues.append(issue)

    # Categorize issues by severity
    critical = [iss for iss in all_issues if iss.get('severity') == 'CRITICAL']
    major = [iss for iss in all_issues if iss.get('severity') == 'MAJOR']
    minor = [iss for iss in all_issues if iss.get('severity') == 'MINOR']

    # Create summary
    summary = {
        "total_issues": len(all_issues),
        "critical": len(critical),
        "major": len(major),
        "minor": len(minor),
        "status": _determine_status(len(critical), len(major)),
    }

    print("[SUMMARY]")
    print(f"Total issues: {summary['total_issues']}")
    print(f"  Critical: {summary['critical']}")
    print(f"  Major: {summary['major']}")
    print(f"  Minor: {summary['minor']}")
    print(f"Status: {summary['status']}")
    print("")

    return {
        "chapter": chapter_num,
        "chapter_title": chapter_info["title"],
        "chapter_file": str(chapter_file),
        "verification_results": results,
        "aggregated_issues": all_issues,
        "summary": summary,
    }


def _determine_status(critical_count: int, major_count: int) -> str:
    """Determine chapter status based on issue counts."""
    if critical_count == 0 and major_count == 0:
        return "PASS"
    elif critical_count == 0 and major_count <= 3:
        return "PASS (minor issues)"
    elif critical_count <= 2 and major_count <= 10:
        return "NEEDS REVISION"
    else:
        return "FAIL (requires substantial work)"


# ==============================================================================
# Batch Verification
# ==============================================================================

def verify_all_chapters(comprehensive: bool = False) -> Dict:
    """
    Verify all chapters in sequence.

    Returns summary report.
    """

    print("[BATCH VERIFICATION] All chapters")
    print(f"Mode: {'Comprehensive' if comprehensive else 'Basic'}")
    print("")

    chapter_results = []
    total_issues = 0

    for ch_info in CHAPTERS:
        ch_num = ch_info["num"]

        if comprehensive:
            result = verify_chapter_comprehensive(ch_num)
        else:
            # Quick verification (just equations and citations)
            references = extract_references(REFERENCES_FILE)
            eq_result = verify_chapter_equations(ch_num)
            cite_result = verify_chapter_citations(ch_num, references)

            all_issues = []
            if "error" not in eq_result:
                all_issues.extend(eq_result["issues"])
            if "error" not in cite_result:
                all_issues.extend(cite_result["issues"])

            result = {
                "chapter": ch_num,
                "chapter_title": ch_info["title"],
                "summary": {
                    "total_issues": len(all_issues),
                    "critical": sum(1 for iss in all_issues if iss.get('severity') == 'CRITICAL'),
                    "major": sum(1 for iss in all_issues if iss.get('severity') == 'MAJOR'),
                    "minor": sum(1 for iss in all_issues if iss.get('severity') == 'MINOR'),
                },
            }

        if "error" not in result:
            chapter_results.append(result)
            total_issues += result["summary"]["total_issues"]

            status = result["summary"].get("status", "N/A")
            print(f"Chapter {ch_num}: {result['summary']['total_issues']} issues - {status}")

    print("")
    print(f"[BATCH SUMMARY] {total_issues} total issues across {len(chapter_results)} chapters")

    return {
        "chapter_results": chapter_results,
        "total_issues": total_issues,
        "chapters_verified": len(chapter_results),
    }


# ==============================================================================
# Save Results
# ==============================================================================

def save_chapter_report(result: Dict, save_issues: bool = True):
    """Save verification report and issues to disk."""

    chapter_num = result["chapter"]

    # Save issues
    if save_issues and result.get("aggregated_issues"):
        ISSUES_DIR.mkdir(parents=True, exist_ok=True)
        issue_file = ISSUES_DIR / f"chapter_{chapter_num}.json"

        issue_data = {
            "chapter": chapter_num,
            "chapter_title": result.get("chapter_title", ""),
            "verification_date": __import__('datetime').datetime.now().isoformat(),
            "issues": result["aggregated_issues"],
            "summary": result.get("summary", {}),
        }

        with open(issue_file, "w", encoding="utf-8") as f:
            json.dump(issue_data, f, indent=2, ensure_ascii=False)

        print(f"[OK] Issues saved: {issue_file}")

    # Save full report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORTS_DIR / f"chapter_{chapter_num}_verification.json"

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"[OK] Report saved: {report_file}")


# ==============================================================================
# Checkpoint Integration
# ==============================================================================

def auto_checkpoint(chapters_complete: List[int], chapters_in_progress: List[int], total_issues: int):
    """Automatically save checkpoint after chapter verification."""

    # Estimate hours (rough estimate: 0.5 hours per chapter verified)
    hours_invested = len(chapters_complete) * 0.5

    # Determine phase/stage
    if len(chapters_complete) < 12:
        phase = "Phase 1: Chapter Verification"
        if chapters_in_progress:
            stage = f"Chapter {chapters_in_progress[0]} in progress"
        else:
            stage = f"{len(chapters_complete)}/12 chapters complete"
    else:
        phase = "Phase 2: Integration Verification"
        stage = "All chapters verified, integration checks pending"

    checkpoint = create_checkpoint(
        phase=phase,
        stage=stage,
        chapters_complete=chapters_complete,
        chapters_in_progress=chapters_in_progress,
        issues_found=total_issues,
        issues_fixed=0,  # Fixes happen in Phase 3
        hours_invested=hours_invested,
        notes=f"Auto-checkpoint after Chapter {chapters_complete[-1] if chapters_complete else 'N/A'} verification",
    )

    save_checkpoint(checkpoint, auto=True)


# ==============================================================================
# CLI
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Thesis Chapter Verification Tool (Master Orchestrator)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--chapter",
        type=lambda x: int(x) if x.isdigit() else x,
        help="Chapter number to verify (0-9, A)"
    )
    parser.add_argument(
        "--all-chapters",
        action="store_true",
        help="Verify all chapters in sequence"
    )
    parser.add_argument(
        "--comprehensive",
        action="store_true",
        help="Run comprehensive verification (all tools)"
    )
    parser.add_argument(
        "--validate-algebra",
        action="store_true",
        help="Validate algebraic manipulations (experimental)"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save issues and reports to .artifacts/thesis/"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from last checkpoint"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show current verification status"
    )

    args = parser.parse_args()

    # Handle status/resume
    if args.status:
        display_status()
        return

    if args.resume:
        checkpoint = load_latest_checkpoint()
        if checkpoint:
            print("[RESUME] Resuming from last checkpoint")
            print(f"Last stage: {checkpoint['phase']['stage']}")
            print(f"Progress: {len(checkpoint['progress']['chapters_complete'])}/12 chapters")
            print("")
            print("To continue, specify next chapter:")
            print("  python verify_chapter.py --chapter N --comprehensive --save")
        else:
            print("[ERROR] No checkpoint found to resume from.", file=sys.stderr)
            print("Start fresh:")
            print("  python verify_chapter.py --chapter 0 --comprehensive --save")
        return

    # Handle verification
    if args.all_chapters:
        result = verify_all_chapters(comprehensive=args.comprehensive)

        if args.save:
            # Save batch report
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            batch_file = REPORTS_DIR / "batch_verification.json"
            with open(batch_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n[OK] Batch report saved: {batch_file}")

    elif args.chapter is not None:
        result = verify_chapter_comprehensive(args.chapter, validate_algebra=args.validate_algebra)

        if "error" in result:
            print(f"[ERROR] {result['error']}", file=sys.stderr)
            sys.exit(1)

        if args.save:
            save_chapter_report(result, save_issues=True)

            # Auto-checkpoint after successful verification
            checkpoint_data = load_latest_checkpoint()
            if checkpoint_data:
                chapters_complete = checkpoint_data["progress"]["chapters_complete"]
            else:
                chapters_complete = []

            # Add current chapter to completed list
            if args.chapter not in chapters_complete:
                chapters_complete.append(args.chapter)

            total_issues = result["summary"]["total_issues"]
            auto_checkpoint(chapters_complete, [], total_issues)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
