#!/usr/bin/env python3
#==========================================================================================\\\
#========================= create_prompt_issues.py =====================================\\\
#==========================================================================================\\\
"""
Create GitHub issues from documented problems in the prompt/ folder.

This script systematically creates GitHub issues based on the comprehensive test analysis
and failure documentation found in the prompt directory.

Usage:
    python .github/scripts/create_prompt_issues.py
    python .github/scripts/create_prompt_issues.py --dry-run
    python .github/scripts/create_prompt_issues.py --category stability
"""

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

# Project paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROMPT_DIR = REPO_ROOT / "prompt"

@dataclass
class IssueSpec:
    """Specification for creating a GitHub issue."""
    title: str
    issue_type: str  # stability, performance, convergence, implementation
    priority: str    # critical, high, medium, low
    description: str
    reproduction_steps: str
    controller: Optional[str] = None
    test_file: Optional[str] = None
    labels: List[str] = None
    source_file: Optional[str] = None

class PromptIssueCreator:
    """Creates GitHub issues from documented problems in prompt folder."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.create_issue_script = REPO_ROOT / ".github" / "scripts" / "create_issue.sh"
        if not self.create_issue_script.exists():
            self.create_issue_script = REPO_ROOT / ".github" / "scripts" / "create_issue.bat"

        self.issues_created = []

    def create_all_documented_issues(self, category_filter: Optional[str] = None) -> int:
        """Create all issues documented in the prompt folder."""
        print("Creating GitHub issues from prompt folder documentation...")

        # Define all documented issues
        issues = self._get_documented_issues()

        # Filter by category if specified
        if category_filter:
            issues = [issue for issue in issues if issue.issue_type == category_filter]

        if not issues:
            print("No issues to create (or filtered out)")
            return 0

        print(f"Creating {len(issues)} GitHub issues")

        success_count = 0
        for issue in issues:
            if self._create_github_issue(issue):
                success_count += 1

        print(f"\nSuccessfully created {success_count} issues")
        if self.dry_run:
            print("This was a DRY RUN - no issues were actually created")

        return 0 if success_count > 0 else 1

    def _get_documented_issues(self) -> List[IssueSpec]:
        """Get all documented issues from the analysis."""
        issues = []

        # 1. CRITICAL STABILITY ISSUES
        issues.extend([
            IssueSpec(
                title="[CRITICAL] Fault Detection Infrastructure Failures",
                issue_type="stability",
                priority="critical",
                description="""
**Critical fault detection system failures identified in comprehensive testing:**

## Failed Components

### Residual Generation Issues
- `TestResidualGeneration::test_residual_with_weights` - Residual amplification not working (0.90 < 1.0)
- Weighted residual computation failing to amplify fault signals

### Threshold Adaptation Problems
- `TestThresholdAdaptation::test_fixed_threshold_operation` - Status returning 'FAULT' instead of 'OK'
- Threshold logic incorrectly triggering false positives

### CUSUM Drift Detection Failures
- `TestCUSUMDriftDetection::test_cusum_drift_detection` - CUSUM not detecting slow drift
- `TestCUSUMDriftDetection::test_cusum_reset_behavior` - CUSUM values not resetting properly
- Critical for detecting gradual system degradation

### History Recording Issues
- `TestFaultDetectionRobustness::test_history_recording` - History length mismatch (9 vs 10)
- Data integrity problems in fault detection logs

## Safety Impact
**SAFETY CRITICAL**: These failures compromise the system's ability to detect faults and ensure safe operation.

## Source Documentation
Based on analysis in `prompt/pytest_analysis_report.md` and detailed test logs.
""",
                reproduction_steps="""
1. Run fault detection tests: `pytest tests/test_analysis/fault_detection/ -v`
2. Observe specific test failures in residual generation and threshold adaptation
3. Check CUSUM algorithm behavior with slow drift scenarios
4. Verify history recording length consistency
""",
                test_file="tests/test_analysis/fault_detection/",
                labels=["critical", "safety", "fault-detection", "stability"],
                source_file="prompt/pytest_analysis_report.md"
            ),

            IssueSpec(
                title="[CRITICAL] Sliding Mode Control Mathematical Property Failures",
                issue_type="stability",
                priority="critical",
                description="""
