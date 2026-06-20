#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.get_zho_block_reviewed."""

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import Mock

from pytest import FixtureRequest, param

from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.lang.zho.block_review import (
    BlockReviewPromptZhoHans,
    BlockReviewPromptZhoHant,
    get_zho_block_reviewed,
    get_zho_reviewer,
)
from test.data.acopopb import (
    get_acopopb_zho_hans_block_review_test_cases,
    get_acopopb_zho_hant_block_review_test_cases,
    get_acopopb_zho_hant_simplify_block_review_test_cases,
)
from test.data.acoptc import (
    get_acoptc_zho_hans_block_review_test_cases,
    get_acoptc_zho_hant_block_review_test_cases,
    get_acoptc_zho_hant_simplify_block_review_test_cases,
)
from test.data.kob import (
    get_kob_zho_hant_block_review_test_cases,
    get_kob_zho_hant_simplify_block_review_test_cases,
)
from test.data.mlamd import (
    get_mlamd_zho_hans_block_review_test_cases,
    get_mlamd_zho_hant_block_review_test_cases,
    get_mlamd_zho_hant_simplify_block_review_test_cases,
)
from test.data.mnt import (
    get_mnt_zho_hans_block_review_test_cases,
    get_mnt_zho_hant_block_review_test_cases,
    get_mnt_zho_hant_simplify_block_review_test_cases,
)
from test.data.t import (
    get_t_zho_hans_block_review_test_cases,
    get_t_zho_hant_block_review_test_cases,
    get_t_zho_hant_simplify_block_review_test_cases,
)
from test.data.tmm import (
    get_tmm_zho_hans_block_review_test_cases,
    get_tmm_zho_hant_block_review_test_cases,
    get_tmm_zho_hant_simplify_block_review_test_cases,
)
from test.helpers import assert_series_equal, parametrize


@parametrize(
    ("series_fixture", "expected_fixture", "test_case_loader", "prompt_cls"),
    [
        param(
            "acopopb_zho_hans_ocr_fuse_clean_validate",
            "acopopb_zho_hans_ocr_fuse_clean_validate_review",
            get_acopopb_zho_hans_block_review_test_cases,
            BlockReviewPromptZhoHans,
            id="acopopb-zho-hans",
        ),
        param(
            "acopopb_zho_hant_ocr_fuse_clean_validate",
            "acopopb_zho_hant_ocr_fuse_clean_validate_review",
            get_acopopb_zho_hant_block_review_test_cases,
            BlockReviewPromptZhoHant,
            id="acopopb-zho-hant",
        ),
        param(
            "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify",
            "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            get_acopopb_zho_hant_simplify_block_review_test_cases,
            BlockReviewPromptZhoHans,
            id="acopopb-zho-hant-simplify",
        ),
        param(
            "acoptc_zho_hans_ocr_fuse_clean_validate",
            "acoptc_zho_hans_ocr_fuse_clean_validate_review",
            get_acoptc_zho_hans_block_review_test_cases,
            BlockReviewPromptZhoHans,
            id="acoptc-zho-hans",
        ),
        param(
            "acoptc_zho_hant_ocr_fuse_clean_validate",
            "acoptc_zho_hant_ocr_fuse_clean_validate_review",
            get_acoptc_zho_hant_block_review_test_cases,
            BlockReviewPromptZhoHant,
            id="acoptc-zho-hant",
        ),
        param(
            "acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify",
            "acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            get_acoptc_zho_hant_simplify_block_review_test_cases,
            BlockReviewPromptZhoHans,
            id="acoptc-zho-hant-simplify",
        ),
        param(
            "kob_zho_hant_ocr_fuse_clean_validate",
            "kob_zho_hant_ocr_fuse_clean_validate_review",
            get_kob_zho_hant_block_review_test_cases,
            BlockReviewPromptZhoHant,
            id="kob-zho-hant",
        ),
        param(
            "kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify",
            "kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            get_kob_zho_hant_simplify_block_review_test_cases,
            BlockReviewPromptZhoHans,
            id="kob-zho-hant-simplify",
        ),
        param(
            "mlamd_zho_hans_fuse_clean_validate",
            "mlamd_zho_hans_fuse_clean_validate_review",
            get_mlamd_zho_hans_block_review_test_cases,
            BlockReviewPromptZhoHans,
            id="mlamd-zho-hans",
        ),
        param(
            "mlamd_zho_hant_fuse_clean_validate",
            "mlamd_zho_hant_fuse_clean_validate_review",
            get_mlamd_zho_hant_block_review_test_cases,
            BlockReviewPromptZhoHant,
            id="mlamd-zho-hant",
        ),
        param(
            "mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify",
            "mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            get_mlamd_zho_hant_simplify_block_review_test_cases,
            BlockReviewPromptZhoHans,
            id="mlamd-zho-hant-simplify",
        ),
        param(
            "mnt_zho_hans_fuse_clean_validate",
            "mnt_zho_hans_fuse_clean_validate_review",
            get_mnt_zho_hans_block_review_test_cases,
            BlockReviewPromptZhoHans,
            id="mnt-zho-hans",
        ),
        param(
            "mnt_zho_hant_fuse_clean_validate",
            "mnt_zho_hant_fuse_clean_validate_review",
            get_mnt_zho_hant_block_review_test_cases,
            BlockReviewPromptZhoHant,
            id="mnt-zho-hant",
        ),
        param(
            "mnt_zho_hant_fuse_clean_validate_review_flatten_simplify",
            "mnt_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            get_mnt_zho_hant_simplify_block_review_test_cases,
            BlockReviewPromptZhoHans,
            id="mnt-zho-hant-simplify",
        ),
        param(
            "t_zho_hans_fuse_clean_validate",
            "t_zho_hans_fuse_clean_validate_review",
            get_t_zho_hans_block_review_test_cases,
            BlockReviewPromptZhoHans,
            id="t-zho-hans",
        ),
        param(
            "t_zho_hant_fuse_clean_validate",
            "t_zho_hant_fuse_clean_validate_review",
            get_t_zho_hant_block_review_test_cases,
            BlockReviewPromptZhoHant,
            id="t-zho-hant",
        ),
        param(
            "t_zho_hant_fuse_clean_validate_review_flatten_simplify",
            "t_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            get_t_zho_hant_simplify_block_review_test_cases,
            BlockReviewPromptZhoHans,
            id="t-zho-hant-simplify",
        ),
        param(
            "tmm_zho_hans_ocr_fuse_clean_validate",
            "tmm_zho_hans_ocr_fuse_clean_validate_review",
            get_tmm_zho_hans_block_review_test_cases,
            BlockReviewPromptZhoHans,
            id="tmm-zho-hans",
        ),
        param(
            "tmm_zho_hant_ocr_fuse_clean_validate",
            "tmm_zho_hant_ocr_fuse_clean_validate_review",
            get_tmm_zho_hant_block_review_test_cases,
            BlockReviewPromptZhoHant,
            id="tmm-zho-hant",
        ),
        param(
            "tmm_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify",
            "tmm_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            get_tmm_zho_hant_simplify_block_review_test_cases,
            BlockReviewPromptZhoHans,
            id="tmm-zho-hant-simplify",
        ),
    ],
)
def test_get_zho_block_reviewed(
    request: FixtureRequest,
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
