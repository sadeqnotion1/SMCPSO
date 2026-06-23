"""
Logging Configuration Management

Handles loading and validating logging configuration from YAML files
and environment variables.

Author: DIP-SMC-PSO Project
Date: 2025-11-11
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class HandlerConfig:
    """Configuration for a log handler."""
    enabled: bool = True
    level: str = "INFO"
    format: str = "json"


@dataclass
class ConsoleHandlerConfig(HandlerConfig):
    """Configuration for console handler."""
    colorize: bool = True
    format: str = "human_readable"


@dataclass
class FileHandlerConfig(HandlerConfig):
    """Configuration for file handler."""
    directory: str = "logs"
    filename_pattern: str = "{component}_{date}.log"
    rotation_strategy: str = "daily_and_size"
    max_bytes: int = 104857600  # 100MB
    backup_count: int = 5
    retention_days: int = 30
    compress: bool = True


@dataclass
class AsyncHandlerConfig:
    """Configuration for async handler wrapper."""
    enabled: bool = True
    queue_size: int = 10000
    flush_interval_ms: int = 100
    flush_on_levels: list = field(default_factory=lambda: ["ERROR", "CRITICAL"])


@dataclass
class LoggingConfig:
    """Complete logging configuration."""
    default_level: str = "INFO"
    component_levels: Dict[str, str] = field(default_factory=dict)
    console: ConsoleHandlerConfig = field(default_factory=ConsoleHandlerConfig)
    file: FileHandlerConfig = field(default_factory=FileHandlerConfig)
    async_handler: AsyncHandlerConfig = field(default_factory=AsyncHandlerConfig)
    validate_schema: bool = True
    strict_mode: bool = False
    self_monitoring: bool = True
    monitoring_interval_seconds: int = 60


def load_config(config_path: Optional[str] = None) -> LoggingConfig:
    """
    Load logging configuration from YAML file with environment variable overrides.

    Args:
        config_path: Path to YAML config file. If None, uses default location.

    Returns:
        LoggingConfig: Loaded configuration

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    # Default config path
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"

    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # Load YAML
    with open(config_path, 'r') as f:
        raw_config = yaml.safe_load(f)

    # Apply environment variable overrides
    raw_config = _apply_env_overrides(raw_config)

    # Build configuration objects
    config = _build_config(raw_config)

    # Validate
    _validate_config(config)

    return config


