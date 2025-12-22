#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for 粤文 shifting."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.lang.eng.prompts import EngPrompt
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.llms.dual_pair import DualPairPrompt

__all__ = [
    "YueZhoHansShiftingPrompt",
    "YueZhoHantShiftingPrompt",
]


class YueZhoHansShiftingPrompt(DualPairPrompt, EngPrompt):
    """Text for LLM correspondence for 粤文 shifting."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        你负责将广东话口语嘅简体粤文字幕同对应嘅中文字幕对齐。
        你会收到一条中文字幕 (zhongwen_1) 同一条初步简体粤文字幕 (yuewen_1)，
        以及第二条中文字幕 (zhongwen_2) 同第二条初步简体粤文字幕 (yuewen_2)。
        请阅读 zhongwen_1、zhongwen_2 同 yuewen_1、yuewen_2，
        调整 yuewen_1 同 yuewen_2 之间嘅分界，使内容同 zhongwen_1 同 zhongwen_2 对齐。
        即系将 yuewen_1 末尾嘅字符移到 yuewen_2 开头，
        或者将 yuewen_2 开头嘅字符移到 yuewen_1 末尾。
        请喺 yuewen_1_shifted 同 yuewen_2_shifted 返回调整后嘅简体粤文字幕。
        如果唔需要调整，请 yuewen_1_shifted 同 yuewen_2_shifted 都返回空字串。""")
    """Base system prompt."""

    # Query fields
    src_1_sub_1: ClassVar[str] = "zhongwen_1"
    """Name of source one subtitle one field in query."""

    src_1_sub_1_desc: ClassVar[str] = "Known 中文 of subtitle 1"
    """Description of source one subtitle one field in query."""

    src_1_sub_2: ClassVar[str] = "zhongwen_2"
    """Name of source one subtitle two field in query."""

    src_1_sub_2_desc: ClassVar[str] = "Known 中文 of subtitle 2"
    """Description of source one subtitle two field in query."""

    src_2_sub_1: ClassVar[str] = "yuewen_1"
    """Name of source two subtitle one field in query."""

    src_2_sub_1_desc: ClassVar[str] = "Transcribed 简体粤文 of subtitle 1"
    """Description of source two subtitle one field in query."""

    src_2_sub_2: ClassVar[str] = "yuewen_2"
    """Name of source two subtitle two field in query."""

    src_2_sub_2_desc: ClassVar[str] = "Transcribed 简体粤文 of subtitle 2"
    """Description of source two subtitle two field in query."""

    # Query validation errors
    src_2_sub_1_sub_2_missing_err: ClassVar[str] = (
        "Query must have yuewen_1, yuewen_2, or both."
    )
    """Error when src_2_sub_1 and src_2_sub_2 fields are missing."""

    # Answer fields
    src_2_sub_1_shifted: ClassVar[str] = "yuewen_1_shifted"
    """Name of shifted source two subtitle one field in answer."""

    src_2_sub_1_shifted_desc: ClassVar[str] = "Shifted 简体粤文 of subtitle 1"
    """Description of shifted source two subtitle one field in answer."""

    src_2_sub_2_shifted: ClassVar[str] = "yuewen_2_shifted"
    """Name of shifted source two subtitle two field in answer."""

    src_2_sub_2_shifted_desc: ClassVar[str] = "Shifted 简体粤文 of subtitle 2"
    """Description of shifted source two subtitle two field in answer."""

    # Test case validation errors
    src_2_sub_1_sub_2_unchanged_err: ClassVar[str] = (
        "Answer's yuewen_1_shifted and yuewen_2_shifted are equal to query's yuewen_1 "
        "and yuewen_2; if no shift is needed, yuewen_1_shifted and yuewen_2_shifted "
        "must be empty strings."
    )
    """Error when src_2_sub_1 and src_2_sub_2 are unchanged."""

    src_2_chars_changed_err_tpl: ClassVar[str] = (
        "Answer's concatenated yuewen_1_shifted and yuewen_2_shifted does not match "
        "query's concatenated yuewen_1 and yuewen_2:\n"
        "Expected: {expected}\n"
        "Received: {received}"
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


class YueZhoHantShiftingPrompt(YueZhoHansShiftingPrompt):
    """Text for LLM correspondence for 粤文 shifting."""

    opencc_config = OpenCCConfig.s2hk
    """Config with which to convert characters from 简体中文 present in parent class."""
