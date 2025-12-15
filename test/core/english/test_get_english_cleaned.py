#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.eng.get_eng_cleaned."""

from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.eng import (
    _get_english_text_cleaned,  # noqa
    get_eng_cleaned,
)


def _test_get_english_cleaned(series: Series, expected: Series):
    """Test get_english_cleaned.

    Arguments:
        series: Series with which to test
        expected: Expected output series
    """
    output = get_eng_cleaned(series)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")


def test_get_english_cleaned_kob(kob_eng: Series, kob_eng_clean: Series):
    """Test get_english_cleaned with KOB English subtitles.

    Arguments:
        kob_eng: KOB English series fixture
        kob_eng_clean: Expected cleaned KOB English series fixture
    """
    _test_get_english_cleaned(kob_eng, kob_eng_clean)


def test_get_english_cleaned_mlamd(
    mlamd_eng_fuse_proofread: Series, mlamd_eng_fuse_proofread_clean: Series
):
    """Test get_english_cleaned with MLAMD English subtitles.

    Arguments:
        mlamd_eng_fuse_proofread: MLAMD English series fixture
        mlamd_eng_fuse_proofread_clean: Expected cleaned MLAMD English series fixture
    """
    _test_get_english_cleaned(mlamd_eng_fuse_proofread, mlamd_eng_fuse_proofread_clean)


def test_get_english_cleaned_mnt(
    mnt_eng_fuse_proofread: Series, mnt_eng_fuse_proofread_clean: Series
):
    """Test get_english_cleaned with MNT English subtitles.

    Arguments:
        mnt_eng_fuse_proofread: MNT English series fixture
        mnt_eng_fuse_proofread_clean: Expected cleaned MNT English series fixture
    """
    _test_get_english_cleaned(mnt_eng_fuse_proofread, mnt_eng_fuse_proofread_clean)


def test_get_english_cleaned_t(t_eng: Series, t_eng_clean: Series):
    """Test get_english_cleaned with T English subtitles.

    Arguments:
        t_eng: T English series fixture
        t_eng_clean: Expected cleaned T English series fixture
    """
    _test_get_english_cleaned(t_eng, t_eng_clean)


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
