#!/usr/bin/env python3
#==========================================================================================\\\
#======================= simulate_with_issue_tracking.py ===============================\\\
#==========================================================================================\\\
"""
Enhanced simulation wrapper that automatically creates GitHub issues when problems are detected.

This script wraps the main simulate.py CLI and monitors for:
- Stability violations (Lyapunov failures, excessive oscillations)
- PSO convergence failures (stagnation, premature convergence)
- Performance issues (settling time, overshoot violations)
- HIL communication failures
- Test failures and regressions

Usage:
    python .github/scripts/integration/simulate_with_issue_tracking.py --ctrl classical_smc --plot
    python .github/scripts/integration/simulate_with_issue_tracking.py --ctrl adaptive_smc --run-pso
"""

import argparse
import json
import logging
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any

# Add the repository root to path for imports
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DIP_PROJECT = REPO_ROOT
sys.path.insert(0, str(DIP_PROJECT))

try:
    import numpy as np
except ImportError:
    np = None

@dataclass
class IssueReport:
    """Structure for issue creation data."""
    title: str
    issue_type: str  # stability, performance, convergence, implementation
    priority: str    # critical, high, medium, low
    description: str
    reproduction_steps: str
    controller: Optional[str] = None
    labels: List[str] = None
    error_output: Optional[str] = None

