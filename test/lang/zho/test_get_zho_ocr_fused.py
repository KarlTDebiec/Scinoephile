#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.get_zho_ocr_fused."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.zho.cleaning import get_zho_cleaned
from scinoephile.lang.zho.ocr_fusion import (
    OcrFusionPromptZhoHant,
    get_zho_ocr_fused,
    get_zho_ocr_fuser,
)
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_converted
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
    processor = get_zho_ocr_fuser(provider=provider)

    output = get_zho_ocr_fused(lens, paddle, processor=processor)

    assert output.events[0].text == "嗯达摩\n达摩祖师果然厉害"
    provider.chat_completion.assert_not_called()


@pytest.mark.parametrize(
    (
        "lens_fixture",
        "paddle_fixture",
        "expected_fixture",
        "convert",
        "use_traditional_prompt",
    ),
    [
        (
            "kob_zho_hant_ocr_lens",
            "kob_zho_hant_ocr_paddle",
            "kob_zho_hant_ocr_fuse",
            OpenCCConfig.s2t,
            True,
        ),
        (
            "mlamd_zho_hans_ocr_lens",
            "mlamd_zho_hans_ocr_paddle",
            "mlamd_zho_hans_fuse",
            None,
            False,
        ),
        (
            "mnt_zho_hans_ocr_lens",
            "mnt_zho_hans_ocr_paddle",
            "mnt_zho_hans_fuse",
            None,
            False,
        ),
        (
            "t_zho_hans_ocr_lens",
            "t_zho_hans_ocr_paddle",
            "t_zho_hans_fuse",
            None,
            False,
        ),
    ],
)
def test_get_zho_ocr_fused(
    request: pytest.FixtureRequest,
    lens_fixture: str,
    paddle_fixture: str,
    expected_fixture: str,
    convert: OpenCCConfig | None,
    use_traditional_prompt: bool,
):
    """Test get_zho_ocr_fused against expected fused outputs.

    Arguments:
        request: pytest request for fixture lookup
        lens_fixture: fixture name for Google Lens OCR subtitles
        paddle_fixture: fixture name for PaddleOCR subtitles
        expected_fixture: fixture name for expected output series
        convert: OpenCC conversion to apply before fusing
        use_traditional_prompt: whether to use the traditional prompt fuser
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

    processor = None
    if use_traditional_prompt:
        processor = get_zho_ocr_fuser(prompt_cls=OcrFusionPromptZhoHant)
    expected = request.getfixturevalue(expected_fixture)
    output = get_zho_ocr_fused(
        lens,
        paddle,
        processor=processor,
    )

    assert len(output) == len(expected)
    assert_series_equal(output, expected)
