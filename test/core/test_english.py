#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
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


def _test_get_english_cleaned(series: Series, expected: Series):
    """Test get_english_cleaned.

    Arguments:
        series: Series with which to test
        expected: Expected output series
    """
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
    """Test get_english_flattened.

    Arguments:
        series: Series with which to test
        expected: Expected output series
    """
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
def test_get_english_cleaned_kob(kob_eng: Series, kob_eng_clean: Series):
    """Test get_english_cleaned with KOB English subtitles.

    Arguments:
        kob_eng: KOB English series fixture
        kob_eng_clean: Expected cleaned KOB English series fixture
    """
    _test_get_english_cleaned(kob_eng, kob_eng_clean)


def test_get_english_cleaned_mnt(mnt_eng: Series, mnt_eng_clean: Series):
    """Test get_english_cleaned with MNT English subtitles.

    Arguments:
        mnt_eng: MNT English series fixture
        mnt_eng_clean: Expected cleaned MNT English series fixture
    """
    _test_get_english_cleaned(mnt_eng, mnt_eng_clean)


def test_get_english_cleaned_pdp(pdp_eng: Series, pdp_eng_clean: Series):
    """Test get_english_cleaned with PDP English subtitles.

    Arguments:
        pdp_eng: PDP English series fixture
        pdp_eng_clean: Expected cleaned PDP English series fixture
    """
    _test_get_english_cleaned(pdp_eng, pdp_eng_clean)


def test_get_english_cleaned_t(t_eng: Series, t_eng_clean: Series):
    """Test get_english_cleaned with T English subtitles.

    Arguments:
        t_eng: T English series fixture
        t_eng_clean: Expected cleaned T English series fixture
    """
    _test_get_english_cleaned(t_eng, t_eng_clean)


# get_english_flattened
def test_get_english_flattened_kob(kob_eng: Series, kob_eng_flatten: Series):
    """Test get_english_flattened with KOB English subtitles.

    Arguments:
        kob_eng: KOB English series fixture
        kob_eng_flatten: Expected flattened KOB English series fixture
    """
    _test_get_english_flattened(kob_eng, kob_eng_flatten)


def test_get_english_flattened_mnt(mnt_eng: Series, mnt_eng_flatten: Series):
    """Test get_english_flattened with MNT English subtitles.

    Arguments:
        mnt_eng: MNT English series fixture
        mnt_eng_flatten: Expected flattened MNT English series fixture
    """
    _test_get_english_flattened(mnt_eng, mnt_eng_flatten)


def test_get_english_flattened_pdp(pdp_eng: Series, pdp_eng_flatten: Series):
    """Test get_english_flattened with PDP English subtitles.

    Arguments:
        pdp_eng: PDP English series fixture
        pdp_eng_flatten: Expected flattened PDP English series fixture
    """
    _test_get_english_flattened(pdp_eng, pdp_eng_flatten)


def test_get_english_flattened_t(t_eng: Series, t_eng_flatten: Series):
    """Test get_english_flattened with T English subtitles.

    Arguments:
        t_eng: T English series fixture
        t_eng_flatten: Expected flattened T English series fixture
    """
    _test_get_english_flattened(t_eng, t_eng_flatten)


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
    """Test _get_english_text_cleaned.

    Arguments:
        text: Text to clean
        expected: Expected cleaned text
    """
    assert _get_english_text_cleaned(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("line 1\nline 2", "line 1 line 2"),
    ],
)
def test_get_english_text_flattened(text: str, expected: str):
    """Test _get_english_text_flattened.

    Arguments:
        text: Text to flatten
        expected: Expected flattened text
    """
    assert _get_english_text_flattened(text) == expected
