<!-- AUTO-GENERATED from .project/ai/edu/ - DO NOT EDIT DIRECTLY -->
<!-- Source: .project/ai/edu/phase1/physics-foundations.md -->
<!-- Generated: 2025-11-11 13:29:26 -->

# Physics Foundations - Understanding the Pendulum System

**Time Required**: 8-10 hours
**Prerequisites**: Basic algebra, `python-fundamentals.md` (for simulations)

------

## What You'll Learn

By the end of this module, you'll understand:
- Newton's laws and how they govern motion
- Forces, torque, and rotational motion
- Energy conservation in mechanical systems
- The physics of pendulums (single and double inverted)
- How to translate physics equations into code

------

## 1. Newton's Laws of Motion

### First Law: Inertia

**Statement**: An object at rest stays at rest, and an object in motion stays in motion at constant velocity, unless acted upon by a force.

**Example**: A book on a table stays there until you push it. A hockey puck on ice keeps sliding until friction stops it.

**Key Insight**: Things naturally resist changes in their motion.

### Second Law: F = ma

**Statement**: Force equals mass times acceleration.

```
F = m × a
```

Where:
- `F` = Force (Newtons, N)
- `m` = Mass (kilograms, kg)
- `a` = Acceleration (meters/second², m/s²)

**Example**: Pushing a shopping cart
- Light cart (small m): easy to accelerate (large a)
- Heavy cart (large m): hard to accelerate (small a)

**Rearranging**:
```
a = F / m
```

If you know the force and mass, you can calculate the acceleration.

### Third Law: Action-Reaction

**Statement**: For every action, there is an equal and opposite reaction.

**Example**: When you push a wall, it pushes back with the same force. When a rocket expels gas downward, the gas pushes the rocket upward.

------

## 2. Kinematics: Describing Motion

### Position, Velocity, Acceleration

**Position (x)**: Where an object is located (meters, m)

**Velocity (v)**: How fast position changes (m/s)
```
v = dx/dt  (derivative of position with respect to time)
```

**Acceleration (a)**: How fast velocity changes (m/s²)
```
a = dv/dt = d²x/dt²  (derivative of velocity)
```

### Example: Falling Object

```python
import numpy as np
import matplotlib.pyplot as plt

# Constants
g = 9.81  # gravity (m/s²)
v0 = 0    # initial velocity
y0 = 100  # initial height (m)

# Time array
t = np.linspace(0, 4.5, 100)

# Kinematic equations
y = y0 + v0 * t - 0.5 * g * t**2  # position
v = v0 - g * t                     # velocity

# Plot
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(t, y)
plt.xlabel("Time (s)")
plt.ylabel("Height (m)")
plt.title("Position vs Time")
plt.grid()

plt.subplot(1, 2, 2)
plt.plot(t, v)
plt.xlabel("Time (s)")
plt.ylabel("Velocity (m/s)")
plt.title("Velocity vs Time")
plt.grid()

plt.tight_layout()
plt.show()
```

------

## 3. Forces

### Types of Forces

**Gravity**: Pulls objects toward Earth
```
F_gravity = m × g  (where g = 9.81 m/s²)
```

**Normal Force**: Surface pushes back on object
- Book on table: normal force = weight (balances gravity)

**Friction**: Opposes motion
```
F_friction = μ × F_normal
```
Where `μ` (mu) is the coefficient of friction.

**Tension**: Force in a rope or cable

**Spring Force**: Hooke's law
```
F_spring = -k × x
```
Where `k` is the spring constant and `x` is displacement.

### Free Body Diagrams

A **free body diagram** shows all forces acting on an object.

Example: Block on a ramp
```
     Normal Force ↑
                  |
                  |
    ______________|
   /|            /
  / |           /
 /  |Weight    /
/   ↓         /
/____________/
```

------

## 4. Rotational Motion

### Angular Quantities

| Linear | Angular | Relationship |
|--------|---------|--------------|
| Position (x) | Angle (θ) | x = r × θ |
| Velocity (v) | Angular velocity (ω) | v = r × ω |
| Acceleration (a) | Angular accel (α) | a = r × α |
| Mass (m) | Moment of inertia (I) | I = Σ(m × r²) |
| Force (F) | Torque (τ) | τ = r × F |

### Torque: Rotational Force

**Definition**: Torque is the rotational equivalent of force.

```
τ = r × F × sin(θ)
```

