<!-- AUTO-GENERATED from .project/ai/edu/ - DO NOT EDIT DIRECTLY -->
<!-- Source: .project/ai/edu/phase1/cheatsheets/python-syntax.md -->
<!-- Generated: 2025-11-11 13:29:26 -->

# Python Syntax - Quick Cheatsheet

**Essential Python Syntax Reference**

------

## Variables and Data Types

```python
# Numbers
x = 42              # int
y = 3.14            # float
z = 1 + 2j          # complex

# Strings
name = "Alice"
multiline = """This is
a multiline string"""

# Boolean
is_active = True
is_done = False

# None (no value)
result = None

# Type checking
type(x)  # <class 'int'>
```

------

## Operators

### Arithmetic

```python
a + b    # Addition
a - b    # Subtraction
a * b    # Multiplication
a / b    # Division (always float)
a // b   # Integer division
a % b    # Modulus (remainder)
a ** b   # Exponentiation
```

### Comparison

```python
a == b   # Equal
a != b   # Not equal
a < b    # Less than
a > b    # Greater than
a <= b   # Less or equal
a >= b   # Greater or equal
```

### Logical

```python
a and b  # Both True
a or b   # At least one True
not a    # Invert
```

------

## Control Flow

### If-Elif-Else

```python
if condition:
    # code
elif other_condition:
    # code
else:
    # code
```

### For Loop

```python
# Range
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4

# List
for item in my_list:
    print(item)

# With index
for i, item in enumerate(my_list):
    print(i, item)
```

### While Loop

```python
while condition:
    # code
    if break_condition:
        break
    if skip_condition:
        continue
```

------

## Data Structures

### Lists (Ordered, Mutable)

```python
# Create
lst = [1, 2, 3]
empty = []

# Access
lst[0]      # First element
lst[-1]     # Last element
lst[1:3]    # Slice [2, 3]

# Modify
lst.append(4)       # Add to end
lst.insert(0, 0)    # Insert at index
lst.remove(2)       # Remove by value
lst.pop()           # Remove and return last
lst[0] = 10         # Change element

# Other
len(lst)            # Length
2 in lst            # Membership
lst1 + lst2         # Concatenate
lst * 3             # Repeat
```

### Tuples (Ordered, Immutable)

```python
# Create
tup = (1, 2, 3)
single = (1,)  # Note comma

# Access
tup[0]

# Unpack
a, b, c = tup
```

### Dictionaries (Key-Value Pairs)

```python
# Create
d = {"name": "Alice", "age": 30}
empty = {}

# Access
d["name"]           # "Alice"
d.get("age")        # 30
d.get("job", "N/A") # Default value

# Modify
d["age"] = 31       # Update
d["job"] = "Eng"    # Add new
del d["name"]       # Remove

# Iterate
for key in d:
    print(key, d[key])

for key, value in d.items():
    print(key, value)

# Keys/Values
d.keys()
d.values()
```

### Sets (Unordered, Unique)

```python
# Create
s = {1, 2, 3}
empty = set()

# Modify
s.add(4)
s.remove(2)

# Operations
s1 & s2   # Intersection
s1 | s2   # Union
s1 - s2   # Difference
```

------

## Functions

### Basic Function

```python
def greet(name):
    """Docstring: what the function does."""
    return f"Hello, {name}!"

result = greet("Alice")
```

### Multiple Parameters

```python
def add(a, b, c=0):
    """c has default value 0."""
    return a + b + c

add(1, 2)       # 3
add(1, 2, 3)    # 6
```

### Multiple Return Values

```python
def min_max(numbers):
    return min(numbers), max(numbers)

minimum, maximum = min_max([1, 2, 3])
```

### Lambda (Anonymous Function)

```python
square = lambda x: x ** 2
print(square(5))  # 25
```

------

## List Comprehensions

```python
# Basic
squares = [x**2 for x in range(10)]

# With condition
evens = [x for x in range(20) if x % 2 == 0]

# Transform
upper = [s.upper() for s in ["a", "b", "c"]]

# Nested
matrix = [[i*j for j in range(3)] for i in range(3)]
```

------

## String Operations

