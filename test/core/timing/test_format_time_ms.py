#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of time formatting helpers."""

from __future__ import annotations

from scinoephile.core.timing import format_time_ms


def test_format_time_ms():
    """Test millisecond timestamp formatting."""
    assert format_time_ms(62_500) == "00:01:02"
    assert format_time_ms(3_725_250) == "01:02:05"
