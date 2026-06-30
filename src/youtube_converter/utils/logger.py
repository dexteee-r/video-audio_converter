"""
logger.py - Application Logging

Provides a configured logger that writes detailed logs to a rotating file
in the application directory. Logs include timestamps, levels, and context.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

# Max 2MB per file, keep 3 backups
MAX_BYTES = 2 * 1024 * 1024
BACKUP_COUNT = 3


def _log_file() -> str:
    """Resolve the log file path lazily to avoid an import cycle with config."""
    # Imported here (not at module top) because config.settings imports this
    # module; a top-level import would create a circular dependency.
    from youtube_converter.config.paths import log_dir
    return os.path.join(log_dir(), "youtube_converter.log")


def get_logger(name: str = "youtube_converter") -> logging.Logger:
    """
    Get or create a configured logger.

    Args:
        name: Logger name (module name recommended).

    Returns:
        A Logger instance writing to a rotating log file in the user data dir.
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        _log_file(), maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_fmt)
    logger.addHandler(file_handler)

    return logger
