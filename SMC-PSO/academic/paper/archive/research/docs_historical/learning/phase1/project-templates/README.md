<!-- AUTO-GENERATED from .project/ai/edu/ - DO NOT EDIT DIRECTLY -->
<!-- Source: .project/ai/edu/phase1/project-templates/README.md -->
<!-- Generated: 2025-11-11 13:29:26 -->

# Project Templates - Quick Start for Your Own Projects

This directory contains starter templates for common project types. Copy and customize these templates to begin your own projects quickly.

------

## Available Templates

### 1. `basic_python_project/`
**Purpose**: General-purpose Python project structure

**Use when**: Starting any Python project that needs organization

**Contains**:
- Project directory structure
- Example main script
- requirements.txt template
- .gitignore
- README template

### 2. `simple_simulation/`
**Purpose**: Physics simulation with plotting

**Use when**: Building simulations (pendulum, mass-spring, etc.)

**Contains**:
- Simulation class template
- Main runner script
- Plotting utilities
- Configuration file

### 3. `data_analysis/`
**Purpose**: Data analysis and visualization

**Use when**: Analyzing CSV data, plotting results

**Contains**:
- Data loading utilities
- Analysis functions
- Plotting templates
- Sample data

------

## How to Use Templates

### Step 1: Copy Template

```powershell
# Navigate to your projects directory
cd ~\Desktop

# Copy template
Copy-Item -Recurse ".ai\edu\phase1\project-templates\basic_python_project" "my_project"

# Navigate to new project
cd my_project
```

### Step 2: Set Up Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Customize

1. Edit `README.md` with your project details
2. Rename files as needed
3. Modify code to fit your requirements
4. Add your own modules

### Step 4: Initialize Git

```powershell
git init
git add .
git commit -m "Initial commit from template"
```

------

## Template Customization Tips

### Update Project Name

Replace all instances of "PROJECT_NAME" with your actual project name:
- In README.md
- In script headers
- In configuration files

### Modify Dependencies

Edit `requirements.txt` to include only packages you need:

```
# Remove unused packages
# Add new packages your project requires
numpy>=1.24.0
matplotlib>=3.7.0
scipy>=1.10.0
```

### Adjust Directory Structure

Add/remove directories based on your needs:

```
my_project/
├─ src/           # Keep if you have modules
├─ tests/         # Keep if you're writing tests
├─ data/          # Add if you have data files
├─ results/       # Add for output files
└─ notebooks/     # Add if using Jupyter
```

------

## Example: Creating a Pendulum Project

```powershell
# Copy simulation template
Copy-Item -Recurse "project-templates\simple_simulation" "pendulum_project"
cd pendulum_project

# Set up environment
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Rename files
Move-Item simulation.py pendulum.py

# Edit pendulum.py to implement pendulum dynamics
# Edit config.yaml to set pendulum parameters

# Run
python pendulum.py
```

------

## Best Practices

### 1. Always Use Virtual Environments

Keeps project dependencies isolated:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Pin Dependency Versions

In `requirements.txt`:

```
# GOOD - specific versions
numpy==1.24.3
matplotlib==3.7.1

# ACCEPTABLE - minimum versions
numpy>=1.24.0
matplotlib>=3.7.0

# BAD - no version constraints
numpy
matplotlib
```

### 3. Document Your Code

Add docstrings to all functions:

```python
def calculate_energy(theta, omega):
    """
    Calculate total mechanical energy.

    Args:
        theta: Angle (rad)
        omega: Angular velocity (rad/s)

    Returns:
        Total energy (J)
    """
    # Implementation...
```

### 4. Use Version Control

Commit often with clear messages:

```powershell
git add .
git commit -m "Add energy calculation function"
```

### 5. Test Your Code

Add simple tests to verify correctness:

```python
def test_calculate_energy():
    # Test with known values
    theta = 0
    omega = 0
    energy = calculate_energy(theta, omega)
    assert energy == 0, "Energy should be zero at rest"
```

------

## Template Structure Philosophy

### Keep It Simple

Templates are intentionally minimal:
- Easy to understand
- Quick to set up
- No unnecessary complexity

### Easy to Extend

Add features as needed:
- More modules
- Additional tests
- Configuration options
- Documentation

### Professional Standards

Follow best practices:
- Clear naming
- Proper documentation
- Version control ready
- Reproducible environment

------

## Next Steps After Copying Template

1. **Read the template's README.md**
2. **Run the example code** to see it works
3. **Understand the structure** before modifying
4. **Make small changes** and test frequently
5. **Commit your changes** regularly

------

## Getting Help

**Template not working?**
1. Check Python version: `python --version`
2. Verify virtual environment is active: `(venv)` in prompt
3. Reinstall dependencies: `pip install -r requirements.txt`
4. Check file paths (use absolute paths if needed)

**Need a different template?**
- Create your own based on these examples
- Request new templates in project issues
- Share your templates with others!

------

**Last Updated**: 2025-10-17
