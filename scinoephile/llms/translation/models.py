#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for translation test cases."""

from __future__ import annotations

from typing import ClassVar, Self

from pydantic import Field, model_validator

from scinoephile.core.llms import Answer, Query, TestCase, TestCaseSubtitle

from .prompt import TranslationPrompt

__all__ = [
    "TranslationAnswer",
    "TranslationOutput",
    "TranslationQuery",
    "TranslationTestCase",
]


_BASE_PROMPT = TranslationPrompt()


class TranslationOutput(TestCaseSubtitle):
    """Indexed translated subtitle text."""

    text: str
    """Translated subtitle text."""


class TranslationQuery(Query):
    """Subtitles to translate."""

    prompt: ClassVar[TranslationPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    subtitles: list[TestCaseSubtitle] = Field(min_length=1)
    """Subtitles to translate, in order."""

    @model_validator(mode="after")
    def validate_subtitle_indices(self) -> Self:
        """Ensure subtitle indexes are consecutive, ordered, and begin at 1."""
        indexes = [subtitle.index for subtitle in self.subtitles]
        if indexes != list(range(1, len(indexes) + 1)):
            raise ValueError(self.prompt.subtitle_indices_err)
        return self


class TranslationAnswer(Answer):
    """Translated subtitles."""

    prompt: ClassVar[TranslationPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    outputs: list[TranslationOutput] = Field(min_length=1)
    """Translated subtitles, in order."""

    @model_validator(mode="after")
    def validate_output_indices(self) -> Self:
        """Ensure output indexes are consecutive, ordered, and begin at 1."""
        indexes = [output.index for output in self.outputs]
        if indexes != list(range(1, len(indexes) + 1)):
            raise ValueError(self.prompt.output_indices_err)
        return self


class TranslationTestCase(TestCase):
    """Translation query, optional answer, and optimization metadata."""

    query_cls: ClassVar[type[TranslationQuery]] = TranslationQuery
    """Query model class."""
    answer_cls: ClassVar[type[TranslationAnswer]] = TranslationAnswer
    """Answer model class."""
    prompt: ClassVar[TranslationPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    query: TranslationQuery
    """Subtitles to translate."""
    answer: TranslationAnswer | None = None
    """Translated subtitles, if available."""

    @model_validator(mode="after")
    def validate_output_correspondence(self) -> Self:
        """Ensure answer outputs correspond exactly to query subtitles."""
        if self.answer is None:
            return self
        subtitle_indexes = [subtitle.index for subtitle in self.query.subtitles]
        output_indexes = [output.index for output in self.answer.outputs]
        if output_indexes != subtitle_indexes:
            raise ValueError(self.prompt.output_correspondence_err)
        return self
