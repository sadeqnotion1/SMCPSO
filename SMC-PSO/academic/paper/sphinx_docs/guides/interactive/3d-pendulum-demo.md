# 3D Interactive Pendulum Visualization

**What This Is:**
An interactive 3D simulation of the double-inverted pendulum that runs directly in your browser. No installation required. Just adjust the controls and watch the physics happen in real-time.

**Why This Matters:**
Understanding how a double-inverted pendulum behaves is hard from equations alone. This visualization lets you see the system move, experiment with different settings, and build intuition for how the controller works.

**What You Can Do:**
- Adjust controller gains and see instant results
- Set different starting angles
- Watch the system stabilize or fail
- View from any angle using 3D camera controls

---

## Features Overview

**Graphics:**
- **WebGL Rendering** - Uses your graphics card (GPU) for smooth 3D graphics
- **Three.js Library** - Industry-standard 3D engine for web browsers

**Physics:**
- **Real-Time Simulation** - Runs at 60 frames per second
- **Simplified Dynamics** - Lighter math for browser performance
- **Interactive Control** - Change parameters while simulation runs

**Visualization:**
- **Orbit Camera** - Click and drag to rotate, scroll to zoom, right-click to pan
- **Visual Trail** - Shows the path the pendulum tip follows
- **Realistic Materials** - Metallic surfaces with realistic lighting and shadows

**Key Point:**
This is a simplified version for visualization. For precise simulations, use the Python version in `simulate.py`.

---

## Quick Start

```{raw} html
<div class="instructions-box">
    <h4>How to Use This Demo</h4>
    <ul>
        <li><strong>Camera Controls:</strong> Left-click + drag to rotate, scroll to zoom, right-click + drag to pan</li>
        <li><strong>Initial Conditions:</strong> Adjust θ₁ and θ₂ sliders to set pendulum angles (in radians)</li>
        <li><strong>Controller Gains:</strong> Tune K1-K6 to modify SMC control law behavior</li>
        <li><strong>Simulation:</strong> Click "Start" to run physics, "Stop" to pause, "Reset" to restore initial state</li>
    </ul>
</div>
```

---

## Interactive 3D Visualization

```{raw} html
<div class="pendulum-demo-container">
    <!-- 3D Canvas Container -->
    <div id="threejs-container">
        <div class="loading-indicator active">
            <div class="loading-spinner"></div>
            <p>Loading 3D renderer...</p>
        </div>
    </div>

    <!-- Control Panel -->
    <div class="control-panel">
        <!-- Simulation Controls -->
        <div class="control-section">
            <h3>Simulation Controls</h3>
            <div class="sim-controls">
                <button id="start-sim" class="sim-btn sim-btn-start">Start</button>
                <button id="stop-sim" class="sim-btn sim-btn-stop">Stop</button>
                <button id="reset-sim" class="sim-btn sim-btn-reset">Reset</button>
            </div>
            <div class="status-display" style="margin-top: 15px;">
                <div class="status-item">
                    <div class="status-label">Time</div>
                    <div class="status-value"><span id="sim-time">0.00</span><span class="status-unit">s</span></div>
                </div>
                <div class="status-item">
                    <div class="status-label">θ₁</div>
                    <div class="status-value"><span id="theta1-current">5.7</span><span class="status-unit">°</span></div>
                </div>
                <div class="status-item">
                    <div class="status-label">θ₂</div>
                    <div class="status-value"><span id="theta2-current">5.7</span><span class="status-unit">°</span></div>
                </div>
            </div>
        </div>

        <!-- Initial Conditions -->
        <div class="control-section">
            <h3>Initial Conditions</h3>
            <div class="slider-group">
                <div class="slider-label">
                    <span class="slider-label-name">θ₁ (rad)</span>
                    <span class="slider-label-value" id="theta1-value">0.10</span>
                </div>
                <input type="range" id="theta1-slider" min="-0.5" max="0.5" step="0.01" value="0.1">
            </div>
            <div class="slider-group">
                <div class="slider-label">
                    <span class="slider-label-name">θ₂ (rad)</span>
                    <span class="slider-label-value" id="theta2-value">0.10</span>
                </div>
                <input type="range" id="theta2-slider" min="-0.5" max="0.5" step="0.01" value="0.1">
            </div>
        </div>

        <!-- Controller Gains -->
        <div class="control-section">
            <h3>Controller Gains (Classical SMC)</h3>
            <div class="gains-grid">
                <div class="slider-group">
                    <div class="slider-label">
                        <span class="slider-label-name">K₁</span>
                        <span class="slider-label-value" id="k1-value">10.0</span>
                    </div>
                    <input type="range" id="k1-slider" min="0" max="30" step="0.1" value="10.0">
                </div>
                <div class="slider-group">
                    <div class="slider-label">
                        <span class="slider-label-name">K₂</span>
                        <span class="slider-label-value" id="k2-value">5.0</span>
                    </div>
                    <input type="range" id="k2-slider" min="0" max="30" step="0.1" value="5.0">
                </div>
                <div class="slider-group">
                    <div class="slider-label">
                        <span class="slider-label-name">K₃</span>
                        <span class="slider-label-value" id="k3-value">8.0</span>
                    </div>
                    <input type="range" id="k3-slider" min="0" max="30" step="0.1" value="8.0">
                </div>
                <div class="slider-group">
                    <div class="slider-label">
                        <span class="slider-label-name">K₄</span>
                        <span class="slider-label-value" id="k4-value">3.0</span>
                    </div>
                    <input type="range" id="k4-slider" min="0" max="30" step="0.1" value="3.0">
                </div>
                <div class="slider-group">
                    <div class="slider-label">
                        <span class="slider-label-name">K₅</span>
                        <span class="slider-label-value" id="k5-value">15.0</span>
                    </div>
                    <input type="range" id="k5-slider" min="0" max="30" step="0.1" value="15.0">
                </div>
                <div class="slider-group">
                    <div class="slider-label">
                        <span class="slider-label-name">K₆</span>
                        <span class="slider-label-value" id="k6-value">2.0</span>
                    </div>
                    <input type="range" id="k6-slider" min="0" max="30" step="0.1" value="2.0">
                </div>
            </div>
        </div>
    </div>
</div>
```

