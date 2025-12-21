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
    reference_1_field: ClassVar[str] = "zhongwen_1"
    """Field name for 中文 subtitle 1."""

    reference_1_description: ClassVar[str] = "Known 中文 of subtitle 1"
    """Description of reference_1 field."""

    reference_2_field: ClassVar[str] = "zhongwen_2"
    """Field name for 中文 subtitle 2."""

    reference_2_description: ClassVar[str] = "Known 中文 of subtitle 2"
    """Description of reference_2 field."""

    target_1_field: ClassVar[str] = "yuewen_1"
    """Field name for 粤文 subtitle 1."""

    target_1_description: ClassVar[str] = "Transcribed 粤文 of subtitle 1"
    """Description of target_1 field."""

    target_2_field: ClassVar[str] = "yuewen_2"
    """Field name for 粤文 subtitle 2."""

    target_2_description: ClassVar[str] = "Transcribed 粤文 of subtitle 2"
    """Description of target_2 field."""

    # Query validation errors
    target_1_target_2_missing_error: ClassVar[str] = (
        "Query must have yuewen_1, yuewen_2, or both."
    )
    """Error when yuewen_1 and yuewen_2 fields are missing."""

    # Answer fields
    target_1_shifted_field: ClassVar[str] = "yuewen_1_shifted"
    """Field name for shifted 粤文 subtitle 1."""

    target_1_shifted_description: ClassVar[str] = "Shifted 粤文 of subtitle 1"
    """Description of target_1_shifted field."""

    target_2_shifted_field: ClassVar[str] = "yuewen_2_shifted"
    """Field name for shifted 粤文 subtitle 2."""

    target_2_shifted_description: ClassVar[str] = "Shifted 粤文 of subtitle 2"
    """Description of target_2_shifted field."""

    # Test case validation errors
    target_1_target_2_unchanged_error: ClassVar[str] = (
        "Answer's yuewen_1_shifted and yuewen_2_shifted are equal to query's yuewen_1 "
        "and yuewen_2; if no shift is needed, yuewen_1_shifted and yuewen_2_shifted "
        "must be empty strings."
    )
    """Error when yuewen_1 and yuewen_2 are unchanged and not both omitted."""

    target_characters_changed_error_template: ClassVar[str] = (
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
        return cls.target_characters_changed_error(expected, received)

    # Legacy compatibility fields
    zhongwen_1_field: ClassVar[str] = reference_1_field
    """Field name for 中文 subtitle 1."""

    zhongwen_1_description: ClassVar[str] = reference_1_description
    """Description of zhongwen_1 field."""

    zhongwen_2_field: ClassVar[str] = reference_2_field
    """Field name for 中文 subtitle 2."""

    zhongwen_2_description: ClassVar[str] = reference_2_description
    """Description of zhongwen_2 field."""

    yuewen_1_field: ClassVar[str] = target_1_field
    """Field name for 粤文 subtitle 1."""

    yuewen_1_description: ClassVar[str] = target_1_description
    """Description of yuewen_1 field."""

    yuewen_2_field: ClassVar[str] = target_2_field
    """Field name for 粤文 subtitle 2."""

    yuewen_2_description: ClassVar[str] = target_2_description
    """Description of yuewen_2 field."""

    yuewen_1_yuewen_2_missing_error: ClassVar[str] = target_1_target_2_missing_error
    """Error when yuewen_1 and yuewen_2 fields are missing."""

    yuewen_1_shifted_field: ClassVar[str] = target_1_shifted_field
    """Field name for shifted 粤文 subtitle 1."""

    yuewen_1_shifted_description: ClassVar[str] = target_1_shifted_description
    """Description of yuewen_1_shifted field."""

    yuewen_2_shifted_field: ClassVar[str] = target_2_shifted_field
    """Field name for shifted 粤文 subtitle 2."""

    yuewen_2_shifted_description: ClassVar[str] = target_2_shifted_description
    """Description of yuewen_2_shifted field."""

    yuewen_1_yuewen_2_unchanged_error: ClassVar[str] = target_1_target_2_unchanged_error
    """Error when yuewen_1 and yuewen_2 are unchanged and not both omitted."""

    yuewen_characters_changed_error_template: ClassVar[str] = (
        target_characters_changed_error_template
    )
    """Error template when shifted 粤文 characters do not match original."""
