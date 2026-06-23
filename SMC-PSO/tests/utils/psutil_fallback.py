#======================================================================================\\\
#============================== tests/psutil_fallback.py ==============================\\\
#======================================================================================\\\

"""
Fallback for psutil when not available.
Provides minimal interface to prevent test failures.
"""

import os


class ProcessInfo:
    """Fallback process memory info."""
    def __init__(self, rss: int = 50 * 1024 * 1024, vms: int = 100 * 1024 * 1024):
        self.rss = rss  # 50MB default
        self.vms = vms  # 100MB default


class Process:
    """Fallback process class."""

    def __init__(self, pid: int = None):
        self.pid = pid or os.getpid()

    def memory_info(self) -> ProcessInfo:
        """Return fallback memory info."""
        return ProcessInfo()

    def cpu_percent(self, interval: float = None) -> float:
        """Return fallback CPU percentage."""
        return 0.1  # Minimal CPU usage


def virtual_memory():
    """Fallback virtual memory info."""
    class VirtualMemory:
        def __init__(self):
            self.total = 8 * 1024 * 1024 * 1024  # 8GB
            self.available = 4 * 1024 * 1024 * 1024  # 4GB
            self.percent = 50.0

    return VirtualMemory()


def cpu_percent(interval: float = None) -> float:
    """Fallback CPU percentage."""
    return 1.0