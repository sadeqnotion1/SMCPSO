<!-- AUTO-GENERATED from .project/ai/edu/ - DO NOT EDIT DIRECTLY -->
<!-- Source: .project/ai/edu/phase1/mathematics-essentials.md -->
<!-- Generated: 2025-11-11 13:29:26 -->

# Mathematics Essentials - Mathematical Toolkit for Control Systems

**Time Required**: 10-12 hours
**Prerequisites**: Algebra basics, `python-fundamentals.md` (for computations)

------

## What You'll Learn

By the end of this module, you'll understand:
- Derivatives and integrals (calculus basics)
- Vectors and matrices (linear algebra)
- Differential equations
- Taylor series and linearization
- Complex numbers (brief introduction)
- How to implement these concepts in Python

------

## 1. Functions and Notation

### Function Basics

A **function** maps inputs to outputs:

```
f(x) = x²

f(3) = 9
f(-2) = 4
```

### Common Functions

**Linear**: `f(x) = mx + b`
- Graph is a straight line
- Example: `f(x) = 2x + 1`

**Quadratic**: `f(x) = ax² + bx + c`
- Graph is a parabola
- Example: `f(x) = x² - 4x + 3`

**Exponential**: `f(x) = aᵉˣ` or `f(x) = e^(kx)`
- Rapid growth or decay
- Example: `f(x) = e^(-0.1x)` (exponential decay)

**Trigonometric**: `sin(x)`, `cos(x)`, `tan(x)`
- Periodic functions (repeating patterns)

### Python Implementation

```python
import numpy as np
import matplotlib.pyplot as plt

# Define functions
def f(x):
    return x**2

def g(x):
    return np.exp(-0.1 * x)

def h(x):
    return np.sin(x)

# Plot
x = np.linspace(-5, 5, 100)
plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.plot(x, f(x))
plt.title("f(x) = x²")
plt.grid()

plt.subplot(1, 3, 2)
plt.plot(x, g(x))
plt.title("g(x) = e^(-0.1x)")
plt.grid()

plt.subplot(1, 3, 3)
plt.plot(x, h(x))
plt.title("h(x) = sin(x)")
plt.grid()

plt.tight_layout()
plt.show()
```

------

## 2. Calculus: Derivatives

### What is a Derivative?

The derivative measures **rate of change**. It answers: "How fast is this function changing?"

**Notation**:
```
f'(x)  or  df/dx  or  (d/dx)f(x)
```

**Interpretation**:
- Derivative = slope of the tangent line
- Derivative = instantaneous rate of change

### Geometric Interpretation

```python
import numpy as np
import matplotlib.pyplot as plt

# Function: f(x) = x²
x = np.linspace(0, 5, 100)
f = x**2

# Point of interest
x0 = 2
y0 = x0**2

# Derivative at x0: f'(x) = 2x, so f'(2) = 4
slope = 2 * x0

# Tangent line: y = slope * (x - x0) + y0
x_tangent = np.linspace(1, 3, 50)
y_tangent = slope * (x_tangent - x0) + y0

plt.figure()
plt.plot(x, f, label="f(x) = x²")
plt.plot(x_tangent, y_tangent, 'r--', label=f"Tangent at x={x0}")
plt.plot(x0, y0, 'ro', markersize=10)
plt.legend()
plt.grid()
plt.title("Derivative as Slope")
plt.show()
```

### Common Derivatives

| Function | Derivative |
|----------|------------|
| `f(x) = c` (constant) | `f'(x) = 0` |
| `f(x) = x` | `f'(x) = 1` |
| `f(x) = x²` | `f'(x) = 2x` |
| `f(x) = xⁿ` | `f'(x) = n·xⁿ⁻¹` |
| `f(x) = eˣ` | `f'(x) = eˣ` |
| `f(x) = sin(x)` | `f'(x) = cos(x)` |
| `f(x) = cos(x)` | `f'(x) = -sin(x)` |
| `f(x) = ln(x)` | `f'(x) = 1/x` |

### Derivative Rules

**Sum Rule**:
```
(f + g)' = f' + g'
```

**Product Rule**:
```
(f · g)' = f' · g + f · g'
```

**Chain Rule** (composite functions):
```
(f(g(x)))' = f'(g(x)) · g'(x)
```

**Example**:
```
f(x) = sin(x²)

Let u = x², then f(x) = sin(u)
f'(x) = cos(u) · (du/dx) = cos(x²) · 2x = 2x·cos(x²)
```

### Numerical Derivatives in Python

