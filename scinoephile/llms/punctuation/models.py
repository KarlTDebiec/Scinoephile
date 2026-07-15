#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for punctuation test cases."""

from __future__ import annotations

from typing import ClassVar, Self

from pydantic import model_validator

from scinoephile.core.llms import Answer, Query, TestCase
from scinoephile.core.text import (
    remove_non_punc_and_whitespace,
    remove_punc_and_whitespace,
)

from .prompt import PunctuationPrompt

__all__ = [
    "PunctuationAnswer",
    "PunctuationQuery",
    "PunctuationTestCase",
]


_BASE_PROMPT = PunctuationPrompt()


class PunctuationQuery(Query):
    """Subtitle lines to punctuate and their guide subtitle."""

    prompt: ClassVar[PunctuationPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    guide: str
    """Guide subtitle whose punctuation informs the output."""
    subtitles: list[str]
    """Subtitle lines to combine and punctuate, in order."""

    @model_validator(mode="after")
    def validate_required_fields(self) -> Self:
        """Ensure subtitle lines and their guide are nonempty."""
        if not self.guide:
            raise ValueError(self.prompt.ref_sub_missing_err)
        if not self.subtitles:
            raise ValueError(self.prompt.target_subs_missing_err)
        return self


class PunctuationAnswer(Answer):
    """Combined and punctuated subtitle text."""

    prompt: ClassVar[PunctuationPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    output: str
    """Combined and punctuated subtitle text."""

    @model_validator(mode="after")
    def validate_output(self) -> Self:
        """Ensure output text is nonempty."""
        if not self.output:
            raise ValueError(self.prompt.target_sub_punctuated_missing_err)
        return self


class PunctuationTestCase(TestCase):
    """Punctuation query, optional answer, and optimization metadata."""

    query_cls: ClassVar[type[PunctuationQuery]] = PunctuationQuery
    """Query model class."""
    answer_cls: ClassVar[type[PunctuationAnswer]] = PunctuationAnswer
    """Answer model class."""
    prompt: ClassVar[PunctuationPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    query: PunctuationQuery
    """Subtitle lines and their punctuation guide."""
    answer: PunctuationAnswer | None = None
    """Combined and punctuated subtitle text, if available."""

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty from output and guide punctuation.

        Returns:
            minimum difficulty
        """
        min_difficulty = super().get_min_difficulty()
        if self.answer is None:
            return min_difficulty

        if remove_non_punc_and_whitespace(self.answer.output):
            min_difficulty = max(min_difficulty, 1)
        if remove_non_punc_and_whitespace(
            self.query.guide
        ) != remove_non_punc_and_whitespace(self.answer.output):
            min_difficulty = max(min_difficulty, 2)
        return min_difficulty

    @model_validator(mode="after")
    def validate_output_characters(self) -> Self:
        """Ensure punctuation does not change subtitle characters.

        Returns:
            validated test case
        """
        if self.answer is None:
            return self

        expected = "".join(
            remove_punc_and_whitespace(subtitle) for subtitle in self.query.subtitles
        )
        received = remove_punc_and_whitespace(self.answer.output)
        if expected != received:
            raise ValueError(self.prompt.target_chars_changed_err(expected, received))
        return self
