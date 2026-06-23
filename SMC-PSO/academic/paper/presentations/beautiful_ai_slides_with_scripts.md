# DIP-SMC-PSO Full Course: Slides + Speaker Scripts
**Format:** Each slide includes Beautiful.ai prompt + full speaker script
**Target:** Students/Learners | Duration: 60+ minutes | 42 slides total

---

## SLIDE 1: Title Slide
**Duration:** 1 minute

### BEAUTIFUL.AI PROMPT:
```
Layout: Title slide (centered)
Background: Gradient (dark blue to light blue)
Visual elements:
  - Large bold title
  - Subtitle with project details
  - Small pendulum animation/icon
  - Your name and date at bottom
```

### SLIDE CONTENT:
**Title:** Double-Inverted Pendulum Control
**Subtitle:** Sliding Mode Control with PSO Optimization
**Visual:** Animated pendulum silhouette
**Footer:** [Your Name] | [Date] | [Institution]

### SPEAKER SCRIPT:
"Good morning everyone! Today we're going to explore one of the most challenging problems in control theory: the double-inverted pendulum. Imagine trying to balance two broomsticks on top of each other, on a moving cart. That's essentially what we're dealing with here.

This project combines classical control theory with modern optimization techniques. We'll learn about Sliding Mode Control, which is a robust control strategy, and Particle Swarm Optimization, which helps us tune our controllers automatically.

By the end of this session, you'll understand not just the theory, but also how to implement these controllers in Python and analyze their performance. Let's get started!"

---

## SLIDE 2: What is a Double-Inverted Pendulum?
**Duration:** 2 minutes

### BEAUTIFUL.AI PROMPT:
```
Layout: Split screen (image left, bullets right)
Visual elements:
  - LEFT: Large diagram of DIP system (cart + two pendulums)
  - RIGHT: Key characteristics as bullets
  - Use arrows to show motion directions
  - Color code: cart=blue, pendulum1=green, pendulum2=orange
```

### SLIDE CONTENT:
**Title:** What is a Double-Inverted Pendulum (DIP)?

**Visual (Left):** Diagram showing:
- Cart on horizontal track
- Two pendulums stacked vertically
- Angle labels (theta1, theta2)
- Force arrow on cart

**Text (Right):**
- Unstable system (like balancing a broomstick)
- Two linked pendulums on a moving cart
- 4 state variables to control
- Real-world analog: rocket stabilization, humanoid robots
- Classic benchmark in control theory

### SPEAKER SCRIPT:
"So what exactly is a double-inverted pendulum? Let's break it down.

Imagine a cart that can move left and right on a horizontal track. On top of this cart, we have not one, but TWO pendulums stacked on top of each other. Both pendulums want to fall down due to gravity - that's why we call it 'inverted.'

Our job is to keep both pendulums upright by moving the cart back and forth. We have four state variables we need to track: the cart's position and velocity, and both pendulums' angles and angular velocities.

Why do we care about this problem? It's not just an academic exercise. The same control principles apply to real-world systems like rocket stabilization during launch, humanoid robot balance, and even segway personal transporters.

The key challenge is that this system is inherently unstable. If we don't actively control it, it collapses immediately. And because the two pendulums are linked, their motions affect each other in complex ways. This makes it a perfect testbed for advanced control algorithms."

---

## SLIDE 3: Why is This Problem Challenging?
**Duration:** 2 minutes

### BEAUTIFUL.AI PROMPT:
```
Layout: Icon grid (4 challenges)
Visual elements:
  - 4 boxes in 2x2 grid
  - Each box has icon + title + 1-line explanation
  - Icons: warning symbol, infinity loop, coupled gears, lightning bolt
  - Color: Red/orange theme for warnings
```

### SLIDE CONTENT:
**Title:** Why is DIP Control So Challenging?

**Challenge 1: Unstable Equilibrium**
- Icon: Warning triangle
- Both pendulums naturally fall
- System diverges in <2 seconds without control

**Challenge 2: Nonlinear Dynamics**
- Icon: Curved arrow/spiral
- Equations involve sin/cos terms
- Behavior changes dramatically with angle

