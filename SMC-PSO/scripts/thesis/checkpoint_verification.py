#!/usr/bin/env python3
"""
Thesis Verification Checkpoint Manager
======================================

Manages session checkpoints for the LT-8 thesis verification project.
Enables recovery from token limits, interruptions, and multi-day gaps.

Usage:
    python checkpoint_verification.py --save                    # Save current state
    python checkpoint_verification.py --status                  # Show current status
    python checkpoint_verification.py --resume                  # Resume from last checkpoint
    python checkpoint_verification.py --list                    # List all checkpoints
    python checkpoint_verification.py --show CHECKPOINT_FILE    # Show checkpoint details

Author: Claude Code (LT-8 Project)
Created: 2025-11-05
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import sys

# ==============================================================================
# Constants
# ==============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT_DIR = PROJECT_ROOT / ".artifacts" / "thesis" / "checkpoints"
ISSUES_DIR = PROJECT_ROOT / ".artifacts" / "thesis" / "issues"
REPORTS_DIR = PROJECT_ROOT / ".artifacts" / "thesis" / "reports"
THESIS_DIR = PROJECT_ROOT / "docs" / "thesis" / "chapters"

# Chapter metadata
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
    {"num": "R", "title": "References", "file": "references.md"},
]

# ==============================================================================
# Checkpoint Data Structures
# ==============================================================================

def create_checkpoint(
    phase: str,
    stage: str,
    chapters_complete: List[int],
    chapters_in_progress: List[int],
    issues_found: int,
    issues_fixed: int,
    hours_invested: float,
    notes: str = "",
) -> Dict[str, Any]:
    """Create a checkpoint data structure."""

    # Calculate issue breakdown (load from issue files)
    issue_summary = _load_issue_summary()

    # Calculate progress
    total_chapters = len(CHAPTERS)
    progress_pct = len(chapters_complete) / total_chapters * 100

    checkpoint = {
        "task_id": "LT-8",
        "checkpoint_version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "phase": {
            "current": phase,
            "stage": stage,
        },
        "progress": {
            "chapters_complete": chapters_complete,
            "chapters_in_progress": chapters_in_progress,
            "chapters_remaining": _get_remaining_chapters(chapters_complete, chapters_in_progress),
            "progress_percentage": round(progress_pct, 1),
        },
        "issues": {
            "total_found": issues_found,
            "total_fixed": issues_fixed,
            "pending": issues_found - issues_fixed,
            "by_severity": issue_summary.get("by_severity", {}),
            "by_category": issue_summary.get("by_category", {}),
        },
        "time_tracking": {
            "total_hours": hours_invested,
            "estimated_remaining_hours": _estimate_remaining_hours(chapters_complete, chapters_in_progress),
        },
        "notes": notes,
    }

    return checkpoint


def _load_issue_summary() -> Dict[str, Any]:
    """Load and summarize all issues from issue files."""
    if not ISSUES_DIR.exists():
        return {"by_severity": {}, "by_category": {}}

    by_severity = {"CRITICAL": 0, "MAJOR": 0, "MINOR": 0}
    by_category = {}

    for issue_file in ISSUES_DIR.glob("chapter_*.json"):
        try:
            with open(issue_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for issue in data.get("issues", []):
                    severity = issue.get("severity", "MINOR")
                    category = issue.get("category", "Other")
                    by_severity[severity] = by_severity.get(severity, 0) + 1
                    by_category[category] = by_category.get(category, 0) + 1
        except Exception:
            continue

    return {"by_severity": by_severity, "by_category": by_category}


def _get_remaining_chapters(complete: List[int], in_progress: List[int]) -> List[str]:
    """Get list of remaining chapter numbers."""
    done = set(complete + in_progress)
    all_nums = [ch["num"] for ch in CHAPTERS]
    remaining = [str(n) for n in all_nums if n not in done]
    return remaining


def _estimate_remaining_hours(complete: List[int], in_progress: List[int]) -> float:
    """Estimate remaining hours based on chapter complexity."""
    # Time estimates per chapter (from roadmap)
    chapter_hours = {
        0: 3.5, 1: 2.5, 2: 4.5, 3: 7, 4: 7, 5: 4.5,
        6: 4.5, 7: 3.5, 8: 5.5, 9: 2.5, "A": 9, "R": 2.5
    }

    done = set(complete)
    remaining_hours = sum(
        hours for ch_num, hours in chapter_hours.items()
        if ch_num not in done
    )

    # Add Phase 2-4 estimates if Phase 1 nearly complete
    if len(complete) >= 10:  # Most chapters done
        remaining_hours += 35  # Phase 2 (15h) + Phase 3 (15h) + Phase 4 (5h)

    return round(remaining_hours, 1)


# ==============================================================================
# Checkpoint Operations
# ==============================================================================

def save_checkpoint(checkpoint: Dict[str, Any], auto: bool = False) -> Path:
    """Save checkpoint to disk and create 'latest' symlink."""
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"checkpoint_{timestamp}.json"
    filepath = CHECKPOINT_DIR / filename

    # Save checkpoint
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, indent=2, ensure_ascii=False)

    # Update 'latest' symlink (or copy on Windows)
    latest_path = CHECKPOINT_DIR / "checkpoint_latest.json"
    try:
        if latest_path.exists():
            latest_path.unlink()
        # On Windows, symlinks may require admin - just copy instead
        import shutil
        shutil.copy(filepath, latest_path)
    except Exception:
        # Fallback: just copy
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)

    label = "[AUTO CHECKPOINT]" if auto else "[CHECKPOINT SAVED]"
    print(f"{label} {filepath.name}")

    return filepath


def load_latest_checkpoint() -> Optional[Dict[str, Any]]:
    """Load the most recent checkpoint."""
    latest_path = CHECKPOINT_DIR / "checkpoint_latest.json"

    if not latest_path.exists():
        return None

    try:
        with open(latest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load checkpoint: {e}", file=sys.stderr)
        return None


def load_checkpoint_by_name(filename: str) -> Optional[Dict[str, Any]]:
    """Load a specific checkpoint by filename."""
    filepath = CHECKPOINT_DIR / filename

    if not filepath.exists():
        print(f"[ERROR] Checkpoint not found: {filename}", file=sys.stderr)
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load checkpoint: {e}", file=sys.stderr)
        return None


def list_checkpoints() -> List[Path]:
    """List all checkpoint files, newest first."""
    if not CHECKPOINT_DIR.exists():
        return []

    checkpoints = sorted(
        CHECKPOINT_DIR.glob("checkpoint_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    # Exclude 'latest' symlink
    return [cp for cp in checkpoints if cp.name != "checkpoint_latest.json"]


# ==============================================================================
# Display Functions
# ==============================================================================

def display_status(checkpoint: Optional[Dict[str, Any]] = None):
    """Display current verification status."""
    if checkpoint is None:
        checkpoint = load_latest_checkpoint()

    if checkpoint is None:
        print("[THESIS VERIFICATION STATUS]")
        print("No checkpoint found. Verification has not started yet.")
        print("")
        print("To start verification:")
        print("  python scripts/thesis/verify_chapter.py --chapter 0")
        return

    # Parse checkpoint data
    phase = checkpoint["phase"]["current"]
    stage = checkpoint["phase"]["stage"]
    progress = checkpoint["progress"]
    issues = checkpoint["issues"]
    time_tracking = checkpoint["time_tracking"]
    timestamp = checkpoint["timestamp"]

    # Format timestamp
    try:
        dt = datetime.fromisoformat(timestamp)
        time_ago = _format_time_ago(dt)
    except Exception:
        time_ago = "unknown"

    # Display
    print("[THESIS VERIFICATION STATUS]")
    print("")
    print(f"Last checkpoint: {time_ago}")
    print(f"Status: {phase}")
    print(f"Current: {stage}")
    print("")
    print("Progress:")
    print(f"  Chapters verified: {len(progress['chapters_complete'])}/12 ({progress['progress_percentage']}%)")
    if progress['chapters_in_progress']:
        print(f"  In progress: Chapter {progress['chapters_in_progress']}")
    print("")
    print("Issues:")
    print(f"  Found: {issues['total_found']} (Fixed: {issues['total_fixed']}, Pending: {issues['pending']})")
    if issues.get('by_severity'):
        sev = issues['by_severity']
        print(f"  Critical: {sev.get('CRITICAL', 0)} | Major: {sev.get('MAJOR', 0)} | Minor: {sev.get('MINOR', 0)}")
    print("")
    print("Time:")
    print(f"  Invested: {time_tracking['total_hours']} hours")
    print(f"  Estimated remaining: {time_tracking.get('estimated_remaining_hours', 'N/A')} hours")
    print("")

    if checkpoint.get('notes'):
        print(f"Notes: {checkpoint['notes']}")
        print("")

    print("To resume:")
    print("  python scripts/thesis/checkpoint_verification.py --resume")


def display_checkpoint_list():
    """Display all checkpoints."""
    checkpoints = list_checkpoints()

    if not checkpoints:
        print("[CHECKPOINT LIST]")
        print("No checkpoints found.")
        return

    print("[CHECKPOINT LIST]")
    print(f"Total checkpoints: {len(checkpoints)}")
    print("")

    for i, cp_path in enumerate(checkpoints, 1):
        try:
            with open(cp_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            timestamp = data.get("timestamp", "unknown")
            stage = data["phase"]["stage"]
            progress_pct = data["progress"]["progress_percentage"]
            issues_pending = data["issues"]["pending"]

            print(f"{i}. {cp_path.name}")
            print(f"   Time: {timestamp}")
            print(f"   Stage: {stage}")
            print(f"   Progress: {progress_pct}% ({issues_pending} issues pending)")
            print("")
        except Exception:
            print(f"{i}. {cp_path.name} (failed to load)")
            print("")


def display_checkpoint_details(checkpoint: Dict[str, Any]):
    """Display full checkpoint details."""
    print("[CHECKPOINT DETAILS]")
    print("")
    print(json.dumps(checkpoint, indent=2, ensure_ascii=False))


def display_resume_context(checkpoint: Dict[str, Any]):
    """Display context for resuming work."""
    phase = checkpoint["phase"]["current"]
    stage = checkpoint["phase"]["stage"]
    progress = checkpoint["progress"]
    issues = checkpoint["issues"]
    timestamp = checkpoint["timestamp"]

    try:
        dt = datetime.fromisoformat(timestamp)
        time_ago = _format_time_ago(dt)
    except Exception:
        time_ago = "unknown"

    print("[THESIS VERIFICATION RESUMED]")
    print("")
    print(f"Last checkpoint: {time_ago}")
    print(f"Resuming: {stage}")
    print("")
    print("Context:")

    # Show completed chapters
    if progress['chapters_complete']:
        completed_names = [
            f"Ch {ch['num']}" for ch in CHAPTERS if ch['num'] in progress['chapters_complete']
        ]
        print(f"  Chapters verified: {', '.join(completed_names)}")

    # Show in-progress chapters
    if progress['chapters_in_progress']:
        in_prog_names = [
            f"Ch {ch['num']}" for ch in CHAPTERS if ch['num'] in progress['chapters_in_progress']
        ]
        print(f"  In progress: {', '.join(in_prog_names)}")

    # Show issues
    print(f"  Issues pending: {issues['pending']} (see .artifacts/thesis/issues/)")
    print("")

    print("Next actions:")
    print("  1. Review current chapter status")
    print("  2. Continue verification from last point")
    print("  3. Use automated tools: python scripts/thesis/verify_chapter.py --chapter N")
    print("")


def _format_time_ago(dt: datetime) -> str:
    """Format datetime as 'X hours/days ago'."""
    now = datetime.now()
    delta = now - dt

    if delta.days > 0:
        return f"{delta.days} day(s) ago"
    elif delta.seconds >= 3600:
        hours = delta.seconds // 3600
        return f"{hours} hour(s) ago"
    elif delta.seconds >= 60:
        minutes = delta.seconds // 60
        return f"{minutes} minute(s) ago"
    else:
        return "just now"


# ==============================================================================
# Main CLI
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Thesis Verification Checkpoint Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--save",
        action="store_true",
        help="Save current state as checkpoint (requires manual input)"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show current verification status"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from last checkpoint"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all checkpoints"
    )
    parser.add_argument(
        "--show",
        metavar="CHECKPOINT_FILE",
        help="Show details of a specific checkpoint"
    )

    args = parser.parse_args()

    # Handle commands
    if args.status:
        display_status()

    elif args.list:
        display_checkpoint_list()

    elif args.show:
        checkpoint = load_checkpoint_by_name(args.show)
        if checkpoint:
            display_checkpoint_details(checkpoint)

    elif args.resume:
        checkpoint = load_latest_checkpoint()
        if checkpoint:
            display_resume_context(checkpoint)
        else:
            print("[ERROR] No checkpoint found to resume from.", file=sys.stderr)
            sys.exit(1)

    elif args.save:
        print("[MANUAL CHECKPOINT SAVE]")
        print("This feature requires interactive input.")
        print("Use automated tools to save checkpoints:")
        print("  python scripts/thesis/verify_chapter.py --chapter N")
        print("")
        print("Or programmatically via Python:")
        print("  from scripts.thesis.checkpoint_verification import save_checkpoint, create_checkpoint")
        print("  checkpoint = create_checkpoint(...)")
        print("  save_checkpoint(checkpoint)")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
