#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for punctuation test cases."""

from __future__ import annotations

from typing import ClassVar, Self

from pydantic import model_validator

from scinoephile.core.llms import Answer, Query, TestCase

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
    subtitles: list[str]
    """Subtitle lines to combine and punctuate, in order."""
    guide: str
    """Guide subtitle whose punctuation informs the output."""

    @model_validator(mode="after")
    def validate_required_fields(self) -> Self:
        """Ensure subtitle lines and their guide are nonempty."""
        if not self.subtitles:
            raise ValueError(self.prompt.src_1_missing_err)
        if not self.guide:
            raise ValueError(self.prompt.src_2_missing_err)
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
            raise ValueError(self.prompt.output_missing_err)
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
