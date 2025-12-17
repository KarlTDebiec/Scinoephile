#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for 粤文 translation against 中文."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.many_to_many_blockwise import ManyToManyBlockwisePrompt
from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.lang.yue.prompts import YueHansPrompt
from scinoephile.lang.zho.conversion import OpenCCConfig

__all__ = [
    "YueHansTranslationPrompt",
    "YueHantTranslationPrompt",
]


class YueHansTranslationPrompt(ManyToManyBlockwisePrompt, YueHansPrompt):
    """LLM correspondence text for 简体粤文 translation against 中文."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text(
        """
        You are reviewing pairs of 粤文 and 中文 subtitles.  Some 粤文 subtitles are
        missing because they could not be transcribed from the audio.  Whenever a
        粤文 subtitle is empty, translate the corresponding 中文 subtitle into written
        Cantonese that matches the colloquial style of the surrounding 粤文 subtitles.
        If a 粤文 subtitle already contains text, leave it unchanged by returning an
        empty string for that subtitle.
        For every translation you provide, also include a short English note
        summarizing your changes.  When no translation is needed, both the translated
        text and the note must be empty strings.
        """
    )
    """Base system prompt."""

    # Query fields
    source_one_pfx: ClassVar[str] = "yuewen_"
    """Prefix for source one fields in query."""

    source_one_desc_tpl: ClassVar[str] = (
        "已知嘅字幕 {idx} 粤文文本；如果为空代表需要翻译"
    )
    """Description template for subtitle fields in query."""

    source_two_pfx: ClassVar[str] = "zhongwen_"
    """Prefix for source two fields in query."""

    source_two_desc_tpl: ClassVar[str] = "字幕 {idx} 对应嘅中文字幕"
    """Description template for subtitle fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "yuewen_"
    """Prefix for output fields in answer."""

    output_desc_tpl: ClassVar[str] = '字幕 {idx} 翻译后嘅粤文；如果毋需翻译请回传 ""'
    """Description template for output fields in answer."""

    note_pfx: ClassVar[str] = "beizhu_"
    """Prefix of note fields in answer."""

    note_desc_tpl: ClassVar[str] = '字幕 {idx} 嘅英文备注；如果冇提供翻译请回传 ""'
    """Description template for note fields in answer."""

    # Test case validation errors
    output_unmodified_err_tpl: ClassVar[str] = (
        "字幕 {idx} 已经包含粤文文本，输出必须系空字串。"
    )
    """Error template when output is present but unmodified relative to source one."""

    output_missing_note_present_err_tpl: ClassVar[str] = (
        "字幕 {idx} 冇翻译，但你提供咗备注；请同样回传空字串。"
    )
    """Error template when output is missing but note is present."""

    output_present_note_missing_err_tpl: ClassVar[str] = (
        "字幕 {idx} 有翻译，但冇备注；提供译文时必须提供备注。"
    )
    """Error template when output is present but note is missing."""


class YueHantTranslationPrompt(YueHansTranslationPrompt):
    """LLM correspondence text for 繁体粤文 translation against 中文."""

    opencc_config = OpenCCConfig.s2hk
    """Config with which to convert characters from 简体中文 present in parent class."""