**Critical mathematical algorithm failures in sliding mode control core:**

## Failed Mathematical Properties

### Boundary Layer Computation Failures
- `test_boundary_layer.py` - Multiple boundary layer computation failures
- Smooth control inside boundary layer not working
- Boundary layer thickness effects not computed correctly
- Control continuity across boundary failing

### Control Computation Shape Consistency Errors
- Control output shapes inconsistent with expected dimensions
- Vector/matrix dimension mismatches in control calculations

### Sliding Surface Property Failures
- Mathematical properties of sliding surfaces not satisfied
- Critical for stability guarantees and convergence

## Lyapunov Analysis Issues
- `test_lyapunov.py` - Lyapunov analysis test errors
- Unable to verify stability through Lyapunov methods
- **CRITICAL**: Without Lyapunov verification, stability cannot be guaranteed

## Impact on System Stability
**STABILITY VIOLATION**: These mathematical failures compromise fundamental stability guarantees.

## Controllers Affected
- Classical SMC
- Adaptive SMC
- Hybrid Adaptive STA-SMC
- Super-Twisting SMC

## Source Documentation
Based on controller test failures in `prompt/pytest_controllers_detailed.txt`
""",
                reproduction_steps="""
1. Run controller tests: `pytest tests/test_controllers/smc/ -v`
2. Focus on boundary layer tests: `pytest tests/test_controllers/smc/algorithms/classical/test_boundary_layer.py -v`
3. Check Lyapunov analysis: `pytest tests/test_analysis/performance/test_lyapunov.py -v`
4. Verify sliding surface properties in mathematical tests
""",
                test_file="tests/test_controllers/smc/",
                labels=["critical", "mathematical", "stability", "lyapunov", "sliding-mode"],
                source_file="prompt/pytest_controllers_detailed.txt"
            ),

            IssueSpec(
                title="[CRITICAL] Configuration Validation System Failures",
                issue_type="stability",
                priority="critical",
                description="""
**Critical configuration validation failures compromising system safety:**

## Configuration Validation Failures

### Classical SMC Config Issues
- `test_config_validation.py` - All classical SMC config validation tests failing
- Valid configurations being rejected
- Invalid configurations being accepted
- Gain validation not working properly

### Parameter Boundary Violations
- Negative max_force values not being rejected
- Zero boundary layer values not being caught
- Invalid gains length not detected

### Safety Parameter Validation
- Critical safety parameters not being validated
- Risk of unsafe parameter combinations being used

## Impact on System Safety
**SAFETY CRITICAL**: Invalid configurations could lead to:
- System instability
- Actuator damage from excessive forces
- Unpredictable control behavior

## Affected Components
- All SMC controllers
- PSO optimization (depends on valid bounds)
- System initialization
- Real-time operation

## Source Documentation
Found in `prompt/pytest_controllers_detailed.txt` - config validation test failures
""",
                reproduction_steps="""
1. Run config validation tests: `pytest tests/test_controllers/smc/algorithms/classical/test_config_validation.py -v`
2. Test with invalid parameters to verify rejection
3. Test with valid parameters to verify acceptance
4. Check boundary condition handling
""",
                test_file="tests/test_controllers/smc/algorithms/classical/test_config_validation.py",
                labels=["critical", "configuration", "validation", "safety"],
                source_file="prompt/pytest_controllers_detailed.txt"
            )
        ])

        # 2. HIGH PRIORITY PSO/OPTIMIZATION ISSUES
        issues.extend([
            IssueSpec(
                title="[HIGH] PSO Integration System Failures",
                issue_type="convergence",
                priority="high",
                description="""
**Critical PSO optimization integration failures affecting controller tuning:**

## PSO Integration Test Failures

### Factory Integration Issues
- `TestPSOIntegration::test_create_smc_for_pso` - Cannot create SMC controllers for PSO
- `TestPSOIntegration::test_get_gain_bounds_for_pso` - Gain bounds retrieval failing
- `TestPSOIntegration::test_validate_smc_gains` - Gain validation not working

### Parameter Bounds Problems
- PSO cannot retrieve valid parameter bounds
- Optimization running with incorrect constraints
- Risk of convergence to infeasible solutions

### Controller Creation for Optimization
- Factory unable to create controllers with PSO-generated gains
- Integration between optimization and control layers broken

