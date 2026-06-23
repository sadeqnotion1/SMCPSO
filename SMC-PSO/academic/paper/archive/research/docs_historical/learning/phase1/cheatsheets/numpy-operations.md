<!-- AUTO-GENERATED from .project/ai/edu/ - DO NOT EDIT DIRECTLY -->
<!-- Source: .project/ai/edu/phase1/cheatsheets/numpy-operations.md -->
<!-- Generated: 2025-11-11 13:29:26 -->

# NumPy Operations - Quick Cheatsheet

**Scientific Computing with NumPy Arrays**

```python
import numpy as np
```

------

## Creating Arrays

```python
# From lists
a = np.array([1, 2, 3])
b = np.array([[1, 2], [3, 4]])

# Special arrays
np.zeros(5)              # [0. 0. 0. 0. 0.]
np.ones((2, 3))          # 2x3 array of ones
np.full((2, 2), 7)       # 2x2 array filled with 7
np.eye(3)                # 3x3 identity matrix

# Ranges
np.arange(0, 10, 2)      # [0 2 4 6 8]
np.linspace(0, 1, 5)     # [0. 0.25 0.5 0.75 1.]

# Random
np.random.rand(3)        # Uniform [0, 1)
np.random.randn(3)       # Standard normal
np.random.randint(0, 10, size=5)  # Random integers
```

------

## Array Attributes

```python
arr = np.array([[1, 2, 3], [4, 5, 6]])

arr.shape       # (2, 3)
arr.ndim        # 2 (number of dimensions)
arr.size        # 6 (total elements)
arr.dtype       # dtype('int64')
```

------

## Indexing and Slicing

```python
a = np.array([10, 20, 30, 40, 50])

# Basic indexing
a[0]            # 10
a[-1]           # 50
a[1:4]          # [20 30 40]
a[::2]          # [10 30 50] (every 2nd)

# 2D arrays
b = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

b[0, 0]         # 1 (row 0, col 0)
b[1, :]         # [4 5 6] (row 1, all cols)
b[:, 2]         # [3 6 9] (all rows, col 2)
b[0:2, 1:]      # [[2 3], [5 6]]

# Boolean indexing
mask = a > 25
a[mask]         # [30 40 50]
a[a > 25]       # Same as above
```

------

## Reshaping

```python
a = np.arange(12)  # [0 1 2 ... 11]

a.reshape(3, 4)    # 3x4 array
a.reshape(2, 6)    # 2x6 array
a.reshape(2, -1)   # 2 rows, auto cols

# Flatten
b = np.array([[1, 2], [3, 4]])
b.flatten()        # [1 2 3 4]
b.ravel()          # [1 2 3 4] (view if possible)

# Transpose
b.T                # [[1 3], [2 4]]
```

------

## Array Operations (Element-wise)

```python
a = np.array([1, 2, 3, 4])
b = np.array([10, 20, 30, 40])

# Arithmetic
a + b              # [11 22 33 44]
a - b              # [-9 -18 -27 -36]
a * b              # [10 40 90 160]
a / b              # [0.1 0.1 0.1 0.1]
a ** 2             # [1 4 9 16]

# With scalars
a + 10             # [11 12 13 14]
a * 2              # [2 4 6 8]
```

------

## Mathematical Functions

```python
a = np.array([1, 2, 3, 4])

# Basic math
np.sqrt(a)         # [1. 1.414 1.732 2.]
np.exp(a)          # [2.718 7.389 20.086 54.598]
np.log(a)          # [0. 0.693 1.099 1.386]
np.abs(a)          # Absolute value

# Trigonometry (angles in radians)
angles = np.array([0, np.pi/2, np.pi])
np.sin(angles)     # [0. 1. 0.]
np.cos(angles)     # [1. 0. -1.]
np.tan(angles)     # [0. 1.633e16 -1.224e-16]

# Rounding
b = np.array([1.2, 2.7, 3.5])
np.round(b)        # [1. 3. 4.]
np.floor(b)        # [1. 2. 3.]
np.ceil(b)         # [2. 3. 4.]
```

------

## Aggregation Functions

```python
a = np.array([1, 2, 3, 4, 5])

np.sum(a)          # 15
np.mean(a)         # 3.0
np.std(a)          # 1.414 (standard deviation)
np.var(a)          # 2.0 (variance)
np.min(a)          # 1
np.max(a)          # 5
np.argmin(a)       # 0 (index of min)
np.argmax(a)       # 4 (index of max)

# 2D arrays (axis matters!)
b = np.array([[1, 2, 3], [4, 5, 6]])

np.sum(b)          # 21 (all elements)
np.sum(b, axis=0)  # [5 7 9] (sum columns)
np.sum(b, axis=1)  # [6 15] (sum rows)
```

