#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Distributes 粤文 text based on corresponding 中文."""

from __future__ import annotations

from functools import cached_property
from typing import override

from scinoephile.audio.cantonese.distribution.distribute_answer import DistributeAnswer
from scinoephile.audio.cantonese.distribution.distribute_query import DistributeQuery
from scinoephile.audio.cantonese.distribution.distribute_test_case import (
    DistributeTestCase,
)
from scinoephile.core.abcs import LLMQueryer


class Distributor(LLMQueryer[DistributeQuery, DistributeAnswer, DistributeTestCase]):
    """Distributes 粤文 text based on corresponding 中文."""

    @cached_property
    @override
    def answer_example(self) -> DistributeAnswer:
        """Example answer."""
        return DistributeAnswer(
            one_yuewen_to_append="粤文 to append to 粤文 text one",
            two_yuewen_to_prepend="粤文 to prepend to 粤文 text two",
        )

    @cached_property
    @override
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        # TODO: Review this prompt
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