## Impact on System Performance
**OPTIMIZATION FAILURE**:
- Cannot automatically tune controller gains
- Manual tuning required (time-intensive, suboptimal)
- Performance degradation from poor gains

## Affected Workflows
- Automated gain tuning via PSO
- Performance optimization cycles
- Adaptive controller parameter updates

## Source Documentation
PSO integration failures documented in `prompt/pytest_controllers_detailed.txt`
""",
                reproduction_steps="""
1. Run PSO integration tests: `pytest tests/test_controllers/factory/test_controller_factory.py::TestPSOIntegration -v`
2. Test controller creation with PSO: `python simulate.py --ctrl classical_smc --run-pso`
3. Verify gain bounds retrieval for different controller types
4. Test gain validation with PSO-generated parameters
""",
                controller="all",
                test_file="tests/test_controllers/factory/test_controller_factory.py",
                labels=["high", "pso", "optimization", "convergence", "integration"],
                source_file="prompt/pytest_controllers_detailed.txt"
            ),

            IssueSpec(
                title="[HIGH] Controller Factory Integration Failures",
                issue_type="implementation",
                priority="high",
                description="""
**Controller factory pattern integration failures affecting system architecture:**

## Factory Pattern Issues

### Advanced Integration Failures
- `TestAdvancedFactoryIntegration` - Multiple advanced integration tests failing
- Closed-loop stability analysis through factory failing
- Controller performance comparison not working
- Gain sensitivity analysis broken

### Memory and Resource Management
- `test_memory_efficiency` - Memory efficiency problems in factory
- Resource leaks during controller creation
- Performance degradation with multiple controller instances

### Controller-Plant Integration
- `test_controller_plant_integration` - Controllers not integrating properly with plant models
- Communication failures between control and dynamics layers
- State/control vector dimension mismatches

### Multi-Controller Support
- `test_multiple_controller_types` - Cannot handle multiple controller types simultaneously
- Factory pattern not supporting parallel controller operations

## Architectural Impact
**ARCHITECTURE FAILURE**:
- Breaks separation of concerns between components
- Prevents modular controller development
- Compromises system scalability

## Production Readiness Impact
- Cannot deploy multiple controller variants
- Memory leaks in production environment
- Performance degradation over time

## Source Documentation
Factory integration failures in `prompt/pytest_controllers_detailed.txt`
""",
                reproduction_steps="""
1. Run factory integration tests: `pytest tests/test_controllers/factory/test_controller_factory.py::TestAdvancedFactoryIntegration -v`
2. Test memory usage: `pytest tests/test_controllers/factory/test_controller_factory.py::TestFactoryRobustness::test_memory_efficiency -v`
3. Test controller-plant integration scenarios
4. Monitor memory usage during multiple controller creation
""",
                test_file="tests/test_controllers/factory/test_controller_factory.py",
                labels=["high", "factory", "integration", "memory", "architecture"],
                source_file="prompt/pytest_controllers_detailed.txt"
            )
        ])

        # 3. MEDIUM PRIORITY IMPLEMENTATION ISSUES
        issues.extend([
            IssueSpec(
                title="[MEDIUM] Test Infrastructure Configuration Problems",
                issue_type="implementation",
                priority="medium",
                description="""
**Test infrastructure configuration issues affecting development workflow:**

## Pytest Configuration Issues

### Unknown Test Marks
The following pytest marks are not configured but used throughout the codebase:
- `@pytest.mark.slow`
- `@pytest.mark.concurrent`
- `@pytest.mark.integration`
- `@pytest.mark.error_recovery`
- `@pytest.mark.end_to_end`
- `@pytest.mark.memory`
- `@pytest.mark.numerical_stability`
- `@pytest.mark.convergence`
- `@pytest.mark.numerical_robustness`
- `@pytest.mark.property_based`
- `@pytest.mark.statistical`

### Test Collection Warnings
- `TestType` enum classes incorrectly detected as test classes
- `TestSystemState` dataclass incorrectly collected as test class
- Duplicate test file names causing import conflicts

### Collection Errors
- Import file mismatch with `test_regression_detection.py`
- Duplicate file names in different directories
- Python import conflicts preventing test execution

