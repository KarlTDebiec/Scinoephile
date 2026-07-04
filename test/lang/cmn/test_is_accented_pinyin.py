#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.cmn.is_accented_pinyin."""

from __future__ import annotations

from scinoephile.lang.cmn.romanization import is_accented_pinyin
from test.helpers import parametrize
from test.lang.id.test_language_id import LANGUAGE_ID_TEST_CASES


@parametrize(
    ("text", "expected"),
    [(case.text, case.is_accented_pinyin) for case in LANGUAGE_ID_TEST_CASES],
)
def test_is_accented_pinyin(text: str, expected: bool):
    """Detect accented pinyin tokens.

    Arguments:
        text: text to classify
        expected: expected accented classification
    """
    assert is_accented_pinyin(text) is expected
