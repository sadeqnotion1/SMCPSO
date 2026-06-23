# Phase 1 NotebookLM Podcast: Episode 7 - Virtual Environments and Git

**Duration**: 22-25 minutes | **Learning Time**: 3 hours | **Difficulty**: Beginner

---

## Opening Hook

Imagine you're a chef with two restaurants. One serves Italian food and needs basil, oregano, and olive oil. The other serves Thai food and needs lemongrass, fish sauce, and coconut milk. You wouldn't mix all these ingredients in one kitchen - they'd interfere with each other.

The same problem exists in programming. Different projects need different versions of libraries. Project A might require NumPy version 1.20, while Project B needs version 2.0. How do you keep them separate? That's what virtual environments solve.

And once you're working on projects, you need version control - a system that tracks every change, lets you experiment safely, and enables collaboration. That's what Git provides.

Today, you'll learn the essential tools that professional developers use daily. By the end, you'll have the DIP-SMC-PSO project running on your machine with proper dependency isolation and version control.

---

## What You'll Discover

By listening to this episode, you'll learn:

- What virtual environments are and why they're essential
- Creating and activating virtual environments
- Installing packages with pip
- Understanding requirements dot txt files
- What Git is and why version control matters
- Cloning repositories from GitHub
- Basic Git commands: status, add, commit
- How to update your local copy from remote

---

## The Problem: Dependency Conflicts

Let's understand why we need virtual environments.

**Scenario**: You have two Python projects on your computer:

Project A requires:
- NumPy version 1 dot 20
- Matplotlib version 3 dot 3

Project B requires:
- NumPy version 2 dot 0
- Matplotlib version 3 dot 7

If you install packages globally (system-wide), you can only have ONE version of each package. Installing NumPy 2.0 for Project B breaks Project A, which needs 1.20.

**The Solution**: Virtual Environments

A virtual environment is an isolated Python installation for one project. It has its own packages, completely separate from other projects.

Think of it as: Each project gets its own kitchen with its own ingredients. They don't interfere.

---

## Creating a Virtual Environment

Let's create a virtual environment for the DIP-SMC-PSO project.

**Step One: Navigate to Your Projects Folder**

Open your terminal (Command Prompt on Windows, Terminal on Mac/Linux) and navigate:

Windows:
c-d space C colon backslash Users backslash YourName backslash Projects

Mac/Linux:
c-d space forward slash home forward slash yourname forward slash Projects

If you don't have a Projects folder yet, create one:

Windows:
m-k-d-i-r space Projects
c-d space Projects

Mac/Linux:
m-k-d-i-r space Projects
c-d space Projects

**Step Two: Create the Virtual Environment**

Windows:
python space dash m space v-e-n-v space v-e-n-v

Mac/Linux:
python3 space dash m space v-e-n-v space v-e-n-v

Let's break this down:
- **python** or **python3** - The Python interpreter
- **dash m** - Run a module
- **v-e-n-v** - The virtual environment module (built into Python)
- **v-e-n-v** - The name of the folder to create (you can choose any name, but "venv" is conventional)

This creates a folder called "venv" containing a complete Python installation.

**Step Three: Activate the Virtual Environment**

This is where things differ between operating systems.

Windows Command Prompt:
v-e-n-v backslash Scripts backslash activate dot bat

Windows PowerShell:
v-e-n-v backslash Scripts backslash Activate dot ps1

Mac/Linux:
source space v-e-n-v forward slash bin forward slash activate

You'll see your prompt change. It now shows:
open-parenthesis v-e-n-v close-parenthesis space your normal prompt

That prefix tells you the virtual environment is active.

**Step Four: Verify Activation**

Windows:
where space python

Mac/Linux:
which space python

You should see a path that includes "venv" - something like:
C colon backslash Users backslash YourName backslash Projects backslash v-e-n-v backslash Scripts backslash python dot exe

This confirms Python is now coming from your virtual environment, not the system installation.

---

## Installing Packages with pip

**pip** is Python's package installer. It downloads and installs libraries from the Python Package Index (PyPI).

**Upgrading pip First**

Always start by upgrading pip itself:

python space dash m space p-i-p space install space dash dash upgrade space p-i-p

This ensures you have the latest installer.

**Installing a Single Package**

To install NumPy:

p-i-p space install space n-u-m-p-y

pip downloads NumPy and its dependencies, installs them in your virtual environment, and confirms success.

**Listing Installed Packages**

p-i-p space list

You'll see a list of all packages in your environment and their versions.

**Checking a Specific Package**

p-i-p space show space n-u-m-p-y

This shows details: version, location, dependencies.

---

## Requirements Files: Project Dependencies

