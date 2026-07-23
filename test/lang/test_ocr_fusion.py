#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of language-aware OCR fusion."""

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import Mock

from pytest import FixtureRequest, param

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.lang.ocr_fusion import get_ocr_fuser
from scinoephile.workflows.clean import clean_series
from scinoephile.workflows.ocr_fusion import fuse_ocr_series
from test.data.acopopb import (
    get_acopopb_eng_ocr_fusion_test_cases,
    get_acopopb_yue_hans_ocr_fusion_test_cases,
    get_acopopb_yue_hant_ocr_fusion_test_cases,
    get_acopopb_zho_hans_ocr_fusion_test_cases,
    get_acopopb_zho_hant_ocr_fusion_test_cases,
)
from test.data.acoptc import (
    get_acoptc_eng_ocr_fusion_test_cases,
    get_acoptc_yue_hans_ocr_fusion_test_cases,
    get_acoptc_yue_hant_ocr_fusion_test_cases,
    get_acoptc_zho_hans_ocr_fusion_test_cases,
    get_acoptc_zho_hant_ocr_fusion_test_cases,
)
from test.data.kob import (
    get_kob_eng_ocr_fusion_test_cases,
    get_kob_zho_hant_ocr_fusion_test_cases,
)
from test.data.mlamd import (
    get_mlamd_eng_ocr_fusion_test_cases,
    get_mlamd_zho_hans_ocr_fusion_test_cases,
    get_mlamd_zho_hant_ocr_fusion_test_cases,
)
from test.data.mnt import (
    get_mnt_eng_ocr_fusion_test_cases,
    get_mnt_zho_hans_ocr_fusion_test_cases,
    get_mnt_zho_hant_ocr_fusion_test_cases,
)
from test.data.t import (
    get_t_eng_ocr_fusion_test_cases,
    get_t_zho_hans_ocr_fusion_test_cases,
    get_t_zho_hant_ocr_fusion_test_cases,
)
from test.data.tmm import (
    get_tmm_eng_ocr_fusion_test_cases,
    get_tmm_yue_hans_ocr_fusion_test_cases,
    get_tmm_yue_hant_ocr_fusion_test_cases,
    get_tmm_zho_hans_ocr_fusion_test_cases,
    get_tmm_zho_hant_ocr_fusion_test_cases,
)
from test.helpers import assert_series_equal, parametrize


