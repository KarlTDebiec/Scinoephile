#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.is_simplified."""

from __future__ import annotations

import pytest

from scinoephile.lang.zho import is_simplified
from test.lang.language_id_test_cases import LANGUAGE_ID_TEST_CASES


@pytest.mark.parametrize(
    ("text", "expected"),
    [(case.text, case.is_simplified) for case in LANGUAGE_ID_TEST_CASES],
)
def test_is_simplified(text: str, expected: bool):
    """Detect simplified Chinese text.

    Arguments:
        text: text to classify
        expected: expected simplified classification
    """
    assert is_simplified(text) is expected
