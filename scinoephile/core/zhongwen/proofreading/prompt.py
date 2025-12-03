#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for 中文 proofreading."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.core.zhongwen.abcs import ZhongwenPrompt

__all__ = [
    "ZhongwenProofreadingPromptBase",
    "ZhongwenProofreadingPrompt",
    "ZhongwenProofreadingSimplifiedPrompt",
    "ZhongwenProofreadingTraditionalPrompt",
]


class ZhongwenProofreadingPromptBase(ZhongwenPrompt, ABC):
    """Abstract text strings for 中文 proofreading."""

    # Prompt
    base_system_prompt: ClassVar[str]
    """Base system prompt."""

    # Query descriptions
    zimu_description: ClassVar[str]
    """Description of 'zimu' field."""

    # Answer descriptions
    xiugai_description: ClassVar[str]
    """Description of 'xiugai' field."""

    beizhu_description: ClassVar[str]
    """Description of 'beizhu' field."""

    # Test case validation errors
    zimu_xiugai_equal_error: ClassVar[str]
    """Error message when 'zimu' and 'xiugai' fields are equal."""

    beizhu_missing_error: ClassVar[str]
    """Error message when 'xiugai' field is present but ''beizhu' field is missing."""

    xiugai_missing_error: ClassVar[str]
    """Error message when 'xiugai' field is missing but 'beizhu' field is present."""


class ZhongwenProofreadingSimplifiedPrompt(ZhongwenProofreadingPromptBase):
    """Simplified 中文 text for proofreading prompts."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        你负责校对由 OCR 识别生成的中文字幕。
        你的任务仅限于纠正 OCR 识别错误（例如错字、漏字、字符混淆等），
        不得进行任何风格或语法上的润色，也不要添加或修改标点符号。
        对于每一条字幕，如有需要修改，请提供修改后的完整字幕，并附上一条说明所作修改的备注。
        如果不需要修改，请将修改后的字幕和备注都留空字符串。""")
    """Base system prompt."""

    # Query descriptions
    zimu_description: ClassVar[str] = "第 {idx} 条字幕"
    """Description of 'zimu' field."""

    # Answer descriptions
    xiugai_description: ClassVar[str] = "第 {idx} 条修改后的字幕"
    """Description of 'xiugai' field."""

    beizhu_description: ClassVar[str] = "关于第 {idx} 条字幕修改的备注说明"
    """Description of 'beizhu' field."""

    # Test case validation errors
    zimu_xiugai_equal_error: ClassVar[str] = (
        "第 {idx} 条答案的修改文本与查询文本相同。如果不需要修改，应提供空字符串。"
    )
    """Error message when 'zimu' and 'xiugai' fields are equal."""

    beizhu_missing_error: ClassVar[str] = (
        "第 {idx} 条答案的文本已被修改，但未提供备注。如需修改，必须附带备注说明。"
    )
    """Error message when 'xiugai' field is present but ''beizhu' field is missing."""

    xiugai_missing_error: ClassVar[str] = (
        "第 {idx} 条答案的文本未修改，但提供了备注。如果不需要修改，应提供空字符串。"
    )
    """Error message when 'xiugai' field is missing but 'beizhu' field is present."""


class ZhongwenProofreadingTraditionalPrompt(ZhongwenProofreadingPromptBase):
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


ZhongwenProofreadingPrompt = ZhongwenProofreadingSimplifiedPrompt
