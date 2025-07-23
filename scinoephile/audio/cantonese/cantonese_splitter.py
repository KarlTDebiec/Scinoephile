#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Splits 粤文 text between two nascent 粤文 texts based on corresponding 中文."""

from __future__ import annotations

from typing import override

from scinoephile.audio.cantonese.models import SplitAnswer, SplitQuery, SplitTestCase
from scinoephile.core.abcs import LLMQueryer


class CantoneseSplitter(LLMQueryer[SplitQuery, SplitAnswer, SplitTestCase]):
    """Splits 粤文 text between two nascent 粤文 texts based on corresponding 中文."""

    @property
    @override
    def answer_cls(self) -> type[SplitAnswer]:
        """Answer class."""
        return SplitAnswer

    @property
    @override
    def answer_example(self) -> SplitAnswer:
        """Example answer."""
        return SplitAnswer(
            one_yuewen_to_append="粤文 one to append",
            two_yuewen_to_prepend="粤文 text two to prepend",
        )

    @property
    @override
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        You are a helpful assistant that matches 粤文 subtitles of spoken Cantonese
        to 中文 subtitles of the same spoken content. You will be given a 中文
        subtitle and its nascent 粤文 subtitle, and a second 中文 subtitle with its
        nascent 粤文 subtitle. You will be given and additional 粤文 text whose
        distribution between the two subtitles is ambiguous, and you will determine
        how the 粤文 text should be distributed between the two nascent 粤文
        subtitles.
        Include all characters "ambiguous 粤文" in either "one" or "two".
        Do not copy "Nascent 粤文 one" into "one", nor "Nascent 粤文 two" into "two".
        Your output "one" and "two" concatenated should equal "ambiguous 粤文".
        """

    @property
    @override
    def query_cls(self) -> type[SplitQuery]:
        """Query class."""
        return SplitQuery

    @property
    @override
    def test_case_cls(self) -> type[SplitTestCase]:
        """Test case class."""
        return SplitTestCase
