#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for written Cantonese/English translation prompts."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.dictionaries import DictionaryToolPrompt
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.yue.prompts import PromptYueHans
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.dual_n_minus_m_to_n import DualNMinusMToNPrompt
from scinoephile.llms.dual_n_to_m import DualNToMPrompt
from scinoephile.llms.mono_n import MonoNPrompt

__all__ = [
    "YueEngTranslationPromptYueHans",
    "YueEngTranslationPromptYueHant",
    "YueEngGappedTranslationPromptYueHans",
    "YueEngGappedTranslationPromptYueHant",
    "YueEngGuidedTranslationPromptYueHans",
    "YueEngGuidedTranslationPromptYueHant",
]


class YueEngTranslationPromptYueHans(DictionaryToolPrompt, MonoNPrompt, PromptYueHans):
    """Text for simplified written Cantonese translation from English."""

    # Dictionary tool
    dictionary_tool_name: ClassVar[str] = "lookup_dictionary"
    """Name of the dictionary lookup tool."""

    dictionary_tool_description: ClassVar[str] = (
        "查本地词典入面嘅粤语同普通话词条。工具会自动判断查询系汉字、拼音定粤拼。"
    )
    """Description of the dictionary lookup tool."""

    dictionary_tool_query_description: ClassVar[str] = (
        "要查嘅普通话或者粤语词语，可以系汉字、拼音或者粤拼。"
    )
    """Description of the dictionary lookup query parameter."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你负责根据英文字幕，创作对应嘅粤文字幕。

        每条英文字幕都要输出一条粤文字幕。译文要用自然、通顺嘅书面粤语，
        准确表达英文字幕嘅意思、语气、戏剧意图同说话人意图。唔好逐字硬译；
        可以调整措辞令佢更似自然粤文字幕。专名、固定称呼、重复术语同字幕标记
        要喺适合时保留或者按粤语习惯处理。

        输出内容只可以系生成嘅粤文字幕正文。绝对唔好附加英文、备注、解释、标签、
        替代译文、方括号内容、括号内容，或者任何字幕以外嘅说明。
        """)
    """Base system prompt."""

    # Query fields
    input_pfx: ClassVar[str] = "eng_"
    """Prefix for English source fields in query."""

    input_desc_tpl: ClassVar[str] = "要翻译成粤文嘅英文字幕 {idx}"
    """Description template for English source fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "yuewen_"
    """Prefix for generated written Cantonese output fields in answer."""

    output_desc_tpl: ClassVar[str] = "字幕 {idx} 对应嘅粤文译文"
    """Description template for generated written Cantonese output fields."""


class YueEngTranslationPromptYueHant(YueEngTranslationPromptYueHans):
    """Text for traditional written Cantonese translation from English."""

    opencc_config = OpenCCConfig.s2hk
    """Config for converting simplified Chinese characters from the parent class."""


class YueEngGappedTranslationPromptYueHans(
    DictionaryToolPrompt, DualNMinusMToNPrompt, PromptYueHans
):
    """Text for simplified written Cantonese gapped translation using English."""

    # Dictionary tool
    dictionary_tool_name: ClassVar[str] = "lookup_dictionary"
    """Name of the dictionary lookup tool."""

    dictionary_tool_description: ClassVar[str] = (
        "查本地词典入面嘅粤语同普通话词条。工具会自动判断查询系汉字、拼音定粤拼。"
    )
    """Description of the dictionary lookup tool."""

    dictionary_tool_query_description: ClassVar[str] = (
        "要查嘅普通话或者粤语词语，可以系汉字、拼音或者粤拼。"
    )
    """Description of the dictionary lookup query parameter."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你负责根据对应嘅英文字幕，补翻译缺失咗嘅粤文字幕。
        只有当某行现有粤文字幕系空字串时，先需要提供译文。
        如果某行已经有粤文内容，唔好改，嗰行请输出空字串。
        译文要用自然、通顺嘅书面粤语，语气同用词要尽量贴近附近已有嘅粤文字幕。
        英文字幕系意思来源；译文唔需要逐字对应，但要准确表达该行意思。
        输出内容只可以系字幕正文本身，绝对唔好附加英文、备注、解释、标签、
        方括号内容、括号内容，或者任何译文以外嘅说明。
        如果唔需要翻译，就输出空字串。
        """)
    """Base system prompt."""

    # Query fields
    src_1_pfx: ClassVar[str] = "yuewen_"
    """Prefix for source one fields in query."""

    src_1_desc_tpl: ClassVar[str] = "字幕 {idx} 现有嘅粤文内容；如果系空就代表要翻译"
    """Description template for source one fields in query."""

    src_2_pfx: ClassVar[str] = "eng_"
    """Prefix for source two fields in query."""

    src_2_desc_tpl: ClassVar[str] = "字幕 {idx} 对应嘅英文字幕"
    """Description template for source two fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "yuewen_"
    """Prefix for output fields in answer."""

    output_desc_tpl: ClassVar[str] = (
        '字幕 {idx} 译好后嘅粤文正文；如果唔需要翻译请输出 ""。'
        "唔好包含英文、备注、解释、标签或者括号说明。"
    )
    """Description template for output fields in answer."""

    # Test case validation errors
    output_unmodified_err_tpl: ClassVar[str] = (
        "字幕 {idx} 已经有粤文内容，嗰行输出必须系空字串。"
    )
    """Error template when output is present but unmodified relative to source one."""

    output_contains_note_err_tpl: ClassVar[str] = (
        "字幕 {idx} 包含英文或者备注说明；只可以输出粤文字幕正文。"
    )
    """Error template when output includes leaked note text."""

    @classmethod
    def output_contains_note_err(cls, idx: int) -> str:
        """Error when output includes note-like text."""
        return cls.output_contains_note_err_tpl.format(idx=idx)


