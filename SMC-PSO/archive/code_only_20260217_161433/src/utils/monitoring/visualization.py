#======================================================================================\
#=================== src/utils/monitoring/visualization.py ===================\
#======================================================================================\

"""
Visualization and export utilities for performance monitoring.

Provides standardized plotting functions, export capabilities, and
custom color schemes for control system performance visualization.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import Dict, List, Optional, Any, Tuple
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from pathlib import Path
import json
import csv

from .data_model import DashboardData, PerformanceSummary, ComparisonData


# Color schemes
CONTROLLER_COLORS = {
    'classical_smc': '#1f77b4',      # Blue
    'sta_smc': '#ff7f0e',            # Orange
    'adaptive_smc': '#2ca02c',       # Green
    'hybrid_adaptive_sta_smc': '#d62728',  # Red
    'swing_up_smc': '#9467bd',       # Purple
    'mpc_controller': '#8c564b',     # Brown
    'pid_controller': '#e377c2'      # Pink
}

METRIC_COLORS = {
    'angle': '#1f77b4',
    'velocity': '#ff7f0e',
    'control': '#d62728',
    'error': '#2ca02c',
    'chattering': '#9467bd'
}


class PerformanceVisualizer:
    """
    Standardized visualization for control system performance.

    Provides matplotlib and plotly plotting functions with consistent
    styling and layouts.
    """

    def __init__(self, style: str = 'seaborn-v0_8-darkgrid'):
        """
        Initialize visualizer.

        Args:
            style: Matplotlib style to use
        """
        self.style = style
        try:
            plt.style.use(style)
        except:
            # Fallback to default if style not available
            pass

    def plot_time_series(self,
                        run_data: DashboardData,
                        metrics: Optional[List[str]] = None,
                        save_path: Optional[str] = None) -> Figure:
        """
        Plot time series for multiple metrics.

        Args:
            run_data: Dashboard data for the run
            metrics: List of metrics to plot (default: all)
            save_path: Optional path to save figure

        Returns:
            Matplotlib figure
        """
        if metrics is None:
            metrics = ['angle1', 'angle2', 'velocity1', 'velocity2', 'control', 'error_norm']

        n_metrics = len(metrics)
        fig, axes = plt.subplots(n_metrics, 1, figsize=(12, 2.5 * n_metrics), sharex=True)

        if n_metrics == 1:
            axes = [axes]

        for i, metric in enumerate(metrics):
            t, values = run_data.get_time_series(metric)

            axes[i].plot(t, values, color=METRIC_COLORS.get(metric.split('_')[0], '#1f77b4'), linewidth=1.5)
            axes[i].set_ylabel(self._get_metric_label(metric))
            axes[i].grid(True, alpha=0.3)

            # Add settling threshold for error
            if metric == 'error_norm':
                axes[i].axhline(y=0.02, color='red', linestyle='--', alpha=0.5, label='Settling Threshold')
                axes[i].legend()

        axes[-1].set_xlabel('Time (s)')
        fig.suptitle(f'Time Series - {run_data.controller} ({run_data.scenario})', fontsize=14, fontweight='bold')
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig

    def plot_performance_summary(self,
                                run_data: DashboardData,
                                save_path: Optional[str] = None) -> Figure:
        """
        Create multi-panel performance summary plot.

        Args:
            run_data: Dashboard data for the run
            save_path: Optional path to save figure

        Returns:
            Matplotlib figure
        """
        if run_data.summary is None:
            raise ValueError("Run must have summary data")

        fig = plt.figure(figsize=(16, 10))
        gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

        # 1. State trajectories
        ax1 = fig.add_subplot(gs[0, :2])
        t, angle1 = run_data.get_time_series('angle1')
        _, angle2 = run_data.get_time_series('angle2')
        ax1.plot(t, np.rad2deg(angle1), label='Theta 1', color=METRIC_COLORS['angle'])
        ax1.plot(t, np.rad2deg(angle2), label='Theta 2', color=METRIC_COLORS['velocity'])
        ax1.set_ylabel('Angle (deg)')
        ax1.set_xlabel('Time (s)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_title('State Trajectories')

        # 2. Control signal
        ax2 = fig.add_subplot(gs[1, :2])
        _, control = run_data.get_time_series('control')
        ax2.plot(t, control, color=METRIC_COLORS['control'], linewidth=1.5)
        ax2.set_ylabel('Control (N)')
        ax2.set_xlabel('Time (s)')
        ax2.grid(True, alpha=0.3)
        ax2.set_title('Control Signal')

        # 3. Error norm
        ax3 = fig.add_subplot(gs[2, :2])
        _, error = run_data.get_time_series('error_norm')
        ax3.plot(t, error, color=METRIC_COLORS['error'], linewidth=1.5)
        ax3.axhline(y=0.02, color='red', linestyle='--', alpha=0.5, label='Settling Threshold')
        ax3.set_ylabel('Error Norm (rad)')
        ax3.set_xlabel('Time (s)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_title('Tracking Error')

        # 4. Performance metrics (text)
        ax4 = fig.add_subplot(gs[0, 2])
        ax4.axis('off')
        summary = run_data.summary
        metrics_text = (
            f"Performance Summary\n\n"
            f"Settling Time: {summary.settling_time_s:.2f} s\n"
            f"Overshoot: {summary.overshoot_pct:.1f} %\n"
            f"SS Error: {summary.steady_state_error:.4f} rad\n"
            f"Energy: {summary.energy_j:.1f} J\n"
            f"Peak Control: {summary.peak_control:.2f} N\n"
            f"Score: {summary.get_score():.1f}/100"
        )
        ax4.text(0.1, 0.9, metrics_text, transform=ax4.transAxes, fontsize=11,
                verticalalignment='top', family='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        # 5. Chattering metrics
        ax5 = fig.add_subplot(gs[1, 2])
        ax5.axis('off')
        chattering_text = (
            f"Chattering Analysis\n\n"
            f"Frequency: {summary.chattering_frequency_hz:.2f} Hz\n"
            f"Amplitude: {summary.chattering_amplitude:.4f}\n"
            f"Total Var: {summary.chattering_total_variation:.2f}"
        )
        ax5.text(0.1, 0.9, chattering_text, transform=ax5.transAxes, fontsize=11,
                verticalalignment='top', family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

        # 6. Stability metrics
        ax6 = fig.add_subplot(gs[2, 2])
        ax6.axis('off')
        stability_text = (
            f"Stability Analysis\n\n"
            f"Bounded: {'Yes' if summary.bounded_states else 'No'}\n"
            f"Margin: {summary.stability_margin:.4f}\n"
            f"Lyapunov: {summary.lyapunov_decrease_rate:.6f}"
        )
        ax6.text(0.1, 0.9, stability_text, transform=ax6.transAxes, fontsize=11,
                verticalalignment='top', family='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))

        fig.suptitle(f'Performance Summary - {run_data.controller}', fontsize=16, fontweight='bold')

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig

    def plot_controller_comparison(self,
                                  comparison_data: ComparisonData,
                                  metric: str = 'score',
                                  save_path: Optional[str] = None) -> Figure:
        """
        Create bar chart comparing controllers.

        Args:
            comparison_data: Comparison data object
            metric: Metric to compare ('score', 'settling_time_s', etc.)
            save_path: Optional path to save figure

        Returns:
            Matplotlib figure
        """
        rankings = comparison_data.get_ranking(metric)

        if not rankings:
            raise ValueError("No valid comparison data")

        controllers, values = zip(*rankings)

        fig, ax = plt.subplots(figsize=(10, 6))

        colors = [CONTROLLER_COLORS.get(c.lower().replace(' ', '_'), '#cccccc') for c in controllers]
        bars = ax.barh(controllers, values, color=colors)

        ax.set_xlabel(self._get_metric_label(metric))
        ax.set_title(f'Controller Comparison - {self._get_metric_label(metric)}', fontsize=14, fontweight='bold')
        ax.grid(True, axis='x', alpha=0.3)

        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2,
                   f'{width:.2f}',
                   ha='left', va='center', fontsize=10)

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig

    def create_interactive_plot(self, run_data: DashboardData) -> go.Figure:
        """
        Create interactive Plotly figure.

        Args:
            run_data: Dashboard data for the run

        Returns:
            Plotly figure
        """
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Angles', 'Velocities', 'Control Signal', 'Error Norm', 'Phase Portrait', 'Metrics'),
            specs=[
                [{'type': 'scatter'}, {'type': 'scatter'}],
                [{'type': 'scatter'}, {'type': 'scatter'}],
                [{'type': 'scatter'}, {'type': 'indicator'}]
            ],
            vertical_spacing=0.1,
            horizontal_spacing=0.1
        )

        # Get time series
        t, angle1 = run_data.get_time_series('angle1')
        _, angle2 = run_data.get_time_series('angle2')
        _, vel1 = run_data.get_time_series('velocity1')
        _, vel2 = run_data.get_time_series('velocity2')
        _, control = run_data.get_time_series('control')
        _, error = run_data.get_time_series('error_norm')

        # Angles
        fig.add_trace(go.Scatter(x=t, y=np.rad2deg(angle1), name='Theta 1', line=dict(color='blue')), row=1, col=1)
        fig.add_trace(go.Scatter(x=t, y=np.rad2deg(angle2), name='Theta 2', line=dict(color='orange')), row=1, col=1)

        # Velocities
        fig.add_trace(go.Scatter(x=t, y=np.rad2deg(vel1), name='Omega 1', line=dict(color='green')), row=1, col=2)
        fig.add_trace(go.Scatter(x=t, y=np.rad2deg(vel2), name='Omega 2', line=dict(color='red')), row=1, col=2)

        # Control
        fig.add_trace(go.Scatter(x=t, y=control, name='Control', line=dict(color='purple')), row=2, col=1)

        # Error
        fig.add_trace(go.Scatter(x=t, y=error, name='Error', line=dict(color='brown')), row=2, col=2)

        # Phase portrait
        fig.add_trace(go.Scatter(x=angle1, y=vel1, mode='lines', name='Phase', line=dict(color='teal')), row=3, col=1)

        # Performance score indicator
        if run_data.summary:
            score = run_data.summary.get_score()
            fig.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=score,
                title={'text': "Performance Score"},
                delta={'reference': 80},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 70], 'color': "lightgray"},
                        {'range': [70, 85], 'color': "gray"},
                        {'range': [85, 100], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ), row=3, col=2)

        fig.update_layout(height=1000, showlegend=True, title_text=f"Interactive Dashboard - {run_data.controller}")

        return fig

    def _get_metric_label(self, metric: str) -> str:
        """Get human-readable label for metric."""
        labels = {
            'angle1': 'Angle 1 (rad)',
            'angle2': 'Angle 2 (rad)',
            'velocity1': 'Velocity 1 (rad/s)',
            'velocity2': 'Velocity 2 (rad/s)',
            'control': 'Control Signal (N)',
            'error_norm': 'Error Norm (rad)',
            'chattering': 'Chattering Index',
            'score': 'Performance Score',
            'settling_time_s': 'Settling Time (s)',
            'overshoot_pct': 'Overshoot (%)',
            'energy_j': 'Energy (J)',
            'steady_state_error': 'Steady-State Error (rad)'
        }
        return labels.get(metric, metric)


class DataExporter:
    """
    Export performance data to various formats.

    Supports CSV, JSON, HDF5 (optional), and summary reports.
    """

    def __init__(self, output_dir: str = '.artifacts/monitoring_exports'):
        """
        Initialize exporter.

        Args:
            output_dir: Directory for exported files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_csv(self,
                  run_data: DashboardData,
                  filepath: Optional[str] = None) -> str:
        """
        Export run data to CSV.

        Args:
            run_data: Dashboard data to export
            filepath: Optional custom filepath

        Returns:
            Path to exported file
        """
        if filepath is None:
            filepath = self.output_dir / f"{run_data.run_id}_data.csv"
        else:
            filepath = Path(filepath)

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'timestamp_s', 'time_step', 'controller', 'scenario',
                'theta1_rad', 'theta2_rad', 'omega1_rad_s', 'omega2_rad_s',
                'control_output', 'error_norm', 'chattering_index', 'settling_detected'
            ])

            # Data rows
            for snap in run_data.snapshots:
                writer.writerow([
                    snap.timestamp_s,
                    snap.time_step,
                    snap.controller_type,
                    run_data.scenario,
                    snap.angle1_rad,
                    snap.angle2_rad,
                    snap.velocity1_rad_s,
                    snap.velocity2_rad_s,
                    snap.control_output,
                    snap.error_norm,
                    snap.chattering_index,
                    snap.settling_detected
                ])

        return str(filepath)

    def export_json(self,
                   run_data: DashboardData,
                   filepath: Optional[str] = None) -> str:
        """
        Export run data to JSON.

        Args:
            run_data: Dashboard data to export
            filepath: Optional custom filepath

        Returns:
            Path to exported file
        """
        if filepath is None:
            filepath = self.output_dir / f"{run_data.run_id}_data.json"
        else:
            filepath = Path(filepath)

        run_data.to_json(str(filepath))

        return str(filepath)

    def export_summary_report(self,
                            run_data: DashboardData,
                            filepath: Optional[str] = None) -> str:
        """
        Export summary report as text.

        Args:
            run_data: Dashboard data to export
            filepath: Optional custom filepath

        Returns:
            Path to exported file
        """
        if filepath is None:
            filepath = self.output_dir / f"{run_data.run_id}_summary.txt"
        else:
            filepath = Path(filepath)

        with open(filepath, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write(f"PERFORMANCE SUMMARY REPORT\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Run ID: {run_data.run_id}\n")
            f.write(f"Controller: {run_data.controller}\n")
            f.write(f"Scenario: {run_data.scenario}\n")
            f.write(f"Status: {run_data.status.value}\n")
            f.write(f"Duration: {run_data.duration_s:.2f} s\n\n")

            if run_data.summary:
                s = run_data.summary
                f.write("-" * 80 + "\n")
                f.write("TIME-DOMAIN METRICS\n")
                f.write("-" * 80 + "\n")
                f.write(f"  Settling Time:       {s.settling_time_s:.4f} s\n")
                f.write(f"  Rise Time:           {s.rise_time_s:.4f} s\n")
                f.write(f"  Overshoot:           {s.overshoot_pct:.2f} %\n")
                f.write(f"  Steady-State Error:  {s.steady_state_error:.6f} rad\n\n")

                f.write("-" * 80 + "\n")
                f.write("ENERGY & EFFORT\n")
                f.write("-" * 80 + "\n")
                f.write(f"  Total Energy:        {s.energy_j:.2f} J\n")
                f.write(f"  Total Variation:     {s.total_variation:.2f}\n")
                f.write(f"  Peak Control:        {s.peak_control:.2f} N\n\n")

                f.write("-" * 80 + "\n")
                f.write("STABILITY METRICS\n")
                f.write("-" * 80 + "\n")
                f.write(f"  Bounded States:      {'Yes' if s.bounded_states else 'No'}\n")
                f.write(f"  Stability Margin:    {s.stability_margin:.6f}\n")
                f.write(f"  Lyapunov Rate:       {s.lyapunov_decrease_rate:.6f}\n\n")

                f.write("-" * 80 + "\n")
                f.write("CHATTERING ANALYSIS\n")
                f.write("-" * 80 + "\n")
                f.write(f"  Frequency:           {s.chattering_frequency_hz:.2f} Hz\n")
                f.write(f"  Amplitude:           {s.chattering_amplitude:.6f}\n")
                f.write(f"  Total Variation:     {s.chattering_total_variation:.2f}\n\n")

                f.write("-" * 80 + "\n")
                f.write("OVERALL SCORE\n")
                f.write("-" * 80 + "\n")
                f.write(f"  Performance Score:   {s.get_score():.1f} / 100\n\n")

        return str(filepath)


# Export all
__all__ = ['PerformanceVisualizer', 'DataExporter', 'CONTROLLER_COLORS', 'METRIC_COLORS']
