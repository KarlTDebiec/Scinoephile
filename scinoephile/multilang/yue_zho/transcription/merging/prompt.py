#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for 粤文/中文 transcription merging."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.lang.yue.prompts import YueHansPrompt
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.llms.dual_multi_single import DualMultiSinglePrompt

__all__ = [
    "YueZhoHansMergingPrompt",
    "YueZhoHantMergingPrompt",
]


class YueZhoHansMergingPrompt(DualMultiSinglePrompt, YueHansPrompt):
    """Text for LLM correspondence for 简体粤文/中文 transcription merging."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        你负责将广东话口语嘅简体粤文字幕同对应嘅中文字幕对齐。
        你会收到一条中文字幕，以及同一条字幕对应嘅多行简体粤文转写。
        多行简体粤文代表口语停顿拆开嘅行。
        请将所有简体粤文行合并成一行，并参考中文字幕嘅标点同空格。
        必须包含所有简体粤文字，合并成一行。
        唔好从中文字幕拷贝汉字。
        只可以调整简体粤文嘅标点同空格以配合中文字幕。
        除咗标点同空格之外唔好改任何简体粤文内容。""")
    """Base system prompt."""

    # Query fields
    src_1: ClassVar[str] = "yuewen_to_merge"
    """Name of source one field in query."""

    src_1_desc: ClassVar[str] = "要合并嘅简体粤文字幕行"
    """Description of source one field in query."""

    src_2: ClassVar[str] = "zhongwen"
    """Name of source two field in query."""

    src_2_desc: ClassVar[str] = "对应嘅中文字幕"
    """Description of source two field in query."""

    # Query validation errors
    src_1_missing_err: ClassVar[str] = "查询必须包含要合并嘅简体粤文字幕行。"
    """Error when source one field is missing from query."""

    src_2_missing_err: ClassVar[str] = "查询必须包含对应嘅中文字幕。"
    """Error when source two field is missing from query."""

    # Answer fields
    output: ClassVar[str] = "yuewen_merged"
    """Name of output field in answer."""

    output_desc: ClassVar[str] = "合并后嘅简体粤文字幕"
    """Description of output field in answer."""

    # Answer validation errors
    output_missing_err: ClassVar[str] = "答案必须包含合并后嘅简体粤文字幕。"
    """Error when output field is missing from answer."""

    # Test case validation errors
    yuewen_chars_changed_err_tpl: ClassVar[str] = (
        "Answer's 粤文 subtitle stripped of punctuation and whitespace does not match "
        "query's 粤文 subtitle concatenated:\n"
        "Expected: {expected}\n"
        "Received: {received}"
    )
    """Error template when merged 粤文 characters do not match original."""

    @classmethod
    def yuewen_chars_changed_err(cls, expected: str, received: str) -> str:
        """Error when merged 粤文 characters do not match original.

        Arguments:
            expected: expected 粤文 characters
            received: received 粤文 characters
        Returns:
            error message
        """
        return cls.yuewen_chars_changed_err_tpl.format(
            expected=expected, received=received
        )


class YueZhoHantMergingPrompt(YueZhoHansMergingPrompt):
    """Text for LLM correspondence for 繁体粤文/中文 transcription merging."""

    opencc_config = OpenCCConfig.s2hk
    """Config with which to convert characters from 简体中文 present in parent class."""
