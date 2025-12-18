#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.get_zho_proofread."""

from __future__ import annotations

import pytest

from scinoephile.core.subtitles import Series
from scinoephile.lang.zho import get_zho_proofread
from scinoephile.lang.zho.proofreading import (
    ZhoHantProofreadingPrompt,
    get_zho_proofreader,
)
from scinoephile.llms.blockwise import BlockwiseReviewer


def _test_get_zho_proofread(
    series: Series, expected: Series, reviewer: BlockwiseReviewer | None = None
):
    """Test get_zho_proofread.

    Arguments:
        series: Series with which to test
        expected: Expected output series
        reviewer: BlockwiseReviewer to use for the test
    """
    output = get_zho_proofread(series, reviewer=reviewer)

    assert len(output) == len(expected)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies:\n" + "\n".join(errors))


def test_get_zho_proofread_kob(
    kob_zho_hant_fuse: Series,
    kob_zho_hant_fuse_proofread: Series,
):
    """Test get_zho_proofread with KOB English subtitles.

    Arguments:
        kob_zho_hant_fuse: KOB English series fixture
        kob_zho_hant_fuse_proofread: Expected proofread KOB English series fixture
    """
    _test_get_zho_proofread(
        kob_zho_hant_fuse,
        kob_zho_hant_fuse_proofread,
        get_zho_proofreader(prompt_cls=ZhoHantProofreadingPrompt),
    )


def test_get_zho_proofread_mlamd(
    mlamd_zho_hans_fuse: Series,
    mlamd_zho_hans_fuse_proofread: Series,
):
    """Test get_zho_proofread with MLAMD English subtitles.

    Arguments:
        mlamd_zho_hans_fuse: MLAMD English series fixture
        mlamd_zho_hans_fuse_proofread: Expected proofread MLAMD English series fixture
    """
    _test_get_zho_proofread(mlamd_zho_hans_fuse, mlamd_zho_hans_fuse_proofread)


def test_get_zho_proofread_mnt(
    mnt_zho_hans_fuse: Series,
    mnt_zho_hans_fuse_proofread: Series,
):
    """Test get_zho_proofread with MNT English subtitles.

    Arguments:
        mnt_zho_hans_fuse: MNT English series fixture
        mnt_zho_hans_fuse_proofread: Expected proofread MNT English series fixture
    """
    _test_get_zho_proofread(mnt_zho_hans_fuse, mnt_zho_hans_fuse_proofread)


def test_get_zho_proofread_t(
    t_zho_hans_fuse: Series,
    t_zho_hans_fuse_proofread: Series,
):
    """Test get_zho_proofread with T English subtitles.

    Arguments:
        t_zho_hans_fuse: T English series fixture
        t_zho_hans_fuse_proofread: Expected proofread T English series fixture
    """
    _test_get_zho_proofread(t_zho_hans_fuse, t_zho_hans_fuse_proofread)
