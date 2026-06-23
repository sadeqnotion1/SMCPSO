#==========================================================================================\
#====================================== setup.py ==========================================\
#==========================================================================================\

"""
Double-Inverted Pendulum (DIP) SMC-PSO Package Configuration.

This setup script uses setuptools to package the project. It provides:
1. Standard installation via pip:
   $ pip install .
2. Editable installation for developers (changes reflect immediately in execution):
   $ pip install -e .
3. Extras groupings for targeted environments:
   - Developer tools:       $ pip install -e .[dev]
   - Documentation tools:   $ pip install -e .[docs]
   - Testing tools:         $ pip install -e .[test]
   - All environments:      $ pip install -e .[all]

Designed to dynamically parse 'requirements.txt' to guarantee dependency synchronization.
"""

import os
import re
from pathlib import Path
from typing import List

from setuptools import find_packages, setup

# -----------------------------------------------------------------------------
# Project Metadata
# -----------------------------------------------------------------------------
# NAME: The distribution name of the package on PyPI/local environments.
NAME = "dip-smc-pso"

# VERSION: SemVer version string indicating stable API iteration.
VERSION = "1.0.0"

# DESCRIPTION: A short summary of the package's goal.
DESCRIPTION = (
    "Advanced Sliding Mode Control for Double-Inverted Pendulum with PSO Optimization"
)

# LONG_DESCRIPTION: Comprehensive description rendered on the package landing page.
LONG_DESCRIPTION = """
A comprehensive Python framework for simulating, controlling, and analyzing a
double-inverted pendulum (DIP) system using advanced sliding mode control (SMC)
techniques with Particle Swarm Optimization (PSO).

Features:
- Multiple SMC variants (Classical, Super-Twisting, Adaptive, Hybrid)
- Intelligent PSO optimization for gain tuning
- High-performance vectorized simulation with Numba
- Hardware-in-the-loop (HIL) support
- Interactive Streamlit dashboard
- Comprehensive test suite with 85%+ coverage
- Complete Sphinx documentation
"""

# Project authorship details
AUTHOR = "SadeQ Soltani Sh."
AUTHOR_EMAIL = "sadeqsoltaanish@gmail.com"
URL = "https://github.com/theSadeQ/dip-smc-pso"
LICENSE = "MIT"

# Supported Python engines: pin to >=3.9 to support modern typing and <4.0 to avoid breaking updates.
PYTHON_REQUIRES = ">=3.9,<4.0"

# -----------------------------------------------------------------------------
# Dependency Management
# -----------------------------------------------------------------------------

def parse_requirements(filename: str = "requirements.txt") -> List[str]:
    """
    Parse the requirements.txt file and extract active dependency specifications.

    This function reads a requirements file line-by-line, filters out comments
    and empty lines, and returns clean strings for setuptools' install_requires.

    Args:
        filename (str): Name of the file containing dependency lists (default: requirements.txt)

    Returns:
        List[str]: Clean requirements strings ready for installation.
    """
    requirements = []
    filepath = Path(__file__).parent / filename

    if not filepath.exists():
        # Fallback if requirements file is missing (e.g. distributed build environment)
        return requirements

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Omit comment-only lines and whitespace
            if line and not line.startswith("#"):
                # Handle potential inline comments by stripping anything after a space-hash
                clean_line = re.split(r"\s+#", line)[0].strip()
                if clean_line:
                    requirements.append(clean_line)

    return requirements


