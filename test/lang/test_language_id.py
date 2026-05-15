#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.language_id."""

from __future__ import annotations

import pytest

from scinoephile.lang.language_id import LanguageId
from test.lang.language_id_test_cases import LANGUAGE_ID_TEST_CASES


def test_language_id_initializes_from_values():
    """Initialize language ID result from explicit values."""
    result = LanguageId(
        text="中文",
        is_accented_pinyin=True,
        is_numbered_pinyin=True,
        is_accented_yale=True,
        is_numbered_jyutping=True,
        is_simplified=False,
        is_traditional=False,
    )

    assert result.text == "中文"
    assert result.is_accented_pinyin is True
    assert result.is_numbered_pinyin is True
    assert result.is_accented_yale is True
    assert result.is_numbered_jyutping is True
    assert result.is_simplified is False
    assert result.is_traditional is False


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
