#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.multilang.yue_zho.get_yue_translated_vs_zho."""

from __future__ import annotations

from scinoephile.core.subtitles import Series, get_series_with_subs_merged
from scinoephile.multilang.yue_zho import get_yue_translated_vs_zho


def test_get_yue_translated_vs_zho_mlamd(
    mlamd_yue_hans_transcribe_review: Series,
    mlamd_zho_hans_fuse_clean_validate_proofread_flatten: Series,
    mlamd_yue_hans_transcribe_review_translate: Series,
):
    """Test get_yue_translated_vs_zho with MLAMD subtitles.

    Arguments:
        mlamd_yue_hans_transcribe_review: input 粤文 subtitles
        mlamd_zho_hans_fuse_clean_validate_proofread_flatten: input 中文 subtitles
        mlamd_yue_hans_transcribe_review_translate: expected output subtitles
    """
    zhongwen = get_series_with_subs_merged(
        mlamd_zho_hans_fuse_clean_validate_proofread_flatten, 539
    )
    output = get_yue_translated_vs_zho(mlamd_yue_hans_transcribe_review, zhongwen)
    assert output == mlamd_yue_hans_transcribe_review_translate
