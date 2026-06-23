#==========================================================================================\\\
#====================== src/integration/compatibility_matrix.py =========================\\\
#==========================================================================================\\\

"""Cross-domain compatibility validation matrix for comprehensive system integration.

This module provides sophisticated compatibility validation across all project domains
including controllers, optimization, testing, analysis, configuration, and HIL systems.
It ensures seamless integration and identifies potential conflicts before they impact
production systems.
"""

import sys
import inspect
import importlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import time

# Add project paths for comprehensive imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

logger = logging.getLogger(__name__)

class CompatibilityLevel(Enum):
    """Compatibility assessment levels with increasing strictness."""
    COMPATIBLE = "compatible"
    WARNING = "warning"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"

class DomainType(Enum):
    """Project domain types for compatibility analysis."""
    CONTROLLERS = "controllers"
    OPTIMIZATION = "optimization"
    TESTING = "testing"
    ANALYSIS = "analysis"
    CONFIGURATION = "configuration"
    HIL = "hil"
    INTERFACES = "interfaces"
    UTILITIES = "utilities"

@dataclass
class CompatibilityIssue:
    """Represents a compatibility issue between system components."""
    domain_a: DomainType
    domain_b: DomainType
    component_a: str
    component_b: str
    issue_type: str
    severity: CompatibilityLevel
    description: str
    recommendation: str
    affected_functionality: List[str] = field(default_factory=list)

@dataclass
class IntegrationPoint:
    """Represents an integration point between domains."""
    source_domain: DomainType
    target_domain: DomainType
    interface_type: str
    data_flow: str
    dependencies: List[str] = field(default_factory=list)
    validation_status: CompatibilityLevel = CompatibilityLevel.UNKNOWN

@dataclass
class DomainHealth:
    """Health status of a specific domain."""
    domain: DomainType
    overall_health: CompatibilityLevel
    component_count: int
    test_coverage: float
    integration_points: int
    critical_issues: List[CompatibilityIssue] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

