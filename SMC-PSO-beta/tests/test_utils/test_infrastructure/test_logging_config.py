"""Tests for src.utils.infrastructure.logging.config.

Covers YAML loading, missing-file handling, environment overrides, component
level resolution (exact + wildcard), and validation errors.
"""

import textwrap

import pytest

from src.utils.infrastructure.logging.config import (
    load_config,
    get_component_level,
    LoggingConfig,
)


MINIMAL_YAML = textwrap.dedent(
    """
    default_level: INFO
    component_levels:
      Controller.*: DEBUG
      Optimizer.PSO: WARNING
    handlers:
      console:
        enabled: true
        level: INFO
      file:
        enabled: false
      async:
        enabled: false
    """
).strip()


def _write(tmp_path, text):
    path = tmp_path / "config.yaml"
    path.write_text(text)
    return str(path)


def test_load_config_from_yaml(tmp_path):
    cfg = load_config(_write(tmp_path, MINIMAL_YAML))
    assert isinstance(cfg, LoggingConfig)
    assert cfg.default_level == "INFO"
    assert cfg.console.enabled is True
    assert cfg.file.enabled is False
    assert cfg.async_handler.enabled is False
    assert cfg.component_levels["Optimizer.PSO"] == "WARNING"


def test_load_config_missing_file_raises(tmp_path):
    missing = str(tmp_path / "does_not_exist.yaml")
    with pytest.raises(FileNotFoundError):
        load_config(missing)


def test_env_override_log_level(tmp_path, monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    cfg = load_config(_write(tmp_path, MINIMAL_YAML))
    assert cfg.default_level == "DEBUG"


def test_env_override_console_disabled(tmp_path, monkeypatch):
    monkeypatch.setenv("LOG_CONSOLE_ENABLED", "false")
    cfg = load_config(_write(tmp_path, MINIMAL_YAML))
    assert cfg.console.enabled is False


def test_get_component_level_exact_match(tmp_path):
    cfg = load_config(_write(tmp_path, MINIMAL_YAML))
    assert get_component_level(cfg, "Optimizer.PSO") == "WARNING"


def test_get_component_level_wildcard_match(tmp_path):
    cfg = load_config(_write(tmp_path, MINIMAL_YAML))
    assert get_component_level(cfg, "Controller.ClassicalSMC") == "DEBUG"


def test_get_component_level_falls_back_to_default(tmp_path):
    cfg = load_config(_write(tmp_path, MINIMAL_YAML))
    assert get_component_level(cfg, "Simulation.Runner") == "INFO"


def test_validate_rejects_bad_default_level(tmp_path):
    bad = MINIMAL_YAML.replace("default_level: INFO", "default_level: BOGUS")
    with pytest.raises(ValueError):
        load_config(_write(tmp_path, bad))


def test_load_default_sibling_config_yaml():
    # No path -> resolves sibling config.yaml shipped with the package.
    cfg = load_config()
    assert cfg.default_level == "INFO"
    assert get_component_level(cfg, "Controller.ClassicalSMC") == "INFO"
