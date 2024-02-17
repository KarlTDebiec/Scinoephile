#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for hanzi processing."""
from __future__ import annotations

import pytest

from scinoephile.core import get_hanzi_simplified, get_hanzi_single_line_text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("你好世界", "你好世界"),
    ],
)
def test_get_hanzi_simplified(text: str, expected: str) -> None:
    """Test get_hanzi_simplified"""
    assert get_hanzi_simplified(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("line 1\nline 2", "line 1　line 2"),
    ],
)
def test_get_hanzi_single_line_text(text: str, expected: str) -> None:
    """Test get_hanzi_single_line_text"""
    assert get_hanzi_single_line_text(text) == expected
