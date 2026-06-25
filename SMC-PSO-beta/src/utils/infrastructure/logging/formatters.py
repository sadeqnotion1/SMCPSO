"""
Log Formatters

Provides formatters for different log output formats (JSON, human-readable, etc.).

Author: DIP-SMC-PSO Project
Date: 2025-11-11
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional


class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs structured JSON logs.

    Each log entry is a single JSON object following the schema defined
    in schema.json.
    """

    def __init__(
        self,
        include_hostname: bool = True,
        include_pid: bool = True,
        include_thread_id: bool = True,
        pretty_print: bool = False
    ):
        """
        Initialize JSON formatter.

        Args:
            include_hostname: Include hostname in metadata
            include_pid: Include process ID in metadata
            include_thread_id: Include thread ID in metadata
            pretty_print: Pretty-print JSON (for debugging)
        """
        super().__init__()
        self.include_hostname = include_hostname
        self.include_pid = include_pid
        self.include_thread_id = include_thread_id
        self.pretty_print = pretty_print

        # Cache hostname and PID
        if include_hostname:
            import socket
            self.hostname = socket.gethostname()
        if include_pid:
            import os
            self.pid = os.getpid()

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record

        Returns:
            str: JSON-formatted log entry
        """
        # Base log entry
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "component": record.name,
            "event": getattr(record, "event", "log_message"),
        }

        # Add data if present
        if hasattr(record, "data"):
            log_entry["data"] = record.data

        # Add duration if present
        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = record.duration_ms

        # Build metadata
        metadata: Dict[str, Any] = {}

        if hasattr(record, "run_id"):
            metadata["run_id"] = record.run_id
        if hasattr(record, "iteration"):
            metadata["iteration"] = record.iteration

        if self.include_thread_id:
            metadata["thread_id"] = record.threadName

        if self.include_hostname:
            metadata["hostname"] = self.hostname

        if self.include_pid:
            metadata["pid"] = self.pid

        # Add custom metadata
        if hasattr(record, "metadata"):
            metadata.update(record.metadata)

        log_entry["metadata"] = metadata

        # Add error information if present
        if record.exc_info:
            log_entry["error"] = {
                "error_type": record.exc_info[0].__name__ if record.exc_info[0] else "Unknown",
                "error_message": str(record.exc_info[1]) if record.exc_info[1] else "",
                "traceback": self.formatException(record.exc_info).split("\n") if record.exc_info else []
            }

            # Add custom error context if present
            if hasattr(record, "error_context"):
                log_entry["error"]["context"] = record.error_context

        # Serialize to JSON
        if self.pretty_print:
            return json.dumps(log_entry, indent=2, default=str)
        else:
            return json.dumps(log_entry, default=str)


class HumanReadableFormatter(logging.Formatter):
    """
    Formatter that outputs human-readable console logs.

    Format: [timestamp] [level] [component] event: data_summary (duration_ms)
    """

    def __init__(
        self,
        timestamp_format: str = "%Y-%m-%d %H:%M:%S.%f",
        max_data_length: int = 100,
        colorize: bool = True
    ):
        """
        Initialize human-readable formatter.

        Args:
            timestamp_format: strftime format string
            max_data_length: Maximum length for data summary
            colorize: Colorize output for terminals
        """
        super().__init__()
        self.timestamp_format = timestamp_format
        self.max_data_length = max_data_length
        self.colorize = colorize

        # ANSI color codes (if colorize enabled)
        if colorize:
            self.colors = {
                "DEBUG": "\033[36m",      # Cyan
                "INFO": "\033[32m",       # Green
                "WARNING": "\033[33m",    # Yellow
                "ERROR": "\033[31m",      # Red
                "CRITICAL": "\033[35m",   # Magenta
                "RESET": "\033[0m"        # Reset
            }
        else:
            self.colors = {level: "" for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "RESET"]}

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as human-readable string.

        Args:
            record: Log record

        Returns:
            str: Human-readable log entry
        """
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime(self.timestamp_format)[:-3]  # Trim to ms

        # Colorize level
        level_color = self.colors.get(record.levelname, self.colors["RESET"])
        level = f"{level_color}{record.levelname}{self.colors['RESET']}"

        # Component name
        component = record.name

        # Event name
        event = getattr(record, "event", "log_message")

        # Data summary
        data_summary = ""
        if hasattr(record, "data"):
            data_str = self._summarize_data(record.data)
            if data_str:
                data_summary = f": {data_str}"

        # Duration
        duration_str = ""
        if hasattr(record, "duration_ms"):
            duration_str = f" ({record.duration_ms:.2f}ms)"

        # Build final message
        message = f"[{timestamp}] [{level}] [{component}] {event}{data_summary}{duration_str}"

        return message

    def _summarize_data(self, data: Any) -> str:
        """
        Create a summary of data for human-readable output.

        Args:
            data: Data to summarize

        Returns:
            str: Data summary
        """
        if isinstance(data, dict):
            # Show key=value pairs
            items = []
            for key, value in data.items():
                if isinstance(value, (int, float, str, bool)):
                    items.append(f"{key}={value}")
                elif isinstance(value, list):
                    items.append(f"{key}=[{len(value)} items]")
                else:
                    items.append(f"{key}=<{type(value).__name__}>")

            summary = " ".join(items)
        elif isinstance(data, (list, tuple)):
            summary = f"[{len(data)} items]"
        else:
            summary = str(data)

        # Truncate if too long
        if len(summary) > self.max_data_length:
            summary = summary[:self.max_data_length - 3] + "..."

        return summary


class MetricFormatter(logging.Formatter):
    """
    Formatter optimized for performance metrics.

    Outputs tab-separated values for easy parsing.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as TSV.

        Args:
            record: Log record

        Returns:
            str: TSV-formatted log entry
        """
        fields = [
            datetime.utcfromtimestamp(record.created).isoformat(),
            record.name,
            getattr(record, "event", ""),
            str(getattr(record, "duration_ms", "")),
            str(getattr(record, "iteration", "")),
        ]

        return "\t".join(fields)


# Example usage
if __name__ == "__main__":
    # Test JSON formatter
    json_formatter = JSONFormatter(pretty_print=True)

    record = logging.LogRecord(
        name="Controller.ClassicalSMC",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="",
        args=(),
        exc_info=None
    )
    record.event = "control_computed"
    record.data = {
        "state_norm": 0.025,
        "control_signal": 15.3,
        "error": [0.01, 0.02, 0.005]
    }
    record.duration_ms = 1.23
    record.run_id = "abc123"
    record.iteration = 100

    print("JSON Format:")
    print(json_formatter.format(record))
    print()

    # Test human-readable formatter
    hr_formatter = HumanReadableFormatter(colorize=False)
    print("Human-Readable Format:")
    print(hr_formatter.format(record))
