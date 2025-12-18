#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for 粤文 transcription merging."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.lang.eng.prompts import EngPrompt

__all__ = ["MergingPrompt"]


class MergingPrompt(EngPrompt):
    """Text for LLM correspondence for 粤文 transcription merging."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
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
        and spacing.""")
    """Base system prompt."""

    # Query fields
    zhongwen_field: ClassVar[str] = "zhongwen"
    """Field name for 中文 of subtitle."""

    zhongwen_description: ClassVar[str] = "Known 中文 of subtitle"
    """Description of zhongwen field."""

    yuewen_to_merge_field: ClassVar[str] = "yuewen_to_merge"
    """Field name for transcribed 粤文 of subtitle."""

    yuewen_to_merge_description: ClassVar[str] = "Transcribed 粤文 of subtitle"
    """Description of yuewen_to_merge field."""

    # Query validation errors
    zhongwen_missing_error: ClassVar[str] = "Query must have 中文 of subtitle."
    """Error when zhongwen field is missing."""

    yuewen_to_merge_missing_error: ClassVar[str] = (
        "Query must have transcribed 粤文 of subtitle."
    )
    """Error when yuewen_to_merge field is missing."""

    # Answer fields
    yuewen_merged_field: ClassVar[str] = "yuewen_merged"
    """Field name for merged 粤文 of subtitle."""

    yuewen_merged_description: ClassVar[str] = "Merged 粤文 of subtitle"
    """Description of yuewen_merged field."""

    # Answer validation errors
    yuewen_merged_missing_error: ClassVar[str] = (
        "Answer must have merged 粤文 subtitle."
    )
    """Error when yuewen_merged field is missing."""

    # Test case validation errors
    yuewen_characters_changed_error_template: ClassVar[str] = (
        "Answer's 粤文 subtitle stripped of punctuation and whitespace does not match "
        "query's 粤文 subtitle concatenated:\n"
        "Expected: {expected}\n"
        "Received: {received}"
    )
    """Error template when merged 粤文 characters do not match original."""

    @classmethod
    def yuewen_characters_changed_error(cls, expected: str, received: str) -> str:
        """Error when merged 粤文 characters do not match original.

        Arguments:
            expected: expected 粤文 characters
            received: received 粤文 characters
        Returns:
            error message
        """
        return cls.yuewen_characters_changed_error_template.format(
            expected=expected, received=received
        )
