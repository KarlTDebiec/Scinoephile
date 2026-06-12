#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.get_zho_ocr_fused."""

from __future__ import annotations

from unittest.mock import Mock

from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.zho.cleaning import get_zho_cleaned
from scinoephile.lang.zho.ocr_fusion import (
    OcrFusionPromptZhoHant,
    get_zho_ocr_fused,
    get_zho_ocr_fuser,
)
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_converted
from scinoephile.llms.dual_1_to_1.ocr_fusion import OcrFusionProcessor
from test.helpers import assert_series_equal


def _test_get_zho_ocr_fused(
    lens: Series,
    paddle: Series,
    expected: Series,
    processor: OcrFusionProcessor | None = None,
):
    """Test get_zho_ocr_fused.

    Arguments:
        lens: subtitles OCRed using Google Lens
        paddle: subtitles OCRed using PaddleOCR
        expected: expected output series
        processor: processor to use
    """
    output = get_zho_ocr_fused(lens, paddle, processor=processor)

    assert len(output) == len(expected)
    assert_series_equal(output, expected)


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


def test_get_zho_ocr_fused_kob(
    kob_zho_hant_ocr_lens: Series,
    kob_zho_hant_ocr_paddle: Series,
    kob_zho_hant_ocr_fuse: Series,
):
    """Test get_zho_ocr_fused with KOB standard Chinese subtitles.

    Arguments:
        kob_zho_hant_ocr_lens: KOB standard Chinese subtitles OCRed using
          Google Lens fixture
        kob_zho_hant_ocr_paddle: KOB standard Chinese subtitles OCRed using
          PaddleOCR fixture
        kob_zho_hant_ocr_fuse: Expected fused KOB standard Chinese subtitles fixture
    """
    lens = get_zho_cleaned(kob_zho_hant_ocr_lens, remove_empty=False)
    lens = get_zho_converted(lens, config=OpenCCConfig.s2t)
    paddle = get_zho_cleaned(kob_zho_hant_ocr_paddle, remove_empty=False)
    paddle = get_zho_converted(paddle, config=OpenCCConfig.s2t)
    _test_get_zho_ocr_fused(
        lens,
        paddle,
        kob_zho_hant_ocr_fuse,
        get_zho_ocr_fuser(prompt_cls=OcrFusionPromptZhoHant),
    )


def test_get_zho_ocr_fused_mlamd(
    mlamd_zho_hans_ocr_lens: Series,
    mlamd_zho_hans_ocr_paddle: Series,
    mlamd_zho_hans_fuse: Series,
):
    """Test get_zho_ocr_fused with MLAMD standard Chinese subtitles.

    Arguments:
        mlamd_zho_hans_ocr_lens: MLAMD standard Chinese subtitles OCRed using
          Google Lens fixture
        mlamd_zho_hans_ocr_paddle: MLAMD standard Chinese subtitles OCRed using
          PaddleOCR fixture
        mlamd_zho_hans_fuse: Expected fused MLAMD standard Chinese subtitles fixture
    """
    lens = get_zho_cleaned(mlamd_zho_hans_ocr_lens, remove_empty=False)
    lens = get_zho_converted(lens)
    paddle = get_zho_cleaned(mlamd_zho_hans_ocr_paddle, remove_empty=False)
    paddle = get_zho_converted(paddle)
    _test_get_zho_ocr_fused(lens, paddle, mlamd_zho_hans_fuse)


def test_get_zho_ocr_fused_mnt(
    mnt_zho_hans_ocr_lens: Series,
    mnt_zho_hans_ocr_paddle: Series,
    mnt_zho_hans_fuse: Series,
):
    """Test get_zho_ocr_fused with MNT standard Chinese subtitles.

    Arguments:
        mnt_zho_hans_ocr_lens: MNT standard Chinese subtitles OCRed using
          Google Lens fixture
        mnt_zho_hans_ocr_paddle: MNT standard Chinese subtitles OCRed using
          PaddleOCR fixture
        mnt_zho_hans_fuse: Expected fused MNT standard Chinese subtitles fixture
    """
    lens = get_zho_cleaned(mnt_zho_hans_ocr_lens, remove_empty=False)
    lens = get_zho_converted(lens)
    paddle = get_zho_cleaned(mnt_zho_hans_ocr_paddle, remove_empty=False)
    paddle = get_zho_converted(paddle)
    _test_get_zho_ocr_fused(lens, paddle, mnt_zho_hans_fuse)


def test_get_zho_ocr_fused_t(
    t_zho_hans_ocr_lens: Series,
    t_zho_hans_ocr_paddle: Series,
    t_zho_hans_fuse: Series,
):
    """Test get_zho_ocr_fused with T standard Chinese subtitles.

    Arguments:
        t_zho_hans_ocr_lens: T standard Chinese subtitles OCRed using Google
          Lens fixture
        t_zho_hans_ocr_paddle: T standard Chinese subtitles OCRed using
          PaddleOCR fixture
        t_zho_hans_fuse: Expected fused T standard Chinese subtitles fixture
    """
    lens = get_zho_cleaned(t_zho_hans_ocr_lens, remove_empty=False)
    lens = get_zho_converted(lens)
    paddle = get_zho_cleaned(t_zho_hans_ocr_paddle, remove_empty=False)
    paddle = get_zho_converted(paddle)
    _test_get_zho_ocr_fused(lens, paddle, t_zho_hans_fuse)