@parametrize(
    (
        "lens_fixture",
        "secondary_fixture",
        "expected_fixture",
        "language",
        "test_case_loader",
    ),
    [
        param(
            "acopopb_eng_ocr_lens",
            "acopopb_eng_ocr_tesseract",
            "acopopb_eng_ocr_fuse",
            Language.eng,
            get_acopopb_eng_ocr_fusion_test_cases,
            id="acopopb-eng",
        ),
        param(
            "acopopb_yue_hans_ocr_lens",
            "acopopb_yue_hans_ocr_paddle",
            "acopopb_yue_hans_ocr_fuse",
            Language.yue_hans,
            get_acopopb_yue_hans_ocr_fusion_test_cases,
            id="acopopb-yue-hans",
        ),
        param(
            "acopopb_yue_hant_ocr_lens",
            "acopopb_yue_hant_ocr_paddle",
            "acopopb_yue_hant_ocr_fuse",
            Language.yue_hant,
            get_acopopb_yue_hant_ocr_fusion_test_cases,
            id="acopopb-yue-hant",
        ),
        param(
            "acopopb_zho_hans_ocr_lens",
            "acopopb_zho_hans_ocr_paddle",
            "acopopb_zho_hans_ocr_fuse",
            Language.zho_hans,
            get_acopopb_zho_hans_ocr_fusion_test_cases,
            id="acopopb-zho-hans",
        ),
        param(
            "acopopb_zho_hant_ocr_lens",
            "acopopb_zho_hant_ocr_paddle",
            "acopopb_zho_hant_ocr_fuse",
            Language.zho_hant,
            get_acopopb_zho_hant_ocr_fusion_test_cases,
            id="acopopb-zho-hant",
        ),
        param(
            "acoptc_eng_ocr_lens",
            "acoptc_eng_ocr_tesseract",
            "acoptc_eng_ocr_fuse",
            Language.eng,
            get_acoptc_eng_ocr_fusion_test_cases,
            id="acoptc-eng",
        ),
        param(
            "acoptc_yue_hans_ocr_lens",
            "acoptc_yue_hans_ocr_paddle",
            "acoptc_yue_hans_ocr_fuse",
            Language.yue_hans,
            get_acoptc_yue_hans_ocr_fusion_test_cases,
            id="acoptc-yue-hans",
        ),
        param(
            "acoptc_yue_hant_ocr_lens",
            "acoptc_yue_hant_ocr_paddle",
            "acoptc_yue_hant_ocr_fuse",
            Language.yue_hant,
            get_acoptc_yue_hant_ocr_fusion_test_cases,
            id="acoptc-yue-hant",
        ),
        param(
            "acoptc_zho_hans_ocr_lens",
            "acoptc_zho_hans_ocr_paddle",
            "acoptc_zho_hans_ocr_fuse",
            Language.zho_hans,
            get_acoptc_zho_hans_ocr_fusion_test_cases,
            id="acoptc-zho-hans",
        ),
        param(
            "acoptc_zho_hant_ocr_lens",
            "acoptc_zho_hant_ocr_paddle",
            "acoptc_zho_hant_ocr_fuse",
            Language.zho_hant,
            get_acoptc_zho_hant_ocr_fusion_test_cases,
            id="acoptc-zho-hant",
        ),
        param(
            "kob_eng_ocr_lens",
            "kob_eng_ocr_tesseract",
            "kob_eng_ocr_fuse",
            Language.eng,
            get_kob_eng_ocr_fusion_test_cases,
            id="kob-eng",
        ),
        param(
            "kob_zho_hant_ocr_lens",
            "kob_zho_hant_ocr_paddle",
            "kob_zho_hant_ocr_fuse",
            Language.zho_hant,
            get_kob_zho_hant_ocr_fusion_test_cases,
            id="kob-zho-hant",
        ),
        param(
            "mlamd_eng_ocr_lens",
            "mlamd_eng_ocr_tesseract",
            "mlamd_eng_fuse",
            Language.eng,
            get_mlamd_eng_ocr_fusion_test_cases,
            id="mlamd-eng",
        ),
        param(
            "mlamd_zho_hans_ocr_lens",
            "mlamd_zho_hans_ocr_paddle",
            "mlamd_zho_hans_fuse",
            Language.zho_hans,
            get_mlamd_zho_hans_ocr_fusion_test_cases,
            id="mlamd-zho-hans",
        ),
        param(
            "mlamd_zho_hant_ocr_lens",
            "mlamd_zho_hant_ocr_paddle",
            "mlamd_zho_hant_fuse",
            Language.zho_hant,
            get_mlamd_zho_hant_ocr_fusion_test_cases,
            id="mlamd-zho-hant",
        ),
        param(
            "mnt_eng_ocr_lens",
            "mnt_eng_ocr_tesseract",
            "mnt_eng_fuse",
            Language.eng,
            get_mnt_eng_ocr_fusion_test_cases,
            id="mnt-eng",
        ),
        param(
            "mnt_zho_hans_ocr_lens",
            "mnt_zho_hans_ocr_paddle",
            "mnt_zho_hans_fuse",
            Language.zho_hans,
            get_mnt_zho_hans_ocr_fusion_test_cases,
            id="mnt-zho-hans",
        ),
        param(
            "mnt_zho_hant_ocr_lens",
            "mnt_zho_hant_ocr_paddle",
            "mnt_zho_hant_fuse",
            Language.zho_hant,
            get_mnt_zho_hant_ocr_fusion_test_cases,
            id="mnt-zho-hant",
        ),
        param(
            "t_eng_ocr_lens",
            "t_eng_ocr_tesseract",
            "t_eng_fuse",
            Language.eng,
            get_t_eng_ocr_fusion_test_cases,
            id="t-eng",
        ),
        param(
            "t_zho_hans_ocr_lens",
            "t_zho_hans_ocr_paddle",
            "t_zho_hans_fuse",
            Language.zho_hans,
            get_t_zho_hans_ocr_fusion_test_cases,
            id="t-zho-hans",
        ),
        param(
            "t_zho_hant_ocr_lens",
            "t_zho_hant_ocr_paddle",
            "t_zho_hant_fuse",
            Language.zho_hant,
            get_t_zho_hant_ocr_fusion_test_cases,
            id="t-zho-hant",
        ),
        param(
            "tmm_eng_ocr_lens",
            "tmm_eng_ocr_tesseract",
            "tmm_eng_ocr_fuse",
            Language.eng,
            get_tmm_eng_ocr_fusion_test_cases,
            id="tmm-eng",
        ),
        param(
            "tmm_yue_hans_ocr_lens",
            "tmm_yue_hans_ocr_paddle",
            "tmm_yue_hans_ocr_fuse",
            Language.yue_hans,
            get_tmm_yue_hans_ocr_fusion_test_cases,
            id="tmm-yue-hans",
        ),
        param(
            "tmm_yue_hant_ocr_lens",
            "tmm_yue_hant_ocr_paddle",
            "tmm_yue_hant_ocr_fuse",
            Language.yue_hant,
            get_tmm_yue_hant_ocr_fusion_test_cases,
            id="tmm-yue-hant",
        ),
        param(
            "tmm_zho_hans_ocr_lens",
            "tmm_zho_hans_ocr_paddle",
            "tmm_zho_hans_ocr_fuse",
            Language.zho_hans,
            get_tmm_zho_hans_ocr_fusion_test_cases,
            id="tmm-zho-hans",
        ),
        param(
            "tmm_zho_hant_ocr_lens",
            "tmm_zho_hant_ocr_paddle",
            "tmm_zho_hant_ocr_fuse",
            Language.zho_hant,
            get_tmm_zho_hant_ocr_fusion_test_cases,
            id="tmm-zho-hant",
        ),
    ],
)
def test_fuse_ocr_series(
    request: FixtureRequest,
    lens_fixture: str,
    secondary_fixture: str,
    expected_fixture: str,
    language: Language,
    test_case_loader: Callable[[], list[TestCase]],
):
    """Test OCR fusion against expected outputs for all supported languages.

    Arguments:
        request: pytest request for fixture lookup
        lens_fixture: fixture name for Google Lens OCR subtitles
        secondary_fixture: fixture name for Tesseract or PaddleOCR subtitles
        expected_fixture: fixture name for expected output series
        language: OCR fusion language
        test_case_loader: loader for OCR fusion test cases
    """
    lens = request.getfixturevalue(lens_fixture)
    secondary = request.getfixturevalue(secondary_fixture)
    lens = clean_series(lens, language=language, remove_empty=False)
    secondary = clean_series(secondary, language=language, remove_empty=False)

    provider = Mock(spec=LLMProvider)
    processor = get_ocr_fuser(
        language,
        test_cases=test_case_loader(),
        provider=provider,
    )
    expected = request.getfixturevalue(expected_fixture)
    output = fuse_ocr_series(
        lens,
        secondary,
        language=language,
        fuser=processor,
    )

    assert len(output) == len(expected)
    assert_series_equal(output, expected)
    provider.chat_completion.assert_not_called()
