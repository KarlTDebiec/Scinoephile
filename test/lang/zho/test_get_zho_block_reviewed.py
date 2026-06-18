#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.get_zho_block_reviewed."""

from __future__ import annotations

from collections.abc import Callable
from os import getenv
from unittest.mock import Mock

import pytest

from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.lang.zho.block_review import (
    BlockReviewPromptZhoHans,
    BlockReviewPromptZhoHant,
    get_zho_block_reviewed,
    get_zho_reviewer,
)
from test.data.t import (
    get_t_zho_hans_block_review_test_cases,
    get_t_zho_hant_block_review_test_cases,
    get_t_zho_hant_simplify_block_review_test_cases,
)
from test.helpers import assert_series_equal, skip_if_ci

_LIVE_LLM_MARKS = [
    skip_if_ci(),
    pytest.mark.skipif(
        not getenv("SCINOEPHILE_RUN_LLM_TESTS"),
        reason="Requires live LLM integration tests",
    ),
]
"""Marks for live LLM integration cases."""


@pytest.mark.parametrize(
    ("series_fixture", "expected_fixture", "use_traditional_prompt"),
    [
        (
            "kob_zho_hant_ocr_fuse_clean_validate",
            "kob_zho_hant_ocr_fuse_clean_validate_review",
            True,
        ),
        pytest.param(
            "mlamd_zho_hans_fuse_clean_validate",
            "mlamd_zho_hans_fuse_clean_validate_review",
            False,
            marks=_LIVE_LLM_MARKS,
        ),
        pytest.param(
            "mnt_zho_hans_fuse_clean_validate",
            "mnt_zho_hans_fuse_clean_validate_review",
            False,
            marks=_LIVE_LLM_MARKS,
        ),
        pytest.param(
            "t_zho_hans_fuse_clean_validate",
            "t_zho_hans_fuse_clean_validate_review",
            False,
            marks=_LIVE_LLM_MARKS,
        ),
    ],
)
def test_get_zho_block_reviewed(
    request: pytest.FixtureRequest,
    series_fixture: str,
    expected_fixture: str,
    use_traditional_prompt: bool,
):
    """Test get_zho_block_reviewed against expected block-reviewed outputs.

    Arguments:
        request: pytest request for fixture lookup
        series_fixture: fixture name for input series
        expected_fixture: fixture name for expected output series
        use_traditional_prompt: whether to use the traditional prompt reviewer
    """
    processor = None
    if use_traditional_prompt:
        processor = get_zho_reviewer(prompt_cls=BlockReviewPromptZhoHant)
    expected = request.getfixturevalue(expected_fixture)
    output = get_zho_block_reviewed(
        request.getfixturevalue(series_fixture),
        processor=processor,
    )

    assert len(output) == len(expected)
    assert_series_equal(output, expected)


@pytest.mark.parametrize(
    ("series_fixture", "expected_fixture", "test_case_loader", "prompt_cls"),
    [
        (
            "t_zho_hans_fuse_clean_validate",
            "t_zho_hans_fuse_clean_validate_review",
            get_t_zho_hans_block_review_test_cases,
            BlockReviewPromptZhoHans,
        ),
        (
            "t_zho_hant_fuse_clean_validate",
            "t_zho_hant_fuse_clean_validate_review",
            get_t_zho_hant_block_review_test_cases,
            BlockReviewPromptZhoHant,
        ),
        (
            "t_zho_hant_fuse_clean_validate_review_flatten_simplify",
            "t_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            get_t_zho_hant_simplify_block_review_test_cases,
            BlockReviewPromptZhoHans,
        ),
    ],
)
def test_get_zho_block_reviewed_t_from_verified_cases(
    request: pytest.FixtureRequest,
    series_fixture: str,
    expected_fixture: str,
    test_case_loader: Callable[[], list[TestCase]],
    prompt_cls: type[BlockReviewPromptZhoHans],
):
    """Test get_zho_block_reviewed with T verified block review cases.

    Arguments:
        request: pytest request for fixture lookup
        series_fixture: fixture name for input series
        expected_fixture: fixture name for expected output series
        test_case_loader: test case loader for the review path
        prompt_cls: prompt class for the review path
    """
    provider = Mock(spec=LLMProvider)
    processor = get_zho_reviewer(
        prompt_cls=prompt_cls,
        test_cases=test_case_loader(),
        provider=provider,
    )
    expected = request.getfixturevalue(expected_fixture)
    output = get_zho_block_reviewed(
        request.getfixturevalue(series_fixture),
        processor=processor,
    )

    assert len(output) == len(expected)
    assert_series_equal(output, expected)
    provider.chat_completion.assert_not_called()
