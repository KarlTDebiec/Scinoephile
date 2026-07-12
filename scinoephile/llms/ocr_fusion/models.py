#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for OCR-fusion test cases."""

from __future__ import annotations

from collections.abc import Mapping
from typing import ClassVar, Self

from pydantic import model_validator

from scinoephile.core.llms import Answer, Query, TestCase

from .prompt import OcrFusionPrompt

__all__ = [
    "OcrFusionAnswer",
    "OcrFusionQuery",
    "OcrFusionTestCase",
]


_BASE_PROMPT = OcrFusionPrompt()


class OcrFusionQuery(Query):
    """Subtitle text from two OCR sources to fuse."""

    prompt: ClassVar[OcrFusionPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    source_one: str
    """Subtitle text from source one."""
    source_two: str
    """Subtitle text from source two."""

    @model_validator(mode="after")
    def validate_sources(self) -> Self:
        """Ensure both source texts are present and differ.

        Returns:
            validated query
        """
        if not self.source_one:
            raise ValueError(self.prompt.src_1_missing_err)
        if not self.source_two:
            raise ValueError(self.prompt.src_2_missing_err)
        if self.source_one == self.source_two:
            raise ValueError(self.prompt.src_1_src_2_equal_err)
        return self

    @model_validator(mode="before")
    @classmethod
    def validate_sources_present(cls, value: object) -> object:
        """Ensure both source fields are present before field validation.

        Arguments:
            value: raw query data
        Returns:
            raw query data after presence validation
        """
        if not isinstance(value, Mapping):
            return value

        source_one_alias = cls.model_fields["source_one"].alias
        source_one_present = "source_one" in value
        if source_one_alias is not None:
            source_one_present = source_one_present or source_one_alias in value
        if not source_one_present:
            raise ValueError(cls.prompt.src_1_missing_err)

        source_two_alias = cls.model_fields["source_two"].alias
        source_two_present = "source_two" in value
        if source_two_alias is not None:
            source_two_present = source_two_present or source_two_alias in value
        if not source_two_present:
            raise ValueError(cls.prompt.src_2_missing_err)
        return value


class OcrFusionAnswer(Answer):
    """Fused subtitle text and an explanation of the selected output."""

    prompt: ClassVar[OcrFusionPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    output: str
    """Fused subtitle text."""
    note: str
    """Explanation of the fused output."""

    @model_validator(mode="after")
    def validate_content(self) -> Self:
        """Ensure output and note text are present.

        Returns:
            validated answer
        """
        if not self.output:
            raise ValueError(self.prompt.output_missing_err)
        if not self.note:
            raise ValueError(self.prompt.note_missing_err)
        return self

    @model_validator(mode="before")
    @classmethod
    def validate_content_present(cls, value: object) -> object:
        """Ensure output and note fields are present before field validation.

        Arguments:
            value: raw answer data
        Returns:
            raw answer data after presence validation
        """
        if not isinstance(value, Mapping):
            return value

        output_alias = cls.model_fields["output"].alias
        output_present = "output" in value
        if output_alias is not None:
            output_present = output_present or output_alias in value
        if not output_present:
            raise ValueError(cls.prompt.output_missing_err)

        note_alias = cls.model_fields["note"].alias
        note_present = "note" in value
        if note_alias is not None:
            note_present = note_present or note_alias in value
        if not note_present:
            raise ValueError(cls.prompt.note_missing_err)
        return value


class OcrFusionTestCase(TestCase):
    """OCR-fusion query, optional answer, and optimization metadata."""

    query_cls: ClassVar[type[OcrFusionQuery]] = OcrFusionQuery
    """Query model class."""
    answer_cls: ClassVar[type[OcrFusionAnswer]] = OcrFusionAnswer
    """Answer model class."""
    prompt: ClassVar[OcrFusionPrompt] = _BASE_PROMPT
    """Text and field aliases for LLM correspondence."""
    query: OcrFusionQuery
    """Subtitle text from two OCR sources."""
    answer: OcrFusionAnswer | None = None
    """Fused subtitle text and explanation, if available."""

    def get_auto_verified(self) -> bool:
        """Whether this test case should automatically be verified.

        Returns:
            whether the test case should be auto-verified
        """
        if self.answer is None or self.get_min_difficulty() > 1:
            return False
        if self.query.source_one == self.answer.output:
            return "\n" not in self.query.source_one
        if self.query.source_two == self.answer.output:
            return "\n" not in self.query.source_two
        return super().get_auto_verified()

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty based on the fused output.

        Returns:
            minimum difficulty
        """
        min_difficulty = max(super().get_min_difficulty(), 1)
        if self.answer is not None and any(
            char in self.answer.output for char in ("-", '"', "“", "”")
        ):
            min_difficulty = max(min_difficulty, 2)
        return min_difficulty
