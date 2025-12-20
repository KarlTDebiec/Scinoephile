#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.multilang.yue_zho.get_yue_vs_zho_translated."""

from __future__ import annotations

import pytest

from scinoephile.core.subtitles import Series, get_series_with_subs_merged
from scinoephile.multilang.yue_zho import get_yue_from_zho_translated


def _test_get_yue_vs_zho_translated(yuewen: Series, zhongwen: Series, expected: Series):
    """Test get_yue_vs_zho_translated function.

    Arguments:
        yuewen: input 粤文 subtitles
        zhongwen: input 中文 subtitles
        expected: expected output subtitles
    """
    output = get_yue_from_zho_translated(yuewen, zhongwen)

    assert len(output) == len(expected)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies:\n" + "\n".join(errors))


def test_get_yue_vs_zho_translated_mlamd(
    mlamd_yue_hans_proofread: Series,
    mlamd_zho_hans_fuse_proofread_clean_flatten: Series,
    mlamd_yue_hans_proofread_translate: Series,
):
    """Test get_yue_vs_zho_translated with MLAMD subtitles.

    Arguments:
        mlamd_yue_hans_proofread: input 粤文 subtitles
        mlamd_zho_hans_fuse_proofread_clean_flatten: input 中文 subtitles
        mlamd_yue_hans_proofread_translate: expected output subtitles fixture
    """
    zhongwen = get_series_with_subs_merged(
        mlamd_zho_hans_fuse_proofread_clean_flatten, 539
    )

    _test_get_yue_vs_zho_translated(
        mlamd_yue_hans_proofread,
        zhongwen,
        mlamd_yue_hans_proofread_translate,
    )
