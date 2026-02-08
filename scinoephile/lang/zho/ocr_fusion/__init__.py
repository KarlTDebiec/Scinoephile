#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 中文 OCR fusion."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.subtitles import Series
from scinoephile.llms.base import TestCase
from scinoephile.llms.dual_single.ocr_fusion import (
    OcrFusionManager,
    OcrFusionProcessor,
)
from scinoephile.testing.default_test_cases import (
    ZHO_HANS_OCR_FUSION_JSON_PATHS,
    ZHO_HANT_OCR_FUSION_JSON_PATHS,
    load_default_test_cases_from_repo_data,
)

from .prompts import ZhoHansOcrFusionPrompt, ZhoHantOcrFusionPrompt

__all__ = [
    "ZhoHansOcrFusionPrompt",
    "ZhoHantOcrFusionPrompt",
    "ZhoOcrFusionProcessKwargs",
    "ZhoOcrFusionProcessorKwargs",
    "get_zho_ocr_fuser",
    "get_zho_ocr_fused",
]


class ZhoOcrFusionProcessKwargs(TypedDict, total=False):
    """Keyword arguments for OcrFusionProcessor.process."""

    stop_at_idx: int | None


class ZhoOcrFusionProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for OcrFusionProcessor initialization."""

    test_case_path: Path | None
    auto_verify: bool


def get_zho_ocr_fused(
    lens: Series,
    paddle: Series,
    processor: OcrFusionProcessor | None = None,
    **kwargs: Unpack[ZhoOcrFusionProcessKwargs],
) -> Series:
    """Get 中文 series fused from Google Lens and PaddleOCR outputs.

    Arguments:
        lens: subtitles OCRed using Google Lens
        paddle: subtitles OCRed using PaddleOCR
        processor: OcrFusionProcessor to use
        **kwargs: additional keyword arguments for OcrFusionProcessor.process
    Returns:
        Fused series
    """
    if processor is None:
        processor = get_zho_ocr_fuser()
    return processor.process(lens, paddle, **kwargs)


def get_zho_ocr_fuser(
    prompt_cls: type[ZhoHansOcrFusionPrompt] = ZhoHansOcrFusionPrompt,
    test_cases: list[TestCase] | None = None,
    **kwargs: Unpack[ZhoOcrFusionProcessorKwargs],
) -> OcrFusionProcessor:
    """Get an OcrFusionProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        **kwargs: additional keyword arguments for OcrFusionProcessor
    Returns:
        OcrFusionProcessor with provided configuration
    """
    if test_cases is None:
        if prompt_cls is ZhoHantOcrFusionPrompt:
            test_cases = load_default_test_cases_from_repo_data(
                OcrFusionManager,
                prompt_cls,
                ZHO_HANT_OCR_FUSION_JSON_PATHS,
            )
        else:
            test_cases = load_default_test_cases_from_repo_data(
                OcrFusionManager,
                prompt_cls,
                ZHO_HANS_OCR_FUSION_JSON_PATHS,
            )
    return OcrFusionProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        **kwargs,
    )
