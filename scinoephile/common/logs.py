#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Logging utilities."""

from __future__ import annotations

from logging import DEBUG, ERROR, INFO, WARNING, Formatter, StreamHandler, getLogger

DEFAULT_LOG_FORMAT = "%(levelname)s: %(name)s: %(message)s"
"""Default format for log messages."""

__all__ = [
    "DEFAULT_LOG_FORMAT",
    "configure_logging",
    "set_logging_verbosity",
]


def configure_logging(verbosity: int = 1, log_format: str | None = None):
    """Configure logging with appropriate verbosity level and format.

    Arguments:
        verbosity: level of verbosity (0=ERROR, 1=WARNING, 2=INFO, 3+=DEBUG)
        log_format: format string for log messages; if None, uses DEFAULT_LOG_FORMAT
    """
    if log_format is None:
        log_format = DEFAULT_LOG_FORMAT

    # Determine log level based on verbosity
    match verbosity:
        case 0:
            level = ERROR
        case 1:
            level = WARNING
        case 2:
            level = INFO
        case _:
            level = DEBUG

    # Get root logger and configure it
    root_logger = getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Add console handler with formatter
    console_handler = StreamHandler()
    console_handler.setLevel(level)
    formatter = Formatter(log_format)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


def set_logging_verbosity(verbosity: int):
    """Set the level of verbosity of logging.

    Deprecated: Use configure_logging() instead for better control.

    Arguments:
        verbosity: level of verbosity (0=ERROR, 1=WARNING, 2=INFO, 3+=DEBUG)
    """
    configure_logging(verbosity)