------

## Linear Algebra

```python
# Dot product
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
np.dot(a, b)       # 32 (1*4 + 2*5 + 3*6)

# Matrix multiplication
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
A @ B              # [[19 22], [43 50]]
np.matmul(A, B)    # Same as A @ B

# Matrix operations
np.linalg.inv(A)   # Inverse
np.linalg.det(A)   # Determinant: -2.0
np.linalg.eig(A)   # Eigenvalues and eigenvectors

# Solve Ax = b
A = np.array([[3, 1], [1, 2]])
b = np.array([9, 8])
x = np.linalg.solve(A, b)  # [2. 3.]
```

------

## Broadcasting

NumPy automatically expands arrays for operations:

```python
# Scalar broadcasting
a = np.array([1, 2, 3])
a + 10             # [11 12 13]

# 1D + 2D
a = np.array([1, 2, 3])
b = np.array([[10], [20], [30]])
a + b
# [[11 12 13]
#  [21 22 23]
#  [31 32 33]]

# Rule: dimensions are compatible if:
# 1. They are equal, or
# 2. One of them is 1
```

------

## Stacking and Splitting

```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

# Stacking
np.vstack((a, b))  # [[1 2 3], [4 5 6]]
np.hstack((a, b))  # [1 2 3 4 5 6]
np.column_stack((a, b))  # [[1 4], [2 5], [3 6]]

# Splitting
c = np.array([1, 2, 3, 4, 5, 6])
np.split(c, 3)     # [array([1, 2]), array([3, 4]), array([5, 6])]
```

------

## Copying

```python
a = np.array([1, 2, 3])

# View (shares data)
b = a              # b is a
c = a.view()       # Shallow copy

# Deep copy (independent)
d = a.copy()
```

**⚠️ Important**: Slices are views, not copies!

```python
a = np.array([1, 2, 3, 4, 5])
b = a[1:4]         # View
b[0] = 99
print(a)           # [1 99 3 4 5] (a changed too!)
```

------

## Conditional Operations

```python
a = np.array([1, 2, 3, 4, 5])

# Where
np.where(a > 3, a, 0)  # [0 0 0 4 5] (if > 3: keep, else: 0)

# Clip
np.clip(a, 2, 4)   # [2 2 3 4 4] (clamp to [2, 4])

# Select
conditions = [a < 2, a > 4]
choices = [0, 10]
np.select(conditions, choices, default=a)  # [0 2 3 4 10]
```

------

## Useful Tricks

### Unique Values

```python
a = np.array([1, 2, 2, 3, 3, 3])
np.unique(a)       # [1 2 3]
```

### Sorting

```python
a = np.array([3, 1, 4, 1, 5])
np.sort(a)         # [1 1 3 4 5]
np.argsort(a)      # [1 3 0 2 4] (indices)
```

### Set Operations

```python
a = np.array([1, 2, 3])
b = np.array([2, 3, 4])
np.intersect1d(a, b)   # [2 3]
np.union1d(a, b)       # [1 2 3 4]
np.setdiff1d(a, b)     # [1]
```

### Saving/Loading

```python
# Save
np.save("array.npy", a)
np.savez("arrays.npz", a=a, b=b)  # Multiple arrays

# Load
a = np.load("array.npy")
data = np.load("arrays.npz")
a = data['a']
```

------

## Common Patterns for Control Systems

### Time Arrays

```python
t = np.linspace(0, 10, 1000)  # Time from 0 to 10s, 1000 points
```

### Initial State

```python
x0 = np.zeros(6)  # 6 state variables, all zero
x0[0] = 1.0       # Set initial position
```

### State History

```python
n_states = 6
n_steps = 1000
state_history = np.zeros((n_steps, n_states))
```

### Matrix Operations

```python
# Ax + Bu (state-space)
A = np.array([[0, 1], [-2, -3]])
B = np.array([[0], [1]])
x = np.array([1, 0])
u = 5

x_dot = A @ x + B @ u
```

------

## Performance Tips

1. **Vectorize**: Use array operations instead of loops
   ```python
   # SLOW
   for i in range(len(a)):
       a[i] = a[i] ** 2

   # FAST
   a = a ** 2
   ```

2. **Pre-allocate**: Create arrays with full size upfront
   ```python
   # SLOW
   result = []
   for i in range(1000):
       result.append(i**2)

   # FAST
   result = np.arange(1000) ** 2
   ```

3. **Use views**: Avoid unnecessary copies

------

**Last Updated**: 2025-10-17
**More Info**: https://numpy.org/doc/stable/user/quickstart.html
