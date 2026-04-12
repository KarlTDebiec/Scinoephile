#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.conversion.is_traditional."""

from __future__ import annotations

import pytest

from scinoephile.lang.zho.conversion import is_traditional


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("简体中文", False),
        ("汉字", False),
        ("繁體中文", True),
        ("漢字", True),
        ("中文", True),
    ],
)
def test_is_traditional(text: str, expected: bool):
    """Detect traditional Chinese text.

    Arguments:
        text: Chinese text to classify
        expected: expected traditional classification
    """
    assert is_traditional(text) is expected
