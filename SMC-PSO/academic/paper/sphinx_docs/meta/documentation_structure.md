# Documentation Structure & Site Map

This page provides a complete overview of the DIP_SMC_PSO documentation organization. Use this as a roadmap to navigate through technical references, user guides, tutorials, and research documentation.

## Overview

The documentation is organized into several main categories:

- **Getting Started**: Installation guides, quickstart tutorials, and basic concepts
- **User Guides & Tutorials**: Step-by-step instructions for common tasks and workflows
- **API & Technical Reference**: Detailed API documentation and module references
- **Testing & Validation**: Testing standards, benchmarking methodologies, and quality assurance
- **Production & Deployment**: Deployment guides, Docker setup, and production readiness
- **Research & Analysis**: Research workflows, data analysis, and publication preparation
- **Project Documentation**: Changelog, contributing guidelines, design patterns

---

## Getting Started

Essential documentation for new users to get up and running quickly.

- {doc}`README` - Project overview and quick start
- {doc}`theory_overview` - Control theory fundamentals
- {doc}`architecture` - System architecture overview
- {doc}`plant_model` - Double inverted pendulum dynamics
- {doc}`hil_quickstart` - Hardware-in-the-loop quickstart
- {doc}`streamlit_dashboard_guide` - Interactive dashboard guide
- {doc}`guides/getting-started` - Complete getting started guide

---

## User Guides & Tutorials

Step-by-step tutorials and how-to guides for common tasks and workflows.

- {doc}`guides/index` - User guides index
- {doc}`guides/how-to/running-simulations` - Running simulations
- {doc}`guides/how-to/optimization-workflows` - PSO optimization workflows
- {doc}`guides/how-to/testing-validation` - Testing and validation
- {doc}`guides/interactive_configuration_guide` - Interactive configuration
- {doc}`guides/interactive_visualizations` - Interactive visualizations
- {doc}`workflows/index` - Workflow documentation index

**Key Resources:**
- Interactive tutorials for first simulations
- Controller comparison guides
- PSO optimization workflows
- Custom controller development

---

## API & Technical Reference

Comprehensive technical reference for all modules, classes, and functions.

**Core API**
- {doc}`api/index` - Complete API reference index
- {doc}`CONTROLLER_FACTORY` - Controller factory system
- {doc}`controller_pso_interface_api_documentation` - PSO integration API
- {doc}`factory_integration_documentation` - Factory integration guide
- {doc}`factory_integration_troubleshooting_guide` - Troubleshooting

**Module References**
- {doc}`reference/controllers/index` - Controller implementations
- {doc}`reference/optimization/index` - PSO optimization modules
- {doc}`reference/simulation/index` - Simulation engines
- {doc}`reference/plant/index` - Dynamics models
- {doc}`reference/analysis/index` - Analysis and metrics
- {doc}`reference/utils/index` - Utility functions
- {doc}`reference/interfaces/index` - System interfaces

---

## Testing & Validation Standards

Testing methodologies, validation protocols, and quality assurance frameworks.

- {doc}`TESTING` - Testing standards and execution guide
- {doc}`testing/index` - Testing framework documentation
- {doc}`benchmarks/index` - Performance benchmarks
- {doc}`validation/index` - Validation protocols
- {doc}`test_infrastructure_validation_report` - Infrastructure validation
- {doc}`test_execution_guide` - Test execution workflows
- {doc}`QUICKSTART_VALIDATION` - Quickstart validation report
- {doc}`control_law_testing_standards` - Control law testing
- {doc}`deployment_validation_checklists` - Deployment validation
- {doc}`benchmarks_methodology` - Benchmarking methodology

**Testing Coverage:**
- Unit tests for all controllers (≥95% coverage)
- Integration tests for simulation workflows (≥85% coverage)
- Benchmark tests for performance validation
- Statistical validation protocols

---

## Production & Deployment

Guides for deploying the framework in production environments.

- {doc}`deployment/DEPLOYMENT_GUIDE` - Complete deployment guide
- {doc}`deployment/docker` - Docker containerization
- {doc}`deployment/STREAMLIT_DEPLOYMENT` - Streamlit deployment
- {doc}`production/index` - Production readiness documentation

