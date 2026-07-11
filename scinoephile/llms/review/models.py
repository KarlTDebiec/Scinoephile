#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for review test cases."""

from __future__ import annotations

from typing import ClassVar, Self

from pydantic import Field, model_validator

from scinoephile.core.llms import (
    AnnotatedTestCaseSubtitle,
    Answer,
    Query,
    TestCase,
    TestCaseSubtitle,
)

from .prompt import ReviewPrompt

__all__ = [
    "ReviewAnswer",
    "ReviewQuery",
    "ReviewTestCase",
]


_BASE_PROMPT = ReviewPrompt()


class ReviewQuery(Query):
    """Subtitles to review."""

    prompt: ClassVar[ReviewPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    subtitles: list[TestCaseSubtitle] = Field(min_length=1)
    """Subtitles to review, in order."""

    @model_validator(mode="after")
    def validate_subtitle_indices(self) -> Self:
        """Ensure subtitle indexes are consecutive, ordered, and begin at 1."""
        indexes = [subtitle.index for subtitle in self.subtitles]
        if indexes != list(range(1, len(indexes) + 1)):
            raise ValueError(self.prompt.subtitle_indices_err)
        return self


class ReviewAnswer(Answer):
    """Sparse revisions for subtitles that require changes."""

    prompt: ClassVar[ReviewPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    revisions: list[AnnotatedTestCaseSubtitle]
    """Revisions in ascending subtitle-index order."""

    @model_validator(mode="after")
    def validate_revision_indices(self) -> Self:
        """Ensure revision indexes are unique and in ascending order."""
        indexes = [revision.index for revision in self.revisions]
        if indexes != sorted(set(indexes)):
            raise ValueError(self.prompt.revision_indices_err)
        return self


class ReviewTestCase(TestCase):
    """Review query, optional answer, and optimization metadata."""

    query_cls: ClassVar[type[ReviewQuery]] = ReviewQuery
    """Query model class."""
    answer_cls: ClassVar[type[ReviewAnswer]] = ReviewAnswer
    """Answer model class."""
    prompt: ClassVar[ReviewPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    query: ReviewQuery
    """Subtitles to review."""
    answer: ReviewAnswer | None = None
    """Sparse subtitle revisions, if available."""
