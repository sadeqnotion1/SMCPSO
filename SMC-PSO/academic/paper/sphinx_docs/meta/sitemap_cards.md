# Visual Documentation Navigator

<link rel="stylesheet" href="_static/visual-tree.css">

<div class="visual-tree">

<div class="visual-tree-root">
    <div class="tree-root-node">
        DIP SMC PSO Documentation
    </div>
</div>

<div class="tree-branches">

<!-- Navigation Hub (Master) -->
<div class="tree-branch navigation-hub">
    <div class="branch-header">
        <div class="branch-icon">[CORE]</div>
        <div class="branch-title">Master Navigation Hub</div>
    </div>
    <div class="branch-description">
        Complete documentation mapping across all 985 files and 11 navigation systems
    </div>
    <ul class="branch-links">
        <li><a href="NAVIGATION.html">NAVIGATION.md - Start Here <span class="branch-badge badge-new">NEW!</span></a></li>
    </ul>
</div>

<!-- Getting Started Branch -->
<div class="tree-branch getting-started">
    <div class="branch-header">
        <div class="branch-icon">🚀</div>
        <div class="branch-title">Getting Started</div>
    </div>
    <div class="branch-description">
        Installation guides, quick start tutorials, and first steps
    </div>
    <ul class="branch-links">
        <li><a href="README.html">Installation Guide <span class="branch-badge badge-new">Start Here</span></a></li>
        <li><a href="guides/getting-started.html">Quick Start Tutorial</a></li>
        <li><a href="streamlit_dashboard_guide.html">Interactive Dashboard</a></li>
        <li><a href="hil_quickstart.html">Hardware-in-the-Loop Setup</a></li>
    </ul>
</div>

<!-- User Guides Branch -->
<div class="tree-branch user-guides">
    <div class="branch-header">
        <div class="branch-icon">📖</div>
        <div class="branch-title">User Guides</div>
    </div>
    <div class="branch-description">
        Step-by-step instructions for common tasks and workflows
    </div>
    <ul class="branch-links">
        <li><a href="guides/how-to/running-simulations.html" class="has-children">Running Simulations</a></li>
        <li><a href="guides/how-to/optimization-workflows.html" class="has-children">PSO Optimization <span class="branch-badge badge-popular">Popular</span></a></li>
        <li><a href="guides/how-to/testing-validation.html">Testing & Validation</a></li>
        <li><a href="guides/interactive_configuration_guide.html">Configuration Guide</a></li>
        <li><a href="workflows/index.html" class="has-children">Complete Workflows</a></li>
    </ul>
</div>

<!-- API Reference Branch -->
<div class="tree-branch api-reference">
    <div class="branch-header">
        <div class="branch-icon">🔧</div>
        <div class="branch-title">API Reference</div>
    </div>
    <div class="branch-description">
        Complete API documentation for all modules and classes
    </div>
    <ul class="branch-links">
        <li><a href="reference/controllers/index.html" class="has-children">Controllers API <span class="branch-badge badge-important">Core</span></a></li>
        <li><a href="reference/optimization/index.html" class="has-children">Optimization API</a></li>
        <li><a href="reference/simulation/index.html" class="has-children">Simulation Engine</a></li>
        <li><a href="reference/plant/index.html" class="has-children">Plant Dynamics</a></li>
        <li><a href="reference/analysis/index.html" class="has-children">Analysis Tools</a></li>
        <li><a href="reference/utils/index.html" class="has-children">Utilities</a></li>
        <li><a href="reference/interfaces/index.html" class="has-children">System Interfaces</a></li>
    </ul>
</div>

<!-- Theory & Mathematics Branch -->
<div class="tree-branch theory">
    <div class="branch-header">
        <div class="branch-icon">📐</div>
        <div class="branch-title">Theory & Math</div>
    </div>
    <div class="branch-description">
        Mathematical foundations, control theory, and algorithms
    </div>
    <ul class="branch-links">
        <li><a href="theory/index.html" class="has-children">Control Theory</a></li>
        <li><a href="theory/pso_algorithm_foundations.html">PSO Algorithm Foundations</a></li>
        <li><a href="mathematical_foundations/index.html" class="has-children">Lyapunov Stability</a></li>
        <li><a href="plant_model.html">Pendulum Dynamics</a></li>
        <li><a href="architecture.html">System Architecture</a></li>
    </ul>
</div>

<!-- Testing & Validation Branch -->
<div class="tree-branch testing">
    <div class="branch-header">
        <div class="branch-icon">✅</div>
        <div class="branch-title">Testing</div>
    </div>
    <div class="branch-description">
        Testing standards, benchmarks, and quality assurance
    </div>
    <ul class="branch-links">
        <li><a href="TESTING.html">Test Standards <span class="branch-badge badge-important">≥85%</span></a></li>
        <li><a href="benchmarks/index.html" class="has-children">Performance Benchmarks</a></li>
        <li><a href="validation/index.html" class="has-children">Validation Protocols</a></li>
        <li><a href="test_infrastructure_validation_report.html">Infrastructure Report</a></li>
        <li><a href="test_execution_guide.html">Execution Guide</a></li>
    </ul>
</div>

<!-- Deployment Branch -->
<div class="tree-branch deployment">
    <div class="branch-header">
        <div class="branch-icon">🚢</div>
        <div class="branch-title">Deployment</div>
    </div>
    <div class="branch-description">
        Production deployment, Docker, cloud platforms
    </div>
    <ul class="branch-links">
        <li><a href="deployment/DEPLOYMENT_GUIDE.html" class="has-children">Deployment Guide</a></li>
        <li><a href="deployment/docker.html">Docker Setup</a></li>
        <li><a href="deployment/STREAMLIT_DEPLOYMENT.html">Streamlit Deployment</a></li>
        <li><a href="production/index.html" class="has-children">Production Readiness</a></li>
    </ul>
</div>

<!-- Project Documentation Branch -->
<div class="tree-branch project-docs">
    <div class="branch-header">
        <div class="branch-icon">📋</div>
        <div class="branch-title">Project Docs</div>
    </div>
    <div class="branch-description">
        Changelog, contributing guidelines, citations
    </div>
    <ul class="branch-links">
        <li><a href="CHANGELOG.html">Version History</a></li>
        <li><a href="CONTRIBUTING.html">Contributing Guide</a></li>
        <li><a href="DEPENDENCIES.html">Dependencies & Licenses</a></li>
        <li><a href="CITATIONS.html">Citations & References</a></li>
        <li><a href="bibliography.html">Complete Bibliography</a></li>
    </ul>
</div>

</div>

</div>

## Alternative Navigation Views

- {doc}`sitemap_interactive` - Interactive D3.js force-directed graph
- {doc}`sitemap_visual` - Mermaid mindmap and flowcharts
- {doc}`documentation_structure` - Traditional text-based sitemap
- {doc}`index` - Main landing page

---

**💡 Tip**: Click any link to navigate directly to that section. Links marked with ▸ contain sub-sections with more detailed documentation.
