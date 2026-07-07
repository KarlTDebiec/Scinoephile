#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.yue.is_accented_yale."""

from __future__ import annotations

from scinoephile.lang.yue.romanization import is_accented_yale
from test.helpers import parametrize


@parametrize(
    ("text", "expected"),
    [
        ("nǐ hǎo", False),
        ("lüè", False),
        ("ni3 hao3", False),
        ("lu:e4", False),
        ("lv4", False),
        ("ni hao", False),
        ("néih hóu", True),
        ("gwóngdūngwá", True),
        ("nei5 hou2", False),
        ("gwong2 dung1 waa2", False),
        ("简体中文", False),
        ("汉字", False),
        ("繁體中文", False),
        ("漢字", False),
        ("中文", False),
        ("", False),
    ],
)
def test_is_accented_yale(text: str, expected: bool):
    """Detect accented Yale tokens.

    Arguments:
        text: text to classify
        expected: expected accented classification
    """
    assert is_accented_yale(text) is expected