class YueEngGappedTranslationPromptYueHant(YueEngGappedTranslationPromptYueHans):
    """Text for traditional written Cantonese gapped translation using English."""

    opencc_config = OpenCCConfig.s2hk
    """Config for converting simplified Chinese characters from the parent class."""


class YueEngGuidedTranslationPromptYueHans(
    DictionaryToolPrompt, DualNToMPrompt, PromptYueHans
):
    """Text for simplified guided written Cantonese translation from English."""

    # Dictionary tool
    dictionary_tool_name: ClassVar[str] = "lookup_dictionary"
    """Name of the dictionary lookup tool."""

    dictionary_tool_description: ClassVar[str] = (
        "查本地词典入面嘅粤语同普通话词条。工具会自动判断查询系汉字、拼音定粤拼。"
    )
    """Description of the dictionary lookup tool."""

    dictionary_tool_query_description: ClassVar[str] = (
        "要查嘅普通话或者粤语词语，可以系汉字、拼音或者粤拼。"
    )
    """Description of the dictionary lookup query parameter."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你负责根据英文字幕，创作对应嘅粤文字幕。你亦会收到同一段场景嘅
        既有粤文字幕，作为参考材料。

        每条英文字幕都要输出一条粤文字幕。译文要准确表达英文字幕嘅意思、
        语气、戏剧意图同说话人意图。既有粤文字幕系角色名、专名、重复术语、
        语域同固定讲法嘅参考；当佢同英文字幕意思兼容时，尽量沿用。
        如果英文字幕同既有粤文字幕有分别，要优先按英文意思翻译，同时保留
        已经建立好嘅名词同称呼。

        输出内容只可以系生成嘅粤文字幕正文。绝对唔好附加英文、备注、解释、标签、
        替代译文、方括号内容、括号内容，或者任何字幕以外嘅说明。
        """)
    """Base system prompt."""

    # Query fields
    src_1_pfx: ClassVar[str] = "eng_"
    """Prefix for English source fields in query."""

    src_1_desc_tpl: ClassVar[str] = "要翻译成粤文嘅英文字幕 {idx}"
    """Description template for English source fields in query."""

    src_2_pfx: ClassVar[str] = "yuewen_reference_"
    """Prefix for written Cantonese reference fields in query."""

    src_2_desc_tpl: ClassVar[str] = "同一段场景嘅既有粤文参考字幕 {idx}"
    """Description template for written Cantonese reference fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "yuewen_"
    """Prefix for generated written Cantonese output fields in answer."""

    output_desc_tpl: ClassVar[str] = "字幕 {idx} 对应嘅粤文译文"
    """Description template for generated written Cantonese output fields."""


class YueEngGuidedTranslationPromptYueHant(YueEngGuidedTranslationPromptYueHans):
    """Text for traditional guided written Cantonese translation from English."""

    opencc_config = OpenCCConfig.s2hk
    """Config for converting simplified Chinese characters from the parent class."""
