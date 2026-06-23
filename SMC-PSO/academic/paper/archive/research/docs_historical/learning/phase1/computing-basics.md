<!-- AUTO-GENERATED from .project/ai/edu/ - DO NOT EDIT DIRECTLY -->
<!-- Source: .project/ai/edu/phase1/computing-basics.md -->
<!-- Generated: 2025-11-11 13:29:26 -->

# Computing Basics - Starting from Zero

**Time Required**: 10-12 hours
**Prerequisites**: None - absolute beginner friendly

------

## What You'll Learn

By the end of this module, you'll understand:
- What computers and programs are
- How to navigate your operating system
- Command line basics for Windows
- How to install Python and development tools
- How to organize code projects

------

## 1. What is a Computer?

A computer is a machine that follows instructions to process information. Think of it like a very fast, very precise calculator that can also remember things and follow complex recipes (programs).

### Key Components

**Hardware** (physical parts):
- **CPU (Central Processing Unit)**: The "brain" that executes instructions
- **RAM (Random Access Memory)**: Short-term memory for running programs
- **Storage (SSD/HDD)**: Long-term memory for saving files
- **Input/Output**: Keyboard, mouse, monitor, network

**Software** (instructions):
- **Operating System (OS)**: Windows, Linux, macOS - manages hardware
- **Applications**: Programs you run (web browser, text editor, Python)
- **Files**: Data stored on disk (documents, images, code)

------

## 2. What is Programming?

Programming is writing instructions that a computer can follow. These instructions are written in a **programming language** (like Python) that both humans and computers can understand.

### Why Python?

Python is ideal for beginners because:
- **Readable**: Looks almost like English
- **Forgiving**: Helps you find mistakes easily
- **Powerful**: Used by NASA, Google, scientific research
- **Popular**: Huge community, tons of tutorials

### Example: Your First Program

```python
print("Hello, world!")
```

This single line tells the computer: "Display the text 'Hello, world!' on the screen."

------

## 3. Operating System Basics (Windows Focus)

### File System Hierarchy

Your files are organized in a tree structure:

```
C:\                          (root drive)
├─ Users\
│  └─ YourName\
│     ├─ Documents\
│     ├─ Downloads\
│     └─ Desktop\
├─ Program Files\
└─ Windows\
```

### File Paths

A **path** tells the computer where a file lives:
- **Absolute path**: Full address from the root
  - Example: `C:\Users\YourName\Documents\project\code.py`
