#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Queries LLM to fuse OCRed 中文 subtitles from Google Lens and PaddleOCR."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.abcs import LLMQueryer
from scinoephile.image.zhongwen.fusion.zhongwen_fusion_answer import (
    ZhongwenFusionAnswer,
)
from scinoephile.image.zhongwen.fusion.zhongwen_fusion_llm_text import (
    ZhongwenFusionLLMText,
)
from scinoephile.image.zhongwen.fusion.zhongwen_fusion_query import ZhongwenFusionQuery
from scinoephile.image.zhongwen.fusion.zhongwen_fusion_test_case import (
    ZhongwenFusionTestCase,
)


class ZhongwenFusionLLMQueryer(
    LLMQueryer[ZhongwenFusionQuery, ZhongwenFusionAnswer, ZhongwenFusionTestCase]
):
    """Queries LLM to fuse OCRed 中文 subtitles from Google Lens and PaddleOCR."""

    text: ClassVar[type[ZhongwenFusionLLMText]]
    """Text strings to be used for corresponding with LLM."""
