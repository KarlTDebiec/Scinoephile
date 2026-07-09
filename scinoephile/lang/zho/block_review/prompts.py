#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for standard Chinese block review."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.zho.prompts import PromptZhoHans, PromptZhoHant
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.block_review import BlockReviewPrompt

__all__ = [
    "BlockReviewPromptZhoHans",
    "BlockReviewPromptZhoHant",
]


class BlockReviewPromptZhoHant(BlockReviewPrompt, PromptZhoHant):
    """LLM correspondence text for traditional standard Chinese block review."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你負責校對中文字幕。
        僅修正排版與錯別字等排版性/輸入性錯誤。
        不要潤色、改寫、改動語氣或用詞，也不要根據上下文改劇情。
        如果沒有明顯的錯別字或排版錯誤，請保持原文不變。
        對每條字幕，只有在需要修改時才提供修訂後的字幕。
        若需要修改，請返回完整的修訂後字幕，並給出說明修改內容的備註。
        若不需要修改，修訂後字幕與備註均返回空字符串。""")
    """Base system prompt."""

    # Query fields
    input_pfx: ClassVar[str] = "zimu_"
    """Prefix for input fields in query."""

    input_desc_tpl: ClassVar[str] = "第 {idx} 條字幕"
    """Description template for input fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "xiugai_"
    """Prefix for output fields in answer."""

    output_desc_tpl: ClassVar[str] = "第 {idx} 條修改後的字幕"
    """Description template for output fields in answer."""

    note_pfx: ClassVar[str] = "beizhu_"
    """Prefix for note fields in answer."""

    note_desc_tpl: ClassVar[str] = "關於第 {idx} 條字幕修改的備註說明"
    """Description template for note fields in answer."""

    # Test case errors
    output_unmodified_err_tpl: ClassVar[str] = (
        "第 {idx} 條答案的修改文本與查詢文本相同。如果不需要修改，應提供空字符串。"
    )
    """Error template when output is present but unmodified."""

    note_missing_err_tpl: ClassVar[str] = (
        "第 {idx} 條答案的文本已被修改，但未提供備註。如需修改，必須附帶備註說明。"
    )
    """Error template when note is missing for a change."""

    output_missing_err_tpl: ClassVar[str] = (
        "第 {idx} 條答案的文本未修改，但提供了備註。如果不需要修改，應提供空字符串。"
    )
    """Error template when output is missing for a note."""


class BlockReviewPromptZhoHans(BlockReviewPromptZhoHant, PromptZhoHans):
    """LLM correspondence text for simplified standard Chinese block review."""

    opencc_config = OpenCCConfig.t2s
    """Config for converting traditional Chinese characters from the parent class."""
