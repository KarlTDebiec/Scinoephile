#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.yue.is_numbered_jyutping."""

from __future__ import annotations

from scinoephile.lang.yue.romanization import is_numbered_jyutping
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
        ("néih hóu", False),
        ("gwóngdūngwá", False),
        ("nei5 hou2", True),
        ("gwong2 dung1 waa2", True),
        ("简体中文", False),
        ("汉字", False),
        ("繁體中文", False),
        ("漢字", False),
        ("中文", False),
        ("", False),
    ],
)
def test_is_numbered_jyutping(text: str, expected: bool):
    """Detect numbered Jyutping tokens.

    Arguments:
        text: Jyutping text to classify
        expected: expected numbered classification
    """
    assert is_numbered_jyutping(text) is expected
