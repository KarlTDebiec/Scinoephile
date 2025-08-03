#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Merges transcribed 粤文 text based on corresponding 中文."""

from __future__ import annotations

from functools import cached_property
from typing import override

from scinoephile.audio.cantonese.merging.merge_answer import MergeAnswer
from scinoephile.audio.cantonese.merging.merge_query import MergeQuery
from scinoephile.audio.cantonese.merging.merge_test_case import MergeTestCase
from scinoephile.core.abcs import FixedLLMQueryer


class Merger(FixedLLMQueryer[MergeQuery, MergeAnswer, MergeTestCase]):
    """Merges transcribed 粤文 text based on corresponding 中文."""

    @cached_property
    @override
    def answer_example(self) -> MergeAnswer:
        """Example answer."""
        return MergeAnswer(yuewen_merged="粤文 merged")

    @cached_property
    @override
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        You are a helpful assistant that merges multi-line 粤文 subtitles of
        spoken Cantonese to match the spacing and punctuation of a single-line
        中文 subtitle.
        Include all 粤文 characters and merge them into one line.
        Do not copy any 汉字 characters from the 中文 input to the 粤文 output.
        Only adjust punctuation and spacing of the 粤文 to match the 中文 input.
        Do not make any corrections to the 粤文 text, other than adjusting punctuation
        and spacing.
        """
