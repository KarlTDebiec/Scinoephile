#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for LLM correspondence concerning 中文 OCR fusion."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.core.zhongwen import (
    OpenCCConfig,
    get_zhongwen_prompt_converted,
)
from scinoephile.core.zhongwen.abcs import ZhongwenPrompt

__all__ = [
    "ZhongwenFusionPrompt",
    "ZhongwenFusionSimplifiedPrompt",
    "ZhongwenFusionTraditionalPrompt",
]


class ZhongwenFusionPrompt(ZhongwenPrompt, ABC):
    """Abstract base class for LLM correspondence concerning 中文 OCR fusion."""

    base_system_prompt: ClassVar[str]
    """Base system prompt."""

    # Query descriptions
    lens_description: ClassVar[str]
    """Description of 'lens' field."""

    paddle_description: ClassVar[str]
    """Description of 'paddle' field."""

    # Query validation errors
    lens_missing_error: ClassVar[str]
    """Error message when 'lens' field is missing."""

    paddle_missing_error: ClassVar[str]
    """Error message when 'paddle' field is missing."""

    lens_paddle_equal_error: ClassVar[str]
    """Error message when 'lens' and 'paddle' fields are equal."""

    # Answer descriptions
    ronghe_description: ClassVar[str]
    """Description of 'ronghe' field."""

    beizhu_description: ClassVar[str]
    """Description of 'beizhu' field."""

    # Answer validation errors
    ronghe_missing_error: ClassVar[str]
    """Error message when 'ronghe' field is missing."""

    beizhu_missing_error: ClassVar[str]
    """Error message when 'beizhu' field is missing."""


class ZhongwenFusionSimplifiedPrompt(ZhongwenFusionPrompt):
    """简体中文 text for LLM correspondence concerning 中文 OCR fusion."""

    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        你负责将来自两个不同来源的中文字幕 OCR 结果进行融合：Google Lens 和 PaddleOCR。
        请遵循以下原则：
        * Google Lens 在识别汉字方面更可靠。
        * Google Lens 在标点符号方面更可靠。
        * PaddleOCR 在换行格式方面更可靠。""")
    """Base system prompt."""

    # Query descriptions
    lens_description: ClassVar[str] = "Google Lens 提取的字幕文本"
    """Description of 'lens' field."""

    paddle_description: ClassVar[str] = "PaddleOCR 提取的字幕文本"
    """Description of 'paddle' field."""

    # Query validation errors
    lens_missing_error: ClassVar[str] = "缺少 Google Lens 的中文字幕文本。"
    """Error message when 'lens' field is missing."""

    paddle_missing_error: ClassVar[str] = "缺少 PaddleOCR 的中文字幕文本。"
    """Error message when 'paddle' field is missing."""

    lens_paddle_equal_error: ClassVar[str] = (
        "Google Lens 与 PaddleOCR 的字幕文本不能完全相同。"
    )
    """Error message when 'lens' and 'paddle' fields are equal."""

    # Answer descriptions
    ronghe_description: ClassVar[str] = "融合后的字幕文本"
    """Description of 'ronghe' field."""

    beizhu_description: ClassVar[str] = "对所做更正的说明"
    """Description of 'beizhu' field."""

    # Answer validation errors
    ronghe_missing_error: ClassVar[str] = "融合后的字幕文本不能为空。"
    """Error message when 'ronghe' field is missing."""

    beizhu_missing_error: ClassVar[str] = "更正说明不能为空。"
    """Error message when 'beizhu' field is missing."""


ZhongwenFusionTraditionalPrompt = get_zhongwen_prompt_converted(
    ZhongwenFusionSimplifiedPrompt,
    ZhongwenFusionPrompt,
    "ZhongwenFusionTraditionalPrompt",
    OpenCCConfig.s2t,
)