## Impact on Development
**TESTING WORKFLOW**:
- Cannot run specific test categories (e.g., only slow tests)
- Cluttered test output with warnings
- Unreliable test collection

## Development Process Impact
- Developers cannot efficiently run subset of tests
- CI/CD pipeline noise from warnings
- Difficulty identifying actual test failures vs. configuration issues

## Source Documentation
Warnings and errors documented in `prompt/pytest_log_detailed.txt`
""",
                reproduction_steps="""
1. Run any test suite to see warnings: `pytest tests/ -v`
2. Try to run specific mark: `pytest -m slow` (will show warning)
3. Check test collection: `pytest --collect-only`
4. Verify import conflicts with regression detection tests
""",
                test_file="pytest.ini",
                labels=["medium", "testing", "configuration", "development"],
                source_file="prompt/pytest_log_detailed.txt"
            ),

            IssueSpec(
                title="[MEDIUM] Performance Benchmark Test Failures",
                issue_type="performance",
                priority="medium",
                description="""
**Performance benchmark and regression detection failures:**

## Benchmark Test Failures

### Core Performance Tests
- `test_performance.py` - Multiple performance benchmark failures
- Performance regression detection not working
- Benchmark comparison baselines missing or incorrect

### Memory Usage Tests
- `test_memory_usage.py` - Memory usage benchmark failures
- Memory leak detection not working properly
- Resource cleanup verification failing

### Integration Accuracy Tests
- `test_integration_accuracy.py` - Numerical integration accuracy tests failing
- Simulation accuracy benchmarks not meeting thresholds
- Error accumulation in long-running simulations

### Simulation Throughput
- `test_simulation_throughput.py` - Throughput benchmarks failing
- Real-time performance requirements not being met
- Scalability issues with large-scale simulations

## Impact on Performance Monitoring
**PERFORMANCE TRACKING**:
- Cannot detect performance regressions
- No baseline for optimization efforts
- Unknown performance characteristics in production

## Quality Assurance Impact
- Cannot validate performance improvements
- Risk of deploying slower code
- No early warning for performance degradation

## Source Documentation
Performance test failures in `prompt/pytest_full_run.txt`
""",
                reproduction_steps="""
1. Run performance benchmarks: `pytest tests/test_benchmarks/core/test_performance.py -v`
2. Run memory tests: `pytest tests/test_benchmarks/core/test_memory_usage.py -v`
3. Test simulation throughput: `pytest tests/test_benchmarks/core/test_simulation_throughput.py -v`
4. Check benchmark baseline files exist and are valid
""",
                test_file="tests/test_benchmarks/",
                labels=["medium", "performance", "benchmarks", "regression"],
                source_file="prompt/pytest_full_run.txt"
            ),

            IssueSpec(
                title="[HIGH] Adaptive SMC Algorithm Core Failures",
                issue_type="stability",
                priority="high",
                description="""
**Adaptive sliding mode control algorithm core failures affecting stability:**

## Adaptive SMC Core Issues

### Controller Initialization Errors
- `TestModularAdaptiveSMC::test_controller_initialization` - ERROR during initialization
- Adaptive controller cannot be instantiated properly
- Parameter initialization failing

### Adaptation Law Failures
- `test_adaptation_law_initialization` - FAILED adaptation law setup
- `test_modified_adaptation_law` - FAILED adaptation mechanism
- Core adaptation algorithms not working

### Uncertainty Estimation Problems
- `test_uncertainty_estimator` - FAILED uncertainty estimation
- Cannot estimate system uncertainties and disturbances
- Critical for adaptive control performance

### Parameter Adaptation Errors
- `test_parameter_adaptation` - ERROR in parameter adaptation mechanism
- `test_adaptation_stability` - ERROR in adaptation stability verification
- `test_convergence_properties` - ERROR in convergence analysis

### Disturbance Adaptation Failures
- `test_constant_disturbance_adaptation` - ERROR handling constant disturbances
- `test_time_varying_disturbance_adaptation` - ERROR with time-varying disturbances

## Impact on Adaptive Control
**ADAPTIVE CONTROL FAILURE**:
- Cannot handle system uncertainties
- No adaptation to changing conditions
- Performance degradation in uncertain environments

## Safety and Stability Concerns
**STABILITY RISK**:
- Adaptive mechanisms not providing stability guarantees
- System may become unstable with uncertainties
- No convergence guarantees for adaptation

