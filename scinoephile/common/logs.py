#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Logging utilities."""

from __future__ import annotations

import logging
from logging import DEBUG, ERROR, INFO, WARNING, Logger

LOGGER = logging.getLogger(__name__)


def initialize_logging(*, level: int | None = None) -> Logger:
    """Initialize logging once per interpreter session.

    Arguments:
        level: Explicit logging level to configure; defaults to WARNING when omitted.

    Returns:
        Configured root logger.
    """
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        logging.basicConfig()

    resolved_level = level if level is not None else WARNING
    root_logger.setLevel(resolved_level)
    LOGGER.debug(
        "Logging initialized with level %s", logging.getLevelName(root_logger.level)
    )
    return root_logger


def set_logging_verbosity(verbosity: int):
    """Set the level of verbosity of logging.

    Arguments:
        verbosity: level of verbosity
    """
    root_logger = initialize_logging()
    match verbosity:
        case 0:
            root_logger.setLevel(level=ERROR)
        case 1:
            root_logger.setLevel(level=WARNING)
        case 2:
            root_logger.setLevel(level=INFO)
        case _:
            root_logger.setLevel(level=DEBUG)

    LOGGER.debug("Logging verbosity set to %s", logging.getLevelName(root_logger.level))


__all__ = [
    "initialize_logging",
    "set_logging_verbosity",
]
