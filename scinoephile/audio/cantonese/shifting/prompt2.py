#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for 粤文 transcription shifting."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.english.abcs.prompt2 import EnglishPrompt2
from scinoephile.core.text import get_dedented_and_compacted_multiline_text

__all__ = ["ShiftingPrompt2"]


class ShiftingPrompt2(EnglishPrompt2):
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

    # Query descriptions
    zhongwen_1_description: ClassVar[str] = "Known 中文 of subtitle 1"
    """Description of 'zhongwen_1' field."""

    zhongwen_2_description: ClassVar[str] = "Known 中文 of subtitle 2"
    """Description of 'zhongwen_2' field."""

    yuewen_1_description: ClassVar[str] = "Transcribed 粤文 of subtitle "
    """Description of 'yuewen_1' field."""

    yuewen_2_description: ClassVar[str] = "Transcribed 粤文 of subtitle 2"
    """Description of 'yuewen_2' field."""

    # Query validation errors
    yuewen_1_yuewen_2_missing_error: ClassVar[str] = (
        "Query must have yuewen_1, yuewen_2, or both."
    )
    """Error message when 'yuewen_1' and 'yuewen_2' fields are missing."""

    # Answer descriptions
    yuewen_1_shifted_description: ClassVar[str] = "Shifted 粤文 of subtitle 1"
    """Description of 'yuewen_1_shifted' field."""

    yuewen_2_shifted_description: ClassVar[str] = "Shifted 粤文 of subtitle 1"
    """Description of 'yuewen_2_shifted' field."""

    # Test case validation errors
    yuewen_1_yuewen_2_unchanged_error: ClassVar[str] = (
        "Answer's yuewen_1_shifted and yuewen_2_shifted are equal to query's yuewen_1 "
        "and yuewen_2; if no shift is needed, yuewen_1_shifted and yuewen_2_shifted "
        "must be empty strings."
    )
    """Error message when yuewen_1 and yuewen_2 are unchanged and not both omitted."""

    yuewen_characters_changed_error: ClassVar[str] = (
        "Answer's concatenated yuewen_1_shifted and yuewen_2_shifted does not match "
        "query's concatenated yuewen_1 and yuewen_2:\n"
        "Expected: {expected}\n"
        "Received: {received}"
    )
    """Error message when shifted 粤文 characters do not match original."""