Where:
- `τ` (tau) = Torque (N⋅m)
- `r` = Distance from pivot point (m)
- `F` = Force (N)
- `θ` = Angle between r and F

**Perpendicular Force** (θ = 90°):
```
τ = r × F
```

**Example**: Opening a door
- Push at the edge (large r): easy to open (large τ)
- Push near the hinge (small r): hard to open (small τ)

### Rotational Newton's Second Law

```
τ = I × α
```

Where:
- `I` = Moment of inertia (kg⋅m²)
- `α` = Angular acceleration (rad/s²)

**Rearranging**:
```
α = τ / I
```

------

## 5. Moment of Inertia

### What is Moment of Inertia?

Moment of inertia (I) is rotational mass. It tells you how hard it is to rotate an object.

**For a Point Mass**:
```
I = m × r²
```

**For Common Shapes**:
- Thin rod (axis through center): `I = (1/12) × m × L²`
- Thin rod (axis at end): `I = (1/3) × m × L²`
- Solid disk: `I = (1/2) × m × R²`
- Thin hoop: `I = m × R²`

### Parallel Axis Theorem

If you know I about the center of mass, you can find I about a parallel axis:

```
I_parallel = I_cm + m × d²
```

Where `d` is the distance between the axes.

------

## 6. Energy and Momentum

### Kinetic Energy

**Linear**:
```
KE = (1/2) × m × v²
```

**Rotational**:
```
KE_rot = (1/2) × I × ω²
```

**Total Energy** (for rotating object):
```
E = (1/2) × m × v² + (1/2) × I × ω²
```

### Potential Energy

**Gravitational**:
```
PE = m × g × h
```

Where `h` is height above reference point.

### Conservation of Energy

In the absence of friction:
```
E_initial = E_final
KE_i + PE_i = KE_f + PE_f
```

**Example**: Pendulum swinging
- At highest point: all PE, no KE
- At lowest point: all KE, no PE
- Total energy stays constant

------

## 7. The Simple Pendulum

### Setup

A simple pendulum is a mass (bob) attached to a massless rod or string, swinging under gravity.

```
      |
      |  Length L
      |
      o  Mass m
```

### Equation of Motion

Using torque = I × α:

```
τ = -m × g × L × sin(θ)
I = m × L²
α = d²θ/dt²

Therefore:
m × L² × (d²θ/dt²) = -m × g × L × sin(θ)

Simplifying:
d²θ/dt² = -(g/L) × sin(θ)
```

### Small Angle Approximation

For small angles (θ < 10°), `sin(θ) ≈ θ` (in radians), so:

```
d²θ/dt² ≈ -(g/L) × θ
```

This is a simple harmonic oscillator with period:

```
T = 2π × sqrt(L/g)
```

### Python Simulation

```python
import numpy as np
import matplotlib.pyplot as plt

def simulate_pendulum(theta0, L, t_max, dt):
    """
    Simulate simple pendulum using Euler method.

    Args:
        theta0: Initial angle (radians)
        L: Length (m)
        t_max: Simulation time (s)
        dt: Time step (s)
    """
    g = 9.81

    # Initialize arrays
    t = np.arange(0, t_max, dt)
    theta = np.zeros_like(t)
    omega = np.zeros_like(t)

    theta[0] = theta0

    # Euler integration
    for i in range(len(t) - 1):
        alpha = -(g / L) * np.sin(theta[i])
        omega[i + 1] = omega[i] + alpha * dt
        theta[i + 1] = theta[i] + omega[i + 1] * dt

    return t, theta, omega

# Simulate
t, theta, omega = simulate_pendulum(
    theta0=np.radians(30),  # 30 degrees
    L=1.0,
    t_max=10,
    dt=0.01
)

# Plot
plt.figure(figsize=(10, 6))
plt.plot(t, np.degrees(theta))
plt.xlabel("Time (s)")
plt.ylabel("Angle (degrees)")
plt.title("Simple Pendulum Motion")
plt.grid()
plt.show()
```

------

## 8. The Inverted Pendulum

### What's Different?

A regular pendulum hangs down (stable). An inverted pendulum balances upright (unstable).

```
Regular:        Inverted:
   |               o
   o               |
```

### Why is it Unstable?

**Equilibrium Points**:
- Regular pendulum: θ = 0 (hanging down) is **stable**
  - Small perturbation → restoring force → returns to equilibrium
