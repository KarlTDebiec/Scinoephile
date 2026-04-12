#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.yue.is_numbered_jyutping."""

from __future__ import annotations

import pytest

from scinoephile.lang.yue import is_numbered_jyutping
from test.lang.language_id_test_cases import LANGUAGE_ID_TEST_CASES


@pytest.mark.parametrize(
    ("text", "expected"),
    [(case.text, case.is_numbered_jyutping) for case in LANGUAGE_ID_TEST_CASES],
)
def test_is_numbered_jyutping(text: str, expected: bool):
    """Detect numbered Jyutping tokens.

    Arguments:
        text: Jyutping text to classify
        expected: expected numbered classification
    """
    assert is_numbered_jyutping(text) is expected