class SimulationMonitor:
    """Monitors simulation execution and creates GitHub issues for detected problems."""

    def __init__(self):
        self.create_issue_script = REPO_ROOT / ".github" / "scripts" / "create_issue.sh"
        if not self.create_issue_script.exists():
            self.create_issue_script = REPO_ROOT / ".github" / "scripts" / "create_issue.bat"

        self.issues_created = []

    def run_simulate_with_monitoring(self, args: List[str]) -> int:
        """Run simulate.py with monitoring and issue detection."""
        # Construct command
        simulate_cmd = [sys.executable, str(DIP_PROJECT / "simulate.py")] + args

        logging.info(f"Running simulation: {' '.join(simulate_cmd)}")

        # Execute with monitoring
        start_time = time.time()
        try:
            result = subprocess.run(
                simulate_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            execution_time = time.time() - start_time

            # Monitor results and create issues if needed
            issues = self._analyze_simulation_output(
                result.returncode,
                result.stdout,
                result.stderr,
                args,
                execution_time
            )

            # Create GitHub issues for detected problems
            for issue in issues:
                self._create_github_issue(issue)

            # Print original output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

            return result.returncode

        except subprocess.TimeoutExpired:
            issue = IssueReport(
                title="Simulation timeout - execution exceeded 5 minutes",
                issue_type="performance",
                priority="high",
                description="Simulation failed to complete within reasonable time",
                reproduction_steps=f"Run: {' '.join(simulate_cmd)}",
                controller=self._extract_controller(args),
                labels=["timeout", "performance"]
            )
            self._create_github_issue(issue)
            return 1

        except Exception as e:
            issue = IssueReport(
                title=f"Simulation execution error: {str(e)}",
                issue_type="implementation",
                priority="high",
                description=f"Unexpected error during simulation execution: {str(e)}",
                reproduction_steps=f"Run: {' '.join(simulate_cmd)}",
                controller=self._extract_controller(args),
                labels=["execution-error", "implementation"]
            )
            self._create_github_issue(issue)
            return 1

    def _analyze_simulation_output(self, returncode: int, stdout: str, stderr: str,
                                 args: List[str], execution_time: float) -> List[IssueReport]:
        """Analyze simulation output for issues."""
        issues = []
        controller = self._extract_controller(args)

        # Check for immediate failures
        if returncode != 0:
            issues.append(IssueReport(
                title=f"Simulation failed with exit code {returncode}",
                issue_type="implementation",
                priority="high",
                description=f"Simulation terminated with non-zero exit code",
                reproduction_steps=f"Run: {' '.join(['python', 'simulate.py'] + args)}",
                controller=controller,
                labels=["simulation-failure", "implementation"],
                error_output=stderr
            ))

        # Stability issue detection
        stability_issues = self._detect_stability_issues(stdout, stderr)
        for issue in stability_issues:
            issue.controller = controller
            issues.append(issue)

        # PSO convergence detection (if PSO was run)
        if "--run-pso" in args:
            pso_issues = self._detect_pso_issues(stdout, stderr)
            for issue in pso_issues:
                issue.controller = controller
                issues.append(issue)

        # Performance issue detection
        performance_issues = self._detect_performance_issues(stdout, stderr, execution_time)
        for issue in performance_issues:
            issue.controller = controller
            issues.append(issue)

        # HIL issue detection (if HIL was run)
        if "--run-hil" in args:
            hil_issues = self._detect_hil_issues(stdout, stderr)
            for issue in hil_issues:
                issue.controller = controller
                issues.append(issue)

        return issues

    def _detect_stability_issues(self, stdout: str, stderr: str) -> List[IssueReport]:
        """Detect stability-related issues."""
        issues = []

        # Check for common stability indicators
        if "unstable" in stdout.lower() or "unstable" in stderr.lower():
            issues.append(IssueReport(
                title="Stability violation detected in simulation",
                issue_type="stability",
                priority="critical",
                description="Simulation output indicates system instability",
                reproduction_steps="Re-run simulation with same parameters",
                labels=["stability", "critical"]
            ))

        if "lyapunov" in stdout.lower() and ("violation" in stdout.lower() or "failed" in stdout.lower()):
            issues.append(IssueReport(
                title="Lyapunov stability criterion violation",
                issue_type="stability",
                priority="critical",
                description="Lyapunov analysis indicates potential stability issues",
                reproduction_steps="Re-run simulation with stability analysis enabled",
                labels=["lyapunov", "stability", "critical"]
            ))

        if "chattering" in stdout.lower() or "oscillation" in stdout.lower():
            issues.append(IssueReport(
                title="Excessive chattering or oscillations detected",
                issue_type="stability",
                priority="high",
                description="Control signal shows excessive chattering or oscillatory behavior",
                reproduction_steps="Re-run simulation and analyze control signal plots",
                labels=["chattering", "stability", "high"]
            ))

        return issues

    def _detect_pso_issues(self, stdout: str, stderr: str) -> List[IssueReport]:
        """Detect PSO convergence and optimization issues."""
        issues = []

        if "convergence failed" in stdout.lower() or "stagnation" in stdout.lower():
            issues.append(IssueReport(
                title="PSO convergence failure detected",
                issue_type="convergence",
                priority="critical",
                description="PSO optimization failed to converge or showed stagnation",
                reproduction_steps="Re-run PSO optimization with different parameters",
                labels=["pso", "convergence", "critical"]
            ))

        if "premature convergence" in stdout.lower():
            issues.append(IssueReport(
                title="PSO premature convergence detected",
                issue_type="convergence",
                priority="high",
                description="PSO converged too early, potentially missing global optimum",
                reproduction_steps="Re-run PSO with increased population size or iterations",
                labels=["pso", "premature-convergence", "high"]
            ))

        if "bounds violation" in stdout.lower() or "infeasible" in stdout.lower():
            issues.append(IssueReport(
                title="PSO parameter bounds violation",
                issue_type="parameter-bounds",
                priority="high",
                description="PSO optimization violated parameter bounds or found infeasible solutions",
                reproduction_steps="Check parameter bounds configuration and re-run optimization",
                labels=["pso", "parameter-bounds", "high"]
            ))

        return issues

    def _detect_performance_issues(self, stdout: str, stderr: str, execution_time: float) -> List[IssueReport]:
        """Detect performance-related issues."""
        issues = []

        # Check for slow execution
        if execution_time > 120:  # 2 minutes
            issues.append(IssueReport(
                title=f"Slow simulation execution: {execution_time:.1f}s",
                issue_type="performance",
                priority="medium",
                description=f"Simulation took {execution_time:.1f} seconds, which may indicate performance issues",
                reproduction_steps="Re-run simulation and monitor execution time",
                labels=["performance", "slow-execution", "medium"]
            ))

        # Check for performance violations in output
        if "overshoot" in stdout.lower() and "excessive" in stdout.lower():
            issues.append(IssueReport(
                title="Excessive overshoot detected",
                issue_type="performance",
                priority="high",
                description="Control system showing excessive overshoot beyond acceptable limits",
                reproduction_steps="Re-run simulation and analyze step response",
                labels=["overshoot", "performance", "high"]
            ))

        if "settling time" in stdout.lower() and ("long" in stdout.lower() or "excessive" in stdout.lower()):
            issues.append(IssueReport(
                title="Extended settling time detected",
                issue_type="performance",
                priority="medium",
                description="Control system taking too long to settle to reference",
                reproduction_steps="Re-run simulation and analyze settling behavior",
                labels=["settling-time", "performance", "medium"]
            ))

        return issues

    def _detect_hil_issues(self, stdout: str, stderr: str) -> List[IssueReport]:
        """Detect HIL (Hardware-in-the-Loop) issues."""
        issues = []

        if "communication failed" in stdout.lower() or "connection error" in stderr.lower():
            issues.append(IssueReport(
                title="HIL communication failure",
                issue_type="implementation",
                priority="high",
                description="Failed to establish or maintain communication with HIL hardware",
                reproduction_steps="Check HIL hardware connection and re-run with --run-hil",
                labels=["hil", "communication", "high"]
            ))

        if "real-time constraint" in stdout.lower() and "violated" in stdout.lower():
            issues.append(IssueReport(
                title="HIL real-time constraint violation",
                issue_type="performance",
                priority="critical",
                description="HIL simulation violated real-time execution constraints",
                reproduction_steps="Re-run HIL simulation with performance monitoring",
                labels=["hil", "real-time", "critical"]
            ))

        return issues

    def _extract_controller(self, args: List[str]) -> Optional[str]:
        """Extract controller name from command line arguments."""
        try:
            ctrl_index = args.index("--ctrl")
            if ctrl_index + 1 < len(args):
                return args[ctrl_index + 1]
        except (ValueError, IndexError):
            pass
        return None

    def _create_github_issue(self, issue: IssueReport) -> None:
        """Create a GitHub issue using the create_issue script."""
        try:
            # Prepare command
            cmd = [str(self.create_issue_script)]

            # Add arguments based on issue type
            cmd.extend(["-t", issue.issue_type])
            cmd.extend(["-p", issue.priority])
            cmd.extend(["-T", issue.title])
            cmd.extend(["-d", issue.description])
            cmd.extend(["-r", issue.reproduction_steps])

            if issue.controller:
                cmd.extend(["-c", issue.controller])

            # Execute the issue creation
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✓ Created GitHub issue: {issue.title}")
                self.issues_created.append(issue.title)
            else:
                print(f"✗ Failed to create issue: {issue.title}")
                print(f"Error: {result.stderr}")

        except Exception as e:
            print(f"✗ Error creating issue '{issue.title}': {e}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Enhanced simulation with automatic GitHub issue creation",
        add_help=False  # We'll pass through all args to simulate.py
    )

    # Parse known args to capture our special flags
    parser.add_argument("--no-issue-tracking", action="store_true",
                       help="Disable automatic issue creation")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose monitoring output")

    # Parse known args and pass the rest to simulate.py
    known_args, unknown_args = parser.parse_known_args()

    if known_args.verbose:
        logging.basicConfig(level=logging.INFO)

    # Create monitor and run simulation
    monitor = SimulationMonitor()

    if known_args.no_issue_tracking:
        # Just run simulate.py directly
        simulate_cmd = [sys.executable, str(DIP_PROJECT / "simulate.py")] + unknown_args
        return subprocess.call(simulate_cmd)
    else:
        # Run with monitoring
        return monitor.run_simulate_with_monitoring(unknown_args)

if __name__ == "__main__":
    sys.exit(main())