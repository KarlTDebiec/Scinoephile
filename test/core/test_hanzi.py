#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for hanzi processing."""
from __future__ import annotations

import pytest

from scinoephile.core import (
    SubtitleSeries,
    get_hanzi_subtitles_merged_to_single_line,
    get_hanzi_subtitles_simplified,
    get_hanzi_text_merged_to_single_line,
    get_hanzi_text_simplified,
)
from scinoephile.testing import get_test_file_path


@pytest.mark.parametrize(
    ("relative_input_path", "relative_output_path"),
    [
        ("t/input/cmn-hans.srt", "t/output/cmn-hans.srt"),
    ],
)
def test_get_hanzi_subtitles_merged_to_single_line(
    relative_input_path: str, relative_output_path: str
) -> None:
    input_path = get_test_file_path(relative_input_path)
    input_subtitles = SubtitleSeries.load(input_path)
    output_subtitles = get_hanzi_subtitles_merged_to_single_line(input_subtitles)

    assert len(input_subtitles.events) == len(output_subtitles.events)

    expected_output_path = get_test_file_path(relative_output_path)
    expected_output_subtitles = SubtitleSeries.load(expected_output_path)

    for output_subtitle, expected_output_subtitle in zip(
        output_subtitles.events, expected_output_subtitles.events
    ):
        assert output_subtitle.text.count("\n") == 0
        assert output_subtitle == expected_output_subtitle


@pytest.mark.parametrize(
    ("relative_input_path"),
    [
        ("b/input/yue-hant.srt"),
        ("t/input/cmn-hant.srt"),
    ],
)
def test_get_hanzi_subtitles_simplified(relative_input_path: str) -> None:
    input_path = get_test_file_path(relative_input_path)
    input_subtitles = SubtitleSeries.load(input_path)
    output_subtitles = get_hanzi_subtitles_simplified(input_subtitles)
    assert len(input_subtitles.events) == len(output_subtitles.events)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("你好世界", "你好世界"),
    ],
)
def test_get_hanzi_text_simplified(text: str, expected: str) -> None:
    """Test get_hanzi_simplified"""
    assert get_hanzi_text_simplified(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("line 1\nline 2", "line 1　line 2"),
    ],
)
def test_get_hanzi_text_merged_to_single_line(text: str, expected: str) -> None:
    """Test get_hanzi_single_line_text"""
    assert get_hanzi_text_merged_to_single_line(text) == expected