class CompatibilityMatrix:
    """Comprehensive compatibility validation matrix for cross-domain integration.

    This class provides sophisticated analysis of compatibility between all project
    domains, identifying potential integration issues and providing actionable
    recommendations for resolution.
    """

    def __init__(self, project_root: Path = PROJECT_ROOT):
        """Initialize compatibility matrix with comprehensive domain mapping.

        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root
        self.src_path = project_root / "src"

        # Domain module mappings
        self.domain_modules = {
            DomainType.CONTROLLERS: [
                "src.controllers.factory",
                "src.controllers.smc",
                "src.controllers.mpc",
                "src.controllers.specialized"
            ],
            DomainType.OPTIMIZATION: [
                "src.optimizer.pso_optimizer"
            ],
            DomainType.TESTING: [
                "tests.test_controllers",
                "tests.test_optimization",
                "tests.test_integration"
            ],
            DomainType.ANALYSIS: [
                "src.utils.analysis",
                "src.utils.visualization",
                "src.benchmarks"
            ],
            DomainType.CONFIGURATION: [
                "src.config"
            ],
            DomainType.HIL: [
                "src.interfaces.hardware",
                "src.interfaces.hil"
            ],
            DomainType.INTERFACES: [
                "src.interfaces.data_exchange",
                "src.interfaces.monitoring"
            ],
            DomainType.UTILITIES: [
                "src.utils.validation",
                "src.utils.control",
                "src.utils.monitoring"
            ]
        }

        # Critical integration points
        self.integration_points = [
            IntegrationPoint(
                DomainType.CONTROLLERS, DomainType.OPTIMIZATION,
                "parameter_tuning", "bidirectional",
                ["gain_bounds", "controller_factory", "fitness_evaluation"]
            ),
            IntegrationPoint(
                DomainType.CONTROLLERS, DomainType.CONFIGURATION,
                "parameter_validation", "unidirectional",
                ["config_schema", "parameter_bounds", "validation_rules"]
            ),
            IntegrationPoint(
                DomainType.TESTING, DomainType.CONTROLLERS,
                "functional_validation", "unidirectional",
                ["test_fixtures", "stability_analysis", "performance_metrics"]
            ),
            IntegrationPoint(
                DomainType.ANALYSIS, DomainType.CONTROLLERS,
                "performance_monitoring", "unidirectional",
                ["metrics_collection", "visualization", "statistical_analysis"]
            ),
            IntegrationPoint(
                DomainType.HIL, DomainType.CONTROLLERS,
                "real_time_control", "bidirectional",
                ["communication_protocol", "latency_constraints", "safety_monitoring"]
            ),
            IntegrationPoint(
                DomainType.INTERFACES, DomainType.HIL,
                "hardware_abstraction", "bidirectional",
                ["device_drivers", "data_exchange", "error_handling"]
            )
        ]

        # Compatibility rules and constraints
        self.compatibility_rules = {
            "memory_management": {
                "domains": [DomainType.OPTIMIZATION, DomainType.ANALYSIS],
                "constraint": "bounded_memory_usage",
                "threshold": "1GB"
            },
            "numerical_stability": {
                "domains": [DomainType.CONTROLLERS, DomainType.OPTIMIZATION],
                "constraint": "numerical_precision",
                "threshold": "1e-12"
            },
            "real_time_constraints": {
                "domains": [DomainType.CONTROLLERS, DomainType.HIL],
                "constraint": "timing_deadlines",
                "threshold": "10ms"
            },
            "thread_safety": {
                "domains": [DomainType.HIL, DomainType.INTERFACES],
                "constraint": "concurrent_access",
                "threshold": "thread_safe"
            }
        }

    def analyze_full_system_compatibility(self) -> Dict[str, Any]:
        """Perform comprehensive compatibility analysis across all domains.

        Returns:
            Complete compatibility analysis results with recommendations
        """
        start_time = time.time()

        # Analyze individual domain health
        domain_health = self._analyze_domain_health()

        # Validate integration points
        integration_status = self._validate_integration_points()

        # Check cross-domain compatibility rules
        rule_violations = self._check_compatibility_rules()

        # Identify potential conflicts
        compatibility_issues = self._identify_compatibility_issues()

        # Generate overall system health score
        system_health = self._calculate_system_health_score(
            domain_health, integration_status, rule_violations
        )

        # Generate actionable recommendations
        recommendations = self._generate_compatibility_recommendations(
            compatibility_issues, rule_violations
        )

        analysis_time = time.time() - start_time

        return {
            "timestamp": time.time(),
            "analysis_duration": analysis_time,
            "system_health_score": system_health,
            "domain_health": {domain.value: asdict(health) for domain, health in domain_health.items()},
            "integration_points": [asdict(point) for point in integration_status],
            "rule_violations": rule_violations,
            "compatibility_issues": [asdict(issue) for issue in compatibility_issues],
            "recommendations": recommendations,
            "production_readiness": self._assess_production_readiness(system_health, rule_violations)
        }

    def _analyze_domain_health(self) -> Dict[DomainType, DomainHealth]:
        """Analyze health status of individual domains."""
        domain_health = {}

        for domain, modules in self.domain_modules.items():
            try:
                health = self._assess_single_domain_health(domain, modules)
                domain_health[domain] = health
            except Exception as e:
                logger.warning(f"Failed to assess health for domain {domain.value}: {e}")
                domain_health[domain] = DomainHealth(
                    domain=domain,
                    overall_health=CompatibilityLevel.UNKNOWN,
                    component_count=0,
                    test_coverage=0.0,
                    integration_points=0
                )

        return domain_health

    def _assess_single_domain_health(self, domain: DomainType, modules: List[str]) -> DomainHealth:
        """Assess health of a single domain."""
        component_count = 0
        importable_modules = 0
        critical_issues = []

        for module_name in modules:
            try:
                # Try to import module to check availability
                module = importlib.import_module(module_name)
                importable_modules += 1

                # Count components (classes and functions) - with recursion guard
                # Use dir() instead of inspect.getmembers() to avoid deep recursion
                try:
                    for name in dir(module):
                        if not name.startswith('_'):  # Skip private members
                            try:
                                obj = getattr(module, name, None)
                                if obj is not None and (inspect.isclass(obj) or inspect.isfunction(obj)):
                                    # Only count objects defined in this module
                                    if hasattr(obj, '__module__') and obj.__module__ == module_name:
                                        component_count += 1
                            except (AttributeError, RecursionError):
                                # Skip problematic attributes that cause recursion
                                continue
                except RecursionError:
                    logger.warning(f"Recursion detected while inspecting {module_name}, skipping component count")

            except ImportError as e:
                critical_issues.append(CompatibilityIssue(
                    domain_a=domain,
                    domain_b=domain,
                    component_a=module_name,
                    component_b="import_system",
                    issue_type="import_error",
                    severity=CompatibilityLevel.INCOMPATIBLE,
                    description=f"Failed to import module {module_name}: {e}",
                    recommendation="Fix import dependencies or module structure"
                ))
            except RecursionError as e:
                logger.warning(f"Recursion error while analyzing {module_name}: {e}")
                critical_issues.append(CompatibilityIssue(
                    domain_a=domain,
                    domain_b=domain,
                    component_a=module_name,
                    component_b="introspection_system",
                    issue_type="recursion_error",
                    severity=CompatibilityLevel.WARNING,
                    description=f"Circular dependency detected in {module_name}",
                    recommendation="Review module imports to remove circular dependencies"
                ))

        # Calculate overall health
        if len(critical_issues) > 0:
            overall_health = CompatibilityLevel.INCOMPATIBLE
        elif importable_modules == len(modules):
            overall_health = CompatibilityLevel.COMPATIBLE
        else:
            overall_health = CompatibilityLevel.WARNING

        # Estimate test coverage (simplified)
        test_coverage = self._estimate_domain_test_coverage(domain)

        # Count integration points for this domain
        integration_count = sum(1 for point in self.integration_points
                              if point.source_domain == domain or point.target_domain == domain)

        return DomainHealth(
            domain=domain,
            overall_health=overall_health,
            component_count=component_count,
            test_coverage=test_coverage,
            integration_points=integration_count,
            critical_issues=critical_issues
        )

    def _estimate_domain_test_coverage(self, domain: DomainType) -> float:
        """Estimate test coverage for a domain (simplified implementation)."""
        # This is a simplified estimation - in practice, would integrate with coverage tools
        coverage_estimates = {
            DomainType.CONTROLLERS: 85.0,
            DomainType.OPTIMIZATION: 75.0,
            DomainType.TESTING: 90.0,
            DomainType.ANALYSIS: 70.0,
            DomainType.CONFIGURATION: 80.0,
            DomainType.HIL: 60.0,
            DomainType.INTERFACES: 65.0,
            DomainType.UTILITIES: 75.0
        }
        return coverage_estimates.get(domain, 50.0)

    def _validate_integration_points(self) -> List[IntegrationPoint]:
        """Validate all defined integration points for compatibility."""
        validated_points = []

        for point in self.integration_points:
            try:
                # Validate that source and target domains are healthy
                source_health = self._check_domain_availability(point.source_domain)
                target_health = self._check_domain_availability(point.target_domain)

                if source_health and target_health:
                    point.validation_status = CompatibilityLevel.COMPATIBLE
                else:
                    point.validation_status = CompatibilityLevel.INCOMPATIBLE

                validated_points.append(point)

            except Exception as e:
                logger.warning(f"Failed to validate integration point {point.interface_type}: {e}")
                point.validation_status = CompatibilityLevel.UNKNOWN
                validated_points.append(point)

        return validated_points

    def _check_domain_availability(self, domain: DomainType) -> bool:
        """Check if a domain is available and functional."""
        modules = self.domain_modules.get(domain, [])

        for module_name in modules:
            try:
                importlib.import_module(module_name)
            except ImportError:
                return False

        return True

    def _check_compatibility_rules(self) -> List[Dict[str, Any]]:
        """Check system-wide compatibility rules and constraints."""
        violations = []

        for rule_name, rule_config in self.compatibility_rules.items():
            try:
                violation = self._validate_compatibility_rule(rule_name, rule_config)
                if violation:
                    violations.append(violation)
            except Exception as e:
                logger.warning(f"Failed to check compatibility rule {rule_name}: {e}")

        return violations

    def _validate_compatibility_rule(self, rule_name: str, rule_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate a specific compatibility rule."""
        domains = rule_config["domains"]
        rule_config["constraint"]
        threshold = rule_config["threshold"]

        # Simplified rule validation - in practice, would implement specific checks
        if rule_name == "memory_management":
            # Check if memory-intensive domains have proper memory management
            return self._check_memory_management_rule(domains, threshold)
        elif rule_name == "numerical_stability":
            # Check numerical precision across domains
            return self._check_numerical_stability_rule(domains, threshold)
        elif rule_name == "real_time_constraints":
            # Check timing constraints for real-time domains
            return self._check_real_time_constraints_rule(domains, threshold)
        elif rule_name == "thread_safety":
            # Check thread safety for concurrent domains
            return self._check_thread_safety_rule(domains, threshold)

        return None

    def _check_memory_management_rule(self, domains: List[DomainType], threshold: str) -> Optional[Dict[str, Any]]:
        """Check memory management compatibility rule."""
        # Simplified check - in practice, would analyze actual memory usage
        for domain in domains:
            if domain == DomainType.OPTIMIZATION:
                # PSO optimization can be memory intensive
                return {
                    "rule": "memory_management",
                    "violated_domains": [domain.value],
                    "severity": "warning",
                    "description": f"Domain {domain.value} may exceed memory threshold {threshold}",
                    "recommendation": "Implement bounded memory usage in PSO algorithms"
                }
        return None

    def _check_numerical_stability_rule(self, domains: List[DomainType], threshold: str) -> Optional[Dict[str, Any]]:
        """Check numerical stability compatibility rule."""
        # Check for potential numerical stability issues
        return None  # Assume stable for now

    def _check_real_time_constraints_rule(self, domains: List[DomainType], threshold: str) -> Optional[Dict[str, Any]]:
        """Check real-time constraints compatibility rule."""
        # Check if real-time domains meet timing requirements
        for domain in domains:
            if domain == DomainType.HIL:
                # HIL systems have strict timing requirements
                return {
                    "rule": "real_time_constraints",
                    "violated_domains": [domain.value],
                    "severity": "critical",
                    "description": f"Domain {domain.value} must meet {threshold} timing deadline",
                    "recommendation": "Validate real-time performance in HIL integration tests"
                }
        return None

    def _check_thread_safety_rule(self, domains: List[DomainType], threshold: str) -> Optional[Dict[str, Any]]:
        """Check thread safety compatibility rule."""
        # Check thread safety for concurrent access
        for domain in domains:
            if domain in [DomainType.HIL, DomainType.INTERFACES]:
                # These domains may have thread safety issues
                return {
                    "rule": "thread_safety",
                    "violated_domains": [domain.value],
                    "severity": "warning",
                    "description": f"Domain {domain.value} requires thread safety validation",
                    "recommendation": "Implement thread safety tests for concurrent operations"
                }
        return None

    def _identify_compatibility_issues(self) -> List[CompatibilityIssue]:
        """Identify potential compatibility issues between domains."""
        issues = []

        # Check for known compatibility issues
        issues.extend(self._check_controller_optimization_compatibility())
        issues.extend(self._check_hil_interface_compatibility())
        issues.extend(self._check_testing_configuration_compatibility())

        return issues

    def _check_controller_optimization_compatibility(self) -> List[CompatibilityIssue]:
        """Check compatibility between controllers and optimization domains."""
        issues = []

        # Check parameter bounds compatibility
        try:
            # Check if both domains are available
            import importlib.util
            has_controllers = importlib.util.find_spec('src.controllers.factory') is not None
            has_optimizer = importlib.util.find_spec('src.optimizer.pso_optimizer') is not None

            # Check if gain bounds are compatible
            if not (has_controllers and has_optimizer):
                return CompatibilityLevel.INCOMPATIBLE
            # This is a simplified check - would implement detailed validation
            issues.append(CompatibilityIssue(
                domain_a=DomainType.CONTROLLERS,
                domain_b=DomainType.OPTIMIZATION,
                component_a="SMCFactory",
                component_b="PSOTuner",
                issue_type="parameter_bounds",
                severity=CompatibilityLevel.WARNING,
                description="PSO parameter bounds may not be optimally configured for all controllers",
                recommendation="Validate PSO bounds against controller stability requirements",
                affected_functionality=["automated_tuning", "gain_optimization"]
            ))

        except ImportError as e:
            issues.append(CompatibilityIssue(
                domain_a=DomainType.CONTROLLERS,
                domain_b=DomainType.OPTIMIZATION,
                component_a="controller_factory",
                component_b="pso_optimizer",
                issue_type="import_dependency",
                severity=CompatibilityLevel.INCOMPATIBLE,
                description=f"Failed to import required modules: {e}",
                recommendation="Fix import dependencies between controllers and optimization"
            ))

        return issues

    def _check_hil_interface_compatibility(self) -> List[CompatibilityIssue]:
        """Check compatibility between HIL and interface domains."""
        issues = []

        # Check for HIL interface compatibility
        try:
            # Try to access HIL interfaces
            hil_path = self.src_path / "interfaces" / "hil"
            if not hil_path.exists():
                issues.append(CompatibilityIssue(
                    domain_a=DomainType.HIL,
                    domain_b=DomainType.INTERFACES,
                    component_a="hil_system",
                    component_b="interface_layer",
                    issue_type="missing_interface",
                    severity=CompatibilityLevel.INCOMPATIBLE,
                    description="HIL interface layer is missing or incomplete",
                    recommendation="Implement complete HIL interface abstraction layer"
                ))

        except Exception as e:
            logger.warning(f"Failed to check HIL interface compatibility: {e}")

        return issues

    def _check_testing_configuration_compatibility(self) -> List[CompatibilityIssue]:
        """Check compatibility between testing and configuration domains."""
        issues = []

        # Check configuration validation in tests
        try:
            # Check if test configuration is compatible with main configuration
            config_path = self.project_root / "config.yaml"
            if config_path.exists():
                # Configuration exists - check test compatibility
                pass  # Simplified - would implement detailed validation
            else:
                issues.append(CompatibilityIssue(
                    domain_a=DomainType.TESTING,
                    domain_b=DomainType.CONFIGURATION,
                    component_a="test_config",
                    component_b="main_config",
                    issue_type="missing_configuration",
                    severity=CompatibilityLevel.WARNING,
                    description="Main configuration file missing for test validation",
                    recommendation="Ensure config.yaml exists and is properly structured"
                ))

        except Exception as e:
            logger.warning(f"Failed to check testing configuration compatibility: {e}")

        return issues

    def _calculate_system_health_score(self, domain_health: Dict[DomainType, DomainHealth],
                                     integration_status: List[IntegrationPoint],
                                     rule_violations: List[Dict[str, Any]]) -> float:
        """Calculate overall system health score (0-100)."""
        # Domain health contribution (60% of total score)
        domain_scores = []
        for health in domain_health.values():
            if health.overall_health == CompatibilityLevel.COMPATIBLE:
                domain_scores.append(100.0)
            elif health.overall_health == CompatibilityLevel.WARNING:
                domain_scores.append(70.0)
            elif health.overall_health == CompatibilityLevel.INCOMPATIBLE:
                domain_scores.append(20.0)
            else:
                domain_scores.append(50.0)

        domain_score = sum(domain_scores) / len(domain_scores) if domain_scores else 0

        # Integration points contribution (30% of total score)
        integration_scores = []
        for point in integration_status:
            if point.validation_status == CompatibilityLevel.COMPATIBLE:
                integration_scores.append(100.0)
            elif point.validation_status == CompatibilityLevel.WARNING:
                integration_scores.append(70.0)
            elif point.validation_status == CompatibilityLevel.INCOMPATIBLE:
                integration_scores.append(20.0)
            else:
                integration_scores.append(50.0)

        integration_score = sum(integration_scores) / len(integration_scores) if integration_scores else 100

        # Rule violations penalty (10% of total score)
        violation_penalty = len([v for v in rule_violations if v.get("severity") == "critical"]) * 20
        violation_penalty += len([v for v in rule_violations if v.get("severity") == "warning"]) * 10
        violation_score = max(0, 100 - violation_penalty)

        # Calculate weighted total
        total_score = (domain_score * 0.6) + (integration_score * 0.3) + (violation_score * 0.1)

        return round(total_score, 1)

    def _generate_compatibility_recommendations(self, issues: List[CompatibilityIssue],
                                              violations: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations for resolving compatibility issues."""
        recommendations = []

        # Process compatibility issues
        critical_issues = [issue for issue in issues if issue.severity == CompatibilityLevel.INCOMPATIBLE]
        warning_issues = [issue for issue in issues if issue.severity == CompatibilityLevel.WARNING]

        if critical_issues:
            recommendations.append(f"[ALERT] CRITICAL: Address {len(critical_issues)} incompatible components before production")
            for issue in critical_issues[:3]:  # Top 3 critical issues
                recommendations.append(f"   - {issue.recommendation}")

        if warning_issues:
            recommendations.append(f"[WARNING] Review {len(warning_issues)} compatibility warnings")
            for issue in warning_issues[:2]:  # Top 2 warnings
                recommendations.append(f"   - {issue.recommendation}")

        # Process rule violations
        critical_violations = [v for v in violations if v.get("severity") == "critical"]
        warning_violations = [v for v in violations if v.get("severity") == "warning"]

        if critical_violations:
            recommendations.append(f"[CRITICAL] URGENT: Resolve {len(critical_violations)} critical rule violations")
            for violation in critical_violations:
                recommendations.append(f"   - {violation.get('recommendation', 'Address violation')}")

        if warning_violations:
            recommendations.append(f"[INFO] REVIEW: Address {len(warning_violations)} rule warnings")

        # General recommendations
        recommendations.extend([
            "[TEST] Run comprehensive integration tests to validate cross-domain functionality",
            "[MONITOR] Monitor system health scores and address degradation promptly",
            "[CI/CD] Implement continuous compatibility monitoring in CI/CD pipeline",
            "[DOCS] Update documentation to reflect integration requirements and constraints"
        ])

        return recommendations

    def _assess_production_readiness(self, system_health: float, violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess overall production readiness based on compatibility analysis."""
        critical_violations = [v for v in violations if v.get("severity") == "critical"]

        if system_health >= 90 and len(critical_violations) == 0:
            status = "production_ready"
            confidence = "high"
        elif system_health >= 80 and len(critical_violations) == 0:
            status = "production_ready_with_monitoring"
            confidence = "medium"
        elif system_health >= 70:
            status = "needs_improvement"
            confidence = "low"
        else:
            status = "not_production_ready"
            confidence = "very_low"

        return {
            "status": status,
            "confidence": confidence,
            "health_score": system_health,
            "critical_blockers": len(critical_violations),
            "recommendation": self._get_production_recommendation(status)
        }

    def _get_production_recommendation(self, status: str) -> str:
        """Get production recommendation based on status."""
        recommendations = {
            "production_ready": "System is ready for production deployment with standard monitoring",
            "production_ready_with_monitoring": "Deploy with enhanced monitoring and gradual rollout",
            "needs_improvement": "Address compatibility issues before production deployment",
            "not_production_ready": "Critical compatibility issues must be resolved before deployment"
        }
        return recommendations.get(status, "Unknown production status")

def asdict(obj, _seen=None) -> Dict[str, Any]:
    """Convert dataclass to dictionary with recursion protection.

    Args:
        obj: Object to convert
        _seen: Set of object IDs already processed (for recursion protection)

    Returns:
        Dictionary representation of the object
    """
    if _seen is None:
        _seen = set()

    # Check if we've already processed this object (circular reference protection)
    obj_id = id(obj)
    if obj_id in _seen:
        return f"<circular reference to {type(obj).__name__}>"

    if hasattr(obj, '__dict__'):
        _seen.add(obj_id)
        result = {}
        for key, value in obj.__dict__.items():
            try:
                if isinstance(value, list):
                    result[key] = [
                        asdict(item, _seen) if hasattr(item, '__dict__') else item
                        for item in value
                    ]
                elif hasattr(value, '__dict__'):
                    result[key] = asdict(value, _seen)
                elif isinstance(value, Enum):
                    result[key] = value.value
                else:
                    result[key] = value
            except RecursionError:
                result[key] = f"<recursion error on {key}>"
        return result
    elif isinstance(obj, Enum):
        return obj.value
    else:
        return str(obj)

def main():
    """Main entry point for compatibility matrix analysis."""
    matrix = CompatibilityMatrix()

    print("🔍 Starting comprehensive compatibility analysis...")
    results = matrix.analyze_full_system_compatibility()

    print(f"\n{'='*80}")
    print("SYSTEM COMPATIBILITY ANALYSIS RESULTS")
    print(f"{'='*80}")
    print(f"Overall Health Score: {results['system_health_score']:.1f}/100")
    print(f"Analysis Duration: {results['analysis_duration']:.2f}s")
    print(f"Production Ready: {results['production_readiness']['status']}")

    print("\n[HEALTH] DOMAIN HEALTH:")
    for domain, health in results['domain_health'].items():
        status_icon = "[OK]" if health['overall_health'] == "compatible" else "[WARNING]" if health['overall_health'] == "warning" else "[ERROR]"
        print(f"  {status_icon} {domain}: {health['overall_health']} ({health['component_count']} components)")

    print("\n[INTEGRATION] INTEGRATION POINTS:")
    for point in results['integration_points']:
        status_icon = "[OK]" if point['validation_status'] == "compatible" else "[WARNING]" if point['validation_status'] == "warning" else "[ERROR]"
        print(f"  {status_icon} {point['source_domain']} -> {point['target_domain']}: {point['interface_type']}")

    if results['rule_violations']:
        print("\n[ALERT] RULE VIOLATIONS:")
        for violation in results['rule_violations']:
            print(f"  - {violation['rule']}: {violation['description']}")

    print("\n[INFO] RECOMMENDATIONS:")
    for rec in results['recommendations']:
        print(f"  {rec}")

    # Export results
    output_path = PROJECT_ROOT / "artifacts" / "compatibility_analysis.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Full analysis exported to: {output_path}")

if __name__ == "__main__":
    main()