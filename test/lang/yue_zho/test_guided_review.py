#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of guided review of written Cantonese using standard Chinese."""

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import Mock, patch

from pytest import FixtureRequest, param

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.lang.review.guided import get_guided_reviewer
from scinoephile.workflows.review import review_series_guided
from test.data.mlamd import get_mlamd_yue_vs_zho_guided_review_test_cases
from test.helpers import assert_series_equal, parametrize


@parametrize(
    (
        "yuewen_fixture",
        "zhongwen_fixture",
        "expected_fixture",
        "test_case_loader",
        "device_patch_target",
        "device_name",
    ),
    [
        param(
            "mlamd_yue_hans_transcribe_review_translate",
            "mlamd_zho_hans_fuse_clean_validate_review_flatten_merged_539",
            "mlamd_yue_hans_transcribe_review_translate_guided_review",
            get_mlamd_yue_vs_zho_guided_review_test_cases,
            "test.data.mlamd.get_torch_device",
            "cuda",
            id="mlamd",
        ),
    ],
)
def test_review_series_guided_yue_zho(
    request: FixtureRequest,
    yuewen_fixture: str,
    zhongwen_fixture: str,
    expected_fixture: str,
    test_case_loader: Callable[[], list[TestCase]],
    device_patch_target: str,
    device_name: str,
):
    """Test guided review of written Cantonese using standard Chinese.

    Arguments:
        request: pytest request for fixture lookup
        yuewen_fixture: fixture name for input written Cantonese subtitles
        zhongwen_fixture: fixture name for input standard Chinese subtitles
        expected_fixture: fixture name for expected output subtitles
        test_case_loader: loader for guided review test cases
        device_patch_target: import path to patch for device-specific test cases
        device_name: device-specific test case file stem
    """
    yuewen = request.getfixturevalue(yuewen_fixture)
    zhongwen = request.getfixturevalue(zhongwen_fixture)
    expected = request.getfixturevalue(expected_fixture)
    provider = Mock(spec=LLMProvider)
    with patch(device_patch_target, return_value=device_name):
        test_cases = test_case_loader()
    reviewer = get_guided_reviewer(
        Language.yue_hans, Language.zho_hans, test_cases=test_cases, provider=provider
    )
    output = review_series_guided(yuewen, zhongwen, reviewer=reviewer)
    assert_series_equal(output, expected)
    provider.chat_completion.assert_not_called()
