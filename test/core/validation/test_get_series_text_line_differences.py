#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.validation.get_series_text_line_differences."""

from __future__ import annotations

import pytest

from scinoephile.core.subtitles import Series
from scinoephile.core.validation import get_series_text_line_differences


def _test_get_series_text_line_differences(
    ocr_series: Series,
    srt_series: Series,
):
    """Test get_series_text_line_differences.

    Arguments:
        ocr_series: OCR subtitle series
        srt_series: SRT subtitle series
    """
    differences = get_series_text_line_differences(
        ocr_series,
        srt_series,
        one_label="OCR",
        two_label="SRT",
    )
    if differences:
        for difference in differences:
            print(difference)
        pytest.fail(f"Found {len(differences)} discrepancies")


def test_get_series_text_line_differences_kob(
    kob_eng_fuse_clean_validate_proofread_flatten: Series,
    kob_eng_timewarp_clean_proofread_flatten: Series,
):
    """Test get_series_text_line_differences with KOB English subtitles.

    Arguments:
        kob_eng_fuse_clean_validate_proofread_flatten: OCR English subtitles
        kob_eng_timewarp_clean_proofread_flatten: timewarped SRT English subtitles
    """
    _test_get_series_text_line_differences(
        kob_eng_fuse_clean_validate_proofread_flatten,
        kob_eng_timewarp_clean_proofread_flatten,
    )
