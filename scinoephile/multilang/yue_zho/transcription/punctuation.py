#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Written Cantonese/standard Chinese transcription punctuation."""

from __future__ import annotations

from functools import partial
from typing import ClassVar, Self

from pydantic import model_validator

from scinoephile.core import Language
from scinoephile.core.llms import TestCase
from scinoephile.core.text import (
    dedent_and_compact,
    remove_non_punc_and_whitespace,
    remove_punc_and_whitespace,
)
from scinoephile.lang.yue.prompts import YUE_HANT_PROMPT_FIELDS
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_text_converted
from scinoephile.llms.punctuation import (
    PunctuationManager,
    PunctuationPrompt,
    PunctuationTestCase,
)

__all__ = [
    "YuePunctuationVsZhoPromptYueHans",
    "YuePunctuationVsZhoPromptYueHant",
    "YueZhoPunctuationManager",
    "YueZhoPunctuationTestCase",
]


YuePunctuationVsZhoPromptYueHant = PunctuationPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責將廣東話口語嘅粵文字幕同對應嘅中文字幕對齊。
        你會收到一條中文字幕，以及同一條字幕對應嘅多行粵文轉寫。
        多行粵文代表口語停頓拆開嘅行。
        你嘅主要任務係為粵文補上標點同空格。
        請先將所有粵文行整理成一行，再參考中文字幕補上標點同空格。
        必須包含所有粵文字，整理成一行。
        唔好從中文字幕拷貝漢字。
        只可以調整粵文嘅標點同空格以配合中文字幕。
        除咗標點同空格之外唔好改任何粵文內容。"""),
    src_1="yuewen_to_punctuate",
    src_1_desc="要整理同加標點嘅粵文字幕行",
    src_2="zhongwen",
    src_2_desc="對應嘅中文字幕",
    src_1_missing_err="查詢必須包含要整理同加標點嘅粵文字幕行。",
    src_2_missing_err="查詢必須包含對應嘅中文字幕。",
    output="yuewen_punctuated",
    output_desc="整理同加標點後嘅粵文字幕",
    output_missing_err="答案必須包含整理同加標點後嘅粵文字幕。",
    src_1_chars_changed_err_tpl=(
        "Answer's written Cantonese subtitle stripped of punctuation and whitespace "
        "does not match query's written Cantonese subtitle concatenated:\n"
        "Expected: {expected}\n"
        "Received: {received}"
    ),
)
"""Text for traditional written Cantonese/standard Chinese punctuation."""

YuePunctuationVsZhoPromptYueHans = YuePunctuationVsZhoPromptYueHant.transformed(
    Language.yue_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.hk2s),
)
"""Text for simplified written Cantonese/standard Chinese punctuation."""


class YueZhoPunctuationTestCase(PunctuationTestCase):
    """Written Cantonese punctuation guided by standard Chinese."""

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty from output and guide punctuation.

        Returns:
            minimum difficulty
        """
        min_difficulty = super().get_min_difficulty()
        if self.answer is None:
            return min_difficulty

        if remove_non_punc_and_whitespace(self.answer.output):
            min_difficulty = max(min_difficulty, 1)
        if remove_non_punc_and_whitespace(
            self.query.guide
        ) != remove_non_punc_and_whitespace(self.answer.output):
            min_difficulty = max(min_difficulty, 2)
        return min_difficulty

    @model_validator(mode="after")
    def validate_output_characters(self) -> Self:
        """Ensure query and answer together are valid.

        Returns:
            validated test case
        """
        if self.answer is None:
            return self

        expected = "".join(
            remove_punc_and_whitespace(subtitle) for subtitle in self.query.subtitles
        )
        received = remove_punc_and_whitespace(self.answer.output)
        if expected != received:
            raise ValueError(self.prompt.src_1_chars_changed_err(expected, received))
        return self


class YueZhoPunctuationManager(PunctuationManager):
    """Factories for written Cantonese/standard Chinese punctuation LLM classes."""

    test_case_base_cls: ClassVar[type[TestCase]] = YueZhoPunctuationTestCase
    """Static test-case model defining Yue/Zho punctuation semantics."""
