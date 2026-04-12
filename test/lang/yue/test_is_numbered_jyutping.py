#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.yue.romanization.is_numbered_jyutping."""

from __future__ import annotations

import pytest

from scinoephile.lang.yue.romanization import is_numbered_jyutping


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("nei5 hou2", True),
        ("gwong2 dung1 waa2", True),
        ("néih hóu", False),
        ("", False),
    ],
)
def test_is_numbered_jyutping(text: str, expected: bool):
    """Detect numbered Jyutping tokens.

    Arguments:
        text: Jyutping text to classify
        expected: expected numbered classification
    """
    assert is_numbered_jyutping(text) is expected