```python
def numerical_derivative(f, x, h=1e-5):
    """
    Approximate derivative using finite difference.
    f'(x) ≈ (f(x+h) - f(x)) / h
    """
    return (f(x + h) - f(x)) / h

# Example
def f(x):
    return x**2

x = 3
analytical = 2 * x  # Exact derivative: f'(x) = 2x
numerical = numerical_derivative(f, x)

print(f"Analytical: {analytical}")
print(f"Numerical: {numerical}")
print(f"Error: {abs(analytical - numerical)}")
```

------

## 3. Calculus: Integrals

### What is an Integral?

The integral measures **accumulated change**. It answers: "What's the total amount of change?"

**Notation**:
```
∫ f(x) dx
```

**Interpretation**:
- Integral = area under the curve
- Integral = anti-derivative (reverse of derivative)

### Definite vs. Indefinite Integrals

**Indefinite** (general anti-derivative):
```
∫ x² dx = (1/3)x³ + C
```

**Definite** (area from a to b):
```
∫[a to b] f(x) dx = F(b) - F(a)
```

Where F is the anti-derivative of f.

### Common Integrals

| Function | Integral |
|----------|----------|
| `f(x) = 0` | `∫ 0 dx = C` |
| `f(x) = 1` | `∫ 1 dx = x + C` |
| `f(x) = x` | `∫ x dx = (1/2)x² + C` |
| `f(x) = xⁿ` | `∫ xⁿ dx = xⁿ⁺¹/(n+1) + C` |
| `f(x) = eˣ` | `∫ eˣ dx = eˣ + C` |
| `f(x) = sin(x)` | `∫ sin(x) dx = -cos(x) + C` |
| `f(x) = cos(x)` | `∫ cos(x) dx = sin(x) + C` |

### Numerical Integration in Python

```python
from scipy.integrate import quad

# Define function
def f(x):
    return x**2

# Analytical integral from 0 to 3: (1/3)x³ |[0 to 3] = 9
analytical = (1/3) * 3**3

# Numerical integration
numerical, error = quad(f, 0, 3)

print(f"Analytical: {analytical}")
print(f"Numerical: {numerical}")
print(f"Error estimate: {error}")
```

------

## 4. Differential Equations

### What is a Differential Equation?

An equation involving derivatives. It describes how a quantity changes over time.

**Example**:
```
dy/dt = -k·y
```

This says: "The rate of change of y is proportional to -y" (exponential decay).

### First-Order Linear ODE

**General form**:
```
dy/dt = f(t, y)
```

**Example: Exponential Growth**:
```
dy/dt = k·y
Solution: y(t) = y₀·e^(kt)
```

**Example: Exponential Decay**:
```
dy/dt = -k·y
Solution: y(t) = y₀·e^(-kt)
```

### Second-Order Linear ODE

**General form**:
```
d²y/dt² + a·dy/dt + b·y = 0
```

**Example: Harmonic Oscillator**:
```
d²y/dt² + ω²·y = 0
Solution: y(t) = A·cos(ωt) + B·sin(ωt)
```

This describes a pendulum (small angles), spring-mass system, etc.

### Solving ODEs in Python

```python
from scipy.integrate import solve_ivp
import numpy as np
import matplotlib.pyplot as plt

# Define ODE: dy/dt = -0.5 * y
def dydt(t, y):
    return -0.5 * y

# Initial condition
y0 = [10]

# Time span
t_span = (0, 10)
t_eval = np.linspace(0, 10, 100)

# Solve
solution = solve_ivp(dydt, t_span, y0, t_eval=t_eval)

# Plot
plt.figure()
plt.plot(solution.t, solution.y[0], label="Numerical")

# Analytical solution: y(t) = 10 * e^(-0.5t)
analytical = 10 * np.exp(-0.5 * solution.t)
plt.plot(solution.t, analytical, '--', label="Analytical")

plt.xlabel("Time")
plt.ylabel("y(t)")
plt.legend()
plt.grid()
plt.title("Exponential Decay")
plt.show()
```

------

## 5. Vectors

### What is a Vector?

A vector is a list of numbers representing magnitude and direction.

**2D Vector**:
```
v = [3, 4]  (or in column form: v = [3]
                                    [4])
```

**Magnitude (length)**:
```
||v|| = sqrt(3² + 4²) = 5
```

### Vector Operations

**Addition**:
```python
import numpy as np

v1 = np.array([1, 2])
v2 = np.array([3, 4])

v_sum = v1 + v2  # [4, 6]
```

**Scalar Multiplication**:
```python
v = np.array([2, 3])
scaled = 3 * v  # [6, 9]
```

