#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.cmn.romanization.is_numbered_pinyin."""

from __future__ import annotations

import pytest

from scinoephile.lang.cmn.romanization import is_numbered_pinyin


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("ni3 hao3", True),
        ("lu:e4", True),
        ("lv4", True),
        ("nǐ hǎo", False),
        ("ni hao", False),
        ("", False),
    ],
)
def test_is_numbered_pinyin(text: str, expected: bool):
    """Detect numbered pinyin tokens.

    Arguments:
        text: pinyin text to classify
        expected: expected numbered classification
    """
    assert is_numbered_pinyin(text) is expected
