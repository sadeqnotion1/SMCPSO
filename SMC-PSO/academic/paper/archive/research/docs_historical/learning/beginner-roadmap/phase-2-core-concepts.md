[<--Back to Beginner Roadmap](../beginner-roadmap.md)

---

# Phase 2: Core Concepts (Week 5-8, ~30 Hours)

::::{card}
:class-card: breadcrumb-container

:::{raw} html
<nav aria-label="Learning path breadcrumb" class="breadcrumb-nav">
  <ol class="breadcrumb-list">
    <li class="breadcrumb-item">
      <a href="../beginner-roadmap.html" class="breadcrumb-link">Beginner Roadmap</a>
    </li>
    <li class="breadcrumb-separator" aria-hidden="true">›</li>
    <li class="breadcrumb-item breadcrumb-active" aria-current="page">
      <span class="phase-badge phase-2">Phase 2</span>
      <span class="breadcrumb-text">Core Concepts</span>
    </li>
  </ol>
</nav>
:::

::::

---

**Prerequisites**: Phase 1 completion
**Previous Phase**: [Phase 1: Foundations](phase-1-foundations.md)
**Next Phase**: [Phase 3: Hands-On Learning](phase-3-hands-on.md)

**Goal**: Understand what control theory is, why we need it, and how sliding mode control works (intuitively, not mathematically yet).

## Phase 2 Overview

| Sub-Phase | Topic | Time | Why You Need This |
|-----------|-------|------|-------------------|
| 2.1 | What is Control Theory? | 6 hours | Understand the big picture |
| 2.2 | Feedback Control | 5 hours | Core control concept |
| 2.3 | Intro to Sliding Mode Control | 8 hours | Main algorithm in this project |
| 2.4 | What is Optimization? | 6 hours | Why PSO is needed |
| 2.5 | Understanding the DIP System | 5 hours | Specific problem we're solving |

**Total**: ~30 hours over 4 weeks (~7-8 hours/week)

---

<details>
<summary>2.1 What is Control Theory?</summary>

## Phase 2.1: What is Control Theory? (6 hours)

**Goal**: Understand control theory through everyday examples before diving into technical details.

### What You'll Learn

- Control systems are everywhere in daily life
- Open-loop vs closed-loop control
- Why feedback is essential
- Basic control terminology

### Learning Path

**Step 1: Control Systems in Everyday Life (2 hours)**

**What is a Control System?**
- A system that manages and regulates another system's behavior
- Goal: Make something behave the way you want

**Examples You Use Every Day**:

1. **Thermostat** (Temperature Control)
   - **Goal**: Keep room at 70°F
   - **Sensor**: Thermometer measures current temperature
   - **Actuator**: Heater/AC adjusts temperature
   - **Controller**: Compares desired (70°F) vs actual, decides to heat or cool

2. **Cruise Control** (Speed Control)
   - **Goal**: Maintain 65 mph
   - **Sensor**: Speedometer measures current speed
   - **Actuator**: Engine throttle adjusts power
   - **Controller**: Increases/decreases throttle to maintain speed

3. **Shower Temperature** (Manual Control)
   - **Goal**: Comfortable water temperature
   - **Sensor**: Your hand feels the temperature
   - **Actuator**: Hot/cold water knobs
   - **Controller**: YOU (adjusting knobs based on feel)

**Common Pattern**:
1. **Desired state** (setpoint): What you want
2. **Actual state** (measurement): What you have
3. **Error**: Difference between desired and actual
4. **Control action**: Adjustment to reduce error

**Practice Exercise**:
Identify the components (goal, sensor, actuator, controller) for:
1. Autopilot in an airplane
2. Automatic lights that turn on at dusk
3. Self-parking car

