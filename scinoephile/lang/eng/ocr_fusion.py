#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM prompts for English OCR fusion."""

from __future__ import annotations

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.llms.ocr_fusion import OcrFusionPrompt

from .prompts import ENG_PROMPT_FIELDS

__all__ = ["OcrFusionPromptEng"]


OcrFusionPromptEng = OcrFusionPrompt(
    language=Language.eng,
    **ENG_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        You are responsible for merging English subtitle OCR results from two different
        sources: Google Lens and Tesseract.
        Please follow these guidelines:
        * Google Lens is more reliable at recognizing text overall.
        * Tesseract is more reliable at italics.
        * Tesseract is more reliable at line breaks.
        * Tesseract is more reliable at the capitalization of the first word."""),
    src_1="lens",
    src_1_desc="Subtitle text OCRed using Google Lens",
    src_2="tesseract",
    src_2_desc="Subtitle text OCRed using Tesseract",
    src_1_missing_err="Subtitle text OCRed using Google Lens is required.",
    src_2_missing_err="Subtitle text OCRed using Tesseract is required.",
    src_1_src_2_equal_err=(
        "Subtitle text OCRed using Google Lens and Tesseract must differ."
    ),
)
"""Text for LLM correspondence for English OCR fusion."""
