#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.image.zhongwen.get_zhongwen_ocr_fused."""

from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.zhongwen import (
    OpenCCConfig,
    get_zhongwen_cleaned,
    get_zhongwen_converted,
)
from scinoephile.image.zhongwen.fusion import get_zhongwen_ocr_fused2


def _test_get_zhongwen_ocr_fused(lens: Series, paddle: Series, expected: Series):
    """Test get_zhongwen_ocr_fused.

    Arguments:
        lens: subtitles OCRed using Google Lens
        paddle: subtitles OCRed using PaddleOCR
        expected: expected output series
    """
    output = get_zhongwen_ocr_fused2(lens, paddle)

    assert len(lens) == len(output)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies:\n" + "\n".join(errors))


def test_get_zhongwen_ocr_fused_kob(
    kob_zho_hant_lens: Series,
    kob_zho_hant_paddle: Series,
    kob_zho_hant_fuse: Series,
):
    """Test get_zhongwen_ocr_fused with KOB Zhongwen subtitles.

    Arguments:
        kob_zho_hant_lens: KOB Zhongwen subtitles OCRed using Google Lens fixture
        kob_zho_hant_paddle: KOB Zhongwen subtitles OCRed using PaddleOCR fixture
        kob_zho_hant_fuse: Expected fused KOB Zhongwen subtitles fixture
    """
    lens = get_zhongwen_cleaned(kob_zho_hant_lens, remove_empty=False)
    lens = get_zhongwen_converted(lens, config=OpenCCConfig.s2t)
    paddle = get_zhongwen_cleaned(kob_zho_hant_paddle, remove_empty=False)
    paddle = get_zhongwen_converted(paddle, config=OpenCCConfig.s2t)
    _test_get_zhongwen_ocr_fused(lens, paddle, kob_zho_hant_fuse)


def test_get_zhongwen_ocr_fused_mlamd(
    mlamd_zho_hans_lens: Series,
    mlamd_zho_hans_paddle: Series,
    mlamd_zho_hans_fuse: Series,
):
    """Test get_zhongwen_ocr_fused with MLAMD Zhongwen subtitles.

    Arguments:
        mlamd_zho_hans_lens: MLAMD Zhongwen subtitles OCRed using Google Lens fixture
        mlamd_zho_hans_paddle: MLAMD 中文 subtitles OCRed using PaddleOCR fixture
        mlamd_zho_hans_fuse: Expected fused MLAMD 中文 subtitles fixture
    """
    lens = get_zhongwen_cleaned(mlamd_zho_hans_lens, remove_empty=False)
    lens = get_zhongwen_converted(lens)
    paddle = get_zhongwen_cleaned(mlamd_zho_hans_paddle, remove_empty=False)
    paddle = get_zhongwen_converted(paddle)
    _test_get_zhongwen_ocr_fused(lens, paddle, mlamd_zho_hans_fuse)


def test_get_zhongwen_ocr_fused_mnt(
    mnt_zho_hans_lens: Series,
    mnt_zho_hans_paddle: Series,
    mnt_zho_hans_fuse: Series,
):
    """Test get_zhongwen_ocr_fused with MNT 中文 subtitles.

    Arguments:
        mnt_zho_hans_lens: MNT 中文 subtitles OCRed using Google Lens fixture
        mnt_zho_hans_paddle: MNT 中文 subtitles OCRed using PaddleOCR fixture
        mnt_zho_hans_fuse: Expected fused MNT 中文 subtitles fixture
    """
    lens = get_zhongwen_cleaned(mnt_zho_hans_lens, remove_empty=False)
    lens = get_zhongwen_converted(lens)
    paddle = get_zhongwen_cleaned(mnt_zho_hans_paddle, remove_empty=False)
    paddle = get_zhongwen_converted(paddle)
    _test_get_zhongwen_ocr_fused(lens, paddle, mnt_zho_hans_fuse)


def test_get_zhongwen_ocr_fused_t(
    t_zho_hans_lens: Series, t_zho_hans_paddle: Series, t_zho_hans_fuse: Series
):
    """Test get_zhongwen_ocr_fused with T 中文 subtitles.

    Arguments:
        t_zho_hans_lens: T 中文 subtitles OCRed using Google Lens fixture
        t_zho_hans_paddle: T 中文 subtitles OCRed using PaddleOCR fixture
        t_zho_hans_fuse: Expected fused T 中文 subtitles fixture
    """
    lens = get_zhongwen_cleaned(t_zho_hans_lens, remove_empty=False)
    lens = get_zhongwen_converted(lens)
    paddle = get_zhongwen_cleaned(t_zho_hans_paddle, remove_empty=False)
    paddle = get_zhongwen_converted(paddle)
    _test_get_zhongwen_ocr_fused(lens, paddle, t_zho_hans_fuse)
