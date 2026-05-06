#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English OCR fusion."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.llms import OperationSpec, TestCase
from scinoephile.core.llms.llm_provider import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.llms.default_test_cases import (
    ENG_OCR_FUSION_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_single.ocr_fusion import OcrFusionManager, OcrFusionProcessor
from scinoephile.llms.providers.registry import get_default_provider

from .prompts import EngOcrFusionPrompt

__all__ = [
    "ENG_OCR_FUSION_OPERATION_SPEC",
    "EngOcrFusionPrompt",
    "EngOcrFusionProcessKwargs",
    "EngOcrFusionProcessorKwargs",
    "get_eng_ocr_fuser",
    "get_eng_ocr_fused",
]

ENG_OCR_FUSION_OPERATION_SPEC = OperationSpec(
    operation="eng-ocr-fusion",
    test_case_table_name="test_cases__eng__ocr_fusion",
    manager_cls=OcrFusionManager,
    prompt_cls=EngOcrFusionPrompt,
)
"""Operation specification for English OCR fusion."""


class EngOcrFusionProcessKwargs(TypedDict, total=False):
    """Keyword arguments for OcrFusionProcessor.process."""

    stop_at_idx: int | None
    """Subtitle index at which to stop processing, inclusive."""


class EngOcrFusionProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for OcrFusionProcessor initialization."""

    test_case_path: Path | None
    """Path where encountered test cases are persisted."""
    auto_verify: bool
    """Whether generated test cases should be marked verified automatically."""


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
    provider: LLMProvider | None = None,
    **kwargs: Unpack[EngOcrFusionProcessorKwargs],
) -> OcrFusionProcessor:
    """Get OcrFusionProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        provider: provider to use for queries
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
    if provider is None:
        provider = get_default_provider()
    return OcrFusionProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        provider=provider,
        **kwargs,
    )
