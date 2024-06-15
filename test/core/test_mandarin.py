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
from scinoephile.testing import get_test_file_path


@pytest.mark.parametrize(
    "relative_input_path",
    [
        "b/input/cmn-hans.srt",
        "t/input/cmn-hans.srt",
    ],
)
def test_get_mandarin_pinyin_subtitles(relative_input_path: str) -> None:
    input_path = get_test_file_path(relative_input_path)
    input_subtitles = SubtitleSeries.load(input_path)
    output_subtitles = get_mandarin_pinyin_subtitles(input_subtitles)
    assert len(input_subtitles.events) == len(output_subtitles.events)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("你好世界", "nǐ hǎo shìjiè"),
    ],
)
def test_get_mandarin_pinyin_text(text: str, expected: str) -> None:
    """Test get_mandarin_pinyin"""
    assert get_mandarin_pinyin_text(text) == expected
