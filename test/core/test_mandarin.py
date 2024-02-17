#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for Mandarin Chinese processing."""
from __future__ import annotations

import pytest

from scinoephile.core import get_mandarin_pinyin


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("你好世界", "nǐ hǎo shìjiè"),
    ],
)
def test_get_mandarin_pinyin(text: str, expected: str) -> None:
    """Test get_mandarin_pinyin"""
    assert get_mandarin_pinyin(text) == expected
