#======================================================================================\\\
#================================== streamlit_app.py ==================================\\\
#======================================================================================\\\

"""
Interactive Streamlit dashboard for PSO‑tuned SMC-controllers of a double‑inverted pendulum.

"""
from __future__ import annotations

import io
import json
import numpy as np
import matplotlib.pyplot as plt
# The Streamlit module is optional.  Wrap the import in a try/except so that
# this file can be imported when Streamlit is not installed (e.g., during
# automated tests).  When the import fails, fall back to a minimal stub
# object that exposes ``warning`` and ``markdown`` as no‑ops.  Any other
# attribute access on the stub returns a no‑op function.  Tests monkey‑patch
# ``streamlit_app.st`` directly, so the presence of this stub ensures that
# module import succeeds and that ``_parse_initial_state`` can still call
# ``st.warning`` without raising AttributeError.
try:
    import streamlit as st  # type: ignore
except Exception:
    class _StreamlitStub:
        def warning(self, *args, **kwargs) -> None:
            return None
        def markdown(self, *args, **kwargs) -> None:
            return None
        def __getattr__(self, name: str):
            # Return a no‑op function for any other attribute.  Using a
            # lambda ensures that calls return None regardless of arguments.
            return lambda *args, **kwargs: None
    st = _StreamlitStub()  # type: ignore
import yaml
import zipfile
from typing import Callable, Optional

from src.config import load_config
from src.controllers.factory import create_controller
from src.core.dynamics import DIPDynamics
from src.core.dynamics_full import FullDIPDynamics
from src.core.simulation_runner import run_simulation
from src.optimization.algorithms.pso_optimizer import PSOTuner
from src.utils.streamlit_theme import inject_theme

# Performance caching decorators
@st.cache_data
def cached_load_config(config_path: str):
    """Cache configuration loading to avoid repeated file I/O."""
    return load_config(config_path)

@st.cache_data
def cached_simulation_run(controller_type: str, params: list, config_dict: dict,
                         initial_state: list, duration: float, use_full_dynamics: bool):
    """Cache simulation results to avoid repeated computation for same parameters."""
    # Recreate objects from cached data
    config = type('Config', (), config_dict)()  # Simple object from dict

    # Create dynamics model
    if use_full_dynamics:
        dynamics = FullDIPDynamics(config.dip_params)
    else:
        dynamics = DIPDynamics(config.dip_params)

    # Create controller
    controller = create_controller(controller_type, config, gains=np.array(params))

    # Run simulation
    t, x, u = run_simulation(
        dynamics, controller,
        initial_state=np.array(initial_state),
        duration=duration,
        dt=config.simulation.dt
    )

    return t, x, u

@st.cache_data
def cached_pso_optimization(controller_type: str, config_dict: dict,
                           initial_state: list, seed: int = None):
    """Cache PSO optimization results to avoid repeated expensive computation."""
    config = type('Config', (), config_dict)()

    # Create dynamics and controller for PSO
    if config.simulation.use_full_dynamics:
        dynamics = FullDIPDynamics(config.dip_params)
    else:
        dynamics = DIPDynamics(config.dip_params)

    controller = create_controller(controller_type, config)

    # Run PSO optimization
    tuner = PSOTuner(
        controller=controller,
        dynamics=dynamics,
        initial_state=np.array(initial_state),
        config=config,
        seed=seed
    )

    best_params, cost_history = tuner.optimize()
    return best_params, cost_history

# Visualizer import (support both in‑repo path and local file during CI/examples)
try:
    from src.utils import Visualizer  # project structure
    if Visualizer is None:  # Gracefully handle stubbed exports
        raise ImportError('Visualizer export is unavailable')
except (ModuleNotFoundError, ImportError):
    try:
        from visualization import Visualizer  # fallback for isolated runs
    except (ModuleNotFoundError, ImportError) as e:
        raise RuntimeError(
            "Critical: Visualizer module not found in either src/utils/ or local path. "
            "Cannot proceed without visualization capability."
        ) from e

# ────────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────────