- **Relative path**: Address from your current location
  - Example: `project\code.py` (if you're in `Documents\`)

### File Extensions

The ending of a filename tells you the file type:
- `.py` - Python script
- `.txt` - Text file
- `.csv` - Data file (comma-separated values)
- `.md` - Markdown documentation

------

## 4. Command Line Interface (CLI)

The **command line** (also called terminal, shell, or PowerShell) lets you control your computer by typing commands instead of clicking icons.

### Why Learn the Command Line?

- **Faster**: Type commands vs. clicking through menus
- **Powerful**: Access advanced features not in GUI
- **Required**: Many development tools are CLI-only
- **Professional**: Industry standard for software development

### Opening PowerShell on Windows

1. Press `Win + X`
2. Select "Windows PowerShell" or "Terminal"
3. You'll see a prompt like: `PS C:\Users\YourName>`

### Essential Commands

#### Navigation

```powershell
# See where you are
pwd

# List files in current directory
ls

# Change directory (move into a folder)
cd Documents

# Go up one level
cd ..

# Go to specific path
cd C:\Users\YourName\Projects
```

#### File Operations

```powershell
# Create a new directory
mkdir my_project

# Create an empty file
New-Item -Path "file.txt" -ItemType File

# Copy a file
Copy-Item source.txt destination.txt

# Move a file
Move-Item file.txt new_location\

# Delete a file (careful!)
Remove-Item file.txt
```

#### Getting Help

```powershell
# Get help for any command
Get-Help ls
Get-Help cd -Examples
```

### Practice Exercise 1

Try these commands in PowerShell:

```powershell
# Create a test project
cd ~\Desktop
mkdir python_practice
cd python_practice
New-Item -Path "hello.py" -ItemType File
ls
```

You should see `hello.py` listed.

------

## 5. Installing Python

### Step 1: Download Python

1. Visit https://www.python.org/downloads/
2. Download the latest Python 3.x (e.g., Python 3.11)
3. Run the installer

### Step 2: Installation Options

**IMPORTANT**: Check "Add Python to PATH" during installation!

This lets you run Python from any command line location.

### Step 3: Verify Installation

```powershell
python --version
```

You should see: `Python 3.11.x` (or similar)

### Step 4: Test Python Interactive Mode

```powershell
python
```

You'll see a prompt: `>>>`

Try this:

```python
>>> print("Hello from Python!")
>>> 2 + 2
>>> exit()
```

------

## 6. Installing a Code Editor

You need a text editor designed for code. Recommended options:

### Option 1: Visual Studio Code (VS Code) - Recommended

**Pros**: Free, powerful, huge community, great Python support

**Installation**:
1. Visit https://code.visualstudio.com/
2. Download and install
3. Install "Python" extension (by Microsoft)

**Basic Usage**:
1. Open VS Code
2. File → Open Folder → Select `python_practice`
3. Click on `hello.py`
4. Type: `print("Hello, VS Code!")`
5. Save (Ctrl+S)
6. Right-click editor → Run Python File in Terminal

### Option 2: Notepad++ (Lightweight)

Good for quick edits, less features than VS Code.

### Option 3: PyCharm Community (Full IDE)

More features, but heavier and more complex for beginners.

------

## 7. Virtual Environments

A **virtual environment** is an isolated Python setup for each project. This prevents conflicts between different projects' dependencies.

### Why Virtual Environments?

Imagine Project A needs numpy version 1.20, but Project B needs version 1.26. Virtual environments let each project have its own versions.

### Creating a Virtual Environment

```powershell
# Navigate to your project
cd ~\Desktop\python_practice

# Create virtual environment named 'venv'
python -m venv venv

# Activate it (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# You'll see (venv) in your prompt:
# (venv) PS C:\Users\YourName\Desktop\python_practice>
```

### Installing Packages

With the virtual environment active:

```powershell
# Install a package
pip install numpy

# Install multiple packages
pip install numpy scipy matplotlib

# See installed packages
pip list
```

### Deactivating

```powershell
deactivate
```

------

## 8. Project Organization Best Practices

### Standard Python Project Structure

```
my_project/
├─ venv/                 # Virtual environment (don't commit to Git)
├─ src/                  # Source code
│  ├─ __init__.py
│  └─ main.py
├─ tests/                # Test files
│  └─ test_main.py
├─ docs/                 # Documentation
├─ data/                 # Data files
├─ requirements.txt      # List of dependencies
├─ README.md             # Project description
└─ .gitignore            # Files to ignore in version control
```

### Creating requirements.txt

```powershell
# After installing packages
pip freeze > requirements.txt
```

This creates a file listing all installed packages and versions. Others can recreate your environment with:

```powershell
pip install -r requirements.txt
```

------

## 9. Git Basics (Version Control)

**Git** tracks changes to your code over time. Think of it as "Track Changes" for code projects.

### Installing Git

1. Download from https://git-scm.com/
2. Install with default options
3. Verify: `git --version`

### Essential Git Commands

```powershell
# Initialize a Git repository
git init

# Check status
git status

# Stage files for commit
git add file.py
git add .              # Stage all changed files

# Commit changes (save a snapshot)
git commit -m "Descriptive message about what changed"

# View commit history
git log
```

### Typical Workflow

```powershell
# Make changes to code
# ...

# Check what changed
git status
git diff

# Stage and commit
git add .
git commit -m "Add hello world function"
```

------

## 10. Common Beginner Mistakes

### Mistake 1: Forgetting to Activate Virtual Environment

**Symptom**: `pip install numpy` installs globally instead of in project

**Solution**: Always activate venv first (`.\venv\Scripts\Activate.ps1`)

### Mistake 2: Wrong Directory

**Symptom**: "File not found" errors

**Solution**: Use `pwd` to check location, `cd` to navigate

### Mistake 3: Spaces in Paths

```powershell
# WRONG - spaces break the command
cd C:\Users\My Name\Documents

# RIGHT - use quotes
cd "C:\Users\My Name\Documents"
```

### Mistake 4: Confusing Python Versions

**Symptom**: Multiple Python versions installed, wrong one runs

**Solution**: Use `python --version` to check, or use specific version:
```powershell
py -3.11 script.py
```

------

## 11. Hands-On Practice Exercises

### Exercise 1: Setup Your First Project

```powershell
# Create project structure
cd ~\Desktop
mkdir dip_practice
cd dip_practice
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install numpy matplotlib

# Save dependencies
pip freeze > requirements.txt

# Verify
ls
```

### Exercise 2: Write and Run Your First Script

Create `calculate.py`:

```python
# calculate.py - My first useful program

def add_numbers(a, b):
    """Add two numbers and return the result."""
    return a + b

def main():
    """Main entry point."""
    result = add_numbers(5, 7)
    print(f"5 + 7 = {result}")

if __name__ == "__main__":
    main()
```

Run it:

```powershell
python calculate.py
```

Expected output: `5 + 7 = 12`

### Exercise 3: Git Version Control

```powershell
git init
git add calculate.py requirements.txt
git commit -m "Initial commit: add calculator"

# Make a change to calculate.py (add a subtract function)
# Then:
git status
git diff
git add calculate.py
git commit -m "Add subtract function"
git log
```

------

## 12. Troubleshooting

### Problem: "python: command not found"

**Solution**: Python not in PATH. Reinstall and check "Add to PATH" option.

### Problem: "Activate.ps1 cannot be loaded" (PowerShell)

**Solution**: Execution policy issue. Run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: pip installs packages but can't import them

**Solution**: Virtual environment not activated, or using wrong Python interpreter.

------

## 13. Next Steps

You're ready for `python-fundamentals.md` when you can:

- [ ] Open PowerShell and navigate directories
- [ ] Create files and folders from command line
- [ ] Install Python and verify version
- [ ] Create and activate a virtual environment
- [ ] Install packages with pip
- [ ] Write and run a simple Python script
- [ ] Initialize a Git repository and make commits

------

## Additional Resources

### Official Documentation
- Python: https://docs.python.org/3/tutorial/
- Git: https://git-scm.com/book/en/v2

### Interactive Tutorials
- Command Line: https://www.codecademy.com/learn/learn-the-command-line
- Git: https://learngitbranching.js.org/

### Cheat Sheets
- See `cheatsheets/cli-reference.md`
- See `cheatsheets/git-commands.md`

------

**Last Updated**: 2025-10-17
**Estimated Time**: 10-12 hours
**Next Module**: `python-fundamentals.md`
