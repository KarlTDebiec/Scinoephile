#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.cmn.romanization.is_numbered_pinyin."""

from __future__ import annotations

import pytest

from scinoephile.lang.cmn.romanization import is_numbered_pinyin
from test.lang.cmn.pinyin_detection_cases import PINYIN_CASES


@pytest.mark.parametrize(("text", "_", "expected"), PINYIN_CASES)
def test_is_numbered_pinyin(text: str, _: bool, expected: bool):
    """Detect numbered pinyin tokens.

    Arguments:
        text: pinyin text to classify
        _: expected accented classification (unused)
        expected: expected numbered classification
    """
    assert is_numbered_pinyin(text) is expected
