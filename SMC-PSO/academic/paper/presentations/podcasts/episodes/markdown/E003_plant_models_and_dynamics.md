# E003: Plant Models and Dynamics

**[AUDIO NOTE: This episode is about the physics - the actual equations of motion for our double broomstick. We'll cut straight to the intuition and skip the tedious algebra. The full derivations are in the show notes if you're curious, but you don't need them to understand how this works.]**

## Introduction: What is the Plant?

In control theory, the "plant" is the thing you're trying to control - the physical system itself. In Episodes E001 and E002, we talked about controllers (the brains making decisions). Now we're talking about the plant (the body those decisions act upon).

For our double-inverted pendulum, the plant model is the set of equations that answer this question: "If I push the cart with force F right now, how will the pendulum angles and velocities change in the next millisecond?"

**Remember that SpaceX rocket?** The plant model for a rocket describes how thrust forces translate into position and velocity changes, accounting for mass, moment of inertia, aerodynamic drag, and gravity. Same concept, different system.

This episode covers:
- WHY we use Lagrangian mechanics (skip the painful algebra)
- THREE model variants: The Sprinter, The Simulator, and The Efficient Pro
- Model accuracy and computational trade-offs
- Singularities (when the math breaks down) and what they mean physically
- How all this works in Python code

## Physical System Description: The Double Broomstick Revisited

Picture the system: A cart that slides left and right on a horizontal track. Standing upright on the cart is the first pendulum (the bottom broomstick). Attached to the top of that first pendulum is the second pendulum (the top broomstick). Both pendulums are free to rotate.

**The ASCII diagram** in the show notes shows this setup, but here's the intuition:
- **Cart**: Has mass, slides on a track with some friction, controlled by a horizontal push force
- **Pendulum 1** (bottom stick): Has mass, length, rotates around a joint on the cart with a bit of friction
- **Pendulum 2** (top stick): Has mass, length, rotates around a joint at the top of Pendulum 1

**The Three Coordinates We Track:**
1. **x**: Cart position (how far left or right along the track)
2. **theta-1**: First pendulum angle (measured from vertical - zero means perfectly upright)
3. **theta-2**: Second pendulum angle (also from vertical)

**Real-World Numbers:**
Our default configuration models a realistic lab-scale system:
- Cart: 1.5 kg (about as heavy as a laptop)
- Pendulum 1: 0.2 kg, 40 cm long (about the weight and length of a wooden ruler)
- Pendulum 2: 0.15 kg, 30 cm long (slightly lighter and shorter)
- Friction: Small but non-zero (a bit of resistance at the joints and cart)

These aren't arbitrary - they're based on actual inverted pendulum rigs you'd find in control labs at universities.

## Lagrangian Mechanics: The Elegant Shortcut

**[AUDIO NOTE: We're skipping the painful algebra entirely. Focus on WHY this approach is brilliant, not HOW to grind through the calculus]**

### Why Lagrangian Instead of Newton's Laws?

Imagine trying to analyze this system using Newton's F=ma directly. You'd need to:

1. Draw free-body diagrams for the cart, first pendulum, and second pendulum
2. Figure out all the internal forces - the force the cart exerts on Pendulum 1's pin, the force Pendulum 1's pin exerts back on the cart, the force Pendulum 1 exerts on Pendulum 2's pin, and so on
3. Write force balance equations for each component
4. Solve a coupled system of equations with all these unknown internal forces

That's a **nightmare** of coupled equations with a dozen variables you don't even care about (the pin forces). You just want to know how the system moves!

**The Lagrangian Approach: Ignore the Internal Glue**

Lagrangian mechanics is a brilliant shortcut discovered in the 1700s. The key insight: you don't need to know the internal constraint forces (like pin forces) if you just focus on energy. Here's the recipe:

1. **Calculate total kinetic energy**: How much energy is in the motion? This includes the cart sliding, plus both pendulums translating through space AND rotating. It's messy because Pendulum 2's motion depends on Pendulum 1's motion (they're coupled), but it's doable.

2. **Calculate total potential energy**: How much gravitational potential energy does the system have? Higher pendulums mean more potential energy.

3. **Subtract them to form the Lagrangian**: L = Kinetic Energy - Potential Energy. This single function captures all the system's dynamics.

4. **Apply Euler-Lagrange equations**: A systematic calculus recipe (like following a cooking recipe) that automatically gives you the equations of motion - NO internal forces needed!

**The Beautiful Result:**

After all that calculus (which we're not subjecting you to), you get a single matrix equation:

**M(q) × acceleration + C(q,q̇) × velocity + G(q) = B × control force + disturbances**

Let's unpack what each matrix actually MEANS physically:

- **M(q) - The Mass Matrix**: Captures how mass and inertia are distributed. "If I want to accelerate the cart by 1 m/s², and the pendulums are at these angles, how much force do I need?" The answer depends on the pendulum angles because the effective inertia changes with configuration.

- **C(q,q̇) - The Spinning Forces**: These are Coriolis and centrifugal terms. Remember that car-turn analogy from the Gemini review? When you take a sharp turn, you feel pushed against the car door - that's centrifugal force. When you try to walk straight on a spinning merry-go-round and your path curves - that's Coriolis. Our pendulums feel both because they're rotating and moving through space simultaneously.

- **G(q) - Gravity**: How much does gravity pull on each component? Depends on the angles - when pendulums are more vertical, gravity pulls them down harder (larger torque).

- **B - Input Distribution**: The control force only pushes the cart directly, not the pendulums. This matrix captures that "the force enters here but affects everything indirectly."

## Mass Matrix Structure: Action and Reaction

**[AUDIO NOTE: This is where the coupling between components shows up mathematically]**

The mass matrix is a 3×3 grid of numbers that changes with the pendulum angles. Here's the intuition:

**Diagonal Elements** (M11, M22, M33):
These represent "self-inertia" - how hard it is to accelerate each component by itself. M11 is the total mass of everything (cart plus both pendulums), because accelerating the cart means dragging everything along. M22 is the rotational inertia of Pendulum 1, M33 is the rotational inertia of Pendulum 2.

**Off-Diagonal Elements** (M12, M13, M23):
These are the **coupling terms** - they capture how motion of one component affects the others. For example, M12 tells you: "If I accelerate the cart, how much does that torque Pendulum 1?" The answer depends on cos(theta-1) - when Pendulum 1 is vertical, the coupling is strongest. When it's horizontal, there's less coupling.

**Key Property - Symmetry:**
The matrix is symmetric: M12 equals M21, M13 equals M31, M23 equals M32. This is Newton's Third Law in disguise - **action and reaction**. The effect of Link 1 on Link 2 is exactly the same magnitude as the effect of Link 2 on Link 1. Just in different directions.

**In Code:**
The Python implementation computes all these elements based on the current pendulum angles, using trig functions (cosines) for the coupling terms. It returns a 3×3 NumPy array that we can invert and use in our dynamics solver.

### Singularities: When the Math Locks Up

**[AUDIO NOTE: This is where the physics breaks down - and it has a clear physical meaning]**

Think about your arm. When you extend your arm fully and lock your elbow, you can't push it any further in that direction. The geometry has "locked up" - there's no more range of motion available in that direction. The same thing happens with our pendulum system at certain configurations.

**What Causes Singularities?**

For the double inverted pendulum, singularities occur when the pendulums align in very specific ways. For example, when both pendulums are perfectly horizontal (lying flat), the mass matrix becomes nearly singular. Why? Because in that configuration, certain motions become mechanically "locked" - the system can't accelerate in certain directions without infinite force.

**The Condition Number - A Health Check:**

We use something called the "condition number" to measure how close the mass matrix is to being singular. Think of it as a health score:
- **κ around 1-100**: Healthy - the matrix inverts cleanly, no numerical issues
- **κ above 1 million**: Sick - numerical errors get amplified, results become unreliable
- **κ approaching infinity**: Dead - the matrix is singular, can't be inverted

**How We Handle It in Code:**

The code checks the condition number before inverting the mass matrix. If it's too high (above 100 million), we switch to a safer "pseudoinverse" method with regularization - essentially adding a tiny bit of numerical cushioning to prevent division-by-near-zero. It's slightly slower but prevents crashes.

**In Practice:**
For normal operation near the upright position, the condition number stays in the healthy range (10-100). Only when pendulums swing toward horizontal do we approach dangerous territory. The controller is designed to avoid those configurations anyway.

## Coriolis and Centrifugal Terms

### Coriolis/Centrifugal Matrix

```python
def _compute_coriolis_matrix(self, theta1: float, theta2: float,
                            theta1_dot: float, theta2_dot: float) -> np.ndarray:
    """
    Compute C(q,q̇) matrix.

    Contains:
    - Coriolis terms (velocity-dependent coupling)
    - Centrifugal terms (velocity-squared terms)
    """
    s1 = np.sin(theta1)
    s2 = np.sin(theta2)
    s12 = np.sin(theta1 - theta2)

    # Coriolis/centrifugal coefficients
    c1 = self.m1 * self.lc1 + self.m2 * self.L1
    c2 = self.m2 * self.lc2
    c12 = self.m2 * self.L1 * self.lc2

    C = np.zeros((3, 3))

    # First row (cart equation)
    C[0, 1] = -c1 * s1 * theta1_dot
    C[0, 2] = -c2 * s2 * theta2_dot

    # Second row (pendulum 1 equation)
    C[1, 0] = -c1 * s1 * theta1_dot
    C[1, 2] = -c12 * s12 * theta2_dot

    # Third row (pendulum 2 equation)
    C[2, 0] = -c2 * s2 * theta2_dot
    C[2, 1] = c12 * s12 * theta1_dot

    return C
```

**Physical Interpretation:**

**Coriolis Force**: Apparent force due to rotation
- Example: When pendulum 1 rotates, it induces forces on cart and pendulum 2
- Term: `-c12 * sin(θ₁ - θ₂) * θ̇₂` couples pendulum velocities

**Centrifugal Force**: Outward force due to rotation
- Example: Rotating pendulum creates force pushing cart sideways
- Term: `-c1 * sin(θ₁) * θ̇₁²` pushes cart away from pendulum

## Gravity Vector

```python
def _compute_gravity_vector(self, theta1: float, theta2: float) -> np.ndarray:
    """
    Compute gravity vector G(q).

    G = -∂V/∂q where V = potential energy
    """
    s1 = np.sin(theta1)
    s2 = np.sin(theta2)

    g1 = self.m1 * self.lc1 + self.m2 * self.L1
    g2 = self.m2 * self.lc2

    return np.array([
        0,                          # No gravity on cart (horizontal)
        -g1 * self.g * s1,         # Pendulum 1 torque
        -g2 * self.g * s2          # Pendulum 2 torque
    ])
```

**Sign Convention**: Upright (θ=0) is unstable equilibrium
- Gravity torque pushes pendulum away from vertical
- Control must counteract this destabilizing torque

## Three Model Variants: Meet the Characters

**[AUDIO NOTE: Think of these three models as three different teammates, each with their own personality and strengths]**

We provide three different mathematical models of the same physical system. Why three? Because there's a fundamental trade-off between **speed** and **accuracy**, and different tasks require different balances. Let's personify them:

### Model 1: The Sprinter (Simplified Linear Model)

**Personality**: Fast, agile, assumes everything is nearly perfect

Think of the Sprinter as your quick prototyping buddy. Makes big simplifying assumptions:
- **Assumes small angles**: "sine of theta is just theta, cosine is just one" - only true when angles are tiny (within 5-10 degrees of vertical)
- **Ignores coupled effects**: "When both pendulums are moving, I'll pretend those interactions are negligible"
- **Constant mass matrix**: "I'll compute the mass distribution once and never update it"

**Superpowers**:
- **Lightning fast**: 10 to 100 times faster than the full model. Can run thousands of simulations in minutes.
- **Perfect for PSO**: When you need to evaluate 30 particles over 50 iterations (1500 simulations), you want the Sprinter.
- **Great for teaching**: Simple enough that students can work through the equations by hand.

**Kryptonite**:
- **Can't handle large angles**: Try to simulate swing-up (starting from hanging down), and the Sprinter gives you garbage. The small-angle approximation breaks completely.
- **Lies about nonlinear effects**: Underestimates how the pendulums actually couple when moving fast.

**When to Call the Sprinter**: Initial prototyping, PSO gain optimization, educational demos, any time you're operating near upright and need speed.

**Code Workflow**: Grab the linearized (constant) mass matrix, compute simplified dynamics (linear in angles), solve one matrix equation, done. Super clean, super fast.

### Model 2: The Simulator (Full Nonlinear Model)

**Personality**: Slow, heavy, brutally honest about physics

The Simulator is your reality-check friend. No shortcuts, no approximations. Every trigonometric term, every Coriolis effect, every bit of coupling - all computed exactly.

**Superpowers**:
- **Tells the truth**: Accurate across the FULL operating range - from hanging down to perfectly upright and everywhere in between.
- **All the physics**: Captures Coriolis forces (remember the merry-go-round?), centrifugal effects (car-turn push), gyroscopic coupling (how rotation in one axis affects another).
- **Your final exam**: When you publish benchmark results, you use the Simulator to prove your controller actually works in realistic conditions.

**Kryptonite**:
- **Computationally expensive**: 10-100x slower than the Sprinter. All those trig functions and matrix updates add up.
- **Overkill for simple tasks**: If you just need a ballpark gain estimate, the Simulator is like using a sledgehammer to crack a nut.

**When to Call the Simulator**: Final validation before hardware deployment, swing-up control (large angles), research benchmarks you'll publish, any time accuracy matters more than speed.

**Code Workflow**: Compute angle-dependent mass matrix, compute velocity-dependent Coriolis matrix, compute angle-dependent gravity vector, combine friction, solve the full dynamics equation. It's a workout for the CPU.

### Model 3: The Efficient Pro (Low-Rank Approximation)

**Personality**: Smart compromise - fast like the Sprinter, accurate like the Simulator (mostly)

The Efficient Pro uses a clever mathematical trick called Proper Orthogonal Decomposition (POD). Here's the idea: run the full Simulator thousands of times, collect all the data, then use math (Singular Value Decomposition) to figure out which "patterns" in the motion matter most. Keep the important patterns, throw away the noise.

**Superpowers**:
- **10-50x speedup**: Almost as fast as the Sprinter, but preserves the accuracy of the Simulator for the dynamics that matter.
- **Perfect for Monte Carlo**: Need to run 1000 simulations with parameter variations? The Efficient Pro handles it.
- **Real-time capable**: Fast enough for hardware-in-the-loop (HIL) testing where you need millisecond-level updates.

**Kryptonite**:
- **Needs training**: You have to run the full Simulator first to collect the "snapshot" data. Not a drop-in replacement.
- **Can miss rare events**: If your training data doesn't include a weird edge case, the reduced model won't capture it.

**When to Call the Efficient Pro**: Large-scale parameter sweeps (testing 1000 different gain combinations), sensitivity analysis, HIL testing where real-time performance matters.

**The Bottom Line**:
- **Quick prototyping?** Sprinter.
- **Final validation?** Simulator.
- **Massive data crunching?** Efficient Pro.

It's like having three tools in your toolbox - hammer, precision screwdriver, and power drill. Use the right tool for the job.

## Model Accuracy Comparison

### Validation Test (MT-6 Benchmark)

**Setup:**
- Initial condition: `θ₁ = 10°`, `θ₂ = 5°`
- Controller: Classical SMC with optimized gains
- Duration: 10 seconds
- Metric: Settling time, overshoot, RMS error

**Results:**

| Model | Settling Time [s] | Overshoot [°] | RMS Error [°] | Speed [sims/sec] |
|-------|-------------------|---------------|---------------|------------------|
| Simplified | 2.31 | 4.2 | 0.12 | 450 |
| Full Nonlinear | 2.58 | 5.1 | 0.15 | 8 |
| Low-Rank (k=10) | 2.54 | 4.9 | 0.14 | 95 |

**Observations:**
1. Simplified model underestimates settling time (optimistic)
2. Full model most conservative (realistic)
3. Low-rank model good compromise (2% error, 12x speedup)

### Angle Range Validation

**Test**: Swing-up from θ₁ = 180° (hanging down)

| Model | Can Simulate? | Max Angle Error |
|-------|---------------|-----------------|
| Simplified | NO (invalid at θ>10°) | N/A |
| Full Nonlinear | YES | Reference |
| Low-Rank | YES (if trained on swing-up) | 3.5° |

**Conclusion**: Simplified model ONLY valid near upright!

## Implementation Details

### Numerical Integration

**Available Integrators** (from `config.yaml`):

```yaml
verification:
  integrators:
    - euler    # 1st order, fast, inaccurate
    - rk4      # 4th order, good balance
    - rk45     # Adaptive, most accurate
```

**Euler (1st order):**
```python
def euler_step(f, state, u, dt):
    state_dot = f(state, u)
    return state + state_dot * dt
```

**RK4 (4th order):**
```python
def rk4_step(f, state, u, dt):
    k1 = f(state, u)
    k2 = f(state + 0.5*dt*k1, u)
    k3 = f(state + 0.5*dt*k2, u)
    k4 = f(state + dt*k3, u)
    return state + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)
```

**RK45 (adaptive):**
- SciPy's `solve_ivp` with automatic step size
- Error control: `rtol=1e-6`, `atol=1e-9`
- Best for high-accuracy validation

**Typical Choice**: RK4 with `dt = 0.001s` (1 kHz)

### Singularity Handling

**Problem**: `M(q)` may become ill-conditioned near certain configurations.

**Solutions:**

**1. Condition Number Monitoring:**
```python
cond = np.linalg.cond(M)
if cond > threshold:
    logger.warning(f"Ill-conditioned mass matrix: κ={cond:.2e}")
```

**2. Regularized Inversion:**
```python
# Add small diagonal perturbation
M_reg = M + epsilon * np.eye(3)
M_inv = np.linalg.inv(M_reg)
```

**3. Pseudoinverse:**
```python
M_inv = np.linalg.pinv(M, rcond=1e-6)
```

**From `config.yaml`:**
```yaml
stability_monitoring:
  conditioning:
    median_threshold: 10000000.0      # Warn if median κ > 1e7
    spike_threshold: 1000000000.0     # Warn if p99 κ > 1e9
    fallback_threshold: 3             # Max pseudoinverse uses per episode
```

## Common Pitfalls and Tips

### Pitfall 1: Wrong Angle Convention

**Problem**: Sign errors in sin/cos terms.

**Our Convention**: θ = 0 at upright (unstable equilibrium)
- Gravity term: `-m·g·l·sin(θ)` (pushes away from vertical)
- Pendulum points UP when θ=0

**Alternative**: θ = 0 at hanging (stable equilibrium)
- Would require different gravity signs
- Less common for inverted pendulum control

### Pitfall 2: Inconsistent Units

**Problem**: Mixing radians and degrees.

**Solution**: ALWAYS use SI units internally:
- Angles: radians
- Angular velocity: rad/s
- Lengths: meters
- Masses: kilograms
- Forces: Newtons

**Conversion for Display:**
```python
theta_deg = np.rad2deg(theta)  # For plotting
theta_rad = np.deg2rad(theta_deg)  # From user input
```

### Pitfall 3: Ignoring Parameter Bounds

**Problem**: Unphysical parameters cause numerical issues.

**Validation** (from `src/config.py`):
```python
@validator('cart_mass')
def validate_cart_mass(cls, v):
    if v <= 0:
        raise ValueError("Cart mass must be positive")
    if v < 0.5 or v > 10.0:
        logger.warning(f"Unusual cart mass: {v} kg")
    return v

@validator('pendulum1_inertia')
def validate_inertia(cls, v, values):
    # Minimum: point mass at COM
    m = values.get('pendulum1_mass', 0.2)
    l = values.get('pendulum1_com', 0.2)
    I_min = m * l**2

    if v < I_min:
        raise ValueError(f"Inertia {v} < minimum {I_min} for point mass")
    return v
```

### Tip 1: Validate Against Known Solutions

**Test Case**: Undamped pendulum oscillation

```python
def test_conservation_of_energy():
    # No friction, no control
    config = get_config(cart_friction=0, joint1_friction=0, joint2_friction=0)

    # Initial condition: θ₁ = 10°, zero velocity
    state0 = np.array([0, 0.174, 0, 0, 0, 0])  # 10° = 0.174 rad

    # Simulate for 10 seconds
    result = simulate(state0, u=0, duration=10.0, dt=0.001)

    # Compute total energy at each timestep
    E = [kinetic_energy(s) + potential_energy(s) for s in result.states]

    # Energy should be conserved (E(t) = E(0))
    energy_drift = abs(E[-1] - E[0]) / E[0]
    assert energy_drift < 0.01  # <1% drift acceptable
```

### Tip 2: Cross-Check with Simplified Model

**Workflow:**
1. Develop controller with simplified model (fast iteration)
2. Validate with full model (realistic)
3. Compare results - should match for small angles

**Example:**
```python
# Simplified model
result_simple = simulate_simplified(state0, controller, duration=5.0)

# Full nonlinear model
result_full = simulate_full(state0, controller, duration=5.0)

# Compare
theta1_diff = np.mean(np.abs(result_simple.theta1 - result_full.theta1))
print(f"Mean θ₁ difference: {np.rad2deg(theta1_diff):.2f}°")

# Should be <1° for |θ| < 5°
assert theta1_diff < np.deg2rad(1.0)
```

## Conclusion: From Equations to Rockets

**Remember that SpaceX rocket from Episodes E001 and E002?** Now you understand what's running inside its flight computer's plant model:

**The Rocket's Plant Model:**
1. **Mass matrix**: Changes constantly as fuel burns - the effective inertia drops from millions of kilograms at launch to tens of thousands at landing. The control system recomputes M(q) hundreds of times per second.
2. **Coriolis/centrifugal terms**: When the rocket is rotating to orient itself, these "spinning forces" affect how thrust translates to motion. Ignore them and your trajectory diverges.
3. **Singularities**: Certain gimbal configurations lock up (like our arm analogy) - the flight computer actively avoids these.
4. **Model switching**: During ascent, SpaceX likely uses a simplified model (small angle deviations from vertical). During landing, when the rocket is maneuvering aggressively, they switch to the full nonlinear model. Speed vs. accuracy - just like our three variants.

**What You've Learned:**

1. **Lagrangian Mechanics**: The elegant shortcut that lets us ignore internal constraint forces and focus on energy. No need to solve for pin forces when we just care about motion.

2. **The Dynamics Equation**: M(q)×acceleration + C(q,q̇)×velocity + G(q) = control force. Mass distribution, spinning forces, gravity - all captured in one matrix equation.

3. **Singularities**: Physical locking when geometry aligns in specific ways. The condition number is your health check - stay in the healthy range.

4. **Three Models, Three Personalities**:
   - **The Sprinter**: Fast prototyping, PSO optimization, small-angle assumptions
   - **The Simulator**: Brutal honesty, full physics, your reality check
   - **The Efficient Pro**: Smart compromise, captures dominant patterns, Monte Carlo champion

5. **Use the Right Tool**: You wouldn't use a sledgehammer to crack a nut, and you wouldn't use the Sprinter to validate swing-up control.

**What's Next?**

Episode E004 dives into PSO Optimization - the algorithm that automatically tunes controller gains. Remember how we said the Sprinter is perfect for PSO? You're about to see why. We'll cover the particle swarm algorithm, cost function design, and the real performance improvements we achieved (up to 360% gain increases while maintaining stability).

**Final Thought**: The physics we covered today - Lagrangian mechanics, coupled dynamics, singularities - has been refined over centuries by brilliant physicists. But at its heart, it's all about understanding how objects move when you push them. Keep the physical intuitions in mind (car turns, merry-go-rounds, locked elbows), and the math becomes a tool, not an obstacle.

See you in E004!

---

**Episode Metadata:**
- **Length**: ~529 lines (optimized for audio clarity, down from ~1000 lines)
- **Audio Time**: 25-30 minutes (estimated at conversational pace)
- **Prerequisites**: Classical mechanics, linear algebra, basic Python (or strong physical intuition)
- **Next**: E004 - PSO Optimization
- **Optimization**: Gemini AI review applied - ALL derivations cut, Lagrangian "WHY" explained, matrix terms given physical analogies (car turns, merry-go-rounds), singularities as "physical locking", three models personified as Sprinter/Simulator/Efficient Pro, SpaceX recurring theme, real-world consequences added
