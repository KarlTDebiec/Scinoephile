#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Chinese script analysis."""

from __future__ import annotations

from scinoephile.lang.zho.script.analysis import (
    get_zho_script_analysis,
    is_simplified,
    is_traditional,
)
from test.helpers import parametrize


@parametrize(
    ("text", "expected_script"),
    [
        ("简体中文汉字", "zho-Hans"),
        ("繁體中文漢字", "zho-Hant"),
        (
            "從前有個小朋友很滑，後來他長大。有一天，他變成一個大叔。傻里傻氣怪模怪樣。",
            "zho-Hant",
        ),
        ("中文", None),
        ("简體中文", None),
        ("English subtitles", None),
    ],
)
def test_get_zho_script_analysis(text: str, expected_script: str | None):
    """Test Chinese script analysis.

    Arguments:
        text: text to analyze
        expected_script: expected script subtag, if determined
    """
    analysis = get_zho_script_analysis(text)

    assert analysis.script == expected_script


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
        ("nei5 hou2", False),
        ("gwong2 dung1 waa2", False),
        ("简体中文", True),
        ("汉字", True),
        ("繁體中文", False),
        ("漢字", False),
        ("中文", True),
        ("", False),
    ],
)
def test_is_simplified(text: str, expected: bool):
    """Detect simplified Chinese text.

    Arguments:
        text: text to classify
        expected: expected simplified classification
    """
    assert is_simplified(text) is expected


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
        ("nei5 hou2", False),
        ("gwong2 dung1 waa2", False),
        ("简体中文", False),
        ("汉字", False),
        ("繁體中文", True),
        ("漢字", True),
        ("中文", True),
        ("", False),
    ],
)
def test_is_traditional(text: str, expected: bool):
    """Detect traditional Chinese text.

    Arguments:
        text: text to classify
        expected: expected traditional classification
    """
    assert is_traditional(text) is expected
