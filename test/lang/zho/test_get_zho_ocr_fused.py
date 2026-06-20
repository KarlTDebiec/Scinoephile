#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.get_zho_ocr_fused."""

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import Mock

from pytest import FixtureRequest, param, parametrize

from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.zho.cleaning import get_zho_cleaned
from scinoephile.lang.zho.ocr_fusion import (
    OcrFusionPromptZhoHans,
    OcrFusionPromptZhoHant,
    get_zho_ocr_fused,
    get_zho_ocr_fuser,
)
from test.data.acopopb import (
    get_acopopb_zho_hans_ocr_fusion_test_cases,
    get_acopopb_zho_hant_ocr_fusion_test_cases,
)
from test.data.acoptc import (
    get_acoptc_zho_hans_ocr_fusion_test_cases,
    get_acoptc_zho_hant_ocr_fusion_test_cases,
)
from test.data.kob import get_kob_zho_hant_ocr_fusion_test_cases
from test.data.mlamd import (
    get_mlamd_zho_hans_ocr_fusion_test_cases,
    get_mlamd_zho_hant_ocr_fusion_test_cases,
)
from test.data.mnt import (
    get_mnt_zho_hans_ocr_fusion_test_cases,
    get_mnt_zho_hant_ocr_fusion_test_cases,
)
from test.data.t import (
    get_t_zho_hans_ocr_fusion_test_cases,
    get_t_zho_hant_ocr_fusion_test_cases,
)
from test.data.tmm import (
    get_tmm_zho_hans_ocr_fusion_test_cases,
    get_tmm_zho_hant_ocr_fusion_test_cases,
)
from test.helpers import assert_series_equal


@parametrize(
    ("lens_text", "paddle_text", "expected_text"),
    [
        param(
            "嗯达摩\n达摩祖师果然厉害",
            "嗯达摩\\N达摩祖师果然厉害",
            "嗯达摩\n达摩祖师果然厉害",
            id="newline-form",
        ),
    ],
)
def test_get_zho_ocr_fused_treats_newline_forms_as_identical(
    lens_text: str,
    paddle_text: str,
    expected_text: str,
):
    """Test OCR fusion skips queries when texts only differ by newline form."""
    lens = Series(
        [
            Subtitle(
                start=0,
                end=1000,
                text=lens_text,
            )
        ]
    )
    paddle = Series(
        [
            Subtitle(
                start=0,
                end=1000,
                text=paddle_text,
            )
        ]
    )
    provider = Mock(spec=LLMProvider)
    processor = get_zho_ocr_fuser(test_cases=[], provider=provider)

    output = get_zho_ocr_fused(lens, paddle, processor=processor)

    assert output.events[0].text == expected_text
    provider.chat_completion.assert_not_called()


