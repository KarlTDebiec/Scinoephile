#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MNT."""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import TypedDict, Unpack

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


class LoadTestCasesKwargs(TypedDict, total=False):
    """Keyword arguments for load_test_cases_from_json."""

    pass


__all__ = [
    "mnt_eng_lens",
    "mnt_eng_tesseract",
    "mnt_zho_hans_lens",
    "mnt_zho_hans_paddle",
    "mnt_zho_hant",
    "mnt_zho_hant_lens",
    "mnt_zho_hant_paddle",
    "get_mnt_eng_ocr_fusion_test_cases",
    "get_mnt_eng_proofreading_test_cases",
    "get_mnt_zho_hans_ocr_fusion_test_cases",
    "get_mnt_zho_hans_proofreading_test_cases",
    "get_mnt_zho_hant_ocr_fusion_test_cases",
    "get_mnt_zho_hant_proofreading_test_cases",
    "get_mnt_zho_hant_simplify_proofreading_test_cases",
    "mnt_eng_fuse",
    "mnt_eng_fuse_clean",
    "mnt_eng_fuse_clean_validate",
    "mnt_eng_fuse_clean_validate_proofread",
    "mnt_eng_fuse_clean_validate_proofread_flatten",
    "mnt_eng_image",
    "mnt_eng_image_path",
    "mnt_zho_hans_fuse",
    "mnt_zho_hans_fuse_clean",
    "mnt_zho_hans_fuse_clean_validate",
    "mnt_zho_hans_fuse_clean_validate_proofread",
    "mnt_zho_hans_fuse_clean_validate_proofread_flatten",
    "mnt_zho_hans_image",
    "mnt_zho_hans_image_path",
    "mnt_zho_hant_fuse",
    "mnt_zho_hant_fuse_clean",
    "mnt_zho_hant_fuse_clean_validate",
    "mnt_zho_hant_fuse_clean_validate_proofread",
    "mnt_zho_hant_fuse_clean_validate_proofread_flatten",
    "mnt_zho_hant_fuse_clean_validate_proofread_flatten_simplify",
    "mnt_zho_hant_fuse_clean_validate_proofread_flatten_simplify_proofread",
    "mnt_zho_hant_image",
    "mnt_zho_hant_image_path",
]

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"


@pytest.fixture
def mnt_eng_lens() -> Series:
    """MNT English subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "eng_lens.srt")


@pytest.fixture
def mnt_eng_tesseract() -> Series:
    """MNT English subtitles OCRed using Tesseract."""
    return Series.load(input_dir / "eng_tesseract.srt")


@pytest.fixture
def mnt_zho_hans_lens() -> Series:
    """MNT 简体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hans_lens.srt")


@pytest.fixture
def mnt_zho_hans_paddle() -> Series:
    """MNT 简体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hans_paddle.srt")


@pytest.fixture
def mnt_zho_hant() -> Series:
    """MNT 繁体中文 series."""
    return Series.load(input_dir / "zho-Hant.srt")


@pytest.fixture
def mnt_zho_hant_lens() -> Series:
    """MNT 繁体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hant_lens.srt")


@pytest.fixture
def mnt_zho_hant_paddle() -> Series:
    """MNT 繁体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hant_paddle.srt")


@cache
def get_mnt_eng_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = EngOcrFusionPrompt,
    **kwargs: Unpack[LoadTestCasesKwargs],
) -> list[TestCase]:
    """Get MNT English OCR fusion test cases.

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
def get_mnt_eng_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = EngProofreadingPrompt,
    **kwargs: Unpack[LoadTestCasesKwargs],
) -> list[TestCase]:
    """Get MNT English proofreading test cases.

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
def get_mnt_zho_hans_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = ZhoHansOcrFusionPrompt,
    **kwargs: Unpack[LoadTestCasesKwargs],
) -> list[TestCase]:
    """Get MNT 简体中文 OCR fusion test cases.

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
def get_mnt_zho_hans_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = ZhoHansProofreadingPrompt,
    **kwargs: Unpack[LoadTestCasesKwargs],
) -> list[TestCase]:
    """Get MNT 简体中文 proofreading test cases.

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
def get_mnt_zho_hant_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = ZhoHantOcrFusionPrompt,
    **kwargs: Unpack[LoadTestCasesKwargs],
) -> list[TestCase]:
    """Get MNT 繁体中文 OCR fusion test cases.

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
def get_mnt_zho_hant_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = ZhoHantProofreadingPrompt,
    **kwargs: Unpack[LoadTestCasesKwargs],
) -> list[TestCase]:
    """Get MNT 繁体中文 proofreading test cases.

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
def get_mnt_zho_hant_simplify_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = ZhoHansProofreadingPrompt,
    **kwargs: Unpack[LoadTestCasesKwargs],
) -> list[TestCase]:
    """Get MNT 繁体中文 simplification proofreading test cases.

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


