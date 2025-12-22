#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for English OCR fusion."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.lang.eng.prompts import EngPrompt
from scinoephile.llms.dual_single.ocr_fusion import OcrFusionPrompt

__all__ = [
    "EngOcrFusionPrompt",
]


class EngOcrFusionPrompt(OcrFusionPrompt, EngPrompt):
    """Text for LLM correspondence for English OCR fusion."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        You are responsible for merging English subtitle OCR results from two different
        sources: Google Lens and Tesseract.
        Please follow these guidelines:
        * Google Lens is more reliable at recognizing text overall.
        * Tesseract is more reliable at italics.
        * Tesseract is more reliable at line breaks.
        * Tesseract is more reliable at the capitalization of the first word.""")
    """Base system prompt."""

    # Query fields
    src_1: ClassVar[str] = "lens"
    """Name of source one field in query."""

    src_1_desc: ClassVar[str] = "Subtitle text OCRed using Google Lens"
    """Description of source one field in query."""

    src_2: ClassVar[str] = "tesseract"
    """Name for source two field in query."""

    src_2_desc: ClassVar[str] = "Subtitle text OCRed using Tesseract"
    """Description of source two field in query."""

    # Query validation errors
    src_1_missing_err: ClassVar[str] = (
        "Subtitle text OCRed using Google Lens is required."
    )
    """Error when source one field is missing from query."""

    src_2_missing_err: ClassVar[str] = (
        "Subtitle text OCRed using Tesseract is required."
    )
    """Error when source two field is missing from query."""

    src_1_src_2_equal_err: ClassVar[str] = (
        "Subtitle text OCRed using Google Lens and Tesseract must differ."
    )
    """Error when source one and two fields are equal."""