- Inverted pendulum: θ = 0 (upright) is **unstable**
  - Small perturbation → amplifying force → falls over

### Control Problem

To keep an inverted pendulum upright, you must:
1. **Measure** the angle θ and angular velocity ω
2. **Calculate** the required force/torque
3. **Apply** the control input quickly

This is the essence of **control theory**.

------

## 9. The Double Inverted Pendulum

### System Description

Two rods connected end-to-end, balanced upright on a cart.

```
        o  (mass m2, length L2)
        |
        o  (mass m1, length L1)
        |
    [===cart===]
```

### State Variables

To fully describe the system, we need:
- Cart position: x
- Cart velocity: ẋ (x-dot)
- Lower pendulum angle: θ1
- Lower pendulum angular velocity: ω1
- Upper pendulum angle: θ2
- Upper pendulum angular velocity: ω2

**Total**: 6 state variables

### Why is it Hard to Control?

- **Highly nonlinear**: sin(θ), cos(θ) terms
- **Coupled**: moving one pendulum affects the other
- **Underactuated**: 1 control input (cart force), 2 pendulums to balance
- **Unstable**: both upright positions are unstable equilibria

------

## 10. Equations of Motion (Simplified)

For a single inverted pendulum on a cart:

```
(M + m) × ẍ + m × L × θ̈ × cos(θ) - m × L × θ̇² × sin(θ) = F

m × L² × θ̈ + m × L × ẍ × cos(θ) - m × g × L × sin(θ) = 0
```

Where:
- M = cart mass
- m = pendulum mass
- L = pendulum length
- F = control force on cart
- θ = pendulum angle
- Dots indicate time derivatives

### Linearization (Small Angles)

For small angles (θ ≈ 0):
- sin(θ) ≈ θ
- cos(θ) ≈ 1
- θ̇² ≈ 0

This simplifies the equations to linear form, which is easier to analyze and control.

------

## 11. Damping and Friction

### Damping Force

Damping opposes motion, proportional to velocity:

```
F_damping = -b × v
```

Where `b` is the damping coefficient.

### Effect on Pendulum

Without damping, a pendulum swings forever (conservation of energy).

With damping, it gradually loses energy and comes to rest.

```python
# Adding damping to simulation
def simulate_damped_pendulum(theta0, L, b, t_max, dt):
    g = 9.81
    m = 1.0  # mass

    t = np.arange(0, t_max, dt)
    theta = np.zeros_like(t)
    omega = np.zeros_like(t)

    theta[0] = theta0

    for i in range(len(t) - 1):
        # Torque from gravity and damping
        tau = -m * g * L * np.sin(theta[i]) - b * omega[i]
        I = m * L**2
        alpha = tau / I

        omega[i + 1] = omega[i] + alpha * dt
        theta[i + 1] = theta[i] + omega[i + 1] * dt

    return t, theta, omega
```

------

## 12. Coordinate Systems

### Cartesian Coordinates (x, y)

Standard 2D coordinates:
- x: horizontal position
- y: vertical position

### Polar Coordinates (r, θ)

Useful for rotational systems:
- r: distance from origin
- θ: angle from horizontal

**Conversion**:
```
x = r × cos(θ)
y = r × sin(θ)

r = sqrt(x² + y²)
θ = atan2(y, x)
```

### Pendulum Position

If pivot is at origin, bob position is:
```
x = L × sin(θ)
y = -L × cos(θ)  (negative because hanging down)
```

------

## 13. Numerical Integration Methods

### Euler Method (Simple, Inaccurate)

```python
# Next state = current state + derivative * dt
theta_next = theta + omega * dt
omega_next = omega + alpha * dt
```

**Pros**: Easy to implement
**Cons**: Accumulates error, energy drifts

### Runge-Kutta 4 (RK4) (Accurate)

```python
def rk4_step(f, t, y, dt):
    """
    One step of RK4 integration.
    f: derivative function (dy/dt = f(t, y))
    t: current time
    y: current state
    dt: time step
    """
    k1 = f(t, y)
    k2 = f(t + dt/2, y + k1 * dt/2)
    k3 = f(t + dt/2, y + k2 * dt/2)
    k4 = f(t + dt, y + k3 * dt)

    y_next = y + (k1 + 2*k2 + 2*k3 + k4) * dt / 6
    return y_next
```

**Pros**: Much more accurate
**Cons**: More complex

**This project uses RK4 for simulation.**

------

## 14. Phase Space

