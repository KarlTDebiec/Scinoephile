#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.cache.duration."""

from __future__ import annotations

from datetime import timedelta

import pytest

from scinoephile.core.cache.duration import parse_duration


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1d", timedelta(days=1)),
        ("7d", timedelta(days=7)),
        ("12h", timedelta(hours=12)),
        ("30m", timedelta(minutes=30)),
        ("90s", timedelta(seconds=90)),
        ("1w", timedelta(weeks=1)),
        ("2w", timedelta(weeks=2)),
        ("0.5d", timedelta(hours=12)),
    ],
)
def test_parse_duration_valid(value: str, expected: timedelta):
    """Test that valid duration strings are parsed correctly.

    Arguments:
        value: duration string input
        expected: expected timedelta result
    """
    assert parse_duration(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "d",
        "7",
        "7x",
        "abc",
        "1dd",
        "-1d",
    ],
)
def test_parse_duration_invalid(value: str):
    """Test that invalid duration strings raise ValueError.

    Arguments:
        value: invalid duration string
    """
    with pytest.raises(ValueError):
        parse_duration(value)
