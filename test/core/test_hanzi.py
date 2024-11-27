#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for hanzi processing."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
# noinspection PyProtectedMember
from scinoephile.core.hanzi import (
    _get_hanzi_text_merged,
    _get_hanzi_text_simplified,
    get_hanzi_merged,
    get_hanzi_simplified,
)
from ..data.kob import kob_yue_hant_hk, kob_yue_hant_hk_simplify
from ..data.t import t_input_hanzi, t_output_hanzi


def _test_get_hanzi_merged(series: Series, expected: Series):
    output = get_hanzi_merged(series)
    assert len(series.events) == len(output.events)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output.events, expected.events), 1):
        if event.text.count("\n") != 0:
            errors.append(f"Subtitle {i} contains newline")
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")


def _test_get_hanzi_simplified(series: Series, expected: Series = None):
    output = get_hanzi_simplified(series)
    assert len(series.events) == len(output.events)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output.events, expected.events), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")


def test_get_hanzi_merged_t(t_input_hanzi: Series, t_output_hanzi: Series):
    _test_get_hanzi_merged(t_input_hanzi, t_output_hanzi)


def test_get_hanzi_simplified_kob(
    kob_yue_hant_hk: Series, kob_yue_hant_hk_simplify: Series
):
    _test_get_hanzi_simplified(kob_yue_hant_hk, kob_yue_hant_hk_simplify)


def test_get_hanzi_simplified_t(t_input_hanzi: Series):
    _test_get_hanzi_simplified(t_input_hanzi)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("你好世界", "你好世界"),
    ],
)
def test_get_hanzi_text_simplified(text: str, expected: str):
    assert _get_hanzi_text_simplified(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("line 1\nline 2", "line 1　line 2"),
    ],
)
def test_get_hanzi_text_merged(text: str, expected: str):
    assert _get_hanzi_text_merged(text) == expected
