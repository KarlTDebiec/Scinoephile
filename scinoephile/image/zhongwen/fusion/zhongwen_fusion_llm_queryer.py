#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Queries LLM to fuse OCRed 中文 subtitles from PaddleOCR and Google Lens."""

from __future__ import annotations

from typing import override

from scinoephile.core.abcs import FixedLLMQueryer
from scinoephile.image.zhongwen.fusion.zhongwen_fusion_answer import (
    ZhongwenFusionAnswer,
)
from scinoephile.image.zhongwen.fusion.zhongwen_fusion_query import ZhongwenFusionQuery
from scinoephile.image.zhongwen.fusion.zhongwen_fusion_test_case import (
    ZhongwenFusionTestCase,
)


class ZhongwenFusionLLMQueryer(
    FixedLLMQueryer[ZhongwenFusionQuery, ZhongwenFusionAnswer, ZhongwenFusionTestCase]
):
    """Queries LLM to fuse OCRed 中文 subtitles from PaddleOCR and Google Lens."""

    @property
    @override
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        你负责将来自两个不同来源的中文字幕 OCR 结果进行融合：PaddleOCR 和 Google Lens。
        请遵循以下原则：
        * Google Lens 在识别汉字方面更可靠。
        * Google Lens 在标点符号方面更可靠。
        * PaddleOCR 在换行格式方面更可靠。
        """
