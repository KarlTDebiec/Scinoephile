#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.yue.is_accented_yale."""

from __future__ import annotations

import pytest

from scinoephile.lang.yue.romanization import is_accented_yale
from test.lang.language_id_test_cases import LANGUAGE_ID_TEST_CASES


@pytest.mark.parametrize(
    ("text", "expected"),
    [(case.text, case.is_accented_yale) for case in LANGUAGE_ID_TEST_CASES],
)
def test_is_accented_yale(text: str, expected: bool):
    """Detect accented Yale tokens.

    Arguments:
        text: text to classify
        expected: expected accented classification
    """
    assert is_accented_yale(text) is expected