**Challenge 3: Coupled Motion**
- Icon: Interconnected gears
- Moving pendulum 1 affects pendulum 2
- 4 degrees of freedom interact

**Challenge 4: Fast Response Needed**
- Icon: Lightning bolt
- Control loop must run at 100+ Hz
- No room for delay or hesitation

### SPEAKER SCRIPT:
"Before we dive into solutions, let's understand why this problem is so difficult. There are four main challenges:

First, unstable equilibrium. Both pendulums naturally want to fall down. If we turn off our controller, the system collapses in less than two seconds. There's no stable resting position we can rely on.

Second, nonlinear dynamics. The equations governing this system aren't simple linear relationships. They involve sine and cosine functions, which means the system's behavior changes dramatically depending on the angle. A small push when the pendulum is nearly upright has a very different effect than the same push when it's tilted at 30 degrees.

Third, coupled motion. The two pendulums aren't independent. When the bottom pendulum moves, it directly affects the top one through the connecting joint. And the top pendulum's motion creates a reaction force on the bottom one. We have four degrees of freedom - cart position, cart velocity, two angles, and two angular velocities - all influencing each other.

Finally, we need fast response. In the real world, this control loop needs to run at least 100 times per second. Our controller must calculate the correct force and apply it within 10 milliseconds. Any delay or computational bottleneck, and the system falls.

These challenges are exactly what make sliding mode control an excellent choice. It's designed specifically to handle nonlinear, uncertain systems with fast switching control laws."

---

## SLIDE 4: Course Objectives & Learning Outcomes
**Duration:** 1.5 minutes

### BEAUTIFUL.AI PROMPT:
```
Layout: Checklist style
Visual elements:
  - Large checkbox icons (interactive if possible)
  - 3 main sections with sub-bullets
  - Progress bar at bottom showing "By the end: 100% understanding"
  - Color: Green checkmarks, blue text
```

### SLIDE CONTENT:
**Title:** What You'll Learn Today

**Understanding (Theory):**
- ✓ How Sliding Mode Control works
- ✓ Why SMC is robust to disturbances
- ✓ The role of optimization in control design

**Building (Implementation):**
- ✓ Implement 4 different SMC controllers
- ✓ Set up PSO for automatic gain tuning
- ✓ Run simulations and analyze results

**Analyzing (Results):**
- ✓ Compare controller performance
- ✓ Understand chattering vs. stability tradeoffs
- ✓ Interpret benchmark metrics

**Bottom:** "From zero to hero in 60 minutes!"

### SPEAKER SCRIPT:
"Here's what you'll walk away with after this session.

First, understanding. You'll learn how Sliding Mode Control actually works under the hood, why it's so robust to disturbances and model uncertainties, and how particle swarm optimization helps us tune controller gains automatically.

Second, building. We won't just talk theory. You'll see how to implement four different SMC variants in Python, set up PSO optimization workflows, and run complete simulations from start to finish.

Third, analyzing. You'll learn to compare different controllers using real metrics, understand the fundamental tradeoff between chattering and stability, and interpret benchmark results like a researcher.

My goal is to take you from zero knowledge to being able to implement and analyze these controllers yourself. All the code is open-source on GitHub, and we'll walk through examples together. Let's make this practical and hands-on!"

---

## SLIDE 5: What is Control Theory?
**Duration:** 2 minutes

### BEAUTIFUL.AI PROMPT:
```
Layout: Process flow diagram
Visual elements:
  - Central flowchart: Reference -> Controller -> Plant -> Output
  - Feedback loop arrow from Output back to Controller
  - Real-world examples in sidebar (3 icons: thermostat, cruise control, robot)
  - Animated arrows showing signal flow
```

### SLIDE CONTENT:
**Title:** Control Theory: The Big Picture

**Main Diagram:**
```
[Reference/Goal] --> [Controller] --> [Plant/System] --> [Output]
                          ^                              |
                          |______ Feedback Loop _________|
```

**Key Concepts:**
- **Reference:** Desired behavior (e.g., "keep pendulums upright")
- **Controller:** Brain that computes control action
- **Plant:** Physical system (cart + pendulums)
- **Feedback:** Measure output, adjust control

