#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM prompts for written Cantonese block review."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.yue.prompts import PromptYueHant
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.block_review import BlockReviewPrompt

__all__ = [
    "BlockReviewPromptYueHans",
    "BlockReviewPromptYueHant",
]


class BlockReviewPromptYueHant(BlockReviewPrompt, PromptYueHant):
    """LLM correspondence text for traditional written Cantonese block review."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你負責校對粵文字幕。
        只修正排版、錯別字、OCR 或轉寫造成嘅明顯錯誤。
        唔好潤色、改寫、改動語氣或用詞，亦唔好根據上下文改劇情。
        如果原句本身已經係合理嘅粵語講法，請保持原文不變。
        對每條字幕，只有喺需要修改時先提供修訂後嘅完整字幕。
        若需要修改，請返回完整修訂後字幕，並給出說明修改內容嘅備註。
        若唔需要修改，修訂後字幕同備註都返回空字符串。""")
    """Base system prompt."""

    # Query fields
    input_pfx: ClassVar[str] = "zimu_"
    """Prefix for input fields in query."""

    input_desc_tpl: ClassVar[str] = "第 {idx} 條粵文字幕"
    """Description template for input fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "xiugai_"
    """Prefix for output fields in answer."""

    output_desc_tpl: ClassVar[str] = "第 {idx} 條修改後嘅粵文字幕"
    """Description template for output fields in answer."""

    note_pfx: ClassVar[str] = "beizhu_"
    """Prefix for note fields in answer."""

    note_desc_tpl: ClassVar[str] = "關於第 {idx} 條粵文字幕修改嘅備註說明"
    """Description template for note fields in answer."""

    # Test case errors
    output_unmodified_err_tpl: ClassVar[str] = (
        "第 {idx} 條答案嘅修改文本同查詢文本相同。如果唔需要修改，應提供空字符串。"
    )
    """Error template when output is present but unmodified."""

    note_missing_err_tpl: ClassVar[str] = (
        "第 {idx} 條答案嘅文本已被修改，但未提供備註。如需修改，必須附帶備註說明。"
    )
    """Error template when note is missing for a change."""

    output_missing_err_tpl: ClassVar[str] = (
        "第 {idx} 條答案嘅文本未修改，但提供咗備註。如果唔需要修改，應提供空字符串。"
    )
    """Error template when output is missing for a note."""


class BlockReviewPromptYueHans(BlockReviewPromptYueHant):
    """LLM correspondence text for simplified written Cantonese block review."""

    opencc_config = OpenCCConfig.hk2s
    """Config for converting traditional Cantonese characters from the parent class."""
