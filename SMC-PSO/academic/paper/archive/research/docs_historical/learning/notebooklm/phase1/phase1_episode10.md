# Phase 1 NotebookLM Podcast: Episode 10 - Functions, Graphing, and Trigonometry

**Duration**: 20-22 minutes | **Learning Time**: 3 hours | **Difficulty**: Beginner

---

## Opening Hook

Stand in an empty room. Face north. Turn 90 degrees clockwise. You're now facing east. Your position didn't change, but your orientation did. That rotation can be described with angle mathematics - trigonometry.

Now imagine a pendulum. As it swings, its angle changes over time. Plot angle versus time, you get a smooth wave - a cosine curve. That curve is a FUNCTION: time is the input, angle is the output.

Today, we'll connect three mathematical concepts that are fundamental to control systems: functions (relationships between variables), graphing (visualizing those relationships), and trigonometry (the mathematics of angles and rotation). By the end, you'll see how sine and cosine aren't abstract formulas - they're descriptions of circular motion that appear everywhere in oscillating systems.

---

## What You'll Discover

By listening to this episode, you'll learn:

- Mathematical functions: definition and notation
- Function properties: domain, range, input, output
- Graphing functions to visualize behavior
- Trigonometric functions: sine, cosine, tangent
- The unit circle and radian measure
- Periodic functions and oscillation
- Why trigonometry appears in pendulum equations
- Practical graphing with Python

---

## What Is a Function?

In Episode 4, we learned about Python functions - reusable blocks of code. Mathematical functions are similar: they're rules that transform inputs into outputs.

**Mathematical Definition**

A function takes an input (x) and produces exactly one output (y).

Notation: y equals f open-parenthesis x close-parenthesis

Read as: "y equals f of x" or "y is a function of x"

**Example One: Linear Function**

f open-parenthesis x close-parenthesis equals 2 times x plus 3

For any input x, multiply by 2 and add 3:
- f open-parenthesis 0 close-parenthesis equals 3
- f open-parenthesis 1 close-parenthesis equals 5
- f open-parenthesis 5 close-parenthesis equals 13

**Example Two: Quadratic Function**

g open-parenthesis x close-parenthesis equals x squared

For any input x, square it:
- g open-parenthesis 2 close-parenthesis equals 4
- g open-parenthesis 5 close-parenthesis equals 25
- g open-parenthesis minus 3 close-parenthesis equals 9

**Example Three: Pendulum Angle Function**

theta open-parenthesis t close-parenthesis equals 0 point 2 times cosine open-parenthesis 3 times t close-parenthesis

Input is time t, output is angle theta:
- theta open-parenthesis 0 close-parenthesis equals 0 point 2 (initial angle)
- theta open-parenthesis 1 close-parenthesis equals minus 0 point 198 (angle after 1 second)
- theta open-parenthesis 2 close-parenthesis equals minus 0 point 083 (angle after 2 seconds)

**Key Properties**

