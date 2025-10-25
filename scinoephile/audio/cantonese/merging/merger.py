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
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        You are responsible for matching 粤文 (yuewen) subtitles of Cantonese speech to
        中文 (zhongwen) subtitles of the same Cantonese speech.
        You will be given a 中文 subtitle (zhongwen) and its nascent 粤文 subtitle
        (yuewen_to_merge).
        yuewen_to_merge will be a list of multiple lines, representing pauses in the
        spoken Cantonese.
        Reply with a single line of 粤文 (yuewen_merged) combining all lines from
        yuewen_to_merge into one and incorporating the punctuation and spacing of
        zhongwen.
        Include all characters in yuewen_to_merge in yuewen_merged.
        Do not copy any 汉字 characters from zhongwen into yuewen_merged.
        Only adjust punctuation and spacing in yuewen_merged to match zhongwen.
        Do not make any corrections to yuewen_to_merge, other than adjusting punctuation
        and spacing.
        """
