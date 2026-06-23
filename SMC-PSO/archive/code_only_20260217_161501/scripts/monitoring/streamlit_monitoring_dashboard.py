#!/usr/bin/env python
#======================================================================================\
#======================= streamlit_monitoring_dashboard.py =======================\
#======================================================================================\

"""
Real-time Performance Monitoring Dashboard for DIP Control Systems.

This Streamlit application provides comprehensive real-time monitoring,
performance comparison, and robustness analysis for all 7 controllers.

Features:
- Real-time state and control signal monitoring
- PSO convergence tracking
- Multi-controller performance comparison
- Robustness analysis and fault injection
- Experiment history and data export

Usage:
    streamlit run streamlit_monitoring_dashboard.py
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.monitoring import (
    ControlMetricsCollector,
    DashboardData,
    PerformanceSummary,
    ComparisonData,
    RunStatus
)
from src.controllers.factory import CONTROLLER_TYPES
from src.config import load_config


# Page configuration
st.set_page_config(
    page_title="DIP Control Monitor",
    page_icon="[CHART]",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-running {
        color: #28a745;
        font-weight: bold;
    }
    .status-complete {
        color: #17a2b8;
        font-weight: bold;
    }
    .status-failed {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'simulation_running' not in st.session_state:
        st.session_state.simulation_running = False
    if 'current_run' not in st.session_state:
        st.session_state.current_run = None
    if 'run_history' not in st.session_state:
        st.session_state.run_history = []
    if 'comparison_data' not in st.session_state:
        st.session_state.comparison_data = ComparisonData(comparison_id="benchmark_001")


# Sidebar configuration
def render_sidebar():
    """Render sidebar with configuration options."""
    st.sidebar.title("[SETTINGS] Configuration")

    # Controller selection
    st.sidebar.subheader("Controller Selection")
    controller = st.sidebar.selectbox(
        "Controller Type",
        options=CONTROLLER_TYPES,
        index=0,
        help="Select the controller to simulate"
    )

    # Scenario selection
    scenario = st.sidebar.selectbox(
        "Scenario",
        options=["stabilization", "tracking", "swing_up", "robustness_test"],
        index=0,
        help="Select simulation scenario"
    )

    # Simulation parameters
    st.sidebar.subheader("Simulation Parameters")
    duration = st.sidebar.slider(
        "Duration (s)",
        min_value=1.0,
        max_value=20.0,
        value=10.0,
        step=0.5,
        help="Simulation duration in seconds"
    )

    dt = st.sidebar.select_slider(
        "Time Step (ms)",
        options=[1, 5, 10, 20, 50],
        value=10,
        help="Simulation time step"
    )

    # Initial conditions
    st.sidebar.subheader("Initial Conditions")
    theta1_init = st.sidebar.slider(
        "Initial Angle 1 (deg)",
        min_value=-30.0,
        max_value=30.0,
        value=10.0,
        step=1.0
    )

    theta2_init = st.sidebar.slider(
        "Initial Angle 2 (deg)",
        min_value=-30.0,
        max_value=30.0,
        value=5.0,
        step=1.0
    )

    # Disturbances (for robustness testing)
    st.sidebar.subheader("Disturbances")
    add_disturbance = st.sidebar.checkbox("Add External Disturbance", value=False)

    disturbance_config = {}
    if add_disturbance:
        disturbance_config['type'] = st.sidebar.selectbox(
            "Disturbance Type",
            options=["impulse", "step", "sine", "random"]
        )
        disturbance_config['magnitude'] = st.sidebar.slider(
            "Magnitude",
            min_value=0.1,
            max_value=5.0,
            value=1.0,
            step=0.1
        )
        disturbance_config['time'] = st.sidebar.slider(
            "Application Time (s)",
            min_value=0.0,
            max_value=duration,
            value=duration / 2,
            step=0.5
        )

    # Advanced settings
    with st.sidebar.expander("Advanced Settings"):
        pso_enabled = st.checkbox("Enable PSO Optimization", value=False)
        save_results = st.checkbox("Auto-save Results", value=True)
        export_format = st.selectbox("Export Format", options=["JSON", "CSV", "Both"])

    return {
        'controller': controller,
        'scenario': scenario,
        'duration': duration,
        'dt': dt / 1000.0,  # Convert to seconds
        'initial_state': [
            np.deg2rad(theta1_init),
            np.deg2rad(theta2_init),
            0.0,
            0.0
        ],
        'disturbance': disturbance_config if add_disturbance else None,
        'pso_enabled': pso_enabled,
        'save_results': save_results,
        'export_format': export_format
    }


# Page 1: Real-Time Monitor
def page_realtime_monitor():
    """Real-time monitoring page with live plots."""
    st.markdown('<p class="main-header">[MONITOR] Real-Time Performance Monitor</p>', unsafe_allow_html=True)

    # Get configuration
    config = render_sidebar()

    # Control buttons
    col1, col2, col3 = st.columns([1, 1, 4])

    with col1:
        if st.button("[START] Start Simulation", disabled=st.session_state.simulation_running):
            st.session_state.simulation_running = True
            st.rerun()

    with col2:
        if st.button("[STOP] Stop Simulation", disabled=not st.session_state.simulation_running):
            st.session_state.simulation_running = False
            st.rerun()

    # Status display
    if st.session_state.simulation_running:
        st.markdown('<p class="status-running">[STATUS] RUNNING</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-complete">[STATUS] IDLE</p>', unsafe_allow_html=True)

    # Create placeholders for live updating
    status_container = st.container()
    plot_container = st.container()

    with status_container:
        st.subheader("[INFO] Current Metrics")
        metric_cols = st.columns(4)

    with plot_container:
        st.subheader("[CHART] Live State Plots")

        # Create tabs for different plots
        tab1, tab2, tab3, tab4 = st.tabs([
            "[ANGLE] Angles",
            "[VELOCITY] Velocities",
            "[CONTROL] Control Signal",
            "[ERROR] Error Norm"
        ])

    # Simulate data if running (in real implementation, this would be actual simulation)
    if st.session_state.simulation_running:
        # Mock data for demonstration
        t = np.linspace(0, config['duration'], int(config['duration'] / config['dt']))

        # Generate sample data
        theta1 = config['initial_state'][0] * np.exp(-t/2) * np.cos(3*t)
        theta2 = config['initial_state'][1] * np.exp(-t/3) * np.cos(2*t)
        theta1_dot = np.gradient(theta1, config['dt'])
        theta2_dot = np.gradient(theta2, config['dt'])
        control = -10 * theta1 - 5 * theta2 - 3 * theta1_dot - 2 * theta2_dot
        error_norm = np.sqrt(theta1**2 + theta2**2 + theta1_dot**2 + theta2_dot**2)

        # Display current metrics
        with metric_cols[0]:
            st.metric("Error Norm", f"{error_norm[-1]:.4f} rad")
        with metric_cols[1]:
            st.metric("Control Output", f"{control[-1]:.2f} N")
        with metric_cols[2]:
            st.metric("Time Elapsed", f"{t[-1]:.2f}s")
        with metric_cols[3]:
            settling_time = t[np.argmax(error_norm < 0.02)] if np.any(error_norm < 0.02) else float('inf')
            st.metric("Settling Time", f"{settling_time:.2f}s" if settling_time < float('inf') else "Not settled")

        # Plot angles
        with tab1:
            fig_angles = go.Figure()
            fig_angles.add_trace(go.Scatter(x=t, y=np.rad2deg(theta1), name='Theta 1', mode='lines'))
            fig_angles.add_trace(go.Scatter(x=t, y=np.rad2deg(theta2), name='Theta 2', mode='lines'))
            fig_angles.update_layout(
                xaxis_title='Time (s)',
                yaxis_title='Angle (deg)',
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig_angles, use_container_width=True)

        # Plot velocities
        with tab2:
            fig_vel = go.Figure()
            fig_vel.add_trace(go.Scatter(x=t, y=np.rad2deg(theta1_dot), name='Omega 1', mode='lines'))
            fig_vel.add_trace(go.Scatter(x=t, y=np.rad2deg(theta2_dot), name='Omega 2', mode='lines'))
            fig_vel.update_layout(
                xaxis_title='Time (s)',
                yaxis_title='Angular Velocity (deg/s)',
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig_vel, use_container_width=True)

        # Plot control signal
        with tab3:
            fig_control = go.Figure()
            fig_control.add_trace(go.Scatter(x=t, y=control, name='Control Signal', mode='lines', line=dict(color='red')))
            fig_control.update_layout(
                xaxis_title='Time (s)',
                yaxis_title='Control Input (N)',
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig_control, use_container_width=True)

        # Plot error norm
        with tab4:
            fig_error = go.Figure()
            fig_error.add_trace(go.Scatter(x=t, y=error_norm, name='Error Norm', mode='lines', line=dict(color='green')))
            fig_error.add_hline(y=0.02, line_dash='dash', annotation_text='Settling Threshold (2%)')
            fig_error.update_layout(
                xaxis_title='Time (s)',
                yaxis_title='Error Norm (rad)',
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig_error, use_container_width=True)


# Page 2: PSO Convergence
def page_pso_convergence():
    """PSO optimization convergence tracking."""
    st.markdown('<p class="main-header">[OPTIMIZE] PSO Convergence Monitor</p>', unsafe_allow_html=True)

    st.info("[INFO] PSO optimization tracking - monitor convergence of particle swarm optimization")

    # Mock PSO data
    generations = np.arange(1, 51)
    best_fitness = 100 * np.exp(-generations / 10)
    avg_fitness = 100 * np.exp(-generations / 15) + 10
    worst_fitness = 100 * np.exp(-generations / 20) + 20

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("[CHART] Fitness Evolution")

        fig_fitness = go.Figure()
        fig_fitness.add_trace(go.Scatter(
            x=generations, y=best_fitness, name='Best', mode='lines+markers',
            line=dict(color='green', width=2)
        ))
        fig_fitness.add_trace(go.Scatter(
            x=generations, y=avg_fitness, name='Average', mode='lines',
            line=dict(color='blue', width=2)
        ))
        fig_fitness.add_trace(go.Scatter(
            x=generations, y=worst_fitness, name='Worst', mode='lines',
            line=dict(color='red', width=1, dash='dash')
        ))
        fig_fitness.update_layout(
            xaxis_title='Generation',
            yaxis_title='Fitness (lower is better)',
            height=500,
            hovermode='x unified'
        )
        st.plotly_chart(fig_fitness, use_container_width=True)

    with col2:
        st.subheader("[INFO] Optimization Status")
        st.metric("Current Generation", f"{generations[-1]}")
        st.metric("Best Fitness", f"{best_fitness[-1]:.4f}")
        st.metric("Improvement", f"{((best_fitness[0] - best_fitness[-1]) / best_fitness[0] * 100):.1f}%")
        st.metric("Convergence Rate", f"{np.mean(np.diff(best_fitness[-10:])):.4f}/gen")

    # Particle diversity
    st.subheader("[CHART] Particle Diversity")
    diversity = 50 * np.exp(-generations / 8)

    fig_diversity = go.Figure()
    fig_diversity.add_trace(go.Scatter(
        x=generations, y=diversity, name='Diversity', mode='lines', fill='tozeroy',
        line=dict(color='purple', width=2)
    ))
    fig_diversity.update_layout(
        xaxis_title='Generation',
        yaxis_title='Swarm Diversity',
        height=300
    )
    st.plotly_chart(fig_diversity, use_container_width=True)


# Page 3: Performance Comparison
def page_performance_comparison():
    """Multi-controller performance comparison."""
    st.markdown('<p class="main-header">[COMPARE] Controller Performance Comparison</p>', unsafe_allow_html=True)

    st.info("[INFO] Compare performance metrics across all 7 controllers")

    # Mock comparison data
    controllers = [
        "Classical SMC",
        "Super-Twisting",
        "Adaptive SMC",
        "Hybrid Adaptive STA",
        "Swing-Up SMC",
        "MPC",
        "PID"
    ]

    # Generate mock performance data
    np.random.seed(42)
    comparison_df = pd.DataFrame({
        'Controller': controllers,
        'Settling Time (s)': [2.3, 1.8, 2.1, 1.5, 3.2, 2.0, 2.5],
        'Overshoot (%)': [15.2, 8.3, 10.5, 5.1, 20.3, 9.2, 18.7],
        'Energy (J)': [125.3, 98.2, 110.7, 85.4, 150.8, 105.3, 132.1],
        'Chattering': [0.45, 0.12, 0.28, 0.08, 0.52, 0.15, 0.35],
        'Score': [72.5, 85.3, 78.9, 92.1, 65.8, 81.4, 70.2]
    })

    # Display table
    st.subheader("[TABLE] Performance Metrics")

    # Color-code the scores
    def highlight_score(val):
        if val >= 90:
            return 'background-color: #d4edda'
        elif val >= 80:
            return 'background-color: #fff3cd'
        elif val >= 70:
            return 'background-color: #f8d7da'
        return ''

    styled_df = comparison_df.style.applymap(highlight_score, subset=['Score'])
    st.dataframe(styled_df, use_container_width=True)

    # Radar chart for top 4 controllers
    st.subheader("[CHART] Multi-Metric Radar Comparison")

    top_4 = comparison_df.nlargest(4, 'Score')

    fig_radar = go.Figure()

    metrics = ['Settling Time', 'Overshoot', 'Energy', 'Chattering', 'Score']

    for idx, row in top_4.iterrows():
        # Normalize metrics (invert so higher is better)
        normalized = [
            100 - (row['Settling Time (s)'] / 5 * 100),
            100 - (row['Overshoot (%)'] / 30 * 100),
            100 - (row['Energy (J)'] / 200 * 100),
            100 - (row['Chattering'] * 100),
            row['Score']
        ]

        fig_radar.add_trace(go.Scatterpolar(
            r=normalized + [normalized[0]],  # Close the polygon
            theta=metrics + [metrics[0]],
            name=row['Controller'],
            fill='toself'
        ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        height=500
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # Bar chart comparison
    st.subheader("[CHART] Score Ranking")

    fig_bar = px.bar(
        comparison_df.sort_values('Score', ascending=True),
        x='Score',
        y='Controller',
        orientation='h',
        color='Score',
        color_continuous_scale='RdYlGn',
        range_color=[0, 100]
    )
    fig_bar.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)


# Page 4: Robustness Analysis
def page_robustness_analysis():
    """Robustness analysis with fault injection."""
    st.markdown('<p class="main-header">[ROBUST] Robustness Analysis</p>', unsafe_allow_html=True)

    st.info("[INFO] Analyze controller robustness to faults and disturbances")

    # Fault types
    fault_types = ['Sensor Noise', 'Actuator Saturation', 'Model Mismatch', 'External Disturbance', 'Parameter Drift']
    controllers = ['Classical SMC', 'Super-Twisting', 'Adaptive SMC', 'Hybrid STA', 'MPC']

    # Mock robustness data (degradation percentage)
    np.random.seed(42)
    robustness_data = np.random.uniform(5, 40, size=(len(fault_types), len(controllers)))

    # Create heatmap
    st.subheader("[CHART] Robustness Heatmap (Performance Degradation %)")

    fig_heatmap = go.Figure(data=go.Heatmap(
        z=robustness_data,
        x=controllers,
        y=fault_types,
        colorscale='RdYlGn_r',  # Red = bad, Green = good
        text=np.round(robustness_data, 1),
        texttemplate='%{text}%',
        textfont={"size": 12},
        colorbar=dict(title="Degradation %")
    ))

    fig_heatmap.update_layout(
        xaxis_title='Controller',
        yaxis_title='Fault Type',
        height=400
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # Degradation curves
    st.subheader("[CHART] Performance Degradation Curves")

    col1, col2 = st.columns(2)

    with col1:
        # Sensor noise robustness
        noise_levels = np.linspace(0, 0.1, 20)
        degradation = {
            'Classical SMC': 100 - 30 * noise_levels / 0.1,
            'Super-Twisting': 100 - 15 * noise_levels / 0.1,
            'Adaptive SMC': 100 - 20 * noise_levels / 0.1,
            'Hybrid STA': 100 - 10 * noise_levels / 0.1
        }

        fig_noise = go.Figure()
        for ctrl, deg in degradation.items():
            fig_noise.add_trace(go.Scatter(x=noise_levels, y=deg, name=ctrl, mode='lines+markers'))

        fig_noise.update_layout(
            xaxis_title='Sensor Noise Level',
            yaxis_title='Performance Retention (%)',
            height=350
        )
        st.plotly_chart(fig_noise, use_container_width=True)

    with col2:
        # Model mismatch robustness
        mismatch_pct = np.linspace(0, 50, 20)
        degradation2 = {
            'Classical SMC': 100 - 40 * mismatch_pct / 50,
            'Super-Twisting': 100 - 25 * mismatch_pct / 50,
            'Adaptive SMC': 100 - 15 * mismatch_pct / 50,
            'Hybrid STA': 100 - 12 * mismatch_pct / 50
        }

        fig_mismatch = go.Figure()
        for ctrl, deg in degradation2.items():
            fig_mismatch.add_trace(go.Scatter(x=mismatch_pct, y=deg, name=ctrl, mode='lines+markers'))

        fig_mismatch.update_layout(
            xaxis_title='Model Mismatch (%)',
            yaxis_title='Performance Retention (%)',
            height=350
        )
        st.plotly_chart(fig_mismatch, use_container_width=True)

    # Vulnerability ranking
    st.subheader("[INFO] Vulnerability Ranking")

    vulnerability_df = pd.DataFrame({
        'Controller': controllers,
        'Most Vulnerable To': ['Sensor Noise', 'Actuator Sat.', 'Model Mismatch', 'Parameter Drift', 'Ext. Disturbance'],
        'Avg Degradation (%)': np.mean(robustness_data, axis=0)
    })

    st.dataframe(vulnerability_df, use_container_width=True)


# Page 5: Experiment History
def page_experiment_history():
    """Experiment history and data export."""
    st.markdown('<p class="main-header">[HISTORY] Experiment History</p>', unsafe_allow_html=True)

    st.info("[INFO] Browse past experiments and export results")

    # Mock experiment history
    history_df = pd.DataFrame({
        'Run ID': [f'run_{i:03d}' for i in range(1, 21)],
        'Controller': np.random.choice(['Classical SMC', 'Super-Twisting', 'Adaptive', 'Hybrid STA'], 20),
        'Scenario': np.random.choice(['stabilization', 'tracking', 'robustness'], 20),
        'Score': np.random.uniform(60, 95, 20).round(1),
        'Duration (s)': np.random.uniform(5, 15, 20).round(1),
        'Timestamp': pd.date_range(start='2025-01-01', periods=20, freq='6H')
    })

    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        controller_filter = st.multiselect(
            'Filter by Controller',
            options=history_df['Controller'].unique(),
            default=history_df['Controller'].unique()
        )

    with col2:
        scenario_filter = st.multiselect(
            'Filter by Scenario',
            options=history_df['Scenario'].unique(),
            default=history_df['Scenario'].unique()
        )

    with col3:
        min_score = st.slider('Minimum Score', 0, 100, 0)

    # Apply filters
    filtered_df = history_df[
        (history_df['Controller'].isin(controller_filter)) &
        (history_df['Scenario'].isin(scenario_filter)) &
        (history_df['Score'] >= min_score)
    ]

    # Display filtered results
    st.subheader(f"[TABLE] Experiment Results ({len(filtered_df)} runs)")
    st.dataframe(filtered_df, use_container_width=True)

    # Export options
    st.subheader("[EXPORT] Export Data")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("[CSV] Download CSV"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV File",
                data=csv,
                file_name='experiment_results.csv',
                mime='text/csv'
            )

    with col2:
        if st.button("[JSON] Download JSON"):
            json_str = filtered_df.to_json(orient='records', indent=2)
            st.download_button(
                label="Download JSON File",
                data=json_str,
                file_name='experiment_results.json',
                mime='application/json'
            )

    with col3:
        if st.button("[PDF] Generate Report"):
            st.info("[INFO] PDF report generation would be triggered here")

    # Statistics
    st.subheader("[STATS] Summary Statistics")

    stat_cols = st.columns(4)

    with stat_cols[0]:
        st.metric("Total Runs", len(filtered_df))
    with stat_cols[1]:
        st.metric("Avg Score", f"{filtered_df['Score'].mean():.1f}")
    with stat_cols[2]:
        st.metric("Best Score", f"{filtered_df['Score'].max():.1f}")
    with stat_cols[3]:
        st.metric("Total Duration", f"{filtered_df['Duration (s)'].sum():.1f}s")


# Main application
def main():
    """Main application entry point."""
    init_session_state()

    # Title
    st.title("[DASHBOARD] DIP Control System Performance Monitor")

    st.markdown("""
    Real-time performance monitoring and analysis dashboard for Double Inverted Pendulum control systems.
    Monitor live simulations, compare controllers, and analyze robustness.
    """)

    # Navigation
    page = st.sidebar.radio(
        "[NAVIGATE] Select Page",
        options=[
            "[MONITOR] Real-Time Monitor",
            "[OPTIMIZE] PSO Convergence",
            "[COMPARE] Performance Comparison",
            "[ROBUST] Robustness Analysis",
            "[HISTORY] Experiment History"
        ]
    )

    # Route to appropriate page
    if "[MONITOR]" in page:
        page_realtime_monitor()
    elif "[OPTIMIZE]" in page:
        page_pso_convergence()
    elif "[COMPARE]" in page:
        page_performance_comparison()
    elif "[ROBUST]" in page:
        page_robustness_analysis()
    elif "[HISTORY]" in page:
        page_experiment_history()


if __name__ == "__main__":
    main()
