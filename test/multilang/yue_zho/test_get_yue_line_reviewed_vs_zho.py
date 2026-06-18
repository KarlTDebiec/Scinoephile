#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.multilang.yue_zho.get_yue_line_reviewed_vs_zho."""

from __future__ import annotations

from unittest.mock import Mock, patch

from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series, get_series_with_subs_merged
from scinoephile.multilang.yue_zho.line_review import (
    get_yue_line_reviewed_vs_zho,
    get_yue_vs_zho_line_reviewer,
)
from test.data.mlamd import get_mlamd_yue_vs_zho_line_review_test_cases
from test.helpers import assert_series_equal


def test_get_yue_line_reviewed_vs_zho_mlamd(
    mlamd_yue_hans_transcribe: Series,
    mlamd_zho_hans_fuse_clean_validate_review_flatten: Series,
    mlamd_yue_hans_transcribe_review: Series,
):
    """Test get_yue_line_reviewed_vs_zho with MLAMD subtitles.

    Arguments:
        mlamd_yue_hans_transcribe: input written Cantonese subtitles
        mlamd_zho_hans_fuse_clean_validate_review_flatten: input standard
          Chinese subtitles
        mlamd_yue_hans_transcribe_review: expected output subtitles
    """
    zhongwen = get_series_with_subs_merged(
        mlamd_zho_hans_fuse_clean_validate_review_flatten, 539
    )
    provider = Mock(spec=LLMProvider)
    with patch("test.data.mlamd.get_torch_device", return_value="cuda"):
        test_cases = get_mlamd_yue_vs_zho_line_review_test_cases()
    line_reviewer = get_yue_vs_zho_line_reviewer(
        test_cases=test_cases,
        use_dictionary_tool=False,
        provider=provider,
    )
    output = get_yue_line_reviewed_vs_zho(
        mlamd_yue_hans_transcribe,
        zhongwen,
        line_reviewer=line_reviewer,
    )
    assert_series_equal(output, mlamd_yue_hans_transcribe_review)
    provider.chat_completion.assert_not_called()
