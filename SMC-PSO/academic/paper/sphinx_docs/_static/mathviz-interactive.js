/**
 * ═══════════════════════════════════════════════════════════════════════════
 * Mathematical Visualization Interactive Controller
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Provides interactive control theory visualizations using Plotly.js
 * Part of Phase 5 - Mathematical Visualization Library
 *
 * Dependencies: Plotly.js (loaded from Phase 3 infrastructure)
 *
 * Features:
 * - 6 directive types with real-time interactivity
 * - Parameter sliders with live updates
 * - 2D/3D plot rendering and controls
 * - Export functionality (PNG, SVG, JSON)
 * - Dark mode support
 * - Mobile responsive
 *
 * @version 1.0.0
 * @date 2025-10-13
 */

(function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════════
    // Global MathViz Object
    // ═══════════════════════════════════════════════════════════════════════

    window.MathViz = {
        // Plot instances cache
        plots: new Map(),

        // Configuration
        config: {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            toImageButtonOptions: {
                format: 'png',
                filename: 'mathviz_plot',
                height: 800,
                width: 1200,
                scale: 2
            }
        },

        // Dark mode detection
        isDarkMode() {
            return window.matchMedia &&
                   window.matchMedia('(prefers-color-scheme: dark)').matches;
        },

        // Get theme colors
        getThemeColors() {
            const dark = this.isDarkMode();
            return {
                background: dark ? '#1e1e1e' : '#ffffff',
                paper: dark ? '#2d2d2d' : '#f8f9fa',
                text: dark ? '#e0e0e0' : '#2c3e50',
                grid: dark ? '#404040' : '#e0e0e0',
                primary: '#3498db',
                secondary: '#e74c3c',
                success: '#2ecc71',
                warning: '#f39c12'
            };
        },

        // ═══════════════════════════════════════════════════════════════════
        // 1. Phase Portrait Directive
        // ═══════════════════════════════════════════════════════════════════

        initPhasePortrait(container) {
            const id = container.dataset.plotId;
            const system = container.dataset.system || 'classical_smc';
            const initialState = this.parseArray(container.dataset.initialState || '0.1, 0.0, 0.05, 0.0');
            const timeRange = this.parseArray(container.dataset.timeRange || '0, 10, 0.01');
            const vectorField = container.dataset.vectorField === 'true';

            this.renderPhasePortrait(id, system, initialState, timeRange, vectorField);
        },

        renderPhasePortrait(id, system, initialState, timeRange, vectorField) {
            const colors = this.getThemeColors();
            const [t0, tf, dt] = timeRange;
            const numPoints = Math.floor((tf - t0) / dt);

            // Simulate system dynamics
            const trajectory = this.simulateSystem(system, initialState, t0, tf, dt);

            // Create trajectory trace
            const traces = [{
                x: trajectory.x1,
                y: trajectory.x2,
                mode: 'lines',
                name: 'Trajectory',
                line: {
                    color: colors.primary,
                    width: 2
                },
                hovertemplate: 'θ₁: %{x:.3f}<br>θ̇₁: %{y:.3f}<extra></extra>'
            }];

            // Add initial point
            traces.push({
                x: [trajectory.x1[0]],
                y: [trajectory.x2[0]],
                mode: 'markers',
                name: 'Initial State',
                marker: {
                    color: colors.success,
                    size: 10,
                    symbol: 'circle'
                },
                hovertemplate: 'Start: (%{x:.3f}, %{y:.3f})<extra></extra>'
            });

            // Add final point
            traces.push({
                x: [trajectory.x1[trajectory.x1.length - 1]],
                y: [trajectory.x2[trajectory.x2.length - 1]],
                mode: 'markers',
                name: 'Final State',
                marker: {
                    color: colors.secondary,
                    size: 10,
                    symbol: 'square'
                },
                hovertemplate: 'End: (%{x:.3f}, %{y:.3f})<extra></extra>'
            });

            // Add vector field if requested
            if (vectorField) {
                const field = this.generateVectorField(system, -1, 1, -1, 1, 15);
                traces.push({
                    x: field.x,
                    y: field.y,
                    mode: 'markers',
                    marker: {
                        color: colors.grid,
                        size: 2,
                        symbol: 'arrow',
                        angleref: 'previous'
                    },
                    name: 'Vector Field',
                    hoverinfo: 'skip'
                });
            }

            const layout = {
                title: {
                    text: `Phase Portrait - ${this.getSystemName(system)}`,
                    font: { color: colors.text }
                },
                xaxis: {
                    title: 'θ₁ (rad)',
                    gridcolor: colors.grid,
                    color: colors.text,
                    zeroline: true,
                    zerolinecolor: colors.grid
                },
                yaxis: {
                    title: 'θ̇₁ (rad/s)',
                    gridcolor: colors.grid,
                    color: colors.text,
                    zeroline: true,
                    zerolinecolor: colors.grid
                },
                plot_bgcolor: colors.background,
                paper_bgcolor: colors.paper,
                showlegend: true,
                legend: {
                    font: { color: colors.text }
                },
                hovermode: 'closest'
            };

            Plotly.newPlot(id, traces, layout, this.config);
            this.plots.set(id, { type: 'phase-portrait', system, initialState, timeRange });
        },

        toggleVectorField(button) {
            const container = button.closest('.mathviz-phase-portrait');
            const id = container.dataset.plotId;
            const plotData = this.plots.get(id);

            if (plotData) {
                const hasField = button.textContent.includes('Hide');
                button.textContent = hasField ? 'Show Vector Field' : 'Hide Vector Field';
                this.renderPhasePortrait(
                    id,
                    plotData.system,
                    plotData.initialState,
                    plotData.timeRange,
                    !hasField
                );
            }
        },

        // ═══════════════════════════════════════════════════════════════════
        // 2. Lyapunov Surface Directive
        // ═══════════════════════════════════════════════════════════════════

        initLyapunovSurface(container) {
            const id = container.dataset.plotId;
            const func = container.dataset.function || 'quadratic';
            const trajectory = container.dataset.trajectory === 'true';
            const levelCurves = container.dataset.levelCurves === 'true';

            this.renderLyapunovSurface(id, func, trajectory, levelCurves);
        },

        renderLyapunovSurface(id, func, trajectory, levelCurves, projection = '3d') {
            const colors = this.getThemeColors();
            const range = [-2, 2];
            const resolution = 50;

            // Generate surface data
            const surface = this.generateLyapunovSurface(func, range, resolution);

            const traces = [];

            if (projection === '3d') {
                // 3D surface
                traces.push({
                    type: 'surface',
                    x: surface.x,
                    y: surface.y,
                    z: surface.z,
                    colorscale: 'Viridis',
                    name: 'V(x)',
                    hovertemplate: 'x₁: %{x:.2f}<br>x₂: %{y:.2f}<br>V: %{z:.2f}<extra></extra>'
                });

                // Add trajectory if requested
                if (trajectory) {
                    const traj = this.simulateSystem('classical_smc', [0.5, 0.3, 0.1, 0.0], 0, 5, 0.01);
                    const vTraj = traj.x1.map((x1, i) => this.evaluateLyapunov(func, x1, traj.x2[i]));

                    traces.push({
                        type: 'scatter3d',
                        x: traj.x1,
                        y: traj.x2,
                        z: vTraj,
                        mode: 'lines',
                        name: 'Trajectory',
                        line: {
                            color: colors.secondary,
                            width: 4
                        }
                    });
                }
            } else {
                // 2D contour plot
                traces.push({
                    type: 'contour',
                    x: surface.x[0],
                    y: surface.y.map(row => row[0]),
                    z: surface.z,
                    colorscale: 'Viridis',
                    name: 'V(x)',
                    contours: {
                        showlabels: true,
                        labelfont: { color: colors.text }
                    },
                    hovertemplate: 'x₁: %{x:.2f}<br>x₂: %{y:.2f}<br>V: %{z:.2f}<extra></extra>'
                });
            }

            const layout = {
                title: {
                    text: `Lyapunov Function - ${this.getLyapunovName(func)}`,
                    font: { color: colors.text }
                },
                scene: projection === '3d' ? {
                    xaxis: { title: 'x₁', gridcolor: colors.grid, color: colors.text },
                    yaxis: { title: 'x₂', gridcolor: colors.grid, color: colors.text },
                    zaxis: { title: 'V(x)', gridcolor: colors.grid, color: colors.text },
                    bgcolor: colors.background
                } : undefined,
                xaxis: projection === '2d' ? {
                    title: 'x₁',
                    gridcolor: colors.grid,
                    color: colors.text
                } : undefined,
                yaxis: projection === '2d' ? {
                    title: 'x₂',
                    gridcolor: colors.grid,
                    color: colors.text
                } : undefined,
                plot_bgcolor: colors.background,
                paper_bgcolor: colors.paper,
                showlegend: true,
                legend: { font: { color: colors.text } }
            };

            Plotly.newPlot(id, traces, layout, this.config);
            this.plots.set(id, { type: 'lyapunov-surface', func, trajectory, levelCurves });
        },

        rotate3D(button) {
            const container = button.closest('.mathviz-lyapunov-surface');
            const id = container.dataset.plotId;

            // Trigger auto-rotation animation
            const update = {
                'scene.camera.eye': { x: 1.5, y: 1.5, z: 1.5 }
            };
            Plotly.relayout(id, update);
        },

        toggleProjection(button) {
            const container = button.closest('.mathviz-lyapunov-surface');
            const id = container.dataset.plotId;
            const plotData = this.plots.get(id);

            if (plotData) {
                const is3D = button.textContent.includes('2D');
                button.textContent = is3D ? '3D View' : '2D Contour';
                this.renderLyapunovSurface(
                    id,
                    plotData.func,
                    plotData.trajectory,
                    plotData.levelCurves,
                    is3D ? '2d' : '3d'
                );
            }
        },

        toggleLevelCurves(button) {
            const container = button.closest('.mathviz-lyapunov-surface');
            const id = container.dataset.plotId;
            const plotData = this.plots.get(id);

            if (plotData) {
                plotData.levelCurves = !plotData.levelCurves;
                button.textContent = plotData.levelCurves ? 'Hide Level Curves' : 'Show Level Curves';
                this.renderLyapunovSurface(
                    id,
                    plotData.func,
                    plotData.trajectory,
                    plotData.levelCurves
                );
            }
        },

        // ═══════════════════════════════════════════════════════════════════
        // 3. Stability Region Directive
        // ═══════════════════════════════════════════════════════════════════

        initStabilityRegion(container) {
            const id = container.dataset.plotId;
            const param1 = container.dataset.param1 || 'K1';
            const param2 = container.dataset.param2 || 'K2';
            const range1 = this.parseArray(container.dataset.range1 || '0, 20, 40');
            const range2 = this.parseArray(container.dataset.range2 || '0, 10, 40');
            const metric = container.dataset.metric || 'settling-time';

            this.renderStabilityRegion(id, param1, param2, range1, range2, metric);
        },

        renderStabilityRegion(id, param1, param2, range1, range2, metric) {
            const colors = this.getThemeColors();
            const [min1, max1, res1] = range1;
            const [min2, max2, res2] = range2;

            // Generate parameter sweep data
            const heatmap = this.generateStabilityHeatmap(
                param1, param2, min1, max1, res1, min2, max2, res2, metric
            );

            const trace = {
                type: 'heatmap',
                x: heatmap.x,
                y: heatmap.y,
                z: heatmap.z,
                colorscale: 'RdYlGn',
                reversescale: metric === 'settling-time', // Lower is better
                colorbar: {
                    title: {
                        text: this.getMetricLabel(metric),
                        font: { color: colors.text }
                    },
                    tickfont: { color: colors.text }
                },
                hovertemplate: `${param1}: %{x:.2f}<br>${param2}: %{y:.2f}<br>${this.getMetricLabel(metric)}: %{z:.2f}<extra></extra>`
            };

            const layout = {
                title: {
                    text: `Stability Region - ${param1} vs ${param2}`,
                    font: { color: colors.text }
                },
                xaxis: {
                    title: param1,
                    gridcolor: colors.grid,
                    color: colors.text
                },
                yaxis: {
                    title: param2,
                    gridcolor: colors.grid,
                    color: colors.text
                },
                plot_bgcolor: colors.background,
                paper_bgcolor: colors.paper
            };

            Plotly.newPlot(id, [trace], layout, this.config);
            this.plots.set(id, { type: 'stability-region', param1, param2, range1, range2, metric });
        },

        changeMetric(select) {
            const container = select.closest('.mathviz-stability-region');
            const id = container.dataset.plotId;
            const plotData = this.plots.get(id);

            if (plotData) {
                plotData.metric = select.value;
                this.renderStabilityRegion(
                    id,
                    plotData.param1,
                    plotData.param2,
                    plotData.range1,
                    plotData.range2,
                    select.value
                );
            }
        },

        // ═══════════════════════════════════════════════════════════════════
        // 4. Sliding Surface Directive
        // ═══════════════════════════════════════════════════════════════════

        initSlidingSurface(container) {
            const id = container.dataset.plotId;
            const gains = this.parseArray(container.dataset.surfaceGains || '1.0, 1.0');
            const reachingLaw = container.dataset.reachingLaw || 'constant';
            const boundaryLayer = parseFloat(container.dataset.boundaryLayer || '0.1');

            this.renderSlidingSurface(id, gains, reachingLaw, boundaryLayer);
        },

        renderSlidingSurface(id, gains, reachingLaw, boundaryLayer) {
            const colors = this.getThemeColors();
            const [c1, c2] = gains;

            // Generate sliding surface s = c1*x1 + c2*x2 = 0
            const x1 = this.linspace(-2, 2, 100);
            const x2Surface = x1.map(x => -c1 / c2 * x);

            // Generate boundary layer
            const x2Upper = x1.map(x => -c1 / c2 * x + boundaryLayer);
            const x2Lower = x1.map(x => -c1 / c2 * x - boundaryLayer);

            // Simulate trajectory
            const traj = this.simulateSystem('classical_smc', [0.5, 0.3, 0.1, 0.0], 0, 5, 0.01);

            const traces = [
                {
                    x: x1,
                    y: x2Surface,
                    mode: 'lines',
                    name: 'Sliding Surface (s=0)',
                    line: { color: colors.primary, width: 3, dash: 'solid' }
                },
                {
                    x: x1,
                    y: x2Upper,
                    mode: 'lines',
                    name: 'Boundary Layer (upper)',
                    line: { color: colors.warning, width: 2, dash: 'dash' },
                    fill: 'tonexty',
                    fillcolor: 'rgba(243, 156, 18, 0.1)'
                },
                {
                    x: x1,
                    y: x2Lower,
                    mode: 'lines',
                    name: 'Boundary Layer (lower)',
                    line: { color: colors.warning, width: 2, dash: 'dash' }
                },
                {
                    x: traj.x1,
                    y: traj.x2,
                    mode: 'lines',
                    name: 'System Trajectory',
                    line: { color: colors.secondary, width: 2 }
                }
            ];

            const layout = {
                title: {
                    text: `Sliding Surface - ${this.getReachingLawName(reachingLaw)}`,
                    font: { color: colors.text }
                },
                xaxis: {
                    title: 'x₁ (error)',
                    gridcolor: colors.grid,
                    color: colors.text,
                    zeroline: true,
                    zerolinecolor: colors.grid
                },
                yaxis: {
                    title: 'x₂ (error rate)',
                    gridcolor: colors.grid,
                    color: colors.text,
                    zeroline: true,
                    zerolinecolor: colors.grid
                },
                plot_bgcolor: colors.background,
                paper_bgcolor: colors.paper,
                showlegend: true,
                legend: { font: { color: colors.text } }
            };

            Plotly.newPlot(id, traces, layout, this.config);
            this.plots.set(id, { type: 'sliding-surface', gains, reachingLaw, boundaryLayer });
        },

        updateBoundaryLayer(slider) {
            const container = slider.closest('.mathviz-sliding-surface');
            const id = container.dataset.plotId;
            const plotData = this.plots.get(id);
            const valueSpan = container.querySelector('.boundary-value');

            if (plotData && valueSpan) {
                valueSpan.textContent = slider.value;
                plotData.boundaryLayer = parseFloat(slider.value);
                this.renderSlidingSurface(
                    id,
                    plotData.gains,
                    plotData.reachingLaw,
                    parseFloat(slider.value)
                );
            }
        },

        changeReachingLaw(select) {
            const container = select.closest('.mathviz-sliding-surface');
            const id = container.dataset.plotId;
            const plotData = this.plots.get(id);

            if (plotData) {
                plotData.reachingLaw = select.value;
                this.renderSlidingSurface(
                    id,
                    plotData.gains,
                    select.value,
                    plotData.boundaryLayer
                );
            }
        },

        // ═══════════════════════════════════════════════════════════════════
        // 5. Control Signal Directive
        // ═══════════════════════════════════════════════════════════════════

        initControlSignal(container) {
            const id = container.dataset.plotId;
            const controllerType = container.dataset.controllerType || 'classical_smc';
            const scenario = container.dataset.scenario || 'stabilization';
            const timeWindow = this.parseArray(container.dataset.timeWindow || '0, 10, 0.01');

            this.renderControlSignal(id, controllerType, scenario, timeWindow);
        },

        renderControlSignal(id, controllerType, scenario, timeWindow) {
            const colors = this.getThemeColors();
            const [t0, tf, dt] = timeWindow;

            // Simulate control signal
            const simulation = this.simulateControlSignal(controllerType, scenario, t0, tf, dt);

            const traces = [
                {
                    x: simulation.time,
                    y: simulation.control,
                    mode: 'lines',
                    name: 'Control Signal u(t)',
                    line: { color: colors.primary, width: 2 }
                }
            ];

            // Add switching function if applicable
            if (controllerType.includes('smc')) {
                traces.push({
                    x: simulation.time,
                    y: simulation.switching,
                    mode: 'lines',
                    name: 'Switching Function s(t)',
                    line: { color: colors.secondary, width: 2 },
                    yaxis: 'y2'
                });
            }

            const layout = {
                title: {
                    text: `Control Signal - ${this.getControllerName(controllerType)}`,
                    font: { color: colors.text }
                },
                xaxis: {
                    title: 'Time (s)',
                    gridcolor: colors.grid,
                    color: colors.text
                },
                yaxis: {
                    title: 'Control u (N⋅m)',
                    gridcolor: colors.grid,
                    color: colors.text
                },
                yaxis2: controllerType.includes('smc') ? {
                    title: 'Switching s',
                    overlaying: 'y',
                    side: 'right',
                    color: colors.text
                } : undefined,
                plot_bgcolor: colors.background,
                paper_bgcolor: colors.paper,
                showlegend: true,
                legend: { font: { color: colors.text } }
            };

            Plotly.newPlot(id, traces, layout, this.config);
            this.plots.set(id, { type: 'control-signal', controllerType, scenario, timeWindow });
        },

        changeController(select) {
            const container = select.closest('.mathviz-control-signal');
            const id = container.dataset.plotId;
            const plotData = this.plots.get(id);

            if (plotData) {
                plotData.controllerType = select.value;
                this.renderControlSignal(
                    id,
                    select.value,
                    plotData.scenario,
                    plotData.timeWindow
                );
            }
        },

        toggleSwitching(button) {
            const container = button.closest('.mathviz-control-signal');
            const id = container.dataset.plotId;

            const plot = document.getElementById(id);
            if (plot && plot.data) {
                const visible = plot.data.length > 1 && plot.data[1].visible !== false;
                Plotly.restyle(id, { visible: !visible }, [1]);
                button.textContent = visible ? 'Show Switching' : 'Hide Switching';
            }
        },

        // ═══════════════════════════════════════════════════════════════════
        // 6. Parameter Sweep Directive
        // ═══════════════════════════════════════════════════════════════════

        initParameterSweep(container) {
            const id = container.dataset.plotId;
            const paramList = container.dataset.parameterList || 'K1,K2,K3';
            const metric = container.dataset.metric || 'settling-time';
            const sweepRange = this.parseArray(container.dataset.sweepRange || '0, 20, 20');

            this.renderParameterSweep(id, paramList.split(','), metric, sweepRange);
        },

        renderParameterSweep(id, paramList, metric, sweepRange) {
            const colors = this.getThemeColors();
            const [min, max, resolution] = sweepRange;

            // Generate multi-parameter sweep
            const sweep = this.generateParameterSweep(paramList, metric, min, max, resolution);

            const traces = paramList.map((param, idx) => ({
                x: sweep.values,
                y: sweep.metrics[idx],
                mode: 'lines+markers',
                name: param,
                line: { width: 2 },
                marker: { size: 6 }
            }));

            const layout = {
                title: {
                    text: `Parameter Sweep - ${this.getMetricLabel(metric)}`,
                    font: { color: colors.text }
                },
                xaxis: {
                    title: 'Parameter Value',
                    gridcolor: colors.grid,
                    color: colors.text
                },
                yaxis: {
                    title: this.getMetricLabel(metric),
                    gridcolor: colors.grid,
                    color: colors.text
                },
                plot_bgcolor: colors.background,
                paper_bgcolor: colors.paper,
                showlegend: true,
                legend: { font: { color: colors.text } },
                hovermode: 'x unified'
            };

            Plotly.newPlot(id, traces, layout, this.config);
            this.plots.set(id, { type: 'parameter-sweep', paramList, metric, sweepRange });
        },

        changeSweepMetric(select) {
            const container = select.closest('.mathviz-parameter-sweep');
            const id = container.dataset.plotId;
            const plotData = this.plots.get(id);

            if (plotData) {
                plotData.metric = select.value;
                this.renderParameterSweep(
                    id,
                    plotData.paramList,
                    select.value,
                    plotData.sweepRange
                );
            }
        },

        findOptimal(button) {
            const container = button.closest('.mathviz-parameter-sweep');
            const id = container.dataset.plotId;
            const plotData = this.plots.get(id);

            if (plotData) {
                const sweep = this.generateParameterSweep(
                    plotData.paramList,
                    plotData.metric,
                    ...plotData.sweepRange
                );

                // Find optimal for each parameter
                const optimal = sweep.metrics.map((metricArray, idx) => {
                    const minIdx = metricArray.indexOf(Math.min(...metricArray));
                    return {
                        param: plotData.paramList[idx],
                        value: sweep.values[minIdx],
                        metric: metricArray[minIdx]
                    };
                });

                // Display optimal values
                const msg = optimal.map(o =>
                    `${o.param}: ${o.value.toFixed(2)} (${this.getMetricLabel(plotData.metric)}: ${o.metric.toFixed(3)})`
                ).join('\n');

                alert(`Optimal Parameters:\n\n${msg}`);
            }
        },

        // ═══════════════════════════════════════════════════════════════════
        // Common Functions
        // ═══════════════════════════════════════════════════════════════════

        resetView(button) {
            const container = button.closest('[class*="mathviz-"]');
            const id = container.dataset.plotId;
            Plotly.relayout(id, {
                'xaxis.autorange': true,
                'yaxis.autorange': true,
                'scene.camera.eye': { x: 1.25, y: 1.25, z: 1.25 }
            });
        },

        exportPlot(button, format = 'png') {
            const container = button.closest('[class*="mathviz-"]');
            const id = container.dataset.plotId;
            const plotData = this.plots.get(id);

            if (format === 'json' && plotData) {
                const dataStr = JSON.stringify(plotData, null, 2);
                const blob = new Blob([dataStr], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `mathviz_${plotData.type}_${Date.now()}.json`;
                a.click();
                URL.revokeObjectURL(url);
            } else {
                Plotly.downloadImage(id, {
                    format: format,
                    width: 1200,
                    height: 800,
                    filename: `mathviz_${id}_${Date.now()}`
                });
            }
        },

        // ═══════════════════════════════════════════════════════════════════
        // Simulation & Computation Utilities
        // ═══════════════════════════════════════════════════════════════════

        simulateSystem(system, initialState, t0, tf, dt) {
            const numPoints = Math.floor((tf - t0) / dt);
            const [x10, x20, x30, x40] = initialState;

            const trajectory = {
                time: new Array(numPoints),
                x1: new Array(numPoints),
                x2: new Array(numPoints),
                x3: new Array(numPoints),
                x4: new Array(numPoints)
            };

            // Simple Euler integration for demonstration
            let x1 = x10, x2 = x20, x3 = x30, x4 = x40;

            for (let i = 0; i < numPoints; i++) {
                const t = t0 + i * dt;
                trajectory.time[i] = t;
                trajectory.x1[i] = x1;
                trajectory.x2[i] = x2;
                trajectory.x3[i] = x3;
                trajectory.x4[i] = x4;

                // Simplified double pendulum dynamics with control
                const [dx1, dx2, dx3, dx4] = this.getDerivatives(system, [x1, x2, x3, x4], t);
                x1 += dx1 * dt;
                x2 += dx2 * dt;
                x3 += dx3 * dt;
                x4 += dx4 * dt;
            }

            return trajectory;
        },

        getDerivatives(system, state, t) {
            const [x1, x2, x3, x4] = state;
            const g = 9.81, m1 = 0.5, m2 = 0.5, l1 = 0.5, l2 = 0.5;

            // Simplified dynamics: ẍ = -ω²sin(x) - bẋ + u/m
            const omega1 = Math.sqrt(g / l1);
            const omega2 = Math.sqrt(g / l2);
            const damping = 0.1;

            // Simple SMC control law
            const s1 = x1 + 0.5 * x2;
            const s2 = x3 + 0.5 * x4;
            const u1 = -10 * Math.sign(s1);
            const u2 = -10 * Math.sign(s2);

            const dx1 = x2;
            const dx2 = -omega1 * omega1 * Math.sin(x1) - damping * x2 + u1 / m1;
            const dx3 = x4;
            const dx4 = -omega2 * omega2 * Math.sin(x3) - damping * x4 + u2 / m2;

            return [dx1, dx2, dx3, dx4];
        },

        generateVectorField(system, x1Min, x1Max, x2Min, x2Max, gridSize) {
            const field = { x: [], y: [], u: [], v: [] };
            const dx1 = (x1Max - x1Min) / gridSize;
            const dx2 = (x2Max - x2Min) / gridSize;

            for (let i = 0; i <= gridSize; i++) {
                for (let j = 0; j <= gridSize; j++) {
                    const x1 = x1Min + i * dx1;
                    const x2 = x2Min + j * dx2;
                    const [v1, v2] = this.getDerivatives(system, [x1, x2, 0, 0], 0);

                    field.x.push(x1);
                    field.y.push(x2);
                    field.u.push(v1);
                    field.v.push(v2);
                }
            }

            return field;
        },

        generateLyapunovSurface(func, range, resolution) {
            const [min, max] = range;
            const x = this.linspace(min, max, resolution);
            const y = this.linspace(min, max, resolution);
            const z = new Array(resolution).fill(0).map(() => new Array(resolution));

            for (let i = 0; i < resolution; i++) {
                for (let j = 0; j < resolution; j++) {
                    z[i][j] = this.evaluateLyapunov(func, x[j], y[i]);
                }
            }

            return { x: x.map(() => x), y: y.map(val => new Array(resolution).fill(val)), z };
        },

        evaluateLyapunov(func, x1, x2) {
            switch (func) {
                case 'quadratic':
                    return x1 * x1 + x2 * x2;
                case 'weighted':
                    return 2 * x1 * x1 + x2 * x2;
                case 'cross-term':
                    return x1 * x1 + x2 * x2 + 0.5 * x1 * x2;
                default:
                    return x1 * x1 + x2 * x2;
            }
        },

        generateStabilityHeatmap(param1, param2, min1, max1, res1, min2, max2, res2, metric) {
            const x = this.linspace(min1, max1, res1);
            const y = this.linspace(min2, max2, res2);
            const z = new Array(res2).fill(0).map(() => new Array(res1));

            for (let i = 0; i < res2; i++) {
                for (let j = 0; j < res1; j++) {
                    const gains = { [param1]: x[j], [param2]: y[i] };
                    z[i][j] = this.evaluateMetric(metric, gains);
                }
            }

            return { x, y, z };
        },

        generateParameterSweep(paramList, metric, min, max, resolution) {
            const values = this.linspace(min, max, resolution);
            const metrics = paramList.map(param =>
                values.map(val => {
                    const gains = { [param]: val };
                    return this.evaluateMetric(metric, gains);
                })
            );

            return { values, metrics };
        },

        evaluateMetric(metric, gains) {
            // Simplified metric evaluation for demonstration
            const baseline = 2.0;
            const gainEffect = Object.values(gains).reduce((sum, g) => sum + Math.abs(g - 10), 0);

            switch (metric) {
                case 'settling-time':
                    return baseline + 0.1 * gainEffect;
                case 'overshoot':
                    return 5 + 0.5 * gainEffect;
                case 'steady-state-error':
                    return 0.01 + 0.001 * gainEffect;
                case 'control-effort':
                    return 10 + gainEffect;
                default:
                    return baseline;
            }
        },

        simulateControlSignal(controllerType, scenario, t0, tf, dt) {
            const numPoints = Math.floor((tf - t0) / dt);
            const time = new Array(numPoints);
            const control = new Array(numPoints);
            const switching = new Array(numPoints);

            for (let i = 0; i < numPoints; i++) {
                const t = t0 + i * dt;
                time[i] = t;

                // Simplified control signal
                const s = Math.sin(2 * Math.PI * 0.5 * t) * Math.exp(-0.3 * t);
                switching[i] = s;

                if (controllerType === 'classical_smc') {
                    control[i] = -10 * Math.sign(s);
                } else if (controllerType === 'sta_smc') {
                    control[i] = -10 * Math.sign(s) - 5 * Math.pow(Math.abs(s), 0.5) * Math.sign(s);
                } else {
                    control[i] = -10 * s; // Adaptive
                }
            }

            return { time, control, switching };
        },

        // ═══════════════════════════════════════════════════════════════════
        // Helper Functions
        // ═══════════════════════════════════════════════════════════════════

        linspace(start, end, num) {
            const step = (end - start) / (num - 1);
            return Array.from({ length: num }, (_, i) => start + i * step);
        },

        parseArray(str) {
            return str.split(',').map(s => parseFloat(s.trim()));
        },

        getSystemName(system) {
            const names = {
                'classical_smc': 'Classical SMC',
                'sta_smc': 'Super-Twisting SMC',
                'adaptive_smc': 'Adaptive SMC',
                'hybrid_smc': 'Hybrid Adaptive STA-SMC'
            };
            return names[system] || system;
        },

        getControllerName(controller) {
            return this.getSystemName(controller);
        },

        getLyapunovName(func) {
            const names = {
                'quadratic': 'V(x) = x₁² + x₂²',
                'weighted': 'V(x) = 2x₁² + x₂²',
                'cross-term': 'V(x) = x₁² + x₂² + 0.5x₁x₂'
            };
            return names[func] || func;
        },

        getReachingLawName(law) {
            const names = {
                'constant': 'Constant Reaching Law',
                'exponential': 'Exponential Reaching Law',
                'power': 'Power Reaching Law'
            };
            return names[law] || law;
        },

        getMetricLabel(metric) {
            const labels = {
                'settling-time': 'Settling Time (s)',
                'overshoot': 'Overshoot (%)',
                'steady-state-error': 'Steady-State Error',
                'control-effort': 'Control Effort (J)'
            };
            return labels[metric] || metric;
        }
    };

    // ═══════════════════════════════════════════════════════════════════════
    // Initialization on DOM Ready
    // ═══════════════════════════════════════════════════════════════════════

    function initializeMathViz() {
        // Initialize all directive types
        document.querySelectorAll('.mathviz-phase-portrait').forEach(container => {
            MathViz.initPhasePortrait(container);
        });

        document.querySelectorAll('.mathviz-lyapunov-surface').forEach(container => {
            MathViz.initLyapunovSurface(container);
        });

        document.querySelectorAll('.mathviz-stability-region').forEach(container => {
            MathViz.initStabilityRegion(container);
        });

        document.querySelectorAll('.mathviz-sliding-surface').forEach(container => {
            MathViz.initSlidingSurface(container);
        });

        document.querySelectorAll('.mathviz-control-signal').forEach(container => {
            MathViz.initControlSignal(container);
        });

        document.querySelectorAll('.mathviz-parameter-sweep').forEach(container => {
            MathViz.initParameterSweep(container);
        });

        // Handle dark mode changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
                // Reinitialize all plots with new theme
                MathViz.plots.forEach((plotData, id) => {
                    const container = document.getElementById(id).closest('[class*="mathviz-"]');
                    if (container) {
                        // Re-render based on type
                        switch (plotData.type) {
                            case 'phase-portrait':
                                MathViz.renderPhasePortrait(id, plotData.system, plotData.initialState, plotData.timeRange, false);
                                break;
                            case 'lyapunov-surface':
                                MathViz.renderLyapunovSurface(id, plotData.func, plotData.trajectory, plotData.levelCurves);
                                break;
                            case 'stability-region':
                                MathViz.renderStabilityRegion(id, plotData.param1, plotData.param2, plotData.range1, plotData.range2, plotData.metric);
                                break;
                            case 'sliding-surface':
                                MathViz.renderSlidingSurface(id, plotData.gains, plotData.reachingLaw, plotData.boundaryLayer);
                                break;
                            case 'control-signal':
                                MathViz.renderControlSignal(id, plotData.controllerType, plotData.scenario, plotData.timeWindow);
                                break;
                            case 'parameter-sweep':
                                MathViz.renderParameterSweep(id, plotData.paramList, plotData.metric, plotData.sweepRange);
                                break;
                        }
                    }
                });
            });
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeMathViz);
    } else {
        initializeMathViz();
    }

})();
