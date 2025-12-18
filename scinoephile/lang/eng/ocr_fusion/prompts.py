#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for English OCR fusion."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.pairwise import PairwisePrompt
from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.lang.eng.prompts import EngPrompt

__all__ = [
    "EngOcrFusionPrompt",
]


class EngOcrFusionPrompt(PairwisePrompt, EngPrompt):
    """LLM correspondence text for English OCR fusion."""

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
    """Name of source one field in query."""

    source_one_description: ClassVar[str] = "Subtitle text OCRed using Google Lens"
    """Description of source one field in query."""

    source_two_field: ClassVar[str] = "tesseract"
    """Name for source two field in query."""

    source_two_description: ClassVar[str] = "Subtitle text OCRed using Tesseract"
    """Description of source two field in query."""

    # Query validation errors
    source_one_missing_error: ClassVar[str] = (
        "Subtitle text OCRed using Google Lens is required."
    )
    """Error when source one field is missing from query."""

    source_two_missing_error: ClassVar[str] = (
        "Subtitle text OCRed using Tesseract is required."
    )
    """Error when source two field is missing from query."""

    sources_equal_error: ClassVar[str] = (
        "Subtitle text OCRed using Google Lens and Tesseract must differ."
    )
    """Error when source one and two fields are equal."""