Instead of installing packages one by one, projects use requirements files that list all dependencies.

**What is requirements dot txt?**

A plain text file listing packages and their versions:

n-u-m-p-y equals equals 1 dot 24 dot 3
m-a-t-plot-l-i-b equals equals 3 dot 8 dot 0
s-c-i-p-y equals equals 1 dot 11 dot 2

**Installing from requirements dot txt**

p-i-p space install space dash r space requirements dot txt

pip reads the file and installs every listed package with the exact specified version. This ensures everyone working on the project has identical environments.

**Creating a requirements file**

If you want to save your current environment:

p-i-p space freeze space greater-than space requirements dot txt

This generates a file listing everything currently installed.

---

## Recap: Virtual Environments

Let's pause and review what you've learned:

**Number one**: Virtual environments isolate project dependencies. Each project has its own Python installation and packages.

**Number two**: Create with: python dash m venv venv

**Number three**: Activate before working:
- Windows CMD: venv backslash Scripts backslash activate dot bat
- Windows PS: venv backslash Scripts backslash Activate dot ps1
- Mac/Linux: source venv forward slash bin forward slash activate

**Number four**: Install packages with: pip install package-name

**Number five**: Install all project dependencies with: pip install dash r requirements dot txt

**Number six**: Always activate your virtual environment before working on a project.

Now let's learn Git, the version control system.

---

## What Is Git?

Git is a version control system. It tracks changes to files over time, enabling:

- **History**: See every change ever made, who made it, and when
- **Undo**: Revert to any previous version
- **Branching**: Experiment without affecting the main codebase
- **Collaboration**: Multiple people work on the same project simultaneously
- **Backup**: Your code lives on remote servers (like GitHub), not just your laptop

Think of Git like "Track Changes" in Microsoft Word, but for entire projects, with powerful features for collaboration.

**Git vs GitHub**

- **Git**: The version control software running on your computer
- **GitHub**: A website that hosts Git repositories online

Git is the tool. GitHub is a hosting service (like Google Drive, but for Git repos).

---

## Installing Git

**Windows**

Download from: https colon forward slash forward slash git dash scm dot com forward slash download forward slash win

Run the installer with default settings.

Verify installation:
g-i-t space dash dash version

**Mac**

Git is usually pre-installed. Check:
g-i-t space dash dash version

If not installed:
brew space install space g-i-t

Or install Xcode Command Line Tools:
xcode dash select space dash dash install

**Linux**

Ubuntu/Debian:
sudo space a-p-t space update
sudo space a-p-t space install space g-i-t

Verify:
g-i-t space dash dash version

---

## Cloning the DIP-SMC-PSO Repository

Now let's download the project from GitHub.

**Step One: Navigate to Your Projects Folder**

Make sure your virtual environment is activated, then:

c-d space to your Projects folder

**Step Two: Clone the Repository**

g-i-t space clone space https colon forward slash forward slash github dot com forward slash theSadeQ forward slash dip dash smc dash pso dot git

Git downloads the entire project history and creates a folder called "dip-smc-pso".

**Step Three: Enter the Project Directory**

c-d space dip dash smc dash pso

**Step Four: List Contents**

Windows: d-i-r
Mac/Linux: l-s

You should see:
- simulate dot py
- config dot yaml
- requirements dot txt
- src folder
- tests folder
- docs folder
- README dot md

You now have the complete project on your computer!

---

## Installing Project Dependencies

The project includes requirements dot txt listing all needed packages.

**Make Sure Virtual Environment Is Active**

You should see (venv) in your prompt. If not, activate it again.

**Install Dependencies**

p-i-p space install space dash r space requirements dot txt

This installs ~50 packages: NumPy, SciPy, Matplotlib, PyYAML, Numba, PySwarms, pytest, Streamlit, and more.

This may take 2-5 minutes.

**Verify Installation**

Try running the main program:

python space simulate dot py space dash dash help

You should see usage instructions. If so, everything is installed correctly!

---

## Basic Git Commands

Now that you have the repository, let's learn essential Git commands.

**git status** - Show Current State

g-i-t space status

This shows:
- Which branch you're on (usually "main")
- Which files have changed
- Which files are staged for commit

Run this frequently to understand what Git sees.

**git log** - View History

g-i-t space log space dash dash oneline space dash dash max-count equals 10

This shows the last 10 commits (snapshots) with their messages. Each commit has:
- A unique identifier (hash)
- Author
- Date
- Message describing what changed

**git diff** - See What Changed

If you modify a file, see the changes:

g-i-t space diff

This shows:
- Which files changed
- Lines removed (red, with minus)
- Lines added (green, with plus)

---

## Making Changes and Committing

Let's practice the Git workflow.

**Step One: Make a Change**

