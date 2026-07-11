#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for review test cases."""

from __future__ import annotations

from typing import Self, cast

from pydantic import BaseModel, ConfigDict, Field, model_validator

from scinoephile.core.llms import Answer, Query, TestCase

from .prompt import ReviewPrompt

__all__ = [
    "ReviewAnswer",
    "ReviewQuery",
    "ReviewRevision",
    "ReviewSubtitle",
    "ReviewTestCase",
]


class ReviewSubtitle(BaseModel):
    """Indexed subtitle text in a review query."""

    model_config = ConfigDict(validate_by_name=True)

    index: int = Field(ge=1)
    """One-based subtitle index."""
    text: str = Field(max_length=1000)
    """Subtitle text."""


class ReviewRevision(ReviewSubtitle):
    """Indexed subtitle revision and its explanatory note."""

    text: str = Field(min_length=1, max_length=1000)
    """Full revised subtitle text."""
    note: str = Field(min_length=1, max_length=1000)
    """Note explaining the revision."""


class ReviewQuery(Query):
    """Subtitles to review."""

    model_config = ConfigDict(validate_by_name=True)

    subtitles: list[ReviewSubtitle] = Field(min_length=1)
    """Subtitles to review, in order."""

    @model_validator(mode="after")
    def validate_subtitle_indices(self) -> Self:
        """Ensure subtitle indexes are consecutive, ordered, and begin at 1."""
        indexes = [subtitle.index for subtitle in self.subtitles]
        if indexes != list(range(1, len(indexes) + 1)):
            prompt = cast(ReviewPrompt, self.prompt)
            raise ValueError(prompt.subtitle_indices_err)
        return self


class ReviewAnswer(Answer):
    """Sparse revisions for subtitles that require changes."""

    model_config = ConfigDict(validate_by_name=True)

    revisions: list[ReviewRevision]
    """Revisions in ascending subtitle-index order."""

    @model_validator(mode="after")
    def validate_revision_indices(self) -> Self:
        """Ensure revision indexes are unique and in ascending order."""
        indexes = [revision.index for revision in self.revisions]
        if indexes != sorted(set(indexes)):
            prompt = cast(ReviewPrompt, self.prompt)
            raise ValueError(prompt.revision_indices_err)
        return self


class ReviewTestCase(TestCase):
    """Review query, optional answer, and optimization metadata."""

    query: ReviewQuery
    """Subtitles to review."""
    answer: ReviewAnswer | None = None
    """Sparse subtitle revisions, if available."""


_base_prompt = ReviewPrompt()
ReviewQuery.prompt = _base_prompt
ReviewAnswer.prompt = _base_prompt
ReviewTestCase.query_cls = ReviewQuery
ReviewTestCase.answer_cls = ReviewAnswer
ReviewTestCase.prompt = _base_prompt
