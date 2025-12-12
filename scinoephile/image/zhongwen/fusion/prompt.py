#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for Zhongwen OCR fusion."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.core.zhongwen import ZhongwenPrompt

__all__ = ["ZhongwenFusionPrompt"]


class ZhongwenFusionPrompt(ZhongwenPrompt):
    """Text for LLM correspondence for Zhongwen OCR fusion."""

    # Prompt
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
