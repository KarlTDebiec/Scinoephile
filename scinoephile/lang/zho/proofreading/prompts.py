#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for 中文 proofreading."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.blockwise import BlockwisePrompt
from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.lang.zho.prompts import ZhoHansPrompt

__all__ = [
    "ZhoHansProofreadingPrompt",
    "ZhoHantProofreadingPrompt",
]


class ZhoHansProofreadingPrompt(BlockwisePrompt, ZhoHansPrompt):
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
    input_prefix: ClassVar[str] = "zimu_"
    """Prefix for subtitle fields in query."""

    input_description_template: ClassVar[str] = "第 {idx} 条字幕"
    """Description template for subtitle fields in query."""

    # Answer fields
    output_prefix: ClassVar[str] = "xiugai_"
    """Prefix of revised field in answer."""

    output_description_template: ClassVar[str] = "第 {idx} 条修改后的字幕"
    """Description template for revised fields in answer."""

    note_prefix: ClassVar[str] = "beizhu_"
    """Prefix of note field in answer."""

    note_description_template: ClassVar[str] = "关于第 {idx} 条字幕修改的备注说明"
    """Description template for note fields in answer."""

    # Test case errors
    output_unmodified_error_template: ClassVar[str] = (
        "第 {idx} 条答案的修改文本与查询文本相同。如果不需要修改，应提供空字符串。"
    )
    """Error template when subtitle and revised fields are equal."""

    note_missing_error_template: ClassVar[str] = (
        "第 {idx} 条答案的文本已被修改，但未提供备注。如需修改，必须附带备注说明。"
    )
    """Error template when note is missing for a revision."""

    output_missing_error_template: ClassVar[str] = (
        "第 {idx} 条答案的文本未修改，但提供了备注。如果不需要修改，应提供空字符串。"
    )
    """Error template when revision is missing for a note."""


class ZhoHantProofreadingPrompt(ZhoHansProofreadingPrompt):
    """LLM correspondence text for 繁体中文 proofreading."""

    opencc_config = OpenCCConfig.s2t
    """Config with which to convert characters from 简体中文 present in parent class."""
