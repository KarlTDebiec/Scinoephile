#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.validation.get_series_text_differences."""

from __future__ import annotations

import pytest

from scinoephile.core.subtitles import Series
from scinoephile.core.validation import get_series_text_differences


def _test_get_series_text_differences(
    one: Series,
    two: Series,
):
    """Test get_series_text_differences.

    Arguments:
        one: First subtitle series
        two: Second subtitle series
    """
    differences = get_series_text_differences(one, two)
    if differences:
        for difference in differences:
            print(difference)
        pytest.fail(f"Found {len(differences)} discrepancies")


def test_get_series_text_differences_kob(
    kob_eng_fuse_clean_validate_proofread_flatten: Series,
    kob_eng_timewarp_clean_proofread_flatten: Series,
):
    """Test get_series_text_differences with KOB English subtitles.

    Arguments:
        kob_eng_fuse_clean_validate_proofread_flatten: OCR English subtitles
        kob_eng_timewarp_clean_proofread_flatten: timewarped SRT English subtitles
    """
    _test_get_series_text_differences(
        kob_eng_fuse_clean_validate_proofread_flatten,
        kob_eng_timewarp_clean_proofread_flatten,
    )
