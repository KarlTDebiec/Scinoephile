#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of English text cleaning."""

from __future__ import annotations

from scinoephile.lang.eng.cleaning import get_eng_text_cleaned
from test.helpers import parametrize


@parametrize(
    ("text", "expected"),
    [
        ("hello\\N-\\Nworld", "hello\\Nworld"),
        (
            '<font face="Monospace">{\\an7}WOODY:\xa0Look out!</font>',
            "WOODY: Look out!",
        ),
        ("hello\x00world", "hello world"),
        (
            "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ "
            "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ "
            "０１２３４５６７８９",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789",
        ),
        ("ΟΚ, οκ.", "OK, ok."),
    ],
)
def test_get_eng_text_cleaned(text: str, expected: str):
    """Test English text cleaning.

    Arguments:
        text: text to clean
        expected: expected cleaned text
    """
    assert get_eng_text_cleaned(text) == expected
