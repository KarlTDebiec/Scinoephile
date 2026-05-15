#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for guided written Cantonese translation from standard Chinese."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.dictionaries import DictionaryToolPrompt
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.yue.prompts import PromptYueHans
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.dual_n_to_m import DualNToMPrompt

__all__ = [
    "YueGuidedTranslationVsZhoPromptYueHans",
    "YueGuidedTranslationVsZhoPromptYueHant",
]


class YueGuidedTranslationVsZhoPromptYueHans(
    DictionaryToolPrompt, DualNToMPrompt, PromptYueHans
):
    """Text for simplified guided written Cantonese translation from Chinese."""

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
        你负责根据中文字幕，创作对应嘅粤文字幕。你亦会收到同一段场景嘅
        既有粤文字幕，作为参考材料。

        每条中文字幕都要输出一条粤文字幕。译文要准确表达中文字幕嘅意思、
        语气、戏剧意图同说话人意图。既有粤文字幕系角色名、专名、重复术语、
        语域同固定讲法嘅参考；当佢同中文字幕意思兼容时，尽量沿用。
        如果中文字幕同既有粤文字幕有分别，要优先按中文字幕意思翻译，同时保留
        已经建立好嘅名词同称呼。

        输出内容只可以系生成嘅粤文字幕正文。绝对唔好附加英文、备注、解释、标签、
        替代译文、方括号内容、括号内容，或者任何字幕以外嘅说明。
        """)
    """Base system prompt."""

    # Query fields
    src_1_pfx: ClassVar[str] = "zhongwen_"
    """Prefix for Chinese source fields in query."""

    src_1_desc_tpl: ClassVar[str] = "要翻译成粤文嘅中文字幕 {idx}"
    """Description template for Chinese source fields in query."""

    src_2_pfx: ClassVar[str] = "yuewen_reference_"
    """Prefix for written Cantonese reference fields in query."""

    src_2_desc_tpl: ClassVar[str] = "同一段场景嘅既有粤文参考字幕 {idx}"
    """Description template for written Cantonese reference fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "yuewen_"
    """Prefix for generated written Cantonese output fields in answer."""

    output_desc_tpl: ClassVar[str] = "字幕 {idx} 对应嘅粤文译文"
    """Description template for generated written Cantonese output fields."""


class YueGuidedTranslationVsZhoPromptYueHant(YueGuidedTranslationVsZhoPromptYueHans):
    """Text for traditional guided written Cantonese translation from Chinese."""

    opencc_config = OpenCCConfig.s2hk
    """Config for converting simplified Chinese characters from the parent class."""
