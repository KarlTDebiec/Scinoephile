#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.eng.get_eng_block_reviewed."""

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import Mock

from pytest import FixtureRequest, param

from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.lang.eng.block_review import (
    get_eng_block_reviewed,
    get_eng_block_reviewer,
)
from test.data.acopopb import get_acopopb_eng_block_review_test_cases
from test.data.acoptc import get_acoptc_eng_block_review_test_cases
from test.data.kob import get_kob_eng_block_review_test_cases
from test.data.mlamd import get_mlamd_eng_block_review_test_cases
from test.data.mnt import get_mnt_eng_block_review_test_cases
from test.data.t import get_t_eng_block_review_test_cases
from test.data.tmm import get_tmm_eng_block_review_test_cases
from test.helpers import assert_series_equal, parametrize


@parametrize(
    ("series_fixture", "expected_fixture", "test_case_loader"),
    [
        param(
            "acopopb_eng_ocr_fuse_clean_validate",
            "acopopb_eng_ocr_fuse_clean_validate_review",
            get_acopopb_eng_block_review_test_cases,
            id="acopopb-eng",
        ),
        param(
            "acoptc_eng_ocr_fuse_clean_validate",
            "acoptc_eng_ocr_fuse_clean_validate_review",
            get_acoptc_eng_block_review_test_cases,
            id="acoptc-eng",
        ),
        param(
            "kob_eng_ocr_fuse_clean_validate",
            "kob_eng_ocr_fuse_clean_validate_review",
            get_kob_eng_block_review_test_cases,
            id="kob-eng-ocr",
        ),
        param(
            "kob_eng_clean",
            "kob_eng_clean_review",
            get_kob_eng_block_review_test_cases,
            id="kob-eng-srt",
        ),
        param(
            "mlamd_eng_fuse_clean_validate",
            "mlamd_eng_fuse_clean_validate_review",
            get_mlamd_eng_block_review_test_cases,
            id="mlamd-eng-ocr",
        ),
        param(
            "mnt_eng_fuse_clean_validate",
            "mnt_eng_fuse_clean_validate_review",
            get_mnt_eng_block_review_test_cases,
            id="mnt-eng",
        ),
        param(
            "t_eng_fuse_clean_validate",
            "t_eng_fuse_clean_validate_review",
            get_t_eng_block_review_test_cases,
            id="t-eng-ocr",
        ),
        param(
            "tmm_eng_ocr_fuse_clean_validate",
            "tmm_eng_ocr_fuse_clean_validate_review",
            get_tmm_eng_block_review_test_cases,
            id="tmm-eng",
        ),
    ],
)
def test_get_eng_block_reviewed(
    request: FixtureRequest,
    series_fixture: str,
    expected_fixture: str,
    test_case_loader: Callable[[], list[TestCase]],
):
    """Test get_eng_block_reviewed against expected block-reviewed outputs.

    Arguments:
        request: pytest request for fixture lookup
        series_fixture: fixture name for input series
        expected_fixture: fixture name for expected output series
        test_case_loader: test case loader for the review path
    """
    provider = Mock(spec=LLMProvider)
    processor = get_eng_block_reviewer(
        test_cases=test_case_loader(),
        provider=provider,
    )
    expected = request.getfixturevalue(expected_fixture)
    output = get_eng_block_reviewed(
        request.getfixturevalue(series_fixture),
        processor=processor,
    )

    assert len(output) == len(expected)
    assert_series_equal(output, expected)
    provider.chat_completion.assert_not_called()
