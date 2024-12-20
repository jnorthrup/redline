import functools
import logging
import logging.handlers
import os
import time
from typing import Any, Callable, Dict


def debounce(interval: float):
    """Decorator to debounce a function call"""

    def decorator(func: Callable) -> Callable:
        last_call = {"time": 0.0}

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_time = time.time()
            if current_time - last_call["time"] >= interval:
                last_call["time"] = current_time
                return func(*args, **kwargs)

        return wrapper

    return decorator


def setup_logging(log_dir: str = "logs") -> None:
    """Set up logging with rotation and proper formatting"""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "supervisor.log")

    # Create rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=1024 * 1024, backupCount=5  # 1MB
    )

    # Create console handler
    console_handler = logging.StreamHandler()

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Set formatter for handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Set to INFO to reduce debug noise

    # Remove existing handlers
    logger.handlers = []

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


class DebouncedLogger:
    """A logger that debounces frequent messages to prevent log spam"""

    def __init__(self, interval: float = 5.0):
        self.interval = interval
        self.last_messages = {}

    def _should_log(self, msg: str) -> bool:
        """Check if enough time has passed since the last similar message"""
        current_time = time.time()
        if msg not in self.last_messages:
            self.last_messages[msg] = current_time
            return True

        if current_time - self.last_messages[msg] >= self.interval:
            self.last_messages[msg] = current_time
            return True

        return False

    def debug(self, msg: str) -> None:
        """Log debug message with debouncing"""
        if self._should_log(msg):
            logging.debug(msg)

    def info(self, msg: str) -> None:
        """Log info message (not debounced)"""
        logging.info(msg)

    def warning(self, msg: str) -> None:
        """Log warning message (not debounced)"""
        logging.warning(msg)

    def error(self, msg: str) -> None:
        """Log error message (not debounced)"""
        logging.error(msg)

    def critical(self, msg: str) -> None:
        """Log critical message (not debounced)"""
        logging.critical(msg)


def format_bytes(bytes: int) -> str:
    """Format bytes into a human-readable string (e.g., KB, MB, GB)"""
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024**2:
        return f"{bytes / 1024:.2f} KB"
    elif bytes < 1024**3:
        return f"{bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{bytes / (1024 ** 3):.2f} GB"