**Dot Product**:
```python
v1 = np.array([1, 2, 3])
v2 = np.array([4, 5, 6])

dot = np.dot(v1, v2)  # 1*4 + 2*5 + 3*6 = 32
```

**Magnitude**:
```python
v = np.array([3, 4])
magnitude = np.linalg.norm(v)  # 5.0
```

### Geometric Interpretation

```python
import matplotlib.pyplot as plt
import numpy as np

# Define vectors
v1 = np.array([3, 2])
v2 = np.array([1, 4])
v_sum = v1 + v2

# Plot
origin = [0, 0]
plt.figure()
plt.quiver(*origin, *v1, angles='xy', scale_units='xy', scale=1, color='r', label='v1')
plt.quiver(*origin, *v2, angles='xy', scale_units='xy', scale=1, color='b', label='v2')
plt.quiver(*origin, *v_sum, angles='xy', scale_units='xy', scale=1, color='g', label='v1+v2')
plt.xlim(-1, 6)
plt.ylim(-1, 7)
plt.grid()
plt.legend()
plt.title("Vector Addition")
plt.show()
```

------

## 6. Matrices

### What is a Matrix?

A 2D array of numbers. Used to represent linear transformations, systems of equations, etc.

**Example**:
```
A = [1  2]
    [3  4]
```

### Matrix Operations in NumPy

```python
import numpy as np

# Create matrices
A = np.array([[1, 2],
              [3, 4]])

B = np.array([[5, 6],
              [7, 8]])

# Matrix addition
C = A + B
print(C)
# [[ 6  8]
#  [10 12]]

# Matrix multiplication (not element-wise!)
D = A @ B  # or np.matmul(A, B)
print(D)
# [[19 22]
#  [43 50]]

# Element-wise multiplication
E = A * B
print(E)
# [[ 5 12]
#  [21 32]]
```

### Special Matrices

**Identity Matrix** (like "1" for matrices):
```python
I = np.eye(3)
# [[1. 0. 0.]
#  [0. 1. 0.]
#  [0. 0. 1.]]
```

**Zero Matrix**:
```python
Z = np.zeros((2, 3))
# [[0. 0. 0.]
#  [0. 0. 0.]]
```

**Diagonal Matrix**:
```python
D = np.diag([1, 2, 3])
# [[1 0 0]
#  [0 2 0]
#  [0 0 3]]
```

### Matrix-Vector Multiplication

```python
A = np.array([[1, 2],
              [3, 4]])

v = np.array([5, 6])

result = A @ v
print(result)  # [17 39]

# Calculation:
# [1*5 + 2*6] = [17]
# [3*5 + 4*6]   [39]
```

------

## 7. Linear Systems

### System of Linear Equations

```
2x + 3y = 8
4x - y = 2
```

**Matrix Form** (Ax = b):
```
[2  3] [x]   [8]
[4 -1] [y] = [2]
```

### Solving in Python

```python
import numpy as np

# Coefficient matrix
A = np.array([[2, 3],
              [4, -1]])

# Right-hand side
b = np.array([8, 2])

# Solve Ax = b
x = np.linalg.solve(A, b)
print(x)  # [1. 2.]

# Verify
print(A @ x)  # [8. 2.] ✓
```

------

## 8. Eigenvalues and Eigenvectors

### What are Eigenvalues?

An **eigenvector** of matrix A is a vector v such that:

```
A·v = λ·v
```

Where λ (lambda) is the **eigenvalue**.

**Meaning**: Matrix A just scales v by λ, without changing its direction.

### Computing in Python

```python
import numpy as np

A = np.array([[4, 2],
              [1, 3]])

# Compute eigenvalues and eigenvectors
eigenvalues, eigenvectors = np.linalg.eig(A)

print("Eigenvalues:", eigenvalues)
# [5. 2.]

print("Eigenvectors:")
print(eigenvectors)
# [[ 0.89442719 -0.70710678]
#  [ 0.4472136   0.70710678]]

# Verify for first eigenvalue/eigenvector
v1 = eigenvectors[:, 0]
lambda1 = eigenvalues[0]

print("A·v1:", A @ v1)
print("λ1·v1:", lambda1 * v1)
# They match!
```

### Why Important for Control?

**Stability analysis**: Eigenvalues tell you if a system is stable.

- All eigenvalues have **negative real parts** → Stable
- Any eigenvalue has **positive real part** → Unstable

------

## 9. Matrix Inverse

### What is an Inverse?

For matrix A, the inverse A⁻¹ satisfies:

```
A · A⁻¹ = I  (identity matrix)
```