---

## Physics Model

**Why Simplified Dynamics:**
This visualization uses a lighter version of the physics equations to run smoothly in your browser. The full equations have coupling terms that are computationally expensive. For learning and visualization, this simplified version works great.

**The Math:**
Here's how the system calculates motion. Don't worry if the equations look complex - the key idea is that cart acceleration (ẍ) and pendulum angles (θ₁, θ₂) all influence each other.

$$
\begin{aligned}
\ddot{x} &= \frac{u - m_1 l_1 \dot{\theta}_1^2 \sin\theta_1 - m_2 l_2 \dot{\theta}_2^2 \sin\theta_2}{m_0 + m_1 + m_2} \\
\ddot{\theta}_1 &= \frac{g \sin\theta_1 - \ddot{x} \cos\theta_1}{l_1} \\
\ddot{\theta}_2 &= \frac{g \sin\theta_2 - \ddot{x} \cos\theta_2}{l_2}
\end{aligned}
$$

**What Each Variable Means:**
- ẍ: Cart acceleration (how fast the cart speeds up)
- θ₁, θ₂: Pendulum angles (how tilted each rod is)
- u: Control force (what the controller applies to stabilize)
- m₀, m₁, m₂: Masses (cart and two pendulums)
- l₁, l₂: Lengths (how long each pendulum rod is)
- g: Gravity (9.81 m/s²)

**For Precise Research:**
The full nonlinear dynamics (with all coupling terms) are available in `src/core/dynamics.py`. Use those for research and publication-quality results.

---

## Controller

**What Type of Controller:**
This uses Classical Sliding Mode Control (SMC). It's a robust control method that pushes the system toward a "sliding surface" where the pendulums stay balanced.

**How It Works:**
The control force (u) is calculated from six gains (K₁ through K₆) multiplied by the system state (position, velocity, angles). Higher gains mean stronger corrections.

$$
u = -\mathbf{K} \cdot \mathbf{x} = -(K_1 x + K_2 \dot{x} + K_3 \theta_1 + K_4 \dot{\theta}_1 + K_5 \theta_2 + K_6 \dot{\theta}_2)
$$

**What You Control:**
The six K values in the control panel. Each one affects a different aspect:
- K₁: Cart position correction
- K₂: Cart velocity damping
- K₃, K₄: First pendulum stabilization
- K₅, K₆: Second pendulum stabilization

**Default Gains:**
The default values were found using PSO (Particle Swarm Optimization). They provide good stability for most initial conditions. Try changing them to see what happens!

---

## Technical Details

**For Developers and Curious Users:**
This section explains how the visualization works under the hood.

### Rendering Engine

**What Powers The Graphics:**
- **Three.js r158** - A JavaScript library that makes WebGL easier to use
- **WebGL 2.0** - Direct access to your graphics card for fast 3D rendering

**Scene Components:**
- **Camera**: Perspective view with orbit controls (like a virtual drone camera)
- **Lighting**: Three light sources for realistic shading and shadows
- **Materials**: PBR rendering (same tech used in video games for realistic metals)

### Performance

**How Fast It Runs:**
- **Target**: 60 FPS (frames per second) - same as most games
- **Physics Rate**: 100 Hz (2 physics steps per visual frame)
- **Integration Method**: Euler method (simple and fast, good enough for visualization)

**Visual Effects:**
- **Trail Buffer**: Stores last 500 positions to show the pendulum's path

**Real-World Performance:**
Actual frame rate depends on your computer. Dedicated graphics cards will hit 60 FPS easily. Integrated graphics may run at 30-40 FPS.

### Browser Requirements

**Minimum:**
- Modern browser: Chrome 90+, Firefox 88+, Safari 14+, or Edge 90+
- WebGL support (enabled by default in most browsers)

**Recommended:**
- Dedicated GPU (graphics card) for smooth 60 FPS
- At least 4GB RAM
- Recent processor (2018 or newer)

---

## Related Pages

- {doc}`/guides/theory/smc-theory` - Full SMC mathematical foundations
- {doc}`/guides/theory/dip-dynamics` - Complete dynamics derivation
- {doc}`/controllers/classical_smc_technical_guide` - Classical SMC implementation details
- {doc}`/api/pso_optimization` - PSO gain tuning methodology

---

## Next Steps

Try these experiments:

1. **Stability Test**: Set θ₁ = θ₂ = 0.3 rad, click Start, observe stabilization
2. **Gain Tuning**: Reduce K₅ to 5.0, observe second pendulum oscillations
3. **Large Disturbance**: Set θ₁ = 0.5 rad (maximum), test controller limits
4. **Camera Views**: Rotate camera to side view, observe cart motion along rail

---

**[AI] Generated with Claude Code**
**Phase 1**: 3D Interactive Visualization (Revolutionary Documentation Enhancement)
