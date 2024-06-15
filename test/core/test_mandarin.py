#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for Mandarin Chinese processing."""
from __future__ import annotations

import pytest

from scinoephile.core import (
    SubtitleSeries,
    get_mandarin_pinyin_subtitles,
    get_mandarin_pinyin_text,
)
from ..fixtures import (
    kob_input_hanzi,
    t_input_hanzi,
)


def _test_get_mandarin_pinyin_subtitles(input_subtitles: SubtitleSeries) -> None:
    output_subtitles = get_mandarin_pinyin_subtitles(input_subtitles)
    assert len(input_subtitles.events) == len(output_subtitles.events)


def test_get_mandarin_pinyin_subtitles_kob(kob_input_hanzi: SubtitleSeries) -> None:
    _test_get_mandarin_pinyin_subtitles(kob_input_hanzi)


def test_get_mandarin_pinyin_subtitles_t(t_input_hanzi: SubtitleSeries) -> None:
    _test_get_mandarin_pinyin_subtitles(t_input_hanzi)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("你好世界", "nǐ hǎo shìjiè"),
    ],
)
def test_get_mandarin_pinyin_text(text: str, expected: str) -> None:
    """Test get_mandarin_pinyin"""
    assert get_mandarin_pinyin_text(text) == expected
