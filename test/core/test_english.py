#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for English processing."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.english import (
    get_english_series_merged_to_single_line,
    get_english_text_merged_to_single_line,
)
from ..data.kob import kob_input_english, kob_output_english
from ..data.t import t_input_english, t_output_english


def _test_get_english_series_merged_to_single_line(
    input_series: Series,
    expected_output_series: Series,
) -> None:
    output_series = get_english_series_merged_to_single_line(input_series)

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


def test_get_english_series_merged_to_single_line_kob(
    kob_input_english: Series,
    kob_output_english: Series,
) -> None:
    _test_get_english_series_merged_to_single_line(
        kob_input_english, kob_output_english
    )


def test_get_english_series_merged_to_single_line_t(
    t_input_english: Series,
    t_output_english: Series,
) -> None:
    _test_get_english_series_merged_to_single_line(t_input_english, t_output_english)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("line 1\nline 2", "line 1 line 2"),
    ],
)
def test_get_english_text_merged_to_single_line(text: str, expected: str) -> None:
    """Test get_english_single_line_text"""
    assert get_english_text_merged_to_single_line(text) == expected
