#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.eng.test_get_eng_flattened."""

from __future__ import annotations

import pytest

from scinoephile.core.subtitles import Series
from scinoephile.lang.eng import get_eng_flattened

# noinspection PyProtectedMember
from scinoephile.lang.eng.flattening import _get_eng_text_flattened


def _test_get_eng_flattened(series: Series, expected: Series):
    """Test get_eng_flattened.

    Arguments:
        series: Series with which to test
        expected: Expected output series
    """
    output = get_eng_flattened(series)

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


def test_get_eng_flattened_kob(
    kob_eng_clean: Series,
    kob_eng_clean_flatten: Series,
):
    """Test get_eng_flattened with KOB English subtitles.

    Arguments:
        kob_eng_clean: KOB English series fixture
        kob_eng_clean_flatten: Expected flattened KOB English series fixture
    """
    _test_get_eng_flattened(kob_eng_clean, kob_eng_clean_flatten)


def test_get_eng_flattened_mlamd(
    mlamd_eng_fuse_clean_validate: Series,
    mlamd_eng_fuse_clean_validate_flatten: Series,
):
    """Test get_eng_flattened with MLAMD English subtitles.

    Arguments:
        mlamd_eng_fuse_clean_validate: MLAMD English series fixture
        mlamd_eng_fuse_clean_validate_flatten: Expected flattened MLAMD English series
          fixture
    """
    _test_get_eng_flattened(
        mlamd_eng_fuse_clean_validate, mlamd_eng_fuse_clean_validate_flatten
    )


def test_get_eng_flattened_mnt(
    mnt_eng_fuse_proofread_clean: Series,
    mnt_eng_fuse_proofread_clean_flatten: Series,
):
    """Test get_eng_flattened with MNT English subtitles.

    Arguments:
        mnt_eng_fuse_proofread_clean: MNT English series fixture
        mnt_eng_fuse_proofread_clean_flatten: Expected flattened MNT English series
          fixture
    """
    _test_get_eng_flattened(
        mnt_eng_fuse_proofread_clean, mnt_eng_fuse_proofread_clean_flatten
    )


def test_get_eng_flattened_t(
    t_eng_clean: Series,
    t_eng_clean_flatten: Series,
):
    """Test get_eng_flattened with T English subtitles.

    Arguments:
        t_eng_clean: T English series fixture
        t_eng_clean_flatten: Expected flattened T English series fixture
    """
    _test_get_eng_flattened(t_eng_clean, t_eng_clean_flatten)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("line 1\nline 2", "line 1 line 2"),
    ],
)
def test_get_eng_text_flattened(text: str, expected: str):
    """Test get_eng_text_flattened.

    Arguments:
        text: Text to flatten
        expected: Expected flattened text
    """
    assert _get_eng_text_flattened(text) == expected
