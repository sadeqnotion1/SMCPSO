# Phase 1 NotebookLM Podcast: Episode 6 - NumPy and Matplotlib Basics

**Duration**: 20-22 minutes | **Learning Time**: 3 hours | **Difficulty**: Beginner

---

## Opening Hook

Imagine trying to add two lists of a thousand numbers using basic Python. You'd write a loop, iterate through each element, add them one by one. Now imagine scientists and engineers doing this thousands of times per day for complex calculations. It would be unbearably slow.

That's why NumPy exists. It provides arrays - like Python lists, but optimized for numerical computation. Operations that would take minutes in pure Python take milliseconds with NumPy. And when you need to visualize results? Matplotlib turns your data into publication-quality plots with just a few lines of code.

Today, you'll learn the two libraries that make Python a powerhouse for scientific computing. By the end, you'll be creating arrays, performing mathematical operations, and plotting results like a pro.

---

## What You'll Discover

By listening to this episode, you'll learn:

- What NumPy is and why it's essential
- Creating and manipulating NumPy arrays
- Array operations and broadcasting
- Mathematical functions in NumPy
- What Matplotlib is and its role in visualization
- Creating basic plots: line plots, labels, legends
- Customizing plots for clarity
- Saving plots to files

---

## What Is NumPy?

NumPy (pronounced "num-pie") stands for Numerical Python. It's the foundational library for numerical computing in Python. Nearly every scientific Python package builds on NumPy.

**Why Not Just Use Python Lists?**

Three reasons:

First, **speed**. NumPy arrays are 10 to 100 times faster than Python lists for numerical operations. They're implemented in C under the hood.

Second, **convenience**. You can perform operations on entire arrays at once, no loops needed.

Third, **functionality**. NumPy includes mathematical functions optimized for arrays: trigonometry, linear algebra, statistics, and more.

**Installing NumPy**

If you followed Episode 2 and installed the project dependencies, you already have NumPy. To verify:

python
import space n-u-m-p-y space as space n-p
print open-parenthesis n-p dot version dot version close-parenthesis

You should see the version number, like 1 dot 24 dot 3.

---

## Creating NumPy Arrays

**From Python Lists**

import space n-u-m-p-y space as space n-p

# Create array from list
arr space equals space n-p dot array open-parenthesis open-bracket 1 comma 2 comma 3 comma 4 comma 5 close-bracket close-parenthesis
print open-parenthesis arr close-parenthesis
print open-parenthesis type open-parenthesis arr close-parenthesis close-parenthesis  # <class 'numpy.ndarray'>

**Using NumPy Functions**

# Array of zeros
zeros space equals space n-p dot zeros open-parenthesis 5 close-parenthesis
print open-parenthesis zeros close-parenthesis  # [0. 0. 0. 0. 0.]

# Array of ones
ones space equals space n-p dot ones open-parenthesis 5 close-parenthesis
print open-parenthesis ones close-parenthesis  # [1. 1. 1. 1. 1.]

# Array with range of values
arr space equals space n-p dot arange open-parenthesis 0 comma 10 comma 2 close-parenthesis
print open-parenthesis arr close-parenthesis  # [0 2 4 6 8]

# Linearly spaced values
arr space equals space n-p dot linspace open-parenthesis 0 comma 10 comma 5 close-parenthesis
print open-parenthesis arr close-parenthesis  # [0. 2.5 5. 7.5 10.]

The difference between arange and linspace:
- **arange**: Start, stop, step size (like Python range)
- **linspace**: Start, stop, number of points (evenly spaced)

**linspace** is preferred for scientific computing because you specify exactly how many points you need.

---

## Array Operations

**Element-wise Operations**

Unlike Python lists, you can perform operations on entire NumPy arrays:

arr1 space equals space n-p dot array open-parenthesis open-bracket 1 comma 2 comma 3 close-bracket close-parenthesis
arr2 space equals space n-p dot array open-parenthesis open-bracket 4 comma 5 comma 6 close-bracket close-parenthesis

# Element-wise addition
print open-parenthesis arr1 space plus space arr2 close-parenthesis  # [5 7 9]

# Element-wise multiplication
print open-parenthesis arr1 space asterisk space arr2 close-parenthesis  # [4 10 18]

# Scalar operations
print open-parenthesis arr1 space asterisk space 2 close-parenthesis  # [2 4 6]

# Power
print open-parenthesis arr1 space asterisk asterisk space 2 close-parenthesis  # [1 4 9]

Compare this to Python lists:

list1 space equals space open-bracket 1 comma 2 comma 3 close-bracket
list2 space equals space open-bracket 4 comma 5 comma 6 close-bracket
print open-parenthesis list1 space plus space list2 close-parenthesis  # [1, 2, 3, 4, 5, 6] (concatenation!)

With lists, you'd need a loop:

result space equals space open-bracket close-bracket
for space i space in space range open-parenthesis len open-parenthesis list1 close-parenthesis close-parenthesis colon
    result dot append open-parenthesis list1 open-bracket i close-bracket space plus space list2 open-bracket i close-bracket close-parenthesis

NumPy makes this trivial.

---

## Mathematical Functions

NumPy includes vectorized mathematical functions:

angles space equals space n-p dot array open-parenthesis open-bracket 0 comma n-p dot pi forward-slash 4 comma n-p dot pi forward-slash 2 close-bracket close-parenthesis

# Trigonometry
print open-parenthesis n-p dot sin open-parenthesis angles close-parenthesis close-parenthesis  # [0. 0.707 1.]
print open-parenthesis n-p dot cos open-parenthesis angles close-parenthesis close-parenthesis  # [1. 0.707 0.]

# Exponential and logarithm
arr space equals space n-p dot array open-parenthesis open-bracket 1 comma 2 comma 3 close-bracket close-parenthesis
print open-parenthesis n-p dot exp open-parenthesis arr close-parenthesis close-parenthesis  # [2.71828 7.38906 20.08554]
print open-parenthesis n-p dot log open-parenthesis arr close-parenthesis close-parenthesis  # [0. 0.693 1.099]

# Square root
print open-parenthesis n-p dot sqrt open-parenthesis arr close-parenthesis close-parenthesis  # [1. 1.414 1.732]

# Absolute value
arr space equals space n-p dot array open-parenthesis open-bracket minus 1 comma 2 comma minus 3 close-bracket close-parenthesis
print open-parenthesis n-p dot abs open-parenthesis arr close-parenthesis close-parenthesis  # [1 2 3]

---

## Array Indexing and Slicing

NumPy arrays support similar indexing to Python lists:

arr space equals space n-p dot array open-parenthesis open-bracket 10 comma 20 comma 30 comma 40 comma 50 close-bracket close-parenthesis

print open-parenthesis arr open-bracket 0 close-bracket close-parenthesis  # 10
print open-parenthesis arr open-bracket minus 1 close-bracket close-parenthesis  # 50
print open-parenthesis arr open-bracket 1 colon 4 close-bracket close-parenthesis  # [20 30 40]

**Boolean Indexing**

You can also index with conditions:

arr space equals space n-p dot array open-parenthesis open-bracket 1 comma 5 comma 8 comma 3 comma 10 close-bracket close-parenthesis

# Get all values greater than 5
large space equals space arr open-bracket arr space greater-than space 5 close-bracket
print open-parenthesis large close-parenthesis  # [8 10]

This is extremely powerful for filtering data.

---

## Practical Example: Simulating Pendulum Motion

Let's use NumPy to simulate a simple pendulum:

import space n-u-m-p-y space as space n-p

# Parameters
L space equals space 1 point 0  # Length (m)
g space equals space 9 point 81  # Gravity (m/s^2)
theta0 space equals space 0 point 2  # Initial angle (rad)
omega space equals space n-p dot sqrt open-parenthesis g forward-slash L close-parenthesis  # Angular frequency

# Time array: 0 to 10 seconds, 1000 points
t space equals space n-p dot linspace open-parenthesis 0 comma 10 comma 1000 close-parenthesis

# Calculate angle at each time (simple harmonic motion)
theta space equals space theta0 space asterisk space n-p dot cos open-parenthesis omega space asterisk space t close-parenthesis

# Calculate angular velocity (derivative of angle)
theta underscore dot space equals space minus theta0 space asterisk space omega space asterisk space n-p dot sin open-parenthesis omega space asterisk space t close-parenthesis

print open-parenthesis f-quote Simulated open-brace len open-parenthesis t close-parenthesis close-brace time steps double-quote close-parenthesis
print open-parenthesis f-quote Initial angle colon open-brace theta open-bracket 0 close-bracket colon dot 4-f close-brace rad double-quote close-parenthesis
print open-parenthesis f-quote Final angle colon open-brace theta open-bracket minus 1 close-bracket colon dot 4-f close-brace rad double-quote close-parenthesis

Notice: No loops! We calculated 1000 time points in three lines.

---

## Recap: NumPy Essentials

Let's pause and review NumPy fundamentals:

**Number one**: NumPy provides arrays - like lists, but optimized for numerical operations. Much faster and more convenient.

