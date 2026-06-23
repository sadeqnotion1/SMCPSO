"""
Sphinx extension for mathematical visualization of control theory concepts.

Provides custom directives for interactive mathematical plots including phase portraits,
Lyapunov functions, stability regions, and control signal analysis.

Usage:
    .. phase-portrait::
       :system: double_pendulum
       :initial-state: [0.1, 0, 0.2, 0]
       :time-range: [0, 10]
       :vector-field: true

    .. lyapunov-surface::
       :function: V = 0.5*s^2
       :trajectory: reaching_phase.json
       :level-curves: [0.1, 0.5, 1.0, 2.0]

    .. stability-region::
       :param1: k1
       :param2: k2
       :range1: [0, 100]
       :range2: [0, 50]
"""

from typing import List, Dict, Any
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective


class PhasePortraitDirective(SphinxDirective):
    """
    Directive for 2D phase portrait visualization.

    Displays state space trajectories, equilibrium points, and vector fields
    for dynamic systems. Perfect for showing SMC reaching and sliding phases.

    Options:
        :system: System type (double_pendulum, linear, nonlinear, custom)
        :initial-state: Initial conditions as [x1, x2, ...] or JSON
        :time-range: Time span [t_start, t_end]
        :vector-field: Show vector field (true/false)
        :equilibrium: Mark equilibrium points (true/false)
        :title: Plot title
        :x-label: X-axis label
        :y-label: Y-axis label
        :trajectory-color: Color for trajectory line
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 0

    option_spec = {
        'system': directives.unchanged,
        'initial-state': directives.unchanged,
        'time-range': directives.unchanged,
        'vector-field': directives.unchanged,
        'equilibrium': directives.unchanged,
        'title': directives.unchanged,
        'x-label': directives.unchanged,
        'y-label': directives.unchanged,
        'trajectory-color': directives.unchanged,
        'width': directives.unchanged,
        'height': directives.unchanged,
    }

    def run(self) -> List[nodes.Node]:
        """Process the phase-portrait directive."""

        system = self.options.get('system', 'custom')
        initial_state = self.options.get('initial-state', '[0, 0]')
        time_range = self.options.get('time-range', '[0, 10]')
        vector_field = self.options.get('vector-field', 'false').lower() == 'true'
        equilibrium = self.options.get('equilibrium', 'true').lower() == 'true'
        title = self.options.get('title', 'Phase Portrait')
        x_label = self.options.get('x-label', 'State x₁')
        y_label = self.options.get('y-label', 'State x₂')
        trajectory_color = self.options.get('trajectory-color', '#2196F3')
        width = self.options.get('width', '100%')
        height = self.options.get('height', '600px')

        # Get custom dynamics from content
        custom_dynamics = '\n'.join(self.content) if self.content else ''

        # Generate unique ID
        plot_id = f"phase-portrait-{self.env.new_serialno('phase-portrait')}"

        # Build HTML
        html = self.generate_phase_portrait_html(
            plot_id=plot_id,
            system=system,
            initial_state=initial_state,
            time_range=time_range,
            vector_field=vector_field,
            equilibrium=equilibrium,
            title=title,
            x_label=x_label,
            y_label=y_label,
            trajectory_color=trajectory_color,
            width=width,
            height=height,
            custom_dynamics=custom_dynamics
        )

        return [nodes.raw('', html, format='html')]

    def generate_phase_portrait_html(self, plot_id: str, system: str,
                                     initial_state: str, time_range: str,
                                     vector_field: bool, equilibrium: bool,
                                     title: str, x_label: str, y_label: str,
                                     trajectory_color: str, width: str, height: str,
                                     custom_dynamics: str) -> str:
        """Generate HTML for phase portrait visualization."""

        import html as html_module

        html_parts = []

        html_parts.append('<div class="mathviz-container mathviz-phase-portrait">')

        # Title
        html_parts.append(f'''
<div class="mathviz-header">
    <strong>📈 {html_module.escape(title)}</strong>
    <span class="mathviz-badge">Phase Portrait</span>
</div>
        ''')

        # Plot container
        html_parts.append(f'''
<div id="{plot_id}"
     class="mathviz-plot"
     data-viz-type="phase-portrait"
     data-system="{html_module.escape(system)}"
     data-initial-state="{html_module.escape(initial_state)}"
     data-time-range="{html_module.escape(time_range)}"
     data-vector-field="{str(vector_field).lower()}"
     data-equilibrium="{str(equilibrium).lower()}"
     data-x-label="{html_module.escape(x_label)}"
     data-y-label="{html_module.escape(y_label)}"
     data-trajectory-color="{html_module.escape(trajectory_color)}"
     data-custom-dynamics="{html_module.escape(custom_dynamics)}"
     style="width:{width};height:{height};"></div>
        ''')

        # Controls
        html_parts.append('''
<div class="mathviz-controls">
    <button class="mathviz-btn" onclick="MathViz.resetView(this)">
        🔄 Reset View
    </button>
    <button class="mathviz-btn" onclick="MathViz.exportPlot(this)">
        📥 Export PNG
    </button>
    <label class="mathviz-toggle">
        <input type="checkbox" onchange="MathViz.toggleVectorField(this)" checked>
        Show Vector Field
    </label>
</div>
        ''')

        # Info box
        html_parts.append(f'''
<div class="mathviz-info">
    <small>
        💡 <strong>Interactive Phase Portrait:</strong>
        Drag to pan, scroll to zoom. Shows system evolution from initial state
        <code>{html_module.escape(initial_state)}</code>.
    </small>
</div>
        ''')

        html_parts.append('</div>')

        return '\n'.join(html_parts)


class LyapunovSurfaceDirective(SphinxDirective):
    """
    Directive for 3D Lyapunov function visualization.

    Displays Lyapunov "energy bowl" surface with system trajectories showing
    convergence to equilibrium. Great for visualizing stability proofs.

    Options:
        :function: Lyapunov function formula (e.g., "V = 0.5*s^2")
        :trajectory: Path to trajectory data JSON file
        :level-curves: List of level curve values [0.1, 0.5, 1.0]
        :gradient-flow: Show gradient flow vectors (true/false)
        :title: Plot title
        :colorscale: Plotly colorscale name (Viridis, Plasma, etc.)
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    option_spec = {
        'function': directives.unchanged_required,
        'trajectory': directives.unchanged,
        'level-curves': directives.unchanged,
        'gradient-flow': directives.unchanged,
        'title': directives.unchanged,
        'colorscale': directives.unchanged,
        'width': directives.unchanged,
        'height': directives.unchanged,
    }

    def run(self) -> List[nodes.Node]:
        """Process the lyapunov-surface directive."""

        function = self.options.get('function', 'V = 0.5*s^2')
        trajectory = self.options.get('trajectory', '')
        level_curves = self.options.get('level-curves', '[0.1, 0.5, 1.0, 2.0]')
        gradient_flow = self.options.get('gradient-flow', 'false').lower() == 'true'
        title = self.options.get('title', 'Lyapunov Energy Surface')
        colorscale = self.options.get('colorscale', 'Viridis')
        width = self.options.get('width', '100%')
        height = self.options.get('height', '600px')

        # Generate unique ID
        plot_id = f"lyapunov-surface-{self.env.new_serialno('lyapunov-surface')}"

        # Build HTML
        html = self.generate_lyapunov_html(
            plot_id=plot_id,
            function=function,
            trajectory=trajectory,
            level_curves=level_curves,
            gradient_flow=gradient_flow,
            title=title,
            colorscale=colorscale,
            width=width,
            height=height
        )

        return [nodes.raw('', html, format='html')]

    def generate_lyapunov_html(self, plot_id: str, function: str,
                               trajectory: str, level_curves: str,
                               gradient_flow: bool, title: str,
                               colorscale: str, width: str, height: str) -> str:
        """Generate HTML for Lyapunov surface visualization."""

        import html as html_module

        html_parts = []

        html_parts.append('<div class="mathviz-container mathviz-lyapunov">')

        # Title with equation
        html_parts.append(f'''
<div class="mathviz-header">
    <strong>🎯 {html_module.escape(title)}</strong>
    <span class="mathviz-equation">{html_module.escape(function)}</span>
</div>
        ''')

        # Plot container
        html_parts.append(f'''
<div id="{plot_id}"
     class="mathviz-plot"
     data-viz-type="lyapunov-surface"
     data-function="{html_module.escape(function)}"
     data-trajectory="{html_module.escape(trajectory)}"
     data-level-curves="{html_module.escape(level_curves)}"
     data-gradient-flow="{str(gradient_flow).lower()}"
     data-colorscale="{html_module.escape(colorscale)}"
     style="width:{width};height:{height};"></div>
        ''')

        # Controls
        html_parts.append('''
<div class="mathviz-controls">
    <button class="mathviz-btn" onclick="MathViz.rotate3D(this, 'reset')">
        🔄 Reset View
    </button>
    <button class="mathviz-btn" onclick="MathViz.toggleProjection(this)">
        📐 Toggle Projection
    </button>
    <label class="mathviz-toggle">
        <input type="checkbox" onchange="MathViz.toggleLevelCurves(this)" checked>
        Show Level Curves
    </label>
</div>
        ''')

        # Info box with theory
        html_parts.append(f'''
<div class="mathviz-info">
    <small>
        💡 <strong>Lyapunov "Energy Bowl":</strong>
        Function <code>{html_module.escape(function)}</code> always decreases along trajectories (V̇ < 0),
        proving convergence to equilibrium at the bottom of the bowl.
    </small>
</div>
        ''')

        html_parts.append('</div>')

        return '\n'.join(html_parts)


