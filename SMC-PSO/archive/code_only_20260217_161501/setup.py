#==========================================================================================\
#====================================== setup.py ==========================================\
#==========================================================================================\

"""
Professional setup.py for Double-Inverted Pendulum SMC-PSO Project.

This setup file enables:
- Editable install: pip install -e .
- Standard install: pip install .
- Development install: pip install -e .[dev]
- Documentation build: pip install -e .[docs]
- Testing environment: pip install -e .[test]
- Complete dev environment: pip install -e .[all]

The setup.py parses requirements.txt automatically to avoid duplication.
"""

import os
import re
from pathlib import Path
from typing import List

from setuptools import find_packages, setup

# -----------------------------------------------------------------------------
# Project Metadata
# -----------------------------------------------------------------------------

NAME = "dip-smc-pso"
VERSION = "1.0.0"
DESCRIPTION = (
    "Advanced Sliding Mode Control for Double-Inverted Pendulum with PSO Optimization"
)
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

For complete documentation, visit: https://dip-smc-pso.readthedocs.io/
"""

AUTHOR = "SadeQ"
AUTHOR_EMAIL = "noreply@github.com"
URL = "https://github.com/theSadeQ/dip-smc-pso"
LICENSE = "MIT"
PYTHON_REQUIRES = ">=3.9,<4.0"

# -----------------------------------------------------------------------------
# Dependency Management
# -----------------------------------------------------------------------------


def parse_requirements(filename: str = "requirements.txt") -> List[str]:
    """
    Parse requirements.txt and extract dependency specifications.

    This function:
    - Reads requirements.txt line by line
    - Filters out comments (lines starting with #)
    - Filters out empty lines
    - Preserves version constraints (>=, <, ==)

    Args:
        filename: Path to requirements file (default: requirements.txt)

    Returns:
        List of dependency strings suitable for install_requires
    """
    requirements = []
    filepath = Path(__file__).parent / filename

    if not filepath.exists():
        return requirements

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith("#"):
                requirements.append(line)

    return requirements


def categorize_dependencies():
    """
    Categorize dependencies into install, dev, docs, and test groups.

    Returns:
        Dict with keys: install_requires, dev, docs, test
    """
    all_deps = parse_requirements()

    # Core dependencies (always installed)
    core_deps = []

    # Development tools (code quality, formatting)
    dev_deps = []

    # Documentation dependencies
    docs_deps = []

    # Testing dependencies
    test_deps = []

    # Categorization patterns
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

        # Check if it's a test dependency
        if any(pattern in dep_lower for pattern in test_patterns):
            test_deps.append(dep)
        # Check if it's a docs dependency
        elif any(pattern in dep_lower for pattern in docs_patterns):
            docs_deps.append(dep)
        # Check if it's a dev dependency
        elif any(pattern in dep_lower for pattern in dev_patterns):
            dev_deps.append(dep)
        # Otherwise it's a core dependency
        else:
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

# Find all packages under src/
packages = find_packages(where=".", include=["src", "src.*"])

# Package data (include YAML configs, JSON schemas, etc.)
package_data = {
    "": [
        "*.yaml",
        "*.yml",
        "*.json",
        "*.md",
        "*.txt",
    ],
}

# Entry points for command-line scripts
entry_points = {
    "console_scripts": [
        # Main simulation CLI
        "dip-simulate=simulate:main",
        # Streamlit dashboard (note: streamlit run is preferred, but this provides alternative)
        "dip-dashboard=streamlit_app:main",
    ],
}

# Classifiers for PyPI (if published)
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

# Keywords for discoverability
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
# Setup Configuration
# -----------------------------------------------------------------------------

# Get categorized dependencies
deps = categorize_dependencies()

# Define extras_require
extras_require = {
    "dev": deps["dev"],
    "docs": deps["docs"],
    "test": deps["test"],
    "all": deps["dev"] + deps["docs"] + deps["test"],
}

setup(
    # Project metadata
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/plain",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,

    # Package discovery
    packages=packages,
    package_data=package_data,
    include_package_data=True,

    # Dependencies
    python_requires=PYTHON_REQUIRES,
    install_requires=deps["install_requires"],
    extras_require=extras_require,

    # Entry points
    entry_points=entry_points,

    # Metadata for PyPI
    classifiers=classifiers,
    keywords=keywords,

    # Ensure zip_safe=False for editable installs
    zip_safe=False,
)
