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
from scinoephile.core.abcs import FixedLLMQueryer


class Distributor(
    FixedLLMQueryer[DistributeQuery, DistributeAnswer, DistributeTestCase]
):
    """Distributes 粤文 text based on corresponding 中文."""

    @cached_property
    @override
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        You are responsible for matching 粤文 subtitles of Cantonese speech to 中文 
        subtitles of the same Cantonese speech.
        You will be given a 中文 subtitle and its nascent 粤文 subtitle, and a second 
        中文 subtitle with its nascent 粤文 subtitle.
        You will be given an additional 粤文 text whose distribution between the
        two subtitles is ambiguous, and you will determine how the 粤文 text
        should be distributed between the two nascent 粤文 subtitles, such that
        the content of 粤文 subtitle 1 is aligned with the content of 中文
        subtitle 1, and the content of 粤文 subtitle 2 is aligned with the
        content of 中文 subtitle 2.
        Include all 粤文 to distribute in either "one" or "two".
        Do not copy "粤文 1 start" into "粤文 1 to append", nor "粤文 2 end" into
        "粤文 2 to prepend".
        Your output "粤文 1 to append" and "粤文 2 to prepend" concatenated must
        equal "粤文 to distribute".
        """
