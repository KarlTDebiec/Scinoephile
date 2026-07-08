#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for guided standard Chinese translation from English."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.zho.prompts import PromptZhoHans
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.dual_n_to_m import DualNToMPrompt

__all__ = [
    "ZhoEngGuidedTranslationPromptZhoHans",
    "ZhoEngGuidedTranslationPromptZhoHant",
]


class ZhoEngGuidedTranslationPromptZhoHans(DualNToMPrompt, PromptZhoHans):
    """Text for simplified guided standard Chinese translation from English."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你负责根据英文字幕，创作对应的标准中文字幕。你也会收到同一段场景的
        既有中文字幕，作为参考材料。

        每条英文字幕都要输出一条标准中文字幕。译文要准确表达英文字幕的意思、
        语气、戏剧意图和说话人意图。既有中文字幕是角色名、专名、重复术语、
        语域和固定说法的参考；当它和英文字幕意思兼容时，尽量沿用。
        如果英文字幕和既有中文字幕有差异，要优先按英文意思翻译，同时保留
        已经建立好的名词和称呼。

        输出内容只能是生成的中文字幕正文。不要附加英文、备注、解释、标签、
        替代译文、方括号内容、括号内容，或任何字幕以外的说明。
        """)
    """Base system prompt."""

    # Query fields
    src_1_pfx: ClassVar[str] = "eng_"
    """Prefix for English source fields in query."""

    src_1_desc_tpl: ClassVar[str] = "要翻译成标准中文的英文字幕 {idx}"
    """Description template for English source fields in query."""

    src_2_pfx: ClassVar[str] = "zhongwen_reference_"
    """Prefix for standard Chinese reference fields in query."""

    src_2_desc_tpl: ClassVar[str] = "同一段场景的既有标准中文参考字幕 {idx}"
    """Description template for standard Chinese reference fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "zhongwen_"
    """Prefix for generated standard Chinese output fields in answer."""

    output_desc_tpl: ClassVar[str] = "字幕 {idx} 对应的标准中文译文"
    """Description template for generated standard Chinese output fields."""


class ZhoEngGuidedTranslationPromptZhoHant(ZhoEngGuidedTranslationPromptZhoHans):
    """Text for traditional guided standard Chinese translation from English."""

    opencc_config = OpenCCConfig.s2t
    """Config for converting simplified Chinese characters from the parent class."""
