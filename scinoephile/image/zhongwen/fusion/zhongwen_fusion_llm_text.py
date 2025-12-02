#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text strings to be used for LLM correspondence for 中文 OCR fusion."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.english.abcs import EnglishLLMText
from scinoephile.core.text import get_dedented_and_compacted_multiline_text


class ZhongwenFusionLLMText(EnglishLLMText):
    """Text strings to be used for LLM correspondence for 中文 OCR fusion."""

    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        你负责将来自两个不同来源的中文字幕 OCR 结果进行融合：PaddleOCR 和 Google Lens。
        请遵循以下原则：
        * Google Lens 在识别汉字方面更可靠。
        * Google Lens 在标点符号方面更可靠。
        * PaddleOCR 在换行格式方面更可靠。""")
    """Base system prompt."""
