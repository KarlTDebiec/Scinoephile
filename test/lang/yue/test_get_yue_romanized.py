#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of written Cantonese text romanization."""

from __future__ import annotations

from scinoephile.lang.yue.romanization import (
    get_yue_char_romanized,
    get_yue_text_romanized,
)
from test.helpers import parametrize


@parametrize(
    ("text", "expected"),
    [
        ("广东话", "gwóngdūngwá"),
        ("你好世界", "néih hóu saigaai"),
        ("你好,世界!", "néih hóu, saigaai!"),
        ("「你好」世界？", "｢néih hóu｣ saigaai?"),
        ("＂你好＂世界", '"néih hóu" saigaai'),
        ("＇你好＇世界", "'néih hóu' saigaai"),
        ("佢话＇你好＇", "kéuih wah 'néih hóu'"),
        ("你好：世界；再见。", "néih hóu: saigaai; joigin｡"),
        ("don't你好", "don't néih hóu"),
        ("rock'n'roll你好", "rock'n'roll néih hóu"),
        ('"t i"你好', '"t i" néih hóu'),
        ("你好　世界", "néih hóu  saigaai"),
        (
            "乱讲，啫啫一 fling fling 吖嘛",
            "lyuhn góng, jē jē yāt fling fling ā ma",
        ),
        (
            "骑呢怪，做咩搞到咁乌 where ？",
            "kèh nē gwaai, jouh mē gáau dou gam wū where ?",
        ),
        ("原来少爷", "yùhnlòih siuyèh"),
        ("龙飞凤舞，苏察哈尔灿", "lùhngfēifuhngmóuh, sōuchaathāyíhchaan"),
    ],
)
def test_get_yue_text_romanized(text: str, expected: str):
    """Test get_yue_text_romanized.

    Arguments:
        text: Text to romanize
        expected: Expected romanization
    """
    assert get_yue_text_romanized(text) == expected


@parametrize(
    ("text", "expected"),
    [
        ("你", "néih"),
        ("，", ""),
        ("？", ""),
    ],
)
def test_get_yue_char_romanized(text: str, expected: str):
    """Test get_yue_char_romanized.

    Arguments:
        text: Text to romanize
        expected: Expected romanization
    """
    assert get_yue_char_romanized(text) == expected
