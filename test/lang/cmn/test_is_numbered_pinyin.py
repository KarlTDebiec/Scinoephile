#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.cmn.is_numbered_pinyin."""

from __future__ import annotations

from scinoephile.lang.cmn.romanization import is_numbered_pinyin
from test.helpers import parametrize


@parametrize(
    ("text", "expected"),
    [
        ("nǐ hǎo", False),
        ("lüè", False),
        ("ni3 hao3", True),
        ("lu:e4", True),
        ("lv4", True),
        ("ni hao", False),
        ("néih hóu", False),
        ("gwóngdūngwá", False),
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
def test_is_numbered_pinyin(text: str, expected: bool):
    """Detect numbered pinyin tokens.

    Arguments:
        text: text to classify
        expected: expected numbered classification
    """
    assert is_numbered_pinyin(text) is expected
