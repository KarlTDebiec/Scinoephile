#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.get_zho_block_reviewed."""

from __future__ import annotations

import pytest

from scinoephile.core.subtitles import Series
from scinoephile.lang.zho import get_zho_block_reviewed
from scinoephile.lang.zho.block_review import (
    ZhoHantBlockReviewPrompt,
    get_zho_reviewer,
)
from scinoephile.llms.mono_block import MonoBlockProcessor


def _test_get_zho_block_reviewed(
    series: Series, expected: Series, processor: MonoBlockProcessor | None = None
):
    """Test get_zho_block_reviewed.

    Arguments:
        series: Series with which to test
        expected: Expected output series
        processor: MonoBlockProcessor to use for the test
    """
    output = get_zho_block_reviewed(series, processor=processor)

    assert len(output) == len(expected)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies:\n" + "\n".join(errors))


def test_get_zho_block_reviewed_kob(
    kob_zho_hant_fuse_clean_validate: Series,
    kob_zho_hant_fuse_clean_validate_review: Series,
):
    """Test get_zho_block_reviewed with KOB 繁体中文 subtitles.

    Arguments:
        kob_zho_hant_fuse_clean_validate: KOB 繁体中文 series fixture
        kob_zho_hant_fuse_clean_validate_review: Expected block-reviewed KOB
          繁体中文 series fixture
    """
    _test_get_zho_block_reviewed(
        kob_zho_hant_fuse_clean_validate,
        kob_zho_hant_fuse_clean_validate_review,
        get_zho_reviewer(prompt_cls=ZhoHantBlockReviewPrompt),
    )


def test_get_zho_block_reviewed_mlamd(
    mlamd_zho_hans_fuse_clean_validate: Series,
    mlamd_zho_hans_fuse_clean_validate_review: Series,
):
    """Test get_zho_block_reviewed with MLAMD 简体中文 subtitles.

    Arguments:
        mlamd_zho_hans_fuse_clean_validate: MLAMD 简体中文 series fixture
        mlamd_zho_hans_fuse_clean_validate_review: Expected block-reviewed MLAMD
          简体中文 series fixture
    """
    _test_get_zho_block_reviewed(
        mlamd_zho_hans_fuse_clean_validate,
        mlamd_zho_hans_fuse_clean_validate_review,
    )


def test_get_zho_block_reviewed_mnt(
    mnt_zho_hans_fuse_clean_validate: Series,
    mnt_zho_hans_fuse_clean_validate_review: Series,
):
    """Test get_zho_block_reviewed with MNT 简体中文 subtitles.

    Arguments:
        mnt_zho_hans_fuse_clean_validate: MNT 简体中文 series fixture
        mnt_zho_hans_fuse_clean_validate_review: Expected block-reviewed MNT
          简体中文 series fixture
    """
    _test_get_zho_block_reviewed(
        mnt_zho_hans_fuse_clean_validate,
        mnt_zho_hans_fuse_clean_validate_review,
    )


def test_get_zho_block_reviewed_t(
    t_zho_hans_fuse_clean_validate: Series,
    t_zho_hans_fuse_clean_validate_review: Series,
):
    """Test get_zho_block_reviewed with T 简体中文 subtitles.

    Arguments:
        t_zho_hans_fuse_clean_validate: T 简体中文 series fixture
        t_zho_hans_fuse_clean_validate_review: Expected block-reviewed T
          简体中文 series fixture
    """
    _test_get_zho_block_reviewed(
        t_zho_hans_fuse_clean_validate,
        t_zho_hans_fuse_clean_validate_review,
    )
