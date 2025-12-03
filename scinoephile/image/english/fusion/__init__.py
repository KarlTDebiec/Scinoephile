#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English OCR fusion."""

from __future__ import annotations

from typing import Any

from scinoephile.core import Series

from .answer import EnglishFusionAnswer
from .fuser import EnglishFuser
from .prompt import EnglishFusionPrompt
from .query import EnglishFusionQuery
from .queryer import EnglishFusionLLMQueryer
from .test_case import EnglishFusionTestCase

__all__ = [
    "EnglishFuser",
    "EnglishFusionAnswer",
    "EnglishFusionLLMQueryer",
    "EnglishFusionPrompt",
    "EnglishFusionQuery",
    "EnglishFusionTestCase",
    "get_english_ocr_fused",
]


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
