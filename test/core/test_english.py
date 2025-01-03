#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.english."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.english import (
    _get_english_text_cleaned,  # noqa
    _get_english_text_flattened,  # noqa
    get_english_cleaned,
    get_english_flattened,
)
from ..data.kob import kob_en_hk, kob_en_hk_clean, kob_en_hk_flatten
from ..data.mnt import mnt_en_us, mnt_en_us_clean, mnt_en_us_flatten
from ..data.pdp import pdp_en_hk, pdp_en_hk_clean, pdp_en_hk_flatten
from ..data.t import t_en_hk, t_en_hk_clean, t_en_hk_flatten


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


def _test_get_english_flattened(series: Series, expected: Series):
    output = get_english_flattened(series)

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


# get_english_cleaned
def test_get_english_cleaned_kob(kob_en_hk: Series, kob_en_hk_clean: Series):
    _test_get_english_cleaned(kob_en_hk, kob_en_hk_clean)


def test_get_english_cleaned_mnt(mnt_en_us: Series, mnt_en_us_clean: Series):
    _test_get_english_cleaned(mnt_en_us, mnt_en_us_clean)


def test_get_english_cleaned_pdp(pdp_en_hk: Series, pdp_en_hk_clean: Series):
    _test_get_english_cleaned(pdp_en_hk, pdp_en_hk_clean)


def test_get_english_cleaned_t(t_en_hk: Series, t_en_hk_clean: Series):
    _test_get_english_cleaned(t_en_hk, t_en_hk_clean)


# get_english_flattened
def test_get_english_flattened_kob(kob_en_hk: Series, kob_en_hk_flatten: Series):
    _test_get_english_flattened(kob_en_hk, kob_en_hk_flatten)


def test_get_english_flattened_mnt(mnt_en_us: Series, mnt_en_us_flatten: Series):
    _test_get_english_flattened(mnt_en_us, mnt_en_us_flatten)


def test_get_english_flattened_pdp(pdp_en_hk: Series, pdp_en_hk_flatten: Series):
    _test_get_english_flattened(pdp_en_hk, pdp_en_hk_flatten)


def test_get_english_flattened_t(t_en_hk: Series, t_en_hk_flatten: Series):
    _test_get_english_flattened(t_en_hk, t_en_hk_flatten)


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
def test_get_english_text_flattened(text: str, expected: str):
    assert _get_english_text_flattened(text) == expected
