#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for KOB."""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

import pytest

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.core.subtitles import Series
from scinoephile.core.testing import test_data_root
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.eng.ocr_fusion import EngOcrFusionPrompt
from scinoephile.lang.eng.proofreading import EngProofreadingPrompt
from scinoephile.lang.zho.ocr_fusion import ZhoHantOcrFusionPrompt
from scinoephile.lang.zho.proofreading import ZhoHantProofreadingPrompt
from scinoephile.llms.base import TestCase, load_test_cases_from_json
from scinoephile.llms.dual_single import DualSinglePrompt
from scinoephile.llms.dual_single.ocr_fusion import OcrFusionManager
from scinoephile.llms.mono_block import MonoBlockManager, MonoBlockPrompt

__all__ = [
    "kob_eng",
    "kob_eng_lens",
    "kob_eng_tesseract",
    "kob_yue_hans",
    "kob_yue_hant",
    "kob_zho_hant_lens",
    "kob_zho_hant_paddle",
    "kob_eng_clean",
    "kob_eng_clean_flatten",
    "kob_eng_fuse",
    "kob_eng_fuse_clean",
    "kob_eng_fuse_clean_validate",
    "kob_eng_fuse_clean_validate_proofread",
    "kob_eng_fuse_clean_validate_proofread_flatten",
    "kob_eng_image",
    "kob_eng_image_path",
    "kob_yue_hans_audio",
    "kob_yue_hans_audio_path",
    "kob_yue_hans_clean",
    "kob_yue_hans_clean_flatten",
    "kob_yue_hans_eng",
    "kob_yue_hans_proofread",
    "kob_yue_hant_simplify",
    "kob_zho_hant_fuse",
    "kob_zho_hant_fuse_clean",
    "kob_zho_hant_fuse_clean_validate",
    "kob_zho_hant_fuse_clean_validate_proofread",
    "kob_zho_hant_fuse_clean_validate_proofread_flatten",
    "kob_zho_hant_image",
    "kob_zho_hant_image_path",
    "get_kob_eng_ocr_fusion_test_cases",
    "get_kob_eng_proofreading_test_cases",
    "get_kob_zho_hant_ocr_fusion_test_cases",
    "get_kob_zho_hant_proofreading_test_cases",
]

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"


# English (SRT)
@pytest.fixture
def kob_eng() -> Series:
    """KOB English subtitles."""
    return Series.load(input_dir / "eng.srt")


# English (OCR)
@pytest.fixture
def kob_eng_lens() -> Series:
    """KOB English subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "eng_lens.srt")


@pytest.fixture
def kob_eng_tesseract() -> Series:
    """KOB English subtitles OCRed using Tesseract."""
    return Series.load(input_dir / "eng_tesseract.srt")


# ???? (SRT)
@pytest.fixture
def kob_yue_hans() -> Series:
    """KOB ???? subtitles."""
    return Series.load(input_dir / "yue-Hans.srt")


@pytest.fixture
def kob_yue_hant() -> Series:
    """KOB ???? subtitles."""
    return Series.load(input_dir / "yue-Hant.srt")


# ???? (OCR)
@pytest.fixture
def kob_zho_hant_lens() -> Series:
    """KOB ???? subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hant_lens.srt")


@pytest.fixture
def kob_zho_hant_paddle() -> Series:
    """KOB ???? subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hant_paddle.srt")


# English (Output)
@pytest.fixture
def kob_eng_image_path() -> Path:
    """Path to KOB English image subtitles."""
    return output_dir / "eng_image"


@pytest.fixture
def kob_eng_image() -> ImageSeries:
    """KOB English image subtitles."""
    return ImageSeries.load(output_dir / "eng_image", encoding="utf-8")


@pytest.fixture
def kob_eng_fuse() -> Series:
    """KOB English fused subtitles."""
    return Series.load(output_dir / "eng_fuse.srt")


@pytest.fixture
def kob_eng_fuse_clean() -> Series:
    """KOB English fused and cleaned subtitles."""
    return Series.load(output_dir / "eng_fuse_clean.srt")


@pytest.fixture
def kob_eng_fuse_clean_validate() -> Series:
    """KOB English fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "eng_fuse_clean_validate.srt")


