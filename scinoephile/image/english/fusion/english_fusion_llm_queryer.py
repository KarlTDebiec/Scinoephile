#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Queries LLM to fuse OCRed English subtitles from Google Lens and Tesseract."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.abcs import FixedLLMQueryer
from scinoephile.image.english.fusion.english_fusion_answer import (
    EnglishFusionAnswer,
)
from scinoephile.image.english.fusion.english_fusion_llm_text import (
    EnglishFusionLLMText,
)
from scinoephile.image.english.fusion.english_fusion_query import EnglishFusionQuery
from scinoephile.image.english.fusion.english_fusion_test_case import (
    EnglishFusionTestCase,
)


class EnglishFusionLLMQueryer(
    FixedLLMQueryer[EnglishFusionQuery, EnglishFusionAnswer, EnglishFusionTestCase]
):
    """Queries LLM to fuse OCRed English subtitles from Google Lens and Tesseract."""

    text: ClassVar[type[EnglishFusionLLMText]] = EnglishFusionLLMText
    """Text strings to be used for corresponding with LLM."""