### What is Phase Space?

A plot of position vs. velocity (or angle vs. angular velocity) shows the system's behavior.

```python
# Phase space plot for pendulum
plt.figure()
plt.plot(theta, omega)
plt.xlabel("Angle (rad)")
plt.ylabel("Angular Velocity (rad/s)")
plt.title("Phase Space Portrait")
plt.grid()
plt.show()
```

### Interpretation

- **Closed loops**: Periodic motion (pendulum swinging)
- **Spiral inward**: Damped oscillation (energy loss)
- **Fixed point**: Equilibrium (pendulum at rest)

------

## 15. Practical Insights for Control

### Sensing

To control a pendulum, you need to measure:
- **Angle**: Using encoders, IMUs, or cameras
- **Angular velocity**: Direct measurement or numerical derivative

### Actuation

Apply control force via:
- **Motor on cart**: Moves cart left/right
- **Motor at pivot**: Directly applies torque to pendulum

### Real-World Challenges

- **Sensor noise**: Measurements aren't perfect
- **Actuator limits**: Motors have max force/torque
- **Time delays**: Measurement → computation → actuation takes time
- **Modeling errors**: Real system ≠ simulation

------

## 16. Practice Exercises

### Exercise 1: Verify Period Formula

```python
# Measure pendulum period and compare to theory
import numpy as np
import matplotlib.pyplot as plt

def find_period(t, theta):
    """Find period by detecting zero crossings."""
    # Find indices where theta crosses zero (downward)
    crossings = []
    for i in range(len(theta) - 1):
        if theta[i] > 0 and theta[i+1] <= 0:
            crossings.append(t[i])

    # Period is time between crossings
    if len(crossings) >= 2:
        periods = np.diff(crossings)
        return np.mean(periods)
    return None

# Simulate and measure
L = 1.0
t, theta, omega = simulate_pendulum(
    theta0=np.radians(10),
    L=L,
    t_max=20,
    dt=0.001
)

measured_period = find_period(t, theta)
theoretical_period = 2 * np.pi * np.sqrt(L / 9.81)

print(f"Measured: {measured_period:.4f} s")
print(f"Theoretical: {theoretical_period:.4f} s")
print(f"Error: {abs(measured_period - theoretical_period):.4f} s")
```

### Exercise 2: Energy Conservation Check

```python
def calculate_energy(theta, omega, m, L, g):
    """Calculate total mechanical energy."""
    # Kinetic energy (rotational)
    I = m * L**2
    KE = 0.5 * I * omega**2

    # Potential energy (height of bob)
    h = L * (1 - np.cos(theta))  # height above lowest point
    PE = m * g * h

    return KE + PE

# Simulate and track energy
t, theta, omega = simulate_pendulum(
    theta0=np.radians(30),
    L=1.0,
    t_max=10,
    dt=0.001
)

m = 1.0
g = 9.81
L = 1.0

energy = calculate_energy(theta, omega, m, L, g)

plt.figure()
plt.plot(t, energy)
plt.xlabel("Time (s)")
plt.ylabel("Total Energy (J)")
plt.title("Energy Conservation Check")
plt.grid()
plt.show()

print(f"Initial energy: {energy[0]:.6f} J")
print(f"Final energy: {energy[-1]:.6f} J")
print(f"Energy drift: {abs(energy[-1] - energy[0]):.6f} J")
```

### Exercise 3: Compare Integration Methods

```python
# Implement both Euler and RK4, compare accuracy
# (Full implementation left as exercise)
```

------

## 17. Next Steps

You're ready for `mathematics-essentials.md` when you can:

- [ ] Explain Newton's laws in your own words
- [ ] Calculate torque given force and distance
- [ ] Derive moment of inertia for simple shapes
- [ ] Simulate a simple pendulum in Python
- [ ] Plot phase space diagrams
- [ ] Understand why inverted pendulum is unstable

------

## Additional Resources

### Books
- "Physics for Scientists and Engineers" by Serway & Jewett
- "Classical Mechanics" by John R. Taylor

### Videos
- Khan Academy: Classical Mechanics
- MIT OpenCourseWare: 8.01 Physics I

### Interactive
- PhET Simulations: https://phet.colorado.edu/
  - Pendulum Lab
  - Energy Skate Park

------

**Last Updated**: 2025-10-17
**Estimated Time**: 8-10 hours
**Next Module**: `mathematics-essentials.md`
