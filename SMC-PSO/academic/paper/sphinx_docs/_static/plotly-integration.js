/**
 * Plotly Integration for Sphinx Documentation
 *
 * Handles rendering of interactive Plotly charts from Sphinx directive data.
 * Supports: plotly-chart, plotly-comparison, plotly-convergence, plotly-scatter-matrix
 *
 * @version 1.0.0
 * @requires Plotly.js v2.27.0+
 */

(function() {
    'use strict';

    // Global namespace
    window.PlotlyIntegration = window.PlotlyIntegration || {};

    /**
     * Initialize all Plotly charts on page load
     */
    function initializePlotlyCharts() {
        console.log('[Plotly] Initializing charts...');

        // Wait for Plotly to load
        if (typeof Plotly === 'undefined') {
            console.warn('[Plotly] Plotly.js not loaded yet, retrying...');
            setTimeout(initializePlotlyCharts, 100);
            return;
        }

        // Initialize different chart types
        initializeBasicCharts();
        initializeComparisonCharts();
        initializeConvergenceCharts();
        initializeScatterMatrixCharts();

        console.log('[Plotly] All charts initialized');
    }

    /**
     * Initialize basic plotly-chart directives
     */
    function initializeBasicCharts() {
        const charts = document.querySelectorAll('.plotly-chart');

        charts.forEach((chartDiv) => {
            try {
                renderBasicChart(chartDiv);
            } catch (error) {
                console.error('[Plotly] Error rendering chart:', error);
                chartDiv.innerHTML = `<div style="color:red;padding:20px;">Error rendering chart: ${error.message}</div>`;
            }
        });
    }

    /**
     * Render a basic Plotly chart
     */
    function renderBasicChart(chartDiv) {
        const chartType = chartDiv.dataset.chartType || 'line';
        const dataSource = chartDiv.dataset.chartData || '{}';
        const dataType = chartDiv.dataset.dataType || 'inline';
        const title = chartDiv.dataset.title || '';
        const xAxis = chartDiv.dataset.xAxis || '';
        const yAxis = chartDiv.dataset.yAxis || '';

        // Parse data
        let data, layout;

        if (dataType === 'inline') {
            // Parse inline JSON
            const chartData = JSON.parse(dataSource);
            ({data, layout} = prepareChartData(chartData, chartType, title, xAxis, yAxis));
        } else if (dataType === 'file') {
            // Load from file (async)
            loadDataFromFile(dataSource).then(chartData => {
                ({data, layout} = prepareChartData(chartData, chartType, title, xAxis, yAxis));
                Plotly.newPlot(chartDiv, data, layout, getPlotlyConfig());
            });
            return; // Exit early, will render after data loads
        }

        // Render chart
        Plotly.newPlot(chartDiv, data, layout, getPlotlyConfig());

        // Handle responsive resize
        window.addEventListener('resize', () => {
            Plotly.Plots.resize(chartDiv);
        });
    }

    /**
     * Prepare chart data and layout based on chart type
     */
    function prepareChartData(chartData, chartType, title, xAxis, yAxis) {
        let data = [];
        let layout = {
            title: title,
            xaxis: { title: xAxis },
            yaxis: { title: yAxis },
            hovermode: 'closest',
            showlegend: true,
        };

        switch (chartType) {
            case 'line':
                data = prepareLineChart(chartData);
                break;
            case 'scatter':
                data = prepareScatterChart(chartData);
                break;
            case 'bar':
                data = prepareBarChart(chartData);
                break;
            case 'box':
                data = prepareBoxChart(chartData);
                break;
            case 'heatmap':
                data = prepareHeatmapChart(chartData);
                break;
            case 'radar':
                data = prepareRadarChart(chartData);
                break;
            default:
                console.warn(`[Plotly] Unknown chart type: ${chartType}, using line`);
                data = prepareLineChart(chartData);
        }

        return { data, layout };
    }

    /**
     * Prepare line chart data
     */
    function prepareLineChart(chartData) {
        if (Array.isArray(chartData)) {
            // Array of traces
            return chartData.map(trace => ({
                x: trace.x || [],
                y: trace.y || [],
                mode: 'lines+markers',
                name: trace.name || '',
                type: 'scatter',
            }));
        } else {
            // Single trace
            return [{
                x: chartData.x || [],
                y: chartData.y || [],
                mode: 'lines+markers',
                type: 'scatter',
            }];
        }
    }

    /**
     * Prepare scatter chart data
     */
    function prepareScatterChart(chartData) {
        return [{
            x: chartData.x || [],
            y: chartData.y || [],
            mode: 'markers',
            type: 'scatter',
            marker: {
                size: 8,
                color: chartData.color || [],
                colorscale: 'Viridis',
                showscale: true,
            }
        }];
    }

    /**
     * Prepare bar chart data
     */
    function prepareBarChart(chartData) {
        if (Array.isArray(chartData)) {
            return chartData.map(trace => ({
                x: trace.x || [],
                y: trace.y || [],
                name: trace.name || '',
                type: 'bar',
            }));
        } else {
            return [{
                x: chartData.x || [],
                y: chartData.y || [],
                type: 'bar',
            }];
        }
    }

    /**
     * Prepare box plot data
     */
    function prepareBoxChart(chartData) {
        return chartData.map(trace => ({
            y: trace.y || [],
            name: trace.name || '',
            type: 'box',
        }));
    }

    /**
     * Prepare heatmap data
     */
    function prepareHeatmapChart(chartData) {
        return [{
            z: chartData.z || [],
            x: chartData.x || [],
            y: chartData.y || [],
            type: 'heatmap',
            colorscale: 'Viridis',
        }];
    }

    /**
     * Prepare radar chart data
     */
    function prepareRadarChart(chartData) {
        return [{
            type: 'scatterpolar',
            r: chartData.r || [],
            theta: chartData.theta || [],
            fill: 'toself',
        }];
    }

    /**
     * Initialize controller comparison charts
     */
    function initializeComparisonCharts() {
        const comparisons = document.querySelectorAll('.plotly-comparison');

        comparisons.forEach((comparisonDiv) => {
            try {
                renderComparisonChart(comparisonDiv);
            } catch (error) {
                console.error('[Plotly] Error rendering comparison:', error);
                comparisonDiv.innerHTML = `<div style="color:red;padding:20px;">Error rendering comparison: ${error.message}</div>`;
            }
        });
    }

    /**
     * Render controller comparison chart
     */
    function renderComparisonChart(comparisonDiv) {
        const controllers = JSON.parse(comparisonDiv.dataset.controllers || '[]');
        const metrics = JSON.parse(comparisonDiv.dataset.metrics || '[]');
        const dataDir = comparisonDiv.dataset.dataDir || 'results/';
        const layout = comparisonDiv.dataset.layout || '2x2';
        const normalize = comparisonDiv.dataset.normalize === 'true';

        // Create simple bar chart comparing metrics
        const data = metrics.map(metric => ({
            x: controllers,
            y: controllers.map((_, i) => Math.random() * 10), // Placeholder data
            name: metric,
            type: 'bar',
        }));

        const plotLayout = {
            title: 'Controller Performance Comparison',
            barmode: 'group',
            xaxis: { title: 'Controller' },
            yaxis: { title: 'Performance Metric' },
        };

        Plotly.newPlot(comparisonDiv, data, plotLayout, getPlotlyConfig());
    }

    /**
     * Initialize PSO convergence animation charts
     */
    function initializeConvergenceCharts() {
        const convergenceCharts = document.querySelectorAll('.plotly-convergence');

        convergenceCharts.forEach((chartDiv) => {
            try {
                renderConvergenceChart(chartDiv);
            } catch (error) {
                console.error('[Plotly] Error rendering convergence:', error);
                chartDiv.innerHTML = `<div style="color:red;padding:20px;">Error rendering convergence: ${error.message}</div>`;
            }
        });
    }

    /**
     * Render PSO convergence animation
     */
    function renderConvergenceChart(chartDiv) {
        const psoLog = chartDiv.dataset.psoLog || '';

        // Placeholder convergence curve
        const iterations = Array.from({length: 100}, (_, i) => i);
        const costs = iterations.map(i => Math.exp(-i/20) + Math.random() * 0.1);

        const data = [{
            x: iterations,
            y: costs,
            mode: 'lines+markers',
            name: 'Best Cost',
            line: { color: '#2196F3', width: 2 },
        }];

        const layout = {
            title: 'PSO Convergence',
            xaxis: { title: 'Iteration' },
            yaxis: { title: 'Cost', type: 'log' },
        };

        Plotly.newPlot(chartDiv, data, layout, getPlotlyConfig());
    }

    /**
     * Initialize scatter matrix charts
     */
    function initializeScatterMatrixCharts() {
        const scatterMatrices = document.querySelectorAll('.plotly-scatter-matrix');

        scatterMatrices.forEach((chartDiv) => {
            try {
                renderScatterMatrix(chartDiv);
            } catch (error) {
                console.error('[Plotly] Error rendering scatter matrix:', error);
                chartDiv.innerHTML = `<div style="color:red;padding:20px;">Error rendering scatter matrix: ${error.message}</div>`;
            }
        });
    }

    /**
     * Render scatter matrix
     */
    function renderScatterMatrix(chartDiv) {
        const parameters = JSON.parse(chartDiv.dataset.parameters || '[]');

        // Placeholder scatter matrix (would load real data from file)
        const trace = {
            type: 'splom',
            dimensions: parameters.map(param => ({
                label: param,
                values: Array.from({length: 100}, () => Math.random()),
            })),
            marker: {
                color: Array.from({length: 100}, () => Math.random()),
                colorscale: 'Viridis',
                showscale: true,
            }
        };

        const layout = {
            title: 'Parameter Space Exploration',
            height: 700,
        };

        Plotly.newPlot(chartDiv, [trace], layout, getPlotlyConfig());
    }

    /**
     * Load data from external file
     */
    async function loadDataFromFile(filepath) {
        try {
            const response = await fetch(filepath);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`[Plotly] Error loading file ${filepath}:`, error);
            return {};
        }
    }

    /**
     * Get default Plotly configuration
     */
    function getPlotlyConfig() {
        return {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            toImageButtonOptions: {
                format: 'png',
                filename: 'plotly_chart',
                height: 800,
                width: 1200,
                scale: 2,
            },
        };
    }

    /**
     * Public API methods
     */
    PlotlyIntegration.exportAllCharts = function(button) {
        console.log('[Plotly] Exporting all charts...');
        // Implementation would export all visible charts
    };

    PlotlyIntegration.resetAllZoom = function(button) {
        console.log('[Plotly] Resetting all zoom...');
        const charts = document.querySelectorAll('.plotly-chart, .plotly-comparison, .plotly-convergence');
        charts.forEach(chart => {
            Plotly.relayout(chart, {
                'xaxis.autorange': true,
                'yaxis.autorange': true,
            });
        });
    };

    PlotlyIntegration.playAnimation = function(button) {
        console.log('[Plotly] Playing animation...');
        button.disabled = true;
        button.nextElementSibling.disabled = false; // Enable pause button
    };

    PlotlyIntegration.pauseAnimation = function(button) {
        console.log('[Plotly] Pausing animation...');
        button.disabled = true;
        button.previousElementSibling.disabled = false; // Enable play button
    };

    PlotlyIntegration.resetAnimation = function(button) {
        console.log('[Plotly] Resetting animation...');
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializePlotlyCharts);
    } else {
        initializePlotlyCharts();
    }

})();
