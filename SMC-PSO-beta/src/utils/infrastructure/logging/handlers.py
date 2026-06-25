"""
Log Handlers

Provides various log handlers (file, console, async, etc.).

Author: DIP-SMC-PSO Project
Date: 2025-11-11
"""

import os
import gzip
import shutil
import logging
import threading
from queue import Queue, Empty
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class DailyRotatingFileHandler(TimedRotatingFileHandler):
    """
    File handler that rotates daily and includes date in filename.

    Files are named: {component}_YYYY-MM-DD.log
    """

    def __init__(
        self,
        base_directory: str,
        component: str,
        backup_count: int = 30,
        encoding: str = "utf-8",
        compress: bool = True
    ):
        """
        Initialize daily rotating file handler.

        Args:
            base_directory: Base directory for log files
            component: Component name for filename
            backup_count: Number of backup files to keep
            encoding: File encoding
            compress: Compress old log files
        """
        self.base_directory = Path(base_directory)
        self.component = component
        self.compress_logs = compress

        # Create directory if it doesn't exist
        self.base_directory.mkdir(parents=True, exist_ok=True)

        # Build filename with current date
        today = datetime.now().strftime("%Y-%m-%d")
        filename = self.base_directory / f"{component}_{today}.log"

        # Initialize parent
        super().__init__(
            filename=str(filename),
            when="midnight",
            interval=1,
            backupCount=backup_count,
            encoding=encoding
        )

    def doRollover(self):
        """Perform rollover and optionally compress old log."""
        # Close current file
        if self.stream:
            self.stream.close()
            self.stream = None

        # Get current and new filenames
        current_time = self.rolloverAt - self.interval
        time_tuple = datetime.fromtimestamp(current_time).timetuple()
        dfn = self.rotation_filename(self.baseFilename + "." + datetime.fromtimestamp(current_time).strftime("%Y-%m-%d"))

        # Rename current file
        if os.path.exists(self.baseFilename):
            if os.path.exists(dfn):
                os.remove(dfn)
            os.rename(self.baseFilename, dfn)

            # Compress if enabled
            if self.compress_logs:
                self._compress_file(dfn)

        # Update rollover time
        currentTime = int(datetime.now().timestamp())
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval

        self.rolloverAt = newRolloverAt

        # Delete old backups
        self.deleteOldBackups()

        # Open new file
        self.stream = self._open()

    def _compress_file(self, filename: str):
        """Compress log file with gzip."""
        try:
            with open(filename, 'rb') as f_in:
                with gzip.open(f"{filename}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            # Remove uncompressed file
            os.remove(filename)
        except Exception as e:
            # Log compression error (but don't fail)
            print(f"[ERROR] Failed to compress {filename}: {e}")

    def deleteOldBackups(self):
        """Delete old backup files beyond retention period."""
        if self.backupCount <= 0:
            return

        # Find all log files for this component
        pattern = f"{self.component}_*.log*"
        log_files = sorted(self.base_directory.glob(pattern), reverse=True)

        # Keep only backupCount files
        for old_file in log_files[self.backupCount:]:
            try:
                old_file.unlink()
            except Exception:
                pass  # Ignore errors


class SizeRotatingFileHandler(RotatingFileHandler):
    """
    File handler that rotates based on size.

    Files are named: {component}.log, {component}.log.1, {component}.log.2, etc.
    """

    def __init__(
        self,
        base_directory: str,
        component: str,
        max_bytes: int = 104857600,  # 100MB
        backup_count: int = 5,
        encoding: str = "utf-8",
        compress: bool = True
    ):
        """
        Initialize size-based rotating file handler.

        Args:
            base_directory: Base directory for log files
            component: Component name for filename
            max_bytes: Maximum file size before rotation
            backup_count: Number of backup files to keep
            encoding: File encoding
            compress: Compress old log files
        """
        self.base_directory = Path(base_directory)
        self.compress_logs = compress

        # Create directory
        self.base_directory.mkdir(parents=True, exist_ok=True)

        # Build filename
        filename = self.base_directory / f"{component}.log"

        # Initialize parent
        super().__init__(
            filename=str(filename),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding=encoding
        )

    def doRollover(self):
        """Perform rollover and optionally compress old log."""
        # Standard rotation
        super().doRollover()

        # Compress oldest backup if enabled
        if self.compress_logs and self.backupCount > 0:
            oldest_backup = f"{self.baseFilename}.{self.backupCount}"
            if os.path.exists(oldest_backup):
                self._compress_file(oldest_backup)

    def _compress_file(self, filename: str):
        """Compress log file with gzip."""
        try:
            with open(filename, 'rb') as f_in:
                with gzip.open(f"{filename}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(filename)
        except Exception:
            pass  # Ignore compression errors


class AsyncHandler(logging.Handler):
    """
    Async wrapper for log handlers.

    Queues log records and writes them in a background thread,
    ensuring logging doesn't block the main control loop.
    """

    def __init__(
        self,
        base_handler: logging.Handler,
        queue_size: int = 10000,
        flush_interval_ms: int = 100,
        flush_on_levels: Optional[list] = None
    ):
        """
        Initialize async handler.

        Args:
            base_handler: Underlying handler to write to
            queue_size: Maximum queue size
            flush_interval_ms: Periodic flush interval
            flush_on_levels: Log levels that trigger immediate flush
        """
        super().__init__()
        self.base_handler = base_handler
        self.queue = Queue(maxsize=queue_size)
        self.flush_on_levels = flush_on_levels or ["ERROR", "CRITICAL"]

        # Start background thread
        self.running = True
        self.thread = threading.Thread(target=self._background_writer, daemon=True)
        self.thread.start()

    def emit(self, record: logging.LogRecord):
        """
        Queue log record for background writing.

        Args:
            record: Log record to queue
        """
        try:
            self.queue.put_nowait(record)

            # Immediate flush for critical levels
            if record.levelname in self.flush_on_levels:
                self._flush_queue()
        except Exception:
            self.handleError(record)

    def _background_writer(self):
        """Background thread that writes queued logs."""
        while self.running:
            try:
                # Get record with timeout
                record = self.queue.get(timeout=0.1)

                # Write to base handler
                self.base_handler.emit(record)

                # Mark task done
                self.queue.task_done()
            except Empty:
                # No records to write
                continue
            except Exception:
                # Ignore errors in background thread
                continue

    def _flush_queue(self):
        """Flush all queued records immediately."""
        while not self.queue.empty():
            try:
                record = self.queue.get_nowait()
                self.base_handler.emit(record)
                self.queue.task_done()
            except Empty:
                break
            except Exception:
                continue

    def flush(self):
        """Flush handler."""
        self._flush_queue()
        self.base_handler.flush()

    def close(self):
        """Close handler and background thread."""
        # Stop background thread
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)

        # Flush remaining records
        self.flush()

        # Close base handler
        self.base_handler.close()

        super().close()


class CombinedRotatingFileHandler(logging.Handler):
    """
    File handler that rotates both daily AND based on size.

    Combines daily rotation with size limits.
    """

    def __init__(
        self,
        base_directory: str,
        component: str,
        max_bytes: int = 104857600,  # 100MB
        backup_count: int = 5,
        retention_days: int = 30,
        encoding: str = "utf-8",
        compress: bool = True
    ):
        """
        Initialize combined rotating file handler.

        Args:
            base_directory: Base directory for log files
            component: Component name for filename
            max_bytes: Maximum file size before rotation
            backup_count: Number of backup files per day
            retention_days: Days to retain logs
            encoding: File encoding
            compress: Compress old log files
        """
        super().__init__()

        self.base_directory = Path(base_directory)
        self.component = component
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.retention_days = retention_days
        self.compress_logs = compress
        self.encoding = encoding

        # Create directory
        self.base_directory.mkdir(parents=True, exist_ok=True)

        # Current file info
        self.current_date = datetime.now().date()
        self.current_size = 0
        self.rotation_count = 0

        # Open initial file
        self._open_file()

    def _open_file(self):
        """Open current log file."""
        # Build filename
        today_str = self.current_date.strftime("%Y-%m-%d")
        if self.rotation_count == 0:
            filename = self.base_directory / f"{self.component}_{today_str}.log"
        else:
            filename = self.base_directory / f"{self.component}_{today_str}.log.{self.rotation_count}"

        self.stream = open(filename, 'a', encoding=self.encoding)
        self.current_filename = filename

        # Get current file size
        self.current_size = self.stream.tell()

    def emit(self, record: logging.LogRecord):
        """
        Emit log record with rotation checks.

        Args:
            record: Log record to emit
        """
        try:
            # Check for date change
            now_date = datetime.now().date()
            if now_date != self.current_date:
                self._rotate_date()

            # Format message
            msg = self.format(record)
            msg_size = len(msg.encode(self.encoding))

            # Check for size limit
            if self.current_size + msg_size > self.max_bytes:
                self._rotate_size()

            # Write message
            self.stream.write(msg + "\n")
            self.current_size += msg_size + 1

            # Flush for critical levels
            if record.levelname in ["ERROR", "CRITICAL"]:
                self.stream.flush()
        except Exception:
            self.handleError(record)

    def _rotate_date(self):
        """Rotate to new date."""
        # Close current file
        self.stream.close()

        # Compress yesterday's logs if enabled
        if self.compress_logs:
            self._compress_yesterday()

        # Delete old logs
        self._delete_old_logs()

        # Update date and reset counters
        self.current_date = datetime.now().date()
        self.rotation_count = 0
        self.current_size = 0

        # Open new file
        self._open_file()

    def _rotate_size(self):
        """Rotate due to size limit."""
        # Close current file
        self.stream.close()

        # Increment rotation count
        self.rotation_count += 1

        # Delete if exceeds backup count
        if self.rotation_count > self.backup_count:
            # Keep only backup_count files for today
            # (This is a simplification - could be more sophisticated)
            pass

        # Reset size
        self.current_size = 0

        # Open new file
        self._open_file()

    def _compress_yesterday(self):
        """Compress log files from yesterday."""
        yesterday = self.current_date - timedelta(days=1)
        yesterday_str = yesterday.strftime("%Y-%m-%d")
        pattern = f"{self.component}_{yesterday_str}.log*"

        for log_file in self.base_directory.glob(pattern):
            if not log_file.name.endswith(".gz"):
                try:
                    with open(log_file, 'rb') as f_in:
                        with gzip.open(f"{log_file}.gz", 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    log_file.unlink()
                except Exception:
                    pass

    def _delete_old_logs(self):
        """Delete logs older than retention period."""
        cutoff_date = self.current_date - timedelta(days=self.retention_days)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")

        pattern = f"{self.component}_*.log*"
        for log_file in self.base_directory.glob(pattern):
            # Extract date from filename
            try:
                date_str = log_file.name.split("_")[1][:10]  # Extract YYYY-MM-DD
                if date_str < cutoff_str:
                    log_file.unlink()
            except Exception:
                continue

    def flush(self):
        """Flush handler."""
        if hasattr(self, 'stream'):
            self.stream.flush()

    def close(self):
        """Close handler."""
        if hasattr(self, 'stream'):
            self.stream.close()
        super().close()


# Example usage
if __name__ == "__main__":
    # Test daily rotating handler
    handler = DailyRotatingFileHandler(
        base_directory="logs",
        component="test",
        backup_count=7,
        compress=True
    )

    logger = logging.getLogger("Test")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    logger.info("Test log message")
    print("Log written to logs/test_YYYY-MM-DD.log")