**Real Examples:**
- Thermostat (temperature control)
- Cruise control (speed regulation)
- Robot arm (position tracking)

### SPEAKER SCRIPT:
"Let's take a step back and understand the fundamentals of control theory, because everything we'll discuss builds on this foundation.

Control theory is about making systems behave the way we want. The basic structure always looks like this: We have a reference or goal - in our case, keeping both pendulums upright. We have a controller, which is the 'brain' that decides what action to take. We have the plant, which is the physical system we're trying to control - our cart and pendulums. And we have the output, which is what actually happens.

The magic happens in the feedback loop. We constantly measure the output, compare it to our reference, and adjust our control action based on the error. This is called closed-loop control.

You interact with control systems every day, even if you don't realize it. Your home thermostat measures temperature, compares it to your setpoint, and turns heating on or off. Your car's cruise control measures speed and adjusts throttle to maintain your desired speed. Industrial robots measure joint angles and adjust motor torques to follow programmed paths.

The double-inverted pendulum is just another control problem, but with extreme instability and nonlinear dynamics that make it much harder than a thermostat. That's where Sliding Mode Control comes in."

---

## SLIDE 6: Open-Loop vs. Closed-Loop Control
**Duration:** 2 minutes

### BEAUTIFUL.AI PROMPT:
```
Layout: Side-by-side comparison
Visual elements:
  - LEFT: Open-loop diagram (no feedback)
  - RIGHT: Closed-loop diagram (with feedback)
  - Red X on open-loop, Green checkmark on closed-loop
  - Examples below each: toaster vs. oven temperature control
```

### SLIDE CONTENT:
**Title:** Two Control Strategies: Open vs. Closed Loop

**LEFT - Open-Loop Control:**
```
[Input] --> [Controller] --> [Plant] --> [Output]
            (no feedback)
```
- No measurement of output
- Cannot correct for disturbances
- Example: Toaster timer (blind to bread color)
- ❌ Unstable systems: fails immediately

**RIGHT - Closed-Loop Control:**
```
[Reference] --> [Error] --> [Controller] --> [Plant] --> [Output]
                  ^                                        |
                  |___________ Feedback Sensor ____________|
```
- Continuously measures output
- Corrects for errors and disturbances
- Example: Oven thermostat (maintains temperature)
- ✓ Unstable systems: keeps them stable

**Bottom:** "For DIP: Closed-loop is MANDATORY"

### SPEAKER SCRIPT:
"There are two fundamental ways to control a system: open-loop and closed-loop. Let's understand the difference, because it's critical for our application.

In open-loop control, you apply a control input and hope for the best. There's no measurement of what's actually happening. A classic example is a toaster. You set the timer for two minutes, and it toasts for exactly two minutes, regardless of whether your bread is burnt or barely warm. It's blind to the actual outcome.

Open-loop control can work for very simple, predictable systems. But for our inverted pendulum? Absolutely not. The system is unstable. Without feedback, it would collapse in under a second.

Closed-loop control, on the other hand, constantly measures the output and adjusts based on errors. Your oven's thermostat is a perfect example. It measures temperature continuously. If the temperature drops below your setpoint, it turns on the heating element. If it rises above, it turns off. This creates a stable feedback loop.

For the double-inverted pendulum, closed-loop control is mandatory. We measure all four state variables - cart position, cart velocity, both pendulum angles, and both angular velocities - at 100 Hz or faster. Every 10 milliseconds, we calculate the error between our reference (upright) and the actual state, and we adjust the force on the cart accordingly.

The entire Sliding Mode Control framework we'll discuss is a closed-loop control strategy. The 'sliding surface' we'll talk about shortly is defined based on measured errors."

---

## SLIDE 7: Introduction to Sliding Mode Control (SMC)
**Duration:** 2.5 minutes

### BEAUTIFUL.AI PROMPT:
```
Layout: Conceptual diagram with explanation
Visual elements:
  - Main: 2D phase plane with sliding surface line
  - Trajectories from different starting points converging to line
  - "Sliding motion" arrow along the surface
  - Inset: switching control signal (binary +/-)
```

