#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for 粤文 transcription shifting."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.lang.eng.prompts import EngPrompt
from scinoephile.llms.dual_pair import DualPairPrompt

__all__ = ["ShiftingPrompt"]


class ShiftingPrompt(DualPairPrompt, EngPrompt):
    """Text for LLM correspondence for 粤文 transcription shifting."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
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
        yuewen_2_shifted.""")
    """Base system prompt."""

    # Query fields
    src_1_sub_1: ClassVar[str] = "zhongwen_1"
    """Name of source one subtitle one field in query."""

    src_1_sub_1_desc: ClassVar[str] = "Known 中文 of subtitle 1"
    """Description of source one subtitle one field in query."""

    src_1_sub_2: ClassVar[str] = "zhongwen_2"
    """Name of source one subtitle two field in query."""

    src_1_sub_2_desc: ClassVar[str] = "Known 中文 of subtitle 2"
    """Description of source one subtitle two field in query."""

    src_2_sub_1: ClassVar[str] = "yuewen_1"
    """Name of source two subtitle one field in query."""

    src_2_sub_1_desc: ClassVar[str] = "Transcribed 粤文 of subtitle 1"
    """Description of source two subtitle one field in query."""

    src_2_sub_2: ClassVar[str] = "yuewen_2"
    """Name of source two subtitle two field in query."""

    src_2_sub_2_desc: ClassVar[str] = "Transcribed 粤文 of subtitle 2"
    """Description of source two subtitle two field in query."""

    # Query validation errors
    src_2_sub_1_sub_2_missing_err: ClassVar[str] = (
        "Query must have yuewen_1, yuewen_2, or both."
    )
    """Error when src_2_sub_1 and src_2_sub_2 fields are missing."""

    # Answer fields
    src_2_sub_1_shifted: ClassVar[str] = "yuewen_1_shifted"
    """Name of shifted source two subtitle one field in answer."""

    src_2_sub_1_shifted_desc: ClassVar[str] = "Shifted 粤文 of subtitle 1"
    """Description of shifted source two subtitle one field in answer."""

    src_2_sub_2_shifted: ClassVar[str] = "yuewen_2_shifted"
    """Name of shifted source two subtitle two field in answer."""

    src_2_sub_2_shifted_desc: ClassVar[str] = "Shifted 粤文 of subtitle 2"
    """Description of shifted source two subtitle two field in answer."""

    # Test case validation errors
    src_2_sub_1_sub_2_unchanged_err: ClassVar[str] = (
        "Answer's yuewen_1_shifted and yuewen_2_shifted are equal to query's yuewen_1 "
        "and yuewen_2; if no shift is needed, yuewen_1_shifted and yuewen_2_shifted "
        "must be empty strings."
    )
    """Error when src_2_sub_1 and src_2_sub_2 are unchanged."""

    src_2_chars_changed_err_tpl: ClassVar[str] = (
        "Answer's concatenated yuewen_1_shifted and yuewen_2_shifted does not match "
        "query's concatenated yuewen_1 and yuewen_2:\n"
        "Expected: {expected}\n"
        "Received: {received}"
    )
    """Error template when shifted 粤文 characters do not match original."""

    @classmethod
    def yuewen_characters_changed_error(cls, expected: str, received: str) -> str:
        """Error when shifted 粤文 characters do not match original.

        Arguments:
            expected: the expected concatenated 粤文 characters
            received: the received concatenated 粤文 characters
        Returns:
            formatted error message
        """
        return cls.src_2_chars_changed_err(expected, received)
