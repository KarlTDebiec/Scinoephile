#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for 中文 proofreading."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.lang.zho.prompts import ZhoHansPrompt
from scinoephile.llms.mono_block import MonoBlockPrompt

__all__ = [
    "ZhoHansProofreadingPrompt",
    "ZhoHantProofreadingPrompt",
]


class ZhoHansProofreadingPrompt(MonoBlockPrompt, ZhoHansPrompt):
    """LLM correspondence text for 简体中文 proofreading."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        你负责校对简体中文字幕。
        仅修正排版与错别字等排版性/输入性错误。
        不要润色、改写、改动语气或用词，也不要根据上下文改剧情。
        如果没有明显的错别字或排版错误，请保持原文不变。
        对每条字幕，只有在需要修改时才提供修订后的字幕。
        若需要修改，请返回完整的修订后字幕，并给出说明修改内容的备注。
        若不需要修改，修订后字幕与备注均返回空字符串。""")
    """Base system prompt."""

    # Query fields
    input_pfx: ClassVar[str] = "zimu_"
    """Prefix for input fields in query."""

    input_desc_tpl: ClassVar[str] = "第 {idx} 条字幕"
    """Description template for input fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "xiugai_"
    """Prefix for output fields in answer."""

    output_desc_tpl: ClassVar[str] = "第 {idx} 条修改后的字幕"
    """Description template for output fields in answer."""

    note_pfx: ClassVar[str] = "beizhu_"
    """Prefix for note fields in answer."""

    note_desc_tpl: ClassVar[str] = "关于第 {idx} 条字幕修改的备注说明"
    """Description template for note fields in answer."""

    # Test case errors
    output_unmodified_err_tpl: ClassVar[str] = (
        "第 {idx} 条答案的修改文本与查询文本相同。如果不需要修改，应提供空字符串。"
    )
    """Error template when output is present but unmodified."""

    note_missing_err_tpl: ClassVar[str] = (
        "第 {idx} 条答案的文本已被修改，但未提供备注。如需修改，必须附带备注说明。"
    )
    """Error template when note is missing for a change."""

    output_missing_err_tpl: ClassVar[str] = (
        "第 {idx} 条答案的文本未修改，但提供了备注。如果不需要修改，应提供空字符串。"
    )
    """Error template when output is missing for a note."""


class ZhoHantProofreadingPrompt(ZhoHansProofreadingPrompt):
    """LLM correspondence text for 繁体中文 proofreading."""

    opencc_config = OpenCCConfig.s2t
    """Config with which to convert characters from 简体中文 present in parent class."""
