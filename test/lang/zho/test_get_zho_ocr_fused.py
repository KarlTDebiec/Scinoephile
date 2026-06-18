#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.get_zho_ocr_fused."""

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import Mock

import pytest

from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.zho.cleaning import get_zho_cleaned
from scinoephile.lang.zho.ocr_fusion import (
    OcrFusionPromptZhoHans,
    OcrFusionPromptZhoHant,
    get_zho_ocr_fused,
    get_zho_ocr_fuser,
)
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_converted
from test.data.kob import get_kob_zho_hant_ocr_fusion_test_cases
from test.data.mlamd import get_mlamd_zho_hans_ocr_fusion_test_cases
from test.data.mnt import get_mnt_zho_hans_ocr_fusion_test_cases
from test.data.t import get_t_zho_hans_ocr_fusion_test_cases
from test.helpers import assert_series_equal


def test_get_zho_ocr_fused_treats_newline_forms_as_identical():
    """Test OCR fusion skips queries when texts only differ by newline form."""
    lens = Series(
        [
            Subtitle(
                start=0,
                end=1000,
                text="嗯达摩\n达摩祖师果然厉害",
            )
        ]
    )
    paddle = Series(
        [
            Subtitle(
                start=0,
                end=1000,
                text="嗯达摩\\N达摩祖师果然厉害",
            )
        ]
    )
    provider = Mock(spec=LLMProvider)
    processor = get_zho_ocr_fuser(test_cases=[], provider=provider)

    output = get_zho_ocr_fused(lens, paddle, processor=processor)

    assert output.events[0].text == "嗯达摩\n达摩祖师果然厉害"
    provider.chat_completion.assert_not_called()


@pytest.mark.parametrize(
    (
        "lens_fixture",
        "paddle_fixture",
        "expected_fixture",
        "convert",
        "prompt_cls",
        "test_case_loader",
    ),
    [
        (
            "kob_zho_hant_ocr_lens",
            "kob_zho_hant_ocr_paddle",
            "kob_zho_hant_ocr_fuse",
            OpenCCConfig.s2t,
            OcrFusionPromptZhoHant,
            get_kob_zho_hant_ocr_fusion_test_cases,
        ),
        (
            "mlamd_zho_hans_ocr_lens",
            "mlamd_zho_hans_ocr_paddle",
            "mlamd_zho_hans_fuse",
            None,
            OcrFusionPromptZhoHans,
            get_mlamd_zho_hans_ocr_fusion_test_cases,
        ),
        (
            "mnt_zho_hans_ocr_lens",
            "mnt_zho_hans_ocr_paddle",
            "mnt_zho_hans_fuse",
            None,
            OcrFusionPromptZhoHans,
            get_mnt_zho_hans_ocr_fusion_test_cases,
        ),
        (
            "t_zho_hans_ocr_lens",
            "t_zho_hans_ocr_paddle",
            "t_zho_hans_fuse",
            None,
            OcrFusionPromptZhoHans,
            get_t_zho_hans_ocr_fusion_test_cases,
        ),
    ],
)
def test_get_zho_ocr_fused(
    request: pytest.FixtureRequest,
    lens_fixture: str,
    paddle_fixture: str,
    expected_fixture: str,
    convert: OpenCCConfig | None,
    prompt_cls: type[OcrFusionPromptZhoHans],
    test_case_loader: Callable[[], list[TestCase]],
):
    """Test get_zho_ocr_fused against expected fused outputs.

    Arguments:
        request: pytest request for fixture lookup
        lens_fixture: fixture name for Google Lens OCR subtitles
        paddle_fixture: fixture name for PaddleOCR subtitles
        expected_fixture: fixture name for expected output series
        convert: OpenCC conversion to apply before fusing
        prompt_cls: OCR fusion prompt class
        test_case_loader: loader for OCR fusion test cases
    """
    lens = get_zho_cleaned(request.getfixturevalue(lens_fixture), remove_empty=False)
    paddle = get_zho_cleaned(
        request.getfixturevalue(paddle_fixture), remove_empty=False
    )
    if convert is None:
        lens = get_zho_converted(lens)
        paddle = get_zho_converted(paddle)
    else:
        lens = get_zho_converted(lens, config=convert)
        paddle = get_zho_converted(paddle, config=convert)

    provider = Mock(spec=LLMProvider)
    processor = get_zho_ocr_fuser(
        prompt_cls=prompt_cls,
        test_cases=test_case_loader(),
        provider=provider,
    )
    expected = request.getfixturevalue(expected_fixture)
    if convert is None:
        expected = get_zho_converted(expected)
    else:
        expected = get_zho_converted(expected, config=convert)
    output = get_zho_ocr_fused(
        lens,
        paddle,
        processor=processor,
    )

    assert len(output) == len(expected)
    assert_series_equal(output, expected)
    provider.chat_completion.assert_not_called()
