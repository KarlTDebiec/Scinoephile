#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for translation of 粤文 from 中文."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.lang.yue.prompts import YueHansPrompt
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.llms.dual_block_gapped import DualBlockGappedPrompt

__all__ = [
    "YueHansFromZhoTranslationPrompt",
    "YueHantFromZhoTranslationPrompt",
]


class YueHansFromZhoTranslationPrompt(DualBlockGappedPrompt, YueHansPrompt):
    """Text for LLM correspondence for translation of 简体粤文 from 中文."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text(
        """
        你而家要核对一对对嘅粤文同中文字幕。有啲粤文字幕因为音频识别唔到而缺失。
        每当某行粤文字幕系空嘅，就用对应嗰行中文，翻译成书面粤语，语气同用词要贴近周边现有嘅粤文字幕嘅口
        语风格。
        如果嗰行粤文字幕已经有内容，唔好改，嗰行请输出空字串。
        只要你有提供翻译，就再加一段简短英文备注，简述你改动嘅重点。
        如果唔需要翻译，译文同备注都必须系空字串。
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

    output_desc_tpl: ClassVar[str] = '字幕 {idx} 译好后嘅粤文；如果唔需要翻译请输出 ""'
    """Description template for output fields in answer."""

    note_pfx: ClassVar[str] = "beizhu_"
    """Prefix for note fields in answer."""

    note_desc_tpl: ClassVar[str] = '字幕 {idx} 嘅英文备注；如果冇提供翻译请输出 ""'
    """Description template for note fields in answer."""

    # Test case validation errors
    output_unmodified_err_tpl: ClassVar[str] = (
        "字幕 {idx} 已经有粤文内容，嗰行输出必须系空字串。"
    )
    """Error template when output is present but unmodified relative to source one."""

    output_missing_note_present_err_tpl: ClassVar[str] = (
        "字幕 {idx} 冇译文，但你提供咗备注；请同样输出空字串。"
    )
    """Error template when output is missing but note is present."""

    output_present_note_missing_err_tpl: ClassVar[str] = (
        "字幕 {idx} 有译文，但冇备注；提供译文时必须一齐提供备注。"
    )
    """Error template when output is present but note is missing."""


class YueHantFromZhoTranslationPrompt(YueHansFromZhoTranslationPrompt):
    """Text for LLM correspondence for translation of 繁体粤文 from 中文."""

    opencc_config = OpenCCConfig.s2hk
    """Config with which to convert characters from 简体中文 present in parent class."""