**Number two**: Create arrays with n-p dot array, n-p dot zeros, n-p dot ones, n-p dot arange, or n-p dot linspace.

**Number three**: Array operations are element-wise. arr1 plus arr2 adds corresponding elements.

**Number four**: NumPy includes vectorized math functions: sin, cos, exp, log, sqrt, and more.

**Number five**: Boolean indexing lets you filter arrays with conditions: arr open-bracket arr greater-than 5 close-bracket.

Now let's visualize data with Matplotlib.

---

## What Is Matplotlib?

Matplotlib is Python's most popular plotting library. It creates static, animated, and interactive visualizations. The name comes from MATLAB, a commercial numerical computing environment - Matplotlib provides similar plotting capabilities in Python.

**Installing Matplotlib**

Like NumPy, if you installed project dependencies, you have Matplotlib. Verify:

python
import space m-a-t-plot-l-i-b dot p-y-plot space as space p-l-t
print open-parenthesis p-l-t dot matplotlib dot version dot version close-parenthesis

---

## Your First Plot

Let's plot the pendulum motion we simulated:

import space n-u-m-p-y space as space n-p
import space m-a-t-plot-l-i-b dot p-y-plot space as space p-l-t

# Generate data (from previous example)
L space equals space 1 point 0
g space equals space 9 point 81
theta0 space equals space 0 point 2
omega space equals space n-p dot sqrt open-parenthesis g forward-slash L close-parenthesis
t space equals space n-p dot linspace open-parenthesis 0 comma 10 comma 1000 close-parenthesis
theta space equals space theta0 space asterisk space n-p dot cos open-parenthesis omega space asterisk space t close-parenthesis

# Create plot
p-l-t dot plot open-parenthesis t comma theta close-parenthesis
p-l-t dot xlabel open-parenthesis "Time open-parenthesis s close-parenthesis" close-parenthesis
p-l-t dot ylabel open-parenthesis "Angle open-parenthesis rad close-parenthesis" close-parenthesis
p-l-t dot title open-parenthesis "Simple Pendulum Motion" close-parenthesis
p-l-t dot grid open-parenthesis True close-parenthesis
p-l-t dot show open-parenthesis close-parenthesis

This opens a window showing a cosine wave - the pendulum swinging back and forth.

Let's break it down:

- **p-l-t dot plot** - Create the plot with x-values (t) and y-values (theta)
- **p-l-t dot xlabel** - Label for horizontal axis
- **p-l-t dot ylabel** - Label for vertical axis
- **p-l-t dot title** - Title at the top
- **p-l-t dot grid** - Show grid lines for readability
- **p-l-t dot show** - Display the plot window

---

## Multiple Lines on One Plot

Let's plot both angle and angular velocity:

import space n-u-m-p-y space as space n-p
import space m-a-t-plot-l-i-b dot p-y-plot space as space p-l-t

# Data
L space equals space 1 point 0
g space equals space 9 point 81
theta0 space equals space 0 point 2
omega space equals space n-p dot sqrt open-parenthesis g forward-slash L close-parenthesis
t space equals space n-p dot linspace open-parenthesis 0 comma 10 comma 1000 close-parenthesis
theta space equals space theta0 space asterisk space n-p dot cos open-parenthesis omega space asterisk space t close-parenthesis
theta underscore dot space equals space minus theta0 space asterisk space omega space asterisk space n-p dot sin open-parenthesis omega space asterisk space t close-parenthesis

# Plot both
p-l-t dot plot open-parenthesis t comma theta comma label equals "Angle" close-parenthesis
p-l-t dot plot open-parenthesis t comma theta underscore dot comma label equals "Angular Velocity" close-parenthesis
p-l-t dot xlabel open-parenthesis "Time open-parenthesis s close-parenthesis" close-parenthesis
p-l-t dot ylabel open-parenthesis "Value" close-parenthesis
p-l-t dot title open-parenthesis "Pendulum Motion" close-parenthesis
p-l-t dot legend open-parenthesis close-parenthesis
p-l-t dot grid open-parenthesis True close-parenthesis
p-l-t dot show open-parenthesis close-parenthesis

The **label** parameter names each line, and **p-l-t dot legend** displays a legend showing which color corresponds to which line.

---

## Customizing Plot Appearance

**Line Styles and Colors**

p-l-t dot plot open-parenthesis t comma theta comma color equals "blue" comma linestyle equals "solid" comma linewidth equals 2 close-parenthesis
p-l-t dot plot open-parenthesis t comma theta underscore dot comma color equals "red" comma linestyle equals "dashed" comma linewidth equals 1 close-parenthesis

