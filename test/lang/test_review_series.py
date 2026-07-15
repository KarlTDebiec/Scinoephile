#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of review workflow."""

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import Mock

from pytest import FixtureRequest, param

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.lang.eng.review import ReviewPromptEng
from scinoephile.lang.review.standard import get_reviewer
from scinoephile.lang.yue.review import ReviewPromptYueHans, ReviewPromptYueHant
from scinoephile.lang.zho.review import ReviewPromptZhoHans, ReviewPromptZhoHant
from scinoephile.llms.review import ReviewPrompt
from scinoephile.workflows.review import review_series
from test.data.acopopb import (
    get_acopopb_eng_review_test_cases,
    get_acopopb_yue_hans_review_test_cases,
    get_acopopb_yue_hant_review_test_cases,
    get_acopopb_yue_hant_simplify_review_test_cases,
    get_acopopb_zho_hans_review_test_cases,
    get_acopopb_zho_hant_review_test_cases,
    get_acopopb_zho_hant_simplify_review_test_cases,
)
from test.data.acoptc import (
    get_acoptc_eng_review_test_cases,
    get_acoptc_yue_hans_review_test_cases,
    get_acoptc_yue_hant_review_test_cases,
    get_acoptc_yue_hant_simplify_review_test_cases,
    get_acoptc_zho_hans_review_test_cases,
    get_acoptc_zho_hant_review_test_cases,
    get_acoptc_zho_hant_simplify_review_test_cases,
)
from test.data.kob import (
    get_kob_eng_review_test_cases,
    get_kob_yue_hans_review_test_cases,
    get_kob_yue_hant_review_test_cases,
    get_kob_yue_hant_simplify_review_test_cases,
    get_kob_zho_hant_review_test_cases,
    get_kob_zho_hant_simplify_review_test_cases,
)
from test.data.mlamd import (
    get_mlamd_eng_review_test_cases,
    get_mlamd_zho_hans_review_test_cases,
    get_mlamd_zho_hant_review_test_cases,
    get_mlamd_zho_hant_simplify_review_test_cases,
)
from test.data.mnt import (
    get_mnt_eng_review_test_cases,
    get_mnt_zho_hans_review_test_cases,
    get_mnt_zho_hant_review_test_cases,
    get_mnt_zho_hant_simplify_review_test_cases,
)
from test.data.t import (
    get_t_eng_review_test_cases,
    get_t_zho_hans_review_test_cases,
    get_t_zho_hant_review_test_cases,
    get_t_zho_hant_simplify_review_test_cases,
)
from test.data.tmm import (
    get_tmm_eng_review_test_cases,
    get_tmm_yue_hans_review_test_cases,
    get_tmm_yue_hant_review_test_cases,
    get_tmm_yue_hant_simplify_review_test_cases,
    get_tmm_zho_hans_review_test_cases,
    get_tmm_zho_hant_review_test_cases,
    get_tmm_zho_hant_simplify_review_test_cases,
)
from test.helpers import assert_series_equal, parametrize


