#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.conversion.is_traditional."""

from __future__ import annotations

import pytest

from scinoephile.lang.zho.conversion import is_traditional
from test.lang.detection_cases import DETECTION_CASES


@pytest.mark.parametrize(
    ("text", "expected"),
    [(case.text, case.is_traditional) for case in DETECTION_CASES],
)
def test_is_traditional(text: str, expected: bool):
    """Detect traditional Chinese text.

    Arguments:
        text: Chinese text to classify
        expected: expected traditional classification
    """
    assert is_traditional(text) is expected