class StabilityRegionDirective(SphinxDirective):
    """
    Directive for parameter space stability analysis.

    Shows regions of stable/unstable behavior in 2D parameter space.
    Useful for gain selection and understanding parameter sensitivity.

    Options:
        :param1: First parameter name (e.g., "k1", "alpha")
        :param2: Second parameter name (e.g., "k2", "beta")
        :range1: Range for param1 as [min, max]
        :range2: Range for param2 as [min, max]
        :metric: Stability metric (settling_time, overshoot, ise, stability_margin)
        :grid-resolution: Grid resolution (default: 50x50)
        :title: Plot title
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    option_spec = {
        'param1': directives.unchanged_required,
        'param2': directives.unchanged_required,
        'range1': directives.unchanged_required,
        'range2': directives.unchanged_required,
        'metric': directives.unchanged,
        'grid-resolution': directives.positive_int,
        'title': directives.unchanged,
        'colorscale': directives.unchanged,
        'width': directives.unchanged,
        'height': directives.unchanged,
    }

    def run(self) -> List[nodes.Node]:
        """Process the stability-region directive."""

        param1 = self.options.get('param1', 'k1')
        param2 = self.options.get('param2', 'k2')
        range1 = self.options.get('range1', '[0, 100]')
        range2 = self.options.get('range2', '[0, 50]')
        metric = self.options.get('metric', 'settling_time')
        grid_resolution = self.options.get('grid-resolution', 50)
        title = self.options.get('title', f'Stability Map: {param1} vs {param2}')
        colorscale = self.options.get('colorscale', 'RdYlGn_r')
        width = self.options.get('width', '100%')
        height = self.options.get('height', '600px')

        # Generate unique ID
        plot_id = f"stability-region-{self.env.new_serialno('stability-region')}"

        # Build HTML
        html = self.generate_stability_html(
            plot_id=plot_id,
            param1=param1,
            param2=param2,
            range1=range1,
            range2=range2,
            metric=metric,
            grid_resolution=grid_resolution,
            title=title,
            colorscale=colorscale,
            width=width,
            height=height
        )

        return [nodes.raw('', html, format='html')]

    def generate_stability_html(self, plot_id: str, param1: str, param2: str,
                                range1: str, range2: str, metric: str,
                                grid_resolution: int, title: str,
                                colorscale: str, width: str, height: str) -> str:
        """Generate HTML for stability region visualization."""

        import html as html_module

        html_parts = []

        html_parts.append('<div class="mathviz-container mathviz-stability">')

        # Title
        html_parts.append(f'''
<div class="mathviz-header">
    <strong>🎯 {html_module.escape(title)}</strong>
    <span class="mathviz-badge">Stability Analysis</span>
</div>
        ''')

        # Plot container
        html_parts.append(f'''
<div id="{plot_id}"
     class="mathviz-plot"
     data-viz-type="stability-region"
     data-param1="{html_module.escape(param1)}"
     data-param2="{html_module.escape(param2)}"
     data-range1="{html_module.escape(range1)}"
     data-range2="{html_module.escape(range2)}"
     data-metric="{html_module.escape(metric)}"
     data-grid-resolution="{grid_resolution}"
     data-colorscale="{html_module.escape(colorscale)}"
     style="width:{width};height:{height};"></div>
        ''')

        # Controls
        html_parts.append(f'''
<div class="mathviz-controls">
    <label>Metric:
        <select onchange="MathViz.changeMetric(this)">
            <option value="settling_time" {"selected" if metric == "settling_time" else ""}>Settling Time</option>
            <option value="overshoot" {"selected" if metric == "overshoot" else ""}>Overshoot</option>
            <option value="ise" {"selected" if metric == "ise" else ""}>ISE (Integral Squared Error)</option>
            <option value="stability_margin" {"selected" if metric == "stability_margin" else ""}>Stability Margin</option>
        </select>
    </label>
    <button class="mathviz-btn" onclick="MathViz.exportPlot(this)">
        📥 Export
    </button>
</div>
        ''')

        # Info box
        html_parts.append(f'''
<div class="mathviz-info">
    <small>
        💡 <strong>Parameter Stability Map:</strong>
        Green regions = stable/good performance, Red regions = unstable/poor performance.
        Hover to see exact {html_module.escape(metric)} values at each parameter combination.
    </small>
</div>
        ''')

        html_parts.append('</div>')

        return '\n'.join(html_parts)


class SlidingSurfaceDirective(SphinxDirective):
    """
    Directive for SMC sliding surface visualization.

    Shows sliding surface, reaching trajectories, and boundary layer.
    Perfect for explaining SMC two-phase operation.

    Options:
        :surface-gains: Sliding surface coefficients [k1, k2, lambda1, lambda2]
        :reaching-law: Reaching law type (classical, super_twisting, adaptive)
        :boundary-layer: Boundary layer thickness epsilon
        :trajectories: Number of trajectories to show
        :title: Plot title
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    option_spec = {
        'surface-gains': directives.unchanged,
        'reaching-law': directives.unchanged,
        'boundary-layer': directives.unchanged,
        'trajectories': directives.positive_int,
        'title': directives.unchanged,
        'width': directives.unchanged,
        'height': directives.unchanged,
    }

    def run(self) -> List[nodes.Node]:
        """Process the sliding-surface directive."""

        surface_gains = self.options.get('surface-gains', '[10, 5, 8, 3]')
        reaching_law = self.options.get('reaching-law', 'classical')
        boundary_layer = self.options.get('boundary-layer', '0.1')
        trajectories = self.options.get('trajectories', 5)
        title = self.options.get('title', 'SMC Sliding Surface')
        width = self.options.get('width', '100%')
        height = self.options.get('height', '600px')

        # Generate unique ID
        plot_id = f"sliding-surface-{self.env.new_serialno('sliding-surface')}"

        # Build HTML
        html = self.generate_sliding_surface_html(
            plot_id=plot_id,
            surface_gains=surface_gains,
            reaching_law=reaching_law,
            boundary_layer=boundary_layer,
            trajectories=trajectories,
            title=title,
            width=width,
            height=height
        )

        return [nodes.raw('', html, format='html')]

    def generate_sliding_surface_html(self, plot_id: str, surface_gains: str,
                                      reaching_law: str, boundary_layer: str,
                                      trajectories: int, title: str,
                                      width: str, height: str) -> str:
        """Generate HTML for sliding surface visualization."""

        import html as html_module

        html_parts = []

        html_parts.append('<div class="mathviz-container mathviz-sliding-surface">')

        # Title
        html_parts.append(f'''
<div class="mathviz-header">
    <strong>📐 {html_module.escape(title)}</strong>
    <span class="mathviz-equation">s = k₁θ₁ + k₂θ̇₁ + λ₁θ₂ + λ₂θ̇₂ = 0</span>
</div>
        ''')

        # Plot container
        html_parts.append(f'''
<div id="{plot_id}"
     class="mathviz-plot"
     data-viz-type="sliding-surface"
     data-surface-gains="{html_module.escape(surface_gains)}"
     data-reaching-law="{html_module.escape(reaching_law)}"
     data-boundary-layer="{html_module.escape(boundary_layer)}"
     data-trajectories="{trajectories}"
     style="width:{width};height:{height};"></div>
        ''')

        # Interactive controls
        html_parts.append(f'''
<div class="mathviz-controls">
    <label>Boundary Layer ε:
        <input type="range" min="0.01" max="0.5" step="0.01" value="{boundary_layer}"
               onchange="MathViz.updateBoundaryLayer(this)">
        <span class="mathviz-value">{boundary_layer}</span>
    </label>
    <label>Reaching Law:
        <select onchange="MathViz.changeReachingLaw(this)">
            <option value="classical" {"selected" if reaching_law == "classical" else ""}>Classical (sign)</option>
            <option value="super_twisting" {"selected" if reaching_law == "super_twisting" else ""}>Super-Twisting</option>
            <option value="adaptive" {"selected" if reaching_law == "adaptive" else ""}>Adaptive</option>
        </select>
    </label>
</div>
        ''')

        # Info box
        html_parts.append(f'''
<div class="mathviz-info">
    <small>
        💡 <strong>SMC Two-Phase Operation:</strong>
        Trajectories start off-surface (red), reach surface (green line), then slide to equilibrium.
        Boundary layer (yellow band) prevents chattering: ε = {html_module.escape(boundary_layer)}.
    </small>
</div>
        ''')

        html_parts.append('</div>')

        return '\n'.join(html_parts)


