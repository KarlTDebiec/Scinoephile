#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for hanzi processing."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.hanzi import (
    get_hanzi_series_merged_to_single_line,
    get_hanzi_series_simplified,
    get_hanzi_text_merged_to_single_line,
    get_hanzi_text_simplified,
)
from ..data.kob import kob_input_hanzi
from ..data.t import t_input_hanzi, t_output_hanzi


def _test_get_hanzi_series_merged_to_single_line(
    input_series: Series, expected_output_series: Series
) -> None:
    output_series = get_hanzi_series_merged_to_single_line(input_series)
    assert len(input_series.events) == len(output_series.events)

    errors = []
    for i, (output_subtitle, expected_output_subtitle) in enumerate(
        zip(output_series.events, expected_output_series.events), 1
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


def test_get_hanzi_series_merged_to_single_line_t(
    t_input_hanzi: Series,
    t_output_hanzi: Series,
) -> None:
    _test_get_hanzi_series_merged_to_single_line(t_input_hanzi, t_output_hanzi)


def _test_get_hanzi_series_simplified(input_series: Series) -> None:
    output_series = get_hanzi_series_simplified(input_series)
    assert len(input_series.events) == len(output_series.events)


def test_get_hanzi_series_simplified_kob(kob_input_hanzi: Series) -> None:
    _test_get_hanzi_series_simplified(kob_input_hanzi)


def test_get_hanzi_series_simplified_t(t_input_hanzi: Series) -> None:
    _test_get_hanzi_series_simplified(t_input_hanzi)


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
