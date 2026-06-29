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
from test.lang.test_language_id import LANGUAGE_ID_TEST_CASES


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
    [(case.text, case.is_simplified) for case in LANGUAGE_ID_TEST_CASES],
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
    [(case.text, case.is_traditional) for case in LANGUAGE_ID_TEST_CASES],
)
def test_is_traditional(text: str, expected: bool):
    """Detect traditional Chinese text.

    Arguments:
        text: text to classify
        expected: expected traditional classification
    """
    assert is_traditional(text) is expected
