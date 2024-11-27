#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for Cantonese subtitle processing."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
# noinspection PyProtectedMember
from scinoephile.core.cantonese import (
    _get_cantonese_text_romanization,
    get_cantonese_romanization,
)
from ..data.kob import kob_input_hanzi


def _test_get_cantonese_pinyin_series(input_series: Series) -> None:
    output_series = get_cantonese_romanization(input_series)
    assert len(input_series.events) == len(output_series.events)


def test_get_cantonese_pinyin_series_kob(kob_input_hanzi: Series) -> None:
    _test_get_cantonese_pinyin_series(kob_input_hanzi)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("你好世界", "néih hóu sai gaai"),
    ],
)
def test_get_cantonese_pinyin_text(text: str, expected: str) -> None:
    """Test get_cantonese_pinyin"""
    assert _get_cantonese_text_romanization(text) == expected
