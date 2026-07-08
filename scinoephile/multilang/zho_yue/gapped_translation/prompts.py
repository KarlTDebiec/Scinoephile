#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for standard Chinese gapped translation using written Cantonese."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.zho.prompts import PromptZhoHans
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.dual_n_minus_m_to_n import DualNMinusMToNPrompt

__all__ = [
    "ZhoYueGappedTranslationPromptZhoHans",
    "ZhoYueGappedTranslationPromptZhoHant",
]


class ZhoYueGappedTranslationPromptZhoHans(DualNMinusMToNPrompt, PromptZhoHans):
    """Text for simplified standard Chinese gapped translation using Cantonese."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你负责根据对应的粤文字幕，补翻译缺失的标准中文字幕。
        只有当某行现有中文字幕为空字符串时，才需要提供译文。
        如果某行已经有中文内容，不要修改，该行请输出空字符串。
        译文要自然、通顺，语气和用词要尽量贴近附近已有的中文字幕。
        粤文字幕是意思来源；译文不需要逐字对应，但要准确表达该行意思。
        输出内容只能是字幕正文本身，不要附加英文、备注、解释、标签、
        方括号内容、括号内容，或任何译文以外的说明。
        如果不需要翻译，就输出空字符串。
        """)
    """Base system prompt."""

    # Query fields
    src_1_pfx: ClassVar[str] = "zhongwen_"
    """Prefix for source one fields in query."""

    src_1_desc_tpl: ClassVar[str] = "字幕 {idx} 现有的中文内容；如果为空就代表要翻译"
    """Description template for source one fields in query."""

    src_2_pfx: ClassVar[str] = "yuewen_"
    """Prefix for source two fields in query."""

    src_2_desc_tpl: ClassVar[str] = "字幕 {idx} 对应的粤文字幕"
    """Description template for source two fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "zhongwen_"
    """Prefix for output fields in answer."""

    output_desc_tpl: ClassVar[str] = (
        '字幕 {idx} 译好后的标准中文正文；如果不需要翻译请输出 ""。'
        "不要包含英文、备注、解释、标签或者括号说明。"
    )
    """Description template for output fields in answer."""

    # Test case validation errors
    output_unmodified_err_tpl: ClassVar[str] = (
        "字幕 {idx} 已经有中文内容，该行输出必须为空字符串。"
    )
    """Error template when output is present but unmodified relative to source one."""

    output_contains_note_err_tpl: ClassVar[str] = (
        "字幕 {idx} 包含英文或者备注说明；只可以输出中文字幕正文。"
    )
    """Error template when output includes leaked note text."""

    @classmethod
    def output_contains_note_err(cls, idx: int) -> str:
        """Error when output includes note-like text."""
        return cls.output_contains_note_err_tpl.format(idx=idx)


class ZhoYueGappedTranslationPromptZhoHant(ZhoYueGappedTranslationPromptZhoHans):
    """Text for traditional standard Chinese gapped translation using Cantonese."""

    opencc_config = OpenCCConfig.s2t
    """Config for converting simplified Chinese characters from the parent class."""
