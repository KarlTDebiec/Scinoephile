#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Splits 粤文 text between two nascent 粤文 texts based on corresponding 中文."""

from __future__ import annotations

from scinoephile.audio.models import SplitAnswer, SplitQuery
from scinoephile.audio.testing import SplitTestCase
from scinoephile.core.abcs import LLMQueryer


class CantoneseSplitter(LLMQueryer[SplitQuery, SplitAnswer, SplitTestCase]):
    """Splits 粤文 text between two nascent 粤文 texts based on corresponding 中文."""

    @property
    def answer_cls(self) -> type[SplitAnswer]:
        """Answer class."""
        return SplitAnswer

    @property
    def answer_example(self) -> SplitAnswer:
        """Example answer."""
        return SplitAnswer(
            one_yuewen_to_append="粤文 one to append",
            two_yuewen_to_prepend="粤文 text two to prepend",
        )

    @property
    def answer_template(self) -> str:
        """Answer template."""
        return (
            "粤文 to append to one:\n{one_yuewen_to_append}\n"
            "粤文 to prepend to two:\n{two_yuewen_to_prepend}\n"
        )

    @property
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
        Your response must be a JSON object with the following structure:
        """

    @property
    def query_cls(self) -> type[SplitQuery]:
        """Query class."""
        return SplitQuery

    @property
    def query_template(self) -> str:
        """Query template."""
        return (
            "中文 one:\n{one_zhongwen}\n"
            "粤文 one start:\n{one_yuewen_start}\n"
            "中文 two:\n{two_zhongwen}\n"
            "粤文 two end:\n{two_yuewen_end}\n"
            "粤文 to split:\n{yuewen_to_split}\n"
        )

    @property
    def test_case_cls(self) -> type[SplitTestCase]:
        """Test case class."""
        return SplitTestCase
