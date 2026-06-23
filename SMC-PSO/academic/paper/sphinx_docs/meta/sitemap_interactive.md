# Interactive Documentation Map

Explore the documentation structure visually with an interactive force-directed graph.

**[CORE]** [Master Navigation Hub](NAVIGATION.md) - Complete documentation mapping across all 985 files and 11 navigation systems.

<div id="visual-sitemap-container" style="width: 100%; height: 800px; margin: 2rem 0; border: 2px solid #e5e7eb; border-radius: 12px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);"></div>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script src="_static/visual-sitemap.js"></script>

## How to Use

**🎯 Navigate**: Click any node to jump to that documentation page
**🔍 Zoom**: Scroll to zoom in/out
**👆 Drag**: Click and drag nodes to rearrange
**💡 Explore**: Hover over nodes for quick info

## Color Legend

- **Green**: Getting Started - Installation, quick start, tutorials
- **Blue**: User Guides - Simulations, optimization, configuration
- **Purple**: API Reference - Controllers, optimization, simulation engines
- **Pink**: Theory & Mathematics - SMC theory, PSO algorithms, stability
- **Teal**: Testing & Validation - Test standards, benchmarks, coverage
- **Orange**: Deployment - Docker, production, cloud platforms
- **Gray**: Project Documentation - Changelog, contributing, citations

## Alternative Views

- {doc}`NAVIGATION` - [CORE] Master navigation hub connecting all 985 files and 11 systems
- {doc}`sitemap_visual` - Mermaid mindmap and flowcharts
- {doc}`documentation_structure` - Traditional text-based sitemap
- {doc}`index` - Main landing page with hierarchical navigation

---

**Tip**: This visualization shows not just the hierarchy, but also the relationships between different sections. Notice how "Quick Start" connects to "Simulations", which connects to "PSO Workflows"  - representing the typical user journey!