@pytest.fixture
def mnt_eng_fuse() -> Series:
    """MNT English fused subtitles."""
    return Series.load(output_dir / "eng_fuse.srt")


@pytest.fixture
def mnt_eng_fuse_clean() -> Series:
    """MNT English fused and cleaned subtitles."""
    return Series.load(output_dir / "eng_fuse_clean.srt")


@pytest.fixture
def mnt_eng_fuse_clean_validate() -> Series:
    """MNT English fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "eng_fuse_clean_validate.srt")


@pytest.fixture
def mnt_eng_fuse_clean_validate_proofread() -> Series:
    """MNT English fused, cleaned, validated, and proofread subtitles."""
    return Series.load(output_dir / "eng_fuse_clean_validate_proofread.srt")


@pytest.fixture
def mnt_eng_fuse_clean_validate_proofread_flatten() -> Series:
    """MNT English fused, cleaned, validated, proofread, and flattened subtitles."""
    return Series.load(output_dir / "eng_fuse_clean_validate_proofread_flatten.srt")


@pytest.fixture
def mnt_eng_image() -> ImageSeries:
    """MNT English image subtitles."""
    return ImageSeries.load(output_dir / "eng_image", encoding="utf-8")


@pytest.fixture
def mnt_eng_image_path() -> Path:
    """Path to MNT English image subtitles."""
    return output_dir / "eng_image"


@pytest.fixture
def mnt_zho_hans_fuse() -> Series:
    """MNT 简体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse.srt")


@pytest.fixture
def mnt_zho_hans_fuse_clean() -> Series:
    """MNT 简体中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_clean.srt")


@pytest.fixture
def mnt_zho_hans_fuse_clean_validate() -> Series:
    """MNT 简体中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_clean_validate.srt")


@pytest.fixture
def mnt_zho_hans_fuse_clean_validate_proofread() -> Series:
    """MNT 简体中文 fused, cleaned, validated, and proofread subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_clean_validate_proofread.srt")


@pytest.fixture
def mnt_zho_hans_fuse_clean_validate_proofread_flatten() -> Series:
    """MNT 简体中文 fused, cleaned, validated, proofread, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hans_fuse_clean_validate_proofread_flatten.srt"
    )


@pytest.fixture
def mnt_zho_hans_image() -> ImageSeries:
    """MNT 简体中文 image subtitles."""
    return ImageSeries.load(output_dir / "zho-Hans_image", encoding="utf-8")


@pytest.fixture
def mnt_zho_hans_image_path() -> Path:
    """Path to MNT 简体中文 image subtitles."""
    return output_dir / "zho-Hans_image"


@pytest.fixture
def mnt_zho_hant_fuse() -> Series:
    """MNT 繁体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse.srt")


@pytest.fixture
def mnt_zho_hant_fuse_clean() -> Series:
    """MNT 繁体中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean.srt")


@pytest.fixture
def mnt_zho_hant_fuse_clean_validate() -> Series:
    """MNT 繁体中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean_validate.srt")


@pytest.fixture
def mnt_zho_hant_fuse_clean_validate_proofread() -> Series:
    """MNT 繁体中文 fused, cleaned, validated, and proofread subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean_validate_proofread.srt")


@pytest.fixture
def mnt_zho_hant_fuse_clean_validate_proofread_flatten() -> Series:
    """MNT 繁体中文 fused, cleaned, validated, proofread, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_fuse_clean_validate_proofread_flatten.srt"
    )


@pytest.fixture
def mnt_zho_hant_fuse_clean_validate_proofread_flatten_simplify() -> Series:
    """MNT 繁体中文 fused/cleaned/validated/proofread/flattened/simplified subtitles."""
    return Series.load(
        output_dir / "zho-Hant_fuse_clean_validate_proofread_flatten_simplify.srt"
    )


@pytest.fixture
def mnt_zho_hant_fuse_clean_validate_proofread_flatten_simplify_proofread() -> Series:
    """MNT 繁体中文 simplified/proofread fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_fuse_clean_validate_proofread_flatten_simplify_proofread.srt"
    )


@pytest.fixture
def mnt_zho_hant_image() -> ImageSeries:
    """MNT 繁体中文 image subtitles."""
    return ImageSeries.load(output_dir / "zho-Hant_image", encoding="utf-8")


@pytest.fixture
def mnt_zho_hant_image_path() -> Path:
    """Path to MNT 繁体中文 image subtitles."""
    return output_dir / "zho-Hant_image"
