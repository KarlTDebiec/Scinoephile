#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for prompt-specific aligned transcription merge classes."""

from __future__ import annotations

from functools import cache
from typing import ClassVar

from scinoephile.core.llms import Answer, Manager, PromptModelField, Query, TestCase

from .models import (
    AlignedTranscriptionMergeAnswer,
    AlignedTranscriptionMergeQuery,
    AlignedTranscriptionMergeSource,
    AlignedTranscriptionMergeTestCase,
)
from .prompt import AlignedTranscriptionMergePrompt

__all__ = ["AlignedTranscriptionMergeManager"]


class AlignedTranscriptionMergeManager(Manager[AlignedTranscriptionMergeTestCase]):
    """Factories for prompt-specific aligned transcription merge classes."""

    operation: ClassVar[str] = "aligned-transcription-merge"
    """Stable operation identifier used in persistence."""
    base_prompt: ClassVar[AlignedTranscriptionMergePrompt] = (
        AlignedTranscriptionMergeTestCase.prompt
    )
    """Base prompt defining persisted field names."""
    test_case_base_cls: ClassVar[type[TestCase]] = AlignedTranscriptionMergeTestCase
    """Static test-case model defining the operation's semantic shape."""

    @classmethod
    @cache
    def get_answer_cls(cls, prompt: AlignedTranscriptionMergePrompt) -> type[Answer]:
        """Get answer class with prompt-specific aliases.

        Arguments:
            prompt: text and field aliases for aligned transcription merging
        Returns:
            answer model class
        """
        return cls.create_prompt_model(
            AlignedTranscriptionMergeAnswer,
            prompt,
            {
                "text": PromptModelField(
                    alias=prompt.answer_text, description=prompt.answer_text_desc
                )
            },
        )

    @classmethod
    @cache
    def get_query_cls(cls, prompt: AlignedTranscriptionMergePrompt) -> type[Query]:
        """Get query class with prompt-specific aliases.

        Arguments:
            prompt: text and field aliases for aligned transcription merging
        Returns:
            query model class
        """
        source_cls = cls.get_source_cls(prompt)
        return cls.create_prompt_model(
            AlignedTranscriptionMergeQuery,
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
    def get_source_cls(
        cls, prompt: AlignedTranscriptionMergePrompt
    ) -> type[AlignedTranscriptionMergeSource]:
        """Get ASR source row class with prompt-specific aliases.

        Arguments:
            prompt: text and field aliases for aligned transcription merging
        Returns:
            ASR source row model class
        """
        return cls.create_prompt_model(
            AlignedTranscriptionMergeSource,
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
