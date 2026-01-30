#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for T."""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

import pytest

from scinoephile.core.subtitles import Series
from scinoephile.core.testing import test_data_root
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.eng.ocr_fusion import EngOcrFusionPrompt
from scinoephile.lang.eng.proofreading import EngProofreadingPrompt
from scinoephile.lang.zho.ocr_fusion import (
    ZhoHansOcrFusionPrompt,
    ZhoHantOcrFusionPrompt,
)
from scinoephile.lang.zho.proofreading import (
    ZhoHansProofreadingPrompt,
    ZhoHantProofreadingPrompt,
)
from scinoephile.llms.base import TestCase, load_test_cases_from_json
from scinoephile.llms.dual_single import DualSinglePrompt
from scinoephile.llms.dual_single.ocr_fusion import OcrFusionManager
from scinoephile.llms.mono_block import MonoBlockManager, MonoBlockPrompt

__all__ = [
    "t_eng",
    "t_eng_lens",
    "t_eng_tesseract",
    "t_zho_hans",
    "t_zho_hans_lens",
    "t_zho_hans_paddle",
    "t_zho_hant",
    "t_zho_hant_lens",
    "t_zho_hant_paddle",
    "get_t_eng_ocr_fusion_test_cases",
    "get_t_eng_proofreading_test_cases",
    "get_t_zho_hans_ocr_fusion_test_cases",
    "get_t_zho_hans_proofreading_test_cases",
    "get_t_zho_hant_ocr_fusion_test_cases",
    "get_t_zho_hant_proofreading_test_cases",
    "get_t_zho_hant_simplify_proofreading_test_cases",
    "t_eng_fuse",
    "t_eng_fuse_clean",
    "t_eng_fuse_clean_validate",
    "t_eng_fuse_clean_validate_proofread",
    "t_eng_fuse_clean_validate_proofread_flatten",
    "t_eng_image",
    "t_zho_hans_eng",
    "t_zho_hans_fuse",
    "t_zho_hans_fuse_clean",
    "t_zho_hans_fuse_clean_validate",
    "t_zho_hans_fuse_clean_validate_proofread",
    "t_zho_hans_fuse_clean_validate_proofread_flatten",
    "t_zho_hans_fuse_clean_validate_proofread_flatten_romanize",
    "t_zho_hans_image",
    "t_zho_hant_fuse",
    "t_zho_hant_fuse_clean",
    "t_zho_hant_fuse_clean_validate",
    "t_zho_hant_fuse_clean_validate_proofread",
    "t_zho_hant_fuse_clean_validate_proofread_flatten",
    "t_zho_hant_fuse_clean_validate_proofread_flatten_simplify",
    "t_zho_hant_fuse_clean_validate_proofread_flatten_simplify_proofread",
    "t_zho_hant_image",
]

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"


@pytest.fixture
def t_eng() -> Series:
    """T English series."""
    return Series.load(input_dir / "eng.srt")


@pytest.fixture
def t_eng_lens() -> Series:
    """T English subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "eng_lens.srt")


@pytest.fixture
def t_eng_tesseract() -> Series:
    """T English subtitles OCRed using Tesseract."""
    return Series.load(input_dir / "eng_tesseract.srt")


@pytest.fixture
def t_zho_hans() -> Series:
    """T 简体中文 series."""
    return Series.load(input_dir / "zho-Hans.srt")


@pytest.fixture
def t_zho_hans_lens() -> Series:
    """T 简体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hans_lens.srt")


@pytest.fixture
def t_zho_hans_paddle() -> Series:
    """T 简体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hans_paddle.srt")


@pytest.fixture
def t_zho_hant() -> Series:
    """T 繁体中文 series."""
    return Series.load(input_dir / "zho-Hant.srt")


@pytest.fixture
def t_zho_hant_lens() -> Series:
    """T 繁体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hant_lens.srt")