@pytest.fixture
def kob_eng_fuse_clean_validate_proofread() -> Series:
    """KOB English fused, cleaned, validated, and proofread subtitles."""
    return Series.load(output_dir / "eng_fuse_clean_validate_proofread.srt")


@pytest.fixture
def kob_eng_fuse_clean_validate_proofread_flatten() -> Series:
    """KOB English fused, cleaned, validated, proofread, and flattened subtitles."""
    return Series.load(output_dir / "eng_fuse_clean_validate_proofread_flatten.srt")


@pytest.fixture
def kob_eng_clean() -> Series:
    """KOB English cleaned subtitles."""
    return Series.load(output_dir / "eng_clean.srt")


@pytest.fixture
def kob_eng_clean_flatten() -> Series:
    """KOB English cleaned and flattened subtitles."""
    return Series.load(output_dir / "eng_clean_flatten.srt")


# ???? (Output)
@pytest.fixture
def kob_yue_hans_audio_path() -> Path:
    """Path to KOB ???? audio subtitles."""
    return output_dir / "yue-Hans_audio"


@pytest.fixture
def kob_yue_hans_audio() -> AudioSeries:
    """KOB ???? audio subtitles."""
    return AudioSeries.load(output_dir / "yue-Hans_audio")


@pytest.fixture
def kob_yue_hans_clean() -> Series:
    """KOB ???? cleaned subtitles."""
    return Series.load(output_dir / "yue-Hans_clean.srt")


@pytest.fixture
def kob_yue_hans_clean_flatten() -> Series:
    """KOB ???? cleaned and flattened subtitles."""
    return Series.load(output_dir / "yue-Hans_clean_flatten.srt")


@pytest.fixture
def kob_yue_hans_eng() -> Series:
    """KOB Bilingual ???? and English subtitles."""
    return Series.load(output_dir / "yue-Hans_eng.srt")


@pytest.fixture
def kob_yue_hans_proofread() -> Series:
    """KOB ???? proofread subtitles."""
    return Series.load(output_dir / "yue-Hans_proofread.srt")


@pytest.fixture
def kob_yue_hant_simplify() -> Series:
    """KOB ???? simplified subtitles."""
    return Series.load(output_dir / "yue-Hant_simplify.srt")


# ???? (OCR output)
@pytest.fixture
def kob_zho_hant_image_path() -> Path:
    """Path to KOB ???? image subtitles."""
    return output_dir / "zho-Hant_image"


@pytest.fixture
def kob_zho_hant_image() -> ImageSeries:
    """KOB ???? image subtitles."""
    return ImageSeries.load(output_dir / "zho-Hant_image", encoding="utf-8")


@pytest.fixture
def kob_zho_hant_fuse() -> Series:
    """KOB ???? fused subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse.srt")


@pytest.fixture
def kob_zho_hant_fuse_clean() -> Series:
    """KOB ???? fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean.srt")


@pytest.fixture
def kob_zho_hant_fuse_clean_validate() -> Series:
    """KOB ???? fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean_validate.srt")


@pytest.fixture
def kob_zho_hant_fuse_clean_validate_proofread() -> Series:
    """KOB ???? fused, cleaned, validated, and proofread subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean_validate_proofread.srt")


@pytest.fixture
def kob_zho_hant_fuse_clean_validate_proofread_flatten() -> Series:
    """KOB ???? fused, cleaned, validated, proofread, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_fuse_clean_validate_proofread_flatten.srt"
    )


@cache
def get_kob_eng_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = EngOcrFusionPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get KOB English OCR fusion test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "eng" / "ocr_fusion.json"
    return load_test_cases_from_json(
        path, OcrFusionManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_kob_zho_hant_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = ZhoHantOcrFusionPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get KOB ?? OCR fusion test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "zho" / "ocr_fusion" / "zho-Hant.json"
    return load_test_cases_from_json(
        path, OcrFusionManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_kob_eng_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = EngProofreadingPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get KOB English proofreading test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "eng" / "proofreading.json"
    return load_test_cases_from_json(
        path, MonoBlockManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_kob_zho_hant_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = ZhoHantProofreadingPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get KOB ?? proofreading test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "zho" / "proofreading" / "zho-Hant.json"
    return load_test_cases_from_json(
        path, MonoBlockManager, prompt_cls=prompt_cls, **kwargs
    )
