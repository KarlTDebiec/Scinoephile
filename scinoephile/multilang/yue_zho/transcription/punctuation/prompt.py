#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for written Cantonese/standard Chinese transcription punctuation."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.yue.prompts import PromptYueHans, PromptYueHant
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.dual_n_to_1 import DualNTo1Prompt

__all__ = [
    "YuePunctuationVsZhoPromptYueHans",
    "YuePunctuationVsZhoPromptYueHant",
]


class YuePunctuationVsZhoPromptYueHant(DualNTo1Prompt, PromptYueHant):
    """Text for traditional written Cantonese/standard Chinese punctuation."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你負責將廣東話口語嘅粵文字幕同對應嘅中文字幕對齊。
        你會收到一條中文字幕，以及同一條字幕對應嘅多行粵文轉寫。
        多行粵文代表口語停頓拆開嘅行。
        你嘅主要任務係為粵文補上標點同空格。
        請先將所有粵文行整理成一行，再參考中文字幕補上標點同空格。
        必須包含所有粵文字，整理成一行。
        唔好從中文字幕拷貝漢字。
        只可以調整粵文嘅標點同空格以配合中文字幕。
        除咗標點同空格之外唔好改任何粵文內容。""")
    """Base system prompt."""

    # Query fields
    src_1: ClassVar[str] = "yuewen_to_punctuate"
    """Name of source one field in query."""

    src_1_desc: ClassVar[str] = "要整理同加標點嘅粵文字幕行"
    """Description of source one field in query."""

    src_2: ClassVar[str] = "zhongwen"
    """Name of source two field in query."""

    src_2_desc: ClassVar[str] = "對應嘅中文字幕"
    """Description of source two field in query."""

    # Query validation errors
    src_1_missing_err: ClassVar[str] = "查詢必須包含要整理同加標點嘅粵文字幕行。"
    """Error when source one field is missing from query."""

    src_2_missing_err: ClassVar[str] = "查詢必須包含對應嘅中文字幕。"
    """Error when source two field is missing from query."""

    # Answer fields
    output: ClassVar[str] = "yuewen_punctuated"
    """Name of output field in answer."""

    output_desc: ClassVar[str] = "整理同加標點後嘅粵文字幕"
    """Description of output field in answer."""

    # Answer validation errors
    output_missing_err: ClassVar[str] = "答案必須包含整理同加標點後嘅粵文字幕。"
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


class YuePunctuationVsZhoPromptYueHans(YuePunctuationVsZhoPromptYueHant, PromptYueHans):
    """Text for simplified written Cantonese/standard Chinese punctuation."""

    opencc_config = OpenCCConfig.hk2s
    """Config for converting traditional Chinese characters from the parent class."""
