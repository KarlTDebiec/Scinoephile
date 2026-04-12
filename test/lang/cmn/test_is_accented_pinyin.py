#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.cmn.romanization.is_accented_pinyin."""

from __future__ import annotations

import pytest

from scinoephile.lang.cmn.romanization import is_accented_pinyin


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("nǐ hǎo", True),
        ("lüè", True),
        ("ni3 hao3", False),
        ("ni hao", False),
        ("", False),
    ],
)
def test_is_accented_pinyin(text: str, expected: bool):
    """Detect accented pinyin tokens.

    Arguments:
        text: pinyin text to classify
        expected: expected accented classification
    """
    assert is_accented_pinyin(text) is expected