**Deployment Options:**
- Docker containerization with GPU support
- Streamlit dashboard deployment
- Cloud deployment (AWS, GCP, Azure)
- Kubernetes orchestration patterns
- Production readiness checklists

---

## Mathematical Foundations

Theoretical foundations, mathematical derivations, and algorithm analysis.

- {doc}`mathematical_foundations/index` - Mathematical foundations index
- {doc}`theory/index` - Control theory documentation
- {doc}`theory/pso_algorithm_foundations` - PSO mathematical foundations

**Theory Coverage:**
- Sliding mode control theory with Lyapunov stability
- PSO algorithm foundations and convergence analysis
- Double inverted pendulum dynamics and linearization
- Finite-time convergence proofs
- Robust control under matched uncertainties

---

## Controller Factory & Integration

Documentation for the controller factory system and integration patterns.

- {doc}`factory/README` - Factory system overview
- {doc}`controllers/index` - Controller implementations index

**Factory System:**
- Controller registration and discovery patterns
- PSO integration with controller factory
- Parameter interface specifications
- Performance benchmarks and validation
- Migration guides for legacy controllers

---

## Analysis & Reports

Performance analysis, experimental reports, and research findings.

- {doc}`analysis/index` - Analysis tools and reports index
- {doc}`reports/index` - Experimental reports

**Analysis Tools:**
- Controller performance comparison matrices
- PSO convergence analysis and diagnostics
- Statistical benchmarking with confidence intervals
- Fault detection and isolation reports
- Memory pattern analysis and leak prevention

---

## Configuration & Integration

Configuration schemas, validation, and system integration documentation.

- {doc}`configuration_integration_documentation` - Configuration integration
- {doc}`configuration_schema_validation` - Schema validation
- {doc}`coverage_analysis_methodology` - Coverage analysis methods
- {doc}`fault_detection_guide` - Fault detection system guide

---

## Project Documentation

Project-level documentation including changelog, contributing guidelines, and design patterns.

- {doc}`CHANGELOG` - Version history and release notes
- {doc}`CONTRIBUTING` - Contributing guidelines and PR workflow
- {doc}`DEPENDENCIES` - Software dependencies and licenses
- {doc}`meta/PATTERNS` - Design patterns and architectural decisions
- {doc}`context` - Project context and background
- {doc}`ACADEMIC_INTEGRITY_STATEMENT` - Academic integrity statement

---

## References & Bibliography

Academic references, citations, and bibliographic information.

- {doc}`bibliography` - Complete BibTeX bibliography
- {doc}`CITATIONS` - Detailed page-numbered citations
- {doc}`CITATIONS_ACADEMIC` - Academic citation guidelines

**Citation Management:**
- Complete BibTeX bibliography with 50+ references
- Detailed page-numbered citations for all algorithms
- Software dependencies and license attributions
- Design pattern attributions and credit

---

## Quick Navigation

**Most Common Pages:**

- [Getting Started Guide](guides/getting-started.md) - Begin here
- [API Index](api/index.md) - Complete API reference
- [Controller Factory](factory/README.md) - Controller system architecture
- [PSO Optimization](api/pso_optimization.md) - Optimization workflows
- [Testing Guide](TESTING.md) - Test execution and standards
- [Contributing](CONTRIBUTING.md) - Development guidelines

**Frequently Accessed:**

- [Troubleshooting](troubleshooting/index.md) - Common issues and solutions
- [Deployment Guide](deployment/DEPLOYMENT_GUIDE.md) - Production deployment
- [Docker Setup](deployment/docker.md) - Containerization
- [Benchmarks](benchmarks/index.md) - Performance benchmarks

---

## Search & Discovery

**Finding What You Need:**

1. **By Task**: Use the [User Guides](guides/index.md) for task-oriented instructions
2. **By Module**: Use the [API Reference](api/index.md) for code documentation
3. **By Topic**: Use the [Theory Overview](theory/index.md) for conceptual understanding
4. **By Example**: Use the [Tutorials](tutorials/index.md) for hands-on learning

**Search Tips:**

- Use the search bar (top-right) for full-text search
- Browse by category using the sidebar navigation
- Check cross-references for related topics
- Refer to the bibliography for academic citations

---

**Last Updated:** 2025-10-11
