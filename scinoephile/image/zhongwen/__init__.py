#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to 中文 image subtitles."""

from __future__ import annotations

from typing import Any

from scinoephile.core.series import Series
from scinoephile.image.zhongwen.fusion.zhongwen_fuser import ZhongwenFuser


def get_zhongwen_ocr_fused(
    paddle: Series, lens: Series, fuser: ZhongwenFuser = None, **kwargs: Any
) -> Series:
    """Get OCRed 中文 series fused from PaddleOCR and Google Lens outputs.

    Arguments:
        paddle: subtitles OCRed using PaddleOCR
        lens: subtitles OCRed using Google Lens
        fuser: ZhongwenFuser to use
        kwargs: additional keyword arguments for ZhongwenFuser.fuse
    Returns:
        Fused series
    """
    if fuser is None:
        fuser = ZhongwenFuser()
    fused = fuser.fuse(paddle, lens, **kwargs)
    return fused


__all__ = [
    "get_zhongwen_ocr_fused",
]
