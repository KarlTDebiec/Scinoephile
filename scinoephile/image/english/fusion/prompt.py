#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for English fusion."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.english import EnglishPrompt
from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.image.fusion import FusionPrompt

__all__ = ["EnglishFusionPrompt"]


class EnglishFusionPrompt(FusionPrompt, EnglishPrompt):
    """LLM correspondence text for English fusion."""

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
    source_one_field: ClassVar[str] = "lens"
    """Field name for OCR source one."""

    source_one_description: ClassVar[str] = "Subtitle text OCRed using Google Lens"
    """Description of source one field."""

    source_two_field: ClassVar[str] = "tesseract"
    """Field name for OCR source two."""

    source_two_description: ClassVar[str] = "Subtitle text OCRed using Tesseract"
    """Description of source two field."""

    # Query validation errors
    source_one_missing_error: ClassVar[str] = (
        "Subtitle text OCRed using Google Lens is required."
    )
    """Error message when source one field is missing."""

    source_two_missing_error: ClassVar[str] = (
        "Subtitle text OCRed using Tesseract is required."
    )
    """Error message when source two field is missing."""

    sources_equal_error: ClassVar[str] = (
        "Subtitle text OCRed using Google Lens and Tesseract must differ."
    )
    """Error message when source one and two fields are equal."""