@parametrize(
    (
        "lens_fixture",
        "paddle_fixture",
        "expected_fixture",
        "prompt_cls",
        "test_case_loader",
    ),
    [
        param(
            "acopopb_zho_hans_ocr_lens",
            "acopopb_zho_hans_ocr_paddle",
            "acopopb_zho_hans_ocr_fuse",
            OcrFusionPromptZhoHans,
            get_acopopb_zho_hans_ocr_fusion_test_cases,
            id="acopopb-zho-hans",
        ),
        param(
            "acopopb_zho_hant_ocr_lens",
            "acopopb_zho_hant_ocr_paddle",
            "acopopb_zho_hant_ocr_fuse",
            OcrFusionPromptZhoHant,
            get_acopopb_zho_hant_ocr_fusion_test_cases,
            id="acopopb-zho-hant",
        ),
        param(
            "acoptc_zho_hans_ocr_lens",
            "acoptc_zho_hans_ocr_paddle",
            "acoptc_zho_hans_ocr_fuse",
            OcrFusionPromptZhoHans,
            get_acoptc_zho_hans_ocr_fusion_test_cases,
            id="acoptc-zho-hans",
        ),
        param(
            "acoptc_zho_hant_ocr_lens",
            "acoptc_zho_hant_ocr_paddle",
            "acoptc_zho_hant_ocr_fuse",
            OcrFusionPromptZhoHant,
            get_acoptc_zho_hant_ocr_fusion_test_cases,
            id="acoptc-zho-hant",
        ),
        param(
            "kob_zho_hant_ocr_lens",
            "kob_zho_hant_ocr_paddle",
            "kob_zho_hant_ocr_fuse",
            OcrFusionPromptZhoHant,
            get_kob_zho_hant_ocr_fusion_test_cases,
            id="kob-zho-hant",
        ),
        param(
            "mlamd_zho_hans_ocr_lens",
            "mlamd_zho_hans_ocr_paddle",
            "mlamd_zho_hans_fuse",
            OcrFusionPromptZhoHans,
            get_mlamd_zho_hans_ocr_fusion_test_cases,
            id="mlamd-zho-hans",
        ),
        param(
            "mlamd_zho_hant_ocr_lens",
            "mlamd_zho_hant_ocr_paddle",
            "mlamd_zho_hant_fuse",
            OcrFusionPromptZhoHant,
            get_mlamd_zho_hant_ocr_fusion_test_cases,
            id="mlamd-zho-hant",
        ),
        param(
            "mnt_zho_hans_ocr_lens",
            "mnt_zho_hans_ocr_paddle",
            "mnt_zho_hans_fuse",
            OcrFusionPromptZhoHans,
            get_mnt_zho_hans_ocr_fusion_test_cases,
            id="mnt-zho-hans",
        ),
        param(
            "mnt_zho_hant_ocr_lens",
            "mnt_zho_hant_ocr_paddle",
            "mnt_zho_hant_fuse",
            OcrFusionPromptZhoHant,
            get_mnt_zho_hant_ocr_fusion_test_cases,
            id="mnt-zho-hant",
        ),
        param(
            "t_zho_hans_ocr_lens",
            "t_zho_hans_ocr_paddle",
            "t_zho_hans_fuse",
            OcrFusionPromptZhoHans,
            get_t_zho_hans_ocr_fusion_test_cases,
            id="t-zho-hans",
        ),
        param(
            "t_zho_hant_ocr_lens",
            "t_zho_hant_ocr_paddle",
            "t_zho_hant_fuse",
            OcrFusionPromptZhoHant,
            get_t_zho_hant_ocr_fusion_test_cases,
            id="t-zho-hant",
        ),
        param(
            "tmm_zho_hans_ocr_lens",
            "tmm_zho_hans_ocr_paddle",
            "tmm_zho_hans_ocr_fuse",
            OcrFusionPromptZhoHans,
            get_tmm_zho_hans_ocr_fusion_test_cases,
            id="tmm-zho-hans",
        ),
        param(
            "tmm_zho_hant_ocr_lens",
            "tmm_zho_hant_ocr_paddle",
            "tmm_zho_hant_ocr_fuse",
            OcrFusionPromptZhoHant,
            get_tmm_zho_hant_ocr_fusion_test_cases,
            id="tmm-zho-hant",
        ),
    ],
)
def test_get_zho_ocr_fused(
    request: FixtureRequest,
    lens_fixture: str,
    paddle_fixture: str,
    expected_fixture: str,
    prompt_cls: type[OcrFusionPromptZhoHans],
    test_case_loader: Callable[[], list[TestCase]],
):
    """Test get_zho_ocr_fused against expected fused outputs.

    Arguments:
        request: pytest request for fixture lookup
        lens_fixture: fixture name for Google Lens OCR subtitles
        paddle_fixture: fixture name for PaddleOCR subtitles
        expected_fixture: fixture name for expected output series
        prompt_cls: OCR fusion prompt class
        test_case_loader: loader for OCR fusion test cases
    """
    lens = get_zho_cleaned(request.getfixturevalue(lens_fixture), remove_empty=False)
    paddle = get_zho_cleaned(
        request.getfixturevalue(paddle_fixture),
        remove_empty=False,
    )
    provider = Mock(spec=LLMProvider)
    processor = get_zho_ocr_fuser(
        prompt_cls=prompt_cls,
        test_cases=test_case_loader(),
        provider=provider,
    )
    expected = request.getfixturevalue(expected_fixture)
    output = get_zho_ocr_fused(
        lens,
        paddle,
        processor=processor,
    )

    assert len(output) == len(expected)
    assert_series_equal(output, expected)
    provider.chat_completion.assert_not_called()
