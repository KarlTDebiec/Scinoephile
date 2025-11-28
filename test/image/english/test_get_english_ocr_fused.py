#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.image.english.get_english_ocr_fused."""

from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.english import get_english_cleaned
from scinoephile.image.english.fusion import get_english_ocr_fused


def _test_get_english_ocr_fused(tesseract: Series, lens: Series, expected: Series):
    """Test get_english_ocr_fused.

    Arguments:
        tesseract: subtitles OCRed using Tesseract
        lens: subtitles OCRed using Google Lens
        expected: expected output series
    """
    output = get_english_ocr_fused(tesseract, lens)

    assert len(tesseract) == len(output)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies:\n" + "\n".join(errors))


def test_get_english_ocr_fused_kob(
    kob_eng_tesseract: Series, kob_eng_lens: Series, kob_eng_fuse: Series
):
    """Test get_english_ocr_fused with KOB English subtitles.

    Arguments:
        kob_eng_tesseract: KOB English subtitles OCRed using Tesseract fixture
        kob_eng_lens: KOB English subtitles OCRed using Google Lens fixture
        kob_eng_fuse: Expected fused KOB English subtitles fixture
    """
    tesseract = get_english_cleaned(kob_eng_tesseract, remove_empty=False)
    lens = get_english_cleaned(kob_eng_lens, remove_empty=False)
    _test_get_english_ocr_fused(tesseract, lens, kob_eng_fuse)


def test_get_english_ocr_fused_mlamd(
    mlamd_eng_tesseract: Series, mlamd_eng_lens: Series, mlamd_eng_fuse: Series
):
    """Test get_english_ocr_fused with MLAMD English subtitles.

    Arguments:
        mlamd_eng_tesseract: MLAMD English subtitles OCRed using Tesseract fixture
        mlamd_eng_lens: MLAMD English subtitles OCRed using Google Lens fixture
        mlamd_eng_fuse: Expected fused MLAMD English subtitles fixture
    """
    tesseract = get_english_cleaned(mlamd_eng_tesseract, remove_empty=False)
    lens = get_english_cleaned(mlamd_eng_lens, remove_empty=False)
    _test_get_english_ocr_fused(tesseract, lens, mlamd_eng_fuse)


def test_get_english_ocr_fused_mnt(
    mnt_eng_tesseract: Series, mnt_eng_lens: Series, mnt_eng_fuse: Series
):
    """Test get_english_ocr_fused with MNT English subtitles.

    Arguments:
        mnt_eng_tesseract: MNT English subtitles OCRed using Tesseract fixture
        mnt_eng_lens: MNT English subtitles OCRed using Google Lens fixture
        mnt_eng_fuse: Expected fused MNT English subtitles fixture
    """
    tesseract = get_english_cleaned(mnt_eng_tesseract, remove_empty=False)
    lens = get_english_cleaned(mnt_eng_lens, remove_empty=False)
    _test_get_english_ocr_fused(tesseract, lens, mnt_eng_fuse)


def test_get_english_ocr_fused_t(
    t_eng_tesseract: Series, t_eng_lens: Series, t_eng_fuse: Series
):
    """Test get_english_ocr_fused with T English subtitles.

    Arguments:
        t_eng_tesseract: T English subtitles OCRed using Tesseract fixture
        t_eng_lens: T English subtitles OCRed using Google Lens fixture
        t_eng_fuse: Expected fused T English subtitles fixture
    """
    tesseract = get_english_cleaned(t_eng_tesseract, remove_empty=False)
    lens = get_english_cleaned(t_eng_lens, remove_empty=False)
    _test_get_english_ocr_fused(tesseract, lens, t_eng_fuse)