@pytest.fixture
def t_zho_hant_paddle() -> Series:
    """T 繁体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hant_paddle.srt")


@cache
def get_t_eng_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = EngProofreadingPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get T English proofreading test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        English proofreading test cases
    """
    path = title_root / "lang" / "eng" / "proofreading.json"
    return load_test_cases_from_json(
        path, MonoBlockManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_t_zho_hans_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = ZhoHansProofreadingPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get T 简体中文 proofreading test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "zho" / "proofreading" / "zho-Hans.json"
    return load_test_cases_from_json(
        path, MonoBlockManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_t_zho_hant_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = ZhoHantProofreadingPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get T 繁体中文 proofreading test cases.

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


@cache
def get_t_zho_hant_simplify_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = ZhoHansProofreadingPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get T 繁体中文 simplification proofreading test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "zho" / "proofreading" / "zho-Hant_simplify.json"
    return load_test_cases_from_json(
        path, MonoBlockManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_t_eng_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = EngOcrFusionPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get T English OCR fusion test cases.

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
def get_t_zho_hans_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = ZhoHansOcrFusionPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get T 简体中文 OCR fusion test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "zho" / "ocr_fusion" / "zho-Hans.json"
    return load_test_cases_from_json(
        path, OcrFusionManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_t_zho_hant_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = ZhoHantOcrFusionPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get T 繁体中文 OCR fusion test cases.

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


@pytest.fixture
def t_eng_fuse() -> Series:
    """T English fused subtitles."""
    return Series.load(output_dir / "eng_fuse.srt")


@pytest.fixture
def t_eng_fuse_clean() -> Series:
    """T English fused and cleaned subtitles."""
    return Series.load(output_dir / "eng_fuse_clean.srt")


@pytest.fixture
def t_eng_fuse_clean_validate() -> Series:
    """T English fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "eng_fuse_clean_validate.srt")


@pytest.fixture
def t_eng_fuse_clean_validate_proofread() -> Series:
    """T English fused, cleaned, validated, and proofread subtitles."""
    return Series.load(output_dir / "eng_fuse_clean_validate_proofread.srt")


@pytest.fixture
def t_eng_fuse_clean_validate_proofread_flatten() -> Series:
    """T English fused, cleaned, validated, proofread, and flattened subtitles."""
    return Series.load(output_dir / "eng_fuse_clean_validate_proofread_flatten.srt")


@pytest.fixture
def t_eng_image() -> ImageSeries:
    """T English image subtitles."""
    return ImageSeries.load(output_dir / "eng_image", encoding="utf-8")


@pytest.fixture
def t_zho_hans_eng() -> Series:
    """T Bilingual 简体中文 and English series."""
    return Series.load(output_dir / "zho-Hans_eng.srt")


@pytest.fixture
def t_zho_hans_fuse() -> Series:
    """T 简体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse.srt")


@pytest.fixture
def t_zho_hans_fuse_clean() -> Series:
    """T 简体中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_clean.srt")


@pytest.fixture
def t_zho_hans_fuse_clean_validate() -> Series:
    """T 简体中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_clean_validate.srt")


@pytest.fixture
def t_zho_hans_fuse_clean_validate_proofread() -> Series:
    """T 简体中文 fused, cleaned, validated, and proofread subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_clean_validate_proofread.srt")


@pytest.fixture
def t_zho_hans_fuse_clean_validate_proofread_flatten() -> Series:
    """T 简体中文 fused, cleaned, validated, proofread, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hans_fuse_clean_validate_proofread_flatten.srt"
    )


@pytest.fixture
def t_zho_hans_fuse_clean_validate_proofread_flatten_romanize() -> Series:
    """T 简体中文 fused/cleaned/validated/proofread/flattened romanized subtitles."""
    return Series.load(
        output_dir / "zho-Hans_fuse_clean_validate_proofread_flatten_romanize.srt"
    )


@pytest.fixture
def t_zho_hans_image() -> ImageSeries:
    """T 简体中文 image subtitles."""
    return ImageSeries.load(output_dir / "zho-Hans_image", encoding="utf-8")


@pytest.fixture
def t_zho_hant_fuse() -> Series:
    """T 繁体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse.srt")


@pytest.fixture
def t_zho_hant_fuse_clean() -> Series:
    """T 繁体中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean.srt")


@pytest.fixture
def t_zho_hant_fuse_clean_validate() -> Series:
    """T 繁体中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean_validate.srt")


@pytest.fixture
def t_zho_hant_fuse_clean_validate_proofread() -> Series:
    """T 繁体中文 fused, cleaned, validated, and proofread subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean_validate_proofread.srt")


@pytest.fixture
def t_zho_hant_fuse_clean_validate_proofread_flatten() -> Series:
    """T 繁体中文 fused, cleaned, validated, proofread, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_fuse_clean_validate_proofread_flatten.srt"
    )


@pytest.fixture
def t_zho_hant_fuse_clean_validate_proofread_flatten_simplify() -> Series:
    """T 繁体中文 fused/cleaned/validated/proofread/flattened/simplified subtitles."""
    return Series.load(
        output_dir / "zho-Hant_fuse_clean_validate_proofread_flatten_simplify.srt"
    )


@pytest.fixture
def t_zho_hant_fuse_clean_validate_proofread_flatten_simplify_proofread() -> Series:
    """T 繁体中文 simplified/proofread fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_fuse_clean_validate_proofread_flatten_simplify_proofread.srt"
    )


@pytest.fixture
def t_zho_hant_image() -> ImageSeries:
    """T 繁体中文 image subtitles."""
    return ImageSeries.load(output_dir / "zho-Hant_image", encoding="utf-8")
