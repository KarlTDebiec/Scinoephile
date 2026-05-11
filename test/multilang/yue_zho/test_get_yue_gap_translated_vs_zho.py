#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.multilang.yue_zho.gap_translation."""

from __future__ import annotations

from scinoephile.core.subtitles import Series, get_series_with_subs_merged
from scinoephile.multilang.yue_zho.gap_translation import get_yue_gap_translated_vs_zho
from test.helpers import assert_series_equal


def test_get_yue_gap_translated_vs_zho_mlamd(
    mlamd_yue_hans_transcribe_review: Series,
    mlamd_zho_hans_fuse_clean_validate_review_flatten: Series,
    mlamd_yue_hans_transcribe_review_translate: Series,
):
    """Test get_yue_gap_translated_vs_zho with MLAMD subtitles.

    Arguments:
        mlamd_yue_hans_transcribe_review: input written Cantonese subtitles
        mlamd_zho_hans_fuse_clean_validate_review_flatten: input standard
          Chinese subtitles
        mlamd_yue_hans_transcribe_review_translate: expected output subtitles
    """
    zhongwen = get_series_with_subs_merged(
        mlamd_zho_hans_fuse_clean_validate_review_flatten, 539
    )
    output = get_yue_gap_translated_vs_zho(mlamd_yue_hans_transcribe_review, zhongwen)
    assert_series_equal(output, mlamd_yue_hans_transcribe_review_translate)
