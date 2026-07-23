#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Mandarin text romanization."""

from __future__ import annotations

from scinoephile.lang.cmn.romanization import get_cmn_text_romanized
from test.helpers import parametrize


@parametrize(
    ("text", "expected"),
    [
        ("你好世界", "nǐhǎo shìjiè"),
        ("你好,世界!", "nǐhǎo, shìjiè!"),
        ("「你好」世界？", "｢nǐhǎo｣ shìjiè?"),
        ("＂你好＂世界", '"nǐhǎo" shìjiè'),
        ("＇你好＇世界", "'nǐhǎo' shìjiè"),
        ("他说＇你好＇", "tā shuō 'nǐhǎo'"),
        ("你好：世界；再见。", "nǐhǎo: shìjiè; zàijiàn｡"),
        ("don't你好", "don't nǐhǎo"),
        ("rock'n'roll你好", "rock'n'roll nǐhǎo"),
        ('"t i"你好', '"t i" nǐhǎo'),
        ("你好 world 吗", "nǐhǎo world ma"),
        ("你好 where ？", "nǐhǎo where ?"),
        ("你好　世界", "nǐhǎo  shìjiè"),
    ],
)
def test_get_cmn_text_romanized(text: str, expected: str):
    """Test get_cmn_text_romanized.

    Arguments:
        text: Text to romanize
        expected: Expected romanization
    """
    assert get_cmn_text_romanized(text) == expected
