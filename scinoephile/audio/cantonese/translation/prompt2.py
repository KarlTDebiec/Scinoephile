#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for 粤文 transcription translation."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.english.abcs.prompt2 import EnglishPrompt2
from scinoephile.core.text import get_dedented_and_compacted_multiline_text

__all__ = ["TranslationPrompt2"]


class TranslationPrompt2(EnglishPrompt2):
    """Text for LLM correspondence for 粤文 transcription translation."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        Translate the missing 粤文 subtitles based on the corresponding 中文
        subtitles.""")
    """Base system prompt."""

    # Query descriptions
    zhongwen_description: ClassVar[str] = "Known 中文 of subtitle {idx}"
    """Description of 'zhongwen_{idx}' fields."""

    yuewen_query_description: ClassVar[str] = "Transcribed 粤文 of subtitle {idx}"
    """Description of 'yuewen_{idx}' query fields."""

    # Answer descriptions
    yuewen_answer_description: ClassVar[str] = "Translated 粤文 of subtitle {idx}"
    """Description of 'yuewen_{idx}' answer fields."""
