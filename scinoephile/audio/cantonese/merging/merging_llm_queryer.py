#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Merges transcribed 粤文 text based on corresponding 中文."""

from __future__ import annotations

from typing import override

from scinoephile.audio.cantonese.merging.merging_answer import MergingAnswer
from scinoephile.audio.cantonese.merging.merging_query import MergingQuery
from scinoephile.audio.cantonese.merging.merging_test_case import MergingTestCase
from scinoephile.core.abcs import FixedLLMQueryer


class MergingLLMQueryer(FixedLLMQueryer[MergingQuery, MergingAnswer, MergingTestCase]):
    """Merges transcribed 粤文 text based on corresponding 中文."""

    @property
    @override
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        You are responsible for matching 粤文 subtitles of Cantonese speech to 中文
        subtitles of the same Cantonese speech.
        You will be given a 中文 subtitle and its nascent 粤文 subtitle.
        The nascent 粤文 subtitle will be split across multiple lines, representing
        pauses in the spoken Cantonese.
        Reply with a single line of 粤文 text combining all lines into one and
        incorporating the punctuation and spacing of the 中文 subtitle.
        Include all 粤文 characters and merge them into one line.
        Do not copy any 汉字 characters from the 中文 input.
        Only adjust punctuation and spacing of the 粤文 to match the 中文 input.
        Do not make any corrections to the 粤文 text, other than adjusting punctuation
        and spacing.
        """