### Computing Inverse

```python
import numpy as np

A = np.array([[4, 7],
              [2, 6]])

# Compute inverse
A_inv = np.linalg.inv(A)
print(A_inv)

# Verify
I = A @ A_inv
print(I)
# [[1. 0.]
#  [0. 1.]]  (identity matrix)
```

### Solving Linear Systems with Inverse

```
Ax = b
x = A⁻¹b
```

But **don't do this in practice**! Use `np.linalg.solve(A, b)` instead (faster, more stable).

------

## 10. Taylor Series and Linearization

### Taylor Series

Approximate a function as a polynomial:

```
f(x) ≈ f(a) + f'(a)·(x-a) + (f''(a)/2!)·(x-a)² + ...
```

**First-order approximation** (linear):
```
f(x) ≈ f(a) + f'(a)·(x-a)
```

### Linearization Example

**Function**: `f(x) = sin(x)`

**Near x = 0**:
```
sin(x) ≈ x  (for small x)
```

**Derivation**:
```
f(0) = sin(0) = 0
f'(0) = cos(0) = 1

Taylor: sin(x) ≈ 0 + 1·(x - 0) = x
```

### Why Important for Control?

Nonlinear systems (like inverted pendulum) are hard to control. We **linearize** around equilibrium points to make them easier.

**Example: Pendulum**:
```
Original: d²θ/dt² = -(g/L)·sin(θ)
Linearized (θ ≈ 0): d²θ/dt² ≈ -(g/L)·θ
```

### Python Example

```python
import numpy as np
import matplotlib.pyplot as plt

# Function and its linear approximation
x = np.linspace(-1, 1, 100)
f_exact = np.sin(x)
f_linear = x  # sin(x) ≈ x near 0

plt.figure()
plt.plot(x, f_exact, label="sin(x)")
plt.plot(x, f_linear, '--', label="Linear approx: x")
plt.legend()
plt.grid()
plt.title("Linearization of sin(x) near 0")
plt.show()
```

------

## 11. State-Space Representation

### What is State Space?

A way to represent dynamic systems using vectors and matrices.

**General form**:
```
dx/dt = A·x + B·u
y = C·x + D·u
```

Where:
- `x` = state vector (what you care about: position, velocity, etc.)
- `u` = control input (what you can change: force, torque, etc.)
- `y` = output (what you measure)
- `A, B, C, D` = system matrices

### Example: Mass-Spring-Damper

**Physical system**:
```
m·d²x/dt² + c·dx/dt + k·x = F
```

**State-space form**:

Define states: `x1 = x` (position), `x2 = dx/dt` (velocity)

```
dx1/dt = x2
dx2/dt = -(k/m)·x1 - (c/m)·x2 + (1/m)·F
```

**Matrix form**:
```
[dx1/dt]   [  0      1  ] [x1]   [  0  ]
[dx2/dt] = [-k/m  -c/m ] [x2] + [1/m  ] F
```

### Python Simulation

```python
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# System parameters
m = 1.0   # mass
c = 0.5   # damping
k = 2.0   # spring constant

# State-space matrices
A = np.array([[0, 1],
              [-k/m, -c/m]])

B = np.array([[0],
              [1/m]])

# Dynamics function
def dynamics(t, x, A, B, u_func):
    u = u_func(t)
    dxdt = A @ x + B @ u
    return dxdt

# Control input (force)
def u_func(t):
    return [0]  # No external force

# Initial condition
x0 = [1, 0]  # x=1, v=0

# Simulate
t_span = (0, 10)
t_eval = np.linspace(0, 10, 200)
sol = solve_ivp(
    lambda t, x: dynamics(t, x, A, B, u_func),
    t_span,
    x0,
    t_eval=t_eval
)

# Plot
plt.figure(figsize=(10, 6))
plt.plot(sol.t, sol.y[0], label="Position")
plt.plot(sol.t, sol.y[1], label="Velocity")
plt.xlabel("Time (s)")
plt.ylabel("State")
plt.legend()
plt.grid()
plt.title("Mass-Spring-Damper Response")
plt.show()
```

------

## 12. Complex Numbers (Brief Intro)

### What are Complex Numbers?

Numbers with real and imaginary parts:

```
z = a + bi
```

Where:
- `a` = real part
- `b` = imaginary part
- `i` = sqrt(-1)

### Why Important?

- Eigenvalues can be complex
- Complex eigenvalues indicate oscillatory behavior
- Stability analysis uses complex plane

### Python Operations

