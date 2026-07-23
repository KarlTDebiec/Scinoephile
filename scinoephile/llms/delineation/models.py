#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for delineation test cases."""

from __future__ import annotations

from typing import ClassVar, Self

from pydantic import model_validator

from scinoephile.core.llms import Answer, Query, TestCase

from .prompt import DelineationPrompt

__all__ = [
    "DelineationAnswer",
    "DelineationQuery",
    "DelineationTestCase",
]


_BASE_PROMPT = DelineationPrompt()


class DelineationQuery(Query):
    """Adjacent reference and target subtitle pairs to delineate."""

    prompt: ClassVar[DelineationPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    reference_one: str
    """First reference subtitle text."""
    reference_two: str
    """Second reference subtitle text."""
    target_one: str = ""
    """Initial target text aligned with the first reference subtitle."""
    target_two: str = ""
    """Initial target text aligned with the second reference subtitle."""

    @model_validator(mode="after")
    def validate_target_presence(self) -> Self:
        """Ensure at least one initial target subtitle is nonempty."""
        if not self.target_one and not self.target_two:
            raise ValueError(self.prompt.target_subs_missing_err)
        return self


class DelineationAnswer(Answer):
    """Target subtitle text after boundary delineation."""

    prompt: ClassVar[DelineationPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    output_one: str = ""
    """Adjusted target text aligned with the first reference subtitle."""
    output_two: str = ""
    """Adjusted target text aligned with the second reference subtitle."""


class DelineationTestCase(TestCase):
    """Delineation query, optional answer, and optimization metadata."""

    query_cls: ClassVar[type[DelineationQuery]] = DelineationQuery
    """Query model class."""
    answer_cls: ClassVar[type[DelineationAnswer]] = DelineationAnswer
    """Answer model class."""
    prompt: ClassVar[DelineationPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    query: DelineationQuery
    """Adjacent reference and target subtitle pairs to delineate."""
    answer: DelineationAnswer | None = None
    """Adjusted target subtitle boundary, if available."""

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty based on whether a boundary shift is present.

        Returns:
            minimum difficulty
        """
        min_difficulty = super().get_min_difficulty()
        if self.answer is None:
            return min_difficulty
        if self.answer.output_one or self.answer.output_two:
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    @model_validator(mode="after")
    def validate_output_boundary(self) -> Self:
        """Ensure adjusted outputs represent a valid target boundary change."""
        if self.answer is None:
            return self

        if (
            self.query.target_one == self.answer.output_one
            and self.query.target_two == self.answer.output_two
        ):
            raise ValueError(self.prompt.target_subs_unchanged_err)

        if self.answer.output_one or self.answer.output_two:
            expected = self.query.target_one + self.query.target_two
            received = self.answer.output_one + self.answer.output_two
            if expected != received:
                raise ValueError(
                    self.prompt.target_chars_changed_err(expected, received)
                )
        return self
