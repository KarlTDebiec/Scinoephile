#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for English OCR fusion."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.english import EnglishPrompt
from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.image.fusion import FusionPrompt

__all__ = ["EnglishFusionPrompt"]


class EnglishFusionPrompt(FusionPrompt, EnglishPrompt):
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
    source_one_field: ClassVar[str] = "lens"
    source_two_field: ClassVar[str] = "tesseract"

    # Query descriptions
    source_one_description: ClassVar[str] = "Subtitle text OCRed using Google Lens"
    """Description of 'lens' field."""

    source_two_description: ClassVar[str] = "Subtitle text OCRed using Tesseract"
    """Description of 'tesseract' field."""

    # Query validation errors
    source_one_missing_error: ClassVar[str] = (
        "Subtitle text OCRed using Google Lens is required."
    )
    """Error message when 'lens' field is missing."""

    source_two_missing_error: ClassVar[str] = (
        "Subtitle text OCRed using Tesseract is required."
    )
    """Error message when 'tesseract' field is missing."""

    sources_equal_error: ClassVar[str] = (
        "Subtitle text OCRed using Google Lens and Tesseract must differ."
    )
    """Error message when 'lens' and 'tesseract' fields are equal."""

    # Answer descriptions
    fused_description: ClassVar[str] = "Merged subtitle text"
    """Description of 'fused' field."""

    note_description: ClassVar[str] = "Explanation of changes made"
    """Description of 'note' field."""

    # Answer validation errors
    fused_missing_error: ClassVar[str] = "Merged subtitle text is required."
    """Error message when 'fused' field is missing."""

    note_missing_error: ClassVar[str] = "Explanation of changes made is required."
    """Error message when 'note' field is missing."""

    # Logging labels
    source_one_label: ClassVar[str] = "Lens"
    source_two_label: ClassVar[str] = "Tesseract"
