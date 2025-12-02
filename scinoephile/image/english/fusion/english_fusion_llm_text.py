#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text strings to be used for LLM correspondence for English OCR fusion."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.english.abcs import EnglishLLMText
from scinoephile.core.text import get_dedented_and_compacted_multiline_text


class EnglishFusionLLMText(EnglishLLMText):
    """Text strings to be used for LLM correspondence for English OCR fusion."""

    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        You are responsible for merging English subtitle OCR results from two different
        sources: Google Lens and Tesseract.
        Please follow these guidelines:
        * Google Lens is more reliable at recognizing text overall.
        * Tesseract is more reliable at italics.
        * Tesseract is more reliable at line breaks.
        * Tesseract is more reliable at the capitalization of the first word.""")
    """Base system prompt."""
