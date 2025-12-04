#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 中文 OCR fusion."""

from __future__ import annotations

from typing import Any

from scinoephile.core import Series

from .answer import ZhongwenFusionAnswer
from .fuser import ZhongwenFuser
from .llm_queryer import ZhongwenFusionLLMQueryer
from .query import ZhongwenFusionQuery
from .test_case import ZhongwenFusionTestCase

__all__ = [
    "ZhongwenFuser",
    "ZhongwenFusionAnswer",
    "ZhongwenFusionLLMQueryer",
    "ZhongwenFusionQuery",
    "ZhongwenFusionTestCase",
    "get_zhongwen_ocr_fused",
]


def get_zhongwen_ocr_fused(
    lens: Series,
    paddle: Series,
    fuser: ZhongwenFuser | None = None,
    **kwargs: Any,
) -> Series:
    """Get OCRed 中文 series fused from Google Lens and PaddleOCR outputs.

    Arguments:
        lens: subtitles OCRed using Google Lens
        paddle: subtitles OCRed using PaddleOCR
        fuser: ZhongwenFuser to use
        kwargs: additional keyword arguments for ZhongwenFuser.fuse
    Returns:
        Fused series
    """
    if fuser is None:
        fuser = ZhongwenFuser()
    fused = fuser.fuse(lens, paddle, **kwargs)
    return fused