def _apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to configuration."""
    # LOG_LEVEL override
    if "LOG_LEVEL" in os.environ:
        config["default_level"] = os.environ["LOG_LEVEL"]

    # LOG_DIR override
    if "LOG_DIR" in os.environ:
        if "handlers" not in config:
            config["handlers"] = {}
        if "file" not in config["handlers"]:
            config["handlers"]["file"] = {}
        config["handlers"]["file"]["directory"] = os.environ["LOG_DIR"]

    # LOG_ASYNC_ENABLED override
    if "LOG_ASYNC_ENABLED" in os.environ:
        enabled = os.environ["LOG_ASYNC_ENABLED"].lower() in ("true", "1", "yes")
        if "handlers" not in config:
            config["handlers"] = {}
        if "async" not in config["handlers"]:
            config["handlers"]["async"] = {}
        config["handlers"]["async"]["enabled"] = enabled

    # LOG_CONSOLE_ENABLED override
    if "LOG_CONSOLE_ENABLED" in os.environ:
        enabled = os.environ["LOG_CONSOLE_ENABLED"].lower() in ("true", "1", "yes")
        if "handlers" not in config:
            config["handlers"] = {}
        if "console" not in config["handlers"]:
            config["handlers"]["console"] = {}
        config["handlers"]["console"]["enabled"] = enabled

    return config


def _build_config(raw_config: Dict[str, Any]) -> LoggingConfig:
    """Build LoggingConfig from raw dictionary."""
    # Extract handler configurations
    handlers = raw_config.get("handlers", {})

    # Console handler
    console_cfg = handlers.get("console", {})
    console = ConsoleHandlerConfig(
        enabled=console_cfg.get("enabled", True),
        level=console_cfg.get("level", "INFO"),
        format=console_cfg.get("format", "human_readable"),
        colorize=console_cfg.get("colorize", True)
    )

    # File handler
    file_cfg = handlers.get("file", {})
    rotation_cfg = file_cfg.get("rotation", {})
    file_handler = FileHandlerConfig(
        enabled=file_cfg.get("enabled", True),
        level=file_cfg.get("level", "DEBUG"),
        format=file_cfg.get("format", "json"),
        directory=file_cfg.get("directory", "logs"),
        filename_pattern=file_cfg.get("filename_pattern", "{component}_{date}.log"),
        rotation_strategy=rotation_cfg.get("strategy", "daily_and_size"),
        max_bytes=rotation_cfg.get("max_bytes", 104857600),
        backup_count=rotation_cfg.get("backup_count", 5),
        retention_days=rotation_cfg.get("retention_days", 30),
        compress=rotation_cfg.get("compress", True)
    )

    # Async handler
    async_cfg = handlers.get("async", {})
    async_handler = AsyncHandlerConfig(
        enabled=async_cfg.get("enabled", True),
        queue_size=async_cfg.get("queue_size", 10000),
        flush_interval_ms=async_cfg.get("flush_interval_ms", 100),
        flush_on_levels=async_cfg.get("flush_on_levels", ["ERROR", "CRITICAL"])
    )

    # Validation settings
    validation = raw_config.get("validation", {})

    # Monitoring settings
    monitoring = raw_config.get("monitoring", {})

    # Build main config
    config = LoggingConfig(
        default_level=raw_config.get("default_level", "INFO"),
        component_levels=raw_config.get("component_levels", {}),
        console=console,
        file=file_handler,
        async_handler=async_handler,
        validate_schema=validation.get("validate_schema", True),
        strict_mode=validation.get("strict_mode", False),
        self_monitoring=monitoring.get("self_monitoring", True),
        monitoring_interval_seconds=monitoring.get("monitoring_interval_seconds", 60)
    )

    return config


def _validate_config(config: LoggingConfig) -> None:
    """
    Validate configuration.

    Args:
        config: Configuration to validate

    Raises:
        ValueError: If configuration is invalid
    """
    # Validate log levels
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    if config.default_level not in valid_levels:
        raise ValueError(f"Invalid default_level: {config.default_level}")

    for component, level in config.component_levels.items():
        if level not in valid_levels:
            raise ValueError(f"Invalid level '{level}' for component '{component}'")

    # Validate file handler
    if config.file.enabled:
        if config.file.max_bytes <= 0:
            raise ValueError("max_bytes must be positive")
        if config.file.backup_count < 0:
            raise ValueError("backup_count must be non-negative")
        if config.file.retention_days <= 0:
            raise ValueError("retention_days must be positive")

    # Validate async handler
    if config.async_handler.enabled:
        if config.async_handler.queue_size <= 0:
            raise ValueError("queue_size must be positive")
        if config.async_handler.flush_interval_ms <= 0:
            raise ValueError("flush_interval_ms must be positive")


def get_component_level(config: LoggingConfig, component: str) -> str:
    """
    Get log level for a specific component.

    Supports wildcard matching (e.g., "Controller.*" matches "Controller.ClassicalSMC").

    Args:
        config: Logging configuration
        component: Component name (e.g., "Controller.ClassicalSMC")

    Returns:
        str: Log level for component
    """
    # Exact match first
    if component in config.component_levels:
        return config.component_levels[component]

    # Wildcard matching
    for pattern, level in config.component_levels.items():
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            if component.startswith(prefix):
                return level

    # Default level
    return config.default_level


# Example usage
if __name__ == "__main__":
    config = load_config()
    print(f"Default level: {config.default_level}")
    print(f"Console enabled: {config.console.enabled}")
    print(f"File directory: {config.file.directory}")
    print(f"Async enabled: {config.async_handler.enabled}")

    # Test component level lookup
    print(f"Controller.ClassicalSMC level: {get_component_level(config, 'Controller.ClassicalSMC')}")
    print(f"Controller.AdaptiveSMC level: {get_component_level(config, 'Controller.AdaptiveSMC')}")
    print(f"Optimizer.PSO level: {get_component_level(config, 'Optimizer.PSO')}")
