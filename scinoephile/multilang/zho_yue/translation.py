#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for standard Chinese/written Cantonese translation prompts."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.zho.prompts import PromptZhoHans
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.dual_n_minus_m_to_n import DualNMinusMToNPrompt
from scinoephile.llms.dual_n_to_m import DualNToMPrompt
from scinoephile.llms.mono_n import MonoNPrompt

__all__ = [
    "ZhoYueTranslationPromptZhoHans",
    "ZhoYueTranslationPromptZhoHant",
    "ZhoYueGappedTranslationPromptZhoHans",
    "ZhoYueGappedTranslationPromptZhoHant",
    "ZhoYueGuidedTranslationPromptZhoHans",
    "ZhoYueGuidedTranslationPromptZhoHant",
]


class ZhoYueTranslationPromptZhoHans(MonoNPrompt, PromptZhoHans):
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
    input_pfx: ClassVar[str] = "yuewen_"
    """Prefix for written Cantonese source fields in query."""

    input_desc_tpl: ClassVar[str] = "要翻译成标准中文的粤文字幕 {idx}"
    """Description template for written Cantonese source fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "zhongwen_"
    """Prefix for generated standard Chinese output fields in answer."""

    output_desc_tpl: ClassVar[str] = "字幕 {idx} 对应的标准中文译文"
    """Description template for generated standard Chinese output fields."""


class ZhoYueTranslationPromptZhoHant(ZhoYueTranslationPromptZhoHans):
    """Text for traditional standard Chinese translation from written Cantonese."""

    opencc_config = OpenCCConfig.s2t
    """Config for converting simplified Chinese characters from the parent class."""


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


class ZhoYueGuidedTranslationPromptZhoHans(DualNToMPrompt, PromptZhoHans):
    """Text for simplified guided standard Chinese translation from Cantonese."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你负责根据粤文字幕，创作对应的标准中文字幕。你也会收到同一段场景的
        既有中文字幕，作为参考材料。

        每条粤文字幕都要输出一条标准中文字幕。译文要准确表达粤文字幕的意思、
        语气、戏剧意图和说话人意图。既有中文字幕是角色名、专名、重复术语、
        语域和固定说法的参考；当它和粤文字幕意思兼容时，尽量沿用。
        如果粤文字幕和既有中文字幕有差异，要优先按粤文意思翻译，同时保留
        已经建立好的名词和称呼。

        输出内容只能是生成的中文字幕正文。不要附加英文、备注、解释、标签、
        替代译文、方括号内容、括号内容，或任何字幕以外的说明。
        """)
    """Base system prompt."""

    # Query fields
    src_1_pfx: ClassVar[str] = "yuewen_"
    """Prefix for written Cantonese source fields in query."""

    src_1_desc_tpl: ClassVar[str] = "要翻译成标准中文的粤文字幕 {idx}"
    """Description template for written Cantonese source fields in query."""

    src_2_pfx: ClassVar[str] = "zhongwen_reference_"
    """Prefix for standard Chinese reference fields in query."""

    src_2_desc_tpl: ClassVar[str] = "同一段场景的既有标准中文参考字幕 {idx}"
    """Description template for standard Chinese reference fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "zhongwen_"
    """Prefix for generated standard Chinese output fields in answer."""

    output_desc_tpl: ClassVar[str] = "字幕 {idx} 对应的标准中文译文"
    """Description template for generated standard Chinese output fields."""


class ZhoYueGuidedTranslationPromptZhoHant(ZhoYueGuidedTranslationPromptZhoHans):
    """Text for traditional guided standard Chinese translation from Cantonese."""

    opencc_config = OpenCCConfig.s2t
    """Config for converting simplified Chinese characters from the parent class."""
