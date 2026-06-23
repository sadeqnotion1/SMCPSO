<!-- AUTO-GENERATED from .project/ai/edu/ - DO NOT EDIT DIRECTLY -->
<!-- Source: .project/ai/edu/phase1/python-fundamentals.md -->
<!-- Generated: 2025-11-11 13:29:26 -->

# Python Fundamentals - Programming from Scratch

**Time Required**: 15-18 hours
**Prerequisites**: `computing-basics.md` (Python installed, command line basics)

------

## What You'll Learn

By the end of this module, you'll be able to:
- Write Python programs with variables, loops, and functions
- Work with data structures (lists, dictionaries, arrays)
- Handle errors gracefully
- Use NumPy for numerical computing
- Read and write files
- Debug common Python errors

------

## 1. Your First Python Program

### Interactive Mode (REPL)

```powershell
python
```

Try this:

```python
>>> print("Hello, Python!")
Hello, Python!
>>> 2 + 2
4
>>> "Hello" + " " + "World"
'Hello World'
>>> exit()
```

### Script Mode

Create `first_script.py`:

```python
print("This is my first Python script!")
print("Python makes math easy:")
print(10 * 5)
```

Run it:

```powershell
python first_script.py
```

------

## 2. Variables and Data Types

### Variables: Storing Information

```python
# Variables hold values
name = "Alice"
age = 25
height = 1.75
is_student = True

# Use them
print(f"{name} is {age} years old and {height}m tall")
```

### Data Types

| Type | Description | Example |
|------|-------------|---------|
| `int` | Whole numbers | `42`, `-7`, `0` |
| `float` | Decimal numbers | `3.14`, `-0.5`, `2.0` |
| `str` | Text | `"hello"`, `'Python'` |
| `bool` | True/False | `True`, `False` |
| `None` | No value | `None` |

### Type Checking

```python
x = 10
print(type(x))  # <class 'int'>

y = 3.14
print(type(y))  # <class 'float'>

name = "Python"
print(type(name))  # <class 'str'>
```

### Type Conversion

```python
# String to integer
age_str = "25"
age_int = int(age_str)
print(age_int + 5)  # 30

# Integer to string
number = 42
text = str(number)
print("The answer is " + text)

# Float to int (truncates)
pi = 3.14159
print(int(pi))  # 3
```

------

## 3. Operators

### Arithmetic Operators

```python
a = 10
b = 3

print(a + b)   # Addition: 13
print(a - b)   # Subtraction: 7
print(a * b)   # Multiplication: 30
print(a / b)   # Division: 3.333...
print(a // b)  # Integer division: 3
print(a % b)   # Modulus (remainder): 1
print(a ** b)  # Exponentiation: 1000
```

### Comparison Operators

```python
x = 5
y = 10

print(x == y)   # Equal: False
print(x != y)   # Not equal: True
print(x < y)    # Less than: True
print(x > y)    # Greater than: False
print(x <= y)   # Less or equal: True
print(x >= y)   # Greater or equal: False
```

### Logical Operators

```python
age = 20
has_license = True

# and: both must be True
can_drive = age >= 18 and has_license
print(can_drive)  # True

# or: at least one must be True
is_minor = age < 18 or age < 21
print(is_minor)  # True

# not: inverts the value
is_adult = not (age < 18)
print(is_adult)  # True
```

------

## 4. Control Flow

### If Statements

```python
temperature = 25

if temperature > 30:
    print("It's hot!")
elif temperature > 20:
    print("It's nice!")
elif temperature > 10:
    print("It's cool!")
else:
    print("It's cold!")
```

### While Loops

```python
# Count from 1 to 5
count = 1
while count <= 5:
    print(f"Count: {count}")
    count += 1

# Common pattern: process until condition
running = True
attempts = 0
while running:
    attempts += 1
    print(f"Attempt {attempts}")
    if attempts >= 3:
        running = False
```

### For Loops

```python
# Loop over a range
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4

# Loop with start and stop
for i in range(2, 7):
    print(i)  # 2, 3, 4, 5, 6

# Loop with step
for i in range(0, 10, 2):
    print(i)  # 0, 2, 4, 6, 8

# Loop over a list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)
```

### Break and Continue

```python
# break: exit the loop early
for i in range(10):
    if i == 5:
        break
    print(i)  # 0, 1, 2, 3, 4

# continue: skip to next iteration
for i in range(5):
    if i == 2:
        continue
    print(i)  # 0, 1, 3, 4
```

