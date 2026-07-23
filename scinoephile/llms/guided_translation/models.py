#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for guided-translation test cases."""

from __future__ import annotations

from typing import ClassVar, Self

from pydantic import Field, model_validator

from scinoephile.core.llms import Answer, Query, TestCase, TestCaseSubtitle

from .prompt import GuidedTranslationPrompt

__all__ = [
    "GuidedTranslationAnswer",
    "GuidedTranslationQuery",
    "GuidedTranslationSubtitle",
    "GuidedTranslationTestCase",
]


_BASE_PROMPT = GuidedTranslationPrompt()


class GuidedTranslationSubtitle(TestCaseSubtitle):
    """Indexed subtitle text without a length restriction."""

    text: str
    """Subtitle text."""


class GuidedTranslationQuery(Query):
    """Subtitles to translate and guide subtitles from the same block."""

    prompt: ClassVar[GuidedTranslationPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    subtitles: list[GuidedTranslationSubtitle] = Field(min_length=1)
    """Source-language subtitles to translate, in order."""
    guides: list[GuidedTranslationSubtitle]
    """Target-language guide subtitles from the same block, in order."""

    @model_validator(mode="after")
    def validate_guide_indices(self) -> Self:
        """Ensure guide indexes are consecutive, ordered, and begin at 1."""
        indexes = [guide.index for guide in self.guides]
        if indexes != list(range(1, len(indexes) + 1)):
            raise ValueError(self.prompt.guide_indices_err)
        return self

    @model_validator(mode="after")
    def validate_subtitle_indices(self) -> Self:
        """Ensure subtitle indexes are consecutive, ordered, and begin at 1."""
        indexes = [subtitle.index for subtitle in self.subtitles]
        if indexes != list(range(1, len(indexes) + 1)):
            raise ValueError(self.prompt.subtitle_indices_err)
        return self


class GuidedTranslationAnswer(Answer):
    """Translated outputs corresponding to query subtitles."""

    prompt: ClassVar[GuidedTranslationPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    outputs: list[GuidedTranslationSubtitle] = Field(min_length=1)
    """Translated subtitles, in query-subtitle order."""

    @model_validator(mode="after")
    def validate_output_indices(self) -> Self:
        """Ensure output indexes are consecutive, ordered, and begin at 1."""
        indexes = [output.index for output in self.outputs]
        if indexes != list(range(1, len(indexes) + 1)):
            raise ValueError(self.prompt.output_indices_err)
        return self


class GuidedTranslationTestCase(TestCase):
    """Guided-translation query, optional answer, and optimization metadata."""

    query_cls: ClassVar[type[GuidedTranslationQuery]] = GuidedTranslationQuery
    """Query model class."""
    answer_cls: ClassVar[type[GuidedTranslationAnswer]] = GuidedTranslationAnswer
    """Answer model class."""
    prompt: ClassVar[GuidedTranslationPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    query: GuidedTranslationQuery
    """Subtitles to translate and optional guide subtitles."""
    answer: GuidedTranslationAnswer | None = None
    """Translated outputs, if available."""

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