class ControlSignalDirective(SphinxDirective):
    """
    Directive for control signal time-series analysis.

    Shows control effort over time, switching behavior, and chattering analysis.
    Useful for comparing different SMC variants.

    Options:
        :controller-type: Controller type (classical_smc, sta_smc, adaptive_smc)
        :scenario: Simulation scenario (step_response, disturbance_rejection)
        :time-window: Time window [t_start, t_end]
        :show-switching: Show switching function (true/false)
        :title: Plot title
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    option_spec = {
        'controller-type': directives.unchanged,
        'scenario': directives.unchanged,
        'time-window': directives.unchanged,
        'show-switching': directives.unchanged,
        'title': directives.unchanged,
        'width': directives.unchanged,
        'height': directives.unchanged,
    }

    def run(self) -> List[nodes.Node]:
        """Process the control-signal directive."""

        controller_type = self.options.get('controller-type', 'classical_smc')
        scenario = self.options.get('scenario', 'step_response')
        time_window = self.options.get('time-window', '[0, 5]')
        show_switching = self.options.get('show-switching', 'true').lower() == 'true'
        title = self.options.get('title', 'Control Signal Analysis')
        width = self.options.get('width', '100%')
        height = self.options.get('height', '500px')

        # Generate unique ID
        plot_id = f"control-signal-{self.env.new_serialno('control-signal')}"

        # Build HTML
        html = self.generate_control_signal_html(
            plot_id=plot_id,
            controller_type=controller_type,
            scenario=scenario,
            time_window=time_window,
            show_switching=show_switching,
            title=title,
            width=width,
            height=height
        )

        return [nodes.raw('', html, format='html')]

    def generate_control_signal_html(self, plot_id: str, controller_type: str,
                                     scenario: str, time_window: str,
                                     show_switching: bool, title: str,
                                     width: str, height: str) -> str:
        """Generate HTML for control signal visualization."""

        import html as html_module

        html_parts = []

        html_parts.append('<div class="mathviz-container mathviz-control-signal">')

        # Title
        html_parts.append(f'''
<div class="mathviz-header">
    <strong>⚡ {html_module.escape(title)}</strong>
    <span class="mathviz-badge">{html_module.escape(controller_type.replace('_', ' ').title())}</span>
</div>
        ''')

        # Plot container
        html_parts.append(f'''
<div id="{plot_id}"
     class="mathviz-plot"
     data-viz-type="control-signal"
     data-controller-type="{html_module.escape(controller_type)}"
     data-scenario="{html_module.escape(scenario)}"
     data-time-window="{html_module.escape(time_window)}"
     data-show-switching="{str(show_switching).lower()}"
     style="width:{width};height:{height};"></div>
        ''')

        # Controls
        html_parts.append(f'''
<div class="mathviz-controls">
    <label>Controller:
        <select onchange="MathViz.changeController(this)">
            <option value="classical_smc" {"selected" if controller_type == "classical_smc" else ""}>Classical SMC</option>
            <option value="sta_smc" {"selected" if controller_type == "sta_smc" else ""}>Super-Twisting</option>
            <option value="adaptive_smc" {"selected" if controller_type == "adaptive_smc" else ""}>Adaptive SMC</option>
            <option value="hybrid_smc" {"selected" if controller_type == "hybrid_smc" else ""}>Hybrid SMC</option>
        </select>
    </label>
    <label class="mathviz-toggle">
        <input type="checkbox" onchange="MathViz.toggleSwitching(this)" {"checked" if show_switching else ""}>
        Show Switching Function
    </label>
</div>
        ''')

        # Info box
        html_parts.append('''
<div class="mathviz-info">
    <small>
        💡 <strong>Control Effort Analysis:</strong>
        Classical SMC shows chattering (high-frequency switching).
        Super-Twisting provides smooth control. Compare RMS values and frequency content.
    </small>
</div>
        ''')

        html_parts.append('</div>')

        return '\n'.join(html_parts)


class ParameterSweepDirective(SphinxDirective):
    """
    Directive for multi-parameter sweep visualization.

    Shows performance metrics across parameter space with heatmaps and contours.
    Helps identify optimal parameter combinations.

    Options:
        :parameter-list: List of parameters to sweep
        :metric: Performance metric (settling_time, overshoot, ise, robustness)
        :sweep-range: Range for each parameter as nested list
        :optimal-mark: Mark optimal point (true/false)
        :title: Plot title
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    option_spec = {
        'parameter-list': directives.unchanged_required,
        'metric': directives.unchanged,
        'sweep-range': directives.unchanged,
        'optimal-mark': directives.unchanged,
        'title': directives.unchanged,
        'colorscale': directives.unchanged,
        'width': directives.unchanged,
        'height': directives.unchanged,
    }

    def run(self) -> List[nodes.Node]:
        """Process the parameter-sweep directive."""

        parameter_list = self.options.get('parameter-list', 'k1,k2')
        metric = self.options.get('metric', 'settling_time')
        sweep_range = self.options.get('sweep-range', '[[0,100],[0,50]]')
        optimal_mark = self.options.get('optimal-mark', 'true').lower() == 'true'
        title = self.options.get('title', 'Parameter Sweep Analysis')
        colorscale = self.options.get('colorscale', 'Viridis')
        width = self.options.get('width', '100%')
        height = self.options.get('height', '600px')

        # Generate unique ID
        plot_id = f"parameter-sweep-{self.env.new_serialno('parameter-sweep')}"

        # Build HTML
        html = self.generate_parameter_sweep_html(
            plot_id=plot_id,
            parameter_list=parameter_list,
            metric=metric,
            sweep_range=sweep_range,
            optimal_mark=optimal_mark,
            title=title,
            colorscale=colorscale,
            width=width,
            height=height
        )

        return [nodes.raw('', html, format='html')]

    def generate_parameter_sweep_html(self, plot_id: str, parameter_list: str,
                                      metric: str, sweep_range: str,
                                      optimal_mark: bool, title: str,
                                      colorscale: str, width: str, height: str) -> str:
        """Generate HTML for parameter sweep visualization."""

        import html as html_module

        html_parts = []

        html_parts.append('<div class="mathviz-container mathviz-parameter-sweep">')

        # Title
        html_parts.append(f'''
<div class="mathviz-header">
    <strong>🔬 {html_module.escape(title)}</strong>
    <span class="mathviz-badge">Parameter Optimization</span>
</div>
        ''')

        # Plot container
        html_parts.append(f'''
<div id="{plot_id}"
     class="mathviz-plot"
     data-viz-type="parameter-sweep"
     data-parameter-list="{html_module.escape(parameter_list)}"
     data-metric="{html_module.escape(metric)}"
     data-sweep-range="{html_module.escape(sweep_range)}"
     data-optimal-mark="{str(optimal_mark).lower()}"
     data-colorscale="{html_module.escape(colorscale)}"
     style="width:{width};height:{height};"></div>
        ''')

        # Controls
        html_parts.append('''
<div class="mathviz-controls">
    <label>Metric:
        <select onchange="MathViz.changeSweepMetric(this)">
            <option value="settling_time">Settling Time</option>
            <option value="overshoot">Overshoot %</option>
            <option value="ise">ISE (Integral Squared Error)</option>
            <option value="robustness">Robustness Score</option>
        </select>
    </label>
    <button class="mathviz-btn" onclick="MathViz.findOptimal(this)">
        🎯 Find Optimal
    </button>
    <button class="mathviz-btn" onclick="MathViz.exportPlot(this)">
        📥 Export
    </button>
</div>
        ''')

        # Info box
        html_parts.append(f'''
<div class="mathviz-info">
    <small>
        💡 <strong>Parameter Space Exploration:</strong>
        Darker blue = better {html_module.escape(metric)}. Optimal point marked with ⭐.
        Use for PSO initialization or manual gain tuning.
    </small>
</div>
        ''')

        html_parts.append('</div>')

        return '\n'.join(html_parts)