def categorize_dependencies():
    """
    Classify package requirements into core and target developer extras.

    Inspects all lines parsed from requirements.txt and groups them to build
    clean, modular installation extras (dev, docs, test, and all).

    Returns:
        dict: A dictionary containing:
            - install_requires (list): Core libraries required to execute the plant and controllers.
            - dev (list): Linters, formatters, and environment management helpers.
            - docs (list): Packages needed to compile Sphinx HTML docs.
            - test (list): Packages needed to execute the pytest suite and Hypothesis tests.
    """
    all_deps = parse_requirements()

    # Core runtime dependencies (NumPy, SciPy, Matplotlib, Pydantic, etc.)
    core_deps = []

    # Code formatting, profiling, and quality checkers
    dev_deps = []

    # Sphinx builders and doc extensions
    docs_deps = []

    # Pytest core and validation engines
    test_deps = []

    # Exact lowercase matching keywords to route dependencies
    dev_patterns = ["black", "psutil", "pygments"]
    docs_patterns = [
        "sphinx",
        "myst-parser",
        "nbsphinx",
        "jupyter",
        "ipykernel",
        "ipywidgets",
        "nbconvert",
        "jupyter-cache",
        "beautifulsoup4",
        "sphinxcontrib-",
        "linkchecker",
        "sympy",
    ]
    test_patterns = ["pytest", "hypothesis"]

    for dep in all_deps:
        dep_lower = dep.lower()

        # Categorize requirements according to pattern presence
        if any(pattern in dep_lower for pattern in test_patterns):
            test_deps.append(dep)
        elif any(pattern in dep_lower for pattern in docs_patterns):
            docs_deps.append(dep)
        elif any(pattern in dep_lower for pattern in dev_patterns):
            dev_deps.append(dep)
        else:
            # Pinned constraints like numpy<2.0.0 are critical:
            # Numba is incompatible with numpy >= 2.0.0, causing JIT failures in simulations.
            core_deps.append(dep)

    return {
        "install_requires": core_deps,
        "dev": dev_deps,
        "docs": docs_deps,
        "test": test_deps,
    }


# -----------------------------------------------------------------------------
# Package Configuration
# -----------------------------------------------------------------------------

# find_packages() locates package folders containing an __init__.py.
# We point setuptools to look under the current working directory.
packages = find_packages(where=".", include=["src", "src.*"])

# package_data maps files that must be bundled with the library during installs.
# In this case, we include setup, config templates, schemas, and markdown files.
package_data = {
    "": [
        "*.yaml",
        "*.yml",
        "*.json",
        "*.md",
        "*.txt",
    ],
}

# Entry points: define console scripts that get generated in the bin/ directory
# of the python environment. Allows running CLI tasks directly from the terminal.
entry_points = {
    "console_scripts": [
        # Main simulation command line interface
        "dip-simulate=simulate:main",
        # Custom shortcut to launch Streamlit dashboard
        "dip-dashboard=streamlit_app:main",
    ],
}

# PyPI Classifiers: indicate support levels, license, and target audience.
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Education",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Physics",
    "Topic :: Scientific/Engineering :: Mathematics",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Operating System :: OS Independent",
]

# Keywords describing project domains for indexing systems
keywords = [
    "control-systems",
    "sliding-mode-control",
    "particle-swarm-optimization",
    "double-inverted-pendulum",
    "robotics",
    "nonlinear-control",
    "optimization",
    "simulation",
    "hardware-in-the-loop",
]

# -----------------------------------------------------------------------------
# Setup Execution
# -----------------------------------------------------------------------------

# Fetch dependencies dynamically grouped into targets
deps = categorize_dependencies()

# Build dictionary for extras_require parameter
extras_require = {
    "dev": deps["dev"],
    "docs": deps["docs"],
    "test": deps["test"],
    "all": deps["dev"] + deps["docs"] + deps["test"],
}

# Execute standard packaging command
setup(
    # Basic package identifiers
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/plain",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,

    # Package structure and physical discovery
    packages=packages,
    package_data=package_data,
    include_package_data=True,

    # Requirements definitions
    python_requires=PYTHON_REQUIRES,
    install_requires=deps["install_requires"],
    extras_require=extras_require,

    # Executable bindings
    entry_points=entry_points,

    # Discoverability and categorizations
    classifiers=classifiers,
    keywords=keywords,

    # zip_safe=False allows installation as a directory, not a zip file.
    # Essential for loading configuration templates, relative schemas, and dev resources.
    zip_safe=False,
)
