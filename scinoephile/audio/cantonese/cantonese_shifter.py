#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shifts 粤文 text between adjacent subtitles based on 中文."""

from __future__ import annotations

from typing import override

from scinoephile.audio.cantonese.models import ShiftAnswer, ShiftQuery, ShiftTestCase
from scinoephile.core.abcs import LLMQueryer


class CantoneseShifter(LLMQueryer[ShiftQuery, ShiftAnswer, ShiftTestCase]):
    """Shifts 粤文 text between adjacent subtitles based on 中文."""

    @property
    @override
    def answer_cls(self) -> type[ShiftAnswer]:
        """Answer class."""
        return ShiftAnswer

    @property
    @override
    def answer_example(self) -> ShiftAnswer:
        """Example answer."""
        return ShiftAnswer(
            one_yuewen_shifted="粤文 one shifted",
            two_yuewen_shifted="粤文 two shifted",
        )

    @property
    @override
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        You are a helpful assistant that shifts the start of the second 粤文
        subtitle so that two 粤文 subtitles match the contents of their corresponding
        中文 subtitles.
        Include all 粤文 characters from the inputs.
        Do not add or remove characters.
        """

    @property
    @override
    def query_cls(self) -> type[ShiftQuery]:
        """Query class."""
        return ShiftQuery

    @property
    @override
    def test_case_cls(self) -> type[ShiftTestCase]:
        """Test case class."""
        return ShiftTestCase
