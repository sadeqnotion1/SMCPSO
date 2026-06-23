"""
Sphinx extension for Plotly interactive chart visualizations.

Provides custom directives for embedding interactive Plotly charts
that support zoom, pan, hover tooltips, and data export.

Usage:
    .. plotly-chart::
       :type: line
       :data: results.json
       :title: Performance Comparison

    .. plotly-comparison::
       :controllers: classical_smc,sta_smc
       :metrics: settling_time,overshoot

    .. plotly-convergence::
       :pso-log: pso_run.json
       :show-particles: true
"""

from typing import List, Dict, Any
import json
import hashlib
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective


class PlotlyChartDirective(SphinxDirective):
    """
    Directive for embedding generic Plotly charts.

    Supports multiple chart types: line, scatter, bar, box, heatmap, radar.
    Data can be provided inline (JSON), from external files, or generated.

    Options:
        :type: Chart type (line, scatter, bar, box, heatmap, radar, 3d-scatter)
        :data: Data source (inline JSON string or file path)
        :title: Chart title
        :x-axis: X-axis label
        :y-axis: Y-axis label
        :height: Chart height (e.g., "500px")
        :width: Chart width (e.g., "100%")
        :config: Configuration flags (comma-separated)
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 0

    option_spec = {
        'type': directives.unchanged,
        'data': directives.unchanged,
        'title': directives.unchanged,
        'x-axis': directives.unchanged,
        'y-axis': directives.unchanged,
        'height': directives.unchanged,
        'width': directives.unchanged,
        'config': directives.unchanged,
        'color-by': directives.unchanged,
        'hover-template': directives.unchanged,
    }

    def run(self) -> List[nodes.Node]:
        """Process the plotly-chart directive and generate HTML."""

        # Get options
        chart_type = self.options.get('type', 'line')
        data_source = self.options.get('data', '')
        title = self.options.get('title', '')
        x_axis = self.options.get('x-axis', '')
        y_axis = self.options.get('y-axis', '')
        height = self.options.get('height', '500px')
        width = self.options.get('width', '100%')
        config = self.options.get('config', '')
        color_by = self.options.get('color-by', '')
        hover_template = self.options.get('hover-template', '')

        # Get inline data from content
        inline_data = '\n'.join(self.content) if self.content else ''

        # Determine data source
        if inline_data.strip():
            chart_data = inline_data
            data_type = 'inline'
        elif data_source:
            chart_data = data_source
            data_type = 'file'
        else:
            self.state_machine.reporter.warning(
                'plotly-chart: No data provided (use :data: or inline content)',
                line=self.lineno
            )
            chart_data = '{}'
            data_type = 'inline'

        # Generate unique ID
        data_hash = hashlib.md5(chart_data.encode()).hexdigest()[:8]
        chart_id = f"plotly-chart-{self.env.new_serialno('plotly-chart')}-{data_hash}"

        # Build HTML
        html = self.generate_html(
            chart_id=chart_id,
            chart_type=chart_type,
            chart_data=chart_data,
            data_type=data_type,
            title=title,
            x_axis=x_axis,
            y_axis=y_axis,
            height=height,
            width=width,
            config=config,
            color_by=color_by,
            hover_template=hover_template
        )

        return [nodes.raw('', html, format='html')]

    def generate_html(self, chart_id: str, chart_type: str, chart_data: str,
                     data_type: str, title: str, x_axis: str, y_axis: str,
                     height: str, width: str, config: str, color_by: str,
                     hover_template: str) -> str:
        """Generate HTML for Plotly chart."""

        import html

        # Escape data for HTML attributes
        escaped_data = html.escape(chart_data)

        html_parts = []

        # Container div
        html_parts.append('<div class="plotly-chart-container">')

        # Caption
        if title:
            html_parts.append(f'''
<div class="plotly-chart-caption">
    <strong>📊 {html.escape(title)}</strong>
</div>
            ''')

        # Chart div with data attributes
        html_parts.append(f'''
<div id="{chart_id}"
     class="plotly-chart"
     data-chart-type="{chart_type}"
     data-chart-data="{escaped_data}"
     data-data-type="{data_type}"
     data-x-axis="{html.escape(x_axis)}"
     data-y-axis="{html.escape(y_axis)}"
     data-height="{height}"
     data-width="{width}"
     data-config="{html.escape(config)}"
     data-color-by="{html.escape(color_by)}"
     data-hover-template="{html.escape(hover_template)}"
     style="width:{width};height:{height};"></div>
        ''')

        # Info box
        html_parts.append('''
<div class="plotly-chart-info">
    <small>
        💡 <strong>Interactive Chart:</strong>
        Click and drag to zoom, double-click to reset, hover for details.
        Use toolbar (top-right) to pan, export, or customize view.
    </small>
</div>
        ''')

        html_parts.append('</div>')

        return '\n'.join(html_parts)


class PlotlyComparisonDirective(SphinxDirective):
    """
    Directive for controller performance comparison charts.

    Generates side-by-side comparison of multiple controllers across
    different performance metrics (settling time, overshoot, ISE, etc.).

    Options:
        :controllers: Comma-separated list of controller names
        :metrics: Comma-separated list of metrics to compare
        :data-dir: Directory containing result JSON files
        :layout: Grid layout (e.g., "2x2", "1x4")
        :title: Overall comparison title
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    option_spec = {
        'controllers': directives.unchanged_required,
        'metrics': directives.unchanged_required,
        'data-dir': directives.unchanged,
        'layout': directives.unchanged,
        'title': directives.unchanged,
        'normalize': directives.flag,
    }

    def run(self) -> List[nodes.Node]:
        """Process the plotly-comparison directive."""

        controllers = self.options.get('controllers', '').split(',')
        metrics = self.options.get('metrics', '').split(',')
        data_dir = self.options.get('data-dir', 'results/')
        layout = self.options.get('layout', '2x2')
        title = self.options.get('title', 'Controller Performance Comparison')
        normalize = 'normalize' in self.options

        # Clean up lists
        controllers = [c.strip() for c in controllers if c.strip()]
        metrics = [m.strip() for m in metrics if m.strip()]

        if not controllers or not metrics:
            self.state_machine.reporter.warning(
                'plotly-comparison: Must specify controllers and metrics',
                line=self.lineno
            )
            return []

        # Generate unique ID
        comparison_id = f"plotly-comparison-{self.env.new_serialno('plotly-comparison')}"

        # Build HTML
        html = self.generate_comparison_html(
            comparison_id=comparison_id,
            controllers=controllers,
            metrics=metrics,
            data_dir=data_dir,
            layout=layout,
            title=title,
            normalize=normalize
        )

        return [nodes.raw('', html, format='html')]

    def generate_comparison_html(self, comparison_id: str, controllers: List[str],
                                metrics: List[str], data_dir: str, layout: str,
                                title: str, normalize: bool) -> str:
        """Generate HTML for controller comparison."""

        import html

        # Convert lists to JSON strings
        controllers_json = json.dumps(controllers)
        metrics_json = json.dumps(metrics)

        html_parts = []

        html_parts.append('<div class="plotly-comparison-container">')

        # Title
        html_parts.append(f'''
<div class="plotly-comparison-title">
    <h3>📊 {html.escape(title)}</h3>
</div>
        ''')

        # Comparison div with data attributes
        html_parts.append(f'''
<div id="{comparison_id}"
     class="plotly-comparison"
     data-controllers='{controllers_json}'
     data-metrics='{metrics_json}'
     data-data-dir="{html.escape(data_dir)}"
     data-layout="{layout}"
     data-normalize="{str(normalize).lower()}"
     style="width:100%;min-height:600px;"></div>
        ''')

        # Controls
        html_parts.append('''
<div class="plotly-comparison-controls">
    <button class="plotly-btn" onclick="PlotlyIntegration.exportAllCharts(this)">
        📥 Export All Charts
    </button>
    <button class="plotly-btn" onclick="PlotlyIntegration.resetAllZoom(this)">
        🔄 Reset All Zoom
    </button>
</div>
        ''')

        html_parts.append('</div>')

        return '\n'.join(html_parts)


