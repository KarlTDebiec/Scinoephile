#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.language_id."""

from __future__ import annotations

import pytest

from scinoephile.lang.language_id import LanguageId

LANGUAGE_ID_TEST_CASES: list[LanguageId] = [
    LanguageId(
        text="nǐ hǎo",
        is_accented_pinyin=True,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    LanguageId(
        text="lüè",
        is_accented_pinyin=True,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    LanguageId(
        text="ni3 hao3",
        is_accented_pinyin=False,
        is_numbered_pinyin=True,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    LanguageId(
        text="lu:e4",
        is_accented_pinyin=False,
        is_numbered_pinyin=True,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    LanguageId(
        text="lv4",
        is_accented_pinyin=False,
        is_numbered_pinyin=True,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    LanguageId(
        text="ni hao",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    LanguageId(
        text="néih hóu",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=True,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    LanguageId(
        text="gwóngdūngwá",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=True,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
    LanguageId(
        text="nei5 hou2",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=True,
        is_simplified=False,
        is_traditional=False,
    ),
    LanguageId(
        text="gwong2 dung1 waa2",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=True,
        is_simplified=False,
        is_traditional=False,
    ),
    LanguageId(
        text="简体中文",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=True,
        is_traditional=False,
    ),
    LanguageId(
        text="汉字",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=True,
        is_traditional=False,
    ),
    LanguageId(
        text="繁體中文",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=True,
    ),
    LanguageId(
        text="漢字",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=True,
    ),
    LanguageId(
        text="中文",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=True,
        is_traditional=True,
    ),
    LanguageId(
        text="",
        is_accented_pinyin=False,
        is_numbered_pinyin=False,
        is_accented_yale=False,
        is_numbered_jyutping=False,
        is_simplified=False,
        is_traditional=False,
    ),
]


@pytest.mark.parametrize("case", LANGUAGE_ID_TEST_CASES)
def test_language_id_from_text(case: LanguageId):
    """Detect language ID features from text.

    Arguments:
        case: expected language ID result
    """
    result = LanguageId.from_text(case.text)

    assert result.is_accented_pinyin is case.is_accented_pinyin
    assert result.is_numbered_pinyin is case.is_numbered_pinyin
    assert result.is_accented_yale is case.is_accented_yale
    assert result.is_numbered_jyutping is case.is_numbered_jyutping
    assert result.is_simplified is case.is_simplified
    assert result.is_traditional is case.is_traditional