### SLIDE CONTENT:
**Title:** Sliding Mode Control: Core Concept

**Main Visual:** Phase plane diagram showing:
- Sliding surface (diagonal line)
- System trajectories approaching surface
- "Sliding motion" along surface to origin
- Control switches: u = +U when above, u = -U when below

**Key Ideas:**
1. Define a "sliding surface" in state space
2. Drive system to this surface (reaching phase)
3. Keep system on surface via switching control (sliding phase)
4. Sliding motion -> desired behavior (stabilization)

**Advantages:**
- Robust to disturbances and uncertainties
- Fast response
- Finite-time convergence

### SPEAKER SCRIPT:
"Now we get to the heart of our approach: Sliding Mode Control. This is a powerful nonlinear control technique that's perfect for unstable, uncertain systems.

Here's the core idea. Imagine your system's behavior as a trajectory in what we call 'state space.' Every point represents a different combination of position, velocity, angles, etc. Your system moves through this space over time.

Now, we define something called a 'sliding surface.' This is a mathematical constraint - essentially a line or plane in state space - that has a special property: if your system is ON this surface, it exhibits the exact behavior we want. For example, moving toward equilibrium at just the right rate.

The control strategy has two phases:

Phase one is the 'reaching phase.' No matter where your system starts, the controller drives it toward the sliding surface. You can see in this diagram how trajectories from different starting points all converge to the line.

Phase two is the 'sliding phase.' Once on the surface, the controller keeps you there by rapidly switching between two control actions. If you drift above the surface, apply force in one direction. If you drift below, switch to the opposite force. This high-frequency switching keeps you 'sliding' along the surface toward equilibrium.

The beauty of SMC is its robustness. Even if there are disturbances - like someone pushing the pendulum - or if your model isn't perfect, the switching control compensates automatically. You're constantly correcting based on which side of the surface you're on.

The downside? All that switching can cause chattering - rapid oscillations in the control signal. We'll address that later with continuous approximations and super-twisting algorithms."

---

## SLIDE 8: Why SMC for Unstable Systems?
**Duration:** 2 minutes

### BEAUTIFUL.AI PROMPT:
```
Layout: Comparison table + visual
Visual elements:
  - TOP: Quick comparison table (SMC vs. PID vs. LQR)
  - BOTTOM: 3 scenarios showing SMC robustness
    1. Model uncertainty (✓ SMC handles it)
    2. Disturbances (✓ SMC rejects them)
    3. Nonlinearity (✓ SMC adapts)
```

### SLIDE CONTENT:
**Title:** Why Choose SMC for This Problem?

**Comparison Table:**

| Feature | PID | LQR | SMC |
|---------|-----|-----|-----|
| Handles nonlinearity | ❌ Poor | ❌ Linear only | ✓ Excellent |
| Robust to uncertainty | ~ Moderate | ~ Moderate | ✓ High |
| Disturbance rejection | ~ Moderate | ✓ Good | ✓ Excellent |
| Design complexity | ✓ Simple | ~ Moderate | ~ Moderate |
| Chattering issue | ✓ None | ✓ None | ❌ Possible |

**SMC Strengths for DIP:**
- Inherent robustness (± 30% parameter variation)
- Fast finite-time convergence (<2 seconds)
- Works across full angle range (-180° to +180°)
- Proven for underactuated systems

### SPEAKER SCRIPT:
"You might be wondering: why Sliding Mode Control specifically? Why not use simpler methods like PID, or optimal control like LQR?

Let me show you this comparison table. PID control is simple to implement, but it's designed for linear systems. Our double pendulum is highly nonlinear. PID controllers struggle when the dynamics change with state.

LQR - Linear Quadratic Regulator - is an optimal control method. It works beautifully for linear systems and provides smooth control. But again, it assumes linearity. You can linearize the pendulum equations around the upright position, but then your controller only works well near that point. Large disturbances can push you outside the valid region.

SMC, on the other hand, is explicitly designed for nonlinear systems. It doesn't care if your dynamics are linear or not. The sliding surface can be designed to handle the full nonlinear model.

