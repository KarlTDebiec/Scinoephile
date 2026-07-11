#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for pairwise-review test cases."""

from __future__ import annotations

from typing import ClassVar, Self

from pydantic import Field, model_validator

from scinoephile.core.llms import Answer, Query, TestCase

from .prompt import PairwiseReviewPrompt

__all__ = [
    "PairwiseReviewAnswer",
    "PairwiseReviewQuery",
    "PairwiseReviewTestCase",
]


_BASE_PROMPT = PairwiseReviewPrompt()


class PairwiseReviewQuery(Query):
    """Target subtitle and its corresponding reference subtitle."""

    prompt: ClassVar[PairwiseReviewPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    target: str = Field(max_length=1000)
    """Subtitle text to review."""
    reference: str = Field(max_length=1000)
    """Corresponding reference subtitle text."""


class PairwiseReviewAnswer(Answer):
    """Optional revision of a target subtitle and explanatory note."""

    prompt: ClassVar[PairwiseReviewPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    output: str = Field("", max_length=1000)
    """Revised target subtitle, removal marker, or empty string if unchanged."""
    note: str = Field("", max_length=1000)
    """Explanation of the revision, or an empty string."""


class PairwiseReviewTestCase(TestCase):
    """Pairwise-review query, optional answer, and optimization metadata."""

    query_cls: ClassVar[type[PairwiseReviewQuery]] = PairwiseReviewQuery
    """Query model class."""
    answer_cls: ClassVar[type[PairwiseReviewAnswer]] = PairwiseReviewAnswer
    """Answer model class."""
    prompt: ClassVar[PairwiseReviewPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    query: PairwiseReviewQuery
    """Target subtitle and corresponding reference subtitle."""
    answer: PairwiseReviewAnswer | None = None
    """Target revision and note, if available."""

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty based on whether the target is revised.

        Returns:
            minimum difficulty
        """
        min_difficulty = super().get_min_difficulty()
        if (
            self.answer is not None
            and self.answer.output
            and self.answer.output != self.query.target
        ):
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    @model_validator(mode="after")
    def validate_output_note_correspondence(self) -> Self:
        """Normalize unchanged output and require revisions and notes together.

        Unchanged full-text outputs from legacy pairwise-review data are normalized to
        the empty-string convention used by the other review operations.

        Returns:
            validated test case
        """
        if self.answer is None:
            return self

        if self.answer.output == self.query.target:
            self.answer.output = ""
            self.answer.note = ""
        elif self.answer.output and not self.answer.note:
            raise ValueError(self.prompt.note_missing_err)
        elif not self.answer.output and self.answer.note:
            raise ValueError(self.prompt.output_missing_err)
        return self