class PlotlyConvergenceDirective(SphinxDirective):
    """
    Directive for PSO convergence animation.

    Visualizes particle swarm optimization convergence with animated
    particles, best position trajectory, and convergence curve.

    Options:
        :pso-log: Path to PSO log JSON file
        :show-particles: Show individual particles (true/false)
        :show-gbest-trajectory: Show global best trajectory (true/false)
        :animation-speed: Animation speed in milliseconds per frame
        :color-by: Color particles by fitness or velocity
        :dimensions: Number of dimensions to visualize (2 or 3)
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    option_spec = {
        'pso-log': directives.unchanged_required,
        'show-particles': directives.unchanged,
        'show-gbest-trajectory': directives.unchanged,
        'animation-speed': directives.positive_int,
        'color-by': directives.unchanged,
        'dimensions': directives.positive_int,
        'title': directives.unchanged,
    }

    def run(self) -> List[nodes.Node]:
        """Process the plotly-convergence directive."""

        pso_log = self.options.get('pso-log', '')
        show_particles = self.options.get('show-particles', 'true').lower() == 'true'
        show_gbest = self.options.get('show-gbest-trajectory', 'true').lower() == 'true'
        animation_speed = self.options.get('animation-speed', 100)
        color_by = self.options.get('color-by', 'fitness')
        dimensions = self.options.get('dimensions', 2)
        title = self.options.get('title', 'PSO Convergence Animation')

        if not pso_log:
            self.state_machine.reporter.warning(
                'plotly-convergence: Must specify :pso-log:',
                line=self.lineno
            )
            return []

        # Generate unique ID
        convergence_id = f"plotly-convergence-{self.env.new_serialno('plotly-convergence')}"

        # Build HTML
        html = self.generate_convergence_html(
            convergence_id=convergence_id,
            pso_log=pso_log,
            show_particles=show_particles,
            show_gbest=show_gbest,
            animation_speed=animation_speed,
            color_by=color_by,
            dimensions=dimensions,
            title=title
        )

        return [nodes.raw('', html, format='html')]

    def generate_convergence_html(self, convergence_id: str, pso_log: str,
                                 show_particles: bool, show_gbest: bool,
                                 animation_speed: int, color_by: str,
                                 dimensions: int, title: str) -> str:
        """Generate HTML for PSO convergence animation."""

        import html

        html_parts = []

        html_parts.append('<div class="plotly-convergence-container">')

        # Title
        html_parts.append(f'''
<div class="plotly-convergence-title">
    <h3>🎬 {html.escape(title)}</h3>
</div>
        ''')

        # Convergence visualization div
        html_parts.append(f'''
<div id="{convergence_id}"
     class="plotly-convergence"
     data-pso-log="{html.escape(pso_log)}"
     data-show-particles="{str(show_particles).lower()}"
     data-show-gbest="{str(show_gbest).lower()}"
     data-animation-speed="{animation_speed}"
     data-color-by="{color_by}"
     data-dimensions="{dimensions}"
     style="width:100%;height:600px;"></div>
        ''')

        # Animation controls
        html_parts.append('''
<div class="plotly-convergence-controls">
    <button class="plotly-btn plotly-play" onclick="PlotlyIntegration.playAnimation(this)">
        ▶️ Play
    </button>
    <button class="plotly-btn plotly-pause" onclick="PlotlyIntegration.pauseAnimation(this)" disabled>
        ⏸️ Pause
    </button>
    <button class="plotly-btn" onclick="PlotlyIntegration.resetAnimation(this)">
        ⏮️ Reset
    </button>
    <span class="plotly-progress-label">Iteration: <span class="plotly-iteration-count">0</span></span>
</div>
        ''')

        html_parts.append('</div>')

        return '\n'.join(html_parts)


class PlotlyScatterMatrixDirective(SphinxDirective):
    """
    Directive for multi-dimensional parameter scatter matrix.

    Displays pairwise scatter plots of PSO search space exploration,
    useful for understanding parameter correlations and search behavior.

    Options:
        :parameters: Comma-separated list of parameter names
        :data: Data source (CSV or JSON file)
        :color-by: Variable to color points by (e.g., cost)
        :color-scale: Plotly colorscale name
        :title: Chart title
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    option_spec = {
        'parameters': directives.unchanged_required,
        'data': directives.unchanged_required,
        'color-by': directives.unchanged,
        'color-scale': directives.unchanged,
        'title': directives.unchanged,
        'dimensions': directives.positive_int,
    }

    def run(self) -> List[nodes.Node]:
        """Process the plotly-scatter-matrix directive."""

        parameters = self.options.get('parameters', '').split(',')
        data_source = self.options.get('data', '')
        color_by = self.options.get('color-by', 'cost')
        color_scale = self.options.get('color-scale', 'Viridis')
        title = self.options.get('title', 'Parameter Space Exploration')
        dimensions = self.options.get('dimensions', len(parameters))

        parameters = [p.strip() for p in parameters if p.strip()]

        if not parameters or not data_source:
            self.state_machine.reporter.warning(
                'plotly-scatter-matrix: Must specify parameters and data',
                line=self.lineno
            )
            return []

        # Generate unique ID
        matrix_id = f"plotly-scatter-matrix-{self.env.new_serialno('plotly-scatter-matrix')}"

        # Build HTML
        html = self.generate_scatter_matrix_html(
            matrix_id=matrix_id,
            parameters=parameters,
            data_source=data_source,
            color_by=color_by,
            color_scale=color_scale,
            title=title,
            dimensions=dimensions
        )

        return [nodes.raw('', html, format='html')]

    def generate_scatter_matrix_html(self, matrix_id: str, parameters: List[str],
                                    data_source: str, color_by: str,
                                    color_scale: str, title: str,
                                    dimensions: int) -> str:
        """Generate HTML for scatter matrix."""

        import html

        parameters_json = json.dumps(parameters)

        html_parts = []

        html_parts.append('<div class="plotly-scatter-matrix-container">')

        # Title
        html_parts.append(f'''
<div class="plotly-scatter-matrix-title">
    <h3>🎯 {html.escape(title)}</h3>
</div>
        ''')

        # Scatter matrix div
        html_parts.append(f'''
<div id="{matrix_id}"
     class="plotly-scatter-matrix"
     data-parameters='{parameters_json}'
     data-data-source="{html.escape(data_source)}"
     data-color-by="{html.escape(color_by)}"
     data-color-scale="{color_scale}"
     data-dimensions="{dimensions}"
     style="width:100%;height:700px;"></div>
        ''')

        html_parts.append('</div>')

        return '\n'.join(html_parts)


