#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for English processing."""
from __future__ import annotations

import pytest

from scinoephile.core import get_english_single_line_text, get_english_truecase


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("HELLO WORLD", "Hello World"),
    ],
)
def test_get_english_truecase(text: str, expected: str) -> None:
    """Test get_english_truecase"""
    assert get_english_truecase(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("line 1\nline 2", "line 1 line 2"),
    ],
)
def test_get_english_single_line_text(text: str, expected: str) -> None:
    """Test get_english_single_line_text"""
    assert get_english_single_line_text(text) == expected