More importantly, SMC is inherently robust. Research shows that properly designed SMC controllers can handle up to 30% variation in system parameters - like pendulum mass or length - without retuning. This is because the switching control constantly corrects for deviations.

For our specific application - an unstable, underactuated, nonlinear system - SMC provides fast convergence, typically within 2 seconds from any initial condition. It works across the full angle range, not just small perturbations.

Yes, chattering is a concern. That's why we implement four different variants: classical SMC as a baseline, then super-twisting, adaptive, and hybrid approaches to reduce chattering while maintaining robustness. We'll see all four in action later."

---

## SLIDE 9: The Chattering Problem
**Duration:** 1.5 minutes

### BEAUTIFUL.AI PROMPT:
```
Layout: Before/after comparison
Visual elements:
  - LEFT: Classical SMC control signal (jagged, high-frequency switching)
  - RIGHT: Continuous SMC control signal (smooth)
  - Waveform diagrams showing chattering vs. smooth control
  - Warning icon for "Why chattering is bad"
```

### SLIDE CONTENT:
**Title:** The Chattering Problem & Solutions

**LEFT - Classical SMC (Chattering):**
- Control signal switches rapidly (+U, -U, +U, -U...)
- Frequency: 100+ Hz
- Looks like high-frequency noise
- Problems: Actuator wear, energy waste, noise

**RIGHT - Continuous Approximations:**
- Smooth control signal (no discontinuities)
- Methods: Boundary layer, super-twisting, adaptive gain
- Slightly slower response
- Benefits: Practical implementation, less wear

**Solutions We Implement:**
1. Super-Twisting Algorithm (STA): Higher-order sliding mode
2. Adaptive SMC: Adjusts gains in real-time
3. Hybrid: Combines STA + adaptive

### SPEAKER SCRIPT:
"Now let's address the elephant in the room: chattering. This is the main practical limitation of classical sliding mode control.

Remember how I said the control switches rapidly between two values to keep you on the sliding surface? In theory, this switching happens infinitely fast. In practice, even at 100 Hz, you get this jagged, high-frequency control signal.

Why is this bad? Three reasons. First, actuator wear. If you're constantly flipping a motor or valve on and off hundreds of times per second, it wears out quickly. Second, energy waste. All that switching consumes power. Third, it excites high-frequency dynamics - vibrations and resonances - that your model doesn't account for.

The solution is to approximate the discontinuous switching with continuous functions. Instead of jumping instantly from +U to -U, we use smooth functions that transition gradually within a thin boundary layer.

This project implements three advanced approaches. First, the Super-Twisting Algorithm, which is a higher-order sliding mode that achieves finite-time convergence without chattering. It's more complex mathematically but very effective.

Second, Adaptive SMC, which adjusts controller gains in real-time based on the current error. When errors are large, it uses high gains for fast response. When errors are small, it reduces gains to minimize chattering.

Third, a Hybrid approach that combines super-twisting with adaptive gains. This gives us the best of both worlds: fast convergence and minimal chattering.

We'll see all three in action during the results section, and you'll be able to compare their chattering performance quantitatively."

---

## SLIDE 10: Physics of the Pendulum
**Duration:** 2 minutes

### BEAUTIFUL.AI PROMPT:
```
Layout: Annotated diagram + key equations
Visual elements:
  - LEFT: Detailed pendulum diagram with force vectors
  - Labels: m1, m2, L1, L2, theta1, theta2, cart mass M
  - Force arrows: gravity, joint forces, cart force F
  - RIGHT: Key parameters table
```

### SLIDE CONTENT:
**Title:** Physical System Parameters

**Diagram (Left):**
- Cart (mass M = 2.0 kg)
- Pendulum 1 (mass m1 = 0.5 kg, length L1 = 0.5 m)
- Pendulum 2 (mass m2 = 0.5 kg, length L2 = 0.5 m)
- Angles theta1, theta2 measured from vertical
- Applied force F on cart

