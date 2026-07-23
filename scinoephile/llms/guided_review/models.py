#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for guided-review test cases."""

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

from .prompt import GuidedReviewPrompt

__all__ = [
    "GuidedReviewAnswer",
    "GuidedReviewQuery",
    "GuidedReviewTestCase",
]


_BASE_PROMPT = GuidedReviewPrompt()


class GuidedReviewQuery(Query):
    """Target and guide subtitles for guided review."""

    prompt: ClassVar[GuidedReviewPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    targets: list[TestCaseSubtitle] = Field(min_length=1)
    """Target subtitles to review, in order."""
    guides: list[TestCaseSubtitle]
    """Guide subtitles for the same passage, in order."""

    @model_validator(mode="after")
    def validate_guide_indices(self) -> Self:
        """Ensure guide indexes are consecutive, ordered, and begin at 1."""
        indexes = [guide.index for guide in self.guides]
        if indexes != list(range(1, len(indexes) + 1)):
            raise ValueError(self.prompt.guide_indices_err)
        return self

    @model_validator(mode="after")
    def validate_target_indices(self) -> Self:
        """Ensure target indexes are consecutive, ordered, and begin at 1."""
        indexes = [target.index for target in self.targets]
        if indexes != list(range(1, len(indexes) + 1)):
            raise ValueError(self.prompt.target_indices_err)
        return self


class GuidedReviewAnswer(Answer):
    """Sparse revisions for guided-review targets that require changes."""

    prompt: ClassVar[GuidedReviewPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    revisions: list[AnnotatedTestCaseSubtitle]
    """Revisions in ascending target-index order."""

    @model_validator(mode="after")
    def validate_revision_indices(self) -> Self:
        """Ensure revision indexes are unique and in ascending order."""
        indexes = [revision.index for revision in self.revisions]
        if indexes != sorted(set(indexes)):
            raise ValueError(self.prompt.revision_indices_err)
        return self


class GuidedReviewTestCase(TestCase):
    """Guided-review query, optional answer, and optimization metadata."""

    query_cls: ClassVar[type[GuidedReviewQuery]] = GuidedReviewQuery
    """Query model class."""
    answer_cls: ClassVar[type[GuidedReviewAnswer]] = GuidedReviewAnswer
    """Answer model class."""
    prompt: ClassVar[GuidedReviewPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    query: GuidedReviewQuery
    """Target and guide subtitles."""
    answer: GuidedReviewAnswer | None = None
    """Sparse target revisions, if available."""

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty based on whether any target is revised.

        Returns:
            minimum difficulty
        """
        min_difficulty = super().get_min_difficulty()
        if self.answer is not None and self.answer.revisions:
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    @model_validator(mode="after")
    def validate_revision_correspondence(self) -> Self:
        """Ensure every answer revision changes a query target.

        Returns:
            validated test case
        """
        if self.answer is None:
            return self

        target_text_by_index = {
            target.index: target.text for target in self.query.targets
        }
        for revision in self.answer.revisions:
            target_text = target_text_by_index.get(revision.index)
            if target_text is None:
                raise ValueError(self.prompt.revision_index_missing_err(revision.index))
            if revision.text == target_text:
                raise ValueError(self.prompt.revision_unmodified_err(revision.index))
        return self
