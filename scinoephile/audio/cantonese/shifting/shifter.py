#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shifts 粤文 text between adjacent subtitles based on corresponding 中文."""

from __future__ import annotations

from typing import override

from scinoephile.audio.cantonese.shifting.shift_answer import ShiftAnswer
from scinoephile.audio.cantonese.shifting.shift_query import ShiftQuery
from scinoephile.audio.cantonese.shifting.shift_test_case import ShiftTestCase
from scinoephile.core.abcs import FixedLLMQueryer


class Shifter(FixedLLMQueryer[ShiftQuery, ShiftAnswer, ShiftTestCase]):
    """Shifts 粤文 text between adjacent subtitles based on corresponding 中文."""

    @property
    @override
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        You are responsible for matching 粤文 subtitles of Cantonese speech to 中文
        subtitles of the same Cantonese speech.
        You will be given a 中文 subtitle and its nascent 粤文 subtitle, and a second
        中文 subtitle with its nascent 粤文 subtitle.
        Read the two consecutive 中文 subtitles and two consecutive 粤文 subtitles, and
        adjust the breakpoint between the first and second 粤文 subtitles so that they
        align with the two corresponding 中文 subtitles.
        This is, either shift characters from the end of the 粤文 subtitle 1 to the
        beginning of 粤文 subtitle 2, or shift characters from the beginning of
        the 粤文 subtitle 2 to the end of 粤文 subtitle 1.
        If no changes are needed, return the original 粤文 subtitles.
        Include all 粤文 characters from the inputs in the same order in the outputs.
        Do not copy punctuation or whitespace from the 中文 subtitles.
        Your output "粤文 1 shifted" and "粤文 2 shifted" concatenated must
        equal "粤文 1" and "粤文 2".
        """
