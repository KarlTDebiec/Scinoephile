#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Queries LLM to fuse OCRed English subtitles from Google Lens and Tesseract."""

from __future__ import annotations

from typing import override

from scinoephile.core.abcs import FixedLLMQueryer
from scinoephile.image.english.fusion.english_fusion_answer import (
    EnglishFusionAnswer,
)
from scinoephile.image.english.fusion.english_fusion_query import EnglishFusionQuery
from scinoephile.image.english.fusion.english_fusion_test_case import (
    EnglishFusionTestCase,
)


class EnglishFusionLLMQueryer(
    FixedLLMQueryer[EnglishFusionQuery, EnglishFusionAnswer, EnglishFusionTestCase]
):
    """Queries LLM to fuse OCRed English subtitles from Google Lens and Tesseract."""

    @property
    @override
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        You are responsible for merging English subtitle OCR results from two different
        sources: Google Lens and Tesseract.
        Please follow these guidelines:
        * Google Lens is more reliable at recognizing English words.
        * Google Lens is more reliable at recognizing punctuation marks.        
        * Tesseract is more reliable at recognizing italics.
        * Tesseract is more reliable at recognizing line breaks.
        """
