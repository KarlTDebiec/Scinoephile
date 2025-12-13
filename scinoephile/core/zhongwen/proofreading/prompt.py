#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for 中文 proofreading."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.proofreading import ProofreadingPrompt
from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.core.zhongwen import (
    OpenCCConfig,
    ZhongwenPrompt,
    get_zhongwen_text_converted,
)

__all__ = [
    "ZhongwenTradProofreadingPrompt",
    "ZhongwenSimpProofreadingPrompt",
]


class ZhongwenSimpProofreadingPrompt(ProofreadingPrompt, ZhongwenPrompt):
    """LLM correspondence text for 简体中文 proofreading."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        你负责校对由 OCR 识别生成的中文字幕。
        你的任务仅限于纠正 OCR 识别错误（例如错字、漏字、字符混淆等），
        不得进行任何风格或语法上的润色，也不要添加或修改标点符号。
        对于每一条字幕，如有需要修改，请提供修改后的完整字幕，并附上一条说明所作修改的备注。
        如果不需要修改，请将修改后的字幕和备注都留空字符串。""")
    """Base system prompt."""

    # Query fields
    subtitle_prefix: ClassVar[str] = "zimu_"
    """Prefix of subtitle field in query."""

    subtitle_description_template: ClassVar[str] = "第 {idx} 条字幕"
    """Description template for subtitle field in query."""

    # Answer fields
    revised_prefix: ClassVar[str] = "xiugai_"
    """Prefix of revised field in answer."""

    revised_description_template: ClassVar[str] = "第 {idx} 条修改后的字幕"
    """Description template for revised field in answer."""

    note_prefix: ClassVar[str] = "beizhu_"
    """Prefix of note field in answer."""

    note_description_template: ClassVar[str] = "关于第 {idx} 条字幕修改的备注说明"
    """Description template for note field in answer."""

    # Test case errors
    subtitle_revised_equal_error_template: ClassVar[str] = (
        "第 {idx} 条答案的修改文本与查询文本相同。如果不需要修改，应提供空字符串。"
    )
    """Error template when subtitle and revised fields are equal."""

    note_missing_error_template: ClassVar[str] = (
        "第 {idx} 条答案的文本已被修改，但未提供备注。如需修改，必须附带备注说明。"
    )
    """Error template when revision is missing but note is provided."""

    revised_missing_error_template: ClassVar[str] = (
        "第 {idx} 条答案的文本未修改，但提供了备注。如果不需要修改，应提供空字符串。"
    )
    """Error template when revision is missing but note is provided."""


class ZhongwenTradProofreadingPrompt(ProofreadingPrompt, ZhongwenPrompt):
    """LLM correspondence text for 繁体中文 proofreading."""

    base_system_prompt: ClassVar[str] = get_zhongwen_text_converted(
        ZhongwenSimpProofreadingPrompt.base_system_prompt, OpenCCConfig.s2t
    )
    """Base system prompt."""

    subtitle_description_template: ClassVar[str] = get_zhongwen_text_converted(
        ZhongwenSimpProofreadingPrompt.subtitle_description_template, OpenCCConfig.s2t
    )
    """Description template for subtitle field in query."""

    revised_description_template: ClassVar[str] = get_zhongwen_text_converted(
        ZhongwenSimpProofreadingPrompt.revised_description_template, OpenCCConfig.s2t
    )
    """Description template for revised field in answer."""

    note_description_template: ClassVar[str] = get_zhongwen_text_converted(
        ZhongwenSimpProofreadingPrompt.note_description_template, OpenCCConfig.s2t
    )
    """Description template for note field in answer."""

    subtitle_revised_equal_error_template: ClassVar[str] = get_zhongwen_text_converted(
        ZhongwenSimpProofreadingPrompt.subtitle_revised_equal_error_template,
        OpenCCConfig.s2t,
    )
    """Error template when subtitle and revised fields are equal."""

    note_missing_error_template: ClassVar[str] = get_zhongwen_text_converted(
        ZhongwenSimpProofreadingPrompt.note_missing_error_template, OpenCCConfig.s2t
    )
    """Error template when revision is missing but note is provided."""

    revised_missing_error_template: ClassVar[str] = get_zhongwen_text_converted(
        ZhongwenSimpProofreadingPrompt.revised_missing_error_template, OpenCCConfig.s2t
    )
    """Error template when revision is missing but note is provided."""
