"""
Sphinx extension for Chart.js integration.

Provides custom directives for embedding interactive Chart.js visualizations
in Sphinx documentation.
"""
from typing import List, Dict, Any
from docutils import nodes
from docutils.parsers.rst import directives, Directive
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective
import json


class ChartJSDirective(SphinxDirective):
    """
    Directive for embedding Chart.js charts in documentation.

    Usage:
        .. chartjs::
           :type: line
           :data: path/to/data.json
           :height: 400

           {
               "labels": ["A", "B", "C"],
               "datasets": [{
                   "label": "Dataset 1",
                   "data": [10, 20, 30]
               }]
           }
    """
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    option_spec = {
        'type': directives.unchanged,
        'data': directives.unchanged,
        'height': directives.positive_int,
        'width': directives.unchanged,
        'title': directives.unchanged,
        'responsive': directives.flag,
        'animation': directives.flag,
    }

    def run(self) -> List[nodes.Node]:
        """Process the chartjs directive."""
        # Generate unique chart ID
        chart_id = f"chart-{self.env.new_serialno('chartjs')}"

        # Get chart configuration
        chart_type = self.options.get('type', 'line')
        chart_height = self.options.get('height', 400)
        chart_width = self.options.get('width', '100%')
        chart_title = self.options.get('title', '')
        responsive = 'responsive' in self.options
        animation = 'animation' not in self.options  # Default true

        # Parse chart data from content or file
        if 'data' in self.options:
            # Load from file
            data_path = self.options['data']
            try:
                with open(data_path, 'r') as f:
                    chart_data = json.load(f)
            except Exception as e:
                self.state_machine.reporter.warning(
                    f'Failed to load chart data from {data_path}: {e}',
                    line=self.lineno
                )
                chart_data = {}
        else:
            # Parse from directive content
            try:
                content_text = '\n'.join(self.content)
                chart_data = json.loads(content_text) if content_text.strip() else {}
            except json.JSONDecodeError as e:
                self.state_machine.reporter.warning(
                    f'Invalid JSON in chartjs directive: {e}',
                    line=self.lineno
                )
                chart_data = {}

        # Build Chart.js configuration
        chart_config = {
            'type': chart_type,
            'data': chart_data,
            'options': {
                'responsive': responsive,
                'maintainAspectRatio': not responsive,
                'animation': animation,
                'plugins': {
                    'title': {
                        'display': bool(chart_title),
                        'text': chart_title
                    }
                }
            }
        }

        # Create HTML container
        html = f'''
<div class="chartjs-container" style="width: {chart_width}; margin: 1em auto;">
    <canvas id="{chart_id}" height="{chart_height}"></canvas>
</div>
<script>
(function() {{
    var ctx = document.getElementById('{chart_id}').getContext('2d');
    var config = {json.dumps(chart_config, indent=2)};
    new Chart(ctx, config);
}})();
</script>
'''

        # Return raw HTML node
        raw_node = nodes.raw('', html, format='html')
        return [raw_node]


class ControllerComparisonDirective(SphinxDirective):
    """
    Specialized directive for controller performance comparison charts.

    Usage:
        .. controller-comparison::
           :metric: settling_time
           :controllers: classical_smc,adaptive_smc,hybrid_smc
    """
    has_content = False
    required_arguments = 0
    optional_arguments = 0
    option_spec = {
        'metric': directives.unchanged_required,
        'controllers': directives.unchanged_required,
        'height': directives.positive_int,
    }

    # Predefined controller colors
    CONTROLLER_COLORS = {
        'classical_smc': 'rgba(54, 162, 235, 0.8)',
        'adaptive_smc': 'rgba(255, 99, 132, 0.8)',
        'hybrid_smc': 'rgba(75, 192, 192, 0.8)',
        'terminal_smc': 'rgba(255, 206, 86, 0.8)',
    }

    # Metric display names
    METRIC_LABELS = {
        'settling_time': 'Settling Time (s)',
        'overshoot': 'Overshoot (%)',
        'steady_state_error': 'Steady-State Error',
        'rise_time': 'Rise Time (s)',
        'control_effort': 'Control Effort',
    }

    def run(self) -> List[nodes.Node]:
        """Process the controller-comparison directive."""
        chart_id = f"controller-comparison-{self.env.new_serialno('controller-comparison')}"

        metric = self.options['metric']
        controllers = [c.strip() for c in self.options['controllers'].split(',')]
        chart_height = self.options.get('height', 400)

        # Build dataset (in real implementation, this would load from results)
        datasets = []
        for controller in controllers:
            color = self.CONTROLLER_COLORS.get(controller, 'rgba(153, 102, 255, 0.8)')
            datasets.append({
                'label': controller.replace('_', ' ').title(),
                'data': [0],  # Placeholder - would load from actual results
                'backgroundColor': color,
                'borderColor': color.replace('0.8', '1'),
                'borderWidth': 2
            })

        metric_label = self.METRIC_LABELS.get(metric, metric.replace('_', ' ').title())

        chart_config = {
            'type': 'bar',
            'data': {
                'labels': [metric_label],
                'datasets': datasets
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'Controller Comparison: {metric_label}'
                    },
                    'legend': {
                        'display': True,
                        'position': 'top'
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True
                    }
                }
            }
        }

        html = f'''
<div class="controller-comparison-chart" style="width: 100%; margin: 1em auto;">
    <canvas id="{chart_id}" height="{chart_height}"></canvas>
</div>
<script>
(function() {{
    var ctx = document.getElementById('{chart_id}').getContext('2d');
    var config = {json.dumps(chart_config, indent=2)};
    new Chart(ctx, config);
}})();
</script>
<p class="chart-note"><em>Note: Data would be loaded from simulation results in production.</em></p>
'''

        raw_node = nodes.raw('', html, format='html')
        return [raw_node]


