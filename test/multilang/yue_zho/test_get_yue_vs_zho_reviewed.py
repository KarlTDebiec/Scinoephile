#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.multilang.yue_zho.get_yue_vs_zho_reviewed."""

from __future__ import annotations

import pytest

from scinoephile.core import Series, get_series_with_subs_merged
from scinoephile.multilang.yue_zho import get_yue_vs_zho_reviewed


def _test_get_yue_vs_zho_reviewed(yuewen: Series, zhongwen: Series, expected: Series):
    """Test get_yue_vs_zho_reviewed function.

    Arguments:
        yuewen: 粤文 Series
        zhongwen: 中文 Series
        expected: expected output Series
    """
    output = get_yue_vs_zho_reviewed(yuewen, zhongwen)

    assert len(output) == len(expected)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies:\n" + "\n".join(errors))


def test_get_yue_vs_zho_reviewed_mlamd(
    mlamd_yue_hans: Series,
    mlamd_zho_hans_fuse_proofread_clean_flatten: Series,
    mlamd_yue_hans_review: Series,
):
    """Test get_yue_vs_zho_reviewed with MLAMD subtitles.

    Arguments:
        mlamd_yue_hans: MLAMD 粤文 subtitles fixture
        mlamd_zho_hans_fuse_proofread_clean_flatten: MLAMD 中文 subtitles fixture
        mlamd_yue_hans_review: Expected reviewed MLAMD 粤文 subtitles fixture
    """
    zhongwen = get_series_with_subs_merged(
        mlamd_zho_hans_fuse_proofread_clean_flatten, 539
    )

    _test_get_yue_vs_zho_reviewed(
        mlamd_yue_hans,
        zhongwen,
        mlamd_yue_hans_review,
    )