Common line styles:
- "solid" or "-"
- "dashed" or "--"
- "dotted" or ":"
- "dashdot" or "-."

Common colors:
- "blue" or "b"
- "red" or "r"
- "green" or "g"
- "black" or "k"
- Hex codes: "#FF5733"

**Markers**

Add markers at data points:

p-l-t dot plot open-parenthesis t comma theta comma marker equals "o" comma markersize equals 3 close-parenthesis

Common markers:
- "o" - circle
- "s" - square
- "^" - triangle
- "x" - x marker
- "+" - plus marker

---

## Subplots: Multiple Plots in One Figure

Sometimes you want separate plots stacked vertically or side-by-side:

import space n-u-m-p-y space as space n-p
import space m-a-t-plot-l-i-b dot p-y-plot space as space p-l-t

# Data
t space equals space n-p dot linspace open-parenthesis 0 comma 10 comma 1000 close-parenthesis
angle1 space equals space 0 point 2 space asterisk space n-p dot cos open-parenthesis 3 space asterisk space t close-parenthesis
angle2 space equals space 0 point 1 space asterisk space n-p dot cos open-parenthesis 5 space asterisk space t close-parenthesis

# Create figure with 2 subplots stacked vertically
fig comma open-parenthesis ax1 comma ax2 close-parenthesis space equals space p-l-t dot subplots open-parenthesis 2 comma 1 comma figsize equals open-parenthesis 10 comma 8 close-parenthesis close-parenthesis

# First subplot
ax1 dot plot open-parenthesis t comma angle1 close-parenthesis
ax1 dot set underscore ylabel open-parenthesis "Angle 1 open-parenthesis rad close-parenthesis" close-parenthesis
ax1 dot set underscore title open-parenthesis "First Pendulum" close-parenthesis
ax1 dot grid open-parenthesis True close-parenthesis

# Second subplot
ax2 dot plot open-parenthesis t comma angle2 close-parenthesis
ax2 dot set underscore xlabel open-parenthesis "Time open-parenthesis s close-parenthesis" close-parenthesis
ax2 dot set underscore ylabel open-parenthesis "Angle 2 open-parenthesis rad close-parenthesis" close-parenthesis
ax2 dot set underscore title open-parenthesis "Second Pendulum" close-parenthesis
ax2 dot grid open-parenthesis True close-parenthesis

p-l-t dot tight underscore layout open-parenthesis close-parenthesis
p-l-t dot show open-parenthesis close-parenthesis

**p-l-t dot subplots** creates a figure with multiple axes (subplots). The arguments are (rows, columns). Here we have 2 rows, 1 column.

**p-l-t dot tight underscore layout** automatically adjusts spacing to prevent overlaps.

---

## Saving Plots to Files

Don't just display plots - save them for reports and presentations:

p-l-t dot plot open-parenthesis t comma theta close-parenthesis
p-l-t dot xlabel open-parenthesis "Time open-parenthesis s close-parenthesis" close-parenthesis
p-l-t dot ylabel open-parenthesis "Angle open-parenthesis rad close-parenthesis" close-parenthesis
p-l-t dot title open-parenthesis "Pendulum Motion" close-parenthesis
p-l-t dot grid open-parenthesis True close-parenthesis
p-l-t dot savefig open-parenthesis "pendulum underscore motion dot png" comma dpi equals 300 close-parenthesis
p-l-t dot show open-parenthesis close-parenthesis

**p-l-t dot savefig** saves the figure to a file. Common formats:
- PNG: Raster format, good for screens
- PDF: Vector format, perfect for publications
- SVG: Vector format, editable in Illustrator/Inkscape

**dpi** (dots per inch) controls resolution. 300 dpi is publication quality.

---

## Practical Example: Double Pendulum State Over Time

Let's create a multi-panel plot showing all state variables:

import space n-u-m-p-y space as space n-p
import space m-a-t-plot-l-i-b dot p-y-plot space as space p-l-t

# Simulate (simplified)
t space equals space n-p dot linspace open-parenthesis 0 comma 10 comma 500 close-parenthesis
cart underscore pos space equals space 0 point 1 space asterisk space n-p dot sin open-parenthesis 0 point 5 space asterisk space t close-parenthesis
angle1 space equals space 0 point 2 space asterisk space n-p dot exp open-parenthesis minus 0 point 1 space asterisk space t close-parenthesis space asterisk space n-p dot cos open-parenthesis 3 space asterisk space t close-parenthesis
angle2 space equals space 0 point 15 space asterisk space n-p dot exp open-parenthesis minus 0 point 15 space asterisk space t close-parenthesis space asterisk space n-p dot cos open-parenthesis 4 space asterisk space t close-parenthesis