class PSOConvergenceDirective(SphinxDirective):
    """
    Specialized directive for PSO convergence visualization.

    Usage:
        .. pso-convergence::
           :iterations: 100
           :particles: 30
    """
    has_content = False
    required_arguments = 0
    optional_arguments = 0
    option_spec = {
        'iterations': directives.positive_int,
        'particles': directives.positive_int,
        'height': directives.positive_int,
    }

    def run(self) -> List[nodes.Node]:
        """Process the pso-convergence directive."""
        chart_id = f"pso-convergence-{self.env.new_serialno('pso-convergence')}"

        iterations = self.options.get('iterations', 100)
        particles = self.options.get('particles', 30)
        chart_height = self.options.get('height', 400)

        # Generate sample convergence data
        # In real implementation, this would load from PSO logs
        chart_config = {
            'type': 'line',
            'data': {
                'labels': list(range(iterations)),
                'datasets': [
                    {
                        'label': 'Global Best Fitness',
                        'data': [],  # Placeholder
                        'borderColor': 'rgba(54, 162, 235, 1)',
                        'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                        'borderWidth': 2,
                        'fill': True,
                        'tension': 0.4
                    },
                    {
                        'label': 'Average Fitness',
                        'data': [],  # Placeholder
                        'borderColor': 'rgba(255, 99, 132, 1)',
                        'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                        'borderWidth': 2,
                        'fill': True,
                        'tension': 0.4
                    }
                ]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'PSO Convergence ({particles} particles, {iterations} iterations)'
                    },
                    'legend': {
                        'display': True,
                        'position': 'top'
                    }
                },
                'scales': {
                    'x': {
                        'title': {
                            'display': True,
                            'text': 'Iteration'
                        }
                    },
                    'y': {
                        'title': {
                            'display': True,
                            'text': 'Fitness Value'
                        },
                        'type': 'logarithmic'
                    }
                }
            }
        }

        html = f'''
<div class="pso-convergence-chart" style="width: 100%; margin: 1em auto;">
    <canvas id="{chart_id}" height="{chart_height}"></canvas>
</div>
<script>
(function() {{
    var ctx = document.getElementById('{chart_id}').getContext('2d');
    var config = {json.dumps(chart_config, indent=2)};
    new Chart(ctx, config);
}})();
</script>
<p class="chart-note"><em>Note: Sample data shown. Load actual PSO logs for real convergence data.</em></p>
'''

        raw_node = nodes.raw('', html, format='html')
        return [raw_node]


def add_chartjs_assets(app: Sphinx, pagename: str, templatename: str,
                       context: Dict[str, Any], doctree: nodes.Node) -> None:
    """Add Chart.js assets to HTML pages."""
    if not hasattr(context, 'metatags'):
        context['metatags'] = ''

    # Add Chart.js CDN
    chartjs_script = '''
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
.chartjs-container {
    margin: 1.5em auto;
    padding: 1em;
    background: #f8f9fa;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.chart-note {
    text-align: center;
    color: #6c757d;
    font-size: 0.9em;
    margin-top: 0.5em;
}
</style>
'''
    context.setdefault('script_files', [])
    context['metatags'] += chartjs_script


def setup(app: Sphinx) -> Dict[str, Any]:
    """Setup the Chart.js extension."""
    # Register directives
    app.add_directive('chartjs', ChartJSDirective)
    app.add_directive('controller-comparison', ControllerComparisonDirective)
    app.add_directive('pso-convergence', PSOConvergenceDirective)

    # Add Chart.js assets to pages
    app.connect('html-page-context', add_chartjs_assets)

    return {
        'version': '0.1.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
