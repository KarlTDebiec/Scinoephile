#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English OCR fusion."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.llms import TestCase
from scinoephile.core.subtitles import Series
from scinoephile.llms.default_test_cases import (
    ENG_OCR_FUSION_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_single.ocr_fusion import OcrFusionManager, OcrFusionProcessor

from .prompts import EngOcrFusionPrompt

__all__ = [
    "EngOcrFusionPrompt",
    "EngOcrFusionProcessKwargs",
    "EngOcrFusionProcessorKwargs",
    "get_eng_ocr_fuser",
    "get_eng_ocr_fused",
]


class EngOcrFusionProcessKwargs(TypedDict, total=False):
    """Keyword arguments for OcrFusionProcessor.process."""

    stop_at_idx: int | None


class EngOcrFusionProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for OcrFusionProcessor initialization."""

    test_case_path: Path | None
    auto_verify: bool


def get_eng_ocr_fused(
    lens: Series,
    tesseract: Series,
    processor: OcrFusionProcessor | None = None,
    **kwargs: Unpack[EngOcrFusionProcessKwargs],
) -> Series:
    """Get English series fused from Google Lens and Tesseract OCR outputs.

    Arguments:
        lens: subtitles OCRed using Google Lens
        tesseract: subtitles OCRed using Tesseract
        processor: OcrFusionProcessor to use
        **kwargs: additional keyword arguments for OcrFusionProcessor.process
    Returns:
        fused series
    """
    if processor is None:
        processor = get_eng_ocr_fuser()
    return processor.process(lens, tesseract, **kwargs)


def get_eng_ocr_fuser(
    prompt_cls: type[EngOcrFusionPrompt] = EngOcrFusionPrompt,
    test_cases: list[TestCase] | None = None,
    **kwargs: Unpack[EngOcrFusionProcessorKwargs],
) -> OcrFusionProcessor:
    """Get OcrFusionProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        **kwargs: additional keyword arguments for OcrFusionProcessor
    Returns:
        OcrFusionProcessor with provided configuration
    """
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(
                OcrFusionManager,
                prompt_cls,
                ENG_OCR_FUSION_JSON_PATHS,
            )
        )
    return OcrFusionProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        **kwargs,
    )
