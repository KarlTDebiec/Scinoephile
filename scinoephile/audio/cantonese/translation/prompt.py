#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for 粤文 transcription translation."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.english import EnglishPrompt
from scinoephile.core.text import get_dedented_and_compacted_multiline_text

__all__ = ["TranslationPrompt"]


class TranslationPrompt(EnglishPrompt):
    """Text for LLM correspondence for 粤文 transcription translation."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        Translate the missing 粤文 subtitles based on the corresponding 中文
        subtitles.""")
    """Base system prompt."""

    # Query fields
    zhongwen_prefix: ClassVar[str] = "zhongwen_"
    """Prefix of zhongwen field in query."""

    @classmethod
    def zhongwen_field(cls, idx: int) -> str:
        """Name of zhongwen field in query.

        Arguments:
            idx: index of subtitle
        Returns:
            name of zhongwen field
        """
        return f"{cls.zhongwen_prefix}{idx}"

    zhongwen_description_template: ClassVar[str] = "Known 中文 of subtitle {idx}"
    """Description template for zhongwen field in query."""

    @classmethod
    def zhongwen_description(cls, idx: int) -> str:
        """Description of zhongwen field in query.

        Arguments:
            idx: index of subtitle
        Returns:
            description of zhongwen field
        """
        return cls.zhongwen_description_template.format(idx=idx)

    yuewen_prefix: ClassVar[str] = "yuewen_"
    """Prefix of yuewen field."""

    @classmethod
    def yuewen_field(cls, idx: int) -> str:
        """Name of yuewen field.

        Arguments:
            idx: index of subtitle
        Returns:
            name of yuewen field
        """
        return f"{cls.yuewen_prefix}{idx}"

    yuewen_query_description_template: ClassVar[str] = (
        "Transcribed 粤文 of subtitle {idx}"
    )
    """Description template for yuewen field in query."""

    @classmethod
    def yuewen_query_description(cls, idx: int) -> str:
        """Description of yuewen field in query.

        Arguments:
            idx: index of subtitle
        Returns:
            description of yuewen field
        """
        return cls.yuewen_query_description_template.format(idx=idx)

    # Answer fields
    yuewen_answer_description_template: ClassVar[str] = (
        "Translated 粤文 of subtitle {idx}"
    )
    """Description template for yuewen field in answer."""

    @classmethod
    def yuewen_answer_description(cls, idx: int) -> str:
        """Description of yuewen field in answer.

        Arguments:
            idx: index of subtitle
        Returns:
            description of yuewen field
        """
        return cls.yuewen_answer_description_template.format(idx=idx)
