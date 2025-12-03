#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Traditional 中文 text for proofreading prompts."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import get_dedented_and_compacted_multiline_text

from .base import ZhongwenProofreadingPrompt

__all__ = ["ZhongwenProofreadingTraditionalPrompt"]


class ZhongwenProofreadingTraditionalPrompt(ZhongwenProofreadingPrompt):
    """Traditional 中文 text for proofreading prompts."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        你負責校對由 OCR 識別生成的中文字幕。
        你的任務僅限於糾正 OCR 識別錯誤（例如錯字、漏字、字符混淆等），
        不得進行任何風格或語法上的潤色，也不要添加或修改標點符號。
        對於每一條字幕，如有需要修改，請提供修改後的完整字幕，並附上一條說明所作修改的備註。
        如果不需要修改，請將修改後的字幕和備註都留空字符串。""")
    """Base system prompt."""

    # Query descriptions
    zimu_description: ClassVar[str] = "第 {idx} 條字幕"
    """Description of 'zimu' field."""

    # Answer descriptions
    xiugai_description: ClassVar[str] = "第 {idx} 條修改後的字幕"
    """Description of 'xiugai' field."""

    beizhu_description: ClassVar[str] = "關於第 {idx} 條字幕修改的備註說明"
    """Description of 'beizhu' field."""

    # Test case validation errors
    zimu_xiugai_equal_error: ClassVar[str] = (
        "第 {idx} 條答案的修改文本與查詢文本相同。如果不需要修改，應提供空字符串。"
    )
    """Error message when 'zimu' and 'xiugai' fields are equal."""

    beizhu_missing_error: ClassVar[str] = (
        "第 {idx} 條答案的文本已被修改，但未提供備註。如需修改，必須附帶備註說明。"
    )
    """Error message when 'xiugai' field is present but ''beizhu' field is missing."""

    xiugai_missing_error: ClassVar[str] = (
        "第 {idx} 條答案的文本未修改，但提供了備註。如果不需要修改，應提供空字符串。"
    )
    """Error message when 'xiugai' field is missing but 'beizhu' field is present."""
