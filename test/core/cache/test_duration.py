#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of cache duration parsing."""

from __future__ import annotations

from datetime import timedelta

import pytest

from scinoephile.core.cache.duration import parse_duration


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("30s", timedelta(seconds=30)),
        ("5m", timedelta(minutes=5)),
        ("12h", timedelta(hours=12)),
        ("7d", timedelta(days=7)),
        ("2 weeks", timedelta(weeks=2)),
    ],
)
def test_parse_duration(value: str, expected: timedelta):
    """Test parsing supported duration strings.

    Arguments:
        value: duration string
        expected: expected timedelta
    """
    assert parse_duration(value) == expected


def test_parse_duration_invalid():
    """Test that invalid durations fail clearly."""
    with pytest.raises(ValueError, match="Invalid duration"):
        parse_duration("yesterday")
