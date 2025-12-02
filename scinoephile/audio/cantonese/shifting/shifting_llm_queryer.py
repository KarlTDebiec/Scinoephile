#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shifts 粤文 text between adjacent subtitles based on corresponding 中文."""

from __future__ import annotations

from typing import override

from scinoephile.audio.cantonese.shifting.shifting_answer import ShiftingAnswer
from scinoephile.audio.cantonese.shifting.shifting_query import ShiftingQuery
from scinoephile.audio.cantonese.shifting.shifting_test_case import ShiftingTestCase
from scinoephile.core.abcs import FixedLLMQueryer


class ShiftingLLMQueryer(
    FixedLLMQueryer[ShiftingQuery, ShiftingAnswer, ShiftingTestCase]
):
    """Shifts 粤文 text between adjacent subtitles based on corresponding 中文."""

    @property
    @override
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        You are responsible for matching 粤文 (yuewen) subtitles of Cantonese speech to 
        中文 (zhongwen) subtitles of the same Cantonese speech.
        You will be given a 中文 subtitle (zhongwen_1) and its nascent 粤文 subtitle
        (yuewen_1), and a second 中文 subtitle (zhongwen_2) with its nascent 粤文
        subtitle (yuewen_2).
        Read zhongwen_1 and zhongwen_2, and yuewen_1 and yuewen_2, and adjust the
        breakpoint between yuewen_1 and yuewen_2 so that their contents align with
        zhongwen_1 and zhongwen_2.
        This is, either shift characters from the end of yuewen_1 to the beginning of
        yuewen_2, or shift characters from the beginning of yuewen_2 to the end of
        yuewen_1.
        Reply with your updated 粤文 (yuewen) subtitles in yuewen_1_shifted and
        yuewen_2_shifted.
        If no changes are needed, return empty strings for both yuewen_1_shifted and
        yuewen_2_shifted.
        """
