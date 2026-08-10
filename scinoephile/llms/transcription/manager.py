#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for prompt-specific transcription classes."""

from __future__ import annotations

from functools import cache
from typing import ClassVar

from scinoephile.core.llms import Answer, Manager, PromptModelField, Query, TestCase

from .models import (
    TranscriptionAnswer,
    TranscriptionQuery,
    TranscriptionSource,
    TranscriptionTestCase,
)
from .prompt import TranscriptionPrompt

__all__ = ["TranscriptionManager"]


class TranscriptionManager(Manager[TranscriptionTestCase]):
    """Factories for prompt-specific transcription classes."""

    operation: ClassVar[str] = "transcription"
    """Stable operation identifier used in persistence."""
    base_prompt: ClassVar[TranscriptionPrompt] = TranscriptionTestCase.prompt
    """Base prompt defining persisted field names."""
    test_case_base_cls: ClassVar[type[TestCase]] = TranscriptionTestCase
    """Static test-case model defining the operation's semantic shape."""

    @classmethod
    @cache
    def get_answer_cls(cls, prompt: TranscriptionPrompt) -> type[Answer]:
        """Get answer class with prompt-specific aliases.

        Arguments:
            prompt: text and field aliases for transcription
        Returns:
            answer model class
        """
        return cls.create_prompt_model(
            TranscriptionAnswer,
            prompt,
            {
                "text": PromptModelField(
                    alias=prompt.answer_text, description=prompt.answer_text_desc
                )
            },
        )

    @classmethod
    @cache
    def get_query_cls(cls, prompt: TranscriptionPrompt) -> type[Query]:
        """Get query class with prompt-specific aliases.

        Arguments:
            prompt: text and field aliases for transcription
        Returns:
            query model class
        """
        source_cls = cls.get_source_cls(prompt)
        return cls.create_prompt_model(
            TranscriptionQuery,
            prompt,
            {
                "sources": PromptModelField(
                    alias=prompt.sources,
                    annotation=list[source_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.sources_desc,
                ),
                "speaker": PromptModelField(
                    alias=prompt.speaker, description=prompt.speaker_desc
                ),
                "language_trace": PromptModelField(
                    alias=prompt.language_trace, description=prompt.language_trace_desc
                ),
                "singing_trace": PromptModelField(
                    alias=prompt.singing_trace, description=prompt.singing_trace_desc
                ),
                "music_trace": PromptModelField(
                    alias=prompt.music_trace, description=prompt.music_trace_desc
                ),
            },
        )

    @classmethod
    @cache
    def get_source_cls(cls, prompt: TranscriptionPrompt) -> type[TranscriptionSource]:
        """Get ASR source row class with prompt-specific aliases.

        Arguments:
            prompt: text and field aliases for transcription
        Returns:
            ASR source row model class
        """
        return cls.create_prompt_model(
            TranscriptionSource,
            prompt,
            {
                "name": PromptModelField(
                    alias=prompt.source_name, description=prompt.source_name_desc
                ),
                "text": PromptModelField(
                    alias=prompt.source_text, description=prompt.source_text_desc
                ),
            },
        )
