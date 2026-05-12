#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Chinese script analysis."""

from __future__ import annotations

import pytest

from scinoephile.lang.zho.script.analysis import get_zho_script_analysis


@pytest.mark.parametrize(
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
