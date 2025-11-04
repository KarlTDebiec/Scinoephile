#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.english.test_get_english_flattened"""

from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.english import (
    _get_english_text_cleaned,  # noqa
    _get_english_text_flattened,  # noqa
    get_english_flattened,
)


def _test_get_english_flattened(series: Series, expected: Series):
    """Test get_english_flattened.

    Arguments:
        series: Series with which to test
        expected: Expected output series
    """
    output = get_english_flattened(series)

    assert len(series) == len(output)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event.text.count("\n") != 0:
            errors.append(f"Subtitle {i} contains newline")
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")


def test_get_english_flattened_kob(kob_eng: Series, kob_eng_flatten: Series):
    """Test get_english_flattened with KOB English subtitles.

    Arguments:
        kob_eng: KOB English series fixture
        kob_eng_flatten: Expected flattened KOB English series fixture
    """
    _test_get_english_flattened(kob_eng, kob_eng_flatten)


def test_get_english_flattened_mlamd(mlamd_eng: Series, mlamd_eng_flatten: Series):
    """Test get_english_flattened with MLAMD English subtitles.

    Arguments:
        mlamd_eng: MLAMD English series fixture
        mlamd_eng_flatten: Expected flattened MLAMD English series fixture
    """
    _test_get_english_flattened(mlamd_eng, mlamd_eng_flatten)


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
