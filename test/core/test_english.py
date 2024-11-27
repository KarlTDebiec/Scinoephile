#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for English processing."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.english import (
    _get_english_text_cleaned,  # noqa
    _get_english_text_merged,  # noqa
    get_english_cleaned,
    get_english_merged,
)
from ..data.kob import (
    kob_en_hk,
    kob_en_hk_clean,
    kob_en_hk_clean_merge,
    kob_en_hk_merge,
)
from ..data.pdp import (
    pdp_input_en,
    pdp_output_en_clean,
    pdp_output_en_clean_merge,
    pdp_output_en_merge,
)
from ..data.t import t_input_english, t_output_english


def _test_get_english_cleaned(series: Series, expected: Series):
    output = get_english_cleaned(series)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output.events, expected.events), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")


def _test_get_english_cleaned_merged(series: Series, expected: Series):
    output = get_english_merged(get_english_cleaned(series))

    errors = []
    for i, (event, expected_event) in enumerate(zip(output.events, expected.events), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")


def _test_get_english_merged(series: Series, expected: Series):
    output = get_english_merged(series)

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


def test_get_english_cleaned_kob(kob_en_hk: Series, kob_en_hk_clean: Series):
    _test_get_english_cleaned(kob_en_hk, kob_en_hk_clean)


def test_get_english_cleaned_pdp(pdp_input_en: Series, pdp_output_en_clean: Series):
    _test_get_english_cleaned(pdp_input_en, pdp_output_en_clean)


def test_get_english_cleaned_merged_kob(
    kob_en_hk: Series, kob_en_hk_clean_merge: Series
):
    _test_get_english_cleaned_merged(kob_en_hk, kob_en_hk_clean_merge)


def test_get_english_cleaned_merged_pdp(
    pdp_input_en: Series, pdp_output_en_clean_merge: Series
):
    _test_get_english_cleaned_merged(pdp_input_en, pdp_output_en_clean_merge)


def test_get_english_merged_kob(kob_en_hk: Series, kob_en_hk_merge: Series):
    _test_get_english_merged(kob_en_hk, kob_en_hk_merge)


def test_get_english_merged_pdp(pdp_input_en: Series, pdp_output_en_merge: Series):
    _test_get_english_merged(pdp_input_en, pdp_output_en_merge)


def test_get_english_merged_t(t_input_english: Series, t_output_english: Series):
    _test_get_english_merged(t_input_english, t_output_english)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("[test]", None),
        ("[test] ", None),
        ("[test] abcd", "abcd"),
        ("[test]\nabcd", "abcd"),
        ("[test\ntest]", None),
        ("abcd [test]", "abcd"),
        ("abcd\ndefg [test]", "abcd\ndefg"),
        ("-[test] abcd\n-defg", "-abcd\n-defg"),
        ("-[test]\n-[test]", None),
        (r"-[test]\N-[test]", None),
        ("-[test] \n-[test] ", None),
        ("- [test]\n- [test]", None),
        ("-abcd \n-[test] ", "abcd"),
        ("{\\i1} abcd{\\i0}", "{\\i1}abcd{\\i0}"),
    ],
)
def test_get_english_text_cleaned(text: str, expected: str):
    assert _get_english_text_cleaned(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("line 1\nline 2", "line 1 line 2"),
    ],
)
def test_get_english_text_merged(text: str, expected: str):
    assert _get_english_text_merged(text) == expected