------

## 5. Functions

### Defining Functions

```python
def greet(name):
    """Print a greeting message."""
    print(f"Hello, {name}!")

greet("Alice")  # Hello, Alice!
greet("Bob")    # Hello, Bob!
```

### Return Values

```python
def add(a, b):
    """Add two numbers and return the result."""
    return a + b

result = add(5, 3)
print(result)  # 8

def square(x):
    """Return the square of x."""
    return x ** 2

print(square(4))  # 16
```

### Multiple Return Values

```python
def min_max(numbers):
    """Return both minimum and maximum of a list."""
    return min(numbers), max(numbers)

minimum, maximum = min_max([3, 1, 4, 1, 5])
print(f"Min: {minimum}, Max: {maximum}")  # Min: 1, Max: 5
```

### Default Arguments

```python
def greet(name, greeting="Hello"):
    """Greet someone with a customizable greeting."""
    print(f"{greeting}, {name}!")

greet("Alice")              # Hello, Alice!
greet("Bob", "Hi")          # Hi, Bob!
greet("Charlie", "Hey")     # Hey, Charlie!
```

### Keyword Arguments

```python
def describe_person(name, age, city):
    print(f"{name} is {age} years old and lives in {city}")

# Positional arguments
describe_person("Alice", 30, "NYC")

# Keyword arguments (order doesn't matter)
describe_person(city="LA", name="Bob", age=25)

# Mix (positional first, then keyword)
describe_person("Charlie", age=28, city="SF")
```

------

## 6. Data Structures

### Lists (Ordered, Mutable)

```python
# Creating lists
fruits = ["apple", "banana", "cherry"]
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True]

# Accessing elements (0-indexed)
print(fruits[0])   # apple
print(fruits[-1])  # cherry (last element)

# Slicing
print(numbers[1:4])   # [2, 3, 4]
print(numbers[:3])    # [1, 2, 3]
print(numbers[2:])    # [3, 4, 5]

# Modifying lists
fruits.append("orange")       # Add to end
fruits.insert(1, "mango")     # Insert at index
fruits.remove("banana")       # Remove by value
last = fruits.pop()           # Remove and return last
fruits[0] = "grape"           # Change element

# List operations
print(len(fruits))            # Length
print("apple" in fruits)      # Membership test
combined = fruits + numbers   # Concatenation
```

### Tuples (Ordered, Immutable)

```python
# Creating tuples
point = (3, 5)
person = ("Alice", 30, "Engineer")

# Accessing elements
x, y = point
print(x, y)  # 3 5

# Tuples can't be modified
# point[0] = 10  # ERROR: TypeError
```

### Dictionaries (Key-Value Pairs)

```python
# Creating dictionaries
person = {
    "name": "Alice",
    "age": 30,
    "city": "NYC"
}

# Accessing values
print(person["name"])        # Alice
print(person.get("age"))     # 30
print(person.get("job", "Unknown"))  # Unknown (default)

# Modifying dictionaries
person["age"] = 31           # Update value
person["job"] = "Engineer"   # Add new key
del person["city"]           # Remove key

# Looping over dictionaries
for key in person:
    print(f"{key}: {person[key]}")

for key, value in person.items():
    print(f"{key}: {value}")
```

### Sets (Unordered, Unique Elements)

```python
# Creating sets
fruits = {"apple", "banana", "cherry"}
numbers = {1, 2, 3, 3, 3}  # Duplicates removed: {1, 2, 3}

# Set operations
fruits.add("orange")
fruits.remove("banana")

# Mathematical operations
set1 = {1, 2, 3}
set2 = {3, 4, 5}
print(set1 & set2)  # Intersection: {3}
print(set1 | set2)  # Union: {1, 2, 3, 4, 5}
print(set1 - set2)  # Difference: {1, 2}
```

------

## 7. List Comprehensions

### Basic Syntax

```python
# Traditional way
squares = []
for i in range(10):
    squares.append(i ** 2)

# List comprehension (shorter, faster)
squares = [i ** 2 for i in range(10)]
print(squares)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

### With Conditions

```python
# Even numbers only
evens = [x for x in range(20) if x % 2 == 0]
print(evens)  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