def add_plotly_assets(app: Sphinx, pagename: str, templatename: str,
                      context: Dict[str, Any], doctree: nodes.Node) -> None:
    """Add Plotly CSS styles to HTML pages."""

    if not hasattr(context, 'metatags'):
        context['metatags'] = ''

    # Add custom styles for directive-generated elements
    plotly_styles = '''
<style>
/* Plotly chart containers */
.plotly-chart-container,
.plotly-comparison-container,
.plotly-convergence-container,
.plotly-scatter-matrix-container {
    margin: 2em 0;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

/* Captions and titles */
.plotly-chart-caption,
.plotly-comparison-title,
.plotly-convergence-title,
.plotly-scatter-matrix-title {
    margin-bottom: 15px;
    padding: 10px 15px;
    background: white;
    border-radius: 8px;
    border-left: 4px solid #2196F3;
    font-size: 15px;
    color: #333;
}

/* Info boxes */
.plotly-chart-info {
    margin-top: 15px;
    padding: 12px 15px;
    background: #e3f2fd;
    border-radius: 6px;
    border-left: 3px solid #2196F3;
}

/* Control buttons */
.plotly-comparison-controls,
.plotly-convergence-controls {
    margin-top: 15px;
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
}

.plotly-btn {
    padding: 8px 16px;
    background: #2196F3;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.2s;
}

.plotly-btn:hover {
    background: #1976D2;
}

.plotly-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
}

.plotly-progress-label {
    font-size: 14px;
    color: #555;
    margin-left: auto;
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
    .plotly-chart-container,
    .plotly-comparison-container,
    .plotly-convergence-container,
    .plotly-scatter-matrix-container {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
    }

    .plotly-chart-caption,
    .plotly-comparison-title,
    .plotly-convergence-title,
    .plotly-scatter-matrix-title {
        background: #2d3748;
        color: #e2e8f0;
    }

    .plotly-chart-info {
        background: #1e2d3d;
        border-left-color: #60a5fa;
        color: #90caf9;
    }

    .plotly-progress-label {
        color: #e2e8f0;
    }
}
</style>
    '''

    context['metatags'] += plotly_styles


def setup(app: Sphinx) -> Dict[str, Any]:
    """Setup the Plotly extension."""

    # Register directives
    app.add_directive('plotly-chart', PlotlyChartDirective)
    app.add_directive('plotly-comparison', PlotlyComparisonDirective)
    app.add_directive('plotly-convergence', PlotlyConvergenceDirective)
    app.add_directive('plotly-scatter-matrix', PlotlyScatterMatrixDirective)

    # Add custom CSS to pages
    app.connect('html-page-context', add_plotly_assets)

    return {
        'version': '1.0.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