## Source Documentation
Adaptive SMC failures in `prompt/pytest_controllers_detailed.txt`
""",
                reproduction_steps="""
1. Run adaptive SMC tests: `pytest tests/test_controllers/smc/algorithms/adaptive/test_modular_adaptive_smc.py -v`
2. Test controller initialization with default parameters
3. Verify adaptation law computation with sample uncertainties
4. Test parameter adaptation under known disturbances
""",
                controller="adaptive_smc",
                test_file="tests/test_controllers/smc/algorithms/adaptive/test_modular_adaptive_smc.py",
                labels=["high", "adaptive", "stability", "uncertainty", "adaptation"],
                source_file="prompt/pytest_controllers_detailed.txt"
            )
        ])

        # 4. LOW PRIORITY ISSUES
        issues.extend([
            IssueSpec(
                title="[MEDIUM] Application Layer Integration Failures",
                issue_type="implementation",
                priority="medium",
                description="""
**Application layer (CLI/UI) integration issues affecting user workflows:**

## CLI Integration Issues
- `test_cli.py` - Multiple CLI functionality failures
- `test_cli_save_gains.py` - Cannot save optimized gains through CLI
- Command-line interface not working with controller factory

## Streamlit UI Problems
- `test_streamlit_app.py` - Streamlit application integration failing
- Web UI cannot interface with simulation backend
- Data export functionality broken

## Data Export Issues
- `test_data_export.py` - Data export functionality failing
- Cannot export simulation results or optimized parameters
- Integration between simulation and data persistence broken

## User Workflow Impact
**USER EXPERIENCE**:
- Users cannot interact with system through web interface
- CLI workflows for development broken
- Cannot save/load optimized controller parameters

## Development Productivity
- Debugging more difficult without working UI
- Cannot easily visualize results
- Manual parameter management required

## Source Documentation
Application test failures in `prompt/pytest_full_run.txt`
""",
                reproduction_steps="""
1. Test CLI functionality: `pytest tests/test_app/test_cli.py -v`
2. Test Streamlit app: `pytest tests/test_app/test_streamlit_app.py -v`
3. Try manual CLI commands: `python simulate.py --help`
4. Launch Streamlit app: `streamlit run streamlit_app.py`
""",
                test_file="tests/test_app/",
                labels=["medium", "application", "cli", "ui", "integration"],
                source_file="prompt/pytest_full_run.txt"
            )
        ])

        return issues

    def _create_github_issue(self, issue: IssueSpec) -> bool:
        """Create a GitHub issue using the create_issue script."""
        try:
            # Prepare command
            cmd = [str(self.create_issue_script)]
            cmd.extend(["-t", issue.issue_type])
            cmd.extend(["-p", issue.priority])
            cmd.extend(["-T", issue.title])
            cmd.extend(["-d", issue.description.strip()])
            cmd.extend(["-r", issue.reproduction_steps])

            if issue.controller:
                cmd.extend(["-c", issue.controller])

            if issue.test_file:
                cmd.extend(["-f", issue.test_file])

            if self.dry_run:
                print(f"[DRY RUN] Would create: {issue.title}")
                print(f"   Type: {issue.issue_type}, Priority: {issue.priority}")
                if issue.labels:
                    print(f"   Labels: {', '.join(issue.labels)}")
                self.issues_created.append(issue.title)
                return True
            else:
                # Execute the issue creation
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    print(f"Created: {issue.title}")
                    self.issues_created.append(issue.title)
                    return True
                else:
                    print(f"Failed to create: {issue.title}")
                    print(f"   Error: {result.stderr}")
                    return False

        except Exception as e:
            print(f"Error creating issue '{issue.title}': {e}")
            return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Create GitHub issues from prompt folder documentation")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without creating issues")
    parser.add_argument("--category", help="Only create issues of specific type (stability, performance, convergence, implementation)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    print("Creating GitHub issues from prompt folder documentation...")

    if args.dry_run:
        print("DRY RUN MODE - No issues will be created")

    creator = PromptIssueCreator(dry_run=args.dry_run)
    return creator.create_all_documented_issues(category_filter=args.category)

if __name__ == "__main__":
    sys.exit(main())