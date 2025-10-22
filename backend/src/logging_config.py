"""Logging configuration with rotating file handler

Implements rotating file handler that creates 3 log files of 3MB each,
rotating based on file size (not time).
"""

import logging
import logging.handlers
import os
from pathlib import Path


def setup_logging(log_dir: str = "logs", log_file: str = "app.log") -> logging.Logger:
    """
    Setup logging with rotating file handler

    Args:
        log_dir: Directory to store log files
        log_file: Name of the log file

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create rotating file handler (3MB * 3 files = 9MB total)
    # When log file reaches 3MB, it rotates to next file (backup count = 3)
    log_path = os.path.join(log_dir, log_file)
    rotating_handler = logging.handlers.RotatingFileHandler(
        filename=log_path,
        maxBytes=3 * 1024 * 1024,  # 3MB
        backupCount=3,  # Keep 3 backup files (total 4 files including main)
        encoding='utf-8'
    )
    rotating_handler.setLevel(logging.DEBUG)

    # Create console handler for important messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatter with detailed information
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    rotating_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(rotating_handler)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module"""
    return logging.getLogger(name)
