"""Tests for src.utils.infrastructure.logging.formatters.

Covers JSON formatting (incl. error block), human-readable summary/no-color,
and the TSV MetricFormatter.
"""

import json
import logging

from src.utils.infrastructure.logging.formatters import (
    JSONFormatter,
    HumanReadableFormatter,
    MetricFormatter,
)


def _make_record(**extra):
    record = logging.LogRecord(
        name="Controller.ClassicalSMC",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="",
        args=(),
        exc_info=None,
    )
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def test_json_formatter_parses_core_fields():
    fmt = JSONFormatter(pretty_print=False)
    record = _make_record(
        event="control_computed",
        data={"state_norm": 0.025, "control_signal": 15.3},
        duration_ms=1.23,
    )
    parsed = json.loads(fmt.format(record))
    assert parsed["level"] == "INFO"
    assert parsed["component"] == "Controller.ClassicalSMC"
    assert parsed["event"] == "control_computed"
    assert parsed["data"]["state_norm"] == 0.025
    assert parsed["duration_ms"] == 1.23
    assert parsed["timestamp"].endswith("Z")
    assert "metadata" in parsed


def test_json_formatter_default_event_when_missing():
    fmt = JSONFormatter()
    parsed = json.loads(fmt.format(_make_record()))
    assert parsed["event"] == "log_message"


def test_json_formatter_includes_error_block():
    fmt = JSONFormatter()
    try:
        raise ValueError("boom")
    except ValueError as exc:
        record = logging.LogRecord(
            name="Controller",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="",
            args=(),
            exc_info=(type(exc), exc, exc.__traceback__),
        )
        record.event = "exception_occurred"
        record.error_context = {"phase": "unit-test"}
    parsed = json.loads(fmt.format(record))
    assert parsed["error"]["error_type"] == "ValueError"
    assert parsed["error"]["error_message"] == "boom"
    assert parsed["error"]["context"] == {"phase": "unit-test"}
    assert isinstance(parsed["error"]["traceback"], list)


def test_human_readable_no_color_contains_event_and_summary():
    fmt = HumanReadableFormatter(colorize=False)
    record = _make_record(
        event="initialized",
        data={"gains": [1.0, 2.0, 3.0], "boundary_layer": 0.1},
        duration_ms=2.5,
    )
    out = fmt.format(record)
    assert "\033[" not in out  # no ANSI color codes
    assert "initialized" in out
    assert "Controller.ClassicalSMC" in out
    assert "boundary_layer=0.1" in out
    assert "gains=[3 items]" in out
    assert "(2.50ms)" in out


def test_human_readable_truncates_long_summary():
    fmt = HumanReadableFormatter(colorize=False, max_data_length=20)
    record = _make_record(event="e", data={"k": "x" * 100})
    out = fmt.format(record)
    assert "..." in out


def test_metric_formatter_is_tab_separated():
    fmt = MetricFormatter()
    record = _make_record(event="control_perf", duration_ms=1.5, iteration=42)
    out = fmt.format(record)
    fields = out.split("\t")
    assert len(fields) == 5
    assert fields[1] == "Controller.ClassicalSMC"
    assert fields[2] == "control_perf"
    assert fields[3] == "1.5"
    assert fields[4] == "42"
