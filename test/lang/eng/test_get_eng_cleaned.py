#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.eng.get_eng_cleaned."""

from __future__ import annotations

from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.eng.cleaning import _get_english_text_cleaned, get_eng_cleaned
from test.helpers import assert_series_equal

# noinspection PyProtectedMember


def _test_get_eng_cleaned(series: Series, expected: Series):
    """Test get_eng_cleaned.

    Arguments:
        series: Series with which to test
        expected: Expected output series
    """
    output = get_eng_cleaned(series, remove_empty=False)
    assert_series_equal(output, expected)


def test_get_english_text_cleaned_removes_ass_dash_only_line():
    """Test ASS multiline dash-only line removal."""
    assert _get_english_text_cleaned("hello\\N-\\Nworld") == "hello\\Nworld"


def test_get_eng_cleaned_kob(
    kob_eng_ocr_fuse: Series,
    kob_eng_ocr_fuse_clean: Series,
):
    """Test get_eng_cleaned with KOB English subtitles.

    Arguments:
        kob_eng_ocr_fuse: KOB English series fixture
        kob_eng_ocr_fuse_clean: Expected cleaned KOB English series fixture
    """
    _test_get_eng_cleaned(kob_eng_ocr_fuse, kob_eng_ocr_fuse_clean)


def test_get_eng_cleaned_invalidates_cached_blocks():
    """Test get_eng_cleaned invalidates cached blocks when events are removed."""
    series = Series(events=[Subtitle(start=0, end=1000, text="-")])
    assert [[event.text for event in block.events] for block in series.blocks] == [
        ["-"]
    ]

    output = get_eng_cleaned(series)

    assert output.events == []
    assert output.blocks == []


def test_get_eng_cleaned_mlamd(
    mlamd_eng_fuse: Series,
    mlamd_eng_fuse_clean: Series,
):
    """Test get_eng_cleaned with MLAMD English subtitles.

    Arguments:
        mlamd_eng_fuse: MLAMD English series fixture
        mlamd_eng_fuse_clean: Expected cleaned MLAMD English series fixture
    """
    _test_get_eng_cleaned(mlamd_eng_fuse, mlamd_eng_fuse_clean)


def test_get_eng_cleaned_mnt(
    mnt_eng_fuse: Series,
    mnt_eng_fuse_clean: Series,
):
    """Test get_eng_cleaned with MNT English subtitles.

    Arguments:
        mnt_eng_fuse: MNT English series fixture
        mnt_eng_fuse_clean: Expected cleaned MNT English series fixture
    """
    _test_get_eng_cleaned(mnt_eng_fuse, mnt_eng_fuse_clean)


def test_get_eng_cleaned_t(
    t_eng_fuse: Series,
    t_eng_fuse_clean: Series,
):
    """Test get_eng_cleaned with T English subtitles.

    Arguments:
        t_eng_fuse: T English series fixture
        t_eng_fuse_clean: Expected cleaned T English series fixture
    """
    _test_get_eng_cleaned(t_eng_fuse, t_eng_fuse_clean)
