[<-- Back to Beginner Roadmap](../beginner-roadmap.md)

---

# Phase 1: Foundations (Week 1-4, ~40 Hours)

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
      <span class="phase-badge phase-1">Phase 1</span>
      <span class="breadcrumb-text">Computing Fundamentals</span>
    </li>
  </ol>
</nav>
:::

::::

---

**Prerequisites**: None
**Next Phase**: [Phase 2: Core Concepts](phase-2-core-concepts.md)

**Goal**: Build the absolute minimum knowledge to start programming and understand basic physics.

## Phase 1 Overview

| Sub-Phase | Topic | Time | Why You Need This |
|-----------|-------|------|-------------------|
| 1.1 | Computing Basics | 4 hours | Navigate files, use command line |
| 1.2 | Python Fundamentals | 20 hours | Write and run code |
| 1.3 | Setting Up Environment | 3 hours | Install tools for this project |
| 1.4 | Basic Physics | 8 hours | Understand pendulums and forces |
| 1.5 | Basic Math | 5 hours | Functions, graphs, equations |

**Total**: ~40 hours over 4 weeks (~10 hours/week)

**Visual Aids**: [View Phase 1 Diagrams -->](phase-1-diagrams.md) (File System, Computing Basics, Error Diagnosis, Data Types, Setup)

---

<details>
<summary>1.1 Computing Basics</summary>

## Phase 1.1: Computing Basics (4 hours)

**Skip if**: You already use command line, understand file paths, and know what a directory is.

### What You'll Learn

- What are files and folders (directories)?
- How to navigate your computer using the command line
- What is a "path" (e.g., `C:\Users\YourName\Documents\project`)?
- How to create, move, and delete files/folders
- What is a "terminal" or "command prompt"?

### Learning Path

**Step 1: Understanding File Systems (1 hour)**

**Analogy**: Think of your computer like a filing cabinet:
- **Drives** (C:, D:) are filing cabinets
- **Folders** (directories) are drawers
- **Files** are documents inside drawers

**Key Concepts**:
- **Absolute path**: Full address from the drive root
  - Windows: `C:\Users\YourName\Projects\main`
  - Mac/Linux: `/home/yourname/Projects/main`
- **Relative path**: Address from where you currently are
  - If you're in `Projects`, then `main` is relative path to `Projects/main`

**Practice Exercise**:
1. Find where your "Documents" folder is located
2. Write down its absolute path
3. Create a new folder called `coding-practice`