def add_mathviz_assets(app: Sphinx, pagename: str, templatename: str,
                       context: Dict[str, Any], doctree: nodes.Node) -> None:
    """Add mathematical visualization CSS styles to HTML pages."""

    if not hasattr(context, 'metatags'):
        context['metatags'] = ''

    # Add custom styles for math visualization elements
    mathviz_styles = '''
<style>
/* Mathematical Visualization Containers */
.mathviz-container {
    margin: 2.5em 0;
    background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    border: 1px solid rgba(99, 102, 241, 0.1);
}

/* Header styling */
.mathviz-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 14px 18px;
    background: white;
    border-radius: 10px;
    border-left: 5px solid #6366f1;
    font-size: 16px;
    color: #1e293b;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.mathviz-badge {
    padding: 5px 14px;
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
    color: white;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 0.5px;
}

.mathviz-equation {
    padding: 4px 12px;
    background: #f1f5f9;
    border-radius: 6px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    color: #4338ca;
    border: 1px solid #c7d2fe;
}

/* Plot container */
.mathviz-plot {
    background: white;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.03);
}

/* Controls styling */
.mathviz-controls {
    margin-top: 18px;
    padding: 16px;
    background: rgba(255, 255, 255, 0.7);
    border-radius: 10px;
    display: flex;
    gap: 16px;
    align-items: center;
    flex-wrap: wrap;
    backdrop-filter: blur(10px);
}

.mathviz-controls label {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 14px;
    font-weight: 500;
    color: #475569;
}

.mathviz-controls select,
.mathviz-controls input[type="range"] {
    padding: 6px 12px;
    border: 2px solid #cbd5e1;
    border-radius: 6px;
    font-size: 14px;
    background: white;
    transition: border-color 0.2s;
}

.mathviz-controls select:hover,
.mathviz-controls select:focus {
    border-color: #6366f1;
    outline: none;
}

.mathviz-controls input[type="range"] {
    width: 150px;
    height: 6px;
    border-radius: 3px;
    background: #cbd5e1;
    outline: none;
}

.mathviz-controls input[type="range"]::-webkit-slider-thumb {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #6366f1;
    cursor: pointer;
    box-shadow: 0 2px 6px rgba(99, 102, 241, 0.4);
}

.mathviz-value {
    min-width: 50px;
    padding: 4px 10px;
    background: #f1f5f9;
    border-radius: 4px;
    font-family: monospace;
    font-size: 13px;
    color: #4338ca;
}

.mathviz-btn {
    padding: 8px 18px;
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
}

.mathviz-btn:hover {
    background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
}

.mathviz-btn:active {
    transform: translateY(0);
}

.mathviz-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
}

.mathviz-toggle input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
}

/* Info box styling */
.mathviz-info {
    margin-top: 18px;
    padding: 14px 18px;
    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
    border-radius: 8px;
    border-left: 4px solid #3b82f6;
    font-size: 13px;
    line-height: 1.6;
    color: #1e40af;
}

.mathviz-info code {
    padding: 2px 6px;
    background: rgba(255, 255, 255, 0.7);
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    color: #4338ca;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .mathviz-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-color: rgba(139, 92, 246, 0.2);
    }

    .mathviz-header {
        background: #1e293b;
        color: #e2e8f0;
        border-left-color: #8b5cf6;
    }

    .mathviz-equation {
        background: #0f172a;
        color: #c4b5fd;
        border-color: #4c1d95;
    }

    .mathviz-plot {
        background: #1e293b;
        border-color: #334155;
    }

    .mathviz-controls {
        background: rgba(30, 41, 59, 0.7);
    }

    .mathviz-controls label {
        color: #cbd5e1;
    }

    .mathviz-controls select,
    .mathviz-value {
        background: #0f172a;
        border-color: #475569;
        color: #e2e8f0;
    }

    .mathviz-controls input[type="range"] {
        background: #475569;
    }

    .mathviz-info {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
        border-left-color: #60a5fa;
        color: #bfdbfe;
    }

    .mathviz-info code {
        background: rgba(15, 23, 42, 0.7);
        color: #c4b5fd;
    }
}

/* Responsive design */
@media (max-width: 768px) {
    .mathviz-container {
        padding: 16px;
        margin: 1.5em 0;
    }

    .mathviz-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }

    .mathviz-controls {
        flex-direction: column;
        align-items: stretch;
    }

    .mathviz-controls label {
        flex-direction: column;
        align-items: flex-start;
    }

    .mathviz-controls input[type="range"] {
        width: 100%;
    }
}
</style>
    '''

    context['metatags'] += mathviz_styles


def setup(app: Sphinx) -> Dict[str, Any]:
    """Setup the Mathematical Visualization extension."""

    # Register directives
    app.add_directive('phase-portrait', PhasePortraitDirective)
    app.add_directive('lyapunov-surface', LyapunovSurfaceDirective)
    app.add_directive('stability-region', StabilityRegionDirective)
    app.add_directive('sliding-surface', SlidingSurfaceDirective)
    app.add_directive('control-signal', ControlSignalDirective)
    app.add_directive('parameter-sweep', ParameterSweepDirective)

    # Add custom CSS to pages
    app.connect('html-page-context', add_mathviz_assets)

    return {
        'version': '1.0.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