```python
import numpy as np

# Create complex numbers
z1 = 3 + 4j
z2 = 1 - 2j

# Operations
print(z1 + z2)  # (4+2j)
print(z1 * z2)  # (11-2j)

# Magnitude
print(abs(z1))  # 5.0

# Real and imaginary parts
print(z1.real)  # 3.0
print(z1.imag)  # 4.0

# Complex conjugate
print(np.conj(z1))  # (3-4j)
```

------

## 13. Optimization Basics

### What is Optimization?

Finding the input that minimizes (or maximizes) an objective function.

**Example**: Find x that minimizes `f(x) = (x - 3)²`

**Calculus approach**:
1. Take derivative: `f'(x) = 2(x - 3)`
2. Set to zero: `2(x - 3) = 0`
3. Solve: `x = 3`

### Gradient Descent

Iterative method to find minimum:

```python
def gradient_descent(f, df, x0, lr=0.1, n_iter=100):
    """
    Minimize f using gradient descent.
    f: objective function
    df: derivative of f
    x0: initial guess
    lr: learning rate
    n_iter: number of iterations
    """
    x = x0
    history = [x]

    for i in range(n_iter):
        x = x - lr * df(x)
        history.append(x)

    return x, history

# Example: minimize f(x) = (x - 3)²
def f(x):
    return (x - 3)**2

def df(x):
    return 2 * (x - 3)

x_min, history = gradient_descent(f, df, x0=0, lr=0.1, n_iter=50)
print(f"Minimum at x = {x_min:.6f}")
```

------

## 14. Practice Exercises

### Exercise 1: Derivative Practice

```python
# Compute derivatives numerically and compare to analytical

def f(x):
    return x**3 - 2*x**2 + x - 5

def df_analytical(x):
    return 3*x**2 - 4*x + 1

x_test = 2.0
df_numerical = numerical_derivative(f, x_test)
df_exact = df_analytical(x_test)

print(f"Numerical: {df_numerical}")
print(f"Analytical: {df_exact}")
print(f"Error: {abs(df_numerical - df_exact)}")
```

### Exercise 2: Solve ODE System

```python
# Solve the coupled ODEs:
# dx/dt = -y
# dy/dt = x
# (This represents circular motion)

def system(t, state):
    x, y = state
    dxdt = -y
    dydt = x
    return [dxdt, dydt]

# Initial condition
state0 = [1, 0]

# Solve
t_span = (0, 2*np.pi)
t_eval = np.linspace(0, 2*np.pi, 100)
sol = solve_ivp(system, t_span, state0, t_eval=t_eval)

# Plot trajectory
plt.figure()
plt.plot(sol.y[0], sol.y[1])
plt.xlabel("x")
plt.ylabel("y")
plt.axis('equal')
plt.grid()
plt.title("Circular Motion")
plt.show()
```

### Exercise 3: Eigenvalue Stability

```python
# Given system matrices, determine stability

A1 = np.array([[-1, 0],
               [0, -2]])

A2 = np.array([[1, 0],
               [0, -1]])

def check_stability(A):
    eigenvalues = np.linalg.eigvals(A)
    print("Eigenvalues:", eigenvalues)

    if np.all(eigenvalues.real < 0):
        print("System is STABLE")
    else:
        print("System is UNSTABLE")

print("System 1:")
check_stability(A1)

print("\nSystem 2:")
check_stability(A2)
```

------

## 15. Next Steps

You've completed Phase 1! You're ready for **Phase 2: Core Concepts** (`.ai/edu/beginner-roadmap.md`) when you can:

- [ ] Compute derivatives and integrals
- [ ] Solve differential equations in Python
- [ ] Perform vector and matrix operations
- [ ] Compute eigenvalues and eigenvectors
- [ ] Linearize nonlinear functions
- [ ] Set up state-space representations
- [ ] Understand optimization basics

------

## Additional Resources

### Books
- "Calculus" by James Stewart
- "Linear Algebra and Its Applications" by Gilbert Strang
- "Differential Equations" by Paul Blanchard

### Online Courses
- Khan Academy: Calculus, Linear Algebra
- MIT OpenCourseWare: 18.01 (Calculus), 18.06 (Linear Algebra)
- 3Blue1Brown YouTube: "Essence of Calculus", "Essence of Linear Algebra"

### Interactive
- Desmos Graphing Calculator: https://www.desmos.com/calculator
- Matrix Calculator: https://www.mathsisfun.com/algebra/matrix-calculator.html

------

**Last Updated**: 2025-10-17
**Estimated Time**: 10-12 hours
**Next Module**: Phase 2 in `.ai/edu/beginner-roadmap.md`
