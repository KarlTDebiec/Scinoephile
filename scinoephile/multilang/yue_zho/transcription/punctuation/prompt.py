#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for written Cantonese/standard Chinese transcription punctuation."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.yue.prompts import YueHansPrompt
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.llms.dual_multi_single import DualMultiSinglePrompt

__all__ = [
    "YueVsZhoYueHansPunctuationPrompt",
    "YueVsZhoYueHantPunctuationPrompt",
]


class YueVsZhoYueHansPunctuationPrompt(DualMultiSinglePrompt, YueHansPrompt):
    """Text for simplified written Cantonese/standard Chinese punctuation."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你负责将广东话口语嘅简体粤文字幕同对应嘅中文字幕对齐。
        你会收到一条中文字幕，以及同一条字幕对应嘅多行简体粤文转写。
        多行简体粤文代表口语停顿拆开嘅行。
        你嘅主要任务系为简体粤文补上标点同空格。
        请先将所有简体粤文行整理成一行，再参考中文字幕补上标点同空格。
        必须包含所有简体粤文字，整理成一行。
        唔好从中文字幕拷贝汉字。
        只可以调整简体粤文嘅标点同空格以配合中文字幕。
        除咗标点同空格之外唔好改任何简体粤文内容。""")
    """Base system prompt."""

    # Query fields
    src_1: ClassVar[str] = "yuewen_to_punctuate"
    """Name of source one field in query."""

    src_1_desc: ClassVar[str] = "要整理同加标点嘅简体粤文字幕行"
    """Description of source one field in query."""

    src_2: ClassVar[str] = "zhongwen"
    """Name of source two field in query."""

    src_2_desc: ClassVar[str] = "对应嘅中文字幕"
    """Description of source two field in query."""

    # Query validation errors
    src_1_missing_err: ClassVar[str] = "查询必须包含要整理同加标点嘅简体粤文字幕行。"
    """Error when source one field is missing from query."""

    src_2_missing_err: ClassVar[str] = "查询必须包含对应嘅中文字幕。"
    """Error when source two field is missing from query."""

    # Answer fields
    output: ClassVar[str] = "yuewen_punctuated"
    """Name of output field in answer."""

    output_desc: ClassVar[str] = "整理同加标点后嘅简体粤文字幕"
    """Description of output field in answer."""

    # Answer validation errors
    output_missing_err: ClassVar[str] = "答案必须包含整理同加标点后嘅简体粤文字幕。"
    """Error when output field is missing from answer."""

    # Test case validation errors
    yuewen_chars_changed_err_tpl: ClassVar[str] = (
        "Answer's written Cantonese subtitle stripped of punctuation and whitespace "
        "does not match query's written Cantonese subtitle concatenated:\n"
        "Expected: {expected}\n"
        "Received: {received}"
    )
    """Error when punctuated written Cantonese characters do not match original."""

    @classmethod
    def yuewen_chars_changed_err(cls, expected: str, received: str) -> str:
        """Error when punctuated written Cantonese characters do not match original.

        Arguments:
            expected: expected written Cantonese characters
            received: received written Cantonese characters
        Returns:
            error message
        """
        return cls.yuewen_chars_changed_err_tpl.format(
            expected=expected, received=received
        )


class YueVsZhoYueHantPunctuationPrompt(YueVsZhoYueHansPunctuationPrompt):
    """Text for traditional written Cantonese/standard Chinese punctuation."""

    opencc_config = OpenCCConfig.s2hk
    """Config for converting simplified Chinese characters from the parent class."""