```python
s = "Hello, World!"

# Methods
s.lower()           # "hello, world!"
s.upper()           # "HELLO, WORLD!"
s.strip()           # Remove whitespace
s.split(",")        # ["Hello", " World!"]
s.replace("H", "J") # "Jello, World!"
s.startswith("He")  # True
s.endswith("!")     # True

# Formatting
name = "Alice"
age = 30
f"Name: {name}, Age: {age}"  # f-string (preferred)
"Name: {}, Age: {}".format(name, age)
```

------

## File I/O

### Reading

```python
# Read entire file
with open("file.txt", "r") as f:
    content = f.read()

# Read lines
with open("file.txt", "r") as f:
    for line in f:
        print(line.strip())

# Read all lines into list
with open("file.txt", "r") as f:
    lines = f.readlines()
```

### Writing

```python
# Write (overwrite)
with open("file.txt", "w") as f:
    f.write("Hello\n")
    f.write("World\n")

# Append
with open("file.txt", "a") as f:
    f.write("New line\n")
```

------

## Exception Handling

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Can't divide by zero!")
except (ValueError, TypeError) as e:
    print(f"Error: {e}")
else:
    print("No error occurred")
finally:
    print("Always runs")
```

------

## Modules and Imports

```python
# Import entire module
import math
print(math.pi)

# Import specific items
from math import pi, sqrt
print(pi)

# Import with alias
import numpy as np
arr = np.array([1, 2, 3])

# Import all (not recommended)
from math import *
```

------

## Classes (Brief)

```python
class Person:
    """A simple class."""

    def __init__(self, name, age):
        """Constructor."""
        self.name = name
        self.age = age

    def greet(self):
        """Method."""
        return f"Hi, I'm {self.name}"

# Create instance
alice = Person("Alice", 30)
print(alice.greet())
```

------

## Common Built-in Functions

```python
# Type conversion
int("42")       # 42
float("3.14")   # 3.14
str(42)         # "42"
list("abc")     # ['a', 'b', 'c']

# Math
abs(-5)         # 5
min(1, 2, 3)    # 1
max(1, 2, 3)    # 3
sum([1, 2, 3])  # 6
round(3.7)      # 4
pow(2, 3)       # 8

# Sequences
len([1, 2, 3])  # 3
sorted([3, 1, 2])  # [1, 2, 3]
reversed([1, 2, 3])  # [3, 2, 1] iterator
range(5)        # 0, 1, 2, 3, 4

# Other
print(x)        # Output
input("Prompt") # User input
help(function)  # Documentation
dir(object)     # List attributes
```

------

## Useful Idioms

### Swap Variables

```python
a, b = b, a
```

### Conditional Expression (Ternary)

```python
result = "positive" if x > 0 else "non-positive"
```

### Enumerate

```python
for i, value in enumerate(["a", "b", "c"]):
    print(i, value)
# 0 a
# 1 b
# 2 c
```

### Zip

```python
names = ["Alice", "Bob"]
ages = [30, 25]
for name, age in zip(names, ages):
    print(name, age)
```

### Map/Filter

```python
# Map: apply function to each element
squared = list(map(lambda x: x**2, [1, 2, 3]))

# Filter: keep elements that pass test
evens = list(filter(lambda x: x % 2 == 0, [1, 2, 3, 4]))
```

### Any/All

```python
any([False, True, False])  # True (at least one)
all([True, True, False])   # False (not all)
```

------

## Common Pitfalls

### Mutable Default Arguments (Don't Do This!)

```python
# WRONG
def append_to(element, lst=[]):
    lst.append(element)
    return lst

# RIGHT
def append_to(element, lst=None):
    if lst is None:
        lst = []
    lst.append(element)
    return lst
```

### Integer Division in Python 2 vs 3

```python
# Python 3
5 / 2   # 2.5 (float division)
5 // 2  # 2 (integer division)
```

### Indentation Matters!

```python
# WRONG (IndentationError)
def foo():
print("hello")

# RIGHT
def foo():
    print("hello")
```

------

**Last Updated**: 2025-10-17
**More Info**: https://docs.python.org/3/
