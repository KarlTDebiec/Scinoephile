#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for standard Chinese translation from written Cantonese."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.zho.prompts import PromptZhoHans
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.dual_n_to_m import DualNToMPrompt

__all__ = [
    "ZhoTranslationVsYuePromptZhoHans",
    "ZhoTranslationVsYuePromptZhoHant",
]


class ZhoTranslationVsYuePromptZhoHans(DualNToMPrompt, PromptZhoHans):
    """Text for simplified standard Chinese translation from written Cantonese."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你负责根据粤文字幕，创作对应的标准中文字幕。

        每条粤文字幕都要输出一条标准中文字幕。译文要自然、通顺，准确表达粤文字幕
        的意思、语气、戏剧意图和说话人意图。不要逐字硬译；可以调整措辞，使其
        更像自然的标准中文字幕。专名、固定称呼、重复术语和字幕标记要在适合时
        保留或按标准中文习惯处理。

        输出内容只能是生成的中文字幕正文。不要附加英文、备注、解释、标签、
        替代译文、方括号内容、括号内容，或任何字幕以外的说明。
        """)
    """Base system prompt."""

    # Query fields
    src_1_pfx: ClassVar[str] = "yuewen_"
    """Prefix for written Cantonese source fields in query."""

    src_1_desc_tpl: ClassVar[str] = "要翻译成标准中文的粤文字幕 {idx}"
    """Description template for written Cantonese source fields in query."""

    src_2_pfx: ClassVar[str] = "context_"
    """Prefix for optional context fields in query."""

    src_2_desc_tpl: ClassVar[str] = "额外上下文字幕 {idx}"
    """Description template for optional context fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "zhongwen_"
    """Prefix for generated standard Chinese output fields in answer."""

    output_desc_tpl: ClassVar[str] = "字幕 {idx} 对应的标准中文译文"
    """Description template for generated standard Chinese output fields."""


class ZhoTranslationVsYuePromptZhoHant(ZhoTranslationVsYuePromptZhoHans):
    """Text for traditional standard Chinese translation from written Cantonese."""

    opencc_config = OpenCCConfig.s2t
    """Config for converting simplified Chinese characters from the parent class."""
