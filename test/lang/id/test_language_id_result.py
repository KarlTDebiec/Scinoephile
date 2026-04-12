#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.id.LanguageIDResult."""

from __future__ import annotations

import pytest

from scinoephile.lang.id import LanguageIDResult
from test.lang.language_id_test_cases import LANGUAGE_ID_TEST_CASES


@pytest.mark.parametrize("case", LANGUAGE_ID_TEST_CASES)
def test_language_id_result_from_text(case: LanguageIDResult):
    """Detect language ID features from text.

    Arguments:
        case: expected language ID result
    """
    result = LanguageIDResult(case.text)

    assert result.is_accented_pinyin is case.is_accented_pinyin
    assert result.is_numbered_pinyin is case.is_numbered_pinyin
    assert result.is_accented_yale is case.is_accented_yale
    assert result.is_numbered_jyutping is case.is_numbered_jyutping
    assert result.is_simplified is case.is_simplified
    assert result.is_traditional is case.is_traditional
