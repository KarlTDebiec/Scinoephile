#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for Mandarin Chinese processing."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.mandarin import (
    get_mandarin_pinyin_series,
    get_mandarin_pinyin_text,
)
from ..data.kob import kob_input_hanzi
from ..data.t import t_input_hanzi


def _test_get_mandarin_pinyin_series(input_series: Series) -> None:
    output_series = get_mandarin_pinyin_series(input_series)
    assert len(input_series.events) == len(output_series.events)


def test_get_mandarin_pinyin_series_kob(kob_input_hanzi: Series) -> None:
    _test_get_mandarin_pinyin_series(kob_input_hanzi)


def test_get_mandarin_pinyin_series_t(t_input_hanzi: Series) -> None:
    _test_get_mandarin_pinyin_series(t_input_hanzi)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("你好世界", "nǐ hǎo shìjiè"),
    ],
)
def test_get_mandarin_pinyin_text(text: str, expected: str) -> None:
    """Test get_mandarin_pinyin"""
    assert get_mandarin_pinyin_text(text) == expected
