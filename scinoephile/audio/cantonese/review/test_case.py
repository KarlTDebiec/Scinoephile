#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription review test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import create_model, model_validator

from scinoephile.core.abcs import TestCase
from scinoephile.core.models import format_field

from .answer import ReviewAnswer
from .prompt import ReviewPrompt
from .query import ReviewQuery

__all__ = ["ReviewTestCase"]


class ReviewTestCase[TQuery: ReviewQuery, TAnswer: ReviewAnswer](
    TestCase[TQuery, TAnswer], ABC
):
    """Abstract base class for 粤文 transcription review test cases."""

    answer_cls: ClassVar[type[ReviewAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[ReviewQuery]]
    """Query class for this test case."""
    text: ClassVar[type[ReviewPrompt]]
    """Text strings to be used for corresponding with LLM."""

    @property
    def size(self) -> int:
        """Get size of the test case."""
        zw_idxs = [
            int(s.split("_")[1]) - 1
            for s in self.query_fields
            if s.startswith("zhongwen_")
        ]
        return max(zw_idxs) + 1

    @property
    def source_str(self) -> str:
        """Get Python source string."""
        lines = [
            f"{ReviewTestCase.__name__}.get_test_case_cls("
            f"    {self.size}, {self.text.__name__})("
        ]
        for field in self.query_fields:
            value = getattr(self, field)
            lines.append(format_field(field, value))
        for field in self.answer_fields:
            value = getattr(self, field)
            if value == "":
                continue
            lines.append(format_field(field, value))
        for field in self.test_case_fields:
            value = getattr(self, field)
            lines.append(format_field(field, value))
        lines.append(")")
        return "\n".join(lines)

    @model_validator(mode="after")
    def validate_test_case(self) -> Self:
        """Ensure query and answer together are valid."""
        for idx in range(self.size):
            yuewen = getattr(self, f"yuewen_{idx + 1}")
            yuewen_revised = getattr(self, f"yuewen_revised_{idx + 1}")
            note = getattr(self, f"note_{idx + 1}")
            if yuewen_revised != "":
                if yuewen_revised == yuewen:
                    raise ValueError(self.text.yuewen_unmodified_error.format(idx + 1))
                if note == "":
                    raise ValueError(
                        self.text.yuewen_revised_missing_note_provided_error.format(
                            idx + 1
                        )
                    )
            elif note != "":
                raise ValueError(
                    self.text.yuewen_revised_missing_note_provided_error.format(idx + 1)
                )
        return self

    @classmethod
    @cache
    def get_test_case_cls(
        cls, size: int, text: type[ReviewPrompt] = ReviewPrompt
    ) -> type[Self]:
        """Get concrete test case class with provided size, and text.

        Arguments:
            size: number of subtitles
            text: Prompt providing descriptions and messages
        Returns:
            TestCase type with appropriate configuration
        """
        query_cls = ReviewQuery.get_query_cls(size)
        answer_cls = ReviewAnswer.get_answer_cls(size)
        return create_model(
            f"{cls.__name__}_{size}_{text.__name__}",
            __base__=(query_cls, answer_cls, cls),
            __module__=cls.__module__,
            query_cls=(ClassVar[type[ReviewQuery]], query_cls),
            answer_cls=(ClassVar[type[ReviewAnswer]], answer_cls),
            text=(ClassVar[type[ReviewPrompt]], text),
        )
