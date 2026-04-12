#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.conversion.is_simplified."""

from __future__ import annotations

import pytest

from scinoephile.lang.zho.conversion import is_simplified


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("简体中文", True),
        ("汉字", True),
        ("繁體中文", False),
        ("漢字", False),
        ("中文", True),
    ],
)
def test_is_simplified(text: str, expected: bool):
    """Detect simplified Chinese text.

    Arguments:
        text: Chinese text to classify
        expected: expected simplified classification
    """
    assert is_simplified(text) is expected
