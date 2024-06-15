#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for English processing."""
from __future__ import annotations

import pytest

from scinoephile.core import (
    SubtitleSeries,
    get_english_subtitles_merged_to_single_line,
    get_english_text_merged_to_single_line,
    get_english_text_truecased,
)
from scinoephile.testing import get_test_file_path


@pytest.mark.parametrize(
    ("relative_input_path", "relative_output_path"),
    [
        ("kob/input/en-hk.srt", "kob/output/en-hk.srt"),
        ("t/input/en-hk.srt", "t/output/en-hk.srt"),
    ],
)
def test_get_english_subtitles_merged_to_single_line(
    relative_input_path: str, relative_output_path: str
) -> None:
    input_path = get_test_file_path(relative_input_path)
    input_subtitles = SubtitleSeries.load(input_path)
    output_subtitles = get_english_subtitles_merged_to_single_line(input_subtitles)

    assert len(input_subtitles.events) == len(output_subtitles.events)

    expected_output_path = get_test_file_path(relative_output_path)
    expected_output_subtitles = SubtitleSeries.load(expected_output_path)

    errors = []
    for i, (output_subtitle, expected_output_subtitle) in enumerate(
        zip(output_subtitles.events, expected_output_subtitles.events), 1
    ):
        if output_subtitle.text.count("\n") != 0:
            errors.append(f"Subtitle {i} contains newline")
        if output_subtitle != expected_output_subtitle:
            errors.append(
                f"Subtitle {i} does not match: "
                f"{output_subtitle} != {expected_output_subtitle}"
            )

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("HELLO WORLD", "Hello World"),
    ],
)
def test_get_english_text_truecased(text: str, expected: str) -> None:
    """Test get_english_truecase"""
    assert get_english_text_truecased(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("line 1\nline 2", "line 1 line 2"),
    ],
)
def test_get_english_text_merged_to_single_line(text: str, expected: str) -> None:
    """Test get_english_single_line_text"""
    assert get_english_text_merged_to_single_line(text) == expected