def load_css(path: str):
    try:
        with open(path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:  # Expected - CSS is optional
        pass

def _parse_initial_state(text: str, default: np.ndarray, state_dim: int) -> np.ndarray:
    """Parse comma‑separated floats; pad/truncate to `state_dim`.
    Falls back to `default` on parse error.

    Why: We only catch ValueError and TypeError because these are the expected
    exceptions from user input parsing. Any other exception (like MemoryError,
    AttributeError) indicates a critical backend issue that should propagate.
    """
    try:
        arr = np.array([float(s) for s in text.replace("\n", ",").split(",") if s.strip() != ""], dtype=float)
        if arr.size == 0:
            st.warning("Empty initial state; using defaults from config.")
            return np.array(default, dtype=float)
    except ValueError:
        # These are expected from bad user input
        st.warning("Could not parse initial state; using defaults from config.")
        return np.array(default, dtype=float)
    except TypeError:
        # Also expected from certain malformed inputs
        st.warning("Invalid input type for initial state; using defaults from config.")
        return np.array(default, dtype=float)
    # Any other exception (like AttributeError, MemoryError) should propagate
    # as it indicates a serious backend issue, not a user input problem
    
    if arr.size < state_dim:
        arr = np.pad(arr, (0, state_dim - arr.size))
    elif arr.size > state_dim:
        st.warning(f"Input has {arr.size} values, but {state_dim} are required. Truncating excess values.")
        arr = arr[:state_dim]
    return arr

def _compute_metrics(t: np.ndarray, x: np.ndarray, u: np.ndarray,
                     tol_x: float = 0.02, tol_th: float = 0.05) -> dict:
    """Compute simple performance metrics.
    - Settling time: first time after which |x|<tol_x & |θ1|,|θ2|<tol_th until end
    - RMS control effort
    - Peak magnitudes
    """
    # tolerances against equilibrium 0
    within = (np.abs(x[:, 0]) < tol_x)
    if x.shape[1] >= 3:
        within = within & (np.abs(x[:, 1]) < tol_th) & (np.abs(x[:, 2]) < tol_th)

    settle_idx = len(t) - 1
    for i in range(len(t)):
        if np.all(within[i:]):
            settle_idx = i
            break

    metrics = {
        "settling_time_s": float(t[settle_idx]),
        "rms_control_N": float(np.sqrt(np.mean(u**2))) if u.size else 0.0,
        "peak_abs_x_m": float(np.max(np.abs(x[:, 0]))),
        "peak_abs_th1_deg": float(np.rad2deg(np.max(np.abs(x[:, 1])))) if x.shape[1] > 1 else 0.0,
        "peak_abs_th2_deg": float(np.rad2deg(np.max(np.abs(x[:, 2])))) if x.shape[1] > 2 else 0.0,
        "max_abs_u_N": float(np.max(np.abs(u))) if u.size else 0.0,
    }
    return metrics

class DisturbedDynamics:
    """Wrap a dynamics model and inject an external disturbance d(t) to the input.

    The wrapped `step` passes (u + d(t)) to the underlying model. Time is
    advanced internally using the provided `dt` at each call.
    """
    def __init__(self, base, d_fn: Optional[Callable[[float], float]]):
        self._base = base
        self._d_fn = d_fn
        self._time = 0.0
        self.state_dim = int(getattr(base, "state_dim", 6))

    def default_state(self):
        if hasattr(self._base, "default_state"):
            return self._base.default_state()
        return np.zeros(self.state_dim)

    def step(self, state: np.ndarray, u: float, dt: float) -> np.ndarray:
        d = float(self._d_fn(self._time)) if self._d_fn is not None else 0.0
        self._time += float(dt)
        return self._base.step(state, u + d, dt)

    def __getattr__(self, name):  # allow Visualizer to read geometry (l1/l2/etc.)
        return getattr(self._base, name)

# ────────────────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────────────────

def main():
    # ───────── Translations
    @st.cache_data
    def load_translations(path: str = "translations.yaml") -> dict:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Translations are optional - return empty dict
            return {}

    cfg = load_config("config.yaml")
    translations = load_translations()

    st.set_page_config(page_title="Pendulum Control Simulator", layout="wide")
    load_css("src/assets/style.css")
    inject_theme(enable=True)  # Phase 3 Wave 3: DIP docs theme parity

    # Workaround for older/newer Streamlit versions: ``st.session_state`` may
    # behave like a dictionary without a ``get`` method.  Define a helper
    # function to retrieve keys safely.  When ``st.session_state.get``
    # exists, use it; otherwise fall back to dict-style indexing.
    def _session_state_get(key: str, default: Optional[str] = None) -> Optional[str]:
        ss = st.session_state  # type: ignore[attr-defined]
        if hasattr(ss, "get"):
            try:
                return ss.get(key, default)  # type: ignore[call-arg]
            except Exception:
                pass
        try:
            return ss[key]  # type: ignore[index]
        except Exception:
            return default
    # Language selector
    lang_default = _session_state_get("lang", "English")
    # Use keyword arguments for selectbox to accommodate fake streamlit stubs in
    # tests.  Passing arguments positionally causes a ``TypeError`` when
    # ``st.sidebar.selectbox`` is a simple function accepting only keyword
    # arguments (see tests/test_app/test_streamlit_app.py).  Provide a label
    # and options explicitly to avoid positional parameters.
    st.session_state.lang = st.sidebar.selectbox(
        label="Language / زبان",
        options=("English", "فارسی"),
        index=("English", "فارسی").index(lang_default),
    )
    t = translations.get(st.session_state.lang, translations.get("English", {}))

    # ───────── Sidebar
    st.sidebar.header(t.get("sidebar_header", "Controls"))

    # 1) Dynamics selection
    st.sidebar.subheader(t.get("dynamics_header", "1. Dynamics Model"))
    use_full_dynamics = st.sidebar.checkbox(
        t.get("use_full_label", "Use Full Nonlinear Dynamics"),
        value=bool(getattr(cfg.simulation, "use_full_dynamics", False)),
        help=t.get("use_full_help", "Use the complete, more accurate dynamics model."),
    )
    cfg.simulation.use_full_dynamics = use_full_dynamics

    # 2) Controller
    st.sidebar.subheader(t.get("controller_select", "2. Controller"))
    controller_options = list(cfg.controllers.keys())
    controller_sel = st.sidebar.selectbox(
        label=t.get("controller_label", "Controller Type"),
        options=controller_options,
    )

    # 3) PSO (optional)
    st.sidebar.subheader(t.get("pso_header", "Optimization"))
    best_params = np.array(cfg.controller_defaults[controller_sel]["gains"], dtype=float)
    if st.sidebar.button(t.get("run_button", "Run PSO")):
        with st.spinner(t.get("spinner_msg", "Optimizing...")):
            def controller_factory(gains):
                return create_controller(controller_sel, config=cfg, gains=gains)
            tuner = PSOTuner(controller_factory, config=cfg, seed=getattr(cfg, "global_seed", None))
            res = tuner.optimise(x0=np.asarray(best_params, dtype=float))
            if np.isfinite(res.get("best_cost", np.inf)):
                best_params = np.array(res["best_pos"], dtype=float)
                st.success(t.get("success_msg", "Optimization succeeded."))
                st.metric(label=t.get("cost_metric", "Best Cost"), value=f"{res['best_cost']:.4f}")
            else:
                st.error(t.get("opt_fail", "Optimization failed to find a valid solution."))
    st.sidebar.write(f"**{t.get('params_header', 'Controller Gains')}**")
    st.sidebar.code(np.array2string(best_params, precision=3))

    # 4) Simulation settings (NEW)
    st.sidebar.subheader(t.get("sim_settings_header", "Simulation Settings"))
    sim_cfg = cfg.simulation
    sim_duration = st.sidebar.slider(
        t.get("sim_duration_label", "Simulation Duration (s)"),
        min_value=1.0,
        max_value=60.0,
        value=float(sim_cfg.duration),
        step=0.5,
    )
    sim_dt = st.sidebar.slider(
        t.get("sim_dt_label", "Time Step dt (s)"),
        min_value=0.001,
        max_value=0.1,
        value=float(sim_cfg.dt),
        step=0.001,
    )

    # Initial state input
    default_state = np.array(sim_cfg.initial_state, dtype=float)
    state_str = st.sidebar.text_area(
        t.get("initial_state_label", "Initial State (comma‑separated)"),
        value=", ".join([f"{v:.3f}" for v in default_state]),
        help=t.get("initial_state_help", "[x, θ1, θ2, ẋ, θ̇1, θ̇2]"),
    )
    state_dim = 6
    initial_state = _parse_initial_state(state_str, default_state, state_dim)

    # 5) Disturbance (NEW)
    st.sidebar.subheader(t.get("disturbance_header", "Disturbance"))
    add_disturbance = st.sidebar.checkbox(t.get("add_disturbance_label", "Add Disturbance"), value=False)
    disturbance_function = None
    if add_disturbance:
        dist_mag = st.sidebar.slider(
            t.get("dist_magnitude_label", "Magnitude (N)"),
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.1,
        )
        dist_start = st.sidebar.slider(
            t.get("dist_start_label", "Start Time (s)"),
            min_value=0.0,
            max_value=sim_duration - 0.1,
            value=1.0,
            step=0.1,
        )
        dist_duration = st.sidebar.slider(
            t.get("dist_duration_label", "Duration (s)"),
            min_value=0.1,
            max_value=sim_duration - dist_start,
            value=0.5,
            step=0.1,
        )
        # Rectangular pulse
        def disturbance_function(t: float) -> float:
            return dist_mag if dist_start <= t < dist_start + dist_duration else 0.0

    # ───────── Main area
    st.title("🎯 Pendulum Control Dashboard")
    st.markdown("""
    **Welcome to your control systems playground!** This interactive simulator lets you experiment with
    advanced sliding mode controllers for a double-inverted pendulum. Whether you're learning control theory,
    optimizing algorithms, or conducting research, you're in the right place.
    """)

    # ───────── Getting Started Guide (comprehensive intro)
    with st.expander("📖 Getting Started - Click here if this is your first time!", expanded=False):
        st.markdown("""
        ### What Is This?

        Imagine balancing a broomstick on your hand — now imagine balancing **two broomsticks**,
        one stacked on top of the other, while the base (your hand) can slide left and right.
        That's a **double-inverted pendulum**, and it's one of the most challenging problems in control engineering!

        This dashboard lets you:
        - **Simulate** the pendulum physics in real-time
        - **Control** it using advanced algorithms (Sliding Mode Control)
        - **Optimize** controller parameters automatically (PSO - Particle Swarm Optimization)
        - **Visualize** how everything works with live animations
        - **Export** your results for further analysis

        ---

        ### Key Features
        """)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            **🎮 Interactive Control**
            - Real-time simulation
            - 4 different controller types
            - Adjustable parameters
            - Live pendulum animation
            - Performance metrics
            """)

        with col2:
            st.markdown("""
            **🧠 Intelligent Optimization**
            - One-click PSO optimization
            - Automatic gain tuning
            - Watch convergence happen
            - Compare before/after
            - Save optimized gains
            """)

        with col3:
            st.markdown("""
            **📊 Analysis & Export**
            - Performance metrics
            - Time-series plots
            - Disturbance testing
            - CSV data export
            - Publication-ready plots
            """)

        st.markdown("""
        ---

        ### Quick Start Guide

        Ready to get started? Follow these 5 simple steps:

        **Step 1: Choose Your Controller** 👈 *(Look at the sidebar on the left)*
        - **Classical SMC**: The foundation — reliable and proven
        - **Super-Twisting SMC**: Smoother control, less "chattering"
        - **Adaptive SMC**: Adapts to changes automatically
        - **Hybrid Adaptive STA**: The best of both worlds

        > 💡 **First time?** Start with **Classical SMC** using default settings.

        **Step 2: (Optional) Run PSO Optimization**
        - Click the "Run PSO" button in the sidebar
        - Wait 30-60 seconds while the swarm finds optimal gains
        - See the "Best Cost" improve in real-time

        > ⚡ **Skip this** if you just want to see how it works with default settings.

        **Step 3: Adjust Simulation Settings**
        - Duration: How long to run (default 10 seconds is good)
        - Time step: Leave at 0.01s for smooth animation
        - Initial state: Starting angles for the pendulums

        > 🎯 **Tip**: Try small initial angles like [0, 0.05, -0.03, 0, 0, 0] for stable starts.

        **Step 4: (Optional) Add a Disturbance**
        - Check "Add Disturbance" to test robustness
        - This simulates a push or external force
        - Watch how the controller recovers

        **Step 5: Watch It Run!**
        - Scroll down to see the live animation
        - Check the time-series plots (expandable)
        - Review performance metrics
        - Download results as ZIP file

        ---

        ### Common Workflows

        **"I want to see how SMC works"**
        1. Select "classical_smc" from the sidebar
        2. Leave everything at defaults
        3. Scroll down and watch the animation
        4. Expand "Time-Series" to see detailed plots

        **"I want optimal performance"**
        1. Select any controller
        2. Click "Run PSO" button
        3. Wait for optimization to finish
        4. Scroll down to see the improved performance
        5. Compare metrics with default gains

        **"I want to test robustness"**
        1. Select any controller
        2. Check "Add Disturbance"
        3. Adjust magnitude (try 2-5 N)
        4. Set start time (around 1-2 seconds)
        5. Watch how the controller recovers

        **"I want to compare controllers"**
        1. Run simulation with Classical SMC, note metrics
        2. Change to Super-Twisting SMC, run again
        3. Compare settling time, control effort, peak angles
        4. Try with and without PSO optimization

        ---

        ### Understanding the Interface

        **Left Sidebar (Controls):**
        - **Dynamics Model**: Choose simple or full physics
        - **Controller**: Pick your control algorithm
        - **Optimization**: Run PSO to find best gains
        - **Simulation Settings**: Duration, time step, initial state
        - **Disturbance**: Add external forces to test robustness

        **Main Area (Results):**
        - **Animation**: Live visualization of the pendulum
        - **Time-Series Plots**: Cart position, angles, velocities, control input
        - **Performance Metrics**: Key numbers (settling time, RMS control, peak values)
        - **Download**: Export everything as ZIP file

        ---

        ### Need Help?

        - 📚 **Documentation**: Full guides available in `docs/` directory
        - 🐛 **Issues**: Report bugs on GitHub
        - 💬 **Questions**: Check README.md for more examples
        - 🔬 **Research**: See CITATIONS.md for academic references

        **Ready?** Close this guide and start experimenting! 🚀
        """)

    # ───────── Advanced Documentation (renamed from previous expander)
    with st.expander("🚀 Advanced Features & Documentation"):
        st.markdown("""
        **🌟 Enhanced Interactive Research Tools Available!**

        This dashboard is part of our **comprehensive interactive documentation system**:

        **📚 Static Documentation** (Task 2 - 96.9% coverage):
        - Professional API documentation with realistic examples
        - Enhanced docstrings showcasing real controller functionality
        - Publication-quality documentation standards

        **🚀 Interactive Research Tools** (Task 3):
        - **Jupyter Notebooks**: Real-time parameter tuning with live visualization
        - **Statistical Analysis**: Rigorous confidence intervals and hypothesis testing
        - **PSO Visualization**: Watch swarm intelligence optimize controller gains

        **🔬 Advanced Analysis Options:**
        """)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**🎛️ Interactive Controller Demo**")
            st.markdown("• Real-time parameter sliders")
            st.markdown("• Live pendulum animation")
            st.markdown("• Performance confidence intervals")

        with col2:
            st.markdown("**🐝 PSO Optimization Visualization**")
            st.markdown("• Live particle swarm animation")
            st.markdown("• Real-time convergence plots")
            st.markdown("• Cost function exploration")

        with col3:
            st.markdown("**📊 Statistical Analysis**")
            st.markdown("• Monte Carlo performance studies")
            st.markdown("• Statistical hypothesis testing")
            st.markdown("• Research report generation")

        st.info("💡 **To access interactive notebooks**: Run `jupyter lab notebooks/` in the project directory")
        st.success("🌟 This demonstrates the evolution from excellent static documentation to interactive research platform!")

    # ───────── Dynamics
    physics_params = cfg.physics
    if use_full_dynamics:
        base_model = FullDIPDynamics(physics_params)
    else:
        base_model = DIPDynamics(physics_params)

    dynamics_model = DisturbedDynamics(base_model, disturbance_function)

    # ───────── Controller
    controller = create_controller(controller_sel, config=cfg, gains=best_params)

    # ───────── Run
    t_sim, x_sim, u_sim = run_simulation(
        controller=controller,
        dynamics_model=dynamics_model,
        sim_time=sim_duration,
        dt=sim_dt,
        initial_state=initial_state,
    )

    # ───────── Visualization (NEW)
    st.subheader(t.get("animation_header", "Simulation Animation"))
    
    # Create visualizer
    visualizer = Visualizer(dynamics_model)
    visualizer.animate(t_sim, x_sim, u_sim, dt=sim_dt)
    
    # Display animation
    # Animation objects don't render reliably in Streamlit; show the figure.
    st.pyplot(visualizer.fig)

    # ───────── Time‑series
    with st.expander(t.get("time_series_header", "Time‑Series (x, θ1, θ2, u)")):
        fig, axes = plt.subplots(4, 1, figsize=(8, 8), sharex=True)
        
        # Cart position
        axes[0].plot(t_sim, x_sim[:, 0], 'b-')
        axes[0].set_ylabel(t.get("cart_position_label", "Cart Position x (m)"))
        axes[0].grid(True, alpha=0.3)
        
        # Pendulum angles
        axes[1].plot(t_sim, np.rad2deg(x_sim[:, 1]), 'r-', label='θ1')
        axes[1].plot(t_sim, np.rad2deg(x_sim[:, 2]), 'g-', label='θ2')
        axes[1].set_ylabel(t.get("angles_label", "Angles (deg)"))
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # Velocities
        axes[2].plot(t_sim, x_sim[:, 3], 'b--', label='ẋ')
        axes[2].plot(t_sim, x_sim[:, 4], 'r--', label='θ̇1')
        axes[2].plot(t_sim, x_sim[:, 5], 'g--', label='θ̇2')
        axes[2].set_ylabel(t.get("velocities_label", "Velocities"))
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        # Control input
        axes[3].plot(t_sim[:-1], u_sim, 'k-')
        axes[3].set_ylabel(t.get("control_input_label", "Control Input u (N)"))
        axes[3].set_xlabel(t.get("time_label", "Time (s)"))
        axes[3].grid(True, alpha=0.3)
        
        # Add disturbance visualization if active
        if disturbance_function is not None:
            d_values = [disturbance_function(t) for t in t_sim[:-1]]
            axes[3].plot(t_sim[:-1], d_values, 'orange', linestyle='--', label='Disturbance')
            axes[3].legend()
        
        fig.tight_layout()
        st.pyplot(fig)

    # ───────── Performance analysis (NEW)
    st.subheader(t.get("performance_header", "Performance Analysis"))
    metrics = _compute_metrics(t_sim, x_sim, u_sim)
    
    cols = st.columns(3)
    with cols[0]:
        st.metric(t.get("settling_time_label", "Settling Time"), f"{metrics['settling_time_s']:.2f} s")
        st.metric(t.get("rms_control_label", "RMS Control"), f"{metrics['rms_control_N']:.2f} N")
    with cols[1]:
        st.metric(t.get("peak_x_label", "Peak |x|"), f"{metrics['peak_abs_x_m']:.3f} m")
        st.metric(t.get("peak_theta1_label", "Peak |θ1|"), f"{metrics['peak_abs_th1_deg']:.1f}°")
    with cols[2]:
        st.metric(t.get("peak_theta2_label", "Peak |θ2|"), f"{metrics['peak_abs_th2_deg']:.1f}°")
        st.metric(t.get("max_u_label", "Max |u|"), f"{metrics['max_abs_u_N']:.1f} N")

    # ───────── Downloads (NEW)
    st.subheader(t.get("download_header", "Download Results"))
    
    # Save time-series figure
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    
    # Create zip file with results
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add the plot
        zf.writestr("time_series.png", buf.getvalue())
        
        # Add metadata
        meta = {
            "controller": controller_sel,
            "parameters": best_params.tolist(),
            "simulation": {
                "duration": sim_duration,
                "dt": sim_dt,
                "initial_state": initial_state.tolist(),
            },
            "disturbance": {
                "enabled": add_disturbance,
                "magnitude": dist_mag if add_disturbance else 0,
                "start_time": dist_start if add_disturbance else 0,
                "duration": dist_duration if add_disturbance else 0,
            } if add_disturbance else None,
            "metrics": metrics,
        }
        zf.writestr("metadata.json", json.dumps(meta, indent=2))
        
        # Add raw data as CSV
        import csv
        csv_buf = io.StringIO()
        writer = csv.writer(csv_buf)
        writer.writerow(["time", "x", "theta1", "theta2", "x_dot", "theta1_dot", "theta2_dot", "u"])
        # Write all steps with control input (N rows)
        for i in range(len(u_sim)):
            writer.writerow([
                t_sim[i], x_sim[i, 0], x_sim[i, 1], x_sim[i, 2],
                x_sim[i, 3], x_sim[i, 4], x_sim[i, 5], u_sim[i]
            ])
        # Append final state vector without a corresponding control value
        writer.writerow([
            t_sim[-1], x_sim[-1, 0], x_sim[-1, 1], x_sim[-1, 2],
            x_sim[-1, 3], x_sim[-1, 4], x_sim[-1, 5], ''
        ])
        zf.writestr("simulation_data.csv", csv_buf.getvalue())
    
    zip_buf.seek(0)
    st.download_button(
        label=t.get("download_button", "Download Results (ZIP)"),
        data=zip_buf,
        file_name="pendulum_simulation_results.zip",
        mime="application/zip",
    )

    # ───────── RTL fix
    if st.session_state.lang == "فارسی":
        st.markdown("<style>div[data-testid='stSidebar'] > div {direction: rtl;}</style>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
#======================================================================================================================\\\