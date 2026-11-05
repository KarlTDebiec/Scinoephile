#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.logs."""

from __future__ import annotations

from logging import DEBUG, ERROR, INFO, WARNING, getLogger

from common.logs import configure_logging
from pytest import mark


@mark.parametrize(
    ("verbosity", "expected_level"),
    [(0, ERROR), (1, WARNING), (2, INFO), (3, DEBUG), (10, DEBUG)],
)
def test_configure_logging(verbosity: int, expected_level: int):
    """Test logging level for verbosity values.

    Arguments:
        verbosity: verbosity value
        expected_level: expected logging level
    """
    root_logger = getLogger()
    handlers, level = root_logger.handlers[:], root_logger.level
    try:
        configure_logging(verbosity)
        assert root_logger.level == expected_level
    finally:
        for handler in root_logger.handlers:
            if handler not in handlers:
                handler.close()
        root_logger.handlers[:] = handlers
        root_logger.setLevel(level)
