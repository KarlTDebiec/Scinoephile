#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for 粤文 transcription translation."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.english.abcs import EnglishLLMText
from scinoephile.core.text import get_dedented_and_compacted_multiline_text


class TranslationLLMText(EnglishLLMText):
    """Text for LLM correspondence for 粤文 transcription translation."""

    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        Translate the missing 粤文 subtitles based on the corresponding 中文
        subtitles.""")
    """Base system prompt."""

    answer_example_yuewen_description: ClassVar[str] = (
        "粤文 subtitle {idx} translated from query's 中文 subtitle {idx}"
    )
