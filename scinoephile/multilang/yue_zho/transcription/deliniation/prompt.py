#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for simplified written Cantonese deliniation."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.eng.prompts import PromptEng
from scinoephile.lang.yue.prompts import PromptYueHans, PromptYueHant
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.dual_2_to_2 import Dual2To2Prompt

__all__ = [
    "YueDeliniationVsZhoPromptYueHans",
    "YueDeliniationVsZhoPromptYueHant",
]


class YueDeliniationVsZhoPromptYueHant(Dual2To2Prompt, PromptEng, PromptYueHant):
    """Text for LLM correspondence for traditional written Cantonese deliniation."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你負責將廣東話口語嘅粵文字幕同對應嘅中文字幕對齊。
        你會收到一條中文字幕 (zhongwen_1) 同一條初步粵文字幕 (yuewen_1)，
        以及第二條中文字幕 (zhongwen_2) 同第二條初步粵文字幕 (yuewen_2)。
        請閲讀 zhongwen_1、zhongwen_2 同 yuewen_1、yuewen_2，
        調整 yuewen_1 同 yuewen_2 之間嘅分界，使內容同 zhongwen_1 同 zhongwen_2 對齊。
        即係將 yuewen_1 末尾嘅字符移到 yuewen_2 開頭，
        或者將 yuewen_2 開頭嘅字符移到 yuewen_1 末尾。
        請喺 yuewen_1_yidong 同 yuewen_2_yidong 返回調整後嘅粵文字幕。
        如果唔需要調整，請 yuewen_1_yidong 同 yuewen_2_yidong 都返回空字串。""")
    """Base system prompt."""

    # Query fields
    src_1_sub_1: ClassVar[str] = "zhongwen_1"
    """Name of source one subtitle one field in query."""

    src_1_sub_1_desc: ClassVar[str] = "已知字幕1嘅中文"
    """Description of source one subtitle one field in query."""

    src_1_sub_2: ClassVar[str] = "zhongwen_2"
    """Name of source one subtitle two field in query."""

    src_1_sub_2_desc: ClassVar[str] = "已知字幕2嘅中文"
    """Description of source one subtitle two field in query."""

    src_2_sub_1: ClassVar[str] = "yuewen_1"
    """Name of source two subtitle one field in query."""

    src_2_sub_1_desc: ClassVar[str] = "初步字幕1嘅粵文"
    """Description of source two subtitle one field in query."""

    src_2_sub_2: ClassVar[str] = "yuewen_2"
    """Name of source two subtitle two field in query."""

    src_2_sub_2_desc: ClassVar[str] = "初步字幕2嘅粵文"
    """Description of source two subtitle two field in query."""

    # Query validation errors
    src_2_sub_1_sub_2_missing_err: ClassVar[str] = (
        "查詢要有 yuewen_1、yuewen_2，或者兩個都有。"
    )
    """Error when src_2_sub_1 and src_2_sub_2 fields are missing."""

    # Answer fields
    src_2_sub_1_shifted: ClassVar[str] = "yuewen_1_yidong"
    """Name of shifted source two subtitle one field in answer."""

    src_2_sub_1_shifted_desc: ClassVar[str] = "調整後字幕1嘅粵文"
    """Description of shifted source two subtitle one field in answer."""

    src_2_sub_2_shifted: ClassVar[str] = "yuewen_2_yidong"
    """Name of shifted source two subtitle two field in answer."""

    src_2_sub_2_shifted_desc: ClassVar[str] = "調整後字幕2嘅粵文"
    """Description of shifted source two subtitle two field in answer."""

    # Test case validation errors
    src_2_sub_1_sub_2_unchanged_err: ClassVar[str] = (
        "回答嘅 yuewen_1_yidong 同 yuewen_2_yidong 同查詢嘅 yuewen_1、yuewen_2 "
        "一樣；如果唔需要調整，yuewen_1_yidong 同 yuewen_2_yidong 要返空字串。"
    )
    """Error when src_2_sub_1 and src_2_sub_2 are unchanged."""

    src_2_chars_changed_err_tpl: ClassVar[str] = (
        "回答裏拼埋嘅 yuewen_1_yidong 同 yuewen_2_yidong 同查詢拼埋嘅 yuewen_1 "
        "同 yuewen_2 唔一致：\n"
        "期望: {expected}\n"
        "收到: {received}"
    )
    """Error template when shifted source two characters do not match original."""

    @classmethod
    def src_2_chars_changed_err(cls, expected: str, received: str) -> str:
        """Error when shifted source two characters do not match original.

        Arguments:
            expected: expected concatenated source two characters
            received: received concatenated source two characters
        Returns:
            formatted error message
        """
        return cls.src_2_chars_changed_err_tpl.format(
            expected=expected, received=received
        )


class YueDeliniationVsZhoPromptYueHans(YueDeliniationVsZhoPromptYueHant, PromptYueHans):
    """Text for LLM correspondence for simplified written Cantonese deliniation."""

    opencc_config = OpenCCConfig.hk2s
    """Config for converting traditional Chinese characters from the parent class."""
