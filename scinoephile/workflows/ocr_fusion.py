#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for fusing subtitle OCR outputs."""

from __future__ import annotations

from typing import Unpack

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, ProcessorKwargs, TestCase
from scinoephile.core.subtitles import Series
from scinoephile.lang.ocr_fusion import get_ocr_fuser
from scinoephile.llms.ocr_fusion import (
    OcrFusionProcessor,
    OcrFusionPrompt,
)

__all__ = ["fuse_ocr_series"]


def fuse_ocr_series(
    source_one: Series,
    source_two: Series,
    *,
    language: Language,
    prompt: OcrFusionPrompt | None = None,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    fuser: OcrFusionProcessor | None = None,
    stop_at_idx: int | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> Series:
    """Fuse two subtitle OCR outputs for a supported language.

    Arguments:
        source_one: Google Lens OCR subtitle series
        source_two: Tesseract or PaddleOCR subtitle series
        language: subtitle language
        prompt: text for LLM correspondence
        test_cases: test cases
        provider: provider to use for queries
        fuser: OCR fuser to use, or None to construct one
        stop_at_idx: exclusive subtitle index at which to stop processing
        **kwargs: additional keyword arguments for OcrFusionProcessor
    Returns:
        fused subtitle series
    Raises:
        ScinoephileError: if OCR fusion does not support the language
    """
    if fuser is None:
        fuser = get_ocr_fuser(language, prompt, test_cases, provider, **kwargs)
    return fuser.process(source_one, source_two, stop_at_idx=stop_at_idx)
