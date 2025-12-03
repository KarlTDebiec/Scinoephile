#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English OCR fusion."""

from __future__ import annotations

from typing import Any

from scinoephile.core import Series
from scinoephile.image.english.fusion.english_fuser import EnglishFuser
from scinoephile.image.english.fusion.english_fusion_answer import (
    EnglishFusionAnswer,
)
from scinoephile.image.english.fusion.english_fusion_llm_queryer import (
    EnglishFusionLLMQueryer,
)
from scinoephile.image.english.fusion.english_fusion_llm_text import (
    EnglishFusionLLMText,
)
from scinoephile.image.english.fusion.english_fusion_query import EnglishFusionQuery
from scinoephile.image.english.fusion.english_fusion_test_case import (
    EnglishFusionTestCase,
)


def get_english_ocr_fused(
    lens: Series,
    tesseract: Series,
    fuser: EnglishFuser | None = None,
    **kwargs: Any,
) -> Series:
    """Get OCRed English series fused from Google Lens and Tesseract outputs.

    Arguments:
        lens: subtitles OCRed using Google Lens
        tesseract: subtitles OCRed using Tesseract
        fuser: EnglishFuser to use
        kwargs: additional keyword arguments for EnglishFuser.fuse
    Returns:
        Fused series
    """
    if fuser is None:
        fuser = EnglishFuser()
    fused = fuser.fuse(lens, tesseract, **kwargs)
    return fused


__all__ = [
    "EnglishFuser",
    "EnglishFusionAnswer",
    "EnglishFusionLLMQueryer",
    "EnglishFusionLLMText",
    "EnglishFusionQuery",
    "EnglishFusionTestCase",
    "get_english_ocr_fused",
]