# Transform and filter
names = ["alice", "bob", "charlie"]
upper_long = [name.upper() for name in names if len(name) > 3]
print(upper_long)  # ['ALICE', 'CHARLIE']
```

------

## 8. File I/O

### Reading Files

```python
# Read entire file
with open("data.txt", "r") as file:
    content = file.read()
    print(content)

# Read line by line
with open("data.txt", "r") as file:
    for line in file:
        print(line.strip())  # strip() removes newline

# Read all lines into a list
with open("data.txt", "r") as file:
    lines = file.readlines()
    print(lines)
```

### Writing Files

```python
# Write (overwrites existing file)
with open("output.txt", "w") as file:
    file.write("Hello, file!\n")
    file.write("Second line\n")

# Append (adds to end)
with open("output.txt", "a") as file:
    file.write("Appended line\n")
```

### CSV Files

```python
import csv

# Write CSV
data = [
    ["Name", "Age", "City"],
    ["Alice", 30, "NYC"],
    ["Bob", 25, "LA"]
]

with open("people.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(data)

# Read CSV
with open("people.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)
```

------

## 9. Error Handling

### Try-Except Blocks

```python
# Handle specific errors
try:
    number = int(input("Enter a number: "))
    result = 10 / number
    print(f"Result: {result}")
except ValueError:
    print("That's not a valid number!")
except ZeroDivisionError:
    print("Can't divide by zero!")
```

### Multiple Exceptions

```python
try:
    # Risky code here
    pass
except (ValueError, TypeError) as e:
    print(f"Error: {e}")
```

### Finally Block

```python
file = None
try:
    file = open("data.txt", "r")
    content = file.read()
except FileNotFoundError:
    print("File not found!")
finally:
    if file:
        file.close()  # Always runs
```

------

## 10. NumPy Basics

### Why NumPy?

NumPy is essential for scientific computing:
- Fast array operations (100x faster than Python lists)
- Mathematical functions (sin, cos, exp, log)
- Linear algebra operations
- Random number generation

### Installation

```powershell
pip install numpy
```

### Creating Arrays

```python
import numpy as np

# From lists
arr1 = np.array([1, 2, 3, 4, 5])
print(arr1)  # [1 2 3 4 5]

# Special arrays
zeros = np.zeros(5)           # [0. 0. 0. 0. 0.]
ones = np.ones((2, 3))        # 2x3 array of ones
arange = np.arange(0, 10, 2)  # [0 2 4 6 8]
linspace = np.linspace(0, 1, 5)  # [0.   0.25 0.5  0.75 1.  ]
```

### Array Operations

```python
# Element-wise operations
a = np.array([1, 2, 3, 4])
b = np.array([10, 20, 30, 40])

print(a + b)   # [11 22 33 44]
print(a * b)   # [10 40 90 160]
print(a ** 2)  # [1 4 9 16]

# Mathematical functions
angles = np.array([0, np.pi/2, np.pi])
print(np.sin(angles))  # [0. 1. 0.]
print(np.exp(a))       # [2.71828183 7.3890561 20.08553692 54.59815003]
```

### Indexing and Slicing

```python
arr = np.array([10, 20, 30, 40, 50])

print(arr[0])      # 10
print(arr[-1])     # 50
print(arr[1:4])    # [20 30 40]
print(arr[::2])    # [10 30 50] (every other element)

# Boolean indexing
mask = arr > 25
print(arr[mask])   # [30 40 50]
```

### 2D Arrays (Matrices)

```python
# Creating 2D arrays
matrix = np.array([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
])

print(matrix[0, 0])     # 1 (row 0, col 0)
print(matrix[1, :])     # [4 5 6] (row 1, all cols)
print(matrix[:, 2])     # [3 6 9] (all rows, col 2)

# Shape and size
print(matrix.shape)     # (3, 3)
print(matrix.size)      # 9
```

------

## 11. Common Python Idioms

### String Formatting

```python
name = "Alice"
age = 30

# f-strings (modern, preferred)
print(f"{name} is {age} years old")

# .format() method
print("{} is {} years old".format(name, age))

# % formatting (old style)
print("%s is %d years old" % (name, age))
```

### Enumerate

```python
fruits = ["apple", "banana", "cherry"]

# Get both index and value
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")
# 0: apple
# 1: banana
# 2: cherry
```

### Zip

```python
names = ["Alice", "Bob", "Charlie"]
ages = [30, 25, 35]

# Combine two lists
for name, age in zip(names, ages):
    print(f"{name}: {age}")
# Alice: 30
# Bob: 25
# Charlie: 35
```

### Lambda Functions

```python
# Anonymous functions
square = lambda x: x ** 2
print(square(5))  # 25

# Useful with map, filter
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x ** 2, numbers))
print(squared)  # [1, 4, 9, 16, 25]

evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # [2, 4]
```

------

## 12. Debugging Tips

### Print Debugging

```python
def complex_calculation(x):
    print(f"Input: {x}")  # Debug print
    result = x ** 2 + 2 * x + 1
    print(f"Result: {result}")  # Debug print
    return result
```

### Type Checking

```python
value = "123"
print(f"Type: {type(value)}")
print(f"Value: {repr(value)}")
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `NameError` | Variable not defined | Check spelling, define before use |
| `TypeError` | Wrong type (e.g., `"5" + 5`) | Convert types (`int("5")`) |
| `IndexError` | List index out of range | Check list length |
| `KeyError` | Dictionary key doesn't exist | Use `.get()` with default |
| `IndentationError` | Inconsistent indentation | Use 4 spaces consistently |

------

## 13. Practice Exercises

### Exercise 1: FizzBuzz

```python
# Print numbers 1-100, but:
# - "Fizz" for multiples of 3
# - "Buzz" for multiples of 5
# - "FizzBuzz" for multiples of both

for i in range(1, 101):
    if i % 15 == 0:
        print("FizzBuzz")
    elif i % 3 == 0:
        print("Fizz")
    elif i % 5 == 0:
        print("Buzz")
    else:
        print(i)
```

### Exercise 2: Word Counter

```python
def count_words(text):
    """Count word frequency in text."""
    words = text.lower().split()
    counts = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    return counts

text = "the quick brown fox jumps over the lazy dog the"
print(count_words(text))
# {'the': 3, 'quick': 1, 'brown': 1, ...}
```

### Exercise 3: Pendulum Angle Simulation

```python
import numpy as np
import matplotlib.pyplot as plt

# Simple harmonic oscillator (approximates small-angle pendulum)
def simulate_pendulum(theta0, omega0, t_max, dt):
    """
    Simulate pendulum motion.
    theta0: initial angle (rad)
    omega0: initial angular velocity (rad/s)
    t_max: simulation time (s)
    dt: time step (s)
    """
    g = 9.81  # gravity
    L = 1.0   # pendulum length

    t = np.arange(0, t_max, dt)
    theta = np.zeros_like(t)
    omega = np.zeros_like(t)

    theta[0] = theta0
    omega[0] = omega0

    for i in range(len(t) - 1):
        # Euler integration (simple numerical method)
        alpha = -(g / L) * np.sin(theta[i])
        omega[i + 1] = omega[i] + alpha * dt
        theta[i + 1] = theta[i] + omega[i + 1] * dt

    return t, theta, omega

# Run simulation
t, theta, omega = simulate_pendulum(
    theta0=np.pi/6,  # 30 degrees
    omega0=0,
    t_max=10,
    dt=0.01
)

# Plot results
plt.figure(figsize=(10, 4))
plt.plot(t, np.degrees(theta))
plt.xlabel("Time (s)")
plt.ylabel("Angle (degrees)")
plt.title("Pendulum Motion")
plt.grid()
plt.show()
```

------

## 14. Next Steps

You're ready for `physics-foundations.md` when you can:

- [ ] Write functions with parameters and return values
- [ ] Use lists, dictionaries, and loops confidently
- [ ] Handle errors with try-except
- [ ] Read and write files
- [ ] Create and manipulate NumPy arrays
- [ ] Complete the pendulum simulation exercise

------

## Additional Resources

### Official Documentation
- Python Tutorial: https://docs.python.org/3/tutorial/
- NumPy Quickstart: https://numpy.org/doc/stable/user/quickstart.html

### Interactive Practice
- Python Tutor (visualize code): https://pythontutor.com/
- Exercism Python Track: https://exercism.org/tracks/python
- Project Euler: https://projecteuler.net/ (math problems)

### Cheat Sheets
- See `cheatsheets/python-syntax.md`
- See `cheatsheets/numpy-operations.md`

------

**Last Updated**: 2025-10-17
**Estimated Time**: 15-18 hours
**Next Module**: `physics-foundations.md` or `mathematics-essentials.md`
