#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shifts 粤文 text between adjacent subtitles based on corresponding 中文."""

from __future__ import annotations

from functools import cached_property
from typing import override

from scinoephile.audio.cantonese.shifting.shift_answer import ShiftAnswer
from scinoephile.audio.cantonese.shifting.shift_query import ShiftQuery
from scinoephile.audio.cantonese.shifting.shift_test_case import ShiftTestCase
from scinoephile.core.abcs import LLMQueryer


class Shifter(LLMQueryer[ShiftQuery, ShiftAnswer, ShiftTestCase]):
    """Shifts 粤文 text between adjacent subtitles based on corresponding 中文."""

    @cached_property
    @override
    def answer_example(self) -> ShiftAnswer:
        """Example answer."""
        return ShiftAnswer(
            one_yuewen_shifted="粤文 one shifted",
            two_yuewen_shifted="粤文 two shifted",
        )

    @cached_property
    @override
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        Read the two consecutive 中文 texts and two consecutive 粤文 texts, and adjust
        the breakpoint between the first and second 粤文 texts so that they align with
        the two corresponding 中文 texts.
        This is, either shift characters from the end of the first 粤文 text to the
        beginning of the second 粤文 text, or shift characters from the beginning of
        the second 粤文 text to the end of the first 粤文 text.
        If no changes are needed, return the original 粤文 texts.
        Include all 粤文 characters from the inputs in the same order in the outputs.
        Do not copy punctuation or whitespace from the 中文 texts.
        """

    @property
    def test_case_log_str(self) -> str:
        """String representation of all test cases in the log.

        If the test case asks for the 粤文 text to be shifted, difficulty is 1.
        If the test case is set to be included in the prompt, difficulty is 2.
        """
        test_case_log_str = "[\n"

        for key, value in self._test_case_log.items():
            source_str: str = value.source_str[:-1]

            difficulty = value.difficulty
            if value.one_yuewen != value.one_yuewen_shifted:
                difficulty = 1
            if value.two_yuewen != value.two_yuewen_shifted:
                difficulty = 1
            if key in self._examples_log:
                difficulty = 2
                source_str += "    prompt=True,\n"
            if key in self._verified_log:
                source_str += "    verified=True,\n"
            if difficulty:
                source_str += f"    difficulty={difficulty},\n"
            source_str += ")"
            test_case_log_str += f"{source_str},\n"
        test_case_log_str += "\n]"
        return test_case_log_str