Open config dot yaml in your text editor. Add a comment:

# My first edit

Save the file.

**Step Two: Check Status**

g-i-t space status

You'll see config dot yaml listed as "modified".

**Step Three: Stage the Change**

g-i-t space add space config dot yaml

This tells Git: "Include this change in the next commit."

**Step Four: Commit the Change**

g-i-t space commit space dash m space "Add comment to config"

The dash m flag provides a message describing what you changed.

Git saves a snapshot with your message, timestamp, and author.

**Step Five: Verify**

g-i-t space log space dash dash oneline space dash 1

You'll see your new commit at the top.

---

## Pulling Updates from GitHub

The repository on GitHub may have new changes (from the maintainer or other contributors). Update your local copy:

**Step One: Fetch Latest**

g-i-t space fetch space origin

This downloads new changes but doesn't apply them yet.

**Step Two: Merge Changes**

g-i-t space pull space origin space main

This merges remote changes into your local branch.

Or combine both steps:

g-i-t space pull

Run this periodically to stay up-to-date.

---

## The .gitignore File

Some files shouldn't be tracked by Git:
- Cache files (underscore underscore pycache underscore underscore)
- Virtual environment folder (venv)
- IDE settings (.vscode, .idea)
- Large data files

The dot gitignore file lists patterns to ignore:

underscore underscore pycache underscore underscore forward slash
asterisk dot pyc
v-e-n-v forward slash
dot vscode forward slash
asterisk dot log

Git automatically excludes these files from commits.

---

## Pronunciation Guide

Technical terms from this episode with phonetic pronunciations:

- **Virtual environment**: VUR-choo-ul en-VY-run-ment (isolated Python installation)
- **venv**: "v-e-n-v" or "vee env" (virtual environment module)
- **pip**: Just "pip" (package installer for Python)
- **PyPI**: "pie-p-i" (Python Package Index)
- **Git**: Just "git" (rhymes with "bit")
- **GitHub**: "git hub" (online hosting for Git repositories)
- **Repository**: rih-PAH-zih-tor-ee (project folder tracked by Git)
- **Clone**: KLOHN (download a repository)
- **Commit**: kuh-MIT (save a snapshot of changes)
- **Branch**: BRANCH (separate line of development)
- **Pull**: POOL (download and merge changes)

---

## Common Issues and Solutions

**Issue One: "python3 not found" on Windows**

On Windows, use "python", not "python3".

**Issue Two: Virtual environment won't activate in PowerShell**

PowerShell blocks scripts by default. Run PowerShell as Administrator:

Set dash ExecutionPolicy space RemoteSigned

Then try activating again.

**Issue Three: Permission errors when installing packages**

Make sure your virtual environment is activated. The prompt should show (venv).

If still failing, try:

p-i-p space install space dash dash user space package-name

**Issue Four: Git asks for username/password repeatedly**

Configure Git to remember credentials:

g-i-t space config space dash dash global space credential dot helper space store

Next time you enter credentials, Git remembers them.

---

## Why This Matters for Control Systems

These tools are essential for control systems development:

**Reason One: Reproducibility**

Virtual environments ensure your simulation results are reproducible. Everyone uses the exact same library versions.

**Reason Two: Dependency Management**

The DIP-SMC-PSO project has ~50 dependencies. requirements dot txt makes installation trivial.

**Reason Three: Version Control**

As you experiment with controllers, you can:
- Commit working code
- Try new approaches
- Revert if experiments fail
- Compare different controller implementations

**Reason Four: Collaboration**

Git enables multiple people to work on the project simultaneously without stepping on each other's toes.

**Reason Five: Documentation**

Git commit messages document WHY changes were made, not just WHAT changed.

---

## What's Next: Newton's Laws and Pendulum Physics

In Episode 8, we'll dive into the physics underlying the double-inverted pendulum:

- Newton's three laws of motion
- Forces, torque, and rotational motion
- Why pendulums swing
- Stable vs unstable equilibria
- The physics equations we'll simulate

These concepts connect the math and code you've learned to the physical system you're controlling.

---

## Pause and Reflect

Before moving on, test your understanding:

1. Why do we need virtual environments?
2. How do you activate a virtual environment on your operating system?
3. What command installs all packages from requirements dot txt?
4. What's the difference between Git and GitHub?
5. What does "git status" show you?

If you struggled with any of these, review the relevant section. Practice by creating a virtual environment and cloning a repository.

---

**Episode 7 of 11** | Phase 1: Foundations

**Previous**: [Episode 6: NumPy and Matplotlib Basics](phase1_episode06.md) | **Next**: [Episode 8: Newton's Laws and Pendulum Physics](phase1_episode08.md)