**Resources**:
- [File Systems Explained (Video, 10 min)](https://www.youtube.com/results?search_query=file+system+basics+explained)
- [Understanding File Paths (Article)](https://www.computerhope.com/jargon/p/path.htm)

---

**Step 2: Command Line Basics (2 hours)**

**What is the command line?**
- A text interface to control your computer
- Instead of clicking, you type commands
- Faster and more powerful than graphical interfaces

**Essential Commands**:

::::{tab-set}
:sync-group: os

:::{tab-item} Windows
:sync: win
:selected:

```cmd
# Show current directory
cd

# List files in current directory
dir

# Change directory
cd C:\Users\YourName\Documents

# Go up one level
cd ..

# Create new directory
mkdir my-project

# Delete directory (empty)
rmdir my-project

# Show file contents
type filename.txt

# Clear screen
cls
```

:::

:::{tab-item} Mac/Linux
:sync: unix

```bash
# Show current directory
pwd

# List files in current directory
ls

# List with details
ls -la

# Change directory
cd /home/yourname/Documents

# Go up one level
cd ..

# Create new directory
mkdir my-project

# Delete directory (empty)
rmdir my-project

# Show file contents
cat filename.txt

# Clear screen
clear
```

:::

::::

**Practice Exercise**:
1. Open terminal/command prompt
2. Navigate to your Documents folder
3. Create a folder called `dip-project-test`
4. Navigate into it (`cd dip-project-test`)
5. Verify you're there (`pwd` or `cd`)
6. Go back to Documents (`cd ..`)
7. Delete the test folder

**Resources**:
- [Command Line Crash Course (Video, 30 min)](https://www.youtube.com/results?search_query=command+line+crash+course+beginners)
- [Windows Command Prompt Guide](https://www.computerhope.com/issues/chusedos.htm)
- [Mac/Linux Terminal Guide](https://ubuntu.com/tutorials/command-line-for-beginners)

---

**Step 3: Text Editors (1 hour)**

**What is a text editor?**
- A program for editing plain text files (not Word documents)
- Used for writing code

**Recommended Editors for Beginners**:

::::{tab-set}
:sync-group: os

:::{tab-item} Windows
:sync: win
:selected:

1. **VS Code** (Most popular, free)
   - Download: https://code.visualstudio.com/
   - Easy to use, lots of extensions
   - Works on Windows, Mac, Linux

2. **Notepad++** (Windows only, lightweight)
   - Download: https://notepad-plus-plus.org/
   - Simple, fast, good for small edits

3. **Sublime Text** (Cross-platform, fast)
   - Download: https://www.sublimetext.com/
   - Free trial, minimal interface

:::

:::{tab-item} Mac/Linux
:sync: unix

1. **VS Code** (Most popular, free)
   - Download: https://code.visualstudio.com/
   - Easy to use, lots of extensions
   - Works on Windows, Mac, Linux

2. **Vim** (Terminal-based, powerful)
   - Pre-installed on most Unix systems
   - Steep learning curve, very efficient once learned

3. **Sublime Text** (Cross-platform, fast)
   - Download: https://www.sublimetext.com/
   - Free trial, minimal interface

:::

::::

**Practice Exercise**:
1. Install VS Code (recommended)
2. Create a file called `hello.txt`
3. Write: "Hello, I'm learning to code!"
4. Save it in your `coding-practice` folder
5. Open the file from command line: `type hello.txt` (Windows) or `cat hello.txt` (Mac/Linux)

**Resources**:
- [VS Code for Beginners (Video, 20 min)](https://www.youtube.com/results?search_query=vs+code+tutorial+beginners)
- [VS Code Documentation](https://code.visualstudio.com/docs/getstarted/introvideos)

---

### Self-Assessment: Phase 1.1

**Quiz** (Answer True/False):

1. The command line is just another way to control my computer without clicking. (T/F)
2. `C:\Users\Alice\Desktop\file.txt` is an example of an absolute path. (T/F)
3. The command `cd ..` moves me one directory level up. (T/F)
4. I can edit code in Microsoft Word. (T/F - **False**, use text editors!)
5. VS Code is a text editor designed for coding. (T/F)

**Answers**: 1-T, 2-T, 3-T, 4-F, 5-T

**If you got 4-5 correct**: Move to Phase 1.2
**If you got 2-3 correct**: Review command line basics
**If you got 0-1 correct**: Spend more time with the resources above

</details>

---

<details>
<summary>1.2 Python Fundamentals</summary>

## Phase 1.2: Python Fundamentals (20 hours)

**Skip if**: You can write Python functions, understand loops, and work with lists/dictionaries.

### What You'll Learn

- Installing Python
- Running Python code
- Variables, data types, and operators
- Control flow (if/else, for/while loops)
- Functions
- Lists, dictionaries, and basic data structures
- Reading error messages

### Learning Path

**Step 1: Install Python (1 hour)**

**What is Python?**
- A programming language (way to give instructions to computers)
- Very popular for scientific computing, data science, AI
- Relatively easy to learn compared to other languages

**Installation**:

::::{tab-set}
:sync-group: os

:::{tab-item} Windows
:sync: win
:selected:

1. **Download Python 3.11+**:
   - Go to: https://www.python.org/downloads/
   - Click "Download Python 3.11.x"
   - **IMPORTANT**: Check "Add Python to PATH" during installation!

2. **Verify Installation**:
   ```bash
   python --version
   # Should show: Python 3.11.x or higher
   ```

3. **Test Python**:
   ```bash
   python
   >>> print("Hello, World!")
   Hello, World!
   >>> exit()
   ```

:::

:::{tab-item} Mac
:sync: unix

1. **Download Python 3.11+**:
   - Go to: https://www.python.org/downloads/
   - Click "Download Python 3.11.x"
   - Use the .pkg installer

2. **Verify Installation**:
   ```bash
   python3 --version
   # Should show: Python 3.11.x or higher
   ```

3. **Test Python**:
   ```bash
   python3
   >>> print("Hello, World!")
   Hello, World!
   >>> exit()
   ```

:::

:::{tab-item} Linux
:sync: unix

1. **Install Python 3.11+**:
   ```bash
   # Usually pre-installed, check version first
   python3 --version

   # If not installed or too old:
   sudo apt update
   sudo apt install python3 python3-pip
   ```

2. **Verify Installation**:
   ```bash
   python3 --version
   # Should show: Python 3.11.x or higher
   ```

3. **Test Python**:
   ```bash
   python3
   >>> print("Hello, World!")
   Hello, World!
   >>> exit()
   ```

:::

::::

**Resources**:
- [Python Installation Guide (Video, 10 min)](https://www.youtube.com/results?search_query=how+to+install+python+windows)
- [Python.org Beginner's Guide](https://wiki.python.org/moin/BeginnersGuide)

---

**Step 2: Python Basics (10 hours)**

**Essential Concepts to Learn**:

:::{dropdown} 1. Variables and Data Types (2 hours)
:animate: fade-in-slide-down
:color: primary

Learn how to store and manipulate different types of data in Python.

**Topics Covered**:
- Numbers (integers, floats)
- Strings (text)
- Booleans (True/False)
- Type conversion

**Code Examples**:

```python
# Variables store values
age = 25
name = "Alice"
height = 1.75  # meters
is_student = True

# You can change variable values
age = age + 1  # Now 26

# Type conversion
age_string = str(age)  # "26"
number = int("42")     # 42
```

**Practice**: Try creating variables for your name, age, and favorite number. Print them!

:::

:::{dropdown} 2. Operators and Expressions (1 hour)
:animate: fade-in-slide-down
:color: primary

Learn how to perform calculations and comparisons in Python.

**Topics Covered**:
- Arithmetic: `+`, `-`, `*`, `/`, `**` (power), `%` (modulo)
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `and`, `or`, `not`

**Code Examples**:

```python
# Arithmetic
result = 10 + 5 * 2  # 20 (multiplication first)
power = 2 ** 3       # 8 (2 to the power of 3)

# Comparison
is_adult = age >= 18  # True if age is 18 or more

# Logical
can_vote = (age >= 18) and (is_citizen)
```

**Practice**: Calculate the area of a circle with radius 5 using `area = 3.14 * radius ** 2`

:::

:::{dropdown} 3. Control Flow: if/else (2 hours)
:animate: fade-in-slide-down
:color: primary

Learn how to make decisions in your code based on conditions.

**Topics Covered**:
- if statements
- elif (else if) for multiple conditions
- else for default case
- Indentation matters!

**Code Examples**:

```python
age = 20

if age >= 18:
    print("You are an adult")
elif age >= 13:
    print("You are a teenager")
else:
    print("You are a child")
```

**Practice**: Write an if/else that checks if a number is positive, negative, or zero.

:::

:::{dropdown} 4. Loops: for and while (2 hours)
:animate: fade-in-slide-down
:color: primary

Learn how to repeat actions efficiently without writing the same code multiple times.

**Topics Covered**:
- for loops (repeat N times)
- while loops (repeat until condition)
- range() function
- Loop control (break, continue)

**Code Examples**:

```python
# For loop (repeat N times)
for i in range(5):
    print(f"Count: {i}")  # Prints 0, 1, 2, 3, 4

# While loop (repeat until condition false)
count = 0
while count < 5:
    print(f"Count: {count}")
    count = count + 1
```

**Practice**: Write a loop that calculates the sum of numbers from 1 to 100.

:::

:::{dropdown} 5. Functions (2 hours)
:animate: fade-in-slide-down
:color: primary

Learn how to create reusable blocks of code that perform specific tasks.

**Topics Covered**:
- Defining functions with def
- Parameters and arguments
- Return values
- Function documentation

**Code Examples**:

```python
# Define a function
def greet(name):
    return f"Hello, {name}!"

# Call the function
message = greet("Alice")
print(message)  # "Hello, Alice!"

# Function with multiple parameters
def add_numbers(a, b):
    return a + b

result = add_numbers(5, 3)  # 8
```

**Practice**: Write a function that takes two numbers and returns their average.

:::

:::{dropdown} 6. Lists and Dictionaries (1 hour)
:animate: fade-in-slide-down
:color: primary

Learn how to work with collections of data - ordered lists and key-value dictionaries.

**Topics Covered**:
- Creating and accessing lists
- List methods (append, remove, sort)
- Creating and accessing dictionaries
- When to use lists vs dictionaries

**Code Examples**:

```python
# Lists (ordered)
numbers = [1, 2, 3, 4, 5]
names = ["Alice", "Bob", "Charlie"]

# Access by index (starts at 0)
first_name = names[0]  # "Alice"

# Add to list
names.append("David")

# Dictionaries (key-value pairs)
person = {
    "name": "Alice",
    "age": 25,
    "city": "New York"
}

# Access by key
person_age = person["age"]  # 25
```

**Practice**: Create a list of your top 5 favorite movies, then access the first and last items.

:::

**Practice Exercises**:

1. **Exercise 1**: Write a function that takes a temperature in Celsius and converts it to Fahrenheit.
   ```python
   def celsius_to_fahrenheit(celsius):
       # Formula: F = C * 9/5 + 32
       # Your code here
       pass
   ```

   :::{dropdown} Solution (try first!)
   :color: success
   :icon: light-bulb

   ```python
   def celsius_to_fahrenheit(celsius):
       """Convert Celsius to Fahrenheit."""
       fahrenheit = celsius * 9/5 + 32
       return fahrenheit

   # Test it
   print(celsius_to_fahrenheit(0))    # 32.0
   print(celsius_to_fahrenheit(100))  # 212.0
   print(celsius_to_fahrenheit(37))   # 98.6 (body temperature)
   ```

   **Explanation**: The formula multiplies Celsius by 9/5 (or 1.8) and adds 32. This converts the temperature scale from Celsius to Fahrenheit.

   :::

2. **Exercise 2**: Write a loop that prints all numbers from 1 to 10 that are even.

   :::{dropdown} Solution (try first!)
   :color: success
   :icon: light-bulb

   **Method 1: Using modulo operator**
   ```python
   for i in range(1, 11):
       if i % 2 == 0:  # % is modulo (remainder)
           print(i)
   # Output: 2, 4, 6, 8, 10
   ```

   **Method 2: Using range with step**
   ```python
   for i in range(2, 11, 2):  # Start at 2, end at 11, step by 2
       print(i)
   # Output: 2, 4, 6, 8, 10
   ```

   **Explanation**: Method 1 checks if each number is divisible by 2 (remainder is 0). Method 2 is more efficient, starting at 2 and counting by 2s.

   :::

3. **Exercise 3**: Create a dictionary representing a pendulum with keys: "length", "mass", "angle".

   :::{dropdown} Solution (try first!)
   :color: success
   :icon: light-bulb

   ```python
   # Simple pendulum dictionary
   pendulum = {
       "length": 1.5,    # meters
       "mass": 0.5,      # kilograms
       "angle": 30       # degrees
   }

   # Access the values
   print(f"Pendulum length: {pendulum['length']} m")
   print(f"Pendulum mass: {pendulum['mass']} kg")
   print(f"Initial angle: {pendulum['angle']} degrees")

   # Modify values
   pendulum["angle"] = 15  # Swing to new angle
   print(f"New angle: {pendulum['angle']} degrees")
   ```

   **Explanation**: Dictionaries use key-value pairs. Each key (like "length") maps to a value (like 1.5). This is perfect for representing objects with named properties.

   :::

**Resources**:
- [Python for Everybody (Free Course, 10 hours)](https://www.py4e.com/)
- [Python Crash Course (Video, 4 hours)](https://www.youtube.com/watch?v=_uQrJ0TkZlc)
- [Learn Python - Codecademy (Interactive)](https://www.codecademy.com/learn/learn-python-3)
- [Python Tutorial - W3Schools](https://www.w3schools.com/python/)

---

**Step 3: Working with Libraries (3 hours)**

**What is a library?**
- Pre-written code you can use
- Like using tools from a toolbox instead of making your own

**Essential Libraries for This Project**:

1. **NumPy** (Numerical computing)
   ```python
   import numpy as np

   # Create arrays (lists of numbers)
   numbers = np.array([1, 2, 3, 4, 5])

   # Mathematical operations
   doubled = numbers * 2  # [2, 4, 6, 8, 10]
   mean = np.mean(numbers)  # 3.0
   ```

2. **Matplotlib** (Plotting)
   ```python
   import matplotlib.pyplot as plt

   # Create a simple plot
   x = [1, 2, 3, 4, 5]
   y = [1, 4, 9, 16, 25]

   plt.plot(x, y)
   plt.xlabel("Time")
   plt.ylabel("Position")
   plt.title("My First Plot")
   plt.show()
   ```

**Practice Exercise**:
Create a plot showing the trajectory of a ball thrown upward:

```python
import numpy as np
import matplotlib.pyplot as plt

# Time from 0 to 2 seconds
time = np.linspace(0, 2, 100)

# Height equation: h = v0*t - 0.5*g*t^2
# v0 = initial velocity = 20 m/s
# g = gravity = 9.81 m/s^2
height = 20 * time - 0.5 * 9.81 * time**2

plt.plot(time, height)
plt.xlabel("Time (s)")
plt.ylabel("Height (m)")
plt.title("Ball Trajectory")
plt.grid(True)
plt.show()
```

**Resources**:
- [NumPy Quickstart Tutorial](https://numpy.org/doc/stable/user/quickstart.html)
- [Matplotlib Tutorial (Video, 1 hour)](https://www.youtube.com/results?search_query=matplotlib+tutorial+beginners)

---

**Step 4: Reading Error Messages (1 hour)**

**Why This Matters**:
- Errors are NORMAL - even experienced programmers see them constantly
- Error messages tell you what went wrong and where

**Common Error Types**:

1. **SyntaxError** (You made a typo):
   ```python
   # Missing colon
   if age >= 18
       print("Adult")
   # Error: SyntaxError: invalid syntax
   ```

2. **NameError** (Using undefined variable):
   ```python
   print(height)  # If 'height' was never defined
   # Error: NameError: name 'height' is not defined
   ```

3. **TypeError** (Wrong data type):
   ```python
   result = "5" + 5  # Can't add string and number
   # Error: TypeError: can only concatenate str (not "int") to str
   ```

4. **IndexError** (List index out of range):
   ```python
   numbers = [1, 2, 3]
   print(numbers[5])  # Only indices 0, 1, 2 exist
   # Error: IndexError: list index out of range
   ```

**How to Debug**:
1. **Read the error message carefully** (last line tells you the error type)
2. **Look at the line number** (tells you where the error occurred)
3. **Check the error type** (gives you a clue about what's wrong)
4. **Google the error** ("Python NameError" will find explanations)

**Practice Exercise**:
Fix these buggy code snippets:

```python
# Bug 1
def calculate_area(length, width)
    return length * width

# Bug 2
ages = [25, 30, 35]
print(ages[3])

# Bug 3
name = "Alice"
age = 25
print(name + age)
```

**Resources**:
- [Understanding Python Errors (Article)](https://realpython.com/python-traceback/)
- [Debugging Python Code (Video, 20 min)](https://www.youtube.com/results?search_query=debugging+python+code+beginners)

---

**Step 5: Python Practice Projects (5 hours)**

Before moving on, solidify your skills with small projects:

**Project 1: Temperature Converter**
- Input: Temperature in Celsius
- Output: Temperature in Fahrenheit and Kelvin
- Use functions, user input, and formatting

**Project 2: Simple Calculator**
- Ask user for two numbers
- Ask user for operation (+, -, *, /)
- Perform calculation and display result
- Use if/else for operation selection

**Project 3: Pendulum Angle Plotter**
- Generate time array (0 to 10 seconds)
- Calculate angle of a swinging pendulum: θ(t) = θ0 * cos(ωt)
- θ0 = initial angle = 0.5 radians
- ω = angular frequency = 2.0 rad/s
- Plot angle vs time

**Resources**:
- [Python Project Ideas for Beginners](https://realpython.com/tutorials/projects/)
- [50 Python Projects (Video Series)](https://www.youtube.com/results?search_query=python+projects+for+beginners)

---

### Self-Assessment: Phase 1.2

**Quiz**:

1. Write a function that returns the square of a number.
2. Create a list of 5 numbers and compute their average using a loop (not using np.mean).
3. Write an if/else statement that prints "Positive" if a number is >0, "Negative" if <0, "Zero" otherwise.
4. Fix this code: `print("The result is " + 42)`
5. Import numpy and create an array of numbers from 0 to 10.

**If you can complete all 5 without looking up answers**: Move to Phase 1.3
**If you can complete 3-4**: Practice more with loops and functions
**If you can complete 0-2**: Revisit Python Crash Course resources

</details>

---

<details>
<summary>1.3 Setting Up the Project Environment</summary>

## Phase 1.3: Setting Up the Project Environment (3 hours)

**Goal**: Install all tools and dependencies needed for this specific project.

### What You'll Learn

- What is a virtual environment and why use it?
- How to install packages with pip
- Cloning a git repository
- Verifying installation

### Learning Path

**Step 1: Understanding Virtual Environments (30 min)**

**What is a virtual environment?**
- An isolated Python environment for your project
- Prevents conflicts between different projects' dependencies
- Like having a separate toolbox for each project

**Why use it?**
- Project A needs numpy version 1.20
- Project B needs numpy version 2.0
- Virtual environments let both coexist without conflicts

**Creating a Virtual Environment**:

::::{tab-set}
:sync-group: os

:::{tab-item} Windows
:sync: win
:selected:

```bash
# Navigate to where you want to create your project
cd C:\Users\YourName\Projects

# Create virtual environment named 'venv'
python -m venv venv

# Activate it (Command Prompt):
venv\Scripts\activate.bat

# OR activate it (PowerShell):
venv\Scripts\Activate.ps1

# You should see (venv) in your terminal prompt
```

:::

:::{tab-item} Mac/Linux
:sync: unix

```bash
# Navigate to where you want to create your project
cd /home/yourname/Projects

# Create virtual environment named 'venv'
python3 -m venv venv

# Activate it:
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

:::

::::

**Resources**:
- [Virtual Environments Explained (Video, 10 min)](https://www.youtube.com/results?search_query=python+virtual+environment+explained)
- [Python venv Documentation](https://docs.python.org/3/library/venv.html)

---

**Step 2: Understanding Git and GitHub (1 hour)**

**What is Git?**
- Version control system (tracks changes to code over time)
- Like "Track Changes" in Word, but for code

**What is GitHub?**
- Website that hosts Git repositories (code projects)
- This project lives on GitHub

**Installing Git**:

::::{tab-set}
:sync-group: os

:::{tab-item} Windows
:sync: win
:selected:

1. **Download Git**:
   - Go to: https://git-scm.com/download/win
   - Run the installer with default settings

2. **Verify Installation**:
   ```bash
   git --version
   # Should show: git version 2.x.x
   ```

:::

:::{tab-item} Mac
:sync: unix

1. **Install Git**:
   ```bash
   # Check if already installed
   git --version

   # If not installed, use Homebrew:
   brew install git

   # Or install Xcode Command Line Tools:
   xcode-select --install
   ```

2. **Verify Installation**:
   ```bash
   git --version
   # Should show: git version 2.x.x
   ```

:::

:::{tab-item} Linux
:sync: unix

1. **Install Git**:
   ```bash
   sudo apt update
   sudo apt install git
   ```

2. **Verify Installation**:
   ```bash
   git --version
   # Should show: git version 2.x.x
   ```

:::

::::

**Basic Git Concepts**:
- **Repository (Repo)**: A project folder tracked by Git
- **Clone**: Download a repository from GitHub to your computer
- **Commit**: Save a snapshot of your changes
- **Push**: Upload your changes to GitHub
- **Pull**: Download latest changes from GitHub

**Resources**:
- [Git Explained in 100 Seconds (Video)](https://www.youtube.com/watch?v=hwP7WQkmECE)
- [Git Basics (Video, 30 min)](https://www.youtube.com/results?search_query=git+basics+tutorial)

---

**Step 3: Clone the DIP-SMC-PSO Project (30 min)**

**Cloning the Repository**:

```bash
# Navigate to where you want the project
cd C:\Users\YourName\Projects  # Windows
cd /home/yourname/Projects      # Mac/Linux

# Clone the repository
git clone https://github.com/theSadeQ/dip-smc-pso.git

# Navigate into the project
cd dip-smc-pso

# Verify you're in the right place
dir  # Windows
ls   # Mac/Linux

# You should see: simulate.py, config.yaml, src/, tests/, docs/
```

**Understanding the Project Structure**:

```
dip-smc-pso/
├── simulate.py              # Main program (you'll run this)
├── streamlit_app.py         # Web interface
├── config.yaml              # Configuration file (you'll edit this)
├── requirements.txt         # List of dependencies
├── src/                     # Source code
│   ├── controllers/         # Control algorithms
│   ├── core/                # Simulation engine
│   ├── plant/               # Physics models
│   └── optimization/        # PSO optimizer
├── tests/                   # Test code
├── docs/                    # Documentation
└── README.md                # Project overview
```

---

**Step 4: Install Project Dependencies (1 hour)**

**What are dependencies?**
- Libraries that this project needs to function
- Listed in `requirements.txt`

**Installation Steps**:

```bash
# Make sure you're in the project directory
cd dip-smc-pso

# Create and activate virtual environment
python -m venv venv
# Activate (see Phase 1.3 Step 1 for activation commands)

# Upgrade pip (package installer)
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# This will install ~50 packages, takes 2-5 minutes
```

**What Gets Installed**:
- **NumPy**: Numerical computing
- **SciPy**: Scientific computing (integration, optimization)
- **Matplotlib**: Plotting and visualization
- **PyYAML**: Configuration file reading
- **Numba**: Performance acceleration
- **PySwarms**: PSO optimization
- **pytest**: Testing
- **Streamlit**: Web interface
- ...and more

**Verify Installation**:

```bash
# Test that the main program works
python simulate.py --help

# You should see usage instructions
```

**Troubleshooting**:

:::{dropdown} Microsoft Visual C++ required (Windows)
:color: warning
:icon: alert

**Error Message**: "Microsoft Visual C++ 14.0 or greater is required" when installing packages.

**Why This Happens**: Some Python packages (like NumPy, SciPy) need to compile C/C++ code during installation. Windows doesn't include these tools by default.

**Solution**:

1. **Download Visual C++ Build Tools**:
   - Go to: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Download "Build Tools for Visual Studio"
   - Run the installer

2. **Select Workloads**:
   - Check "Desktop development with C++"
   - Click Install (may take 15-30 minutes)

3. **Retry pip install**:
   ```bash
   pip install -r requirements.txt
   ```

**Alternative**: Use pre-compiled wheels from https://www.lfd.uci.edu/~gohlke/pythonlibs/ (advanced)

:::

:::{dropdown} pip command not found
:color: warning
:icon: alert

**Error Message**: "'pip' is not recognized as an internal or external command"

**Solutions** (try in order):

1. **Use python -m pip**:
   ```bash
   python -m pip install -r requirements.txt
   ```
   This explicitly calls pip through Python.

2. **Check PATH** (Windows):
   - During Python installation, was "Add to PATH" checked?
   - If not, reinstall Python with this option enabled

3. **Verify pip is installed**:
   ```bash
   python -m ensurepip --upgrade
   ```

**Why This Happens**: pip wasn't added to your system PATH during Python installation, so your terminal can't find it.

:::

:::{dropdown} Permission denied errors
:color: warning
:icon: alert

**Error Message**: "PermissionError: [Errno 13] Permission denied"

**Solutions** (try in order):

1. **Check virtual environment is activated**:
   - Look for `(venv)` prefix in your terminal prompt
   - If missing, run activation command again:
     ```bash
     # Windows
     venv\Scripts\activate.bat

     # Mac/Linux
     source venv/bin/activate
     ```

2. **Use --user flag** (if venv doesn't work):
   ```bash
   pip install --user -r requirements.txt
   ```
   This installs packages to your user directory instead of system-wide.

3. **Check folder permissions**:
   - Make sure you have write access to the project folder
   - On Windows, don't install in `C:\Program Files\`

**Why This Happens**: You're trying to install packages to a protected system location without proper permissions.

:::

:::{dropdown} Virtual environment activation fails (PowerShell)
:color: warning
:icon: tools

**Error Message**: "cannot be loaded because running scripts is disabled on this system"

**Why This Happens**: Windows PowerShell blocks script execution by default for security.

**Solution**:

1. **Check current execution policy**:
   ```powershell
   Get-ExecutionPolicy
   ```

2. **Allow script execution** (run PowerShell as Administrator):
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Activate virtual environment**:
   ```powershell
   venv\Scripts\Activate.ps1
   ```

4. **Verify activation**:
   - You should see `(venv)` in prompt

**Alternative**: Use Command Prompt instead:
```cmd
venv\Scripts\activate.bat
```

**Security Note**: `RemoteSigned` only affects scripts. It's safe for local development.

:::

:::{dropdown} Import errors after installation
:color: warning
:icon: alert

**Error Message**: "ModuleNotFoundError: No module named 'numpy'" (or other package)

**Solutions** (try in order):

1. **Verify virtual environment is activated**:
   ```bash
   # Check if (venv) appears in prompt
   # If not, activate it first
   ```

2. **Check packages are installed**:
   ```bash
   pip list | grep numpy
   # Or on Windows:
   pip list | findstr numpy
   ```

3. **Reinstall the package**:
   ```bash
   pip install numpy --force-reinstall
   ```

4. **Check Python interpreter**:
   ```bash
   which python   # Mac/Linux
   where python   # Windows
   ```
   Should point to `venv/bin/python` or `venv\Scripts\python.exe`

**Why This Happens**: You might be running a different Python interpreter that doesn't have access to the packages installed in your virtual environment.

**Pro Tip**: Always activate venv before running Python code!

:::

**Resources**:
- [pip Documentation](https://pip.pypa.io/en/stable/getting-started/)
- [Troubleshooting pip (Article)](https://realpython.com/what-is-pip/)

---

### Self-Assessment: Phase 1.3

**Checklist**:

- [ ] I can create and activate a virtual environment
- [ ] I have Git installed and can run `git --version`
- [ ] I successfully cloned the dip-smc-pso repository
- [ ] I installed all dependencies without errors
- [ ] `python simulate.py --help` shows usage instructions
- [ ] I understand what each major folder contains (src/, docs/, tests/)

**If all boxes checked**: Move to Phase 1.4
**If 4-5 boxes checked**: Review troubleshooting steps
**If 0-3 boxes checked**: Revisit installation steps, seek help in GitHub Discussions

</details>

---

<details>
<summary>1.4 Basic Physics Concepts</summary>

## Phase 1.4: Basic Physics Concepts (8 hours)

**Skip if**: You understand forces, torque, Newton's laws, and basic kinematics.

### What You'll Learn

- What is a pendulum and why does it swing?
- Forces and Newton's laws
- Torque and rotational motion
- Energy (potential, kinetic)
- Why double pendulums are chaotic

### Learning Path

:::{dropdown} Step 1: Forces and Newton's Laws (2 hours)
:animate: fade-in-slide-down
:color: info
:icon: mortar-board

Understand the fundamental laws that govern how objects move and interact.

**Newton's First Law** (Inertia):
- An object at rest stays at rest
- An object in motion stays in motion
- Unless acted upon by a force

**Example**: A pendulum at rest won't start swinging unless you push it.

**Newton's Second Law** (F = ma):
- Force = Mass × Acceleration
- Heavier objects need more force to accelerate

**Example**:
- Cart mass = 1 kg
- To accelerate at 2 m/s², need force = 1 × 2 = 2 Newtons

**Newton's Third Law** (Action-Reaction):
- For every action, there's an equal and opposite reaction

**Example**: When cart accelerates right, pendulum tilts left.

**Practice Exercise**:
1. If a cart has mass 2 kg and you apply 10 N force, what is the acceleration?
2. What happens to acceleration if you double the force?
3. What happens if you double the mass instead?

:::{dropdown} Exercise Solutions
:color: success
:icon: light-bulb

1. **Acceleration = Force / Mass = 10 N / 2 kg = 5 m/s²**

   Using F = ma, rearrange to get a = F/m.

2. **Acceleration doubles to 10 m/s²**

   If force doubles (20 N) and mass stays the same (2 kg):
   a = 20 / 2 = 10 m/s²

3. **Acceleration is cut in half to 2.5 m/s²**

   If mass doubles (4 kg) and force stays the same (10 N):
   a = 10 / 4 = 2.5 m/s²

**Key Insight**: Acceleration is directly proportional to force and inversely proportional to mass.

:::

**Resources**:
- [Newton's Laws Explained (Video, 15 min)](https://www.youtube.com/results?search_query=newton's+laws+explained+simply)
- [Khan Academy: Newton's Laws](https://www.khanacademy.org/science/physics/forces-newtons-laws)

:::

---

:::{dropdown} Step 2: Understanding Pendulums (3 hours)
:animate: fade-in-slide-down
:color: info
:icon: mortar-board

Learn how pendulums work and why they're important for control systems.

**What is a Pendulum?**
- A mass suspended from a fixed point that can swing freely
- Examples: Grandfather clock, playground swing, chandelier

**Why Does It Swing?**

1. **Gravity pulls it down**
   - Creates a restoring force toward the equilibrium (hanging straight down)

2. **Inertia keeps it moving**
   - When passing through equilibrium, it has velocity
   - Continues past equilibrium due to inertia

3. **Energy conversion**
   - At highest point: Maximum potential energy, zero kinetic energy
   - At lowest point: Zero potential energy, maximum kinetic energy
   - Energy constantly converts between potential and kinetic

**Key Variables**:
- **θ (theta)**: Angle from vertical (0 = straight down)
- **L**: Length of pendulum
- **m**: Mass of pendulum bob
- **g**: Gravitational acceleration (9.81 m/s²)

**Simple Pendulum Equation** (for small angles):
```
Period = 2π√(L/g)
```

**Example**:
- Length L = 1 meter
- Period = 2π√(1/9.81) ≈ 2 seconds (time for one complete swing)

**Interactive Demonstration**:

Try this online simulator:
- [PhET Pendulum Lab](https://phet.colorado.edu/sims/html/pendulum-lab/latest/pendulum-lab_en.html)

**Practice Exercise**:
1. What happens to the period if you double the length?
2. What happens if you double the mass?
3. What happens if you increase the initial angle?

:::{dropdown} Exercise Solutions
:color: success
:icon: light-bulb

1. **Period increases by √2 (about 1.41 times)**

   If L doubles: Period = 2π√(2L/g) = √2 × 2π√(L/g)

   Example: 1m pendulum (2 sec) --> 2m pendulum (2.83 sec)

2. **Period stays the same**

   Mass doesn't appear in the period equation! All pendulums with the same length have the same period, regardless of mass.

   This surprised Galileo when he first discovered it.

3. **Period increases slightly (for large angles)**

   The equation Period = 2π√(L/g) assumes small angles (< 15°).

   For larger angles, the period is longer because the pendulum takes a longer path.

**Key Insight**: Pendulum period depends only on length and gravity, not mass!

:::

**Resources**:
- [Pendulum Physics Explained (Video, 10 min)](https://www.youtube.com/results?search_query=pendulum+physics+explained)
- [Khan Academy: Pendulums](https://www.khanacademy.org/science/physics/mechanical-waves-and-sound/harmonic-motion/v/pendulum)

:::

---

:::{dropdown} Step 3: Double-Inverted Pendulum Basics (2 hours)
:animate: fade-in-slide-down
:color: info
:icon: mortar-board

Understand the specific challenges of the double-inverted pendulum system.

**What Makes It "Double"?**
- TWO pendulums connected in series
- First pendulum attached to cart
- Second pendulum attached to tip of first pendulum

**What Makes It "Inverted"?**
- Equilibrium is UPRIGHT (both vertical)
- NOT hanging down naturally
- Like balancing a broomstick on your hand

**Why Is This Hard?**

1. **Unstable Equilibrium**:
   - Upright position is unstable (like balancing a pencil on its point)
   - Any tiny disturbance causes it to fall
   - Requires constant correction

2. **Underactuated System**:
   - 1 input: Force on cart (left/right)
   - 3 degrees of freedom: Cart position, angle 1, angle 2
   - Can't directly control pendulum angles!

3. **Coupled Dynamics**:
   - Moving cart affects both pendulums
   - First pendulum motion affects second pendulum
   - Second pendulum motion affects first pendulum
   - Everything is interconnected

4. **Nonlinear Behavior**:
   - Small angle approximation (sin(θ) ≈ θ) doesn't work
   - Must use full nonlinear equations
   - Chaotic motion possible for large disturbances

**Analogy**:
Imagine balancing two broomsticks stacked end-to-end on a cart that you can only push left or right. That's the double-inverted pendulum challenge!

**Real-World Applications**:

- **Bipedal Robots**: Legs are like inverted pendulums
- **Rocket Landing**: Rocket body is inverted pendulum, thrust is control input
- **Human Standing**: Body segments as stacked pendulums, muscles provide control

**Visual Understanding**:

```
     O <-- m2 (second pendulum mass)
     |
     | L2 (second pendulum length)
     |
     O <-- m1 (first pendulum mass)
     |
     | L1 (first pendulum length)
     |
    [===] <-- Cart (mass m0)
     |||
  =========== <-- Track (cart moves left/right)
```

**State Variables** (what we need to track):
1. **x**: Cart position (meters)
2. **ẋ**: Cart velocity (meters/second)
3. **θ₁**: First pendulum angle from vertical (radians)
4. **θ̇₁**: First pendulum angular velocity (radians/second)
5. **θ₂**: Second pendulum angle from vertical (radians)
6. **θ̇₂**: Second pendulum angular velocity (radians/second)

**Practice Questions**:
1. Why can't we directly control the pendulum angles?
2. What happens if we push the cart to the right when both pendulums are tilting right?
3. Why is the upright position unstable?

:::{dropdown} Practice Solutions
:color: success
:icon: light-bulb

1. **Why can't we directly control the pendulum angles?**

   Because we only have ONE control input (force on cart), but THREE things to control (cart position, angle 1, angle 2). This is called an "underactuated" system.

   We can only indirectly influence the angles by moving the cart, which affects the pendulums through their connection points.

2. **What happens if we push the cart right when both pendulums tilt right?**

   It depends on how fast they're tilting! If tilting slowly: cart acceleration might help bring them back. If tilting fast: cart movement might make it worse.

   This is why control algorithms are complex - they must consider both position AND velocity of all components.

3. **Why is the upright position unstable?**

   Gravity always pulls the pendulums down. In the upright position, even the tiniest disturbance creates a torque that causes the pendulum to fall away from vertical.

   Unlike a hanging pendulum (where gravity pulls it BACK to equilibrium), an inverted pendulum has gravity pulling it AWAY from equilibrium.

:::

**Resources**:
- [Inverted Pendulum Explained (Video, 15 min)](https://www.youtube.com/results?search_query=inverted+pendulum+control+explained)
- [Double Pendulum Chaos (Video, 10 min)](https://www.youtube.com/results?search_query=double+pendulum+chaos)
- [Interactive Double Pendulum](https://www.myphysicslab.com/pendulum/double-pendulum-en.html)

:::

---

:::{dropdown} Step 4: Energy and Stability (1 hour)
:animate: fade-in-slide-down
:color: info
:icon: mortar-board

Learn about energy conversion and why some equilibrium positions are stable while others aren't.

**Potential Energy** (PE):
- Energy due to position in gravitational field
- PE = mgh (mass × gravity × height)
- Higher = more potential energy

**Kinetic Energy** (KE):
- Energy due to motion
- KE = ½mv² (half × mass × velocity squared)
- Faster = more kinetic energy

**Energy in Pendulum**:

- **At top of swing**: Maximum PE, zero KE (stopped momentarily)
- **At bottom**: Zero PE (lowest point), maximum KE (fastest)
- **Total energy conserved** (ignoring friction)

**Stability**:

- **Stable Equilibrium**: Small disturbances decay back to equilibrium
  - Example: Pendulum hanging straight down
  - Ball at bottom of bowl

- **Unstable Equilibrium**: Small disturbances grow, system falls away
  - Example: Inverted pendulum (upright)
  - Ball balanced on top of hill

**Why Control is Needed**:
- Double-inverted pendulum is unstable equilibrium
- Without control, any tiny disturbance causes it to fall
- Controller must constantly make corrections to keep it upright

**Resources**:
- [Potential vs Kinetic Energy (Video, 10 min)](https://www.youtube.com/results?search_query=potential+kinetic+energy+explained)
- [Stable vs Unstable Equilibrium (Article)](https://physics.info/equilibrium/)

:::

---

### Self-Assessment: Phase 1.4

**Quiz**:

1. What are Newton's three laws? (Summarize in one sentence each)
2. Why does a pendulum swing back and forth?
3. What makes the double-inverted pendulum "inverted"?
4. Why can't we directly control the pendulum angles?
5. What is an unstable equilibrium? Give an example.
6. If you double the length of a simple pendulum, what happens to its period?

**If you can answer 5-6 correctly**: Move to Phase 1.5
**If you can answer 3-4 correctly**: Review pendulum and stability concepts
**If you can answer 0-2 correctly**: Spend more time with Khan Academy physics resources

</details>

---

<details>
<summary>1.5 Basic Math Concepts</summary>

## Phase 1.5: Basic Math Concepts (5 hours)

**Skip if**: You're comfortable with functions, graphs, basic calculus (derivatives), and trigonometry.

### What You'll Learn

- Functions and graphs
- Trigonometry (sin, cos, angles)
- Derivatives (rate of change)
- Basic differential equations (conceptual)

### Learning Path

**Step 1: Functions and Graphs (1.5 hours)**

**What is a Function?**
- A relationship between input and output
- Example: f(x) = 2x (double the input)
- Input x=3 --> Output f(3) = 6

**Graphing Functions**:
- x-axis: Input (independent variable)
- y-axis: Output (dependent variable)
- Plot shows how output changes with input

**Example: Pendulum Angle Over Time**

```python
import numpy as np
import matplotlib.pyplot as plt

# Time from 0 to 10 seconds
t = np.linspace(0, 10, 100)

# Angle as function of time (damped oscillation)
theta = 0.5 * np.exp(-0.1*t) * np.cos(2*np.pi*t)

plt.plot(t, theta)
plt.xlabel('Time (seconds)')
plt.ylabel('Angle (radians)')
plt.title('Pendulum Angle vs Time')
plt.grid(True)
plt.show()
```

**Key Function Types**:

1. **Linear**: y = mx + b (straight line)
2. **Quadratic**: y = ax² + bx + c (parabola)
3. **Exponential**: y = a·eᵇˣ (growth/decay)
4. **Trigonometric**: y = A·sin(ωx + φ) (oscillation)

**Practice Exercise**:
Plot these functions from x = 0 to 10:
1. y = 2x + 1
2. y = x²
3. y = sin(x)

**Resources**:
- [Khan Academy: Functions](https://www.khanacademy.org/math/algebra/x2f8bb11595b61c86:functions)
- [Graphing Functions (Video, 20 min)](https://www.youtube.com/results?search_query=graphing+functions+explained)

---

**Step 2: Trigonometry Basics (1.5 hours)**

**Why Trigonometry?**
- Pendulum angles are measured in radians
- Sin and cos appear in pendulum equations
- Needed to understand rotational motion

**Key Concepts**:

**Angles**:
- **Degrees**: Full circle = 360°
- **Radians**: Full circle = 2π ≈ 6.28
- Conversion: radians = degrees × π/180

**Right Triangle**:
```
    |\
    | \  (hypotenuse)
  a |  \
    |   \
    |____\
      b
```

- sin(θ) = opposite/hypotenuse = a/c
- cos(θ) = adjacent/hypotenuse = b/c
- tan(θ) = opposite/adjacent = a/b

**Unit Circle**:
- Circle with radius 1
- Point on circle: (cos(θ), sin(θ))
- θ = 0: Point at (1, 0) --> Right
- θ = π/2: Point at (0, 1) --> Top
- θ = π: Point at (-1, 0) --> Left

**Pendulum Connection**:
- Pendulum angle θ measured from vertical
- Horizontal position: L·sin(θ)
- Vertical position: L·cos(θ)

**Small Angle Approximation**:
- For small θ (< 0.1 rad ≈ 6°):
  - sin(θ) ≈ θ
  - cos(θ) ≈ 1
- This simplifies equations!
- **Inverted pendulum needs full equations** (large angles possible)

**Practice Exercise**:

```python
import numpy as np
import matplotlib.pyplot as plt

# Angles from 0 to 2π
theta = np.linspace(0, 2*np.pi, 100)

# Plot sin and cos
plt.plot(theta, np.sin(theta), label='sin(θ)')
plt.plot(theta, np.cos(theta), label='cos(θ)')
plt.xlabel('θ (radians)')
plt.ylabel('Value')
plt.title('Sine and Cosine Functions')
plt.legend()
plt.grid(True)
plt.show()

# Verify small angle approximation
small_angle = 0.1  # radians
print(f"θ = {small_angle}")
print(f"sin(θ) = {np.sin(small_angle):.4f}")
print(f"θ      = {small_angle:.4f}")
print(f"Difference: {abs(np.sin(small_angle) - small_angle):.6f}")
```

**Resources**:
- [Khan Academy: Trigonometry](https://www.khanacademy.org/math/trigonometry)
- [Unit Circle Explained (Video, 15 min)](https://www.youtube.com/results?search_query=unit+circle+explained)

---

**Step 3: Derivatives (Rate of Change) (2 hours)**

**What is a Derivative?**
- Measures how fast something is changing
- Slope of a function at a point
- Example: Position --> Velocity (rate of change of position)

**Notation**:
- dx/dt: Derivative of x with respect to t (velocity)
- dθ/dt or θ̇: Derivative of θ (angular velocity)
- d²x/dt² or ẍ: Second derivative (acceleration)

**Physical Meaning**:

| Quantity | Symbol | Derivative | Physical Meaning |
|----------|--------|------------|------------------|
| Position | x | dx/dt = v | Velocity |
| Velocity | v | dv/dt = a | Acceleration |
| Angle | θ | dθ/dt = ω | Angular velocity |
| Angular velocity | ω | dω/dt = α | Angular acceleration |

**Example: Falling Ball**

```python
import numpy as np
import matplotlib.pyplot as plt

# Time
t = np.linspace(0, 2, 100)

# Position (starts at 20m, falls with gravity)
h = 20 - 0.5 * 9.81 * t**2

# Velocity (derivative of position)
v = -9.81 * t

# Acceleration (derivative of velocity)
a = -9.81 * np.ones_like(t)

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 10))

ax1.plot(t, h)
ax1.set_ylabel('Height (m)')
ax1.set_title('Position vs Time')
ax1.grid(True)

ax2.plot(t, v)
ax2.set_ylabel('Velocity (m/s)')
ax2.set_title('Velocity (derivative of position)')
ax2.grid(True)

ax3.plot(t, a)
ax3.set_xlabel('Time (s)')
ax3.set_ylabel('Acceleration (m/s²)')
ax3.set_title('Acceleration (derivative of velocity)')
ax3.grid(True)

plt.tight_layout()
plt.show()
```

**Derivatives in This Project**:

State vector includes both positions AND velocities:
```
[x, ẋ, θ₁, θ̇₁, θ₂, θ̇₂]
 ^  ^   ^   ^    ^   ^
 |  |   |   |    |   dθ₂/dt (second pendulum angular velocity)
 |  |   |   |    θ₂ (second pendulum angle)
 |  |   |   dθ₁/dt (first pendulum angular velocity)
 |  |   θ₁ (first pendulum angle)
 |  dx/dt (cart velocity)
 x (cart position)
```

**Differential Equations** (conceptual):
- Equations that relate quantities to their derivatives
- Example: Newton's 2nd Law: F = m·a = m·(dv/dt)
- Pendulum dynamics are differential equations
- Simulation "integrates" these equations to find motion over time

**You Don't Need to Calculate Derivatives by Hand**:
- The computer does it for you
- Just understand what they represent physically

**Resources**:
- [Derivatives Explained (Video, 20 min)](https://www.youtube.com/results?search_query=derivatives+explained+simply)
- [Khan Academy: Derivatives](https://www.khanacademy.org/math/calculus-1/cs1-derivatives-definition-and-basic-rules)
- [3Blue1Brown: Essence of Calculus (Video Series, 3 hours)](https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr)

---

### Self-Assessment: Phase 1.5

**Quiz**:

1. Graph y = sin(x) from 0 to 2π. What is its maximum value?
2. Convert 90 degrees to radians.
3. What is the derivative of position with respect to time?
4. If θ(t) = 0.5·cos(2t), what is θ̇(t) (conceptually)?
5. Why do we track both x and ẋ in the state vector?

**Practical Test**:

Write Python code to:
1. Create time array from 0 to 5 seconds
2. Calculate position: x(t) = 10·sin(πt)
3. Plot both x(t) and its approximate derivative (using np.gradient)

**If you can complete the quiz and practical test**: Move to Phase 2
**If you struggle with derivatives**: Review calculus concepts
**If you struggle with trigonometry**: Review unit circle and sin/cos

</details>

---


## Learning Resources

```{grid} 1 1 2 3
:gutter: 2

```{grid-item-card} YouTube: Phase 1 Tutorials
:link: https://www.youtube.com/results?search_query=python+programming+beginners+2024
:link-type: url
:text-align: center

Watch video tutorials for Python, command line, and physics basics
[View -->]

```

```{grid-item-card} Article: Computing & Python Concepts
:link: https://realpython.com/learning-paths/python3-introduction/
:link-type: url
:text-align: center

Read detailed explanations and examples for beginners
[Read -->]

```

```{grid-item-card} Interactive Quiz
:link: #self-assessment-phase-15
:link-type: url
:text-align: center

Test your understanding of Phase 1 concepts
[Take Quiz -->]

```
```

---
## Phase 1 Complete!

**Achievement Unlocked**: Foundation Builder

You now have:
- Python programming skills
- Development environment set up
- Basic physics understanding
- Essential math concepts

**Time to Celebrate!** Take a break, you've earned it.

**Next Phase**: [Phase 2: Core Concepts -->](phase-2-core-concepts.md)

---

**Navigation:**
- **Next**: [Phase 2: Core Concepts](phase-2-core-concepts.md) -->
- [<-- Back to Beginner Roadmap](../beginner-roadmap.md)

---

## Next Steps

Ready to move on? [--> Phase 2: Core Concepts](phase-2-core-concepts.md)

Or [<-- Back to Beginner Roadmap](../beginner-roadmap.md)
