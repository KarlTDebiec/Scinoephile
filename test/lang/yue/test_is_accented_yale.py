#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.yue.romanization.is_accented_yale."""

from __future__ import annotations

import pytest

from scinoephile.lang.yue.romanization import is_accented_yale


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("néih hóu", True),
        ("gwóngdūngwá", True),
        ("nei5 hou2", False),
        ("", False),
    ],
)
def test_is_accented_yale(text: str, expected: bool):
    """Detect accented Yale tokens.

    Arguments:
        text: Yale text to classify
        expected: expected accented classification
    """
    assert is_accented_yale(text) is expected
