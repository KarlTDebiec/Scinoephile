#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.get_zho_flattened."""

from __future__ import annotations

import pytest

from scinoephile.core.subtitles import Series
from scinoephile.lang.zho import get_zho_flattened

# noinspection PyProtectedMember
from scinoephile.lang.zho.flattening import _get_zho_text_flattened


def _test_get_zho_flattened(series: Series, expected: Series):
    """Test get_zho_flattened.

    Arguments:
        series: Series with which to test
        expected: Expected output series
    """
    output = get_zho_flattened(series)
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


def test_get_zho_flattened_kob(
    kob_yue_hans_clean: Series,
    kob_yue_hans_clean_flatten: Series,
):
    """Test get_zho_flattened with KOB 简体粤文 subtitles.

    Arguments:
        kob_yue_hans_clean: KOB 简体粤文 series fixture
        kob_yue_hans_clean_flatten: Expected flattened KOB 简体粤文 series fixture
    """
    _test_get_zho_flattened(kob_yue_hans_clean, kob_yue_hans_clean_flatten)


def test_get_zho_flattened_mlamd(
    mlamd_zho_hans_fuse_proofread_clean: Series,
    mlamd_zho_hans_fuse_proofread_clean_flatten: Series,
):
    """Test get_zho_flattened with MLAMD 简体中文 subtitles.

    Arguments:
        mlamd_zho_hans_fuse_proofread_clean: MLAMD 简体中文 series fixture
        mlamd_zho_hans_fuse_proofread_clean_flatten: Expected flattened MLAMD 简体中文
          series fixture
    """
    _test_get_zho_flattened(
        mlamd_zho_hans_fuse_proofread_clean, mlamd_zho_hans_fuse_proofread_clean_flatten
    )


def test_get_zho_flattened_mnt(
    mnt_zho_hant_clean: Series,
    mnt_zho_hant_clean_flatten: Series,
):
    """Test get_zho_flattened with MNT 繁体中文 subtitles.

    Arguments:
        mnt_zho_hant_clean: MNT 繁体中文 series fixture
        mnt_zho_hant_clean_flatten: Expected flattened MNT 繁体中文 series fixture
    """
    _test_get_zho_flattened(mnt_zho_hant_clean, mnt_zho_hant_clean_flatten)


def test_get_zho_flattened_t(
    t_zho_hans_clean: Series,
    t_zho_hans_clean_flatten: Series,
):
    """Test get_zho_flattened with T 簡體中文 subtitles.

    Arguments:
        t_zho_hans_clean: T 簡體中文 series fixture
        t_zho_hans_clean_flatten: Expected flattened T 簡體中文 series fixture
    """
    _test_get_zho_flattened(t_zho_hans_clean, t_zho_hans_clean_flatten)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("line 1\nline 2", "line 1　line 2"),
    ],
)
def test_get_zho_text_flattened(text: str, expected: str):
    """Test _get_zho_text_flattened.

    Arguments:
        text: Text to flatten
        expected: Expected flattened text
    """
    assert _get_zho_text_flattened(text) == expected