**Parameters Table (Right):**
| Parameter | Symbol | Value |
|-----------|--------|-------|
| Cart mass | M | 2.0 kg |
| Pendulum 1 mass | m1 | 0.5 kg |
| Pendulum 2 mass | m2 | 0.5 kg |
| Pendulum 1 length | L1 | 0.5 m |
| Pendulum 2 length | L2 | 0.5 m |
| Gravity | g | 9.81 m/s² |
| Damping | b | 0.1 N·s/m |

**Goal:** Keep theta1 = 0°, theta2 = 0° (both upright)

### SPEAKER SCRIPT:
"Let's get concrete about the physical system we're controlling. Here are the actual parameters we use in simulation.

Our cart has a mass of 2 kilograms. On top of it, we have two pendulums, each with mass 0.5 kg and length 0.5 meters. These are reasonable values for a tabletop experimental setup.

The angles theta1 and theta2 are measured from the vertical upright position. So theta = 0 degrees means perfectly upright, which is our goal. Theta = 180 degrees would mean hanging straight down.

The control input F is a horizontal force applied to the cart. In a real system, this might come from a motor driving the cart along a rail. The force can be positive (pushing right) or negative (pushing left), and we can apply up to 50 Newtons in either direction.

Gravity pulls both pendulums downward with acceleration 9.81 meters per second squared. We also include a small damping term - friction at the joints - with coefficient 0.1. This represents realistic energy dissipation.

Our control objective is simple to state but hard to achieve: keep both theta1 and theta2 at zero degrees, while also keeping the cart position within reasonable bounds, say within +/- 2 meters of center.

These parameters define our simulation environment. In the code, they're all configured in a YAML file, so you can easily experiment with different masses, lengths, or gravity values to see how the controller responds."

---

## SLIDE 11: Mathematical Model Overview
**Duration:** 2.5 minutes (can skip details for non-technical audience)

### BEAUTIFUL.AI PROMPT:
```
Layout: Hierarchical model explanation
Visual elements:
  - TOP: Lagrangian mechanics badge/icon
  - MIDDLE: Simplified equation block (high-level)
  - BOTTOM: "What this means in English" translation
  - Code snippet sidebar showing Python implementation
```

### SLIDE CONTENT:
**Title:** Mathematical Model (How We Simulate Physics)

**High-Level Equations:**
```
M·(d²x/dt²) + m1·L1·θ1'' + m2·L2·θ2'' = F  (Cart motion)
m1·L1·θ1'' + ... = -m1·g·sin(θ1)           (Pendulum 1)
m2·L2·θ2'' + ... = -m2·g·sin(θ2)           (Pendulum 2)
```
*(Full equations: 3 coupled second-order nonlinear ODEs)*

**In Plain English:**
- Cart acceleration depends on applied force F AND pendulum motions
- Pendulum accelerations depend on gravity AND cart motion
- Everything is coupled (moving one affects all others)
- Nonlinear terms: sin(θ), cos(θ) make this hard

**Implementation:**
```python
def dynamics(state, force):
    # State: [x, x', θ1, θ1', θ2, θ2']
    # Returns: derivatives [x', x'', θ1', θ1'', θ2', θ2'']
    # Solved using scipy.integrate.solve_ivp
```

**Bottom:** "Don't worry about math details - the code handles it!"

### SPEAKER SCRIPT:
"Now, a quick look at the mathematics. Don't worry if you're not a math person - I'll translate this into plain English, and the code handles all the complexity.

The system is governed by three coupled second-order differential equations derived from Lagrangian mechanics. This is a standard approach in robotics and mechanical systems.

Here's what these equations say in English. The cart's acceleration depends not only on the force we apply, but also on how the pendulums are moving. If both pendulums are swinging to the right, they push the cart to the right through inertial coupling.

Similarly, each pendulum's angular acceleration depends on both gravity pulling it down and the cart's motion underneath it. If the cart accelerates to the right, the pendulum feels a pseudo-force pushing it to the left, like you feel pushed back in your seat when a car accelerates.

Everything is coupled. You can't move the cart without affecting the pendulums. You can't move pendulum 1 without affecting pendulum 2. This is what makes the control problem difficult.

The nonlinear terms - sine and cosine of the angles - mean the system behavior changes with state. Near upright, small-angle approximations work reasonably well. But at large angles, these nonlinear effects dominate.

