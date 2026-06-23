#==========================================================================================\\
#============================== src/utils/logging/paths.py ===============================\\
#==========================================================================================\\

"""
Centralized log path configuration for the DIP-SMC-PSO project.

This module provides a single source of truth for all log directory paths used
throughout the project. It supports environment variable overrides for flexible
deployment scenarios.

Environment Variables:
    LOG_DIR: Override default log directory (default: ".logs")

Usage:
    from src.utils.infrastructure.logging.paths import LOG_DIR, PSO_LOG_DIR, TEST_LOG_DIR

    log_file = PSO_LOG_DIR / f"pso_{controller}.log"
    test_log = TEST_LOG_DIR / "test_validation.log"

Migration Notes:
    - Dec 17, 2025: Centralized all log paths to eliminate hardcoded references
    - Old hardcoded paths like "logs/" have been replaced with this module
    - All logging code should import from this module, not hardcode paths
"""

from pathlib import Path
import os

# Base log directory (can be overridden via environment variable)
# Updated for academic/ reorganization (Dec 2025)
LOG_DIR = Path(os.getenv("LOG_DIR", "academic/logs"))

# Subdirectories for different log types
PSO_LOG_DIR = LOG_DIR / "pso"
TEST_LOG_DIR = LOG_DIR / "test"
MONITORING_LOG_DIR = LOG_DIR / "monitoring"
ARCHIVE_DIR = LOG_DIR / "archive"

# Ensure directories exist when module is imported
for directory in [LOG_DIR, PSO_LOG_DIR, TEST_LOG_DIR, MONITORING_LOG_DIR, ARCHIVE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

__all__ = [
    "LOG_DIR",
    "PSO_LOG_DIR",
    "TEST_LOG_DIR",
    "MONITORING_LOG_DIR",
    "ARCHIVE_DIR",
]
