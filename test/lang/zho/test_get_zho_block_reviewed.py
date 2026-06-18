#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.get_zho_block_reviewed."""

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import Mock

import pytest

from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.lang.zho.block_review import (
    BlockReviewPromptZhoHans,
    BlockReviewPromptZhoHant,
    get_zho_block_reviewed,
    get_zho_reviewer,
)
from test.data.kob import get_kob_zho_hant_block_review_test_cases
from test.data.t import (
    get_t_zho_hans_block_review_test_cases,
    get_t_zho_hant_block_review_test_cases,
    get_t_zho_hant_simplify_block_review_test_cases,
)
from test.helpers import assert_series_equal


@pytest.mark.parametrize(
    ("series_fixture", "expected_fixture", "test_case_loader", "prompt_cls"),
    [
        pytest.param(
            "kob_zho_hant_ocr_fuse_clean_validate",
            "kob_zho_hant_ocr_fuse_clean_validate_review",
            get_kob_zho_hant_block_review_test_cases,
            BlockReviewPromptZhoHant,
            id="kob-zho-hant",
        ),
        pytest.param(
            "t_zho_hans_fuse_clean_validate",
            "t_zho_hans_fuse_clean_validate_review",
            get_t_zho_hans_block_review_test_cases,
            BlockReviewPromptZhoHans,
            id="t-zho-hans",
        ),
        pytest.param(
            "t_zho_hant_fuse_clean_validate",
            "t_zho_hant_fuse_clean_validate_review",
            get_t_zho_hant_block_review_test_cases,
            BlockReviewPromptZhoHant,
            id="t-zho-hant",
        ),
        pytest.param(
            "t_zho_hant_fuse_clean_validate_review_flatten_simplify",
            "t_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            get_t_zho_hant_simplify_block_review_test_cases,
            BlockReviewPromptZhoHans,
            id="t-zho-hant-simplify",
        ),
    ],
)
def test_get_zho_block_reviewed(
    request: pytest.FixtureRequest,
    series_fixture: str,
    expected_fixture: str,
    test_case_loader: Callable[[], list[TestCase]],
    prompt_cls: type[BlockReviewPromptZhoHans],
):
    """Test get_zho_block_reviewed against expected block-reviewed outputs.

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