@parametrize(
    (
        "series_fixture",
        "expected_fixture",
        "test_case_loader",
        "language",
        "prompt",
    ),
    [
        param(
            "acopopb_eng_ocr_fuse_clean_validate",
            "acopopb_eng_ocr_fuse_clean_validate_review",
            get_acopopb_eng_review_test_cases,
            Language.eng,
            ReviewPromptEng,
            id="acopopb-eng",
        ),
        param(
            "acopopb_yue_hans_ocr_fuse_clean_validate",
            "acopopb_yue_hans_ocr_fuse_clean_validate_review",
            get_acopopb_yue_hans_review_test_cases,
            Language.yue_hans,
            ReviewPromptYueHans,
            id="acopopb-yue-hans",
        ),
        param(
            "acopopb_yue_hant_ocr_fuse_clean_validate",
            "acopopb_yue_hant_ocr_fuse_clean_validate_review",
            get_acopopb_yue_hant_review_test_cases,
            Language.yue_hant,
            ReviewPromptYueHant,
            id="acopopb-yue-hant",
        ),
        param(
            "acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify",
            "acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            get_acopopb_yue_hant_simplify_review_test_cases,
            Language.yue_hans,
            ReviewPromptYueHans,
            id="acopopb-yue-hant-simplify",
        ),
        param(
            "acopopb_zho_hans_ocr_fuse_clean_validate",
            "acopopb_zho_hans_ocr_fuse_clean_validate_review",
            get_acopopb_zho_hans_review_test_cases,
            Language.zho_hans,
            ReviewPromptZhoHans,
            id="acopopb-zho-hans",
        ),
        param(
            "acopopb_zho_hant_ocr_fuse_clean_validate",
            "acopopb_zho_hant_ocr_fuse_clean_validate_review",
            get_acopopb_zho_hant_review_test_cases,
            Language.zho_hant,
            ReviewPromptZhoHant,
            id="acopopb-zho-hant",
        ),
        param(
            "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify",
            "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            get_acopopb_zho_hant_simplify_review_test_cases,
            Language.zho_hans,
            ReviewPromptZhoHans,
            id="acopopb-zho-hant-simplify",
        ),
        param(
            "acoptc_eng_ocr_fuse_clean_validate",
            "acoptc_eng_ocr_fuse_clean_validate_review",
            get_acoptc_eng_review_test_cases,
            Language.eng,
            ReviewPromptEng,
            id="acoptc-eng",
        ),
        param(
            "acoptc_yue_hans_ocr_fuse_clean_validate",
            "acoptc_yue_hans_ocr_fuse_clean_validate_review",
            get_acoptc_yue_hans_review_test_cases,
            Language.yue_hans,
            ReviewPromptYueHans,
            id="acoptc-yue-hans",
        ),
        param(
            "acoptc_yue_hant_ocr_fuse_clean_validate",
            "acoptc_yue_hant_ocr_fuse_clean_validate_review",
            get_acoptc_yue_hant_review_test_cases,
            Language.yue_hant,
            ReviewPromptYueHant,
            id="acoptc-yue-hant",
        ),
        param(
            "acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify",
            "acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            get_acoptc_yue_hant_simplify_review_test_cases,
            Language.yue_hans,
            ReviewPromptYueHans,
            id="acoptc-yue-hant-simplify",
        ),
        param(
            "acoptc_zho_hans_ocr_fuse_clean_validate",
            "acoptc_zho_hans_ocr_fuse_clean_validate_review",
            get_acoptc_zho_hans_review_test_cases,
            Language.zho_hans,
            ReviewPromptZhoHans,
            id="acoptc-zho-hans",
        ),
        param(
            "acoptc_zho_hant_ocr_fuse_clean_validate",
            "acoptc_zho_hant_ocr_fuse_clean_validate_review",
            get_acoptc_zho_hant_review_test_cases,
            Language.zho_hant,
            ReviewPromptZhoHant,
            id="acoptc-zho-hant",
        ),
        param(
            "acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify",
            "acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            get_acoptc_zho_hant_simplify_review_test_cases,
            Language.zho_hans,
            ReviewPromptZhoHans,
            id="acoptc-zho-hant-simplify",
        ),
        param(
            "kob_eng_ocr_fuse_clean_validate",
            "kob_eng_ocr_fuse_clean_validate_review",
            get_kob_eng_review_test_cases,
            Language.eng,
            ReviewPromptEng,
            id="kob-eng-ocr",
        ),
        param(
            "kob_eng_clean",
            "kob_eng_clean_review",
            get_kob_eng_review_test_cases,
            Language.eng,
            ReviewPromptEng,
            id="kob-eng-srt",
        ),
        param(
            "kob_zho_hant_ocr_fuse_clean_validate",
            "kob_zho_hant_ocr_fuse_clean_validate_review",
            get_kob_zho_hant_review_test_cases,
            Language.zho_hant,
            ReviewPromptZhoHant,
            id="kob-zho-hant-ocr",
        ),
        param(
            "kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify",
            "kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            get_kob_zho_hant_simplify_review_test_cases,
            Language.zho_hans,
            ReviewPromptZhoHans,
            id="kob-zho-hant-simplify-ocr",
        ),
        param(
            "kob_yue_hans_clean",
            "kob_yue_hans_clean_review",
            get_kob_yue_hans_review_test_cases,
            Language.yue_hans,
            ReviewPromptYueHans,
            id="kob-yue-hans-srt",
        ),
        param(
            "kob_yue_hant_clean",
            "kob_yue_hant_clean_review",
            get_kob_yue_hant_review_test_cases,
            Language.yue_hant,
            ReviewPromptYueHant,
            id="kob-yue-hant-srt",
        ),
        param(
            "kob_yue_hant_clean_review_flatten_timewarp_simplify",
            "kob_yue_hant_clean_review_flatten_timewarp_simplify_review",
            get_kob_yue_hant_simplify_review_test_cases,
            Language.yue_hans,
            ReviewPromptYueHans,
            id="kob-yue-hant-srt-simplify",
        ),
        param(
            "mlamd_eng_fuse_clean_validate",
            "mlamd_eng_fuse_clean_validate_review",
            get_mlamd_eng_review_test_cases,
            Language.eng,
            ReviewPromptEng,
            id="mlamd-eng-ocr",
        ),
        param(
            "mlamd_zho_hans_fuse_clean_validate",
            "mlamd_zho_hans_fuse_clean_validate_review",
            get_mlamd_zho_hans_review_test_cases,
            Language.zho_hans,
            ReviewPromptZhoHans,
            id="mlamd-zho-hans",
        ),
        param(
            "mlamd_zho_hant_fuse_clean_validate",
            "mlamd_zho_hant_fuse_clean_validate_review",
            get_mlamd_zho_hant_review_test_cases,
            Language.zho_hant,
            ReviewPromptZhoHant,
            id="mlamd-zho-hant",
        ),
        param(
            "mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify",
            "mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            get_mlamd_zho_hant_simplify_review_test_cases,
            Language.zho_hans,
            ReviewPromptZhoHans,
            id="mlamd-zho-hant-simplify",
        ),
        param(
            "mnt_eng_fuse_clean_validate",
            "mnt_eng_fuse_clean_validate_review",
            get_mnt_eng_review_test_cases,
            Language.eng,
            ReviewPromptEng,
            id="mnt-eng",
        ),
        param(
            "mnt_zho_hans_fuse_clean_validate",
            "mnt_zho_hans_fuse_clean_validate_review",
            get_mnt_zho_hans_review_test_cases,
            Language.zho_hans,
            ReviewPromptZhoHans,
            id="mnt-zho-hans",
        ),
        param(
            "mnt_zho_hant_fuse_clean_validate",
            "mnt_zho_hant_fuse_clean_validate_review",
            get_mnt_zho_hant_review_test_cases,
            Language.zho_hant,
            ReviewPromptZhoHant,
            id="mnt-zho-hant",
        ),
        param(
            "mnt_zho_hant_fuse_clean_validate_review_flatten_simplify",
            "mnt_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            get_mnt_zho_hant_simplify_review_test_cases,
            Language.zho_hans,
            ReviewPromptZhoHans,
            id="mnt-zho-hant-simplify",
        ),
        param(
            "t_eng_fuse_clean_validate",
            "t_eng_fuse_clean_validate_review",
            get_t_eng_review_test_cases,
            Language.eng,
            ReviewPromptEng,
            id="t-eng-ocr",
        ),
        param(
            "t_zho_hans_fuse_clean_validate",
            "t_zho_hans_fuse_clean_validate_review",
            get_t_zho_hans_review_test_cases,
            Language.zho_hans,
            ReviewPromptZhoHans,
            id="t-zho-hans",
        ),
        param(
            "t_zho_hant_fuse_clean_validate",
            "t_zho_hant_fuse_clean_validate_review",
            get_t_zho_hant_review_test_cases,
            Language.zho_hant,
            ReviewPromptZhoHant,
            id="t-zho-hant",
        ),
        param(
            "t_zho_hant_fuse_clean_validate_review_flatten_simplify",
            "t_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            get_t_zho_hant_simplify_review_test_cases,
            Language.zho_hans,
            ReviewPromptZhoHans,
            id="t-zho-hant-simplify",
        ),
        param(
            "tmm_eng_ocr_fuse_clean_validate",
            "tmm_eng_ocr_fuse_clean_validate_review",
            get_tmm_eng_review_test_cases,
            Language.eng,
            ReviewPromptEng,
            id="tmm-eng",
        ),
        param(
            "tmm_yue_hans_ocr_fuse_clean_validate",
            "tmm_yue_hans_ocr_fuse_clean_validate_review",
            get_tmm_yue_hans_review_test_cases,
            Language.yue_hans,
            ReviewPromptYueHans,
            id="tmm-yue-hans",
        ),
        param(
            "tmm_yue_hant_ocr_fuse_clean_validate",
            "tmm_yue_hant_ocr_fuse_clean_validate_review",
            get_tmm_yue_hant_review_test_cases,
            Language.yue_hant,
            ReviewPromptYueHant,
            id="tmm-yue-hant",
        ),
        param(
            "tmm_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify",
            "tmm_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            get_tmm_yue_hant_simplify_review_test_cases,
            Language.yue_hans,
            ReviewPromptYueHans,
            id="tmm-yue-hant-simplify",
        ),
        param(
            "tmm_zho_hans_ocr_fuse_clean_validate",
            "tmm_zho_hans_ocr_fuse_clean_validate_review",
            get_tmm_zho_hans_review_test_cases,
            Language.zho_hans,
            ReviewPromptZhoHans,
            id="tmm-zho-hans",
        ),
        param(
            "tmm_zho_hant_ocr_fuse_clean_validate",
            "tmm_zho_hant_ocr_fuse_clean_validate_review",
            get_tmm_zho_hant_review_test_cases,
            Language.zho_hant,
            ReviewPromptZhoHant,
            id="tmm-zho-hant",
        ),
        param(
            "tmm_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify",
            "tmm_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            get_tmm_zho_hant_simplify_review_test_cases,
            Language.zho_hans,
            ReviewPromptZhoHans,
            id="tmm-zho-hant-simplify",
        ),
    ],
)
def test_review_series(
    request: FixtureRequest,
    series_fixture: str,
    expected_fixture: str,
    test_case_loader: Callable[[], list[TestCase]],
    language: Language,
    prompt: ReviewPrompt,
):
    """Test series review against expected outputs.

    Arguments:
        request: pytest request for fixture lookup
        series_fixture: fixture name for input series
        expected_fixture: fixture name for expected output series
        test_case_loader: test case loader for the review path
        language: language to review
        prompt: prompt for the review path
    """
    provider = Mock(spec=LLMProvider)
    reviewer = get_reviewer(
        language,
        prompt=prompt,
        test_cases=test_case_loader(),
        provider=provider,
    )
    expected = request.getfixturevalue(expected_fixture)
    output = review_series(
        request.getfixturevalue(series_fixture),
        language=language,
        reviewer=reviewer,
    )

    assert len(output) == len(expected)
    assert_series_equal(output, expected)
    provider.chat_completion.assert_not_called()