**Domain**: Set of all valid inputs. For square root, domain is x greater-than-equals 0 (can't take square root of negative).

**Range**: Set of all possible outputs. For x squared, range is y greater-than-equals 0 (squares are never negative).

**One-to-one**: Each input maps to exactly one output (defines a function). One output might correspond to multiple inputs (parabola symmetry).

---

## Graphing Functions

Graphs visualize the relationship between input and output.

**The Coordinate System**

Two perpendicular axes:
- **Horizontal (x-axis)**: Independent variable (input)
- **Vertical (y-axis)**: Dependent variable (output)

Each point has coordinates open-parenthesis x comma y close-parenthesis.

**Example: Graphing y equals x squared**

Create a table of values:

x: -2, -1, 0, 1, 2
y: 4, 1, 0, 1, 4

Plot each point, connect with smooth curve. Result: parabola opening upward.

**In Python**

import space n-u-m-p-y space as space n-p
import space m-a-t-plot-l-i-b dot p-y-plot space as space p-l-t

x space equals space n-p dot linspace open-parenthesis minus 5 comma 5 comma 100 close-parenthesis
y space equals space x space asterisk asterisk space 2

p-l-t dot plot open-parenthesis x comma y close-parenthesis
p-l-t dot xlabel open-parenthesis "x" close-parenthesis
p-l-t dot ylabel open-parenthesis "y" close-parenthesis
p-l-t dot title open-parenthesis "y equals x squared" close-parenthesis
p-l-t dot grid open-parenthesis True close-parenthesis
p-l-t dot show open-parenthesis close-parenthesis

---

## Common Function Types

**Linear: y equals m times x plus b**

Straight line. Slope m, y-intercept b.

Example: y equals 2 times x plus 1
- Slope 2 (rises 2 units for every 1 unit right)
- y-intercept 1 (crosses y-axis at 1)

**Quadratic: y equals a times x squared plus b times x plus c**

Parabola. Opens upward if a greater-than 0, downward if a less-than 0.

Example: y equals x squared minus 4 times x plus 3
- Opens upward (a equals 1 greater-than 0)
- Vertex (minimum) at x equals 2

**Exponential: y equals a times e to the b times x**

Rapid growth (b greater-than 0) or decay (b less-than 0).

Example: y equals 2 times e to the 0 point 5 times x
- Doubles approximately every 1.4 units
- Growth accelerates over time

**Logarithmic: y equals log of x**

Inverse of exponential. Grows slowly, undefined for x less-than-equals 0.

**Trigonometric: sine, cosine** (coming up next)

---

## Angles: Degrees vs Radians

Before trigonometry, we need angle measurement.

**Degrees**

Full circle: 360 degrees
Right angle: 90 degrees
Straight line: 180 degrees

Intuitive, but mathematically awkward.

**Radians**

Radian is the natural mathematical unit for angles.

**Definition**: Angle subtended by an arc equal in length to the radius.

Full circle: 2 times pi radians (approximately 6.28 radians)
Half circle: pi radians (approximately 3.14 radians)
Right angle: pi forward-slash 2 radians (approximately 1.57 radians)

**Conversion**

Radians to degrees: degrees equals radians times 180 forward-slash pi
Degrees to radians: radians equals degrees times pi forward-slash 180

**Examples**

pi radians equals 180 degrees
pi forward-slash 2 radians equals 90 degrees
pi forward-slash 4 radians equals 45 degrees
2 times pi radians equals 360 degrees

**Why Radians in Physics?**

Angular velocity omega has units radians per second. If we used degrees, formulas would include conversion factors everywhere. Radians make formulas cleaner:

Angular displacement equals radius times angle (only true if angle in radians)
Arc length equals radius times angle (only true if angle in radians)

---

## Trigonometric Functions: The Unit Circle

Trigonometry studies relationships between angles and lengths.

**The Unit Circle**

Circle with radius 1, centered at origin.

For any angle theta:
- Start from positive x-axis (3 o'clock position)
- Rotate counterclockwise by angle theta
- Mark the point where you land on the circle

That point has coordinates:
- x-coordinate equals cosine of theta
- y-coordinate equals sine of theta

**Key Angles**

theta equals 0: Point at open-parenthesis 1 comma 0 close-parenthesis
- cosine of 0 equals 1
- sine of 0 equals 0

theta equals pi forward-slash 2 (90 degrees): Point at open-parenthesis 0 comma 1 close-parenthesis
- cosine of pi forward-slash 2 equals 0
- sine of pi forward-slash 2 equals 1

theta equals pi (180 degrees): Point at open-parenthesis minus 1 comma 0 close-parenthesis
- cosine of pi equals minus 1
- sine of pi equals 0

theta equals 3 times pi forward-slash 2 (270 degrees): Point at open-parenthesis 0 comma minus 1 close-parenthesis
- cosine of 3 times pi forward-slash 2 equals 0
- sine of 3 times pi forward-slash 2 equals minus 1

theta equals 2 times pi (360 degrees): Back to start open-parenthesis 1 comma 0 close-parenthesis
- cosine of 2 times pi equals 1
- sine of 2 times pi equals 0

**Pattern Recognition**

Cosine gives horizontal position (x-coordinate).
Sine gives vertical position (y-coordinate).

As you rotate around the circle, cosine and sine oscillate between minus 1 and plus 1.

---

## Sine and Cosine Functions

**Graphing sine**

y equals sine of x

import space n-u-m-p-y space as space n-p
import space m-a-t-plot-l-i-b dot p-y-plot space as space p-l-t

x space equals space n-p dot linspace open-parenthesis 0 comma 2 space asterisk space n-p dot pi comma 100 close-parenthesis
y space equals space n-p dot sin open-parenthesis x close-parenthesis

p-l-t dot plot open-parenthesis x comma y close-parenthesis
p-l-t dot xlabel open-parenthesis "Angle open-parenthesis radians close-parenthesis" close-parenthesis
p-l-t dot ylabel open-parenthesis "sine open-parenthesis angle close-parenthesis" close-parenthesis
p-l-t dot title open-parenthesis "Sine Function" close-parenthesis
p-l-t dot grid open-parenthesis True close-parenthesis
p-l-t dot show open-parenthesis close-parenthesis

You see a smooth wave:
- Starts at 0
- Rises to 1 at pi forward-slash 2
- Falls to 0 at pi
- Drops to minus 1 at 3 times pi forward-slash 2
- Returns to 0 at 2 times pi
- Repeats forever

**Graphing cosine**

y equals cosine of x

y space equals space n-p dot cos open-parenthesis x close-parenthesis

You see a wave similar to sine, but shifted:
- Starts at 1
- Falls to 0 at pi forward-slash 2
- Drops to minus 1 at pi
- Rises to 0 at 3 times pi forward-slash 2
- Returns to 1 at 2 times pi

**Relationship**

cosine of x equals sine of open-parenthesis x plus pi forward-slash 2 close-parenthesis

Cosine is sine shifted left by 90 degrees (pi forward-slash 2 radians).

---

## Recap: Functions and Trigonometry

Let's pause and review:

**Number one**: A function maps inputs to outputs. Notation: y equals f of x.

**Number two**: Graphs visualize functions by plotting input on x-axis, output on y-axis.

**Number three**: Radians are the natural mathematical unit for angles. One radian is the angle subtending an arc equal to the radius.

**Number four**: The unit circle defines sine and cosine. For angle theta, point on circle has coordinates open-parenthesis cosine of theta comma sine of theta close-parenthesis.

**Number five**: Sine and cosine are periodic functions, oscillating between minus 1 and plus 1 with period 2 times pi.

Now let's connect this to pendulums.

---

## Trigonometry in Pendulum Equations

Why do sine and cosine appear in pendulum physics?

**Simple Pendulum Geometry**

Pendulum at angle theta from vertical has:
- Horizontal displacement: L times sine of theta
- Vertical displacement: L times open-parenthesis 1 minus cosine of theta close-parenthesis

Where L is pendulum length.

**Gravitational Torque**

Component of gravity perpendicular to rod:
F equals m times g times sine of theta

This creates restoring torque.

**Small Angle Approximation**

For small theta (less than 0.2 radians approximately equals 11 degrees):
sine of theta approximately equals theta
cosine of theta approximately equals 1

This linearizes the equation:
theta double-dot equals minus open-parenthesis g forward-slash L close-parenthesis times theta

Solution: theta equals theta-naught times cosine of open-parenthesis omega times t close-parenthesis

Where omega equals square root of g forward-slash L.

**Why Cosine?**

Cosine describes oscillation starting from maximum displacement (released from angle theta-naught with zero velocity). The pendulum swings back and forth following a cosine curve.

If you give the pendulum an initial velocity from vertical, you'd use sine instead.

---

## Periodic Functions and Frequency

**Period**

The time for one complete cycle.

For cosine of open-parenthesis omega times t close-parenthesis:
Period T equals 2 times pi forward-slash omega

**Frequency**

Number of cycles per unit time.

f equals 1 forward-slash T equals omega forward-slash 2 times pi

**Example: Simple Pendulum**

L equals 1 meter, g equals 9.81 m/s²
omega equals square root of 9.81 forward-slash 1 equals 3.13 rad/s

Period: T equals 2 times pi forward-slash 3.13 equals 2.01 seconds
Frequency: f equals 1 forward-slash 2.01 equals 0.50 Hz (half cycle per second)

**Graphing Pendulum Motion**

import space n-u-m-p-y space as space n-p
import space m-a-t-plot-l-i-b dot p-y-plot space as space p-l-t

L space equals space 1 point 0
g space equals space 9 point 81
omega space equals space n-p dot sqrt open-parenthesis g forward-slash L close-parenthesis
theta0 space equals space 0 point 3

t space equals space n-p dot linspace open-parenthesis 0 comma 10 comma 1000 close-parenthesis
theta space equals space theta0 space asterisk space n-p dot cos open-parenthesis omega space asterisk space t close-parenthesis

p-l-t dot plot open-parenthesis t comma theta close-parenthesis
p-l-t dot xlabel open-parenthesis "Time open-parenthesis s close-parenthesis" close-parenthesis
p-l-t dot ylabel open-parenthesis "Angle open-parenthesis rad close-parenthesis" close-parenthesis
p-l-t dot title open-parenthesis "Pendulum Oscillation" close-parenthesis
p-l-t dot grid open-parenthesis True close-parenthesis
p-l-t dot show open-parenthesis close-parenthesis

You see smooth sinusoidal oscillation - the signature of harmonic motion.

---

## Amplitude, Phase, and Frequency

General sinusoidal function:
y equals A times cosine of open-parenthesis omega times t plus phi close-parenthesis

**Amplitude (A)**: Maximum displacement from zero. Larger A means bigger swings.

**Angular frequency (omega)**: How fast oscillation occurs (radians per second). Larger omega means faster oscillation.

**Phase (phi)**: Horizontal shift. Changes where the oscillation starts.

**Example: Two Pendulums**

Pendulum 1: theta-one equals 0 point 3 times cosine of 3 times t
- Amplitude 0.3 rad
- Frequency omega equals 3 rad/s
- Phase 0

Pendulum 2: theta-two equals 0 point 2 times cosine of 4 times t
- Amplitude 0.2 rad
- Frequency omega equals 4 rad/s (faster oscillation)
- Phase 0

Graph both:

theta1 space equals space 0 point 3 space asterisk space n-p dot cos open-parenthesis 3 space asterisk space t close-parenthesis
theta2 space equals space 0 point 2 space asterisk space n-p dot cos open-parenthesis 4 space asterisk space t close-parenthesis

p-l-t dot plot open-parenthesis t comma theta1 comma label equals "Pendulum 1" close-parenthesis
p-l-t dot plot open-parenthesis t comma theta2 comma label equals "Pendulum 2" close-parenthesis
p-l-t dot legend open-parenthesis close-parenthesis
p-l-t dot show open-parenthesis close-parenthesis

Pendulum 2 oscillates faster (more cycles in same time).

---

## Pronunciation Guide

Technical terms from this episode with phonetic pronunciations:

- **Function**: FUNK-shun (relationship between input and output)
- **Domain**: doh-MAYN (set of valid inputs)
- **Range**: RAYNJ (set of possible outputs)
- **Radian**: RAY-dee-un (natural angle unit, 2π rad = 360°)
- **Sine**: SYN (trigonometric function, y-coordinate on unit circle)
- **Cosine**: KOH-syn (trigonometric function, x-coordinate on unit circle)
- **Tangent**: TAN-jent (trigonometric function, sine divided by cosine)
- **Periodic**: peer-ee-AH-dik (repeating at regular intervals)
- **Amplitude**: AM-plih-tood (maximum displacement)
- **Frequency**: FREE-kwen-see (cycles per unit time)
- **Phase**: FAYZ (horizontal shift in oscillation)

---

## Why This Matters for Control Systems

Functions, graphing, and trigonometry are everywhere in control:

**Reason One: System Equations Are Functions**

State derivatives are functions of current state and control input:
x-dot equals f open-parenthesis state comma control close-parenthesis

**Reason Two: Oscillations Are Trigonometric**

Pendulum motion, vibrations, AC signals - all described by sine and cosine.

**Reason Three: Analysis Uses Graphs**

Performance plots show:
- Error vs time
- Control effort vs time
- State trajectories in phase space

**Reason Four: Design Requires Intuition**

Understanding function shapes helps you:
- Predict system behavior
- Tune controller gains
- Interpret simulation results

---

## What's Next: Derivatives and Differential Equations

In Episode 11 (the final episode of Phase 1), we'll tackle calculus concepts:

- What derivatives represent physically
- Velocity as derivative of position
- Acceleration as derivative of velocity
- Differential equations: relating quantities to their rates of change
- Why simulation "integrates" equations of motion
- Conceptual understanding without heavy calculation

This final piece connects all the math, physics, and programming you've learned into a complete picture of simulation and control.

---

## Pause and Reflect

Before moving on, test your understanding:

1. What is a function? Give an example.
2. Convert 90 degrees to radians.
3. What are the coordinates of the point on the unit circle at angle pi?
4. Sketch (mentally or on paper) the graph of y equals sine of x from 0 to 2π.
5. Why does cosine appear in the pendulum equation?

If you struggled with any of these, review the relevant section. Practice graphing functions in Python.

---

**Episode 10 of 11** | Phase 1: Foundations

**Previous**: [Episode 9: Double-Inverted Pendulum and Stability](phase1_episode09.md) | **Next**: [Episode 11: Derivatives and Differential Equations](phase1_episode11.md)
