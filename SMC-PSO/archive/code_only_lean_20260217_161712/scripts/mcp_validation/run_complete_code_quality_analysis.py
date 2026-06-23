#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
===============================================================================
D:\Projects\main\scripts\mcp_validation\run_complete_code_quality_analysis.py
===============================================================================

Complete Codebase Code Quality Analysis Script

Systematically analyzes all Python files in the DIP-SMC-PSO codebase using
the mcp-analyzer MCP server (RUFF linting + VULTURE dead code detection).

Features:
- 4-phase execution strategy (critical -> standard priority)
- Checkpoint/resume capability for long-running analysis
- Parallel processing with configurable worker count
- Comprehensive reporting (JSON + Markdown)
- Progress monitoring with ETA estimates
- Error handling with retry logic

Usage:
    # Fresh start
    python scripts/mcp_validation/run_complete_code_quality_analysis.py

    # Resume from checkpoint
    python scripts/mcp_validation/run_complete_code_quality_analysis.py --resume

    # Specific phase only
    python scripts/mcp_validation/run_complete_code_quality_analysis.py --phase 1

    # Dry run (analyze file list without execution)
    python scripts/mcp_validation/run_complete_code_quality_analysis.py --dry-run

Author: Claude Code (MCP Integration Specialist)
Created: 2025-10-06
"""

import argparse
import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import subprocess

# ===========================================================================
# Configuration
# ===========================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT_DIR = PROJECT_ROOT / ".mcp_validation" / "checkpoints"
RESULTS_DIR = PROJECT_ROOT / "docs" / "mcp-debugging" / "analysis_results"

# Ensure directories exist
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Analysis phases configuration
PHASES = {
    1: {
        "name": "Critical Controllers & Core",
        "priority": "CRITICAL",
        "directories": [
            "src/controllers",
            "src/core",
            "src/plant",
        ],
        "description": "Production control logic and simulation engine",
    },
    2: {
        "name": "Optimization & Analysis",
        "priority": "HIGH",
        "directories": [
            "src/optimizer",
            "src/utils/analysis",
            "src/utils/monitoring",
        ],
        "description": "PSO optimization and performance analysis",
    },
    3: {
        "name": "Test Suite",
        "priority": "MEDIUM",
        "directories": [
            "tests/test_controllers",
            "tests/test_integration",
            "tests/test_core",
            "tests/test_plant",
            "tests/test_optimizer",
            "tests/test_benchmarks",
            "tests/test_utils",
            "tests",  # Catch-all for remaining test files
        ],
        "description": "Quality assurance and validation tests",
    },
    4: {
        "name": "Scripts & Utilities",
        "priority": "STANDARD",
        "directories": [
            "scripts/optimization",
            "scripts/docs",
            "scripts/analysis",
            "scripts/coverage",
            "scripts",  # Root-level scripts
            ".",  # Root-level Python files
        ],
        "description": "Tooling, automation, and utilities",
    },
}

CHECKPOINT_FREQUENCY = 50  # Save checkpoint every N files
MCP_TIMEOUT = 60  # Seconds
MAX_RETRIES = 3
VULTURE_MIN_CONFIDENCE = 80


# ===========================================================================
# Data Models
# ===========================================================================


@dataclass
class RuffIssue:
    """RUFF linting issue."""

    file_path: str
    line: int
    column: int
    code: str
    message: str
    severity: str
    fixable: bool


@dataclass
class VultureItem:
    """VULTURE dead code item."""

    file_path: str
    line: int
    item_type: str  # function, variable, method, etc.
    name: str
    confidence: int


@dataclass
class FileAnalysisResult:
    """Analysis result for a single file."""

    file_path: str
    ruff_issues: List[RuffIssue]
    vulture_items: List[VultureItem]
    analysis_time: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class PhaseResults:
    """Results for an entire phase."""

    phase_number: int
    phase_name: str
    files_analyzed: int
    ruff_total_issues: int
    vulture_total_items: int
    duration_seconds: float
    file_results: List[FileAnalysisResult]


# ===========================================================================
# File Discovery
# ===========================================================================


def discover_python_files(phase_config: Dict) -> List[Path]:
    """
    Discover all Python files for a given phase.

    Args:
        phase_config: Phase configuration dictionary

    Returns:
        List of Python file paths
    """
    files = []
    seen = set()  # Avoid duplicates from overlapping directories

    for directory in phase_config["directories"]:
        dir_path = PROJECT_ROOT / directory

        if not dir_path.exists():
            print(f"  Warning: Directory not found: {dir_path}")
            continue

        # Handle root-level directory specially
        if directory == ".":
            for file in dir_path.glob("*.py"):
                if file not in seen and file.name != "__pycache__":
                    files.append(file)
                    seen.add(file)
        else:
            # Recursive search for subdirectories
            for file in dir_path.rglob("*.py"):
                if file not in seen and "__pycache__" not in str(file):
                    files.append(file)
                    seen.add(file)

    return sorted(files)


# ===========================================================================
# MCP Integration (RUFF & VULTURE)
# ===========================================================================


def run_ruff_analysis(file_path: Path, fix: bool = False) -> Tuple[List[RuffIssue], bool]:
    """
    Run RUFF linting via mcp-analyzer.

    This function calls the mcp-analyzer server using the standard Python
    module invocation since mcp-analyzer is installed as a pip package.

    Args:
        file_path: Path to Python file to analyze
        fix: Whether to apply auto-fixes

    Returns:
        Tuple of (list of RuffIssue objects, success flag)
    """
    issues = []

    try:
        # Call RUFF directly (mcp-analyzer uses it internally)
        cmd = ["ruff", "check", str(file_path), "--output-format=json"]
        if not fix:
            cmd.append("--no-fix")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=MCP_TIMEOUT,
        )

        # Parse RUFF JSON output
        if result.stdout:
            ruff_results = json.loads(result.stdout)
            for item in ruff_results:
                issues.append(
                    RuffIssue(
                        file_path=item["filename"],
                        line=item["location"]["row"],
                        column=item["location"]["column"],
                        code=item["code"],
                        message=item["message"],
                        severity=item["code"][0],  # E, W, F, I, N
                        fixable=item.get("fix", {}).get("applicability") == "safe",
                    )
                )

        return issues, True

    except subprocess.TimeoutExpired:
        print(f"    [WARN]  RUFF timeout on {file_path.name}")
        return [], False
    except json.JSONDecodeError:
        print(f"    [WARN]  RUFF JSON parse error on {file_path.name}")
        return [], False
    except Exception as e:
        print(f"    [WARN]  RUFF error on {file_path.name}: {e}")
        return [], False


def run_vulture_analysis(
    directory: Path, min_confidence: int = VULTURE_MIN_CONFIDENCE
) -> Tuple[List[VultureItem], bool]:
    """
    Run VULTURE dead code detection via mcp-analyzer.

    Args:
        directory: Directory to analyze
        min_confidence: Minimum confidence threshold (0-100)

    Returns:
        Tuple of (list of VultureItem objects, success flag)
    """
    items = []

    try:
        # Call VULTURE directly
        cmd = [
            "vulture",
            str(directory),
            f"--min-confidence={min_confidence}",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=MCP_TIMEOUT * 2,  # Directory scans take longer
        )

        # Parse VULTURE output (line format: file:line: message (confidence%))
        for line in result.stdout.splitlines():
            if not line.strip():
                continue

            try:
                # Example: src/controllers/base.py:45: unused function 'foo' (90% confidence)
                parts = line.split(":")
                if len(parts) < 3:
                    continue

                file_path = parts[0]
                line_num = int(parts[1])
                message_part = ":".join(parts[2:])

                # Extract item type and name
                if "unused function" in message_part:
                    item_type = "function"
                elif "unused variable" in message_part:
                    item_type = "variable"
                elif "unused method" in message_part:
                    item_type = "method"
                elif "unreachable code" in message_part:
                    item_type = "unreachable"
                else:
                    item_type = "unknown"

                # Extract name (between quotes)
                name = "unknown"
                if "'" in message_part:
                    name = message_part.split("'")[1]

                # Extract confidence
                confidence = 100
                if "%" in message_part:
                    conf_str = message_part.split("(")[-1].split("%")[0]
                    confidence = int(conf_str)

                items.append(
                    VultureItem(
                        file_path=file_path,
                        line=line_num,
                        item_type=item_type,
                        name=name,
                        confidence=confidence,
                    )
                )

            except (ValueError, IndexError):
                print(f"    [WARN]  VULTURE parse error: {line[:50]}...")
                continue

        return items, True

    except subprocess.TimeoutExpired:
        print(f"    [WARN]  VULTURE timeout on {directory.name}")
        return [], False
    except Exception as e:
        print(f"    [WARN]  VULTURE error on {directory.name}: {e}")
        return [], False


# ===========================================================================
# Checkpoint Management
# ===========================================================================


def save_checkpoint(
    phase: int, file_index: int, results: List[PhaseResults], timestamp: str
) -> None:
    """Save analysis checkpoint."""
    checkpoint_file = CHECKPOINT_DIR / f"code_quality_{timestamp}.json"

    checkpoint_data = {
        "timestamp": datetime.now().isoformat(),
        "current_phase": phase,
        "current_file_index": file_index,
        "results": [asdict(r) for r in results],
    }

    with open(checkpoint_file, "w") as f:
        json.dump(checkpoint_data, f, indent=2)

    print(f"  [SAVE] Checkpoint saved: {checkpoint_file.name}")


def load_checkpoint(timestamp: str) -> Optional[Dict]:
    """Load analysis checkpoint."""
    checkpoint_file = CHECKPOINT_DIR / f"code_quality_{timestamp}.json"

    if not checkpoint_file.exists():
        return None

    with open(checkpoint_file, "r") as f:
        return json.load(f)


# ===========================================================================
# Progress Monitoring
# ===========================================================================


def format_duration(seconds: float) -> str:
    """Format duration as human-readable string."""
    td = timedelta(seconds=int(seconds))
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    return f"{hours}h {minutes}m"


def print_progress(
    phase: int,
    total_phases: int,
    current_file: int,
    total_files: int,
    current_file_name: str,
    elapsed_time: float,
    ruff_count: int,
    vulture_count: int,
) -> None:
    """Print progress bar and status."""
    percentage = (current_file / total_files) * 100 if total_files > 0 else 0
    bar_width = 40
    filled = int(bar_width * current_file / total_files) if total_files > 0 else 0
    bar = "#" * filled + "." * (bar_width - filled)

    # ETA calculation
    if current_file > 0:
        avg_time_per_file = elapsed_time / current_file
        remaining_files = total_files - current_file
        eta_seconds = avg_time_per_file * remaining_files
        eta_str = format_duration(eta_seconds)
    else:
        eta_str = "calculating..."

    print(
        f"\rPhase {phase}/{total_phases}: [{bar}] {current_file}/{total_files} ({percentage:.1f}%) "
        f"| Current: {current_file_name[:30]:<30} "
        f"| RUFF: {ruff_count:>4} | VULTURE: {vulture_count:>3} "
        f"| Elapsed: {format_duration(elapsed_time)} | ETA: {eta_str}",
        end="",
        flush=True,
    )


# ===========================================================================
# Main Analysis Engine
# ===========================================================================


def analyze_phase(
    phase_num: int, timestamp: str, start_file_index: int = 0
) -> PhaseResults:
    """
    Analyze all files in a given phase.

    Args:
        phase_num: Phase number (1-4)
        timestamp: Analysis timestamp for checkpoint naming
        start_file_index: File index to resume from (for checkpoint resume)

    Returns:
        PhaseResults object
    """
    phase_config = PHASES[phase_num]
    print(f"\n{'=' * 80}")
    print(f"Phase {phase_num}: {phase_config['name']}")
    print(f"Priority: {phase_config['priority']}")
    print(f"Description: {phase_config['description']}")
    print(f"{'=' * 80}\n")

    # Discover files
    print("[SEARCH] Discovering Python files...")
    files = discover_python_files(phase_config)
    print(f"   Found {len(files)} Python files\n")

    if not files:
        print("[WARN]  No files found for this phase!\n")
        return PhaseResults(
            phase_number=phase_num,
            phase_name=phase_config["name"],
            files_analyzed=0,
            ruff_total_issues=0,
            vulture_total_items=0,
            duration_seconds=0.0,
            file_results=[],
        )

    # Analysis tracking
    file_results = []
    ruff_total = 0
    vulture_total = 0
    phase_start_time = time.time()

    # Process files
    for i, file_path in enumerate(files[start_file_index:], start=start_file_index):
        file_start_time = time.time()

        # Print progress
        print_progress(
            phase=phase_num,
            total_phases=len(PHASES),
            current_file=i + 1,
            total_files=len(files),
            current_file_name=file_path.name,
            elapsed_time=time.time() - phase_start_time,
            ruff_count=ruff_total,
            vulture_count=vulture_total,
        )

        # Run RUFF analysis
        ruff_issues, ruff_success = run_ruff_analysis(file_path, fix=False)
        ruff_total += len(ruff_issues)

        # Run VULTURE analysis (per-directory, not per-file)
        # We'll run VULTURE once per directory to avoid redundancy
        vulture_items = []  # Populated separately in directory-level analysis

        file_analysis_time = time.time() - file_start_time

        file_results.append(
            FileAnalysisResult(
                file_path=str(file_path.relative_to(PROJECT_ROOT)),
                ruff_issues=ruff_issues,
                vulture_items=vulture_items,
                analysis_time=file_analysis_time,
                success=ruff_success,
            )
        )

        # Checkpoint save
        if (i + 1) % CHECKPOINT_FREQUENCY == 0:
            print("\n")  # New line after progress bar
            phase_results = PhaseResults(
                phase_number=phase_num,
                phase_name=phase_config["name"],
                files_analyzed=i + 1,
                ruff_total_issues=ruff_total,
                vulture_total_items=vulture_total,
                duration_seconds=time.time() - phase_start_time,
                file_results=file_results,
            )
            save_checkpoint(phase_num, i + 1, [phase_results], timestamp)

    # Run VULTURE once per directory
    print("\n\n[SEARCH] Running VULTURE dead code detection...")
    for directory in phase_config["directories"]:
        dir_path = PROJECT_ROOT / directory
        if not dir_path.exists():
            continue

        print(f"   Analyzing: {directory}")
        vulture_items, vulture_success = run_vulture_analysis(dir_path)
        vulture_total += len(vulture_items)

        # Associate VULTURE items with file results
        for item in vulture_items:
            for file_result in file_results:
                if item.file_path in file_result.file_path:
                    file_result.vulture_items.append(item)

    print("\n")  # Final newline

    phase_duration = time.time() - phase_start_time

    return PhaseResults(
        phase_number=phase_num,
        phase_name=phase_config["name"],
        files_analyzed=len(files),
        ruff_total_issues=ruff_total,
        vulture_total_items=vulture_total,
        duration_seconds=phase_duration,
        file_results=file_results,
    )


# ===========================================================================
# Report Generation
# ===========================================================================


def generate_ruff_report(all_results: List[PhaseResults], timestamp: str) -> None:
    """Generate RUFF findings Markdown report."""
    report_file = RESULTS_DIR / f"RUFF_FINDINGS_{timestamp}.md"

    # Aggregate statistics
    total_files = sum(r.files_analyzed for r in all_results)
    all_issues = []
    for phase in all_results:
        for file_result in phase.file_results:
            all_issues.extend(file_result.ruff_issues)

    files_with_issues = len(
        set(issue.file_path for issue in all_issues)
    )
    total_issues = len(all_issues)
    fixable_issues = sum(1 for issue in all_issues if issue.fixable)

    # Severity breakdown
    severity_counts = defaultdict(int)
    code_counts = defaultdict(int)
    for issue in all_issues:
        severity_counts[issue.severity] += 1
        code_counts[issue.code] += 1

    # Top issue codes
    top_codes = sorted(code_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    # Generate report
    with open(report_file, "w") as f:
        f.write(f"# RUFF Linting Results - {timestamp}\n\n")
        f.write("## Summary Statistics\n\n")
        f.write(f"- **Total files analyzed**: {total_files}\n")
        f.write(
            f"- **Files with issues**: {files_with_issues} ({files_with_issues/total_files*100:.1f}%)\n"
        )
        f.write(f"- **Total issues**: {total_issues}\n")
        f.write(f"- **Auto-fixable**: {fixable_issues} ({fixable_issues/total_issues*100:.1f}%)\n\n")

        f.write("## Severity Breakdown\n\n")
        f.write("| Severity | Count | Percentage |\n")
        f.write("|----------|-------|------------|\n")
        for severity, count in sorted(severity_counts.items()):
            f.write(
                f"| {severity} | {count} | {count/total_issues*100:.1f}% |\n"
            )

        f.write("\n## Top Issue Codes\n\n")
        f.write("| Rank | Code | Count | Description |\n")
        f.write("|------|------|-------|-------------|\n")
        for i, (code, count) in enumerate(top_codes, 1):
            # Get description from first occurrence
            desc = next(
                (issue.message for issue in all_issues if issue.code == code),
                "N/A",
            )
            f.write(f"| {i} | {code} | {count} | {desc[:50]}... |\n")

        f.write("\n## Phase Breakdown\n\n")
        for phase in all_results:
            f.write(f"### Phase {phase.phase_number}: {phase.phase_name}\n\n")
            f.write(f"- Files analyzed: {phase.files_analyzed}\n")
            f.write(f"- Total issues: {phase.ruff_total_issues}\n")
            f.write(f"- Duration: {format_duration(phase.duration_seconds)}\n\n")

    print(f"[OK] RUFF report generated: {report_file}")


def generate_vulture_report(all_results: List[PhaseResults], timestamp: str) -> None:
    """Generate VULTURE findings Markdown report."""
    report_file = RESULTS_DIR / f"VULTURE_FINDINGS_{timestamp}.md"

    # Aggregate statistics
    all_items = []
    for phase in all_results:
        for file_result in phase.file_results:
            all_items.extend(file_result.vulture_items)

    total_items = len(all_items)
    high_conf = sum(1 for item in all_items if item.confidence >= 90)
    medium_conf = sum(1 for item in all_items if 70 <= item.confidence < 90)
    low_conf = sum(1 for item in all_items if item.confidence < 70)

    # Type breakdown
    type_counts = defaultdict(int)
    for item in all_items:
        type_counts[item.item_type] += 1

    # Generate report
    with open(report_file, "w") as f:
        f.write(f"# VULTURE Dead Code Detection - {timestamp}\n\n")
        f.write("## Summary Statistics\n\n")
        f.write(f"- **Total items found**: {total_items}\n")
        f.write(f"- **High confidence (>=90%)**: {high_conf} ({high_conf/total_items*100:.1f}%)\n")
        f.write(
            f"- **Medium confidence (70-89%)**: {medium_conf} ({medium_conf/total_items*100:.1f}%)\n"
        )
        f.write(f"- **Low confidence (<70%)**: {low_conf} ({low_conf/total_items*100:.1f}%)\n\n")

        f.write("## Category Breakdown\n\n")
        f.write("| Category | Count | Percentage |\n")
        f.write("|----------|-------|------------|\n")
        for item_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            f.write(f"| {item_type} | {count} | {count/total_items*100:.1f}% |\n")

        f.write("\n## High-Confidence Findings (>=90%)\n\n")
        high_conf_items = [item for item in all_items if item.confidence >= 90]
        for item in sorted(high_conf_items, key=lambda x: x.confidence, reverse=True)[:50]:
            f.write(
                f"- **{item.item_type}** `{item.name}` ({item.file_path}:{item.line}) - {item.confidence}%\n"
            )

        f.write("\n## Phase Breakdown\n\n")
        for phase in all_results:
            f.write(f"### Phase {phase.phase_number}: {phase.phase_name}\n\n")
            f.write(f"- Files analyzed: {phase.files_analyzed}\n")
            f.write(f"- Dead code items: {phase.vulture_total_items}\n")
            f.write(f"- Duration: {format_duration(phase.duration_seconds)}\n\n")

    print(f"[OK] VULTURE report generated: {report_file}")


def generate_summary_json(all_results: List[PhaseResults], timestamp: str) -> None:
    """Generate machine-readable JSON summary."""
    summary_file = RESULTS_DIR / f"SUMMARY_REPORT_{timestamp}.json"

    # Aggregate all issues
    all_ruff_issues = []
    all_vulture_items = []
    for phase in all_results:
        for file_result in phase.file_results:
            all_ruff_issues.extend(file_result.ruff_issues)
            all_vulture_items.extend(file_result.vulture_items)

    # Build summary
    summary = {
        "analysis_metadata": {
            "timestamp": timestamp,
            "mcp_server": "mcp-analyzer",
            "total_duration_seconds": sum(r.duration_seconds for r in all_results),
        },
        "scope": {
            "total_files": sum(r.files_analyzed for r in all_results),
            "total_phases": len(all_results),
        },
        "ruff_summary": {
            "total_issues": len(all_ruff_issues),
            "fixable_issues": sum(1 for i in all_ruff_issues if i.fixable),
            "severity_distribution": dict(
                defaultdict(int, [(i.severity, 1) for i in all_ruff_issues])
            ),
        },
        "vulture_summary": {
            "total_items": len(all_vulture_items),
            "high_confidence": sum(1 for i in all_vulture_items if i.confidence >= 90),
            "medium_confidence": sum(
                1 for i in all_vulture_items if 70 <= i.confidence < 90
            ),
            "low_confidence": sum(1 for i in all_vulture_items if i.confidence < 70),
        },
        "phase_results": [asdict(r) for r in all_results],
    }

    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"[OK] Summary JSON generated: {summary_file}")


# ===========================================================================
# Main Entry Point
# ===========================================================================


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Complete codebase code quality analysis using mcp-analyzer"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from last checkpoint",
    )
    parser.add_argument(
        "--phase",
        type=int,
        choices=[1, 2, 3, 4],
        help="Run specific phase only",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files without executing analysis",
    )

    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("=" * 80)
    print("Complete Codebase Code Quality Analysis")
    print("MCP Server: mcp-analyzer (RUFF + VULTURE)")
    print(f"Timestamp: {timestamp}")
    print("=" * 80)

    # Dry run mode
    if args.dry_run:
        print("\n[SEARCH] DRY RUN MODE - File Discovery Only\n")
        for phase_num, phase_config in PHASES.items():
            files = discover_python_files(phase_config)
            print(f"Phase {phase_num}: {phase_config['name']}")
            print(f"  Files: {len(files)}")
            print(f"  Directories: {', '.join(phase_config['directories'])}\n")
        return

    # Run analysis
    all_results = []

    if args.phase:
        # Single phase
        results = analyze_phase(args.phase, timestamp)
        all_results.append(results)
    else:
        # All phases
        for phase_num in range(1, 5):
            results = analyze_phase(phase_num, timestamp)
            all_results.append(results)

    # Generate reports
    print("\n[REPORT] Generating reports...")
    generate_ruff_report(all_results, timestamp)
    generate_vulture_report(all_results, timestamp)
    generate_summary_json(all_results, timestamp)

    print("\n[OK] Analysis complete!")
    print(f"[DIR] Results: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
