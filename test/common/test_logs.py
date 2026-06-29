#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.logs."""

from __future__ import annotations

from logging import DEBUG, ERROR, INFO, WARNING, getLogger

from scinoephile.common.logs import set_logging_verbosity
from test.helpers import parametrize


@parametrize(
    ("verbosity", "expected_level"),
    [
        (0, ERROR),
        (1, WARNING),
        (2, INFO),
        (3, DEBUG),
        (10, DEBUG),
    ],
)
def test_set_logging_verbosity(verbosity: int, expected_level: int):
    """Test logging level for verbosity values.

    Arguments:
        verbosity: verbosity value
        expected_level: expected logging level
    """
    set_logging_verbosity(verbosity)
    assert getLogger().level == expected_level