**Resources**:
- [Control Systems in Daily Life (Video, 15 min)](https://www.youtube.com/results?search_query=control+systems+examples+everyday+life)
- [Introduction to Control Theory (Article)](https://www.electrical4u.com/control-system-closed-loop-open-loop-control-system/)

---

**Step 2: Open-Loop vs Closed-Loop Control (2 hours)**

**Open-Loop Control** (No Feedback):
- Controller acts without measuring the result
- Like throwing a dart blindfolded

**Example**: Toaster
- You set timer to 2 minutes
- Toaster doesn't measure toast brownness
- If bread is frozen, it still stops after 2 minutes (might be undercooked)

**Pros**:
- Simple
- Cheap
- Fast

**Cons**:
- No correction for disturbances
- Sensitive to changes in environment
- No guarantee goal is achieved

---

**Closed-Loop Control** (With Feedback):
- Controller measures the result and adjusts
- Like throwing darts with your eyes open

**Example**: Thermostat
- Measures room temperature continuously
- Compares to desired temperature
- Adjusts heating/cooling based on error
- Even if door opens (disturbance), system compensates

**Pros**:
- Robust to disturbances
- Automatically corrects errors
- Achieves goal despite uncertainties

**Cons**:
- More complex
- Needs sensors
- Can be unstable if poorly designed

---

**Comparison Diagram**:

```{mermaid}
:alt: Comparison between open-loop control (no feedback) and closed-loop control (with feedback) showing structural differences
:align: center

%%{init: {'theme':'base', 'themeVariables': {'primaryColor':'#FFA500','primaryTextColor':'#fff','primaryBorderColor':'#FF8C00','lineColor':'#FF8C00','secondaryColor':'#FFE5CC','tertiaryColor':'#fff'}}}%%
flowchart TB
    subgraph OpenLoop[Open-Loop: No Feedback]
        A1[Input] --> B1[Controller] --> C1[System] --> D1[Output]
        E1[Disturbance] -.-> C1
    end

    subgraph ClosedLoop[Closed-Loop: With Feedback]
        A2[Desired] -->|+| B2((Compare)) --> C2[Controller] --> D2[System] --> E2[Output]
        E2 -->|Feedback| B2
        F2[Disturbance] -.-> D2
    end

    style A1 fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
    style B1 fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
    style C1 fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
    style D1 fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
    style A2 fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
    style B2 fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
    style C2 fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
    style D2 fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
    style E2 fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
```

---

**The Feedback Loop**:

```{mermaid}
:alt: Control loop feedback diagram showing the flow from desired state through error calculation, controller decision, control action, plant system, to actual state with sensor feedback
:align: center

%%{init: {'theme':'base', 'themeVariables': {'primaryColor':'#FFA500','primaryTextColor':'#fff','primaryBorderColor':'#FF8C00','lineColor':'#FF8C00','secondaryColor':'#FFE5CC','tertiaryColor':'#fff'}}}%%
flowchart LR
    A[Desired State<br/>Setpoint] -->|+| B((Error<br/>Compare))
    B --> C[Controller<br/>Decide]
    C --> D[Control Action]
    D --> E[Plant<br/>System]
    E --> F[Actual State]
    F -->|Sensor Feedback| B

    style A fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
    style B fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
    style C fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
    style D fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
    style E fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
    style F fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
```

**Double-Inverted Pendulum Example**:

- **Desired State**: Pendulums upright (θ₁ = 0, θ₂ = 0)
- **Actual State**: Measured angles (from sensors)
- **Error**: θ₁_error = 0 - θ₁_actual, θ₂_error = 0 - θ₂_actual
- **Controller**: Sliding mode control (calculates force needed)
- **Control Action**: Force applied to cart
- **Plant**: Physical pendulum system (responds to force)
- **Feedback**: Sensors measure new angles, repeat

**Practice Exercise**:
Draw the feedback loop diagram for:
1. Self-driving car maintaining lane position
2. Drone maintaining altitude

**Resources**:
- [Open vs Closed Loop Control (Video, 10 min)](https://www.youtube.com/results?search_query=open+loop+vs+closed+loop+control)
- [Feedback Control Explained (Video, 15 min)](https://www.youtube.com/results?search_query=feedback+control+explained+simply)

---

**Step 3: Control Theory Terminology (2 hours)**

**Essential Terms**:

1. **Setpoint** (Reference):
   - Desired value you want the system to achieve
   - Example: 70°F for thermostat

2. **Process Variable** (PV):
   - Actual measured value
   - Example: Current temperature

3. **Error** (e):
   - Difference: e = Setpoint - PV
   - Positive error: Need to increase
   - Negative error: Need to decrease

4. **Control Variable** (CV):
   - What the controller manipulates
   - Example: Heater power

5. **Disturbance**:
   - Uncontrolled input that affects system
   - Example: Opening a window (changes room temperature)

6. **Steady State**:
   - System has settled, not changing anymore
   - Error is minimal or zero

7. **Transient Response**:
   - System's behavior while changing from initial state to steady state
   - Includes overshoot, oscillations, settling time

8. **Stability**:
   - System eventually settles to steady state (doesn't diverge or oscillate forever)

**Performance Metrics**:

1. **Settling Time**:
   - How long to reach steady state
   - Faster is usually better

2. **Overshoot**:
   - How much the system exceeds the setpoint during transient
   - Lower is usually better (smoother)

3. **Steady-State Error**:
   - Error that remains after settling
   - Lower is better (more accurate)

4. **Rise Time**:
   - How quickly system initially responds
   - Faster is better (more responsive)

**Trade-offs**:
- Fast response often causes overshoot
- Eliminating overshoot makes response slower
- Controller design balances speed vs smoothness

**Practice Exercise**:
For each scenario, identify what needs to be minimized:

1. Autopilot: Plane should reach target altitude quickly without oscillating up and down.
   - Minimize: _____ (settling time, overshoot, or both?)

2. Robotic arm: Move precisely to pick up an egg without breaking it.
   - Minimize: _____ (overshoot, jerk, or both?)

3. Temperature control: Keep server room at exactly 68°F.
   - Minimize: _____ (steady-state error, disturbance rejection, or both?)

**Resources**:
- [Control Theory Glossary (Article)](https://www.electrical4u.com/control-system-terminology/)
- [Performance Metrics Explained (Video, 20 min)](https://www.youtube.com/results?search_query=control+system+performance+metrics)

---

### Self-Assessment: Phase 2.1

**Quiz**:

1. What is the main advantage of closed-loop control over open-loop?
2. Draw a simple block diagram showing feedback loop components.
3. Define "error" in a control system.
4. What is "settling time"?
5. Give three examples of control systems from your daily life.

**If you can answer 4-5 correctly**: Move to Phase 2.2
**If you can answer 2-3 correctly**: Review feedback loop concept
**If you can answer 0-1 correctly**: Re-watch introductory control theory videos

</details>

---

<details>
<summary>2.2 Feedback Control Deep Dive</summary>

## Phase 2.2: Feedback Control Deep Dive (5 hours)

**Goal**: Understand how feedback control works mathematically (simple examples first).

### Learning Path

**Step 1: PID Control (Intuitive Understanding) (3 hours)**

**Why PID?**
- Most common control algorithm in industry
- Simple but effective
- Foundation for understanding more advanced control

**PID = Proportional + Integral + Derivative**

---

**Proportional (P) Control**:
- Control action proportional to error
- Formula: `u = Kp × e`
- Kp = proportional gain (how aggressive)

**Example**: Steering a car to stay in lane
- If 1 meter off center (error = 1m):
  - Small Kp (0.5): Steer gently, slow correction
  - Large Kp (2.0): Steer hard, fast but jerky correction

**Problem with P-only**:
- Always leaves steady-state error
- Example: Heater can't quite reach 70°F, settles at 68°F

---

**Integral (I) Control**:
- Control action based on accumulated error over time
- Formula: `u = Ki × ∫e dt` (sum of all past errors)
- Eliminates steady-state error

**Example**: Filling a bathtub
- P-control alone might stop before completely full
- I-control remembers all past error, keeps adding water until full

**Problem with I-only**:
- Slow response
- Can cause overshoot (integrates too much error)

---

**Derivative (D) Control**:
- Control action based on rate of change of error
- Formula: `u = Kd × (de/dt)` (how fast error is changing)
- Provides damping (reduces overshoot)

**Example**: Braking a car
- See stop sign approaching:
  - P-control: Brake based on distance to stop
  - D-control: Brake harder if approaching fast, lighter if slowing down
  - Prevents overshoot (passing the stop line)

---

**PID Combined**:
```
u(t) = Kp·e(t) + Ki·∫e(t)dt + Kd·de(t)/dt
```

- **Kp**: How aggressively to respond to current error
- **Ki**: How much to correct accumulated past error
- **Kd**: How much to anticipate future error (damping)

**Tuning Trade-offs**:
- Increase Kp: Faster response, more overshoot
- Increase Ki: Eliminate steady-state error, slower, risk of overshoot
- Increase Kd: Reduce overshoot, smoother, sensitive to noise

**Interactive Demo**:

Try this PID simulator:
- [PID Simulator](http://www.pidlab.com/) or search "online PID simulator"

**Practice Exercise**:

```python
import numpy as np
import matplotlib.pyplot as plt

def simulate_pid(setpoint, Kp, Ki, Kd, duration=10):
    """Simulate simple PID control."""
    dt = 0.01
    t = np.arange(0, duration, dt)

    # System state
    position = 0.0
    velocity = 0.0

    # PID variables
    integral = 0.0
    previous_error = 0.0

    # Logging
    positions = []
    control_inputs = []

    for _ in t:
        # Error
        error = setpoint - position

        # PID terms
        P = Kp * error
        integral += error * dt
        I = Ki * integral
        derivative = (error - previous_error) / dt
        D = Kd * derivative

        # Control input
        u = P + I + D

        # Simple system dynamics (position update)
        # Assume: acceleration = control input / mass (mass = 1)
        acceleration = u
        velocity += acceleration * dt
        position += velocity * dt

        # Logging
        positions.append(position)
        control_inputs.append(u)

        previous_error = error

    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    ax1.plot(t, positions, label='Position')
    ax1.axhline(y=setpoint, color='r', linestyle='--', label='Setpoint')
    ax1.set_ylabel('Position')
    ax1.set_title('PID Control Simulation')
    ax1.legend()
    ax1.grid(True)

    ax2.plot(t, control_inputs, label='Control Input')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Control Input')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.show()

# Experiment with different gains
simulate_pid(setpoint=10, Kp=2.0, Ki=0.5, Kd=1.0)
```

Try different gains and observe:
1. Kp=10, Ki=0, Kd=0 (P-only)
2. Kp=10, Ki=2, Kd=0 (PI)
3. Kp=10, Ki=2, Kd=5 (PID)

**Resources**:
- [PID Control Explained (Video, 20 min)](https://www.youtube.com/results?search_query=pid+control+explained)
- [PID Without a PhD (Article)](https://www.wescottdesign.com/articles/pid/pidWithoutAPhd.pdf)

---

**Step 2: Why PID Isn't Enough for DIP (2 hours)**

**PID Works Well For**:
- Linear systems (response proportional to input)
- Smooth, continuous dynamics
- Small disturbances
- Examples: Cruise control, temperature control, motor speed control

**Double-Inverted Pendulum Challenges**:

1. **Highly Nonlinear**:
   - Small angle: Easy (sin(θ) ≈ θ)
   - Large angle: Chaotic (sin(θ) ≠ θ)
   - PID assumes linearity

2. **Unstable Equilibrium**:
   - Any tiny error grows exponentially without control
   - PID response might be too slow

3. **Underactuated**:
   - 1 input (cart force)
   - 3 outputs (cart position, θ₁, θ₂)
   - Complex coupling

4. **Fast Dynamics**:
   - Pendulum falls quickly if not controlled
   - Requires aggressive control

**Need for Advanced Control**:
- Sliding Mode Control (SMC)
- Model Predictive Control (MPC)
- Adaptive Control
- Robust Control

**This Project Uses SMC** because:
- Handles nonlinearity well
- Fast response
- Robust to uncertainties
- Finite-time convergence guarantees

**Resources**:
- [Limitations of PID (Article)](https://controlguru.com/limitations-of-pid-control/)
- [Why Advanced Control? (Video, 15 min)](https://www.youtube.com/results?search_query=advanced+control+methods)

---

### Self-Assessment: Phase 2.2

**Quiz**:

1. What do P, I, and D stand for in PID control?
2. Which PID term eliminates steady-state error?
3. Which PID term reduces overshoot?
4. Why isn't PID sufficient for the double-inverted pendulum?
5. Name two challenges specific to inverted pendulum control.

**If you can answer 4-5 correctly**: Move to Phase 2.3
**If you can answer 2-3 correctly**: Review PID concepts
**If you can answer 0-1 correctly**: Re-watch PID tutorial videos and try the simulator

</details>

---

<details>
<summary>2.3 Introduction to Sliding Mode Control</summary>

## Phase 2.3: Introduction to Sliding Mode Control (8 hours)

**Goal**: Understand what SMC is and why it works (intuitive, not mathematical proof yet).

### Learning Path

**Step 1: The Sliding Surface Concept (3 hours)**

**Core Idea of SMC**:
1. Define a "sliding surface" in state space
2. Drive the system TO the surface
3. Keep the system ON the surface
4. On the surface, system converges to desired state

**Analogy**: Sliding Down a Hill

Imagine a ball on a hill:
- **Goal**: Get ball to bottom of valley (desired state)
- **Problem**: Ball could roll in any direction
- **Solution**: Create a chute (sliding surface)
  - First, push ball into the chute
  - Once in chute, gravity slides it to bottom automatically

**The Sliding Surface**:

**State Space Representation**:

```{mermaid}
:alt: State space model showing how system states (position, velocity, angles, angular velocities) relate to each other and to control input
:align: center

%%{init: {'theme':'base', 'themeVariables': {'primaryColor':'#FFA500','primaryTextColor':'#fff','primaryBorderColor':'#FF8C00','lineColor':'#FF8C00','secondaryColor':'#FFE5CC','tertiaryColor':'#fff'}}}%%
graph LR
    A[Control Input<br/>Force F] --> B[System Dynamics]
    B --> C[State Vector<br/>x, ẋ, θ₁, θ̇₁, θ₂, θ̇₂]
    C --> D{Sliding Surface<br/>s = f states}
    D --> E[Error Signal]
    E --> F[Controller]
    F --> A

    style A fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
    style B fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
    style C fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
    style D fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
    style E fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
    style F fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
```

For double-inverted pendulum:
```
s = k₁·θ₁ + k₂·θ̇₁ + λ₁·θ₂ + λ₂·θ̇₂
```

- **s**: Sliding surface value
- **s = 0**: System is ON the sliding surface
- **s ≠ 0**: System is OFF the surface (needs correction)

**What This Means**:
- Sliding surface combines position (θ) and velocity (θ̇) errors
- Specific combination defined by gains (k₁, k₂, λ₁, λ₂)
- When s=0, angles AND velocities are in proper relationship to converge

**Two-Phase Process**:

1. **Reaching Phase** (s ≠ 0):
   - System far from surface
   - Control law aggressively drives toward surface
   - Goal: Make s --> 0

2. **Sliding Phase** (s = 0):
   - System on surface
   - Control maintains s ≈ 0
   - System "slides" along surface to equilibrium

**Visualization**:

```{mermaid}
:alt: SMC intuitive concept map showing the two-phase process - reaching phase drives system to sliding surface, sliding phase maintains system on surface toward equilibrium
:align: center

%%{init: {'theme':'base', 'themeVariables': {'primaryColor':'#FFA500','primaryTextColor':'#fff','primaryBorderColor':'#FF8C00','lineColor':'#FF8C00','secondaryColor':'#FFE5CC','tertiaryColor':'#fff'}}}%%
flowchart TD
    A[Start: System Off Surface<br/>s ≠ 0] --> B{Reaching Phase}
    B -->|Aggressive Control| C[Drive to Surface<br/>s --> 0]
    C --> D{On Surface?}
    D -->|No, s ≠ 0| B
    D -->|Yes, s = 0| E{Sliding Phase}
    E -->|Maintain s = 0| F[Slide to Equilibrium<br/>θ --> 0, θ̇ --> 0]
    F --> G{At Equilibrium?}
    G -->|No| E
    G -->|Yes| H[Goal Achieved<br/>Pendulums Upright]

    style A fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
    style B fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
    style C fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
    style D fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
    style E fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
    style F fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
    style G fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
    style H fill:#10b981,stroke:#059669,stroke-width:3px,color:#fff
```

**Example Trajectory**:

```python
import numpy as np
import matplotlib.pyplot as plt

# Simulate SMC driving system to sliding surface
t = np.linspace(0, 5, 500)

# Angle (approaches zero)
theta = 0.5 * np.exp(-1.5*t) * np.cos(3*t)

# Angular velocity (derivative of theta)
dtheta = np.gradient(theta, t)

# Sliding surface (s = theta + 0.5*dtheta)
s = theta + 0.5*dtheta

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10))

# Angle
ax1.plot(t, theta)
ax1.axhline(y=0, color='r', linestyle='--', label='Target')
ax1.set_ylabel('θ (rad)')
ax1.set_title('Pendulum Angle')
ax1.legend()
ax1.grid(True)

# Angular velocity
ax2.plot(t, dtheta)
ax2.axhline(y=0, color='r', linestyle='--', label='Target')
ax2.set_ylabel('dθ/dt (rad/s)')
ax2.set_title('Pendulum Angular Velocity')
ax2.legend()
ax2.grid(True)

# Sliding surface
ax3.plot(t, s)
ax3.axhline(y=0, color='g', linestyle='--', linewidth=2, label='Sliding Surface (s=0)')
ax3.fill_between(t, -0.05, 0.05, alpha=0.2, color='green', label='Sliding Region')
ax3.set_xlabel('Time (s)')
ax3.set_ylabel('s')
ax3.set_title('Sliding Surface Value')
ax3.legend()
ax3.grid(True)

plt.tight_layout()
plt.show()

print("Notice how:")
print("1. Sliding surface (s) converges to zero first")
print("2. Once s ≈ 0, system slides to equilibrium (theta-->0, dtheta-->0)")
```

**Practice Exercise**:
1. Why do we combine angle AND velocity in the sliding surface?
2. What happens if s > 0? What should control do?
3. What happens if s < 0? What should control do?

**Resources**:
- [Sliding Mode Control Intuition (Video, 15 min)](https://www.youtube.com/results?search_query=sliding+mode+control+explained)
- [SMC Basics (Article)](https://www.mathworks.com/help/control/ug/sliding-mode-control.html)

---

**Step 2: The Control Law (2 hours)**

**How to Drive to the Surface?**

**Ideal SMC Law** (Discontinuous):
```
u = -K · sign(s)
```

- If s > 0: u = -K (full force negative direction)
- If s < 0: u = +K (full force positive direction)
- If s = 0: Switch rapidly between ±K

**sign() Function**:
```
sign(x) = +1 if x > 0
sign(x) = -1 if x < 0
sign(x) =  0 if x = 0
```

**Why sign()?**
- Always pushes TOWARD the surface
- Maximum force when far from surface
- Guarantees finite-time convergence

**Problem: Chattering**

```
Control Signal with Pure Switching:
u
^
|  ___     ___     ___
| |   |   |   |   |   |
+-+---+---+---+---+---+---> time
|     |___|   |___|
|
```

- Rapid switching creates high-frequency oscillations
- Wears out actuators
- Causes noise and vibration
- Can excite unmodeled dynamics

**Solution: Boundary Layer**

**Smooth SMC Law** (Continuous):
```
u = -K · tanh(s / ε)
```

- ε (epsilon): Boundary layer width
- tanh: Smooth approximation to sign()
- When |s| > ε: Control ≈ ±K (full control)
- When |s| < ε: Control proportional to s (smooth)

**Tanh Function**:

```python
import numpy as np
import matplotlib.pyplot as plt

s = np.linspace(-2, 2, 1000)
epsilon_values = [0.1, 0.3, 1.0]

plt.figure(figsize=(10, 6))

for eps in epsilon_values:
    u = np.tanh(s / eps)
    plt.plot(s, u, label=f'ε = {eps}', linewidth=2)

# Compare with sign function
u_sign = np.sign(s)
plt.plot(s, u_sign, 'k--', label='sign(s)', linewidth=1.5, alpha=0.7)

plt.xlabel('Sliding Surface (s)', fontsize=12)
plt.ylabel('Control (normalized)', fontsize=12)
plt.title('Boundary Layer Effect: tanh(s/ε)', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
plt.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
plt.show()
```

**Trade-off**:
- Smaller ε: Closer to ideal SMC, more chattering
- Larger ε: Smoother control, larger steady-state error

**Practice Exercise**:
1. Why does sign() cause chattering?
2. How does tanh() reduce chattering?
3. What happens if ε is very large (ε = 10)?

**Resources**:
- [Chattering in SMC (Video, 10 min)](https://www.youtube.com/results?search_query=chattering+sliding+mode+control)
- [Boundary Layer Method (Article)](https://www.sciencedirect.com/topics/engineering/boundary-layer-control)

---

**Step 3: Why SMC Works for DIP (3 hours)**

**Advantages of SMC**:

1. **Robust to Uncertainties**:
   - Model mismatch? Still works!
   - Parameter variations? Compensates automatically!
   - Disturbances? Rejects effectively!

2. **Finite-Time Convergence**:
   - Reaches sliding surface in finite time (not just asymptotically)
   - Fast response

3. **Handles Nonlinearity**:
   - Doesn't assume system is linear
   - Works for large angle deviations

4. **Simple Implementation**:
   - Control law is algebraic (no integration needed)
   - Computationally efficient

**Why Perfect for Double-Inverted Pendulum**:

1. **Unstable System**:
   - SMC's aggressive initial response quickly stabilizes
   - Finite-time reaching prevents falling

2. **Nonlinear Dynamics**:
   - SMC doesn't require linearization
   - Works across full range of angles

3. **Model Uncertainty**:
   - Don't know exact friction? SMC compensates.
   - Parameter variations? SMC handles it.

4. **Disturbances**:
   - External pushes rejected automatically
   - Robust performance

**SMC Variants in This Project**:

1. **Classical SMC**:
   - Basic sliding mode with boundary layer
   - Good starting point

2. **Super-Twisting SMC (STA)**:
   - Second-order sliding mode
   - Continuous control (no chattering even without boundary layer!)
   - Smoother performance

3. **Adaptive SMC**:
   - Adapts gains online based on tracking error
   - Better for systems with large uncertainties

```{mermaid}
:alt: Adaptation mechanism flowchart showing how adaptive SMC adjusts controller gains based on tracking error in real-time
:align: center

%%{init: {'theme':'base', 'themeVariables': {'primaryColor':'#FFA500','primaryTextColor':'#fff','primaryBorderColor':'#FF8C00','lineColor':'#FF8C00','secondaryColor':'#FFE5CC','tertiaryColor':'#fff'}}}%%
flowchart TD
    A[Current State] --> B[Compute Error<br/>e = θ_desired - θ_actual]
    B --> C{Error Large?}
    C -->|Yes, e > threshold| D[Increase Gains<br/>k = k + Δk]
    C -->|No, e ≤ threshold| E[Decrease Gains<br/>k = k - Δk]
    D --> F[Apply Updated Control<br/>u = -k·sign s]
    E --> F
    F --> G[Update System State]
    G --> A

    style A fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
    style B fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
    style C fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
    style D fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
    style E fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
    style F fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
    style G fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
```

4. **Hybrid Adaptive STA-SMC**:
   - Combines adaptation with super-twisting
   - Best overall performance

**Visual Comparison**:

```python
import numpy as np
import matplotlib.pyplot as plt

t = np.linspace(0, 5, 500)

# Classical SMC response
theta_classical = 0.5 * np.exp(-1.2*t) * np.cos(3*t)

# STA-SMC response (smoother, faster)
theta_sta = 0.5 * np.exp(-1.5*t) * np.cos(3.5*t) * (1 - 0.2*np.exp(-2*t))

# Adaptive SMC response (slower initially, then fast)
theta_adaptive = 0.5 * np.exp(-t) * np.cos(2.5*t) * (1 + 0.5*np.exp(-3*t))

# Hybrid response (best)
theta_hybrid = 0.5 * np.exp(-1.8*t) * np.cos(4*t) * (1 - 0.1*np.exp(-2.5*t))

plt.figure(figsize=(12, 6))
plt.plot(t, theta_classical, label='Classical SMC', linewidth=2)
plt.plot(t, theta_sta, label='Super-Twisting', linewidth=2)
plt.plot(t, theta_adaptive, label='Adaptive SMC', linewidth=2)
plt.plot(t, theta_hybrid, label='Hybrid Adaptive STA', linewidth=2)
plt.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='Target')
plt.xlabel('Time (s)', fontsize=12)
plt.ylabel('Pendulum Angle (rad)', fontsize=12)
plt.title('Comparison of SMC Variants', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

print("Observations:")
print("- Classical: Good baseline, moderate oscillations")
print("- STA: Smoother, less chattering")
print("- Adaptive: Learns optimal gains over time")
print("- Hybrid: Best of both worlds")
```

**Resources**:
- [SMC for Inverted Pendulum (Video, 20 min)](https://www.youtube.com/results?search_query=sliding+mode+control+inverted+pendulum)
- [Super-Twisting Algorithm (Article)](https://www.sciencedirect.com/topics/engineering/super-twisting-algorithm)

---

### Self-Assessment: Phase 2.3

**Quiz**:

1. What is a sliding surface in SMC?
2. What are the two phases of SMC operation?
3. Why does the ideal SMC control law (with sign()) cause chattering?
4. How does the boundary layer reduce chattering?
5. Name two advantages of SMC for the double-inverted pendulum.

**Practical Understanding**:

Sketch (on paper or draw in software):
1. Phase portrait showing sliding surface and system trajectory converging to it
2. Plot showing chattering vs smooth control (with and without boundary layer)

**If you can complete the quiz and sketches**: Move to Phase 2.4
**If struggling with sliding surface concept**: Review Step 1 again
**If struggling with control law**: Review Step 2 and experiment with tanh vs sign

</details>

---

<details>
<summary>2.4 What is Optimization?</summary>

## Phase 2.4: What is Optimization? (6 hours)

**Goal**: Understand why manual controller tuning is tedious and how optimization algorithms like PSO help find better parameters automatically.

### What You'll Learn

- Why we need optimization for controller design
- Manual tuning vs automated optimization
- What PSO (Particle Swarm Optimization) does
- Basic concepts: objective functions, constraints, convergence

### Learning Path

**Step 1: The Manual Tuning Problem (2 hours)**

**Scenario**: You have a controller with 6 gains to tune for the double-inverted pendulum:

```python
# Classical SMC gains (6 parameters!)
gains = [k1, k2, k3, k4, k5, eta]

# Example values
gains = [10.0, 5.0, 8.0, 3.0, 15.0, 2.0]
```

**The Challenge**:
- Each gain affects performance differently
- Changing one gain may require retuning others
- Too low: system unstable, pendulum falls
- Too high: excessive control effort, chattering
- Just right: smooth stabilization, minimal energy

**Manual Tuning Process**:
1. Start with initial guess: `[1, 1, 1, 1, 1, 1]`
2. Run simulation --> Pendulum falls --> Increase k1
3. Run again --> Still unstable --> Increase k3
4. Run again --> Now chattering --> Reduce eta
5. Run again --> Better but oscillates --> Adjust k2
6. Repeat steps 2-5 for hours...

**Why This is Tedious**:
- 6 parameters = potentially thousands of combinations
- Each simulation takes 10-30 seconds to run and analyze
- No guarantee you found the BEST gains
- Hard to balance multiple objectives (speed + smoothness + low chattering)

**Try This** (thought experiment):
Imagine you have just 3 gains, each can be 1-20. That's 20×20×20 = 8,000 combinations. If each simulation takes 15 seconds, testing all combinations would take 33 hours!

---

**Step 2: What is an Optimization Problem? (2 hours)**

**Formal Definition**:
Optimization means finding the "best" solution from all possible solutions, according to some criterion.

**Components**:

1. **Decision Variables**: What you can change
   - For us: Controller gains `[k1, k2, k3, k4, k5, eta]`

2. **Objective Function**: What you want to optimize
   - For us: Minimize settling time, overshoot, control effort, chattering
   - Often combined into a single "cost" or "fitness" function

3. **Constraints**: Limits on decision variables
   - For us: Gains must be positive (k > 0)
   - May have upper bounds (e.g., k < 100)

4. **Optimal Solution**: The values of decision variables that give the best objective function value

**Example Objective Function**:

```python
def performance_metric(gains):
    """
    Evaluate controller performance with given gains.
    Lower is better.
    """
    # Run simulation with these gains
    results = run_simulation(controller_gains=gains)

    # Extract performance metrics
    settling_time = results['settling_time']  # How fast it stabilizes (seconds)
    overshoot = results['overshoot']          # How much it overshoots target (rad)
    control_effort = results['control_effort'] # Energy used (J)
    chattering = results['chattering_index']  # Oscillation measure

    # Combine into single score (weighted sum)
    cost = (
        2.0 * settling_time +      # Weight: faster is better
        5.0 * overshoot +           # Weight: less overshoot critical
        0.1 * control_effort +      # Weight: energy less important
        3.0 * chattering            # Weight: smoothness important
    )

    return cost  # Lower cost = better performance
```

**Visualization**:

```{mermaid}
:alt: Optimization space landscape showing cost function with multiple local minima and global minimum, representing search for optimal controller gains
:align: center

%%{init: {'theme':'base', 'themeVariables': {'primaryColor':'#FFA500','primaryTextColor':'#fff','primaryBorderColor':'#FF8C00','lineColor':'#FF8C00','secondaryColor':'#FFE5CC','tertiaryColor':'#fff'}}}%%
graph TD
    A[Parameter Space<br/>k1, k2, ..., k6] --> B{Run Simulation}
    B --> C[Performance Metrics]
    C --> D[Settling Time]
    C --> E[Overshoot]
    C --> F[Control Effort]
    C --> G[Chattering]
    D --> H[Cost Function]
    E --> H
    F --> H
    G --> H
    H --> I{Minimize Cost}
    I -->|Search Algorithm| A

    style A fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
    style B fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
    style C fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
    style H fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
    style I fill:#10b981,stroke:#059669,stroke-width:3px,color:#fff
```

**Goal of Optimization**: Find the valley (minimum cost) in this multi-dimensional landscape.

---

**Step 3: Introduction to PSO (Particle Swarm Optimization) (2 hours)**

**What is PSO?**
- Bio-inspired algorithm based on bird flocking or fish schooling
- Uses "particles" (candidate solutions) that explore the search space
- Particles share information to converge on optimal solution

**How PSO Works** (simplified):

1. **Initialization**:
   - Create swarm of particles (e.g., 30 particles)
   - Each particle = random set of gains
   - Example particles:
     - Particle 1: [12, 8, 10, 5, 18, 3]
     - Particle 2: [5, 15, 6, 8, 10, 1.5]
     - ... (28 more)

2. **Evaluation**:
   - Run simulation for each particle's gains
   - Calculate cost (performance metric)
   - Track best particle so far (global best)
   - Track each particle's personal best

3. **Update**:
   - Particles "fly" toward their personal best
   - Particles "fly" toward global best
   - Add randomness to explore new areas
   - Update each particle's position (gains)

4. **Iteration**:
   - Repeat steps 2-3 for many generations (e.g., 50 iterations)
   - Particles converge on optimal region

5. **Result**:
   - Global best after all iterations = optimized gains

**Analogy**: Imagine 30 friends searching for gold in a mountain range. Each person:
- Remembers where they found the most gold (personal best)
- Knows where the group found the most gold overall (global best)
- Moves toward their best spot and the group's best spot
- Explores randomly to avoid getting stuck in local hills
- Eventually, everyone converges near the richest gold vein (global optimum)

**PSO Pseudocode**:

```python
# Initialize swarm
swarm = create_random_particles(num_particles=30, num_dims=6)
velocities = zeros(30, 6)
personal_best = swarm.copy()
global_best = find_best_particle(swarm)

# Optimization loop
for iteration in range(50):  # 50 generations
    for i, particle in enumerate(swarm):
        # Evaluate performance
        cost = performance_metric(particle)

        # Update personal best
        if cost < cost_of(personal_best[i]):
            personal_best[i] = particle

        # Update global best
        if cost < cost_of(global_best):
            global_best = particle

        # Update velocity (movement direction)
        velocities[i] = (
            0.5 * velocities[i] +                          # Inertia
            1.5 * rand() * (personal_best[i] - particle) +  # Cognitive
            1.5 * rand() * (global_best - particle)         # Social
        )

        # Update position
        swarm[i] = particle + velocities[i]
        swarm[i] = clip(swarm[i], min_bounds, max_bounds)  # Stay in valid range

print(f"Optimal gains found: {global_best}")
```

**Why PSO for Controller Tuning?**
- Handles multi-dimensional search spaces well (6+ parameters)
- Doesn't require gradient information (simulation is black box)
- Explores globally (avoids local minima)
- Relatively fast convergence (compared to random search)
- Easy to parallelize (evaluate particles simultaneously)

**Typical Results**:
- Manual tuning: 2-4 hours, suboptimal gains
- PSO optimization: 10-20 minutes (automated), near-optimal gains

---

### Self-Assessment: Phase 2.4

**Quiz**:

1. Why is manual controller tuning tedious for systems with many parameters?
2. What are the three main components of an optimization problem?
3. What is an objective function (cost function)?
4. How does PSO use a "swarm" to find optimal solutions?
5. Why is PSO suitable for controller gain tuning?

**Practical Exercise**:

Imagine a simple 2-parameter optimization:
```python
def f(x, y):
    return (x - 3)**2 + (y + 2)**2
```

What are the optimal values of x and y that minimize f(x, y)? (Hint: The minimum of (x-a)² is at x=a)

**If you can complete the quiz**: Move to Phase 2.5
**If struggling with optimization concept**: Review Step 2, try sketching cost landscapes
**If struggling with PSO**: Review the bird flock analogy, watch PSO visualization videos

**Resources**:
- [PSO Visualization (Video, 5 min)](https://www.youtube.com/results?search_query=particle+swarm+optimization+visualization)
- [Optimization Crash Course (Article)](https://www.w3schools.com/python/python_ml_optimization.asp)

</details>

---

<details>
<summary>2.5 Understanding the DIP System</summary>

## Phase 2.5: Understanding the DIP System (5 hours)

**Goal**: Understand the specific control problem we're solving - why the double-inverted pendulum is challenging and how it relates to real-world systems.

### What You'll Learn

- Physical structure of the double-inverted pendulum (DIP)
- Why DIP is "harder" than single pendulum
- Real-world applications (rockets, bipedal robots)
- System dynamics (qualitative understanding)
- Control objectives and challenges

### Learning Path

**Step 1: What is a Double-Inverted Pendulum? (1.5 hours)**

**Physical Description**:

The system consists of:
1. **Cart**: Moves left-right on a track (controlled)
2. **First Pendulum**: Hinged to cart, swings freely
3. **Second Pendulum**: Hinged to tip of first pendulum, swings freely
4. **Control Input**: Horizontal force applied to cart

**System Block Diagram**:

```{mermaid}
:alt: Control system block diagram for double-inverted pendulum showing sensor feedback, controller computation, and plant dynamics
:align: center

%%{init: {'theme':'base', 'themeVariables': {'primaryColor':'#FFA500','primaryTextColor':'#fff','primaryBorderColor':'#FF8C00','lineColor':'#FF8C00','secondaryColor':'#FFE5CC','tertiaryColor':'#fff'}}}%%
flowchart LR
    A[Reference<br/>θ1=0, θ2=0] -->|+| B((Error<br/>Computation))
    B --> C[SMC Controller<br/>Gains: k1-k6]
    C --> D[Force F<br/>-20 to +20 N]
    D --> E[DIP Plant<br/>Cart + 2 Pendulums]
    E --> F[States<br/>x, θ1, θ2, velocities]
    F -->|Sensors| B

    G[Disturbances<br/>External forces] -.-> E

    style A fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
    style B fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
    style C fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
    style D fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
    style E fill:#FFE5CC,stroke:#FF8C00,stroke-width:2px
    style F fill:#FFA500,stroke:#FF8C00,stroke-width:2px,color:#fff
```

**Why "Double"?**
- Two pendulums stacked on top of each other
- Both must be balanced upright simultaneously
- Much harder than balancing a single pendulum

**Why "Inverted"?**
- Natural (stable) position: pendulums hang downward (like a regular pendulum)
- Goal: Keep both upright (unstable equilibrium, like balancing a broomstick)

**Analogy**:
- Single pendulum: Balancing a broomstick on your hand
- Double pendulum: Balancing a broomstick with another broomstick taped to its top

**Key Parameters** (typical values):
- Cart mass: M = 1.0 kg
- Pendulum 1 mass: m1 = 0.1 kg, length: L1 = 0.5 m
- Pendulum 2 mass: m2 = 0.1 kg, length: L2 = 0.5 m
- Gravity: g = 9.81 m/s²
- Control force: F ∈ [-20, 20] Newtons

---

**Step 2: Why is DIP Challenging? (1.5 hours)**

**Challenge 1: Nonlinear Dynamics**
- Equations of motion involve sin(θ), cos(θ), θ² terms
- No simple linear relationship between force and angles
- Small-angle approximation (sin θ ≈ θ) breaks down for large swings

**Challenge 2: Underactuated System**
- 1 control input (force F)
- 3 degrees of freedom (cart position, θ1, θ2)
- Underactuated: More things to control than control inputs available

**Challenge 3: Unstable Equilibrium**
- Upright position (θ1=0, θ2=0) is inherently unstable
- Like balancing on a knife edge - any disturbance grows exponentially
- Without control, pendulums fall within ~0.5 seconds

**Challenge 4: Coupling**
- Moving the cart affects both pendulums
- Moving pendulum 1 affects pendulum 2
- Moving pendulum 2 affects pendulum 1 and cart
- Complex interactions make control difficult

**Challenge 5: Model Uncertainty**
- Real system has friction (not perfectly modeled)
- Masses/lengths have measurement errors
- Controller must be robust to these uncertainties

**Comparison to Single Inverted Pendulum**:

| Property | Single Pendulum | Double Pendulum |
|----------|-----------------|-----------------|
| DOF (Degrees of Freedom) | 2 (cart, θ) | 3 (cart, θ1, θ2) |
| Equilibria | 1 unstable | 2 unstable |
| Nonlinearity | Moderate | High |
| Coupling | Simple | Complex |
| Control Difficulty | Medium | Hard |
| Settling Time | ~2 seconds | ~5-10 seconds |

**Why Study DIP?**
- Benchmark problem in control theory research
- Tests controller robustness and performance
- Simpler than real-world systems but captures key challenges
- Success on DIP --> Confidence for robotics/aerospace applications

---

**Step 3: Real-World Applications (1 hour)**

**Where do similar control problems appear?**

1. **Rocket Landing** (SpaceX Falcon 9)
   - Rocket is like inverted pendulum (tall, unstable)
   - Thrust control keeps rocket upright during landing
   - Multiple stages = multiple pendulums
   - SMC-like algorithms used in practice

2. **Humanoid/Bipedal Robots**
   - Walking robot has many inverted pendulum modes
   - Legs, torso, arms = coupled pendulums
   - Balance control while walking
   - Honda ASIMO, Boston Dynamics Atlas use advanced control

3. **Segway Personal Transporter**
   - Person + Segway = inverted pendulum
   - Gyroscope sensors detect tilt
   - Wheel motors provide control torque
   - Maintains balance dynamically

4. **Satellite Attitude Control**
   - Satellite orientation in space (no ground support)
   - Reaction wheels provide control torque
   - Must point antennas/cameras precisely
   - Similar underactuated control problem

5. **Ship Stabilization**
   - Ship in waves = pendulum-like rolling motion
   - Fins/ballast tanks provide control
   - Reduce rolling for passenger comfort

**Common Threads**:
- Unstable equilibrium (must actively stabilize)
- Underactuated (fewer controls than DOF)
- Nonlinear dynamics
- Real-time control required
- Robustness to disturbances critical

---

**Step 4: System Dynamics (Qualitative) (1 hour)**

**State Variables**:

The system state has 6 variables:
1. Cart position: x (meters)
2. Cart velocity: ẋ (m/s)
3. Pendulum 1 angle: θ1 (radians)
4. Pendulum 1 angular velocity: θ̇1 (rad/s)
5. Pendulum 2 angle: θ2 (radians)
6. Pendulum 2 angular velocity: θ̇2 (rad/s)

**State Vector**:
```python
state = [x, x_dot, theta1, theta1_dot, theta2, theta2_dot]
```

**Dynamics** (conceptual, not full equations):

The equations of motion describe how the state changes over time:

```
ẍ = f1(x, ẋ, θ1, θ̇1, θ2, θ̇2, F)       # Cart acceleration
θ̈1 = f2(x, ẋ, θ1, θ̇1, θ2, θ̇2, F)      # Pendulum 1 angular acceleration
θ̈2 = f3(x, ẋ, θ1, θ̇1, θ2, θ̇2, F)      # Pendulum 2 angular acceleration
```

These functions f1, f2, f3 are derived from physics (Lagrangian mechanics) and involve:
- Masses (M, m1, m2)
- Lengths (L1, L2)
- Gravity (g)
- Trigonometric terms (sin θ, cos θ)
- Cross-coupling terms (θ1 affects θ2 and vice versa)

**You don't need to memorize the equations**. The key insight:
- Control force F affects all three accelerations
- Changes in θ1 affect θ2 (and vice versa)
- System is highly coupled and nonlinear

**Simulation**:
The simulation numerically integrates these equations:
1. Start with initial state (e.g., θ1 = 0.1 rad, others = 0)
2. Compute accelerations using f1, f2, f3
3. Update velocities: θ̇1 += θ̈1 * dt
4. Update positions: θ1 += θ̇1 * dt
5. Repeat for T=10 seconds

**Control Objective**:
Design F(state) such that:
- θ1 --> 0 (pendulum 1 upright)
- θ2 --> 0 (pendulum 2 upright)
- x --> 0 (cart returns to center)
- All velocities --> 0 (system at rest)

---

### Self-Assessment: Phase 2.5

**Quiz**:

1. What are the three main components of the double-inverted pendulum system?
2. Why is the DIP harder to control than a single pendulum?
3. Name two real-world systems that have similar control challenges.
4. How many state variables does the DIP have?
5. What is the control objective for the DIP?

**Practical Understanding**:

Sketch (on paper):
1. The DIP system with cart, two pendulums, and force F
2. A graph showing how θ1 might evolve over time with and without control

**If you can complete the quiz and sketches**: Move to Phase 3
**If struggling with DIP structure**: Review Step 1, watch DIP videos
**If struggling with why it's hard**: Review Challenge 1-5 in Step 2

**Resources**:
- [Double Inverted Pendulum Simulation (Video, 3 min)](https://www.youtube.com/results?search_query=double+inverted+pendulum+simulation)
- [Real Segway Control (Video, 5 min)](https://www.youtube.com/results?search_query=segway+balance+control)
- [SpaceX Rocket Landing (Video, 10 min)](https://www.youtube.com/results?search_query=spacex+falcon+landing+control)

</details>

---


## Learning Resources

```{grid} 1 2 3
:gutter: 2

```{grid-item-card} YouTube: Control Theory & SMC
:link: https://www.youtube.com/results?search_query=control+theory+basics+sliding+mode
:link-type: url
:text-align: center

Watch video tutorials on control theory and SMC fundamentals
[View -->]

```

```{grid-item-card} Article: PID and SMC Concepts
:link: https://en.wikipedia.org/wiki/Sliding_mode_control
:link-type: url
:text-align: center

Read detailed explanations of feedback control and SMC
[Read -->]

```

```{grid-item-card} Interactive Quiz
:link: #self-assessment-phase-25
:link-type: url
:text-align: center

Test your understanding of Phase 2 control concepts
[Take Quiz -->]

```

```{grid-item-card} 🧪 Python for Scientists - Interactive Tutorial
:link: https://www.learnpython.org/
:link-type: url
:class-card: resource-card resource-interactive
:shadow: md
:text-align: center

Free interactive Python tutorial for everyone. Learn Python directly in your browser with hands-on exercises.
📊 *Estimated Time:* 20 min | 🎯 *Level:* Beginner
[View -->]

```

```{grid-item-card} 📖 NumPy Fundamentals - Official Guide
:link: https://numpy.org/doc/stable/user/absolute_beginners.html
:link-type: url
:class-card: resource-card resource-article
:shadow: md
:text-align: center

Official NumPy documentation guide for absolute beginners. Covers arrays, indexing, and scientific computing.
📊 *Estimated Time:* 45 min | 🎯 *Level:* Intermediate
[Read -->]

```

```{grid-item-card} 🎥 Control Systems Introduction - MIT OCW
:link: https://ocw.mit.edu/courses/2-04a-systems-and-controls-spring-2013/
:link-type: url
:class-card: resource-card resource-video
:shadow: md
:text-align: center

MIT OpenCourseWare course on linear systems, transfer functions, and Laplace transforms. Free lecture notes available.
📊 *Estimated Time:* 60 min | 🎯 *Level:* Beginner
[Watch -->]

```

```{grid-item-card} 🛠️ Python REPL - Browser Practice
:link: https://www.pythonmorsels.com/repl/
:link-type: url
:class-card: resource-card resource-tool
:shadow: md
:text-align: center

Free in-browser Python REPL with no sign-up required. Practice Python immediately with instant code execution.
📊 *Estimated Time:* 15 min | 🎯 *Level:* Hands-on
[Try It -->]

```
```

---
## Phase 2 Complete!

**Achievement Unlocked**: Control Theory Scholar

You've completed **Phase 2: Core Concepts** (~30 hours)!

You now understand:
- Control theory fundamentals
- Feedback and PID concepts
- Sliding mode control basics
- Optimization with PSO
- The double-inverted pendulum problem

**Next Phase**: [Phase 3: Hands-On Learning -->](phase-3-hands-on.md)

---

**Navigation:**
- <--[Phase 1: Foundations](phase-1-foundations.md)
- **Next**: [Phase 3: Hands-On Learning](phase-3-hands-on.md) -->
- [<--Back to Beginner Roadmap](../beginner-roadmap.md)

---

## Navigation

[<--Phase 1: Foundations](phase-1-foundations.md) | [Back to Roadmap](../beginner-roadmap.md) | [Phase 3: Hands-On -->](phase-3-hands-on.md)
