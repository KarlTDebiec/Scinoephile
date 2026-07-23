#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Chinese text cleaning."""

from __future__ import annotations

from scinoephile.lang.zho.cleaning import get_zho_text_cleaned
from test.helpers import parametrize


@parametrize(
    ("text", "expected"),
    [
        ('<font face="Monospace">{\\an7}中文\xa0測試</font>', "中文 測試"),
        ("ΟΚ\x00中文", "OK 中文"),
        (
            "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ "
            "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ "
            "０１２３４５６７８９",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789",
        ),
        ("｢你好､世界｡｣周·星馳･劉德華", "「你好、世界。」周・星馳・劉德華"),
    ],
)
def test_get_zho_text_cleaned(text: str, expected: str):
    """Test Chinese text cleaning.

    Arguments:
        text: text to clean
        expected: expected cleaned text
    """
    assert get_zho_text_cleaned(text) == expected