# Create 3x1 subplot
fig comma open-parenthesis ax1 comma ax2 comma ax3 close-parenthesis space equals space p-l-t dot subplots open-parenthesis 3 comma 1 comma figsize equals open-parenthesis 10 comma 10 close-parenthesis close-parenthesis

# Cart position
ax1 dot plot open-parenthesis t comma cart underscore pos comma color equals "blue" close-parenthesis
ax1 dot set underscore ylabel open-parenthesis "Cart Position open-parenthesis m close-parenthesis" close-parenthesis
ax1 dot set underscore title open-parenthesis "Double Inverted Pendulum State Variables" close-parenthesis
ax1 dot grid open-parenthesis True close-parenthesis

# First pendulum angle
ax2 dot plot open-parenthesis t comma angle1 comma color equals "green" close-parenthesis
ax2 dot set underscore ylabel open-parenthesis "Angle 1 open-parenthesis rad close-parenthesis" close-parenthesis
ax2 dot grid open-parenthesis True close-parenthesis

# Second pendulum angle
ax3 dot plot open-parenthesis t comma angle2 comma color equals "red" close-parenthesis
ax3 dot set underscore xlabel open-parenthesis "Time open-parenthesis s close-parenthesis" close-parenthesis
ax3 dot set underscore ylabel open-parenthesis "Angle 2 open-parenthesis rad close-parenthesis" close-parenthesis
ax3 dot grid open-parenthesis True close-parenthesis

p-l-t dot tight underscore layout open-parenthesis close-parenthesis
p-l-t dot savefig open-parenthesis "state underscore variables dot png" comma dpi equals 300 close-parenthesis
p-l-t dot show open-parenthesis close-parenthesis

This creates a professional multi-panel figure showing how all three state variables evolve over time.

---

## Pronunciation Guide

Technical terms from this episode with phonetic pronunciations:

- **NumPy**: NUM-pie (Numerical Python)
- **Matplotlib**: MAT-plot-lib (MATLAB-like plotting library)
- **Array**: uh-RAY (data structure for numerical computing)
- **Element-wise**: EL-uh-ment-wize (operation on corresponding elements)
- **Vectorized**: VEK-tor-ized (operation applied to entire array at once)
- **Broadcasting**: BRAWD-cast-ing (automatic array shape matching)
- **Subplot**: SUB-plot (individual plot within a figure)
- **Axes**: AK-seez (individual subplot object, plural of axis)
- **DPI**: "d-p-i" (dots per inch, resolution measure)
- **Linspace**: LIN-space (linearly spaced values)

---

## Why This Matters for Control Systems

NumPy and Matplotlib are the backbone of control system simulation and analysis:

**Reason One: Fast Numerical Computation**

Simulating 10 seconds at 0.01-second time steps = 1000 calculations. NumPy handles this efficiently without loops.

**Reason Two: State Vector Operations**

State vectors are NumPy arrays. All operations (addition, scaling, dot products) are vectorized and fast.

**Reason Three: Visualization**

You can't understand system behavior without plotting. Matplotlib shows you:
- Angle over time
- Control effort over time
- Phase portraits
- Error convergence

**Reason Four: Analysis**

NumPy provides statistical functions (mean, std, max, min) for analyzing controller performance. Matplotlib visualizes these metrics.

The DIP-SMC-PSO project uses both libraries extensively. Every simulation produces NumPy arrays of results. Every plot uses Matplotlib.

---

## What's Next: Virtual Environments and Git

In Episode 7, we'll learn essential development tools:

- Virtual environments: Isolating project dependencies
- Installing packages with pip
- Git basics: Version control
- Cloning the DIP-SMC-PSO repository
- Committing changes and collaboration

These tools enable professional development workflows and ensure your environment matches the project requirements.

---

## Pause and Reflect

Before moving on, test your understanding:

1. What's the difference between n-p dot arange and n-p dot linspace?
2. How do you perform element-wise addition of two NumPy arrays?
3. What function creates linearly spaced values from 0 to 10 with 100 points?
4. How do you add a legend to a Matplotlib plot?
5. Write code to plot y equals x squared from x equals 0 to x equals 10.

If you struggled with any of these, review the relevant section. Practice by creating arrays and plots in your Python environment.

---

**Episode 6 of 11** | Phase 1: Foundations

**Previous**: [Episode 5: Lists and Dictionaries](phase1_episode05.md) | **Next**: [Episode 7: Virtual Environments and Git](phase1_episode07.md)