In our Python implementation, we encode these equations in a dynamics function. It takes the current state - cart position, velocity, both angles, and angular velocities - plus the applied force, and returns the derivatives. Then we use SciPy's ODE solver to integrate forward in time.

The good news is, you don't need to derive or solve these equations by hand. The code is already written and tested. But it's good to understand conceptually what's happening under the hood."

---

## SLIDE 12: State Space Representation
**Duration:** 1.5 minutes

### BEAUTIFUL.AI PROMPT:
```
Layout: State vector visualization
Visual elements:
  - Large state vector graphic: [x, x', θ1, θ1', θ2, θ2']
  - Icons for each: cart position, speedometer, angle1, angular velocity1, angle2, angular velocity2
  - Timeline showing state evolution over 5 seconds
  - Arrows showing feedback to controller
```

### SLIDE CONTENT:
**Title:** State Space: What We Measure & Control

**State Vector (6 dimensions):**
```
x(t) = [  x,    x',   θ1,   θ1',  θ2,   θ2' ]
       [pos, vel, ang1, ω1,  ang2,  ω2 ]
```

**What Each Means:**
1. **x:** Cart position (meters from center)
2. **x':** Cart velocity (m/s, left/right speed)
3. **θ1:** Pendulum 1 angle (radians from vertical)
4. **θ1':** Pendulum 1 angular velocity (rad/s)
5. **θ2:** Pendulum 2 angle (radians from vertical)
6. **θ2':** Pendulum 2 angular velocity (rad/s)

**Control Loop:**
- Measure all 6 states at 100 Hz
- Controller computes force F based on state
- Apply F to cart
- System evolves to new state
- Repeat

**Bottom:** "6 numbers tell us everything about the system"

### SPEAKER SCRIPT:
"Before we move to implementation, let's clarify what we mean by 'state' and 'state space.'

The state of our system at any moment is completely described by six numbers. First, the cart's position - how far left or right it is from center, measured in meters. Second, the cart's velocity - how fast it's moving and in which direction.

Third and fourth are pendulum 1's angle and angular velocity. The angle tells us how far from vertical it is. The angular velocity tells us if it's tilting and how fast.

Fifth and sixth are the same for pendulum 2.

These six numbers - collectively called the state vector - tell us everything we need to know about the system's current condition. Given this state and the current control force, we can predict exactly how the system will evolve forward in time using our dynamics equations.

The control loop works like this: we measure all six states at 100 Hz using sensors. In simulation, we have perfect measurements. In a real system, you might use encoders for positions and angles, and estimate velocities using differences or filters.

The controller receives this state vector, computes the optimal force F based on the current error, and applies it to the cart. The system evolves to a new state. We measure again, and repeat. One hundred times per second, every 10 milliseconds.

This is the foundation of state-space control. Instead of just looking at one output like traditional PID, we consider the entire system state when deciding what control action to take. This is what enables SMC to handle the complex, coupled dynamics effectively."

---

## SLIDES 13-42: [TO BE GENERATED]

This template demonstrates the format. Each slide will include:
- Duration estimate
- Beautiful.ai layout prompt
- Full slide content
- Complete speaker script

**Next sections to generate:**
- Part 2: Controllers & PSO (Slides 13-24)
- Part 3: Implementation (Slides 25-33)
- Part 4: Results (Slides 34-39)
- Part 5: Advanced Topics (Slides 40-42)

---

## Usage Instructions

### For Beautiful.ai:
1. Create new presentation
2. For each slide, use the "BEAUTIFUL.AI PROMPT" section to select layout and add elements
3. Copy "SLIDE CONTENT" directly into slide

### For Speaker Preparation:
1. Read "SPEAKER SCRIPT" for each slide
2. Practice timing (durations shown)
3. Adapt language to your style (scripts are templates)
4. Add personal anecdotes or examples

### Estimated Prep Time:
- Review all slides: 2 hours
- Build in Beautiful.ai: 4-6 hours
- Practice delivery: 2-3 run-throughs (2 hours)
**Total: 8-10 hours to full proficiency**
