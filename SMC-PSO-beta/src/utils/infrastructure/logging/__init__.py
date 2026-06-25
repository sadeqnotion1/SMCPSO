"""
Structured Logging Module for DIP-SMC-PSO

Provides comprehensive structured logging with:
- JSON-based machine-parseable logs
- Hierarchical component organization
- Async non-blocking I/O
- Daily + size-based rotation
- Performance tracking
- Context injection

Quick Start:
    from src.utils.infrastructure.logging import StructuredLogger

    logger = StructuredLogger("Controller.ClassicalSMC")
    logger.log_event("initialized", gains=[10.0, 5.0, 8.0])

Author: DIP-SMC-PSO Project
Date: 2025-11-11
"""

from .structured_logger import StructuredLogger
from .config import load_config, LoggingConfig, get_component_level
from .formatters import JSONFormatter, HumanReadableFormatter, MetricFormatter
from .handlers import (
    DailyRotatingFileHandler,
    SizeRotatingFileHandler,
    AsyncHandler,
    CombinedRotatingFileHandler
)

__all__ = [
    # Main API
    "StructuredLogger",

    # Configuration
    "load_config",
    "LoggingConfig",
    "get_component_level",

    # Formatters
    "JSONFormatter",
    "HumanReadableFormatter",
    "MetricFormatter",

    # Handlers
    "DailyRotatingFileHandler",
    "SizeRotatingFileHandler",
    "AsyncHandler",
    "CombinedRotatingFileHandler",
]

__version__ = "1.0.0"
