#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.multilang.yue_zho.get_yue_line_reviewed_vs_zho."""

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import Mock, patch

from pytest import FixtureRequest, param

from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.multilang.yue_zho.line_review import (
    get_yue_line_reviewed_vs_zho,
    get_yue_vs_zho_line_reviewer,
)
from test.data.mlamd import get_mlamd_yue_vs_zho_line_review_test_cases
from test.helpers import assert_series_equal, parametrize


@parametrize(
    ("yuewen_fixture", "zhongwen_fixture", "expected_fixture", "test_case_loader"),
    [
        param(
            "mlamd_yue_hans_transcribe",
            "mlamd_zho_hans_fuse_clean_validate_review_flatten_merged_539",
            "mlamd_yue_hans_transcribe_review",
            get_mlamd_yue_vs_zho_line_review_test_cases,
            id="mlamd",
        ),
    ],
)
def test_get_yue_line_reviewed_vs_zho(
    request: FixtureRequest,
    yuewen_fixture: str,
    zhongwen_fixture: str,
    expected_fixture: str,
    test_case_loader: Callable[[], list[TestCase]],
):
    """Test get_yue_line_reviewed_vs_zho.

    Arguments:
        request: pytest request for fixture lookup
        yuewen_fixture: fixture name for input written Cantonese subtitles
        zhongwen_fixture: fixture name for input standard Chinese subtitles
        expected_fixture: fixture name for expected output subtitles
        test_case_loader: loader for line review test cases
    """
    yuewen = request.getfixturevalue(yuewen_fixture)
    zhongwen = request.getfixturevalue(zhongwen_fixture)
    expected = request.getfixturevalue(expected_fixture)
    provider = Mock(spec=LLMProvider)
    with patch("test.data.mlamd.get_torch_device", return_value="cuda"):
        test_cases = test_case_loader()
    line_reviewer = get_yue_vs_zho_line_reviewer(
        test_cases=test_cases,
        use_dictionary_tool=False,
        provider=provider,
    )
    output = get_yue_line_reviewed_vs_zho(
        yuewen,
        zhongwen,
        line_reviewer=line_reviewer,
    )
    assert_series_equal(output, expected)
    provider.chat_completion.assert_not_called()

