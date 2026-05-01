#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for translation of 粤文 from 中文."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.dictionaries import DictionaryToolPrompt
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.yue.prompts import YueHansPrompt
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.llms.dual_block_gapped import DualBlockGappedPrompt

__all__ = [
    "YueVsZhoYueHansTranslationPrompt",
    "YueVsZhoYueHantTranslationPrompt",
]


class YueVsZhoYueHansTranslationPrompt(
    DictionaryToolPrompt, DualBlockGappedPrompt, YueHansPrompt
):
    """Text for LLM correspondence for translation of 简体粤文 from 中文."""

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
    base_system_prompt: ClassVar[str] = dedent_and_compact(
        """
        你负责根据对应嘅中文字幕，补翻译缺失咗嘅粤文字幕。
        只有当某行现有粤文字幕系空字串时，先需要提供译文。
        如果某行已经有粤文内容，唔好改，嗰行请输出空字串。
        译文要用自然、通顺嘅书面粤语，语气同用词要尽量贴近附近已有嘅粤文字幕。
        中文字幕只系参考；译文唔需要逐字对应，但要准确表达该行意思。
        输出内容只可以系字幕正文本身，绝对唔好附加英文、备注、解释、标签、
        方括号内容、括号内容，或者任何译文以外嘅说明。
        如果唔需要翻译，就输出空字串。
        """
    )
    """Base system prompt."""

    # Query fields
    src_1_pfx: ClassVar[str] = "yuewen_"
    """Prefix for source one fields in query."""

    src_1_desc_tpl: ClassVar[str] = "字幕 {idx} 现有嘅粤文内容；如果系空就代表要翻译"
    """Description template for source one fields in query."""

    src_2_pfx: ClassVar[str] = "zhongwen_"
    """Prefix for source two fields in query."""

    src_2_desc_tpl: ClassVar[str] = "字幕 {idx} 对应嘅中文字幕"
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


class YueVsZhoYueHantTranslationPrompt(YueVsZhoYueHansTranslationPrompt):
    """Text for LLM correspondence for translation of 繁体粤文 from 中文."""

    opencc_config = OpenCCConfig.s2hk
    """Config with which to convert characters from 简体中文 present in parent class."""
